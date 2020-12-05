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
#import pdb; pdb.set_trace()

# Globals
WORKING_DIR = "/library/working/maps"
SOURCE_DIR = "/library/www/html/internetarchive"
SPACE_NAME = "iiab"
PREFIX = "/osm-tiles"
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

def s3_get_metadata(fname):
    info = client.head_object(Bucket="iiab", Key="upload2s3.py")
    data = info['Metadata']
    # print(str(data))
    k = list(data.keys())[0]
    v = data[k]
    meta = {}
    for nibble in v.split('/'):
        key, value = nibble.split(':')
        meta[key] = value
    return meta
    
# check for presence of list of files to upload
# if missing, create a list of all mbtiles in SOURCE_DIR
# This lets user to delete and narrow down for testing
if not os.path.exists("%s/upload.list"%WORKING_DIR):
    with open("%s/upload.list"%WORKING_DIR,"w") as fp:
        for tile in glob.glob('%s/*.mbtiles'%(SOURCE_DIR)):
            #print(os.path.basename(tile))
            fp.write(tile + '\n')
with open("%s/upload.list"%WORKING_DIR,"r") as fp:
    for line in fp.readlines():
        if line.rstrip() == '':continue
        print(line)
        line = line.rstrip()
        # Check to see if the file has already been transferred
        metadata =s3_get_metadata(os.path.basename(line))
        if len(metadata) != 0:
            print('file %s is already uploaded'%line)
        else:
            print('%s is missing from bucket'%line)
