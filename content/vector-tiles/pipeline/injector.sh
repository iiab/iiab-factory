#!/bin/bash -x
# transform osm.pbf files into vector.mbtiles
planet_src_dir=/hd/root/
planet=2017-07-03_planet_z0_z14.mbtiles
planet_pbf=$planet_src_dir$planet

#central_america=[-99.8237843347,1.1619509497],[-118.9537281823,33.3622652637],[-84.7189564538,28.0515786731],[-83.6841816736,25.0204894651],[-62.3226399255,23.5811870317],[-67.6530690027,14.037561858],[-99.8237843347,1.1619509497]

download_urls=https://download.geofabrik.de/south-america-latest.osm.pbf /
      https://download.geofabrik.de/africa-latest.osm.pbf
#https://download.geofabrik.de/central-america-latest.osm.pbf

function get_osm_subset(){
/usr/share/osmosis/bin/osmosis --read-pbf $planet_pbf --bounding-polygon file="central_ameerica.poly" --write-pgsql --user="osm" --database='pgsnapshot' --host='localhost'
   
}


#################################
get_osm_subset
