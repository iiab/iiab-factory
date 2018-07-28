#!/bin/bash
# Functions useful to manipulate SD card content
# All sizes in bytes, unless otherwise noted

# number of partitions on IIAB may change
LIBRARY_PARTITION=2
if [ -f /etc/iiab/iiab.env ]; then
   source /etc/iiab/iiab.env
else
   PRODUCT=IIAB 
   VERSION=6.5
fi

min_device_size(){
   # Params:  in: full path of file containing image
   #  -- echos out: bytes

   # get the next loop device
   DEVICEREF=$(losetup -f)
   $(losetup -P $DEVICEREF $1)
   if [ $? -ne 0 ];then
      echo failed to create RAWDEVICE reference for $1
      losetup -d $DEVICEREF
      exit 1
   fi
   
   # what is the last partition on this device
   last=`fdisk -l $DEVICEREF | tail -n1 | cut -d" " -f1`
   part=${last:(-1)}
   PARTITION=${DEVICEREF}p${part}

   root_start=$(fdisk -l $DEVICEREF | grep $PARTITION | awk '{print $2}')

   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null
   block4k=`resize2fs -M -P $PARTITION | cut -d" " -f7`
   e2fsck -fy $PARTITION > /dev/null
   echo $(expr $block4k \* 4096 + $root_start \* 512)
   # clean up
   losetup -d $DEVICEREF
}

