#!/bin/bash -e
BASE=/opt/iiab
FLAGS=$BASE/iiab-factory/flags
REINSTALL=""

if [ "$1" = "--reinstall" ]; then
    rm $FLAGS/*
    REINSTALL="--reinstall"
fi

if [ -f $FLAGS/iiab-complete ]; then
    echo -e 'iiab-complete'
    systemctl disable iiab-installer
    exit 0
fi

cd $BASE/iiab
./iiab-install $REINSTALL

if [ ! -f $FLAGS/iiab-admin-console-complete ]; then
    cd $BASE/iiab-admin-console
    ./install
    touch $FLAGS/iiab-admin-console-complete
    else
    echo -e 'iiab-admin-console complete'
fi
if [ ! -f $FLAGS/iiab-menu-complete ]; then
    cd $BASE/iiab-menu
    ./cp-menus
    touch $FLAGS/iiab-menu-complete
    else
    echo -e 'iiab-menu complete'
fi
$BASE/iiab-factory/scripts/post-install
touch $FLAGS/iiab-complete
