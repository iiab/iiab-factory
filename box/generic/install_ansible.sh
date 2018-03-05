#!/bin/bash -e
# required to start loading IIAB with ansible

#   Author: Jerry Vonau <jvonau3(at)gmail(dot)com>
#Add GPL copyright release wording

FOUND=""
URL="NA"
if [ $(which ansible-playbook) ]; then
    echo "Ansible installed exiting..."
    exit 0
fi
echo "Installing --- Please Wait"
if [ -f /etc/fedora-release ]; then
    VER=`grep VERSION_ID /etc/*elease | cut -d= -f2`
    URL=https://github.com/jvonau/iiab/blob/ansible/vars/fedora-$VER.yml
    dnf -y upgrade
    dnf -y install ansible git bzip2 file findutils gzip hg svn sudo tar which unzip xz zip libselinux-python
    dnf -y install python-pip python-setuptools python-wheel patch
    FOUND="yes"
    FAMILY="redhat"
fi
# might have to revisit dependencies with a redhat dialect
# ansible python-kerberos python-selinux python-winrm python-xmltodict sshpass bzip2 file findutils gzip tar unzip zip python-keyczar python-boto python-dnspython python-pyrax python-sphere

if [ -f /etc/centos-release ]; then
    yum -y upgrade
    yum -y install ca-certificates nss epel-release
    yum -y install ansible git bzip2 file findutils gzip hg svn sudo tar which unzip xz zip libselinux-python
    yum -y install python-pip python-setuptools python-wheel patch
    FOUND="yes"
    FAMILY="redhat"
fi
if [ -f /etc/olpc-release ]; then
    yum -y upgrade
    yum -y install ca-certificates nss
    yum -y install git bzip2 file findutils gzip hg svn sudo tar which unzip xz zip libselinux-python
    yum -y install python-pip python-setuptools python-wheel patch
    pip install --upgrade pip setuptools wheel #EOL just do it
    FOUND="yes"
    FAMILY="olpc"
fi

if [ -f /etc/debian_version ]; then
# might pickup usbmount confirm ppa location
#    echo "deb http://ppa.launchpad.net/ansible/ansible/ubuntu trusty main" >> /etc/apt/sources.list
#    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367
#    apt-get update
    apt-get install ansible git python-pip python-setuptools python-wheel patch
#    apt-get install ansible python-kerberos python-selinux python-winrm python-xmltodict sshpass bzip2 file findutils gzip tar unzip zip python-keyczar python-boto python-dnspython python-pyrax python-sphere
    FOUND="yes"
    FAMILY="debian"
fi
if [ `grep -qi ubuntu /etc/lsb-release` ] ||  [ `grep -qi ubuntu /etc/os-release` ]; then
    apt-get update
# confirm PPA location
#    apt-get install software-properties-common
#    apt-add-repository ppa:ansible/ansible
#    apt-get update
    apt-get install ansible git python-pip python-setuptools python-wheel patch
#    apt-get install ansible python-kerberos python-selinux python-winrm python-xmltodict sshpass bzip2 file findutils gzip tar unzip zip python-keyczar python-boto python-dnspython python-pyrax python-sphere
    FOUND="yes"
    FAMILY="debian"
fi
# Has 2.2.1
if [ `grep -qi raspbian /etc/*elease` ]; then
    apt-get update
#    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367
#    apt-get update
    apt-get install ansible git python-pip python-setuptools python-wheel patch
#    apt-get install ansible python-kerberos python-selinux python-winrm python-xmltodict sshpass bzip2 file findutils gzip tar unzip zip python-keyczar python-boto python-dnspython python-pyrax python-sphere
    FOUND="yes"
    FAMILY="debian"
fi

if [ ! $FOUND = "yes" ]; then
    echo 'WARN: Could not detect distro or distro unsupported'
    exit 1
fi

# latest pip 2.2 is 2.2.3.0 on 2017-07-07
# ansible-2.3.1.0-1.el7.noarch.rpm from 2017-06-01

### start ansible pip install TODO add venv location /opt/iiab/anisble
if [ $FAMILY = "olpc" ]; then
    pip install ansible==2.2.1 --disable-pip-version-check
    VER=`ansible --version|head -n 1|cut -f 2 -d " "`
    echo "ansible version installed via pip $VER"
fi

#if [ $FAMILY = "debian" ]; then
#   rpm -e ansible
#   pip install ansible==2.2.1 --disable-pip-version-check
#fi
VER=`ansible --version|head -n 1|cut -f 2 -d " "`
echo "ansible version installed via package manager $VER"

#if [ $FAMILY = "debian" ]; then
#    echo 'WARN: Trying to install ansible via pip without some dependencies'
#    echo 'WARN: Not all functionality of ansible may be available'
#    pip install ansible==2.3.1 --disable-pip-version-check
#fi
mkdir -p /etc/ansible/
echo -e '[local]\nlocalhost\n' > /etc/ansible/hosts

### end ansible routine
###
# other pip upgrades here if needed
###