size_image(){
   # truncate last partition
   # param1: full path of the file containing IIAB image
   # param2 (optional): desired size in 4kblocks (smallest possible if not specified)
   # returns 0 on success

   # get the next loop device
   DEVICEREF=$(losetup -f)
   $(losetup -P $DEVICEREF $1)
   if [ $? -ne 0 ];then
      echo failed to create RAWDEVICE reference for $1
      losetup -d $DEVICEREF
      exit 1
   fi
   # what is the last partition on this device
   last=`fdisk -l $DEVICEREF | tail -n1 | cut -d" " -f1`
   part=${last:(-1)}
   PARTITION=${DEVICEREF}p${part}

   root_start=$(fdisk -l $DEVICEREF | grep $PARTITION | awk '{print $2}')

   # total prior sectors is 1 less than start of this one
   prior_sectors=$(( root_start - 1 ))

   # resize root file system
   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null
   if test $? -ne 0; then 
      losetup -d $DEVICEREF
      echo Failed to pass e2fsck before resize operation on $PARTITION
      exit 1
   fi
   if [ $# -lt 2 ]; then
     block4k=`resize2fs -P $PARTITION | cut -d" " -f7`
   else
     block4k=$(echo "$2 / 4096 " | bc )
   fi

   # do the real work of this function
   resize2fs -p $PARTITION $block4k

   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null
   if [ $? -ne 0 ];then
      echo failed to pass e2fsck format check after resize operation
      losetup -d $DEVICEREF
      exit 1
   fi

   # fetch the new size of ROOT PARTITION
   blocks4k=`e2fsck -n $PARTITION 2>/dev/null|grep blocks|cut -f5 -d" "|cut -d/ -f2`

   root_end=$( echo "$blocks4k * 8 + $prior_sectors" | bc )

   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null

   # resize root partition
   parted -s $DEVICEREF rm $LIBRARY_PARTITION
   parted -s $DEVICEREF unit s mkpart primary ext4 $root_start $root_end
   losetup -d $DEVICEREF

   copy_size=`echo "$blocks4k * 4096 + $prior_sectors * 512" | bc`
   copy4k=$(echo "($copy_size / 4096) + 1" | bc)
   set +x
while IFS= read line > /dev/null;do
     echo $line | grep copied 
     if [ $? -ne 0 ]; then continue;fi
     (  copied=$(echo $line | awk '{print $1}'); 
       percent=$(expr $copied \* 100 / $copy_size) &> /dev/null; 
      echo XXX; 
      echo $percent; 
      echo $line; 
      echo XXX; ) \
      | dialog --title "Writing  Smaller resized Image" --gauge "Progress..." 8 80 
done< <( dd if=$1 of=$1.$$ bs=4096 count=$copy4k  \
         iflag=nocache,fullblock conv=notrunc 2>&1 & 
          pid=$!
          sleep 1
          while kill -USR1 $pid 2>/dev/null;do
               sleep 10
          done )
   set -x
   if test $? -ne 0; then exit 1; fi
   rm $1
   mv $1.$$ $1
   return 0
}

ptable_size(){
   # parameter is filename of image
   DEVICEREF=$(losetup -f)
   $(losetup -P $DEVICEREF $1)
   if [ $? -ne 0 ];then
      error_msg="failed to create RAWDEVICE reference for $1"
      losetup -d $DEVICEREF
      exit 1
   fi
   sectors=$(fdisk  -l $DEVICEREF | grep ${DEVICEFEF}p2 | awk '{print $3}')
   losetup -d $DEVICEREF
   echo "$sectors * 512" | bc
}

iiab_label(){
   if [ $# -ne 3 ];then
      echo "requires parameters iiab partition mount, username, labelstring"
      exit 1
   fi
   PARTITION=$1
   USER=$2
   LABEL=$3
   local iiab=false
   if [ -d $PARTITION/opt/iiab/iiab ]; then
      iiab=true
   fi

   # create id for image
   if test "$iiab" = "true"; then
      pushd /$PARTITION/opt/iiab/iiab > /dev/null
      HASH=`git log --pretty=format:'g%h' -n 1`
      popd > /dev/null
   else
      local tc_partition=${PARTITION:0:-1}3
      if [ -d $tc_partition/opt/iiab/iiab-factory ]; then
         pushd /$tc_partition/opt/iiab/iiab-factory > /dev/null
         HASH=`git log --pretty=format:'g%h' -n 1`
         popd > /dev/null
      else
         HASH="$$"
      fi
      PRODUCT=LOCAL
      VERSION="$IMAGERVERSION"
   fi
   YMD=$(date "+%y%m%d-%H%M")
   FILENAME=$(printf "%s-%s-%s-%s-%s-%s.img" $PRODUCT $VERSION $USER $LABEL $YMD $HASH)
   persist_variable "LAST_FILENAME" $FILENAME
   echo $FILENAME
}

bytes_to_human() {
    b=${1:-0}; d=''; s=0; S=(Bytes {K,M,G,T,E,P,Y,Z}B)
    while ((b > 1024)); do
        d="$(printf ".%02d" $((b % 1024 * 100 / 1024)))"
        b=$((b / 1024))
        let s++
    done
    echo "$b$d ${S[$s]}"
}

persist_variable(){
   # Save name value pair $1 $2
   # see if it already exists
   grep $1 $PERSIST_STATE_FILE > /dev/null
   if [ $? -eq 0 ]; then
      sed -i -e "s|^$1=.*|$1=$2|" $PERSIST_STATE_FILE
   else
      (echo "$1=$2") >> $PERSIST_STATE_FILE
   fi
}

get_persisted_variable(){
   grep ^$1 $PERSIST_STATE_FILE > /dev/null
   if [ $? -eq 0 ]; then
      echo $(grep ^$1 $PERSIST_STATE_FILE | cut -d= -f2)
   else
      echo
   fi
}

modify_dest(){
   # receives mounted partition as $1
   root_path=$1
   if [ ! -d "$root_path/etc/iiab" ]; then
      return 0
   fi

   # remove keys
   rm -f $root_path/etc/ssh/ssh_host_rsa_key{,.pub}
   rm -f $root_path/root/.ssh/*
   rm -f $root_path/root/.netrc
   rm -rf $root_path/root/tools

   # remove UUID -- regenerated on first run of IIAB
   rm -f $root_path/etc/iiab/uuid
   #echo $(uuidgen) > $root_path/etc/iiab/uuid
   if [ -f "$root_path/etc/iiab/handle" ]; then
      handle=$(cat "$root_path/etc/iiab/handle")
   else
      handle=
   fi
   user=$(get_persisted_variable "NAME")
   label=$(get_persisted_variable "LABEL")
   lastfilename=$(get_persisted_variable "LAST_FILENAME")

   # only modify handle the first time
   if [[ ! "$handle" =~ ".*\.cpy$" ]]; then
      handle="${handle}${user}${label}.cpy"
   else
      handle="$lastfilename"
   fi
      echo $handle > $root_path/etc/iiab/handle

   # record each imager operation in subsequent children
   YMD=$(date "+%y%m%d_%H.%M")
   echo "handle: $handle" > $root_path/etc/iiab/imager.$YMD
   echo "last filename: $lastfilename" >> $root_path/etc/iiab/imager.$YMD
   echo "last operation: $OBJECTIVE" >> $root_path/etc/iiab/imager.$YMD

   # set the copied image to expand 
   touch $root_path/.resize-rootfs

}

