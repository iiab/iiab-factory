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
import hashlib


# Think of the sibling files of an image file as imager_metadata

#  GLOBALS
src_url = "https://downloads.raspberrypi.org/os_list_imagingutility.json"
iiab_url = "https://raw.githubusercontent.com/georgejhunt/iiab-factory/iiab/box/rpi/iiab-imager/os_list_imagingutility_iiab.json"
#repo_prefix = "/opt/iiab/iiab-factory/box/rpi/iiab-imager"
repo_prefix = "/hd/root/images/iiab-factory/box/rpi/iiab-imager"
imager_menu = "subitems"
icon = "https://raw.githubusercontent.com/iiab/iiab-factory/master/box/rpi/rpi-imager/iiab40.png"
url_prefix = "https://archive.org/download"
args = None

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',\
           ca_certs=certifi.where())
#resp = (http.request("GET",src_url,retries=10))


def parse_args():
    parser = argparse.ArgumentParser(description="Upload img to archive.org, Set rpi-imager json files.")
    parser.add_argument("-c","--check", help='Check archive.org version and metadata (no changes).',action='store_true')
    parser.add_argument("-d","--delete", help='Delete this menu item.',action='store_true')
    parser.add_argument("-r","--replace", help='Replace img.zip at archive.org.',action='store_true')
    parser.add_argument("-e","--experimental", help='Put image into Experimental menu.',action='store_true')
    parser.add_argument("image_name", help='Specify the image file name')
    return parser.parse_args()


def get_archive_metadata(identifier):
      return internetarchive.get_item(identifier)

def get_archive_file_xml(identifier):
   url = os.path.join(url_prefix,args.image_name,args.image_name + '_files.xml')
   resp = (http.request("GET",url,retries=10))
   if resp.status == 200:
      tree = ET.fromstring(resp.data) 
     
      for item in tree.findall('file'):
         if item.attrib['name'] == args.image_name + '.zip':
            return item.find('md5').text
   return ''

def file_contents(fname):
   try:
      with open(fname,'r') as fp:
         chunk = fp.read().rstrip()
         return chunk
   except Exception as e:
      return ''

# The following are the keys for the rpi-imager os-list.json files
menu_names = [ 'name','description','extract_size','extract_sha256','image_download_size','release_date','zip.md5' ]

def fetch_imager_info():
   # reads the sibling files adjacent to *.img with suffix in list [menu_names]
   md = {}  # metadata
   for item in menu_names:
      fname = './%s.%s'%(args.image_name,item)
      retn = file_contents(fname)
      if retn != '':
         md[item] = retn 
         #print(fname)
      else:
         return {}
   md['image_download_size'] = int(md['image_download_size'])
   md['extract_size'] = int(md['extract_size'])
   md['url'] = os.path.join(url_prefix,args.image_name,args.image_name + '.zip')
   md['icon'] = icon
   return md

def do_zip():
   print('do_zip function is not implemented')
   sys.exit(1)

def digest(fname,algorithm):
    hasher = hashlib.net(algorithm)
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
           hasher.update(chunk)
    return hasher.hexdigest()

def ensure(key,value):
   if not os.path.isfile('./%s%s'%(args.image_name,key)):
      with open('./%s%s'%(args.image_name,key),'w') as fp:
         fp.write(value + '\n')
   
def create_imager_metadata():
   print('in create_image_metadata')
   imager_md = {}
   # in case the zip file is missing
   if not os.path.isfile(args.image_name + '.zip'):
      do_zip()
   if not os.path.isfile(args.image_name + '.zip.md5'):
      imager_md['md5'] = digest(args.image_name + '.zip','md5')
      ensure('zip.md5',imager_md['md5'])
   if not os.path.isfile(args.image_name + '.zip.md5.txt'):
      ensure('zip.md5.txt',imager_md['md5'])
   if not os.path.isfile(args.image_name + '.extract_sha256'):
      imager_md['sha256'] = digest(args.image_name,'sha256')
      ensure('extract_sha256',imager_md['sha256'])
   if not os.path.isfile(args.image_name + '.extract_size'):
      imager_md['extract_size'] = os.stat(args.image_name).st_size
      ensure('extract_size',imager_md['extract_size'])
   if not os.path.isfile(args.image_name + '.image_download_size'):
      imager_md['image_download__size'] = os.stat('./%s%s'%(args.image_name + '.zip')).st_size
      ensure('image_download_size',imager_md['image_download_size'])
   return imager_md

def calculate_imager_md():
   imager_md = {}
   imager_md['md5'] = digest(args.image_name + '.zip','md5')
   imager_md['sha256'] = digest(args.image_name,'sha256')
   imager_md['extract_size'] = os.stat(args.image_name).st_size
   imager_md['image_download__size'] = os.stat('./%s%s'%(args.image_name + '.zip')).st_size
   return imager_md


