#!/usr/bin/env python
from __future__ import print_function
import argparse
import binascii
import os
import sys
import time
import struct
from bluepy import btle

if os.getenv('C', '1') == '0':
    ANSI_RED = ''
    ANSI_GREEN = ''
    ANSI_YELLOW = ''
    ANSI_CYAN = ''
    ANSI_WHITE = ''
    ANSI_OFF = ''
else:
    ANSI_CSI = "\033["
    ANSI_RED = ANSI_CSI + '31m'
    ANSI_GREEN = ANSI_CSI + '32m'
    ANSI_YELLOW = ANSI_CSI + '33m'
    ANSI_CYAN = ANSI_CSI + '36m'
    ANSI_WHITE = ANSI_CSI + '37m'
    ANSI_OFF = ANSI_CSI + '0m'


def hex_to_short(raw_data):
    return list(struct.unpack("hhh", bytearray(raw_data)))

def CopeData(raw_data):
    if raw_data[0] != 0x55:
        return
    if raw_data[1] == 0x61 :
        acc = [hex_to_short(raw_data[2:8])[i] / 32768.0 * 16 for i in range(0, 3)]
        gyro = [hex_to_short(raw_data[8:14])[i] / 32768.0 * 2000 for i in range(0, 3)]
        angle = [hex_to_short(raw_data[14:20])[i] / 32768.0 * 180 for i in range(0, 3)]
        print("acc:%.2f,%.2f,%.2f gyro:%.2f,%.2f,%.2f angle:%.2f,%.2f,%.2f"
         % (acc[0], acc[1], acc[2],gyro[0], gyro[1], gyro[2],angle[0], angle[1], angle[2],))
    elif raw_data[1] == 0x71:
        if raw_data[2] == 0x3A:
            mag = hex_to_short(raw_data[4:10])
            print("mag:%d,%d,%d" % (mag[0], mag[1], mag[2],))
        else :
            print("unkonw data")

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        # print(cHandle)
        # print(data)
        size = len(data)
        index = 0
        while (size - index) >= 20:
            CopeData(data[index:index+20])
            index = index + 20

class ScanPrint(btle.DefaultDelegate):

    def __init__(self, opts):
        btle.DefaultDelegate.__init__(self)
        self.opts = opts

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            status = "new"
        elif isNewData:
            status = "update"
                # return
        else:
                return

        if dev.rssi < self.opts.sensitivity or not dev.connectable:
            return

        print ('    Device (%s): %s (%s), %d dBm %s' %
               (status,
                   ANSI_WHITE + dev.addr + ANSI_OFF,
                   dev.addrType,
                   dev.rssi,
                   ('' if dev.connectable else '(not connectable)'))
               )
        for (sdid, desc, val) in dev.getScanData():
            if sdid in [8, 9]:
                print ('\t' + desc + ': \'' + ANSI_CYAN + val + ANSI_OFF + '\'')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--hci', action='store', type=int, default=0,
                        help='Interface number for scan')
    parser.add_argument('-t', '--timeout', action='store', type=int, default=2,
                        help='Scan delay, 0 for continuous')
    parser.add_argument('-s', '--sensitivity', action='store', type=int, default=-128,
                        help='dBm value for filtering far devices')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increase output verbosity')
    parser.add_argument('-m', '--mac', type=str, default='',
                        help='connect device mac addr')
    parser.add_argument('-n', '--name', type=str, default='WT901BLE67',
                        help='connect device name')
    arg = parser.parse_args(sys.argv[1:])
    btle.Debugging = arg.verbose

    scanner = btle.Scanner(arg.hci).withDelegate(ScanPrint(arg))

    if arg.mac == '':
        print (ANSI_RED + "Scanning for devices..." + ANSI_OFF)
        devices = scanner.scan(arg.timeout)
        connectaddr = None
        for d in devices:
            if not d.connectable or d.rssi < arg.sensitivity:
                continue
            for (sdid, desc, val) in d.getScanData():
                if arg.name == val:
                    print('find {} device'.format(arg.name))
                    connectaddr = d.addr
                    break
    else:
        connectaddr = arg.mac
    if connectaddr != None:
        p = btle.Peripheral()
        p.setDelegate(MyDelegate())
        try:
            p.connect(connectaddr)
            p.setMTU(247)
            # # get all services
            # services=p.getServices()
            # for service in services:
            #     print(service)
            #     if "0000ffe5" in str(service.uuid) or "0000fff0" in str(service.uuid):
            #         svc = service

            chList = p.getCharacteristics()
            print("Handle   UUID                                Properties")
            print("-------------------------------------------------------")
            for ch in chList:
               print("  0x"+ format(ch.getHandle(),'02X')  +"   "+str(ch.uuid) +" " + ch.propertiesToString())
               if '0000ffe4' in str(ch.uuid) or '0000fff1' in str(ch.uuid):
                   hEcg = ch.getHandle()
               if '0000ffe9' in str(ch.uuid) or '0000fff2' in str(ch.uuid):
                   writehdl = ch.getHandle()

            # svc = p.getServiceByUUID("0000ffe5-0000-1000-8000-00805f9a34fb")
            # print(svc)
            # ch = svc.getCharacteristics("0000ffe4-0000-1000-8000-00805f9a34fb")[0]
            # print(ch)
            #
            # writehdl = svc.getCharacteristics("0000ffe90000-1000-8000-00805f9a34fb")[0].getHandle()
            # print(writehdl)
            # hEcg = ch.getHandle()

            for descriptor in p.getDescriptors(hEcg):
                if (descriptor.uuid==0x2902):
                    p.writeCharacteristic(descriptor.handle,bytes([1, 0]))
                    print("handleNotification")

            # time.sleep(2)
            start = time.time()
            while True:
                p.waitForNotifications(1)
                if (time.time() - start) > 1:
                     start = time.time()
                     p.writeCharacteristic(writehdl,bytes([0xff, 0xaa, 0x27, 0x3A, 0x00]))

        finally:
            pass
            # p.disconnect()

if __name__ == "__main__":
    main()
