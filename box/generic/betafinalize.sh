#!/bin/bash
# Just do minimal resetting -- and prepare for image duplication

# Try to determin if this is raspbian
PLATFORM=`cat /etc/*release|grep ^ID=|cut -f2 -d=`

# use environmnt variables discovered by XSCE
source /etc/xsce/xsce.env

# openvpn needs unique identities
rm -f /etc/xsce/uuid
echo "Default handle" > /etc/xsce/handle

if [ "PLATFORM" = "OLPC" ]; then
  rm -f /.olpc-configured
  rm -f /home/olpc/.olpc-configured
  rm -rf /home/olpc/.sugar /home/olpc/.gconf* /home/olpc/.local.share.telepathy
  rm -f /etc/alsa/sound.state
fi

# probably will be running on new hardware -- forget the adapters
if [ "$OS" = "Fedora" ]; then
  rm -rf /etc/NetworkManager/system-connections/*
fi

# record the git hash so clonezilla can pick it up -- cz does not have git
pushd /opt/schoolserver/xsce
HASH=`git log --pretty=format:'g%h' -n 1`
YMD=$(date +%y%m%d)
echo $HASH > /etc/xsce/image-hash
echo $YMD > /etc/xsce/image-date
popd
rm -f /etc/ssh/ssh_host_rsa_key{,.pub}
rm -f /etc/sysconfig/network
rm -rf /home/.devkey.html
rm -f /root/.netrc
# the following will probably alread be done in minimize script
touch /.resize-rootfs


