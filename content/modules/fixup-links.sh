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
for f in `find  ./wiki -type f`; do
      base=`basename $f`
      dirname=`dirname $f`
      mkdir -p $OUTPUT_DIR/$dirname

      # reqular expressions have extension (-E) which permits chopping off http.../.../ repeatedly 
      sed -E  's|https*://([- ._a-z0-9A-Z]*/)*|xsce/|g' $f > ${OUTPUT_DIR}/$f

      # but extended regular expressions do not remember match for output -- do in 2 stages
      sync
      sed -i  's|xsce/\([-._a-z0-9A-Z]*.png\)|../images/\1|g 
               s|xsce/\([-._a-z0-9A-Z]*.jpg\)|../images/\1|g
               s|xsce/\([-._a-z0-9A-Z]*.pdg\)|../images/\1|g
               s|xsce/\([-._a-z0-9A-Z]*.pdf\)|../docs/\1|g
               s|xsce/\([-._a-z0-9A-Z]*.mp4\)|../videos/\1|g' ${OUTPUT_DIR}/$f
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
   sed -e 's|https*://wikem.org/w/|./|' $f > $OUTPUT_DIR/$f
done
popd
