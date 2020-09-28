#!/usr/bin/python3

import xml.etree.ElementTree as ET
import json
import csv
import operator
import base64
import os.path
import os
import sys
import shutil
import urllib.request, urllib.error, urllib.parse
import json
import time
import uuid
import re
import argparse
import fnmatch
from datetime import date
import random

import socket
# import asyncio - I think asyncio is masking issues
import threading
import subprocess
#import shlex

# On NUC
# N.B. if hostapd running on host for this app then all requests go to local server
# systemctl stop hostapd
# brctl delif br0 wlp0s20f3 to remove nucs internal wifi
# after which connect_wifi will connect it

# both the wpa_supplicant and dhclient commands throw errors, but still succeed
# rfkill: Cannot get wiphy information
# ioctl[SIOCSIWAP]: Operation not permitted
# ioctl[SIOCSIWENCODEEXT]: Invalid argument
# ioctl[SIOCSIWENCODEEXT]: Invalid argument
# contrary to googling -D wext is necessary
# these errors do not seem to prevent a connection to iiab ssid

# N.B on rpi iw does not work with tplink 725
# looks like same on NUC - only Canakit and edimax
# ralink chip works
# tried  modprobe mac80211_hwsim radios=8 - ip a shows wlan0 to wlan15 plus hwsim0
# ip link set wlan15 up no complaints
# wpa_supplicant says successful
# dhclient -4 wlan15 hangs
# but I now have iw list |grep Wiphy phy0 to phy8
# tried wlan10. also hangs

# cat  /sys/class/net/wlx801f02bbfa46/phy80211/name can relate device to phy#
# one gets rename28 (wlx801f02bbfa46) and the other gets similar name (wlx000f6003c82f gets wlx000f6003c828)
# one (wlx801f02bbfa46)seems to allow multiple clones and now doesn't rename, but all have the same mac address
# assign mac address works on edimmax but canakit does automatically and ignores parameter
# cat /var/lib/dhcp/dhclient.leases for leases

usb_wifi_ifaces = {}
our_wifi_macs = {}
total_connections = 0
failed_connections = []
monitor_iface = None
start_time = None

CLONE_DEVS = False
VDEV_SUFFIX = 'vdev'
VMAC_BASE = '02:00:00:00:00:' # for local 2nd least significant bit of first octet must be 1 (2, 6, A, E)
START_URL = '/home/index.html' # no protocol or host
SLEEP_SECONDS = 5 # this was not better than 1 on two instances and was in fact worse
# SLEEP_SECONDS = 1
WIFI_DEV_PREFIX = 'wl'
ESC='\033'

vmac_counter = 0
run_flag = True
verbose = False

def main():
    global total_connections
    global failed_connections
    global monitor_iface

    print('Starting')
    threading.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    print('Press the ENTER key to terminate')

    init()

    print('Starting connections. Could take a little time.')
    for dev in usb_wifi_ifaces:
        print(f'Attempting connection for {dev}')
        rc = connect_wifi(dev)
        if rc:
            total_connections += 1
            print(f'Connection successful. Total Connections: {total_connections}')
        else:
            failed_connections.append(dev)

    for dev in usb_wifi_ifaces: # now start using the connections
        if dev in failed_connections:
            continue
        if not monitor_iface: # pick first dev as monitor
            monitor_iface = dev
            thread = threading.Thread(target=monitor_dev, args=(dev,))
            thread.start()
        else:
            thread = threading.Thread(target=one_dev, args=(dev,))
            thread.start()

    while run_flag:
        time.sleep(SLEEP_SECONDS) # vamp until ready

    # now wait for all threads to terminate
    # rewrite
    #for dev in usb_wifi_ifaces:
    #    if 'task' in usb_wifi_ifaces[dev]:
    #        await usb_wifi_ifaces[dev]['task']
    # await reset_all_ifaces()

def monitor_dev(dev):
    global total_connections
    global usb_wifi_ifaces

    # await connect_wifi(dev) # try to get a connection
    url = '/stat'
    while run_flag:
        client_ip = usb_wifi_ifaces[dev].get('ip-addr', None)
        #print(client_ip)
        if client_ip:
            header, stat_json = get_html(client_ip, url, port=10080)
            usb_wifi_ifaces[dev]['access_cnt'] += 1
            #print(header)
            if header['status'] >= '500':
                print('Error Connecting to Status Server')
            else:
                show_stat(stat_json)
        else:
            connect_wifi(dev)
        time.sleep(5)

