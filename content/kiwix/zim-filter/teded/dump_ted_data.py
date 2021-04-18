#!/usr/bin/python3
# extract useful data from data.js in teded zim

import json
import os,sys

if len(sys.argv) < 2:
    print('Please specify the path to json file')
    sys.exit(1)
outstr = ''
lineno = 0
data = {}
with open(sys.argv[1],'r') as fp:
    while True:
        lineno += 1
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
                    print(outstr)
                    sys.exit(1)
            cat = line[9:-4]
            outstr = '['
        else:
            outstr += line
    for cat in data:
        print(cat)
        for item in range(len(data[cat])): 
            print('%s --%s'%(data[cat][item]['slug'],data[cat][item]['id']))
        sys.exit(1)
