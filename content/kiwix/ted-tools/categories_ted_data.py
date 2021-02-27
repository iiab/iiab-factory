#!/usr/bin/python3
# extract useful data from data.js in teded zim

import json
import os,sys

if len(sys.argv) < 2:
    print('Please specify the path to json file')
    sys.exit(1)
outstr = ''
data = {}
category_name = []
members_count = []
category_index = 0
with open(sys.argv[1],'r') as fp:
    while True:
        line = fp.readline()
        if not line:
            break
        if line.startswith('var'):
            if len(outstr) > 1:
                # clip off the trailing semicolon
                outstr = outstr[:-2]
                try:
                    data[cat] = json.loads(outstr)
                except Exception:
                    print('Parse error: %s'%outstr[:80])
                    sys.exit(1)
                category_name.append(None)
                category_name[category_index] = cat
                members_count.append(None)
                members_count[category_index] = len(data[cat]) 
                category_index += 1
            cat = line[9:-4]
            outstr = '['
        else:
            outstr += line
    print('Total number of Categories: %s'%category_index)
    for catno in range(category_index):
        print('%s  %s'%(members_count[catno],category_name[catno]))
