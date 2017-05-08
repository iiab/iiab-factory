#!/bin/bash -x

# make sure the base operating system is updated -- the base image may be stale
apt-get -y update
apt-get -y dist-upgrade
apt-get -y clean
apt-get -y autoremove
reboot
