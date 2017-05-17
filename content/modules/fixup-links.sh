#!/bin/bash -x
# read a file containing a list

# bring in the settings
source ../../fixup-links.settings

mkdir -p $OUTPUT-DATA-Dir/docs
mkdir -p $OUTPUT-DATA-Dir/html
mkdir -p $OUTPUT-DATA-Dir/images
mkdir -p $OUTPUT-DATA-Dir/duplicates

for d in `ls $TARGET-DATA-DIR/wiki`; do
   for f in `find $d`; do
      if [ ! -f $f ];then
        continue
      fi
      fname=`basename $f`
      suffix=${fname: -4}
      case $suffix in
      "html")
         if [ -f $OUTPUT-DATA-Dir/html/$fname ]; then
            cp $f $OUTPUT-DATA-Dir/duplicates
         else
            cp $f $OUTPUT-DATA-Dir/html
         fi
         ;;
      ".pdf")
         if [ -f $OUTPUT-DATA-Dir/docs/$fname ]; then
            cp $f $OUTPUT-DATA-Dir/duplicates
         else
            cp $f $OUTPUT-DATA-Dir/html
         fi
         ;;
      ".png"|"jpeg"|".jpg")
         if [ -f $OUTPUT-DATA-Dir/images/$fname ]; then
            cp $f $OUTPUT-DATA-Dir/duplicates
         else
            cp $f $OUTPUT-DATA-Dir/images
         fi
         cp $f $OUTPUT-DATA-Dir/images
         ;;
      "*")
         ;;
      esac         
   done
done 

