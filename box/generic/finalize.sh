#!/bin/bash
# remove all the proprietary and non generic data


# the secure-accounts.sh  script removes developer credentials
source ./secure-accounts.sh

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

# none of the FINAL images should have openvpn enabled
systemctl disable openvpn@xscenet.service
systemctl disable openvpn

# following removes standard files used by ghunt
rm -rf /root/tools
rm -f /root/.netrc
if [ "$PLATFORM" == 'raspbian' ]; then
   cp -f ../rpi/pibashrc /root/.bashrc
   echo -e g0adm1n\ng0adm1n | passwd iiab-admin
   echo -e raspberry\nraspberry | passwd pi
   
   # if hostkeys are missing, recreate them and restart sshd
   if [ ! -f /etc/ssh/ssh_host_rsa_key.pub ]; then
      sed '/^exit.*/i ssh-keygen -A\nsystemctl restart sshd' /etc/rc.local
   fi
fi

