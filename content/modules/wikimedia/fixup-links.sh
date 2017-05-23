#!/bin/bash  
# first modify the links in SRC_LINKS_DIR, then cp the httrack files into docs,images,videos 

# define the settings
PREFIX=/library/www/html/modules
SRC_LINKS_DIR=$PREFIX/en-wikem3
TARGET_DATA_DIR=$PREFIX/en-wikem-george # originally a httrack output
OUTPUT_DIR=$TARGET_DATA_DIR/output

# make all the output directories
mkdir -p ${OUTPUT_DIR}/docs
mkdir -p ${OUTPUT_DIR}/images
mkdir -p ${OUTPUT_DIR}/videos
mkdir -p ${OUTPUT_DIR}/duplicates
mkdir -p ${OUTPUT_DIR}/errors
mkdir -p ${OUTPUT_DIR}/wiki
mkdir -p ${OUTPUT_DIR}/w

# change the link in the source directory
pushd ${SRC_LINKS_DIR}/
# first make all the references at the first level in wiki `to http://wikem/w relative
for f in `ls wiki/`; do
  if [ -f wiki/$f ]; then
      sed  -e  's%https*://wikem.org/w%../w%g' wiki/$f > ${OUTPUT_DIR}/wiki/$f
  fi
done

for f in `find  ./wiki -type f`; do
      base=`basename $f`
      dirname=`dirname $f`
      mkdir -p $OUTPUT_DIR/$dirname
   if [ "$dirname" = "./wiki" ]; then
      sed -i -E  's%https*://([-._/a-z0-9A-Z]*/)*([-_/a-z0-9A-Z]*\.(png|jpg|jpeg)+)+%../images/\2%g
                  s%https*://([-._/a-z0-9A-Z]*/)*([-_/a-z0-9A-Z]*\.(pdf))+%../docss/\2%g
                  s%https*://([-._/a-z0-9A-Z]*/)*([-_/a-z0-9A-Z]*\.(mp4))+%../videos/\2%g' $f
   else
      sed  -E  's%https*://([-._/a-z0-9A-Z]*/)*([-_/a-z0-9A-Z]*\.(png|jpg|jpeg)+)+%../images/\2%g
                  s%https*://([-._/a-z0-9A-Z]*/)*([-_/a-z0-9A-Z]*\.(pdf))+%../docss/\2%g
                  s%https*://([-._/a-z0-9A-Z]*/)*([-_/a-z0-9A-Z]*\.(mp4))+%../videos/\2%g' $f > ${OUTPUT_DIR}/$f
   fi
done

for f in `find  ./w -type f`; do
      base=`basename $f`
      dirname=`dirname $f`
      mkdir -p $OUTPUT_DIR/$dirname

      sed  -E  's%https*://([-._/a-z0-9A-Z]*/)*([-_/a-z0-9A-Z]*.(png|jpg|jpeg))+%../images/\2%g
                s%https*://([-._/a-z0-9A-Z]*/)*([-_/a-z0-9A-Z]*.pdf)+%../docs/\2%g
                s%https*://([-._/a-z0-9A-Z]*/)*([-_/a-z0-9A-Z]*.mp4)+%../videos/\2%g' $f > ${OUTPUT_DIR}/$f

done

popd
   
# read through the downloaded external resources and collapse into docs,vides,images
for d in `ls $TARGET_DATA_DIR/wiki`; do
   for f in `find $TARGET_DATA_DIR/wiki/$d`; do
      if [ ! -f $f ];then
        continue
      fi
      fname=`basename $f`
      suffix=${fname: -4}
      case $suffix in
      ".pdf")
         if [ -f $OUTPUT_DIR/docs/$fname ]; then
            rsync $f $OUTPUT_DIR/duplicates
         else
            rsync $f $OUTPUT_DIR/docs
         fi
         ;;
      ".mp4")
         if [ -f $OUTPUT_DIR/videos/$fname ]; then
            rsync $f $OUTPUT_DIR/duplicates
         else
            rsync $f $OUTPUT_DIR/videos
         fi
         ;;
      ".png"|"jpeg"|".jpg"|".pdg")
         if [ -f $OUTPUT_DIR/images/$fname ]; then
            rsync $f $OUTPUT_DIR/duplicates
         else
            rsync $f $OUTPUT_DIR/images
         fi
         ;;
      "*")
            rsync $f $OUTPUT_DIR/errors
         ;;
      esac         
   done
done 

# substitute, and copy, the ./w/ directory
pushd ${SRC_LINKS_DIR}
for f in `find  ./w/ -type f`; do
   dirname=`dirname $f`
   mkdir -p $dirname
   sed  -E  's%https*://([-._/a-z0-9A-Z]*/)*([-_/a-z0-9A-Z]*.(png|jpg|jpeg))+%../images/\2%g
             s|https*://wikem.org/w/|./|g' $f > $OUTPUT_DIR/$f
done
popd
