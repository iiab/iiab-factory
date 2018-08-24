## An Offline Version of OpenStreetMap Using Vector Tiles

### Background
1. OpenStreetMap (OSM) data has been organized into <a href=https://www.mapbox.com/vector-tiles/specification/>MVT (map vector tile) format</a>.  (This is a standard open format developed by Mapbox, which puts all of the tiles into a single SQLite database file.)
1. This OSM application tries to provide Raspberry Pi (RPi) computers with some higher resolution (higher zoom levels) data, while using the minimum footprint on your RPi Internet-in-a-Box SD card.
1. There is a basic tile set of mbtiles (Mapbox tiles) for the whole world at zoom levels 0-10 (about 1.4 GB).
1. And there is also another `details.mbtiles` file which provides zoom level 11-14 for a selected part of the world.
1. The http://download.iiab.io/content/OSM/vector-tiles/osm-min.zip file includes a small `details.mbtiles` file which takes up only 109 MB, and provides detailed geographic info for the Bay Area in California.
1. The intention is that the small Bay Area file will be replaced by a region of local/special interest to the community.  These regional plug-in files can be downloaded from https://openmaptiles.com/downloads/planet/ (use right column of this page to select region).

### How To Include High Definition Details For Your Region
1. Change to root by running: `sudo su -`
1. Run: `cd /library/www/html/modules`
1. Download 1.5 GB osm-min.zip by running: `wget http://download.iiab.io/content/OSM/vector-tiles/osm-min.zip`
1. Run: `unzip osm-min.zip` (after unzipping, folder `osm-min` will be created; once that's done the .zip file can be deleted)
1. Run: `cd /library/www/html/modules/osm-min/`
1. Download (into the above folder) your mbtiles of interest from https://openmaptiles.com/downloads/planet/ (for example, Central-America.mbtiles takes up about 1.9 GB)
1. Create a symbolic link to replace link "details.mbtiles -> 2017-07-03_california_san-francisco-bay.mbtiles" by running: `ln -sf ./<full name of the downloaded region> details.mbtiles`
1. Test it by connecting another device to your RPi's Wi-Fi (SSID is typically "Internet in a Box")
1. Browse to http://box/modules/osm-min (occasionally "box" needs to be replaced by "box.lan" or "172.18.96.1")
1. Zoom into your region of interest to confirm it works!

#### Technical Design Decisions
* See https://github.com/iiab/iiab-factory/blob/master/content/vector-tiles/Design-Decisions.md which is sometimes out-of-date, so also check: https://github.com/georgejhunt/iiab-factory/blob/vector-maps/content/vector-tiles/Design-Decisions.md
