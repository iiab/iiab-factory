#!/bin/bash
# Just do minimal resetting -- and prepare for image duplication

rm -f /root/.netrc

rm -rf /root/tools

# remove host keys
rm -f /etc/ssh/*_key*

# reset the iiab-admin password back to default
echo g0adm1n | passwd --stdin iiab-admin

