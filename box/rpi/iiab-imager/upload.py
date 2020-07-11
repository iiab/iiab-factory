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
import zipfile
import xml.etree.ElementTree as ET 
import hashlib
import pdb


# Think of the sibling files of an image file as imager_metadata

#  GLOBALS
src_url = "https://downloads.raspberrypi.org/os_list_imagingutility.json"

url_owner = 'iiab'
url_branch = 'master'
# the following may eventually reset to iiab-factory branch=master -- currently unused
iiab_url = "https://raw.githubusercontent.com/%s/iiab-factory/%s/box/rpi/iiab-imager/os_list_imagingutility_iiab.json"%(url_owner,url_branch)

repo_prefix = "/opt/iiab/iiab-factory/box/rpi/iiab-imager"
icon = "https://raw.githubusercontent.com/iiab/iiab-factory/master/box/rpi/rpi-imager/iiab40.png"
url_prefix = "https://archive.org/download"
args = None
imager_menu = "subitems"
imager_md = {} # contains the sibling data in same folder as <fname>.img.<key> with keys needed by rpi-imager
local_md = {}  # calculated values for the check function
archive_item = {} # metadata from archive.org version.

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',\
           ca_certs=certifi.where())
#resp = (http.request("GET",src_url,retries=10))


def parse_args():
    parser = argparse.ArgumentParser(description="Upload img to archive.org, Set rpi-imager json files.")
    parser.add_argument("-c","--check", help='Check archive.org version and metadata (no changes).',action='store_true')
    parser.add_argument("-d","--delete", help='Delete listed item by number.',type=int)
    #parser.add_argument("-r","--replace", help='Replace img.zip at archive.org.',action='store_true')
    parser.add_argument("-e","--experimental", help='Put image into Experimental menu.',action='store_true')
    parser.add_argument("-l","--list", help='List menus.',action='store_true')
    parser.add_argument("-s","--save", help='Save current menus',action='store_true')
    parser.add_argument("-r","--restore", help='Restore saved menus',action='store_true')
    parser.add_argument("image_name", nargs='?',default='',  help='Specify the image file name')
    return parser.parse_args()

def human_readable(num):
    # return 3 significant digits and unit specifier
    num = float(num)
    units = [ '','K','M','G']
    for i in range(4):
        if num<10.0:
            return "%.2f%s"%(num,units[i])
        if num<100.0:
            return "%.1f%s"%(num,units[i])
        if num < 1000.0:
            return "%.0f%s"%(num,units[i])
        num /= 1000.0

def get_archive_metadata(identifier):
      return internetarchive.get_item(identifier)

def get_archive_file_xml(identifier):
   url = os.path.join(url_prefix,identifier,identifier + '_files.xml')
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
      print('not able to read %s'%fname)
      return ''

# The following are the keys for the rpi-imager os-list.json files
menu_names = [ 'name','description','extract_size','extract_sha256','image_download_size','release_date','zip.md5' ]

def exists_imager_info():
   global imager_md
   exists = True
   #print('in exists_imager_info')
   # reads the sibling files adjacent to *.img with suffix in list [menu_names]
   md = {}  # metadata
   for item in menu_names:
      fname = './%s.%s'%(args.image_name,item)
      retn = file_contents(fname)
      if retn != '':
         md[item] = retn 
         #print(fname)
      else:
         exists = False
         print('No existing file found: %s'%fname)
   md['image_download_size'] = int(md.get('image_download_size','0'))
   md['extract_size'] = int(md.get('extract_size','0'))
   identifier = args.image_name + '.zip'
   md['url'] = os.path.join(url_prefix,identifier,identifier,)
   md['icon'] = icon
   imager_md = md.copy()
   return exists
   #print("\nArchive.org metadata:\n%s"%json.dumps(imager_md,indent=2))
   #sys.exit(1)


def do_zip():
   print("Creating zip file")
   my_zipfile = zipfile.ZipFile("./%s"%args.image_name  + ".zip", mode='w', compression=zipfile.ZIP_DEFLATED)
   # Write to zip file
   my_zipfile.write("./%s"%args.image_name)
   my_zipfile.close()

def digest(fname,algorithm):
    print(algorithm)
    hasher = hashlib.new(algorithm)
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
           hasher.update(chunk)
    return hasher.hexdigest()

def write_imager_md(imager_md):
   print('in write_imager_md')
   for key in imager_md.keys():
      with open('./%s.%s'%(args.image_name,key),'w') as fp:
         fp.write(str(imager_md[key]) + '\n')
   
def calculate_local_md():
   # This creates a local version of imager_md
   global local_md
   local_md = {}
   local_md['zip.md5'] = digest(args.image_name + '.zip','md5')
   local_md['extract_sha256'] = digest(args.image_name,'sha256')
   local_md['extract_size'] = os.stat(args.image_name).st_size
   local_md['image_download_size'] = os.stat(args.image_name + '.zip').st_size
   now = datetime.now()
   release_date = now.strftime("%m/%d/%Y")
   local_md['release_date'] = release_date
   

