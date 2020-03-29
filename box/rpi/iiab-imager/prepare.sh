#!/bin/bash 
# get all of the data for the upload to archive.org 
# input required filename 

if [ $# -eq 0 ]; then
   echo You must pass filename as parameter
   echo "  If second parameter is "-f",then recalculate everything"
   exit 1
fi
if [ $# -eq 2 ] && [ "$2" == '-f' ]; then
   rm -f $1.extract_size
   rm -f $1.image_download_size
   rm -f $1.zim.md5
   rm -f $1.extract_sha256
   rm -f $1.release_date
fi   
if [ $# -eq 2 ] && [ "$2" == '-d' ]; then
   rm -f $1.extract_size
   rm -f $1.image_download_size
   rm -f $1.zim.md5
   rm -f $1.extract_sha256
   rm -f $1.release_date
   exit 0
fi   
if [ ! -f $1.name ]; then
   read -p "Menu name: " name
   echo $name > $1.name
fi
if [ ! -f $1.description ]; then
   read -p "Description: " description
   echo $description > $1.description
fi
if [ ! -f $1.extract_size ]; then
   echo $(ls -l $1) | gawk '{print $5}' > $1.extract_size
fi
if [ ! -f $1.image_download_size ]; then
   echo $(ls -l $1.zip) | gawk '{print $5}' > $1.image_download_size
fi
if [ ! -f $1.zip.md5 ]; then
   md5sum $1.zip |gawk '{print $1}' > $1.zip.md5
fi
if [ ! -f $1.extract_sha256 ]; then
   sha256sum $1 |gawk '{print $1}' > $1.extract_sha256
fi
if [ ! -f $1.release_date ]; then
   echo $(date +%Y-%m-%d) > $1.release_date
fi
