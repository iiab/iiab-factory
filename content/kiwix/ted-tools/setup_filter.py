#!/usr/bin/env  python3
# -*- coding: utf-8 -*-

import sys,os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Configure the filtering of the contents of a ZIM file.")
    parser.add_argument("-s","--status", help='List the status of all variables.',action='store_true')
    parser.add_argument("-l","--list", help='List Zims already downloaded by Admin Console.',action='store_true')
    parser.add_argument("-p","--prefix", help='Prefix for path to storage/work area.')
    parser.add_argument("-u","--url", help='Fetch ZIM at this URL to filter')
    parser.add_argument("-z","--zim_#", help='Select listed Zim to filter',type=int)
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
   args = parse_args()

if __name__ == "__main__":
   main()
