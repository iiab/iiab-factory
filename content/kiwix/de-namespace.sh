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


cd $DOCROOT/zimtest
# put all of the images back in their original places
cd I
mv * ..
cd $DOCROOT/zimtest
if [ -d I ];then
   rmdir I
fi

# Clip off the A namespace for html
cd A
cp -rp * ..

cd $DOCROOT/zimtest
if [ -d A ];then
   rm -rf A
fi

for f in $(find .|grep html); do
   sed -i -e's|../../I/|../|' $f
   sed -i -e's|../I/|./|' $f
done

