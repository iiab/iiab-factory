#!/bin/bash
# Just do minimal resetting -- and prepare for image duplication

# Try to determin if this is raspbian
PLATFORM=`cat /etc/*release|grep ^ID=|cut -f2 -d=`

# use environmnt variables discovered by XSCE
source /etc/iiab/iiab.env

# openvpn needs unique identities
rm -f /etc/iiab/uuid
#echo "Default handle" > /etc/iiab/handle

if [ "PLATFORM" = "OLPC" ]; then
  rm -f /.olpc-configured
  rm -f /home/olpc/.olpc-configured
  rm -rf /home/olpc/.sugar /home/olpc/.gconf* /home/olpc/.local.share.telepathy
  rm -f /etc/alsa/sound.state
fi

# record the git hash so clonezilla can pick it up -- cz does not have git
pushd /opt/iiab/iiab
HASH=`git log --pretty=format:'g%h' -n 1`
YMD=$(date +%y%m%d)
echo $HASH > /etc/iiab/image-hash
echo $YMD > /etc/iiab/image-date
popd

rm -f /etc/ssh/ssh_host_rsa_key{,.pub}
rm -f /etc/sysconfig/network
rm -rf /home/.devkey.html
rm -f /root/.netrc
# the following will probably alread be done in minimize script
touch /.resize-rootfs

rm -rf /root/tools

# remove host keys
rm -f /etc/ssh/*_key*

# reset the iiab-admin password back to default
echo g0adm1n | passwd --stdin iiab-admin

