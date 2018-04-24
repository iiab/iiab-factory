## An Offline Version of Openstreetmaps Using Vector Tiles
#### Background
1. Openstreetmap data has been organized into MVT (map vector tile) format. (This is a standard open format developed by Mapbox, which puts all of the tiles into a single sqlite database file).
1. This OSM application tries to provide raspberry pi computers with some higher resolution (higher zoom levels) data, but using up the minimum footprint on the SD card.
1. There is a basic tile set of mbtiles (mapbox tiles) for the whole world at zoom levels 0-10 (this occupies about 1.4GB).
1. And there is also another details.mbtiles file which provides zoom level 11-14 of some part of the world (The osm-vec-min
1. The http://download.iiab.io/content/OSM/vector-tiles/osm-min.zip file includes a small details.mbtiles file which takes up only 100MB, and provides detailed geographic information about the Bay area in California.
1. The intention is that the small Bay Area file will be replaced by a region of special interest to the user. These regional plug in files can be downloaded from https://openmaptiles.com/downloads/planet/ (use right column of this page to select region).
#### How To Include High Definition Details about your Region
1. Download the http://download.iiab.io/content/OSM/vector-tiles/osm-min.zip file.
1. Move it to /library/www/html/modules directory
1. Unzip osm-min.zip. (After unziping, a new "osm-min" folder will be created. Once that is done the zip file can be deleted).
1. Download the mbtiles of interest (For example, the Central-America.mbtiles takes up about 1.9GB)
1. Put the downloaded high resolution tiles into /library/www/html/modules/osm-min/.
1. Create a symbolic link which will replace the link "details.mbtiles =>2017-07-03_california_san-francisco-bay.mbtiles" using the following command line:
```
 ln -sf ./<full name of the downloaded region> details.mbtiles
 ```
 * Associate with the wifi signal transmitted by your RPI (the SSID is "Internet in a Box").
 * Browse to http://box.lan/modules/osm-min
 * Zoom into the region of interest to test your high definition region.
