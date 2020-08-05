*Wifi Connection Tester for Raspberry Pi*

## The Problem

Different versions of the wifi firmware allow different numbers of maximum wifi connections to hostapd.
This utility helps test how many such connections are allowed for a given configuration

## On a suitable client

* Use a non-IIAB Raspberry Pi as the client.
* Run wifi_tester.py from this directory.
* At the very least hostapd should not be running and wlan0 should be available

## On the test IIAB server

* Add the following two lines to /etc/hostapd/hostapd.conf
  * ctrl_interface=/var/run/hostapd
  * ctrl_interface_group=0

* Run wifi-stat.py from this directory

## Hardware

This utility expects many USB WiFi dongles, which can be ganged together on a USB hub.

## Known Problems

* An attempt is made to clone WiFi interfaces to get two connections, but most dongles
do not support this.
