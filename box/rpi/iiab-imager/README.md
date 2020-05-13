## Automating the management of IIAB images
#### Overall Workflow
1. The generic/secure-accounts.sh script is used to secure an image, remove any root paswords, user keys, and add the IIAB developer keys.
1. rpi/min-sd shrinks the image on a SD card, and specifies optional part of filename -- the IIAB, version, date, git hash are standard.
1. rpi/cp-sd copies the SD card to an image file, and zips it.
1. rpi/iiab-imager/prepare.sh accepts the image.zip filename as parameter, and creates metadata in the current folder that will be picked up and transfered to the json file which drives the rpi-imager. It also queries for name and description which are required by rpi-imager.
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
  -d, --delete        Delete item from json file.
  -e, --experimental  Put/delete image to/from Experimental menu.
```
6. "rpi/iiab-imager/upload.py <image filename.zip>" uploads the image to archive.org, sets the metadata at archive.org, and adds the image metadata and url to the json files that specify the "Released" and "Experimental" sub menus.
1. The "Released" menu is the default target for a new image. The "Experimental" menu is targeted by using the "-e" flag.
1. The rpi/iiab-imager/toplevel.py refreshes the top level menu items from Raspberry Pi Foundation site, and adds the IIAB **Released** and **Experimental** menu items. The ```toplevel.py``` should be run after the release of a new vesion of raspbian (on average every 2-3 months).
  
  #### Notes for Testing Images and the "testiiab" Branch
  1. This workflow creates a "private" installer which is contained in the "testiiab" branch of the http://github.com/georgejhunt/iiab-factory repo.
  2. Use of this imager workflow requies a desktop shortcut that specifies a "--repo" that points to the branch (#1 above).
  3. Images that pass the testing phase, can be published via the upload.py in master. Upload will check archive.org, and skip the upload if it already exists -- in which case it just adjusts the json file which advertises availaability.
  