def show_stat(stat_json):
    global total_connections
    global usb_wifi_ifaces
    global our_wifi_macs

    clear_line = ESC+'[0K'
    curtime = time.time()
    elapsed = time.strftime('%H:%M:%S', time.gmtime(curtime - start_time))

    if not verbose:
        print(ESC+'[0;0H') # cursor to top of screen
    server_mac_arr = json.loads(stat_json)
    print(f'Time Started {time.ctime(start_time)}. Elapsed {elapsed}{clear_line}')
    print(f'Total Connections on Server: {len(server_mac_arr)}{clear_line}')
    print(clear_line)
    print(f'These are our interfaces:{clear_line}')
    for dev in usb_wifi_ifaces:
        ip_addr = usb_wifi_ifaces[dev]['ip-addr']
        mac = usb_wifi_ifaces[dev]['mac']
        if mac in server_mac_arr:
            conn_stat = 'connected to server'
        else:
            conn_stat = 'no connection'
        access_cnt = usb_wifi_ifaces[dev]['access_cnt']

        print(f'{dev} mac: {mac} ip: {ip_addr} connection: {conn_stat}{clear_line} urls accessed: {access_cnt}')

    print(clear_line)
    print(f'These mac addresses seen on the server:{clear_line}')
    for mac in server_mac_arr:
        if mac in our_wifi_macs:
            print (f'{mac} ( {our_wifi_macs[mac]} ) connected to server{clear_line}')
        else:
            print(f'{mac}  on server is not ours{clear_line}')
    #print('Server has additional ' + str(len(mac_arr - total_connections)) + ' connections')

def one_dev(dev):
    global total_connections
    global usb_wifi_ifaces

    # await connect_wifi(dev) # try to get a connection already done
    url = START_URL
    while run_flag:
        client_ip = usb_wifi_ifaces[dev].get('ip-addr', None)
        if client_ip:
            header, html = get_html(client_ip, url)
            usb_wifi_ifaces[dev]['access_cnt'] += 1
        else:
            connect_wifi(dev)
        #time.sleep(random.uniform(.5 * SLEEP_SECONDS, 1.5 * SLEEP_SECONDS)) # makes no difference
        time.sleep(SLEEP_SECONDS)

def get_html(client_ip, page_url, port=80, server_ip='172.18.96.1'):
    print_msg('Retrieving page for ' + client_ip)
    BUF_SIZE = 4096

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((client_ip, 0)) # use ip of interface
        try:
            s.connect((server_ip , port))
        except ConnectionRefusedError as e:
            print ('socket error: ' + str(e))
            header = {'status': '503', 'content-length': '0'} # pseudo status for not connection
            html = ''
            return header, html
        head = 'HEAD ' +  page_url +  ' HTTP/1.1\r\nHost: ' + server_ip + '\r\nAccept: text/html\r\n\r\n'
        request = 'GET ' +  page_url +  ' HTTP/1.1\r\nHost: ' + server_ip + '\r\nAccept: text/html\r\n\r\n'
        s.sendall(request.encode('utf8'))
        header = b''
        while True:
            buf = s.recv(BUF_SIZE)
            if not header:
                parts = buf.split(b'\r\n\r\n',1)
                header = parse_header(parts[0].decode())
                html_bytes = parts[1]
            else:
                html_bytes += buf
            if len(html_bytes) >= int(header['content-length']):
            # if len(buf) < BUF_SIZE: # this can fail if header and body are two fetches
                break
        html = html_bytes.decode()
        print_msg (header)
    return header, html

def init():
    global total_connections
    global start_time

    start_time = time.time()
    vdevs = {}
    total_connections = 0

    if not verbose:
        print(ESC+'[0;0H') # cursor to top of screen
        print(ESC+'[2J')   # clear screen
    print('Starting init')

    # remove existing connections
    reset_all_ifaces()

    find_wifi_dev() # get dict of physical wifi devices
    #for dev in usb_wifi_ifaces: # reset any wpa services
    #    await reset_wifi_conn(dev)

    if CLONE_DEVS:
        find_wiphy() # find support for iw but can return false positive
        for dev in usb_wifi_ifaces:
            if VDEV_SUFFIX in dev: # it's virtual
                continue
            wiphy = usb_wifi_ifaces[dev].get('wiphy', None)
            if wiphy:
                vdev = dev + VDEV_SUFFIX
                if add_vdev(wiphy, vdev):
                    vdevs[vdev] = {'vdev': True}
        find_wifi_dev()

def add_vdev(phy, vdev):
    global vmac_counter
    cmdstr = 'iw phy ' + phy +' interface add ' + vdev + ' type managed'
    compl_proc = subproc_run(cmdstr)
    if compl_proc.returncode == 0:
        # now override mac address
        vmac_counter += 1
        cmdstr = 'ip link set ' + vdev + ' address ' + VMAC_BASE + str(vmac_counter).zfill(2)
        compl_proc = subproc_run(cmdstr) # this can fail when new mac automatically assigned (i.e. Canakit)
        return True
    else:
        return False

