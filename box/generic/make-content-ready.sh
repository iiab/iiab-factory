#!/bin/bash -x
# most of this should find its way into ansible
# you must run ansible before running this
# assumes osm, kiwix, kalite are installed and iiab-menus have been cloned

# patch osm
pushd ../../content/osm-fixes
bash  ./fix-osm
popd

# refresh kiwix catalog
xsce-cmdsrv-ctl GET-KIWIX-CAT

# rebuild local library.xml
/usr/bin/xsce-make-kiwix-lib

# register with kalite - not sure if necessary or what user/passwd to supply
# kalite manage register

# get kalite English language pack - takes awhile and seems to re-download if run again
export KALITE_HOME=/library/ka-lite
kalite manage retrievecontentpack download en

# copy the menu files into doc root-- if they are not already there
  pushd /opt/iiab-menu
  git pull
  ./cp-menus
  popd

# fetch the online documents into image for offline use
pushd /opt/schoolserver/xsce/scripts
./refresh-wiki-docs.sh
popd
