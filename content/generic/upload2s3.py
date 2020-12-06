#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import hashlib
import requests
import subprocess
from subprocess import Popen, PIPE
import glob
import boto3
import botocore
from botocore.errorfactory import ClientError
import threading
import hashlib

#import pdb; pdb.set_trace()

# Globals
WORKING_DIR = "/library/working/maps"
SOURCE_DIR = "/library/www/html/internetarchive"
SPACE_NAME = "iiab"
PREFIX = "osm-tiles"
ENDPOINT_URL = "https://sfo2.digitaloceanspaces.com" 
key = os.environ['DIGITAL_OCEAN_IIAB_UPLOADER_ACCESS_KEY']
secret = os.environ['DIGITAL_OCEAN_IIAB_UPLOADER_SECRET_KEY']

# Initialize a session using DigitalOcean Spaces.
session = boto3.session.Session()
client = session.client('s3',
                        region_name='sfo2',
                        endpoint_url=ENDPOINT_URL,
                        aws_access_key_id=key,
                        aws_secret_access_key=secret)

s3 = boto3.resource('s3')
bucket = s3.Bucket('iiab')
cors = bucket.Cors()
config = {
    'CORSRules': [
        {
            'AllowedMethods': ['GET'],
            'AllowedOrigins': ['*']
        }
    ]
}
#cors.put(CORSConfiguration=config)
#cors.delete()

def digest(fname,algorithm):
    print(algorithm)
    hasher = hashlib.new(algorithm)
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
           hasher.update(chunk)
    return hasher.hexdigest()

def s3_get_metadata(fname):
    try:
        info = client.head_object(Bucket="iiab", Key=fname)
    except Exception as e:
        print(str(e))
        return {}
    data = info['Metadata']
    print('Returned metadata: %s'%str(data))
    if data.get('md5','') != '':
        meta = data
    else:
        # s3cmd creates metadata as a set of value pairs separated by '/'
        meta = {}
        for nibble in v.split('/'):
            key, value = nibble.split(':')
            meta[key] = value
    return meta
    
def upload_file_to_s3(fname,meta,folder=''):
    if len(folder) > 0 and folder[-1] != '/':
        folder += '/'
    try:
        client.upload_file(fname,'iiab',folder + fname,
            ExtraArgs={'Metadata': meta},
            Callback=ProgressPercentage(fname))
    except Exception as e:
        print(e)
        return False
    return True
    
class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()
    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

# check for presence of list of files to upload
# if missing, create a list of all mbtiles in SOURCE_DIR
# This lets user to delete and narrow down for testing
if not os.path.exists("%s/upload.list"%WORKING_DIR):
    with open("%s/upload.list"%WORKING_DIR,"w") as fp:
        for tile in glob.glob('%s/*.mbtiles'%(SOURCE_DIR)):
            #print(os.path.basename(tile))
            fp.write(tile + '\n')
with open("%s/upload.list"%WORKING_DIR,"r") as fp:
    os.chdir(SOURCE_DIR)
    for line in fp.readlines():
        if line.rstrip() == '':continue
        print(line)
        line = line.rstrip()
        # Check to see if the file has already been transferred
        metadata =s3_get_metadata('%s/%s'%(PREFIX,os.path.basename(line)))
        #print(metadata)
        if len(metadata) != 0:
            print('file %s is already uploaded'%line)
            print(str(metadata))
        else:
            print('%s is missing from bucket'%line)
            local_md = {}
            local_md['md5'] = digest(line,'md5')
            local_md['sha256'] = digest(line,'sha256')
            local_md['size'] = str(os.stat(line).st_size)
            local_md['ctime'] = str(os.stat(line).st_ctime)
            if not os.path.exists(line): 
                print('Warning. . . file does not exist:%s'%line)
                continue
            result = upload_file_to_s3(os.path.basename(line),local_md,'osm-tiles')
            if not result:
                sys.exit(1)