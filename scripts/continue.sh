#!/bin/bash -e
BASE=/opt/iiab

if [ -f /etc/iiab/iiab-complete ]; then
    systemctl disable iiab-installer
    exit 0
fi

cd $BASE/iiab
./iiab-install
cd $BASE/iiab-admin-console
./install
cd $BASE/iiab/iiab-menu
./cp-menus
$BASE/iiab-factory/scripts/post-install
touch /etc/iiab/iiab-complete
reboot
