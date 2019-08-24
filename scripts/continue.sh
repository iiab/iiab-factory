#!/bin/bash -e
BASE=/opt/iiab
FLAGS=$BASE/iiab-factory/flags

if [ -f $FLAGS/iiab-complete ]; then
    echo -e 'iiab-complete'
    systemctl disable iiab-installer
    exit 0
fi
/usr/sbin/iiab
