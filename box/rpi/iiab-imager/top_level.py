#!/usr/bin/env  python3
# Read input file, download urls with missing data, write output json

import os,sys
import json
import urllib3
import certifi

src_url = "https://downloads.raspberrypi.org/os_list_imagingutility.json"
iiab_url = "https://raw.githubusercontent.com/iiab/iiab-factory/master/box/rpi/iiab-imager/os_list_imagingutility_iiab.json"
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',\
           ca_certs=certifi.where())
resp = (http.request("GET",src_url,retries=10))
#with open('os_input','r') as img_fp:
if True:
   try:
      data = json.loads(resp.data)
   except:
      print("img.json parse error")
      sys.exit(1)

   # create the item for IIAB and put it at the top of the list
   iiab_json = {}
   
   iiab_json['name'] = "IIAB -- Experimental"
   iiab_json["description"] = "Pre-release and specialized Images"
   iiab_json["icon"] = "https://raw.githubusercontent.com/iiab/iiab-factory/master/box/rpi/rpi-imager/iiab40.png"
   iiab_json["subitems_url"] = "https://raw.githubusercontent.com/iiab/iiab-factory/master/box/rpi/iiab-imager/os_list_imagingutility_iiab_experimental.json"
   data['os_list'].insert(0,iiab_json)

   iiab_json = {}
   iiab_json['name'] = "IIAB -- Releases"
   iiab_json["description"] = "Internet in a Box Images"
   iiab_json["icon"] = "https://raw.githubusercontent.com/iiab/iiab-factory/master/box/rpi/rpi-imager/iiab40.png"
   iiab_json["subitems_url"] = "https://raw.githubusercontent.com/iiab/iiab-factory/master/box/rpi/iiab-imager/os_list_imagingutility_iiab_subitems.json"
   data['os_list'].insert(0,iiab_json)
   with open("os_list_imagingutility.json",'w') as fp:
      json.dump(data,fp,indent=2)

