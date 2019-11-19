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
#!/usr/bin/python3
#import evdev

#devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
#for device in devices:
#  print(device.fn, device.name, device.phys)

#device = evdev.InputDevice("/dev/input/event0")
#print(device)
#for event in device.read_loop(): 
#  print(event)

from evdev import InputDevice, categorize, ecodes  # import * is evil :)
dev = InputDevice('/dev/input/event0')

# Provided as an example taken from my own keyboard attached to a Centos 6 box:
scancodes = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'q', 17: u'w', 18: u'e', 19: u'r',
    20: u't', 21: u'y', 22: u'u', 23: u'i', 24: u'o', 25: u'p', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'a', 31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 36: u'j', 37: u'k', 38: u'l', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'z', 45: u'x', 46: u'c', 47: u'v', 48: u'b', 49: u'n',
    50: u'm', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

capscodes = {
    0: None, 1: u'ESC', 2: u'!', 3: u'@', 4: u'#', 5: u'$', 6: u'%', 7: u'^', 8: u'&', 9: u'*',
    10: u'(', 11: u')', 12: u'_', 13: u'+', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'{', 27: u'}', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u':',
    40: u'\'', 41: u'~', 42: u'LSHFT', 43: u'|', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u'<', 52: u'>', 53: u'?', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}
#setup vars
x = ''
caps = False

#grab that shit
dev.grab()

#loop
for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        data = categorize(event)  # Save the event temporarily to introspect it
        if data.scancode == 42:
            if data.keystate == 1:
                caps = True
            if data.keystate == 0:
                caps = False
        if data.keystate == 1:  # Down events only
            if caps:
                key_lookup = u'{}'.format(capscodes.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
            else:
                key_lookup = u'{}'.format(scancodes.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
            if (data.scancode != 42) and (data.scancode != 28):
                x += key_lookup  # Print it all out!
            if(data.scancode == 28):
                print x
                x = ''
