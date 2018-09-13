#!/bin/bash -e

CURR_VER="undefined"    # Ansible version you currently have installed
GOOD_VER="2.6.4"    # For XO laptops (pip install) & CentOS (yum install rpm)
# On other OS's we attempt the latest from PPA, which might be more recent

export DEBIAN_FRONTEND=noninteractive

echo -e '\n\nSTRONGLY RECOMMENDED PREREQUISITE: (1) remove all prior versions of Ansible using "apt purge ansible" and/or "pip uninstall ansible" and (2) clear out all lines containing ansible from /etc/apt/sources.list and /etc/apt/sources.list.d/*\n'

echo -e 'COMPLETE INSTALL INSTRUCTIONS:\nhttps://github.com/iiab/iiab/wiki/IIAB-Installation#do-everything-from-scratch\n'

echo -e 'VERIFY YOU'"'"'RE ONLINE BEFORE RUNNING THIS: /opt/iiab/iiab-factory/scripts/ansible-2.6.x'
echo -e 'Alternative: Run /opt/iiab/iiab-factory/scripts/ansible for the very latest Ansible\n'

if [ $(command -v ansible-playbook) ]; then    # "command -v" is POSIX compliant; also catches built-in commands like "cd"
    CURR_VER=`ansible --version | head -1 | awk '{print $2}'`    # To match iiab-install.  Was: CURR_VER=`ansible --version | head -n 1 | cut -f 2 -d " "`
    echo "Currently installed Ansible: $CURR_VER"
    echo -e "INTERNET-IN-A-BOX GENERALLY REQUIRES ANSIBLE VERSION: $GOOD_VER or higher"
    if [ -f /etc/centos-release ] || [ -f /etc/fedora-release ]; then
        echo "Please use your system's package manager (or pip if nec) to update Ansible."
        exit 0
    elif [ -f /etc/olpc-release ]; then
        echo 'Please use pip package manager to update Ansible.'
        exit 0
    fi
else
    echo -e 'Ansible NOT found on this computer.'
    echo -e "INTERNET-IN-A-BOX GENERALLY REQUIRES ANSIBLE VERSION: $GOOD_VER or higher"
fi

echo -e 'scripts/ansible-2.6.x will now try to install Ansible 2.6.x...\n'
if [ -f /etc/olpc-release ]; then
    yum -y install ca-certificates nss
    yum -y install git bzip2 file findutils gzip hg svn sudo tar which unzip xz zip libselinux-python
    yum -y install python-pip python-setuptools python-wheel patch
    # Can above 3 lines be merged into 1 line?
    pip install --upgrade pip setuptools wheel #EOL just do it
    pip install ansible==$GOOD_VER --disable-pip-version-check
elif [ -f /etc/centos-release ]; then
    yum -y install ansible
elif [ -f /etc/debian_version ]; then    # Includes Debian, Ubuntu & Raspbian

    echo -e '\napt update; install dirmngr; PPA to /etc/apt/sources.list.d/iiab-ansible.list\n'
    apt update
    apt -y install dirmngr    # Raspbian needs.  Formerly: python-pip python-setuptools python-wheel patch
    echo "deb http://ppa.launchpad.net/ansible/ansible-2.6/ubuntu xenial main" \
         > /etc/apt/sources.list.d/iiab-ansible.list

    echo -e '\nIF YOU FACE ERROR "signatures couldn'"'"'t be verified because the public key is not available" THEN REPEATEDLY RE-RUN "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367"\n'
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367

    echo -e '\napt update; apt install ansible\n'
    apt update
    apt -y --allow-downgrades install ansible
    echo -e '\nPlease verify Ansible using "ansible --version" and/or "apt -a list ansible"'

    echo -e '\n\nPPA source "deb http://ppa.launchpad.net/ansible/ansible-2.6/ubuntu xenial main" successfully saved to /etc/apt/sources.list.d/iiab-ansible.list'
    echo -e '\nIF *OTHER* ANSIBLE SOURCES ARE ALSO IN THE LIST BELOW, PLEASE MANUALLY REMOVE THEM TO ENSURE ANSIBLE UPDATES CLEANLY: (then re-run this script to be sure!)\n'
    grep '^deb .*ansible' /etc/apt/sources.list /etc/apt/sources.list.d/*.list | grep -v '^/etc/apt/sources.list.d/iiab-ansible.list:' || true    # Override bash -e (instead of aborting at 1st error)
else
    echo -e "\nEXITING: Could not detect your OS (unsupported?)\n"
    exit 1
fi

# Needed?
mkdir -p /etc/ansible
echo -e '[local]\nlocalhost\n' > /etc/ansible/hosts
