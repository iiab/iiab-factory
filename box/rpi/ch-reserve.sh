#!/bin/bash -x
# change the root reserve portion of root fs

if [ $# -eq 0 ]; then
   RES_PERCENT=1
else
   RES_PERCENT=$1
fi

tune2fs -m $RES_PERCENT /dev/mmcblk0p2
