## Automating the management of IIAB images
#### Overall Workflow
1. The generic/secure-accounts.sh script is used to secure an image, remove any root paswords, user keys, and add the IIAB developer keys.
1. rpi/min-sd shrinks the image on a SD card, and specifies optional part of filename -- the IIAB, version, date, git hash are standard.
1. rpi/cp-sd copies the SD card to an image file, and zips it.
1. rpi/iiab-imager/upload.py calculates the checksums and sizes that are required for the rpi-imager.json menu description. It also queries for name and description which are displayed it its menu.
1. "rpi/iiab-imager/upload.py -h" shows help.
```
./upload.py -h
usage: upload.py [-h] [-c] [-r] [-e] image_name

Upload img to archive.org, Set rpi-imager json files.

positional arguments:
  image_name          Specify the image file namel

optional arguments:
  -h, --help          show this help message and exit
  -c, --check         Check version, update metadata.
  -d  --delete        Delete the menu item.
  -e, --experimental  Put image into Experimental menu.
```
6. "rpi/iiab-imager/upload.py <image filename.zip>" uploads the image to archive.org, sets the metadata at archive.org, and adds the image metadata and url to the json files that specify the "Released" and "Experimental" sub menus.
1. The "Released" menu is the default target for a new image. The "Experimental" menu is targeted by using the "-e" flag.
1. The rpi/iiab-imager/toplevel.py refreshes the top level menu items from Raspberry Pi Foundation site, and adds the IIAB **Released** and **Experimental** menu items. The ```toplevel.py``` should be run after the release of a new vesion of raspbian (on average every 2-3 months).
