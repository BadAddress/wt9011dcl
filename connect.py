import sys
from bluepy.btle import UUID, Peripheral,DefaultDelegate
import time
import bluepy

# for val in sys.argv:
#     print(val)
#
# if len(sys.argv) != 2:
#   print("Fatal, must pass device address:", sys.argv[0], "<device address>")
#   quit()

class MyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        # print(params)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        print(cHandle)
        print(data)

p = Peripheral()
p.setDelegate(MyDelegate())
p.connect("0c:95:41:26:2f:11")

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
   # if '0000fff1' in str(ch.uuid):
        # p.writeCharacteristic(str(ch.getHandle()), b"0100")

svc = p.getServiceByUUID( 0xfff0 )
ch = svc.getCharacteristics( 0xfff1 )[0]
# ch.write( b"\xff\xff" )
hEcg=ch.getHandle()
for descriptor in p.getDescriptors(hEcg,svc.hndEnd):
    if (descriptor.uuid==0x2902):
        print('Client Characteristic Configuration found at handle 0x{}'.format(descriptor.handle,"02X"))
        hEcgCCC=descriptor.handle
p.writeCharacteristic(hEcgCCC,bytes([1, 0]))

# svc = p.getServiceByUUID(0xfff0)
# print(svc)
# ch = svc.getCharacteristics()[0]
# print(ch.getHandle())
# p.writeCharacteristic(ch.getHandle(), b"\x02\x00")
cnt = 10
while cnt:
    if p.waitForNotifications(1.0):
        # handleNotification() was called
        continue

    print("Waiting...")
    cnt = cnt - 1
    # Perhaps do something else here

time.sleep(5)
p.disconnect()
