#!/bin/bash -x
# dump param #1 (zim in CWD or absolute path) to DOCROOT,and de-namespace

# GLOBALS
DOCROOT=/library/www/html

# Must supply ZIM
if [ $# -eq 0 ];then
   echo "Please supply ZIM filename in CWD or absolute path"
   exit 1
fi

# see if supplied filename works
if [ ! -f $1 ];then
   echo Could not open $1. Quitting . . .
   exit 1
fi

# We will take DOCROOT/zimtest if it is not used
if [ -d $DOCROOT/zimtest ];then
   if [ ! -f $DOCROOT/zimtest/de-namespace ];then
      echo "$DOCROOT/zimtest exists but is not ours. Please delete or move"
      exit 1
   fi
fi

# Delete the previous contents of zimtest
rm -rf $DOCROOT/zimtest
# Make directory
mkdir -p $DOCROOT/zimtest
echo "This de-namespace file reminds you that this folder will be overwritten?" > $DOCROOT/zimtest/de-namespace

zimdump dump --dir=$DOCROOT/zimtest $1

# stop here to look around at the clean dumped format
# exit 0

# put all of the images back in their original places
mv $DOCROOT/zimtest/I/* $DOCROOT/zimtest/
if [ -d I ];then
   rmdir I
fi

# Clip off the A namespace for html
cp -rp $DOCROOT/zimtest/A/* $DOCROOT/zimtest/
cp -rp $DOCROOT/zimtest/-/* $DOCROOT/zimtest/

if [ -d $DOCROOT/zimtest/A ];then
   rm -rf $DOCROOT/zimtest/A
fi

cd $DOCROOT/zimtest
for f in $(find .|grep html); do
   sed -i -e's|../../I/|../|' $f
   sed -i -e's|../../-/|../|' $f
   sed -i -e's|../I/|./|' $f
done
for f in $(find $DOCROOT/zimtest -type f -maxdepth 1 );do
   sed -i -e's|../-/|./|' $f
   sed -i -e's|../I/|./|' $f
done
