from bluepy.btle import Scanner, DefaultDelegate
from bluepy.btle import UUID, Peripheral

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)

scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(5)

dev_name_uuid = UUID(0xFFE9)
connectflag = 0
p = Peripheral()
p.disconnect()
for dev in devices:
    if connectflag:
        break
    print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
        if 'WT901BLE112233' in value:
            print(" %s = %s " % (desc, value))
            print("connect dev")
            p.connect(dev.addr, dev.addrType)
            connectflag = 1
            break
if connectflag:
    # get all services
    services=p.getServices()
    for service in services:
        print(service)

    # get all characteristics
    chList = p.getCharacteristics()
    print("Handle   UUID                                Properties")
    print("-------------------------------------------------------")
    for ch in chList:
        print("  0x"+ format(ch.getHandle(),'02X')  +"   "+str(ch.uuid) +" " + ch.propertiesToString())
        if '0000ffe4' in str(ch.uuid):
            dev = ch
            p.writeCharacteristic(ch.getHandle(), "\x02\x00")
    # p.writeCharacteristic(str(ch.getHandle()), b"1", True)
    # p.waitForNotifications(5)
    if dev.supportsRead():
        print('read')
        print(dev.read())
    else:
        print('no read support')
    p.disconnect()
else:
    print('no dev connect')
