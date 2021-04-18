#!/bin/bash -x 
# dump param #1 (zim in CWD or absolute path) to dest (PREFIX/$NAME)
set -e

# Must supply ZIM
if [ $# -lt 2 ];then
   echo "Please supply absolute path of ZIM filename and the project name"
   exit 1
fi

# see if supplied filename works
if [ ! -f $1 ];then
   echo Could not open $1. Quitting . . .
   exit 1
fi

# for use in jupyter notebook, do not overwrite any tree contents
contents=$(ls $2/tree|wc -l)
if [ $contents -ne 0 ];then
    echo "The $2/tree is not empty. Delete if you want to repeat this step."
    exit 0
fi

# Delete the previous contents of zims
rm -rf $2/tree
# Make directory
mkdir -p $2/tree
echo "This de-namespace file reminds you that this folder will be overwritten?" > $2/tree/de-namespace

zimdump dump --dir=$2/tree $1

# stop here to look around at the clean dumped format
# It looks like just living with the namespace layout imposed by zim spec might be a better strategy
#exit 0

# put all of the images back in their original places
mv $2/tree/I/* $2/tree
if [ -d I ];then
   rmdir I
fi

# Clip off the A namespace for html
cp -rp $2/tree/A/* $2/tree
cp -rp $2/tree/-/* $2/tree

if [ -d $2/tree/A ];then
   rm -rf $2/tree/A
fi

cd $2/tree
for f in $(find .|grep -e html -e css); do
   sed -i -e's|../../../I/||g' $f
   sed -i -e's|../../I/||g' $f
   sed -i -e's|../I/||g' $f
   sed -i -e's|../../-/||g' $f
   sed -i -e's|../A/||g' $f
done
for f in $(find $2/tree -maxdepth 1 -type f );do
   sed -i -e's|../-/||g' $f
done
