#!/bin/bash -x

# assumes git installed and following done
# cd /opt/iiab
# git clone https://github.com/iiab/iiab-factory --depth 1
# cd iiab-factory/box/generic
# ./setup.sh (this script)

if [[ -f ../../factory-settings ]]; then
  source ../../factory-settings
else
  echo 'cd /opt/iiab/iiab-factory/box/generic before running this.'
  exit 1
fi

pushd /opt/iiab
git clone https://github.com/iiab/iiab-menu --depth 1

# should be softcoded in factory-settings
git clone https://github.com/iiab/iiab --depth 1

cd  iiab/scripts
./ansible

popd

# install local_vars.yml - this should be OS dependent at some point
./merge_local_vars.sh ../vars/stock_vars.yml

# add in commands for xs-remote-{on/off}
cat << EOF > /usr/local/sbin/xs-remote-on
#!/bin/bash
# add command to control openvpn from command line

systemctl enable openvpn@xscenet
systemctl start openvpn@xscenet
EOF
chmod 755 /usr/local/sbin/xs-remote-on
cat << EOF > /usr/local/sbin/xs-remote-off
#!/bin/bash
# add command to control openvpn from command line

systemctl disable openvpn@xscenet
systemctl stop openvpn@xscenet
EOF
chmod 755 /usr/local/sbin/xs-remote-off

echo 'cd /opt/iiab/iiab/'
echo './runansible'
