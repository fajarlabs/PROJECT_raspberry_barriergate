import RPi.GPIO as gpio
import time
import os
import configparser
import requests
# thermal printer library
from escpos.printer import Usb
# HID barcode 1D & 2D scanner
from evdev import InputDevice, categorize, ecodes  # import * is evil :)

config = configparser.ConfigParser()
config.read('config.ini')

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
Define Thermal USB 
View info : sudo lsusb -vvv -d 0483:5840
"""
ID_VENDOR = int(config['PRINTER']['vid'],0)
ID_PRODUCT = int(config['PRINTER']['pid'],0)
TIMEOUT = int(config['PRINTER']['timeout'],0)
EP_1_IN = int(config['PRINTER']['ep1in'],0)
EP_1_OUT =int(config['PRINTER']['ep1out'],0)

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
		os.system("mpg123 " + file+ " &")
		result = True
	except Exception as e :
		print(e)

	return result

"""
Request capture
"""
# def cctv_capture():
# 	result = False
# 	try :
# 		url = ""
# 		os.system("curl " + url)
# 		result = True
# 	except Exception as e :
# 		print(e)

# 	return result

# POST
def get_tiket():
	url = 'https://www.w3schools.com/python/demopage.php'
	myobj = {'somekey': 'somevalue'}
	x = requests.post(url, data = myobj)
	print(x.text)

# GET
def camera_request():
	url = 'https://www.w3schools.com/python/demopage.php'
	PARAMS = {'address':location} 
	x = requests.get(url, params  = PARAMS)
	print(x.text)

track = 0
while True:
	if (gpio.input(PIN_IN1) == False):
		print("1.) TEKAN TOMBOL TICKET")
		if (track < 1) :
			print_thermal('KARCIS PARKIR', 'MALL EPICENTRUM', 'Gedung Epicentrum Kuningan', 'Tanggal : 11/20/2019    12:39', '12345', 'Gate 1')
			play_sound()
			track += 1
	else :
		if (track > 0):
			# waiting vld sensor
			track_vld = 0
			while True :
				if (gpio.input(PIN_IN2) == False):
					if(track_vld < 1):
						print("2.) MOTOR SEDANG DI ATAS VLD")
						track_vld += 1
				else :
					if((track_vld > 0) and (track_vld < 2)):
						print("3.) MOTOR SUDAH LEWATI VLD")
						track_vld += 1
						if(track_vld > 1):
							print("4.) PROSES TUTUP PALANG PARKIR")
							time.sleep(0.3)
							gpio.output(PIN_OUT1, 1)
							time.sleep(0.3)
							gpio.output(PIN_OUT1, 0)
							print("5.) TRANSAKSI BERAKHIR")
							track = 0
							break
				time.sleep(0.2)
	time.sleep(0.2)
