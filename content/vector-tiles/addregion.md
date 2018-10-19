### Objectives
* Combine mbtiles from an arbitrary number of regions (available from https://openmaptiles.org/downloads).
* Provide a mode which uses all the *.mbtiles in a specified, or current directory, as source.
* Provode a second interface which accepts input from the Admin Console, and merges one mbtile at a time (thinking that the download and merge might be an atomic and repeated accumulative action).
* Permit input and output specification via full path filenames (default to current working directory).

### Inputs
* opetional flag -d --dir <full path> -- make the specified directory the default before appending. (optional flag must be specified before the two required parameters).
* parameter 1 -- required. If parameter 1 is a directory, append all *.mbtiles to parameter 2. If a parameter 1 is a mbtile, append it to parameter 2.
* parameter 2 -- required. Name of mbtile to which additional tile data should be appended. If parameter is full path, put output there. Otherwise put it into <default directory>/output/<parameter 2>

### Examples
* Add all the mbtiles in my download directory to a new test.mbtiles in the IIAB modules/en-osm-omt-min/ directory:
```
# the following symbolic link will make the append2region executable from any directory. Do it once
ln -s /opt/iiab/iiab-factory/content/vector/tiles/append2region /usr/bin/
cd /home/ghunt/downloads
append2region  . /library/www/html/modules/en-osm-omt-min/test.mbtiles
```
