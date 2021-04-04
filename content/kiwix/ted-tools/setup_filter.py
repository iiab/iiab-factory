#!/usr/bin/env  python3
# -*- coding: utf-8 -*-

import sys,os
import argparse
import glob
from ruamel.yaml import YAML
from  pprint import pprint
import subprocess
from operator import itemgetter
from inputimeout import inputimeout, TimeoutOccurred

cfg = {}

def myFunc(e):
    return len(e[3])

def disk_used():
    # Filesystem      Size  Used Avail Use% Mounted on  
    cmd = "df -h|gawk '{print $1,$2,$4,$6}'"
    resp = subprocess.run(cmd,shell=True,capture_output=True)
    devices = []
    lines = resp.stdout.splitlines()
    for line in lines:
        nibbles = line.decode().split(' ')
        devices.append(nibbles)
    devices = sorted(devices,reverse=True, key=myFunc)
    # Try to find the longest match starting at [0]
    for device in devices:
            if cfg['PREFIX'].find(device[3]) == 0:
                return device

def status():
    dev,tot,avail,path = disk_used()
    print('\n\nDisk: %s Size: %s Available: %s Mount point:%s'%(dev,tot,avail,path))
    config = get_yaml(lookfor)
    for k in config.keys():
        print('%-14s %s'%(k,config[k]))
    print('\n')

def get_yaml(path):
    yml = YAML()
    with open(path,'r') as fp:
        return(yml.load(fp))

def update_yaml(path,data_dict):
    yml = YAML()
    with open(path,'r') as fp:
        data = yml.load(fp.read())
        for k in data_dict.keys():
            data[k] = data_dict[k]
        with open(path,'w') as outfp:
            yml.dump(data,outfp)
        return data


def parse_args():
    parser = argparse.ArgumentParser(description="Configure the filtering of the contents of a ZIM file.")
    parser.add_argument("-s","--status", help='List the status of all variables.',action='store_true')
    parser.add_argument("-f","--filter", help='Confirm settings, filter,and create new ZIM file.',action='store_true')
    parser.add_argument("-l","--list", help='List Zims already downloaded by Admin Console.',action='store_true')
    parser.add_argument("-n","--name", help='Project name - keeps them separate')
    parser.add_argument("-p","--prefix", help='Prefix for path to storage/work area.')
    parser.add_argument("-u","--url", help='Fetch ZIM at this URL to filter')
    parser.add_argument("-z","--zim_no", help='Select ZIM listed by "-l" to filter',type=int,default=0)
    return parser.parse_args()

def human_readable(num):
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

def main():
    global args
    global url
    zims = None
    args = parse_args()
    if args.list:
       zims = glob.glob('/library/zims/content/*.zim')
       num = 1
       for zim in zims:
           print('%2d %s'%(num,zim))
           num += 1
       sys.exit(0)
    if args.zim_no != 0:
       zims = glob.glob('/library/zims/content/*.zim')
       if args.zim_no not in range(1,len(zims)+1):
           print('Index out of ramge. Quitting')
           sys.exit(1)
       url = zims[args.zim_no-1]
       data = dict(SOURCE_URL=url)
       update_yaml(lookfor,data)

    if args.status:
        status()
    if args.prefix:
        if args.prefix.find('zim') == -1:
            prefix = args.prefix + '/zims'
        else:
            prefix = args.prefix
        data = dict(PREFIX=prefix)
        update_yaml(lookfor,data)
    if args.url:
        data = dict(SOURCE_URL=args.url)
        update_yaml(lookfor,data)
    if args.name:
        data = dict(PROJECT_NAME=args.name)
        update_yaml(lookfor,data)
    if args.filter:
        status()
        try:
            resp = inputimeout(prompt='Confirm these settings and proceed? ("n" within 10 seconds aborts) Y/n: ', timeout=10)
        except TimeoutOccurred:
            resp = 'Y'
        if resp.upper() == 'Y':
            print('Processing will begin')
        else:
            print('Processing aborted')
                            


    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    home = os.environ['HOME']
    lookfor = home + '/.default_filter.yaml'
    dflt_cfg = '/opt/iiab/iiab-factory/content/kiwix/ted-tools/default_filter.yaml'
    if os.path.exists(lookfor):
        cfg = get_yaml(lookfor)
    else:
        yml = YAML()
        with open(dflt_cfg,'r') as fp:
            cfg = yml.load(fp)
        cfg['PREFIX'] = home + '/zims'
        cfg['PROJECT_NAME'] = 'new'
        with open(lookfor,'w') as newfp:
            yml.dump(cfg,newfp)
    main()
