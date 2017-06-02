#!/usr/bin/python
import os
import iiab
import sys
from sys import argv
from iiab import map_views
from iiab import render_cities
from iiab import osmtile
from iiab import config
import math

if len(argv) == 1:
    print("Please specify the name of the <spec>.ini file")
    sys.exit()

if not os.path.isfile(argv[1]): 
    print("%s not found"%argv[1])
    sys.exit()

config.load_config([argv[1],])
c = config.config()
lngw = c.getfloat("DEFAULT",'lngw')
lnge = c.getfloat("DEFAULT",'lnge')
lats = c.getfloat("DEFAULT",'lats')
latn = c.getfloat("DEFAULT",'latn')
zoom_start = c.getint("DEFAULT",'zoom_start')
zoom_stop = c.getint("DEFAULT",'zoom_stop')
subset_name = c.get("DEFAULT",'subset_name')

def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)

path = '/library/knowledge/modules/openstreetmap/mod_tile64'
tileset = osmtile.TileSet(path, 'default', METATILE=64, flatter=True)

# open an output file to hold the list of files to copy
fd = open(subset_name + '.list','w')
tilelist=[]
# now iterate over the desired bounding box
zoom = zoom_start
last_written=0
total=0.0
missing=0
last_missing = 0
while zoom <= zoom_stop:
    bbxn, bbyn = deg2num(latn, lngw, zoom)
    bbxs, bbys = deg2num(lats, lnge, zoom)
    lng = bbxn
    while lng <= bbxs:
        lat = bbyn
        while lat <= bbys:
            fn = tileset.xyz_to_meta(lng,lat,zoom)
            if fn not in tilelist:
                try:
                    total += os.path.getsize(fn)
                except:
                    missing += 1
                else:
                    fd.write(fn + '\n')
                    tilelist.append(fn)
            lat += 1
        lng += 1
    print("files written on zoom level:%s = %s. Missing: %s"%(zoom,len(tilelist)-last_written),missing-last missing)
    zoom += 1
    last_written = len(tilelist)
    last_missing = missing
    
fd.close()
print("total number of files copied: %s. Total filesize %s. Missing:%s"%(len(tilelist), total, missing,))
