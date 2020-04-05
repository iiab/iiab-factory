#!/bin/bash
# remove all the proprietary and non generic data


# the secure-accounts.sh  script renives developer credentials
source ./secure-accounts.sh
rm -f /root/.netrc

# if this is a Raspberry Pi GUI pixel version (think young kids) -nuc history
if [ -f /etc/lightdm/lightdm.conf -a "$PLATFORM" = "raspbian" ]; then
  su pi -c history -cw
  su iiab-admin -c history -cw
  history -cw
fi

# place developers' keys enabling remote access which becomes root with sudo su
mkdir -p /home/iiab-admin/.ssh
cp -f ../keys/developers_authorized_keys /home/iiab-admin/.ssh/authorized_keys
chown iiab-admin:iiab-admin /home/iiab-admin/.ssh/authorized_keys
chmod 640 /home/iiab-admin/.ssh/authorized_keys

# remove any aliases we might have added
rm -f /root/.bash_aliases
rm -f /home/iiab-admin/.bash_aliases
cp -f /home/pi/.bashrc /root/.bashrc

# put our own aliases in place, destroying any others in the process
cp -f bash_aliases /root/.bash_aliases


# none of the FINAL images should have openvpn enabled
systemctl disable openvpn@xscenet.service
systemctl disable openvpn

rm -rf /root/tools

