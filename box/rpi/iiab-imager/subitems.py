#!/usr/bin/env  python3
# Read input file, download urls with missing data, write output json

import os,sys
sys.path.append('/usr/local/lib/python2.7/dist-packages')
import json
import shutil
import subprocess
import internetarchive
import re
from datetime import datetime
import urllib3
import certifi

src_url = "https://downloads.raspberrypi.org/os_list_imagingutility.json"
iiab_url = "https://raw.githubusercontent.com/georgejhunt/iiab-factory/iiab/box/rpi/iiab-imager/os_list_imagingutility_iiab.json"
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
   iiab_json['name'] = "IIAB"
   iiab_json["description"] = "Internet in a Box Images"
   iiab_json["icon"] = "https://raw.githubusercontent.com/iiab/iiab-factory/master/box/rpi/rpi-imager/iiab40.png"
   iiab_json["subitems_url"] = "https://raw.githubusercontent.com/georgejhunt/iiab-factory/iiab/box/rpi/iiab-imager/os_list_imagingutility_iiab.json"
   data['os_list'].insert(0,iiab_json)
   with open("os_list_imagingutility.json",'w') as fp:
      json.dump(data,fp,indent=2)

   sys.exit(0)

   if False:
         # pull the version string out of the url for use in identity
         url = data['regions'][region]['url']
         match = re.search(r'.*\d{4}-\d{2}-\d{2}_(v\d+\.\d+)\..*',url)
         version =  match.group(1)

         # Fetch the md5 to see if local file needs uploading
         target_zip = os.path.join(MR_HARD_DISK,'stage4',os.path.basename(url))
         with open(target_zip + '.md5','r') as md5_fp:
            instr = md5_fp.read()
            md5 = instr.split(' ')[0]
         if len(md5) == 0:
            print('md5 was zero length. ABORTING')
            sys.exit(1)

         # Gather together the metadata for archive.org
         md = {}
         md['title'] = "OSM Vector Server for %s"%region
         #md['collection'] = "internetinabox"
         md["creator"] = "Internet in a Box" 
         md["subject"] = "rpi" 
         md["subject"] = "maps" 
         md["licenseurl"] = "http://creativecommons.org/licenses/by-sa/4.0/"
         md["zip_md5"] = md5
         md["mediatype"] = "software"
         md["description"] = "This client/server IIAB package makes OpenStreetMap data in vector format browsable from clients running Windows, Android, iOS browsers." 

         perma_ref = 'en-osm-omt_' + region
         identifier = perma_ref + '_' + data['regions'][region]['date'] \
                      + '_' + version

         # Check is this has already been uploaded
         item = internetarchive.get_item(identifier)
         print('Identifier: %s. Filename: %s'%(identifier,target_zip,))
         if item.metadata:
            if item.metadata['zip_md5'] == md5:
               # already uploaded
               print('local file md5:%s  metadata md5:%s'%(md5,item.metadata['zip_md5']))
               print('Skipping %s -- checksums match'%region)
               continue
            else:
               print('md5sums for %s do not match'%region)
               r = item.modify_metadata({"zip_md5":"%s"%md5})
         else:
            print('Archive.org does not have file with identifier: %s'%identifier) 
         # Debugging information
         print('Uploading %s'%region)
         print('MetaData: %s'%md)
         try:
            r = internetarchive.upload(identifier, files=[target_zip], metadata=md)
            print(r[0].status_code) 
            status = r[0].status_code
         except Exception as e:
            status = 'error'
            with open('./upload.log','a+') as ao_fp:
               ao_fp.write("Exception from internetarchive:%s"%e) 
         with open('./upload.log','a+') as ao_fp:
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            ao_fp.write('Uploaded %s at %s Status:%s\n'%(identifier,date_time,status))
