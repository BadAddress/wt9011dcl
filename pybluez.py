#!/usr/bin/env python
# --*--coding=utf-8--*--
# pip install pybluez

import time
import bluetooth

alreadyFound = []

def findDevs():
    foundDevs = discover_devices(lookup_names=True)
    for (addr,name) in foundDevs:
        if addr not in alreadyFound:
            print("[*]蓝牙设备:" + str(name))
            print("[+]蓝牙MAC:" + str(addr))
            alreadyFound.append(addr)

while True:
    findDevs()
    time.sleep(5)