def connect_wifi(iface):
    # wpa_cli -i wlxc4e98408a7be disconnect
    # wpa_cli -i wlan6 terminate - fails if not running
    if usb_wifi_ifaces[iface]['status'] != 'UP':
        print_msg('Starting set link up for ' + iface)
        cmdstr = 'ip link set ' + iface + ' up'
        compl_proc = subproc_run(cmdstr)
        if compl_proc.returncode != 0:
            print('Set link up failed for ' + iface)
            print(compl_proc.stderr)

    print_msg('Resetting wpa_supplicant for ' + iface)
    reset_wifi_conn(iface) # close and wpa services

    print_msg('Starting wpa_supplicant -B -i ' + iface + ' -c wpa_iiab.conf -D wext')
    cmdstr = 'wpa_supplicant -B -i ' + iface + ' -c wpa_iiab.conf -D wext'
    compl_proc = subproc_run(cmdstr)
    if compl_proc.returncode != 0:
        print('wpa_supplicant connection failed for ' + iface)
        return False

    print_msg('Starting dhclient ' + iface)
    cmdstr = 'dhclient -4 ' + iface
    compl_proc = subproc_run(cmdstr)
    if compl_proc.returncode != 0:
        print('dhclient failed to get IP Address for ' + iface)
        return False
    else:
        print_msg('Connection successful for ' + iface)
        # now get the ip addr
        get_wifi_dev_ip(iface)
        return True

def reset_all_ifaces():
    subproc_run('killall dhclient')
    subproc_run('killall wpa')
    try:
        os.remove('/var/lib/dhcp/dhclient.leases') # get rid of existing leases
    except OSError:
        pass

def reset_wifi_conn(iface, force=False):
    cmdstr = 'wpa_cli -i ' + iface + ' status'
    compl_proc = subproc_run(cmdstr)
    if compl_proc.returncode != 0 and force==False:
        return # assume nothing to reset
    cmdstr = 'wpa_cli -i ' + iface + ' disconnect'
    compl_proc = subproc_run(cmdstr)
    cmdstr = 'wpa_cli -i ' + iface + ' terminate'
    compl_proc = subproc_run(cmdstr)

def find_wifi_dev(filter=WIFI_DEV_PREFIX, virt=VDEV_SUFFIX):
    global usb_wifi_ifaces
    global our_wifi_macs
    usb_wifi_ifaces = {}
    compl_proc = subproc_run('ip -j a')
    if compl_proc.returncode != 0:
        print('Error accessing ip a')
    else:
        ip_info = json.loads(compl_proc.stdout)
        for item in ip_info:
            wifi_dev = item['ifname']
            if filter not in wifi_dev:
                continue
            usb_wifi_ifaces[wifi_dev] = {}
            usb_wifi_ifaces[wifi_dev]['status'] = item['operstate']
            usb_wifi_ifaces[wifi_dev]['mac'] = item['address']
            our_wifi_macs[item['address']] = wifi_dev
            if len(item['addr_info']) > 0:
                ip_addr = item['addr_info'][0]['local']
            else:
                ip_addr = None
            usb_wifi_ifaces[wifi_dev]['ip-addr'] = ip_addr
            usb_wifi_ifaces[wifi_dev]['access_cnt'] = 0
            if virt not in wifi_dev:
                usb_wifi_ifaces[wifi_dev]['vdev'] = False
            else:
                usb_wifi_ifaces[wifi_dev]['vdev'] = True

def find_wiphy():
    global usb_wifi_ifaces
    for dev in usb_wifi_ifaces:
        cmdstr = 'cat /sys/class/net/' + dev + '/phy80211/name'
        compl_proc = subproc_run(cmdstr)
        if compl_proc.returncode == 0:
            wiphy = compl_proc.stdout.split('\n')[0]
            usb_wifi_ifaces[dev]['wiphy'] = wiphy

def get_wifi_dev_ip(iface):
    global usb_wifi_ifaces

    cmdstr = 'ip -j a show dev ' + iface
    compl_proc = subproc_run(cmdstr)
    if compl_proc.returncode != 0:
        print('Error accessing ip a')
    else:
        wifi_info = json.loads(compl_proc.stdout)[0] # for some reason it's an array
        if len(wifi_info['addr_info']) > 0:
            ip_addr = wifi_info['addr_info'][0]['local']
        else:
            ip_addr = None
        usb_wifi_ifaces[iface]['ip-addr'] = ip_addr
        usb_wifi_ifaces[iface]['status'] = wifi_info['operstate']

def parse_header(header_str, delim='\r\n'):
    hdr_dict = {}
    lines = header_str.split(delim)
    hdr_dict['status'] = lines[0].split()[1]
    for l in lines[1:]:
        if ': ' in l:
            key, val = l.split(': ')
            hdr_dict[key.lower()] = val
    return hdr_dict

def subproc_run(cmd):
    compl_proc = subprocess.run(cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #ComplProc.stdout = stdout.decode()
    #ComplProc.stderr = stderr.decode()
    #ComplProc.returncode = proc.returncode
    #ComplProc.stdoutarr = stdout.decode().split('\n')
    return compl_proc

def print_msg(msg):
    if verbose:
        print(msg)

def key_capture_thread():
    global run_flag
    input()
    run_flag = False

if __name__ == "__main__":
    # Now run the main routine
    main()
