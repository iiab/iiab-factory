#!/bin/bash -e
BASE=/opt/iiab

if [ -f /etc/iiab/iiab-complete ]; then
    systemctl disable iiab-installer
    exit 0
fi

cd $BASE/iiab
./iiab-install

if [ ! -f $BASE/iiab-admin-console/complete ]; then
    cd $BASE/iiab-admin-console
    ./install
    touch $BASE/iiab-admin-console/complete
fi
if [ ! -f $BASE/iiab-menu/complete ]; then
    cd $BASE/iiab-menu
    ./cp-menus
    touch $BASE/iiab-menu/complete
fi
$BASE/iiab-factory/scripts/post-install
touch /etc/iiab/iiab-complete
reboot
