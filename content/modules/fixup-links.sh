#!/bin/bash  
# first modify the links in SRC_LINKS_DIR, then cp the httrack files into docs,images,videos 

# bring in the settings
source ../../fixup-links.settings

# make all the output directories
mkdir -p ${OUTPUT_DIR}/docs
mkdir -p ${OUTPUT_DIR}/images
mkdir -p ${OUTPUT_DIR}/videos
mkdir -p ${OUTPUT_DIR}/duplicates
mkdir -p ${OUTPUT_DIR}/other
mkdir -p ${OUTPUT_DIR}/wiki

# change the link in the source directory
for f in `ls $SRC_LINKS_DIR`; do
   # reqular expressions have an extension which permits chopping off http.../.../ repeatedly 
   sed -E  's|https*://([- ._a-z0-9A-Z]*/)*|xsce/|g' ${SRC_LINKS_DIR}/$f > ${OUTPUT_DIR}/wiki/$f
   # but extended regular expressions do not remember match for output -- do in 2 stages
   sync
   sed -i  's|xsce/\([-._a-z0-9A-Z]*.png\)|../images/\1|g 
            s|xsce/\([-._a-z0-9A-Z]*.jpg\)|../images/\1|g
            s|xsce/\([-._a-z0-9A-Z]*.pdg\)|../images/\1|g
            s|xsce/\([-._a-z0-9A-Z]*.pdf\)|../docs/\1|g
            s|xsce/\([-._a-z0-9A-Z]*.mp4\)|../videos/\1|g' ${OUTPUT_DIR}/wiki/$f
done
   
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
            rsync $f $OUTPUT_DIR/other
         ;;
      esac         
   done
done 

