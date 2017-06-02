#!/bin/bash 
# check/copy the files in the list to an output path
if [ $# -eq 0 ]; then
    echo "need filename of the <subset>.list"
    exit 1
fi
subset=`echo $1 | cut -d. -f1`
for f in `cat $1`;do
   if [ ! -f $f ]; then
      echo $f not found
   else
      prefix=`dirname $f`
      prefix=`echo $prefix|sed -E 's%.*default/(.*)%\1%'`
      mkdir -p /library/$subset/output/$prefix
      rsync -a $f /library/$subset/output/$prefix/
   fi
done
space=`du -sh /library/$subset/output`
echo "du -sh reports: $space"
