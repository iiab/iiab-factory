#!/bin/bash
# remove all the proprietary and non generic data

# use environmnt variables discovered by XSCE
source /etc/xsce/xsce.env

# the betafinalize script manages image dup tasks
source ./betafinalize.sh

# if this is a Raspberry Pi GUI pixel version (think young kids) -nuc history
if [ -f /etc/lightdm/lightdm.conf -a "$PLATFORM" = "raspbian" ]; then
  history -cw
fi

rm -f /root/.bash_aliases
rm -f /root/.ssh/*

# decided to let the expansion service handle -- works all platforms
#grep init_resize.sh /boot/cmdline.txt
#if [ $? -ne 0 ] &&[ "$PLATFORM" = "raspbian" ]; then
#  cp -f ./cmdline.txt /boot/cmdline.txt
#fi

# remove any aliases we might have added
rm -f /root/.bash_aliases
rm -f /home/xsce-admin/.bash_aliases

# put our own aliases in place, destroying any others in the process
cp -f bash_aliases /home/xsce-admin/.bash_aliases

# Maybe this could be accomplished via deletion of xsce_cmdsrv.0.2.db
#if [ "$OS"  = "debian" ]; then
if [ 1 -eq 0 ]; then
   apt-get install sqlite3
   cat <<EOF > sqlite3 /opt/schoolserver/xsce_cmdsrv/xsce_cmdsrv.0.2.db

   delete * from commands;
   delete * from jobs;
   EOF 
fi

# none of the FINAL images should have openvpn enabled
systemctl disable openvpn@xscenet.service

rm -rf /root/iiab-factory
rm -rf /root/tools
cd /root

