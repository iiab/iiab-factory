#!/bin/bash -x
# download zim-tools, libzim, compile tools, and place in $PATH

PREFIX=/opt/iiab
cd $PREFIX
if [ ! -d "$PREFIX/zim-tools" ];then
   git clone https://github.com/openzim/zim-tools
fi
if [ ! -d "$PREFIX/libzim" ];then
   git clone https://github.com/openzim/libzim
fi

apt install -y libzstd-dev
apt install -y libdocopt-dev
apt install -y libgumbo-dev
apt install -y libmagic-dev
apt install -y liblzma-dev
apt install -y libxapian-dev
apt install -y libicu-dev
apt install -y docopt-dev
apt install -y ninja
apt install -y meson
apt install -y cmake
apt install -y pkgconf

cd $PREFIX/libzim
meson . build
ninja -C build install
if [ $? -ne 0 ];then
   echo Build of libzim failed. Quitting . . .
   exit 1
fi

cd $PREFIX/zim-tools
meson . build
ninja -C build
if [ $? -ne 0 ];then
   echo Build of zim-tools failed. Quitting . . .
   exit 1
fi


rsync -a $PREFIX/zim-tools/build/src/zim* /usr/local/sbin/

