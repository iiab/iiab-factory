#!/usr/bin/python

import os
import iiab
import sys
from sys import argv
from iiab import map_views
from iiab import osmtile
from iiab import config
import math

# source tree from which the higher resolution tiles are copied
source_path = '/library/knowledge/modules/openstreetmap/mod_tile64'
prefix = '/library'

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
  # source http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)

def human_readible(num):
    # return 3 significant digits and unit specifier
    num = float(num)
    units = [ '','K','M','G']
    for i in range(4):
        if num<10.0:
            return "%.2f%s"%(num,units[i])
        if num<100.0:
            return "%.1f%s"%(num,units[i])
        if num < 1000.0:
            return "%.0f%s"%(num,units[i])
        num /= 1000.0

tileset = osmtile.TileSet(source_path, 'default', METATILE=64, flatter=True)

outpath=os.path.join(prefix,'working','osm',subset_name,'output')
workdir=os.path.join(prefix,'working','osm',subset_name)
if not os.path.exists(outpath):
    os.makedirs(outpath)

# open an output file to hold the list of files to copy
fd = open(workdir + '/' +subset_name + '.list','w')

# open a file to capture the summary so it can be included in the zip file
summaryfd = open(workdir + '/' +subset_name + '.info','w')
summaryfd.write("# Generated by iiab-factory/content/subset-osm/mk-subset.py\n")

tilelist=[]
# now iterate over the desired bounding box
zoom = zoom_start
last_written=0
total=0.0
missing=0
last_missing = 0
last_total = 0.0
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
    print("files written on zoom level:%s = %s. Size: %s. Missing: %s" % (zoom,len(tilelist)-last_written,human_readible(total - last_total), missing - last_missing))
    summaryfd.write(" Files written on zoom level:%s = %s. Size: %s. Missing: %s\n" % (zoom,len(tilelist)-last_written,human_readible(total - last_total), missing-last_missing))
    zoom += 1
    last_written = len(tilelist)
    last_missing = missing
    last_total = total
    
fd.close()
print("total number of files copied: %s. Total filesize %s. Missing:%s"%(len(tilelist), human_readible(total), missing,))
summaryfd.write("\n\n Total number of files copied: %s. Total filesize %s. Missing:%s\n"%(len(tilelist), human_readible(total), missing,))
summaryfd.close()
