#!/bin/bash -x 
# dump param #1 (zim in CWD or absolute path) to work area,and de-namespace
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
contents=$(ls $HOME/zimtest/$2/tree|wc -l)
if [ $contents -ne 0 ];then
    echo "The $HOME/zimtest/$2/tree is not empty. Delete if you want to repeat this step."
    exit 0
fi

# Delete the previous contents of zimtest
rm -rf $HOME/zimtest/$2/tree
# Make directory
mkdir -p $HOME/zimtest/$2/tree
echo "This de-namespace file reminds you that this folder will be overwritten?" > $HOME/zimtest/$2/tree/de-namespace

zimdump dump --dir=$HOME/zimtest/$2/tree $1

# stop here to look around at the clean dumped format
# exit 0

# put all of the images back in their original places
mv $HOME/zimtest/$2/tree/I/* $HOME/zimtest/$2/tree
if [ -d I ];then
   rmdir I
fi

# Clip off the A namespace for html
cp -rp $HOME/zimtest/$2/tree/A/* $HOME/zimtest/$2/tree
cp -rp $HOME/zimtest/$2/tree/-/* $HOME/zimtest/$2/tree

if [ -d $HOME/zimtest/$2/tree/A ];then
   rm -rf $HOME/zimtest/$2/tree/A
fi

cd $HOME/zimtest/$2/tree
for f in $(find .|grep html); do
   sed -i -e's|../../I/|../|' $f
   sed -i -e's|../../-/|../|' $f
   sed -i -e's|../I/|./|' $f
done
for f in $(find $HOME/zimtest/$2/tree -maxdepth 1 -type f );do
   sed -i -e's|../-/|./|' $f
   sed -i -e's|../I/|./|' $f
done