def xfer_imager_md_to_archive_md(imager_md):
   print(repr(imager_md))
   archive_md = {}
   archive_md['title'] = imager_md['name']
   #archive_md['collection'] = "internetinabox"
   archive_md["creator"] = "Internet in a Box" 
   archive_md["subject"] = "rpi" 
   archive_md["licenseurl"] = "http://creativecommons.org/licenses/by-sa/4.0/"
   archive_md["zip_md5"] = imager_md['zip.md5']
   archive_md["mediatype"] = "software"
   archive_md["description"] = imager_md['description']
   archive_md["extract_sha256"] = imager_md['extract_sha256']
   archive_md['extract_size'] =  imager_md['extract_size']
   archive_md['image_download_size'] =  imager_md['image_download_size']
   return archive_md
       
def check(name):
   info =  get_archive_metadata(name)
   if (info.metadata):
      print(str(info.metadata))

def upload_image(archive_md):
   print("Uploading image to archive.org")
   # Debugging information
   print('MetaData: %s'%archive_md)
   try:
      r = internetarchive.upload(args.image_name, files=['./%s'%args.image_name], metadata=archive_md)
      print(r[0].status_code) 
      status = r[0].status_code
   except Exception as e:
      status = 'error'
      with open('./logs/archive_org.log','a+') as ao_fp:
         ao_fp.write("Exception from internetarchive:%s"%e) 
   with open('./archive_org.log','a+') as ao_fp:
      now = datetime.now()
      date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
      ao_fp.write('Uploaded %s at %s Status:%s\n'%(args.image_name,date_time,status))

def do_rpi_imager():
   imager_md = fetch_imager_info()

   # update the menu item json
   imager_menu = "subitems"
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
   data['os_list'].insert(0,imager_md)

   # Before changing the json file, make a backup copy, in case things go wrong
   now = datetime.now()
   date_time = now.strftime("%m-%d-%Y_%H:%M")
   os.makedirs("./logs/%s"%date_time)
   for fn in glob.glob(repo_prefix+'/os_list*'): 
      shutil.copy(fn,"./logs/%s"%date_time)

   # Before changing the json file, make a backup copy, in case things go wrong
   now = datetime.now()
   date_time = now.strftime("%m-%d-%Y_%H:%M")
   if not os.path.exists("./logs/%s"%date_time):
      os.makedirs("./logs/%s"%date_time)
   for fn in glob.glob(repo_prefix+'/os_list*'): 
      shutil.copy(fn,"./logs/%s"%date_time)

   # write the new json to /tmp and compare with previous version
   fname = os.path.join(repo_prefix,json_filename_suffix)
   tmp_name = os.path.join('/tmp',json_filename_suffix)
   with open (tmp_name,'w') as fp:
      json.dump(data,fp,indent=2)

def do_archive():
   # Get the md5 for this .img created during the shrink-copy process
   recorded_md5 = file_contents('./%s.%s'%(args.image_name,'zip.md5'))
   imager_md = fetch_imager_info()
   print('imager_md:',repr(imager_md))
   if recorded_md5 == '' or not imager_md:
      create_imager_metadata()
      recorded_md5 = file_contents('./%s.%s'%(args.image_name,'zip.md5'))

   # Fetch metadata, if it exists, from archive.org
   item = internetarchive.get_item(args.image_name)

   if item:
      # Get the md5 calculated by archive.org during upload
      uploaded_md5 = get_archive_file_xml(args.image_name)

   if uploaded_md5 != '' and uploaded_md5 == recorded_md5:
      if item and item.metadata['zip_md5'] == recorded_md5:
         # probably the other metadata recorded at archive is valid
         # already uploaded
         print('Skipping %s -- checksums match'%args.image_name)
      else:
         print('md5sums for %s do not match'%md['title'])
         print('local file md5:%s  metadata md5:%s'%(metadata['zip.md5'],item.metadata['zip_md5']))
         upload_image()
   else: # Img metadata and archive.org missing or wrong
      if args.check:
         print("Image at archive.org is either wrong, or missing")
      else:
         imager_md = create_imager_metadata()
         archive_md = xfer_imager_md_to_archive_md(imager_md)
         upload_image(archive_md)

def main():
   global args
   if not os.path.exists(repo_prefix +'/logs'):
      os.mkdir(repo_prefix +'/logs')
   args = parse_args()
   if not os.path.isfile(args.image_name):
      print(args.image_name + " not found in the current directory: %s"%os.getcwd())
      sys.exit(1)
   if not args.delete:
      do_archive()
   do_rpi_imager()
   if args.check:
      check(args.image_name)

if __name__ == "__main__":
   main()
