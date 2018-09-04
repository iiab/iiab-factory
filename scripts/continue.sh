#!/bin/bash -e
BASE=/opt/iiab

if [ -f /etc/iiab/iiab-complete ]; then
    systemctl disable iiab-installer
    exit 0
fi

$BASE/iiab/iiab-install
$BASE/iiab-admin/install
$BASE/iiab/iiab-menu/cp-menus
$BASE/iiab-factory/scripts/post-install
touch /etc/iiab/iiab-complete
reboot
