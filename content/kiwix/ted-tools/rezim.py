#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,sys
import datetime
import json
import pprint

from pathlib import Path
from zimscraperlib.zim import make_zim_file

# Get the baton values being passed
CACHE_DIR = '/home/ghunt/zimtest/youtube/cache'
with open(CACHE_DIR + '/pass_baton.json','r') as fp:
    baton = json.loads(fp.read())
OUTPUT_DIR = baton['OUTPUT_DIR']
PROJECT_NAME = baton['PROJECT_NAME']
NEW_ZIM_DIR = baton['NEW_ZIM_DIR']
    

period = datetime.datetime.now().strftime("%Y-%m")
fname = f"{PROJECT_NAME}_{period}"
pprint.pprint(baton)
print('fname:%s'%fname)
#logger.info("building ZIM file")
#sys.exit(1)

os.chdir(OUTPUT_DIR)
make_zim_file(
    build_dir=Path(OUTPUT_DIR),
    fpath=Path(NEW_ZIM_DIR),
    name=fname,
    main_page= "home.html",
    favicon="favicon.jpg",
    title=baton['Title'],
    description=baton['Description'],
    language=baton['Language'],
    creator=baton['Creator'],
    publisher="IIAB",
    tags=baton['Tags'],
    scraper=baton['Scraper'],
)
