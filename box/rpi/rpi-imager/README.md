# rpi-imager

The Raspberry Pi rpi-imager utility (https://www.raspberrypi.org/downloads/) supports third party images. These can be integrated by

- a) Having the Raspberry Pi Foundation add a link to a custom subitem json file, as Ubunutu does.
- b) Invoking the imager with the argument --repo <url to top level json file>

As of 3/26/2020 you can do b) on Windows with the following command, which could easily be made into at .bat:

"C:\Program Files (x86)\Raspberry Pi Imager\rpi-imager.exe"  --repo http://iiab.me/images.json

This will present a link to a selected list of some of the IIAB images on https://archive.org/search.php?query=internetinabox

## Implementation

The json files are in this directory. os_list_imagingutility_iiab_subitems.json will need to be modified as images evolve.

We may also change the top level json file url in the future.
