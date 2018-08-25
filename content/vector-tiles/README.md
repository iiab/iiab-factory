## Offline OpenStreetMap + Regional Vector Map Datasets

### Summary Architecture

1. OpenMapTiles.com regularly publishes OpenStreetMap (OSM) data into [MVT](https://www.mapbox.com/vector-tiles/) Mapbox Vector Tile format, for dozens of regions around the world.  (This is an [open standard](https://www.mapbox.com/vector-tiles/specification/) which puts all of a region's vector tiles into a single SQLite database, in this case serialized as [PBF](https://wiki.openstreetmap.org/wiki/PBF_Format) and then delivered in a single .mbtiles file.)
1. Internet-in-a-Box (IIAB) works with these highly zoomable regional vector map datasets &mdash; each such .mbtiles file has a very minimal footprint &mdash; yet displays exceptional geographic detail.  IIAB's space-constrained microSD cards (typically running in a Raspberry Pi) greatly benefit!
1. The critical 4 data files are cities1000.sqlite (25 MB) + these 3 .mbtiles files: (the [MBTiles](https://github.com/mapbox/mbtiles-spec) file format can be used to store either raster/bitmap tilesets or vector tilesets)
   1. The world's landmasses are covered by `base.mbtiles -> osm_z0-10_planet.mbtiles` (1.4 GB) at zoom levels 0-10, encoded as MVT/PBF vector maps.
   1. The world's oceans are covered by `ocean.mbtiles -> mymap.mbtiles` (87 MB) at zoom levels 0-10, encoded as PNG raster/bitmap imagery.
   1. <b>Finally the 3rd one is the clincher: `details.mbtiles` adds in zoom levels 1-14 (for one single/chosen region, encoded as MVT/PBF vector maps) and can be overzoomed to level 18+.</b>
1. An example that includes all 1 + 3 data files is http://download.iiab.io/content/OSM/vector-tiles/en-osm-omt-min.zip (1.5 GB unzips to 1.8 GB, browsable at http://medbox.iiab.me/modules/en-osm-omt-min/).  Specifically: in addition to 1000 city locations/populations (user searchable, by typing in city names) and the above base maps for the world's landmasses and oceans, this also includes 109 MB file `detail.mbtiles -> 2017-07-03_california_san-francisco-bay.mbtiles` (whose detailed vector maps provide incredible geographic detail across California's [San Francisco Bay Area](https://openmaptiles.com/downloads/north-america/us/california/san-francisco-bay/), including building outlines).
1. Your Goal Below: replace this small 109 MB vector file, with a different local-or-larger region, for your own regional community.  These regional vector map datasets (plug-in files) can be downloaded from https://openmaptiles.com/downloads/planet/ &mdash; <i>on the right column of this page, choose a region!</i>

### How To Include Zoomable Map Detail For Your Region

1. Another example is http://download.iiab.io/content/OSM/vector-tiles/en-osm-omt-central-am.zip (2.8 GB unzips to 3.5 GB, browsable at http://medbox.iiab.me/modules/en-osm-omt-central-am/) which again includes base geodata for the world's landmasses and oceans, but in this case also includes 1.8 GB of zoomable vector map detail for [Central America and the Caribbean](https://openmaptiles.com/downloads/central-america/).  But the goal here is to pull together your own!  So...
1. Start by installing the original 1.5 GB file mentioned as the top of this page, including worldwide base maps etc:
   1. Log in to your IIAB then change to root by running: `sudo su -`
   1. Run: `cd /library/www/html/modules/`
   1. Download it by running:<br>`wget http://download.iiab.io/content/OSM/vector-tiles/en-osm-omt-min.zip`
   1. Run: `unzip en-osm-omt-min.zip` (creates 1.8 GB folder `en-osm-omt-min`)
   1. If you're <i>sure</i> you don't need it, run: `rm en-osm-omt-min.zip` (recovers 1.5 GB)
1. Add your favorite regional vector map dataset:
   1. Run: `cd /library/www/html/modules/en-osm-omt-min/`
   1. Download (into folder `en-osm-omt-min`) your chosen region's vector map dataset from https://openmaptiles.com/downloads/planet/ <i>(for example, if you download the 1.14-1.33 GB vector tiles for Central America & Caribbean, you get a region that is 5000KM wide including parts of South and North America, covering 20 independent countries and porions of 10 other countries)</i>
   1. <b>Create a symbolic link to replace "details.mbtiles -> 2017-07-03_california_san-francisco-bay.mbtiles" by running: `ln -sf ./<full filename of the downloaded region> details.mbtiles`</b>
1. Test it:
   1. Connect another device to your IIAB's Wi-Fi (SSID is typically "Internet in a Box")
   1. Browse to http://box/modules/osm-min (occasionally "box" needs to be replaced by "box.lan" or "172.18.96.1")
   1. Zoom into your region of interest to confirm local details appear!
   1. If so, recover 109 MB by running: `rm 2017-07-03_california_san-francisco-bay.mbtiles`

### Design -> Product

- Design Decisions:
  - [github.com/iiab/iiab-factory/blob/master/content/vector-tiles/Design-Decisions.md](https://github.com/iiab/iiab-factory/blob/master/content/vector-tiles/Design-Decisions.md) is sometimes out-of-date?
  - [github.com/georgejhunt/iiab-factory/blob/vector-maps/content/vector-tiles/Design-Decisions.md](https://github.com/georgejhunt/iiab-factory/blob/vector-maps/content/vector-tiles/Design-Decisions.md) just in case!
- How do we evolve this into a continuously more friendly product?  Usability Engineering begins here &mdash; thanks all who can assist &mdash; improving this for schools worldwide!
  - Package up vector-based OSM maps: [#877](https://github.com/iiab/iiab/issues/877)
  - Can OSM Vector Maps fill the entire screen? [#1035](https://github.com/iiab/iiab/issues/1035)
  - Can Vector OSM search more than 1000 cities? [#1034](https://github.com/iiab/iiab/issues/1034)
  - Teachers want Accents to work when searching for cities in OpenStreetMap [#662](https://github.com/iiab/iiab/issues/662)
