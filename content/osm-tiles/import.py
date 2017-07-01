#!/bin/env python
import os
import iiab
import osmtile


src=osmtile.TileSet('/root/en-worldmap-10','tile', METATILE=1, style="osm")
dst=osmtile.TileSet('/root/mod_tile64', 'default', METATILE=64, flatter=True)
for z in range(9, 11):
    osmtile.convert(src, dst, z)
