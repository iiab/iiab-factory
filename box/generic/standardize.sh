#!/bin/bash -x
# keep a list of all that finalizes images
set -e

# Try to determin if this is raspbian
PLATFORM=`cat /etc/*release|grep ^ID=|cut -f2 -d=`

# this script can be run repeatedly. As the last step, run finalize script.
#  finalize resets authorized keys to authorized developers -- wipes private keys

cd /opt/schoolserver/xsce
git pull origin release-6.2

# get the iiab-factory
cd /root
if [ ! -d iiab-factory ]; then
  git clone https://github.com/iiab/iiab-factory
  cd iiab-factory
else
  cd /root/iiab-factory
  git pull origin master
fi
pushd ./content/osm-fixes
bash  ./fix-osm
popd

# copy the menu files into doc root-- if they are not already there
  pushd /opt/iiab-menu
  git pull
  ./cp-menus
  popd

# blast the gui selected settings into place to standardize images
# cp -f /root/tools/config_vars.yml /etc/xsce/

# adjust the flags in local_vars
# xsce_hostname: box
# xsce_home_url: /home
# host_ssid: "Internet in a Box"
# hostapd_secure: False
# hostapd_password: "MYPASSWORD"

set +e
grep xsce_hostname /opt/schoolserver/xsce/vars/local_vars.yml
if [ $? -ne 0 ]; then
  echo "xsce_hostname: box" >> /opt/schoolserver/xsce/vars/local_vars.yml
else
  sed -i -e 's/^xsce_hostname.*/xsce_hostname: box/' /opt/schoolserver/xsce/vars/local_vars.yml
fi
set +e
grep xsce_home_url /opt/schoolserver/xsce/vars/local_vars.yml
if [ $? -ne 0 ]; then
  echo "xsce_home_url: /home" >> /opt/schoolserver/xsce/vars/local_vars.yml
else
  sed -i -e 's/^xsce_home_url.*/xsce_home_url: /home' /opt/schoolserver/xsce/vars/local_vars.yml
fi

grep host_ssid /opt/schoolserver/xsce/vars/local_vars.yml
if [ $? -ne 0 ]; then
  echo "host_ssid: 'Internet in a Box'" >> /opt/schoolserver/xsce/vars/local_vars.yml
else
  sed -i -e 's/^host_ssid.*/host_ssid: "Internet in a Box"' /opt/schoolserver/xsce/vars/local_vars.yml
fi

grep hostapd_secure /opt/schoolserver/xsce/vars/local_vars.yml
if [ $? -ne 0 ]; then
  echo "hostapd_secure: False" >> /opt/schoolserver/xsce/vars/local_vars.yml
else
  sed -i -e 's/^hostapd_secure.*/host_secure: False' /opt/schoolserver/xsce/vars/local_vars.yml
fi

grep host_password /opt/schoolserver/xsce/vars/local_vars.yml
if [ $? -ne 0 ]; then
  echo "host_password: MYPASSWORD" >> /opt/schoolserver/xsce/vars/local_vars.yml
else
  sed -i -e 's/^host_password.*/host_password: MYPASSWORD' /opt/schoolserver/xsce/vars/local_vars.yml
fi

grep xsce_gateway_enabled /opt/schoolserver/xsce/vars/local_vars.yml
if [ $? -ne 0 ]; then
  echo "xsce_gateway_enabled: false" >> /opt/schoolserver/xsce/vars/local_vars.yml
else
  sed -i -e 's/^xsce_gateway_enabled.*/xsce_gateway_enabled: false/' /opt/schoolserver/xsce/vars/local_vars.yml
fi

grep services_externally_visible /opt/schoolserver/xsce/vars/local_vars.yml
if [ $? -ne 0 ]; then
  echo "services_externally_visible: true" >> /opt/schoolserver/xsce/vars/local_vars.yml
else
  sed -i -e 's/^services_externally_visible.*/services_externally_visible: true/' /opt/schoolserver/xsce/vars/local_vars.yml
fi

set -e
# don't let the /home directory be empty
if [ ! -f /library/www/html/home/index.html ]; then
   cp /library/www/html/iiab-menu/samples/sampler.html /library/www/html/home/index.html
fi

# We need to replace kalite 0.16 with 0.17 -- not every time this script is run
# and only if image was created with 0.16
if [ -e /usr/share/kalite/docs/_build ]; then
   rm -rf /library/ka-lite
   rm -rf /usr/share/kalite
   cd /opt/schoolserver/xsce
   ./runtags kalite
fi

# getting content is best done interactively
# get some zim content
#wget http://download.kiwix.org/portable/wikipedia/kiwix-0.9+wikipedia_en_ray_charles_2015-06.zip 

# change the default user for raspbian pixel from pi to xsce-admin
if [ -f /etc/lightdm/lightdm.conf ]; then
#  sed -i -e 's/^autologin-user=pi/autologin-user=xsce-admin/' /etc/lightdm/lightdm.conf
   sleep 1
else
  if [ $PLATFORM = "raspberry" ]; then
    # this is a headless install -- so disable pi password login
    sed -i -e 's/^pi\:.*/pi\:\*\:17228\:0\:99999\:\:\:\:/' /etc/shadow
  fi
fi

# prevent root password
sed -i -e 's/^root\:.*/root\:\*\:17228\:0\:99999\:\:\:\:/' /etc/shadow

# fetch the online documents into image for offline use
cd /opt/schoolserver/xsce/scripts
./refresh-wiki-docs.sh

# the kiwix index is no longer initialized by cp-menu
/usr/bin/xsce-make-kiwix-lib

cd /opt/schoolserver/xsce/
# perhaps no need for the next step, because "Install Configured Options" button #   does almost the same
#./runansible

# make sure the base operating system is updated -- the base image may be stale
apt-get -y update
apt-get -y dist-upgrade
apt-get -y clean
apt-get -y autoremove
reboot
