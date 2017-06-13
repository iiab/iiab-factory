#!/bin/bash -x
# lock down root and pi (where appropriate) accounts
# put keys in iiab-admin for support
set -e

# Try to determin if this is raspbian
PLATFORM=`cat /etc/*release|grep ^ID=|cut -f2 -d=`

ADMIN_SSH=/home/iiab-admin/.ssh

mkdir -p $ADMIN_SSH
cp ../keys/developers_authorized_keys $ADMIN_SSH/authorized_keys
chmod 700 $ADMIN_SSH
chmod 600 $ADMIN_SSH/authorized_keys
chown -R iiab-admin:iiab-admin $ADMIN_SSH

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
