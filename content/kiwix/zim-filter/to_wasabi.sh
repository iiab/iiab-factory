#!/bin/bash -x
# Copy fils to our wasabi cloud storage

PREFIX=/ext/zims
for f in $(ls  $PREFIX/*/new-zim/*.zim); do
   cmd="rclone copy $f wasabi:/iiab-zims/"
   echo $cmd
   #exec $cmd
done
