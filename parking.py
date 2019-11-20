import RPi.GPIO as gpio
import time
import os
# thermal printer library
from escpos.printer import Usb
# HID barcode 1D & 2D scanner
from evdev import InputDevice, categorize, ecodes  # import * is evil :)

"""
Define Thermal USB 
View info : sudo lsusb -vvv -d 0483:5840
"""
ID_VENDOR = 0x0483
ID_PRODUCT = 0x5840
TIMEOUT = 0
EP_1_IN = 0x81
EP_1_OUT = 0x03

"""
Remove warning
"""
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

# output pin relay module
PIN_OUT1 = 10
PIN_OUT2 = 9
PIN_OUT3 = 11
PIN_OUT4 = 8

# input pin optocoupler
PIN_IN1 = 12
PIN_IN2 = 13
PIN_IN3 = 19
PIN_IN4 = 20

# setup pin as output
gpio.setup(PIN_OUT1, gpio.OUT) # trigger mainless barrier gate
gpio.setup(PIN_OUT2, gpio.OUT)
gpio.setup(PIN_OUT3, gpio.OUT)
gpio.setup(PIN_OUT4, gpio.OUT)

# setup pin as input
gpio.setup(PIN_IN1, gpio.IN) # print ticket
gpio.setup(PIN_IN2, gpio.IN) # vld
gpio.setup(PIN_IN3, gpio.IN)
gpio.setup(PIN_IN4, gpio.IN)

"""
Print ticket
"""
def print_thermal(header, title_first, title_seconds, date_time, qr_code, gate_info ):
	result = False
	try :
		p = Usb(ID_VENDOR,ID_PRODUCT,TIMEOUT,EP_1_IN,EP_1_OUT)
		p.set("CENTER", "B", "A", 2, 2)
		p.text(str(header)+"\n\n")
		p.set("CENTER", "A", "normal", 1, 1)
		p.text(str(title_first)+"\n")
		p.text(str(title_seconds)+"\n")
		p.text(str(date_time)+"\n\n") 
		#p.barcode(str(qr_code), "CODE128", function_type="B")
		p.qr(str(qr_code),0,10)
		p.text("\nPintu Masuk : "+str(gate_info)+"\n*** TERIMAKASIH ***\n\n\n")

		result = True
	except Exception as e :
		print(e)

	return result

"""
Play sound
"""
def play_sound():
	result = False
	try :
		file = "/home/pi/raspberry_parking/sounds/welcome.mp3"
		os.system("mpg123 " + file)
		result = True
	except Exception as e :
		print(e)

	return result

"""
Request capture
"""
def cctv_capture():
	result = False
	try :
		url = ""
		os.system("curl " + url)
		result = True
	except Exception as e :
		print(e)

	return result

track = 0
while True:
	if (gpio.input(PIN_IN1) == False):
		if (track < 1) :
			print_thermal('KARCIS PARKIR', 'MALL EPICENTRUM', 'Gedung Epicentrum Kuningan', 'Tanggal : 11/20/2019    12:39', '12345', 'Gate 1')
			play_sound()
			track += 1
		if (track > 0):
			# waiting vld sensor
			track_vld = 0
			while True :
				if (gpio.input(PIN_IN2) == False):
					if(track_vld < 1):
						track_vld += 1
				else :
					if(track_vld > 0):
						track_vld += 1
				if(track_vld > 1):
					break
			track = 0 # reset track
			time.sleep(0.5)
			gpio.output(PIN_OUT1, 1)
			time.sleep(0.3)
			gpio.output(PIN_OUT1, 0)


    time.sleep(0.2)
