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


# remove any aliases we might have added
rm -f /root/.bash_aliases
rm -f /home/iiab-admin/.bash_aliases

# put our own aliases in place, destroying any others in the process
cp -f bash_aliases /root/.bash_aliases
# none of the FINAL images should have openvpn enabled
systemctl disable openvpn@xscenet.service
systemctl disable openvpn

if [ "$PLATFORM" == 'raspbian' ]; then
   rm -f /etc/ssh/ssh_host*
   cp -f ../rpi/pibashrc /root/.bashrc
   echo -e g0adm1n\ng0adm1n | passwd iiab-admin
   echo -e raspberry\nraspberry | passwd pi
   
   # if hostkeys are missing, recreate them and restart sshd
   grep ssh-keygen /etc/rc.local
   if [ $? -ne 0 ]; then
      sed '/^exit.*/i ssh-keygen -A\nsystemctl restart sshd' /etc/rc.local
   fi
fi

# following removes standard files used by ghunt
rm -rf /root/tools
rm -f /root/.netrc
