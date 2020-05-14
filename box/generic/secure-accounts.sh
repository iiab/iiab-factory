#!/bin/bash
# put keys in root for support
set -e

# Try to determin if this is raspbian
PLATFORM=`cat /etc/*release|grep ^ID=|cut -f2 -d=`

ADMIN_SSH=/root/.ssh

mkdir -p $ADMIN_SSH
cp ../keys/developers_authorized_keys $ADMIN_SSH/authorized_keys
chmod 700 $ADMIN_SSH
chmod 600 $ADMIN_SSH/authorized_keys
chown -R root:root $ADMIN_SSH

if [ "$PLATFORM" = "raspbian" ]; then
  # this is a headless install -- so disable pi password login
  #sed -i -e 's/^pi\:.*/pi\:\*\:17228\:0\:99999\:\:\:\:/' /etc/shadow
  cp -f ../rpi/pibashrc /root/.bashrc
  echo -e "g0adm1n\ng0adm1n" | passwd iiab-admin
  echo -e "raspberry\nraspberry"| passwd pi
fi

# prevent root password
sed -i -e 's/^root\:.*/root\:\*\:17228\:0\:99999\:\:\:\:/' /etc/shadow
rm -f /root/.ssh/id_rsa
