## Offline OpenStreetMap Using Regional Map Packs (Vector Tiles)

### Summary Architecture

1. OpenStreetMap (OSM) data has been organized into <a href=https://www.mapbox.com/vector-tiles/specification/>MVT (map vector tile) format</a>.  (This is a standard open format developed by Mapbox, which puts all of that region's tiles into a single SQLite database file.)
1. This OSM application works with higher resolution (highly zoomable) regional datasets AKA map packs, while using the minimum footprint, since Internet-in-a-Box (IIAB) is typically running off a microSD card in a Raspberry Pi.  The key pieces are cities1000.sqlite (25 MB) and 3 critical .mbtiles files:
   1. The world's landmasses are covered by `base.mbtiles -> osm_z0-10_planet.mbtiles` (1.4 GB) which is a base set of mbtiles (Mapbox tiles) at zoom levels 0-10.
   1. The world's oceans are covered by `ocean.mbtiles -> mymap.mbtiles` (87 MB).
   1. Finally the 3rd one is `details.mbtiles` which provides zoom level 11-14 for any selected part of the world.
1. An example that includes all 1+3 files is http://download.iiab.io/content/OSM/vector-tiles/en-osm-omt-min.zip (1.5 GB, browsable at http://medbox.iiab.me/modules/en-osm-omt-min/).  Specifically: in addition to 1000 cities (searchable by their names) and base maps for the world's landmasses and oceans, it includes 109 MB file `detail.mbtiles -> 2017-07-03_california_san-francisco-bay.mbtiles` which provides geographic detail for the <a href=https://openmaptiles.com/downloads/north-america/us/california/san-francisco-bay/>San Francisco Bay Area</a> in California.
1. Your Goal Below: replace this small 109 MB file with a local region of interest to your own community.  These regional dataset plug-in files (AKA map packs) can be downloaded from https://openmaptiles.com/downloads/planet/ &mdash; <i>on the right column of this page, choose a region!</i>

### How To Include Zoomable Map Detail For Your Region

1. An alternate example http://download.iiab.io/content/OSM/vector-tiles/en-osm-omt-central-am.zip (2.8 GB, browsable at http://medbox.iiab.me/modules/en-osm-omt-central-am/) which incorporates zoomable detail for Central America and the Caribbean.  But the goal here is to pull together your own!  So...
1. Log in to your IIAB then change to root by running: `sudo su -`
1. Run: `cd /library/www/html/modules`
1. Download the original 1.5 GB file mentioned as the top of this page, by running: `wget http://download.iiab.io/content/OSM/vector-tiles/en-osm-omt-min.zip`
1. Run: `unzip en-osm-omt-min.zip` (after unzipping, folder `en-osm-omt-min` will be created; once that's done the .zip file can be deleted)
1. Run: `cd /library/www/html/modules/en-osm-omt-min/`
1. Download (into folder `en-osm-omt-min`) your .mbtiles regional dataset AKA map pack of interest from https://openmaptiles.com/downloads/planet/ (for example, Central-America.mbtiles takes up about 1.9 GB)
1. <b>Create a symbolic link to replace "details.mbtiles -> 2017-07-03_california_san-francisco-bay.mbtiles" by running: `ln -sf ./<full name of the downloaded region> details.mbtiles`</b>
1. Test it by connecting another device to your IIAB's Wi-Fi (SSID is typically "Internet in a Box")
1. Browse to http://box/modules/osm-min (occasionally "box" needs to be replaced by "box.lan" or "172.18.96.1")
1. <i>Zoom into your region of interest to confirm local details appear!</i>

### Design Decisions (Technical Background)

* See https://github.com/iiab/iiab-factory/blob/master/content/vector-tiles/Design-Decisions.md which is sometimes out-of-date, so also check: https://github.com/georgejhunt/iiab-factory/blob/vector-maps/content/vector-tiles/Design-Decisions.md
