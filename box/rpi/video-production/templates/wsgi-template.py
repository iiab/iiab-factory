#!/usr/bin/env python
# -*- coding: utf-8 -*-
# server.py

import os
from flask import Flask,request
#from flask_mysqldb import MySQL
from jinja2 import Environment, FileSystemLoader
import json
import sqlite3

# Create the jinja2 environment.
VIDEOS_BASE = "/opt/iiab/video/assets"
j2_env = Environment(loader=FileSystemLoader(VIDEOS_BASE),trim_blocks=True)

# Create an interface to sqlite3 database
class Videos(object):
   def __init__(self, filename):

      self.conn = sqlite3.connect(filename)
      self.conn.row_factory = sqlite3.Row
      self.c = self.conn.cursor()
      self.schemaReady = False

   def __del__(self):
      self.conn.commit()
      self.c.close()
      del self.conn

   def ListTiles(self):
      rows = self.c.execute("SELECT zoom_level, tile_column, tile_row FROM tiles")
      out = []
      for row in rows:
         out.append((row[0], row[1], row[2]))
      return out



application = Flask(__name__)
# Config MySQL
application.config['MYSQL_HOST'] = 'localhost'
application.config['MYSQL_USER'] = 'menus_user'
application.config['MYSQL_PASSWORD'] = 'g0adm1n'
application.config['MYSQL_DB'] = 'menus_db'
application.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(application)
@application.route('/')
def one():
    rv = "hello world"
    return str(rv)

    
if __name__ == "__main__":
    application.run(host='0.0.0.0',port=9458)

#vim: tabstop=3 expandtab shiftwidth=3 softtabstop=3 background=dark