def get_title_description(fieldname):
   global imager_md
   if local_md and local_md.get(fieldname,'') == '' and fieldname not in local_md.keys():
      prompt = f'Please enter a {fieldname.capitalize()} for this image: '
   else:
      prompt = f'Enter new {fieldname.capitalize()}, or just return to keep current Title \n{imager_md[fieldname]}'
   resp = input(prompt)
   if resp == '':
      resp = imager_md[fieldname]
   return resp
 
def create_imager_metadata():
   print('in create_imager_metadata')
   # check that we have a zip file. If not create it now
   if not os.path.isfile(args.image_name + '.zip'):
      do_zip()
   global imager_md
   global local_md
   #if len(imager_md) > 0:
      #return
   calculate_local_md()
   local_md['name'] = get_title_description('name')
   local_md['description'] = get_title_description('description`')
   identifier = args.image_name + '.zip'
   local_md['url'] = os.path.join(url_prefix,identifier,identifier,)
   write_imager_md(local_md)
   imager_md = local_md.copy()

def xfer_imager_md_to_archive_md():
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
   archive_md['release_date'] =  imager_md['release_date']
   return archive_md
       
def find_url_in_imager_json(url, imager_json):
   for index in range(len(imager_json['os_list'])):
      if url == imager_json['os_list'][index]['url']:
         return index   
   return -1
   
def check(name):
   info =  get_archive_metadata(name)
   if (info.metadata):
      print("\nArchive.org metadata:\n%s"%json.dumps(info.metadata,indent=2))

def upload_image(archive_md):
   print("Uploading image to archive.org")
   # Debugging information
   print('MetaData: %s'%archive_md)
   try:
      r = internetarchive.upload(args.image_name + '.zip', files=['./%s'%args.image_name + '.zip'], metadata=archive_md, verbose=True)
      print(r[0].status_code) 
      status = r[0].status_code
   except Exception as e:
      status = 'error'
      with open('./logs/archive_org.log','a+') as ao_fp:
         ao_fp.write("Exception from internetarchive:%s"%e) 
   with open('%s/archive_org.log'%repo_prefix,'a+') as ao_fp:
      now = datetime.now()
      date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
      ao_fp.write('Uploaded %s at %s Status:%s\n'%(args.image_name + '.zip',date_time,status))

def get_json_filename(experimental):
   global imager_menu
   imager_menu = "subitems"
   if experimental:
      imager_menu = 'experimental'
   return os.path.join(repo_prefix,'os_list_imagingutility_iiab_' + imager_menu + '.json')

def get_os_list(experimental):
   global imager_menu
   json_filename = get_json_filename(experimental)
   #print('json_filename:%s'%json_filename)
   #pdb.set_trace()
   try:
      with open(json_filename,'r') as fp:
         json_str = fp.read()
         data = json.loads(json_str)
         # following 3 lines are cludge to change string to int
         for index in range(len(data['os_list'])):
            #pdb.set_trace()
            data['os_list'][index]['extract_size'] = int(data['os_list'][index]['extract_size'])
            data['os_list'][index]['image_download_size'] = int(data['os_list'][index]['image_download_size'])
   except FileNotFoundError as e:
      print(json_filename)
      print("File not found: %s"%e)
      sys.exit(1)
   except:
      print("%s img.json parse error"%json_filename)
      sys.exit(1)
   return data

def print_os_list():
   experimental = False
   num = 1
   data =  get_os_list(experimental)
   print("\nReleased")
   for item in data['os_list']:
      print("%s %s-%s,%s, %s"%(num, item['name'],item['description'],human_readable(item['extract_size']),item['release_date']))
      num += 1
   experimental = True
   data =  get_os_list(experimental)
   print("\nExperimental")
   for item in data['os_list']:
      print("%s %s-%s,%s, %s"%(num, item['name'],item['description'],human_readable(item['extract_size']),item['release_date']))
      num += 1
   print()

def do_delete(delete_num):
   experimental = False
   num = 1
   released = 0
   data =  get_os_list(experimental)
   for item in data['os_list']:
      released = num
      if num == delete_num:
         del data['os_list'][num - 1]
         json_filename_suffix = os.path.join('os_list_imagingutility_iiab_' + 'subitems' + '.json')
         json_filename = os.path.join(repo_prefix,json_filename_suffix)
         with open (json_filename,'w') as fp:
            json.dump(data,fp,indent=2)
         return
      num += 1
   experimental = True
   data =  get_os_list(experimental)
   for item in data['os_list']:
      if num  == delete_num:
         del data['os_list'][num - released - 1]
         json_filename_suffix = os.path.join('os_list_imagingutility_iiab_' + 'experimental' + '.json')
         json_filename = os.path.join(repo_prefix,json_filename_suffix)
         with open (json_filename,'w') as fp:
            json.dump(data,fp,indent=2)
         return
      num += 1

