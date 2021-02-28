#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Make directories, and store the downloaded zip files based upon category


import os
import sys
import sqlite3
import json
import hashlib
import requests
import subprocess
from subprocess import Popen, PIPE
import zipfile
#import pdb; pdb.set_trace()


# Globals
db = object
WORKING_DIR = "/library/working/zims"
ZIM_DIR = "/library/www/html/zimtest"

class Sqlite():
   def __init__(self, filename):
      self.conn = sqlite3.connect(filename)
      self.conn.row_factory = sqlite3.Row
      self.conn.text_factory = str
      self.c = self.conn.cursor()

   def __del__(self):
      self.conn.commit()
      self.c.close()
      del self.conn

def get_video_json(path):
    with open(path,'r') as fp:
        try:
            jsonstr = fp.read()
            print(path)
            modules = json.loads(jsonstr.strip())
        except Exception as e:
            print(e)
            print(jsonstr[:80])
            sys.exit(1)
            
    return modules


def make_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download_file(url,todir):
    local_filename = url.split('/')[-1]
    r = requests.get(url)
    f = open(todir + '/' + local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: 
            f.write(chunk)
    f.close()

def video_size(yt_id):
    return os.path.getsize(ZIM_DIR + '/videos/' + yt_id + '/video.webm')

def initialize_db():
    sql = 'CREATE TABLE IF NOT EXISTS video_info ('\
            'yt_id TEXT UNIQUE, zim_size INTEGER, view_count INTEGER, average_rating REAL)'
    db.c.execute(sql)

def main():
    initialize_db()
    yt_id_list = os.listdir(ZIM_DIR + '/videos/')
    for yt_id in iter(yt_id_list):
        data = get_video_json(WORKING_DIR + "/" + yt_id + '.json')
        vsize = video_size(yt_id)
        view_count = data['view_count']
        average_rating = data['average_rating']
        sql = 'INSERT OR REPLACE INTO video_info VALUES (?,?,?,?)'
        db.c.execute(sql,[yt_id,vsize,view_count,average_rating])
        

###########################################################
if __name__ == "__main__":
   ########### get metadata to global space  ##############
   db = Sqlite(WORKING_DIR + '/zim_video_info.sqlite')

   main()
