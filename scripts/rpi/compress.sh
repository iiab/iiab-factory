#!/bin/bash
# umbrella script to combine min-sd and cp-sd into a single function

if [ $# -eq 0 ]; then
   echo "Usage: $0 filename (no .img), optional rootfs device (like /dev/sdg3), optional image directory (like /curation/images)"
   exit 1
fi

./min-sd $1 $2 $3

./cp-sd $1 $2 $3