def save(to_dir):
   for fn in glob.glob(repo_prefix+'/os_list*'): 
      shutil.copy(fn,to_dir)

def restore_from(to_dir):
   for fn in glob.glob(to_dir + '/os_list*'): 
      shutil.copy(fn,repo_prefix)

def do_rpi_imager():
   global imager_md

   if not exists_imager_info():
      print('Got to do_rpi_imager without sibling files and imager_md. Quitting..')
      sys.exit(1)

   # update the menu item json
   # but first get the menu as it exists currently
   data = get_os_list(args.experimental)
   if args.check:
      print('\nContents of imager %s:\n'%imager_menu)
      print(json.dumps(data,indent=2))
      return

   # does the args.image_name already exist in the imager json?
   image_index = find_url_in_imager_json(imager_md['url'],data)

   if image_index != -1:
      print("This item is already in the rpi_imager. Replacing ...")
      del data['os_list'][image_index]

   # insert the new metadata into the menu json
   data['os_list'].insert(0,imager_md)

   # and write it
   fname = get_json_filename(args.experimental)
   with open (fname,'w') as fp:
      json.dump(data,fp,indent=2)

def do_archive():
   global archive_item
   global imager_md
   uploaded_md5 = ''
   # Get the md5 for this .img created during the shrink-copy process
   recorded_md5 = file_contents('./%s.%s'%(args.image_name,'zip.md5'))
   if args.check:
      print('\nSibling file contents:\n%s'%json.dumps(imager_md,indent=2))
   if recorded_md5 == '' or len(imager_md) == 0:
      if not exists_imager_info():
         create_imager_metadata()
      recorded_md5 = file_contents('./%s.%s'%(args.image_name,'zip.md5'))

   # Fetch metadata, if it exists, from archive.org
   archive_item = internetarchive.get_item(args.image_name + '.zip')

   if archive_item:
      # Get the md5 calculated by archive.org during upload
      uploaded_md5 = get_archive_file_xml(args.image_name + '.zip')

   if uploaded_md5 != '' and uploaded_md5 == recorded_md5:
      if archive_item and archive_item.metadata['zip_md5'] == recorded_md5:
         # probably the other metadata recorded at archive is valid
         print('Updating metadata at Archive.org')
         archive_md = xfer_imager_md_to_archive_md()
         archive_item.modify_metadata(metadata=archive_md)
            
         # already uploaded
         print('\nSkipping upload to archive.org of %s -- checksums match'%args.image_name)
      else:
         print('md5sums for %s do not match'%md['title'])
         print('local file md5:%s  metadata md5:%s'%(metadata['zip.md5'],archive_item.metadata['zip_md5']))
         if not args.check:
            upload_image()
   else: # Img metadata and archive.org missing or wrong
      if args.check:
         print("\nImage at archive.org is either wrong, or missing")
         print('local file md5:%s  archive.org metadata md5:%s'%(imager_md['zip.md5'],uploaded_md5))
      else:
         if len(imager_md) == 0:
            create_imager_metadata()
         archive_md = xfer_imager_md_to_archive_md()
         print(str(archive_md))
         upload_image(archive_md)

   
def main():
   global args
   orig_dir = ''
   if not os.path.exists(repo_prefix +'/logs'):
      os.mkdir(repo_prefix +'/logs')
   args = parse_args()
   if args.save:
      save(repo_prefix +'/logs')
      print("The following menu items were saved.")
      print_os_list()
      sys.exit(0)
   if args.restore:
      restore_from(repo_prefix +'/logs')
      print_os_list()
      sys.exit(0)
   if args.list:
      print_os_list()
      sys.exit(0)
   if args.delete:
      do_delete(args.delete)
      print_os_list()
      sys.exit(0)
   
   if not os.path.isfile(args.image_name):
      print(args.image_name + " not found in the current directory: %s"%os.getcwd())
      if args.image_name == '':
         print("You must specify an Image file to upload to archive.org")
      sys.exit(1)

   # if path is absolute, record curdir, and change to dir with sibling files
   if args.image_name[0] == '/':
      orig_dir = os.getcwd()
      os.chdir(os.path.dirname(args.image_name))
      args.image_name = os.path.basename(args.image_name)

   if args.image_name.endswith('.zip'):
      args.image_name = args.image_name[:-4]
   do_archive()
   do_rpi_imager()
   if args.check:
      check(args.image_name + '.zip')
   if orig_dir != '':
      os.chdir(orig_dir)

if __name__ == "__main__":
   main()
