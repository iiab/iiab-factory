#!/bin/bash
# Copied from: https://github.com/iiab/iiab-factory/blob/master/install.txt

# To install Internet-in-a-Box (IIAB) 8.3 / pre-release onto Raspberry Pi OS,
# Ubuntu 24.04+, Linux Mint 22+ or Debian 12+, run this 1-line installer:
#
#                     curl iiab.io/install.txt | bash

# 1. WARNING: NOOBS IS *NOT* SUPPORTED, as its partitioning is very different.
#    On a Raspberry Pi, WE RECOMMEND YOU INSTALL THE LATEST RASPBERRY PI OS:
#    https://www.raspberrypi.com/documentation/computers/getting-started.html
#    To attempt IIAB 8.3 on another Linux see the manual/legacy instructions:
#    https://github.com/iiab/iiab/wiki/IIAB-Installation#do-everything-from-scratch

# 2. An Ethernet cable is HIGHLY RECOMMENDED during installation, as this is
#    more reliable than WiFi (and faster!)  WARNING: IF YOU CONNECT YOUR IIAB'S
#    INTERNAL WIFI TO THE INTERNET OVER 5 GHz, YOU'LL PREVENT OLDER LAPTOPS/
#    PHONES/TABLETS (WHICH REQUIRE 2.4 GHz) FROM CONNECTING TO YOUR IIAB'S
#    INTERNAL HOTSPOT.  See: "wifi_up_down: True" in /etc/iiab/local_vars.yml

# 3. Run 'sudo raspi-config' on Raspberry Pi, to set LOCALISATION OPTIONS

# 4. OPTIONAL: if you have slow/pricey Internet, pre-position KA Lite's
#    mandatory 0.9 GB English Pack (en.zip) within /tmp -- you can grab it from
#    https://pantry.learningequality.org/downloads/ka-lite/0.17/content/contentpacks/en.zip

# 5. Follow on-screen instructions (TYPE 'sudo iiab' TO RESUME IF EVER NECESS!)

# 6. Within about 1-2 hours, it will announce that INTERNET-IN-A-BOX (IIAB)
#    SOFTWARE INSTALL IS COMPLETE, prompting you to reboot...TO ADD CONTENT!

# Thanks   For   Building   Your   Own   Library   To   Serve   One   &   All
#
# DRAFT IIAB 8.3 Release Notes:
# https://github.com/iiab/iiab/wiki/IIAB-8.3-Release-Notes
#
# SPECIAL THANKS to the countries + communities + volunteers working non-stop
# to bring about IIAB 8.3!  https://internet-in-a-box.org/contributing.html
#
# IIAB Dev Team
# http://FAQ.IIAB.IO

set -e                                   # Exit on error (avoids snowballing)
export DEBIAN_FRONTEND=noninteractive    # Bypass (most!) interactive questions

# Save script to /usr/sbin/iiab (easy resume/continue mnemonic 'sudo iiab')
sudo mv /usr/sbin/iiab /usr/sbin/iiab.old 2> /dev/null || true    # Overrides 'set -e'
curl https://raw.githubusercontent.com/iiab/iiab-factory/master/iiab | sudo tee /usr/sbin/iiab > /dev/null
sudo chmod 0755 /usr/sbin/iiab

# Run install script!
sudo /usr/sbin/iiab "$@"    # Pass on all CLI params (PR #s) for easy
# community testing -- SEE "Install optional PR's" in /usr/sbin/iiab
# EXAMPLE: curl iiab.io/install.txt | bash -s 361 2604 2607
