## How to Get Started -- Create IMAGER on a USB Stick
* IMAGER makes it easy to back up, shrink (truncate) and copy Internet-in-a-Box microSD cards, on almost any Windows computer.
  * Amazingly, IMAGER even allows you to copy to microSD cards that are "just a bit too small" (when extremely annoying size differences between manufacturers prevent other copying tools from working!)
  * In future Mac computers may be supported as well.
  * On the Linux OS, please use the [dd](https://www.linuxnix.com/what-you-should-know-about-linux-dd-command/) and [min-sd and cp-sd](https://github.com/iiab/iiab-factory/blob/master/box/rpi/howto-mkimg.txt) commands (min-sd is the underlying magic that shrinks or truncates microSD cards, without any data loss).
* DOWNLOAD the most recent IMAGER from [download.iiab.io/packages/imager](http://download.iiab.io/packages/imager/).  Depending on the speed of your Internet, this could take a while (IMAGER is about 112 MB).
* Use [Etcher.io](https://etcher.io) or [sourceforge.net/projects/win32diskimager](https://sourceforge.net/projects/win32diskimager/) to flash (burn) the downloaded .img file onto a USB stick &mdash; all USB stick data will be lost!
* Make sure that your Windows computer's BIOS is set to boot first from USB.
  * Setting the BIOS may require that you strike the F1, F2, F10, F12, or Delete key just after turning on the power.
  * Look for a BIOS setting called "boot options" or "boot order", and make sure the USB drive (USB stick) comes first.
* Put the USB stick into your Windows computer, and turn on the power.
  * After a short time you should see the colorful boot process of Tiny Core Linux, and eventually the IMAGER menu as shown in IMAGER's [GET STARTED GUIDE](https://github.com/iiab/iiab-factory/blob/master/box/rpi/imager/docs/GET-STARTED-GUIDE.md).
  * Begin copying Internet-in-a-Box microSD cards!
