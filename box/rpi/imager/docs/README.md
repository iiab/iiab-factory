## Put IMAGER on a USB Stick&mdash;to copy Internet-in-a-Box microSD cards!

* IMAGER makes it easy to back up, shrink (truncate) and copy Internet-in-a-Box microSD cards, on almost any Windows computer.
    * Amazingly, IMAGER even allows you to copy to microSD cards that are "just a bit too small" (a godsend when each manufacturer's microSD card is a slightly different size, which prevents other copying tools from working!)
    * IMAGER _can_ be converted to run on Mac computers _if_ the need is very strong.
    * On the Linux OS, please use the [dd](https://www.linuxnix.com/what-you-should-know-about-linux-dd-command/), [min-sd and cp-sd](https://github.com/iiab/iiab-factory/blob/master/box/rpi/howto-mkimg.txt) commands (min-sd is the underlying magic that shrinks or truncates microSD cards, without any data loss).
* DOWNLOAD the most recent IMAGER from [download.iiab.io/packages/imager](http://download.iiab.io/packages/imager/).  Depending on the speed of your Internet, this could take a while (IMAGER is about 112 MB).
* Use [Etcher.io](https://etcher.io) or [sourceforge.net/projects/win32diskimager](https://sourceforge.net/projects/win32diskimager/) to flash (burn) the downloaded .img file onto a USB stick&mdash;_remember that all prior USB stick data will be lost._
* Make sure that your Windows computer's [BIOS is set to boot USB](http://www.boot-disk.com/boot_priority.htm) devices first.
    * Setting the BIOS may require that you strike the ESC, F1, F2, F8, F10, F12, or Delete key&mdash;_just after you power on the computer._
    * Look for a BIOS setting called "boot options" or "boot order", and make sure the USB stick/drive/device comes first.
* Put the USB stick into your Windows computer, then turn on the computer.
    * After a short time you should see the colorful boot process of Tiny Core Linux, and eventually the IMAGER menu as shown in IMAGER's [GET STARTED GUIDE](https://github.com/iiab/iiab-factory/blob/master/box/rpi/imager/docs/GET-STARTED-GUIDE.md).
    * Begin copying Internet-in-a-Box microSD cards :-)
    * Kindly provide [feedback](http://FAQ.IIAB.IO#What_are_the_best_places_for_community_support.3F) to help schools, libaries & clinics around the world improve on this humanitarian work, _Thank You!_
