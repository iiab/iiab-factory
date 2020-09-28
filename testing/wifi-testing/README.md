*Wifi Connection Tester for Raspberry Pi*

## The Problem

Different versions of the wifi firmware allow different numbers of maximum wifi connections to hostapd.
This utility helps test how many such connections are allowed for a given configuration

## On a suitable client

* Use a non-IIAB Raspberry Pi as the client.
* Run wifi-tester.py from this directory.
* At the very least hostapd should not be running and wlan0 should be available
* The initial connection can take some time.

## On the test IIAB server

* Add the following two lines to /etc/hostapd/hostapd.conf
  * ctrl_interface=/var/run/hostapd
  * ctrl_interface_group=0

run ctl-hostapd to do this.

* Run stat-serve.py from this directory

## Hardware

This utility expects many USB WiFi dongles, which can be ganged together on a USB hub.

## Known Problems

* A Raspberry Pi client can be overwhelmed when USB dongles are attached
* Make sure all dongles are powered off when starting client.
* Power on the USB hubs one at a time.
* It can happen that a few dongles do not connect. Power off and try again.
* An attempt is made to clone WiFi interfaces to get two connections, but most dongles
do not support this. August, 2020 This is disabled.
