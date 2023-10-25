from bluepy.btle import UUID, Peripheral, DefaultDelegate
import time

class NotifyDelegate(DefaultDelegate):
    def __init__(self):
            DefaultDelegate.__init__(self)
    def handleNotification(self,cHandle,data):
        print("notify from "+str(cHandle)+str(data)+"\n")

#p = Peripheral("d0:3e:7d:a4:c2:8b").withDelegate(NotifyDelegate())
p = Peripheral("d0:3e:7d:c4:4a:48").withDelegate(NotifyDelegate())

#time.sleep(0.5)
dev = 0

for ser in p.getServices():
    print(str(ser))
    for chara in ser.getCharacteristics():
        print(str(chara))
        print("Handle is "+str(chara.getHandle()))
        print("properties is "+chara.propertiesToString())
        print("uuid is "+str(chara.uuid))
        if "0000ffe4" in str(chara.uuid):
            dev = chara
            dev.write("1", False)
            print("en")
        if(chara.supportsRead()):
            data = chara.read()
            print(type(data))
            print(len(data))
            print(data)
    print("\n")


try:
    while True:
        if dev:
            dev.write("1", True)
            print("en")
        if(dev.supportsRead()):
            data = dev.read()
            print(type(data))
            print(len(data))
            print(data)
        if p.waitForNotifications(1.0):
            # handleNotification() was called
            continue

        print "Waiting..."
        # Perhaps do something else here
except ZeroDivisionError as e:
    print("except:",e)
    p.disconnect()
    exit(1)
finally:
    print("final print")
    p.disconnect()
    exit(1)

p.disconnect()
exit(1)


# # get all services
# services=p.getServices()
# for service in services:
#    print(service)
#
# # get all characteristics
# chList = p.getCharacteristics()
# print("Handle   UUID                                Properties")
# print("-------------------------------------------------------")
# for ch in chList:
#    print("  0x"+ format(ch.getHandle(),'02X')  +"   "+str(ch.uuid) +" " + ch.propertiesToString())
#    if '0000ffe4' in str(ch.uuid):
#        dev = ch
# # dev.write("1")
# try:
#     while True:
#         if(dev.supportsRead()):
#             print(type(dev.read()))
#             print(dev.read())
#         if p.waitForNotifications(1.0):
#             # handleNotification() was called
#             continue
#
#         print "Waiting..."
#         # Perhaps do something else here
# except ZeroDivisionError as e:
#     print("except:",e)
#     p.disconnect()
#     exit(1)
# finally:
#     print("final print")
#     p.disconnect()
#     exit(1)
# # p.writeCharacteristic(dev.getHandle(),"12345",withResponse=True)
# p.disconnect()
# exit(1)
