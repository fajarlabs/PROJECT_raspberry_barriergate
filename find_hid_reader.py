#from evdev import InputDevice, ecodes, list_devices
#from select import select

#keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
#dev = InputDevice("/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.4/1-1.4:1.0/0003:08FF:0009.0001/input/input0")

#barcode = ""
#while True:
#    r,w,x = select([dev], [], [])

#    for event in dev.read():
#        if event.type != 1 or event.value != 1:
#            continue
#        if event.code == 28:
#            print(barcode)
#            barcode = ""
#            break
#        barcode += keys[event.code]
import evdev

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)
