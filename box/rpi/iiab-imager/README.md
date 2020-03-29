## Automating the management of IIAB images
#### Overall Workflow
1. Some bash script to secure an image, remove any root paswords, user keys, and add the IIAB developer keys.
1. rpi/min-sd shrinks the image on a SD card, and specifies optional part of filename -- the IIAB, version, date, git hash are standard.
1. rpi/cp-sd copies the SD card to an image file, and zips it.
1. rpi/iiab-imager/prepare.sh accepts the image.zip filename as parameter, and create metadata in the current folder that will be picked up an transfered to the json file which drives the rpi-imager. It also queries for name and description which are required by rpi-imager.
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
  -r, --replace       Replace img.zip at archive.org.
  -e, --experimental  Put image into Experimental menu.
```
6. "rpi/iiab-imager/upload.py <image filename.zip>" uploads the image to archive.org, sets the metadata at archive.org, and adds the image metadata and url to the json files that specify the "Released" and "Experimental" sub menus.
1. The "Released" menu is the default target for a new image. The "Experimental" menu is targeted by using the "-e" flag.
