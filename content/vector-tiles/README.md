## An Offline Version of OpenStreetMap Using Vector Tiles
#### Background
1. OpenStreetMap (OSM) data has been organized into MVT (map vector tile) format. (This is a standard open format developed by Mapbox, which puts all of the tiles into a single sqlite database file).
1. This OSM application tries to provide Raspberry Pi (RPi) computers with some higher resolution (higher zoom levels) data, while using the minimum footprint on the RPi's SD card.
1. There is a basic tile set of mbtiles (Mapbox tiles) for the whole world at zoom levels 0-10 (about 1.4 GB).
1. And there is also another `details.mbtiles` file which provides zoom level 11-14 for a selected part of the world.
1. The http://download.iiab.io/content/OSM/vector-tiles/osm-min.zip file includes a small `details.mbtiles` file which takes up only 109 MB, and provides detailed geographic info for the Bay Area in California.
1. The intention is that the small Bay Area file will be replaced by a region of local/special interest to the community.  These regional plug-in files can be downloaded from https://openmaptiles.com/downloads/planet/ (use right column of this page to select region).
#### How To Include High Definition Details about your Region
1. Download file: http://download.iiab.io/content/OSM/vector-tiles/osm-min.zip (1.5 GB)
1. Move it to /library/www/html/modules directory.
1. Unzip osm-min.zip (after unziping, folder `osm-min` will be created; once that's done the .zip file can be deleted).
1. Download the mbtiles of interest from https://openmaptiles.com/downloads/planet/.  (for example, Central-America.mbtiles takes up about 1.9 GB)
1. Put the downloaded high resolution tiles (<region>.mbtiles) into /library/www/html/modules/osm-min/
1. Create a symbolic link which will replace the link "details.mbtiles -> 2017-07-03_california_san-francisco-bay.mbtiles" using the following command line:
```
  ln -sf ./<full name of the downloaded region> details.mbtiles
```
 * Connect another device to your RPi's Wi-Fi (SSID is typically "Internet in a Box").
 * Browse to http://box.lan/modules/osm-min
 * Zoom into the region of interest to test your high definition region.
 #### Technical Design Decisions
 * See https://github.com/iiab/iiab-factory/blob/master/content/vector-tiles/Design-Decisions.md which is sometimes out-of-date, so also check: https://github.com/georgejhunt/iiab-factory/blob/vector-maps/content/vector-tiles/Design-Decisions.md
