Installs IIAB - if Ubuntu or Debian, run "sudo su -" then SKIP TO STEP 4

1. RUN "sudo su -" then "passwd pi" to SECURE published password
2. RUN "raspi-config" to set LOCALISATION OPTIONS
3. RUN "touch /boot/ssh" to enable incoming SSH after next reboot
4. OPTIONAL: if you have slow/pricey Internet, pre-position KA Lite's
   mandatory 0.9 GB English Pack (en.zip) within /tmp -- if nec grab a copy
   from http://pantry.learningequality.org/downloads/ka-lite/0.17/content/con$
5. RUN THIS SCRIPT: curl http://github.com/jvonau/iiab-factory/install-latest.txt | sudo bash
6. REBOOTS AUTOMATICALLY WHEN DONE (typically 1-to-3 hours later)
   which sets the hostname, improves RTC settings + memory mgmt
