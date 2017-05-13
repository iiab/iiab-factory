#!/bin/bash -x

# assumes git installed and following done
# cd /opt
# git clone https://github.com/iiab/iiab-factory --depth 1
# cd iiab-factory/box/generic
# ./setup.sh (this script)

if [[ -f ../../factory-settings ]]; then
  source ../../factory-settings
else
  echo 'cd /opt/iiab-factory/box/generic before running this.'
  exit 1
fi

pushd /opt
git clone https://github.com/tim-moody/iiab-menu --depth 1

mkdir -p schoolserver

cd schoolserver

# should be softcoded in factory-settings
git clone https://github.com/XSCE/xsce --depth 1 -b release-6.2

cd  xsce/scripts
./ansible

popd

# install local_vars.yml - this should be OS dependent at some point
./merge_local_vars.sh ../vars/stock_vars.yml

# add in aliases for xs-remote-{on/off}
grep xs-remote-on /root/.bashrc
if [ $? -ne 0 ];then
   cat << EOF >> /root/.bashrc

# add aliases to control openvpn from command line
alias xs-remote-on='systemctl enable openvpn@xscenet; systemctl start openvpn@xscenet'
alias xs-remote-off='systemctl disable openvpn@xscenet; systemctl stop openvpn@xscenet'
EOF
fi  

echo 'cd /opt/schoolserver/xsce/'
echo './runansible'
