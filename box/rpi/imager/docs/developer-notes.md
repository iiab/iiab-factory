## Notes on making Imager

* .mkdblboot was developed on ubuntu 16.04
* Does not run on Raspbian rpi, because grub2 does not exist in arm repos.
* Depending on mount and umount history, $device in ./mkdblboot may need to be changed -- defines the raw device used as target.
* Most of the config for tinycore, and imager, is tarred up in mydata.tgz, and downloaded from download.iiab.io/packages/imager/mydata.tgz
* Initial development was on tiny core, it was easier to run as non-root. So mkdblboot still requires that.

