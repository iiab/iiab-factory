## Offline OpenStreetMap + Vector Tile Regional Map Packs

### Summary Architecture

1. OpenStreetMap (OSM) data has been organized into [MVT](https://www.mapbox.com/vector-tiles/) Mapbox Vector Tile format.  (This is an [open standard](https://www.mapbox.com/vector-tiles/specification/) which puts all of a region's vector tiles into a single SQLite database, in this case serialized as [PBF](https://wiki.openstreetmap.org/wiki/PBF_Format) then wrapped into an .mbtiles file.)
1. This OSM application works with highly zoomable such regional datasets AKA vector map packs &mdash; each having a very minimal footprint &mdash; since Internet-in-a-Box (IIAB) is typically running on a space-constrained microSD card in a Raspberry Pi.  The critical 4 data files are cities1000.sqlite (25 MB) + these 3 .mbtiles files: (the [MBTiles](https://github.com/mapbox/mbtiles-spec) file format is used to store either raster/bitmap or vector tilesets)
   1. The world's landmasses are covered by `base.mbtiles -> osm_z0-10_planet.mbtiles` (1.4 GB) at zoom levels 0-10, encoded as MVT/PBF vector maps.
   1. The world's oceans are covered by `ocean.mbtiles -> mymap.mbtiles` (87 MB) encoded as PNG raster/bitmap imagery.
   1. Finally the 3rd one is `details.mbtiles` which provides zoom levels 11-14 for any selected part of the world, encoded as MVT/PBF vector maps.
1. An example that includes all 1 + 3 data files is http://download.iiab.io/content/OSM/vector-tiles/en-osm-omt-min.zip (1.5 GB, browsable at http://medbox.iiab.me/modules/en-osm-omt-min/).  Specifically: in addition to 1000 cities (user searchable, by typing in city names) and the base maps for the world's landmasses and oceans, this also includes 109 MB file `detail.mbtiles -> 2017-07-03_california_san-francisco-bay.mbtiles` (whose detailed vector maps provide incredible geographic detail across California's [San Francisco Bay Area](https://openmaptiles.com/downloads/north-america/us/california/san-francisco-bay/)).
1. Your Goal Below: replace this small 109 MB vector file, with a different local/larger region, of interest to your own community.  These regional dataset plug-in files (AKA vector map packs) can be downloaded from https://openmaptiles.com/downloads/planet/ &mdash; <i>on the right column of this page, choose a region!</i>

### How To Include Zoomable Map Detail For Your Region

1. Another example http://download.iiab.io/content/OSM/vector-tiles/en-osm-omt-central-am.zip (2.8 GB, browsable at http://medbox.iiab.me/modules/en-osm-omt-central-am/) again includes base geodata for the world's landmasses and oceans, but in this case also includes 1.8GB of zoomable vector map detail for [Central America and the Caribbean](https://openmaptiles.com/downloads/central-america/).  But the goal here is to pull together your own!  So...
1. Start by installing the original 1.5 GB file mentioned as the top of this page, including worldwide base maps etc:
   1. Log in to your IIAB then change to root by running: `sudo su -`
   1. Run: `cd /library/www/html/modules/`
   1. Download it by running:<br>`wget http://download.iiab.io/content/OSM/vector-tiles/en-osm-omt-min.zip`
   1. Run: `unzip en-osm-omt-min.zip` (after unzipping, folder `en-osm-omt-min` will be created; once that's done the .zip file can be deleted)
1. Add your favorite regional map pack:
   1. Run: `cd /library/www/html/modules/en-osm-omt-min/`
   1. Download (into folder `en-osm-omt-min`) your .mbtiles vector map pack of interest AKA regional dataset from https://openmaptiles.com/downloads/planet/ (for example, central-america_z10-14.mbtiles takes up about 1.8 GB)
   1. <b>Create a symbolic link to replace "details.mbtiles -> 2017-07-03_california_san-francisco-bay.mbtiles" by running: `ln -sf ./<full name of the downloaded region> details.mbtiles`</b>
1. Test it:
   1. Connect another device to your IIAB's Wi-Fi (SSID is typically "Internet in a Box")
   1. Browse to http://box/modules/osm-min (occasionally "box" needs to be replaced by "box.lan" or "172.18.96.1")
   1. Zoom into your region of interest to confirm local details appear!
   1. If so, recover 109 MB by running: `rm 2017-07-03_california_san-francisco-bay.mbtiles`

### Design -> Product

- Design Decisions:
  - [github.com/iiab/iiab-factory/blob/master/content/vector-tiles/Design-Decisions.md](https://github.com/iiab/iiab-factory/blob/master/content/vector-tiles/Design-Decisions.md) is sometimes out-of-date?
  - [github.com/georgejhunt/iiab-factory/blob/vector-maps/content/vector-tiles/Design-Decisions.md](https://github.com/georgejhunt/iiab-factory/blob/vector-maps/content/vector-tiles/Design-Decisions.md) just in case!
- How do we evolve this into a continuously more friendly product?  Usability Engineering begins here &mdash; thanks all who can assist!
  - Package up vector-based OSM maps: [#877](https://github.com/iiab/iiab/issues/877)
  - Can OSM Vector Maps fill the entire screen? [#1035](https://github.com/iiab/iiab/issues/1035)
  - Can Vector OSM search more than 1000 cities? [#1034](https://github.com/iiab/iiab/issues/1034)
  - Teachers want Accents to work when searching for cities in OpenStreetMap [#662](https://github.com/iiab/iiab/issues/662)
