#!/bin/bash -x
# keep a list of all that finalizes rpi images for 6.2
set -e

# this script can be run repeatedly. As the last step, run sysprep script.
#  sysprep resets authorized keys to authorized developers -- wipes private keys

cd /opt/schoolserver/xsce
git pull origin release-6.2

# get the iiab-factory
cd 
git clone https://github.com/iiab/iiab-factory
cd iiab-factory/scripts/osm-fixes
bash  ./fix-osm

# copy the menu files into doc root-- if they are not already there
  cd /opt/iiab-menu
  git pull
  ./cp-menus

# adjust the flags in local_vars
grep xsce_gateway_enabled /opt/schoolserver/xsce/vars/local_vars.yml
if [ $? -ne 0 ]; then
  echo "xsce_gateway_enabled: false" >> /opt/schoolserver/xsce/vars/local_vars.yml
else
  sed -i -e /^xsce_gateway_enabled.*/xsce_gateway_enabled: false/ /opt/schoolserver/xsce/vars/local_vars.yml
fi

grep services_externally_visible /opt/schoolserver/xsce/vars/local_vars.yml
if [ $? -ne 0 ]; then
  echo "services_externally_visible: true" >> /opt/schoolserver/xsce/vars/local_vars.yml
else
  sed -i -e /^services_externally_visible.*/services_externally_visible: true/ /opt/schoolserver/xsce/vars/local_vars.yml
fi

# blast the services enabled into config-vars
#cp ./config_vars.yml /etc/xsce/config_vars.yml

# don't let the /home directory be empty
if [ ! -f /library/www/html/home/index.html ]; then
   cp /library/www/html/iiab-menu/samples/content-ready-index.html /library/www/html/home/index.html
fi

# fetch the openstreetmap up to level 8 --adds 200MB
rsync -av xsce.org:/downloads/content/osm8.tar.gz /tmp
tar xzf /tmp/osm8.tar.gz --directory /library/knowledge

# We need to replace kalite 0.16 with 0.17 -- not every time this script is run
# and only if image was created with 0.16
if [ -f /usr/share/kalite/docs/_build ]; then
   rm -rf /library/ka-lite
   rm -rf /usr/share/kalite
   cd /opt/schoolserver/xsce
   ./runtags kalite
fi

./runansible

# fetch the online documents into image for offline use
cd /opt/schoolserver/xsce/scripts
./refresh-wiki-docs.sh


