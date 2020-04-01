#!/usr/bin/env  python3
# Read input file, download urls with missing data, write output json

import os,sys
import json
import argparse
# add path for internetarchive utility
sys.path.append('/usr/local/lib/python2.7/dist-packages')
import internetarchive
from datetime import datetime
import urllib3
import certifi
import glob
import shutil
import xml.etree.ElementTree as ET 


src_url = "https://downloads.raspberrypi.org/os_list_imagingutility.json"
iiab_url = "https://raw.githubusercontent.com/georgejhunt/iiab-factory/iiab/box/rpi/iiab-imager/os_list_imagingutility_iiab.json"
#repo_prefix = "/opt/iiab/iiab-factory/box/rpi/iiab-imager"
repo_prefix = "/hd/root/images/iiab-factory/box/rpi/iiab-imager"
imager_menu = "subitems"
icon = "https://raw.githubusercontent.com/iiab/iiab-factory/master/box/rpi/rpi-imager/iiab40.png"
url_prefix = "https://archive.org/download"

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',\
           ca_certs=certifi.where())
#resp = (http.request("GET",src_url,retries=10))
args = None
menu_names = [ 'name','description','extract_size','extract_sha256','image_download_size','release_date','zip.md5' ]
current_working_directory = os.getcwd()

def parse_args():
    parser = argparse.ArgumentParser(description="Upload img to archive.org, Set rpi-imager json files.")
    parser.add_argument("-c","--check", help='Check archive.org version and metadata (no changes).',action='store_true')
    parser.add_argument("-d","--delete", help='Delete this menu item.',action='store_true')
    parser.add_argument("-r","--replace", help='Replace img.zip at archive.org.',action='store_true')
    parser.add_argument("-e","--experimental", help='Put image into Experimental menu.',action='store_true')
    parser.add_argument("image_name", help='Specify the image file name')
    return parser.parse_args()


def get_archive_org_metadata(identifier):
      return internetarchive.get_item(identifier)

def get_archive_file_xml(identifier):
   url = os.path.join(url_prefix,args.image_name,args.image_name + '_files.xml')
   resp = (http.request("GET",url,retries=10))
   tree = ET.fromstring(resp.data) 
   file_data = {}
  
   for item in tree.findall('file'):
      if item.attrib['name'] == args.image_name + '.zip':
        print( item.find('md5').text)
                   

def fetch_image_info():
   md = {}
   for item in menu_names:
      fname = './%s.%s'%(args.image_name,item)
      #print(fname)
      try:
         with open(fname,'r') as fp:
            md[item] = fp.read().rstrip()
      except Exception as e:
         print("error reading %s:%s"%(fname,e,))
         print("Perhaps you did not run 'prepare.sh', which is required by this program")
         sys.exit(1)
   md['image_download_size'] = int(md['image_download_size'])
   md['extract_size'] = int(md['extract_size'])
   md['url'] = os.path.join(url_prefix,args.image_name,args.image_name + '.zip')
   md['icon'] = icon
   return md

def check(name):
   info =  get_archive_org_metadata(name)
   if (info.metadata):
      print(str(info.metadata))

def main():
   global args
   global imager_menu
   args = parse_args()
   get_archive_file_xml(args.image_name)
   sys.exit(0)
   if args.check:
      check(args.image_name)
      sys.exit(0)

   # fall through to do the upload
   metadata = fetch_image_info()
   #print(str(metadata))

   # Gather together the metadata for archive.org
   md = {}
   md['title'] = metadata['name']
   #md['collection'] = "internetinabox"
   md["creator"] = "Internet in a Box" 
   md["subject"] = "rpi" 
   md["licenseurl"] = "http://creativecommons.org/licenses/by-sa/4.0/"
   md["zip_md5"] = metadata['zip.md5']
   md["mediatype"] = "software"
   md["description"] = metadata['description']
   md["extract_sha256"] = metadata['extract_sha256']
   md['extract_size'] =  metadata['extract_size']
   md['image_download_size'] =  metadata['image_download_size']
   
   # Check is this has already been uploaded
   item = internetarchive.get_item(args.image_name)
   upload = False
   status = 'ok'
   if not item.metadata:
      print('Archive.org does not have file with identifier: %s'%identifier) 
      upload = True
   else:
      if item.metadata['zip_md5'] == metadata['zip.md5']:
         # already uploaded
         print('Skipping %s -- checksums match'%args.image_name)
      else:
         print('md5sums for %s do not match'%md['title'])
         print('local file md5:%s  metadata md5:%s'%(metadata['zip.md5'],item.metadata['zip_md5']))
         upload = True
   if upload:
      # Debugging information
      print('MetaData: %s'%md)
      try:
         r = internetarchive.upload(args.image_name, files=['./%s'%args.image_name], metadata=md)
         print(r[0].status_code) 
         status = r[0].status_code
      except Exception as e:
         status = 'error'
         with open('./archive_org.log','a+') as ao_fp:
            ao_fp.write("Exception from internetarchive:%s"%e) 
   with open('./archive_org.log','a+') as ao_fp:
      now = datetime.now()
      date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
      ao_fp.write('Uploaded %s at %s Status:%s\n'%(args.image_name,date_time,status))


   # update the menu item json
   if args.experimental:
      imager_menu = 'experimental'
   json_filename_suffix = os.path.join('os_list_imagingutility_iiab_' + imager_menu + '.json')
   json_filename = os.path.join(repo_prefix,json_filename_suffix)
   #print('json_filename:%s'%json_filename)
   try:
      with open(json_filename,'r') as fp:
         json_str = fp.read()
         data = json.loads(json_str)
   except FileNotFoundError as e:
      print("File not found: %s"%e)
      sys.exit(1)
   except:
      print("img.json parse error")
      sys.exit(1)
   data['os_list'].insert(0,metadata)

   # write the new json to /tmp and compare with previous version
   fname = os.path.join(repo_prefix,json_filename_suffix)
   tmp_name = os.path.join('/tmp',json_filename_suffix)
   with open (tmp_name,'w') as fp:
      json.dump(data,fp,indent=2)

   # Before changing the json file, make a backup copy, in case things go wrong
   now = datetime.now()
   date_time = now.strftime("%m-%d-%Y_%H:%M")
   os.makedirs("./logs/%s"%date_time)
   for fn in glob.glob(repo_prefix+'/os_list*'): 
      shutil.copy(fn,"./logs/%s"%date_time)
   sys.exit(1)
   

if __name__ == "__main__":
   if not os.path.exists(repo_prefix +'/logs'):
      os.mkdir(repo_prefix +'/logs')
   main()
