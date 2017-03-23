#!/bin/bash
# remove all the proprietary and non generic data

# use environmnt variables discovered by XSCE
source /etc/xsce/xsce.env

# the betafinalize script manages image dup tasks
source ./betafinalize.sh

# if this is a Raspberry Pi GUI pixel version (think young kids) -nuc history
if [ -f /etc/lightdm/lightdm.conf -a "$PLATFORM" = "raspbian" ]; then
  su pi -c history -cw
  su xsce-admin -c history -cw
  history -cw
fi

rm -f /root/.ssh/*

# place developers' keys enabling remote access which becomes root with sudo su
mkdir -p /home/xsce-admin/.ssh
cp -f ../keys/developers_authorized_keys /home/xsce-admin/.ssh/authorized_keys
chown xsce-admin:xsce-admin /home/xsce-admin/.ssh/authorized_keys
chmod 640 /home/xsce-admin/.ssh/zuthorized_keys

# decided to let the expansion service handle -- works all platforms
#grep init_resize.sh /boot/cmdline.txt
#if [ $? -ne 0 ] &&[ "$PLATFORM" = "raspbian" ]; then
#  cp -f ./cmdline.txt /boot/cmdline.txt
#fi

# remove any aliases we might have added
rm -f /root/.bash_aliases
rm -f /home/xsce-admin/.bash_aliases

# put our own aliases in place, destroying any others in the process
cp -f bash_aliases /root/.bash_aliases


# none of the FINAL images should have openvpn enabled
systemctl disable openvpn@xscenet.service

cd /root
rm -rf /root/iiab-factory
rm -rf /root/tools

