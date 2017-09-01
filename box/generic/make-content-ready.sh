#!/bin/bash -x

# you must run ansible before running this
# and reboot so hostname take effect
# assumes kiwix, kalite are installed
# 1. Gets the latest version of the Kiwix Catalog and rebuilds the local catalog
# 2. Registers the Kalite install to avoid doing it manually
# 3. Gets the Kalite English Language Pack required even for other languages

# refresh kiwix catalog
iiab-cmdsrv-ctl GET-KIWIX-CAT

# rebuild local library.xml
/usr/bin/iiab-make-kiwix-lib

export KALITE_HOME=/library/ka-lite

# register with kalite - not sure if necessary or what user/passwd to supply
# kalite manage register - nope
kalite manage generate_zone

# get kalite English language pack - takes awhile and seems to re-download if run again
kalite manage retrievecontentpack download en
