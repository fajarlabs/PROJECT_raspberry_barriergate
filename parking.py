import RPi.GPIO as gpio
import time
import os
import configparser
import requests
import sys
import json
import threading
# thermal printer library
from escpos.printer import Usb
# HID barcode 1D & 2D scanner
from evdev import InputDevice, categorize, ecodes  # import * is evil :)
# i2c lcd
import lcddriver

DISPLAY = lcddriver.lcd()

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')

RFID = InputDevice(CONFIG['HARDWARE']["rfid"])
GRAB_RFID = []
GRAB_RFID_STATUS = [] # if length > 0 is finish reading card

QRID = InputDevice(CONFIG['HARDWARE']["qrid"])
GRAB_QRID = []
GRAB_QRID_STATUS = [] # if length > 0 is finish reading card

# Provided as an example taken from my own keyboard attached to a Centos 6 box:
SCANCODES = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'q', 17: u'w', 18: u'e', 19: u'r',
    20: u't', 21: u'y', 22: u'u', 23: u'i', 24: u'o', 25: u'p', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'a', 31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 36: u'j', 37: u'k', 38: u'l', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'z', 45: u'x', 46: u'c', 47: u'v', 48: u'b', 49: u'n',
    50: u'm', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

CAPSCODES = {
    0: None, 1: u'ESC', 2: u'!', 3: u'@', 4: u'#', 5: u'$', 6: u'%', 7: u'^', 8: u'&', 9: u'*',
    10: u'(', 11: u')', 12: u'_', 13: u'+', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'{', 27: u'}', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u':',
    40: u'\'', 41: u'~', 42: u'LSHFT', 43: u'|', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u'<', 52: u'>', 53: u'?', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

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
NOTIFY START
"""
time.sleep(0.3)
gpio.output(PIN_OUT1, 1)
time.sleep(0.3)
gpio.output(PIN_OUT1, 0)

"""
LCD
"""
def show_lcd(message, valign):
	try :
		if(valign == "TOP"):
			DISPLAY.lcd_display_string(message, 1)
		if(valign == "BOTTOM"):
			DISPLAY.lcd_display_string(message, 2)
	except Exception as e :
		print(e)

"""
CLEAR LCD
"""
def clear_lcd():
	try :
		DISPLAY.lcd_clear()
	except Exception as e :
		print(e)

"""
QRID
"""
def qrid_reader():
	#setup vars
	caps = False

	#grab that shit
	QRID.grab()

	#loop
	for event in QRID.read_loop():
	    if event.type == ecodes.EV_KEY:
	        data = categorize(event)  # Save the event temporarily to introspect it
	        if data.scancode == 42:
	            if data.keystate == 1:
	                caps = True
	            if data.keystate == 0:
	                caps = False
	        if data.keystate == 1:  # Down events only
	            if caps:
	                key_lookup = u'{}'.format(CAPSCODES.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
	            else:
	                key_lookup = u'{}'.format(SCANCODES.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
	            if (data.scancode != 42) and (data.scancode != 28):
	                GRAB_QRID.append(key_lookup)  # Print it all out!
	            if(data.scancode == 28):
	                GRAB_QRID_STATUS.append(1)
	                #print("".join(GRAB_QRID))
	                # empty array
	                # del GRAB_QRID[:]

# QRID READER
t_qrid_reader = threading.Thread(target=qrid_reader, args=())
t_qrid_reader.start()

"""
RFID
"""
def rfid_reader():
	#setup vars
	caps = False

	#grab that shit
	RFID.grab()

	#loop
	for event in RFID.read_loop():
	    if event.type == ecodes.EV_KEY:
	        data = categorize(event)  # Save the event temporarily to introspect it
	        if data.scancode == 42:
	            if data.keystate == 1:
	                caps = True
	            if data.keystate == 0:
	                caps = False
	        if data.keystate == 1:  # Down events only
	            if caps:
	                key_lookup = u'{}'.format(CAPSCODES.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
	            else:
	                key_lookup = u'{}'.format(SCANCODES.get(data.scancode)) or u'UNKNOWN:[{}]'.format(data.scancode)  # Lookup or return UNKNOWN:XX
	            if (data.scancode != 42) and (data.scancode != 28):
	                GRAB_RFID.append(key_lookup)  # Print it all out!
	            if(data.scancode == 28):
	                GRAB_RFID_STATUS.append(1)
	                #print("".join(GRAB_RFID))
	                # empty array
	                # del GRAB_RFID[:]

# RFID READER
t_rfid_reader = threading.Thread(target=rfid_reader, args=())
t_rfid_reader.start()

"""
Print ticket
"""
def print_thermal(header, title_first, title_seconds, date_time, qr_code, gate_info, type_scan ):
	result = False
	try :
		p = Usb(
			int(CONFIG['PRINTER']['vid'],0),
			int(CONFIG['PRINTER']['pid'],0),
			int(CONFIG['PRINTER']['timeout'],0),
			int(CONFIG['PRINTER']['ep1in'],0),
			int(CONFIG['PRINTER']['ep1out'],0)
		)
		p.set("CENTER", "B", "A", 2, 2)
		p.text(str(header)+"\n\n")
		p.set("CENTER", "A", "normal", 1, 1)
		p.text(str(title_first)+"\n")
		p.text(str(title_seconds)+"\n")
		p.text(str(date_time)+"\n\n") 
		if(type_scan == 0):
			p.qr(str(qr_code),0,10)
		else :
			p.barcode(str(qr_code), "CODE128", function_type="B")
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
		file = CONFIG['AUDIO']['voice_path']+"/welcome.mp3"
		os.system("mpg123 " + file+ " &")
		result = True
	except Exception as e :
		print(e)

	return result

"""
Play sound rfid
"""
def play_sound_rfid():
	result = False
	try :
		file = CONFIG['AUDIO']['voice_path']+"/welcome_short.mp3"
		os.system("mpg123 " + file+ " &")
		result = True
	except Exception as e :
		print(e)

	return result

def get_tiket():
	try :
		url = CONFIG['SERVER']['ip']+'parking_system/api/gate/gate_in_sticker.php?action=send_ticket&loc='+CONFIG['CLIENT']['loc']+'&gate='+CONFIG['CLIENT']['gate']
		print(url)
		return requests.get(url).json()
	except Exception as e :
		print(e)

	return None

def send_card(card_id):
	try :
		url = CONFIG['SERVER']['ip']+'parking_system/api/gate/gate_in_card.php?action=send_card&loc='+\
		CONFIG['CLIENT']['loc']+\
		'&gate='+CONFIG['CLIENT']['gate']+"&card_id="+card_id
		print(url)
		return requests.get(url).json()
	except Exception as e :
		print(e)

	return None

def send_qr_code(qr_code):
	try :
		url = CONFIG['SERVER']['ip']+'parking_system/api/gate/gate_in_qr_code.php?action=send_qr_code&loc='+\
		CONFIG['CLIENT']['loc']+\
		'&gate='+CONFIG['CLIENT']['gate']+"&qr_code="+qr_code
		print(url)
		return requests.get(url).json()
	except Exception as e :
		print(e)

	return None

def record_cctv(id_parking, ip_cctv, username_cctv, password_cctv):
	try :
		url = CONFIG['SERVER']['ip']+'parking_system/api/gate/camera_cctv.php?loc='+\
		CONFIG['CLIENT']['loc']+\
		'&gate='+CONFIG['CLIENT']['gate']+\
		"&id_parking="+id_parking+\
		"&ip_cctv="+ip_cctv+\
		"&username_cctv="+username_cctv+\
		"&password_cctv="+password_cctv
		print(url)
		return requests.get(url).json()
	except Exception as e :
		print(e)

	return None

track = 0
while True:
	if(track == 0):
		show_lcd("Selamat Datang!", "TOP")
		show_lcd("di Crown Parking", "BOTTOM")
	if (gpio.input(PIN_IN1) == False):
		clear_lcd()
		print("1.) TEKAN TOMBOL TICKET")
		if (track < 1) :
			sticker_data = get_tiket()
			if(sticker_data != None):

				# PLAY SOUND
				t_play_sound = threading.Thread(target=play_sound, args=())
				t_play_sound.start()
				
				# LCD
				show_lcd("Silahkan ambil tiket!", "TOP")
				show_lcd("Silahkan masuk","BOTTOM")

				# THERMAL PRINTER
				print_thermal(
					'KARCIS PARKIR', 
					sticker_data["location"], 
					sticker_data["address"], 
					'Tanggal : '+sticker_data["parking_date"], 
					sticker_data["qr_code"], 
					sticker_data["gate"],
					int(sticker_data["type_scan"])
				)

				# CAPTURE CCTV
				t_capture = threading.Thread(
					target=record_cctv, 
					args=(
						sticker_data["id_parking"],
						sticker_data["ip_cctv"],
						sticker_data["username_cctv"],
						sticker_data["password_cctv"],
					)
				)
				t_capture.start()
				track += 1
			else :
				# do something with error
				pass
	elif(len(GRAB_RFID_STATUS) > 0) :
		clear_lcd()
		print("1.) BACA READER")
		rfid_data = "".join(GRAB_RFID)
		if (track < 1) :
			sticker_data = get_tiket()
			if(sticker_data != None):
				rfid_json = send_card(rfid_data)
				card_status = int(rfid_json["status"])
				running_text = rfid_json["description"]
				
				# card success
				if(card_status == 1):
					# LCD
					show_lcd("Verifikasi berhasil!", "TOP")
					show_lcd("Silahkan masuk","BOTTOM")
					
					# PLAY SOUND
					t_play_sound = threading.Thread(target=play_sound_rfid, args=())
					t_play_sound.start()

					# CAPTURE CCTV
					t_capture = threading.Thread(
						target=record_cctv, 
						args=(
							sticker_data["id_parking"],
							sticker_data["ip_cctv"],
							sticker_data["username_cctv"],
							sticker_data["password_cctv"],
						)
					)
					t_capture.start()

					track += 1
					print("Kartu sukses")
				else :
					print("Kartu tidak terdaftar / rusak.")
					pass
			else :
				# do something with error
				pass

			# clear data
			del GRAB_RFID[:]
			del GRAB_RFID_STATUS[:]
	elif(len(GRAB_QRID_STATUS) > 0) :
		clear_lcd()
		print("1.) BACA QR READER")
		qrid_data = "".join(GRAB_QRID)
		if (track < 1) :
			sticker_data = get_tiket()
			if(sticker_data != None):
				qrid_json = send_qr_code(qrid_data)
				qrid_status = int(qrid_json["status"])
				running_text = qrid_json["description"]
				
				# card success
				if(qrid_status == 1):
					# LCD
					show_lcd("Verifikasi berhasil!", "TOP")
					show_lcd("Silahkan masuk","BOTTOM")
					
					# PLAY SOUND
					t_play_sound = threading.Thread(target=play_sound_rfid, args=())
					t_play_sound.start()

					# CAPTURE CCTV
					t_capture = threading.Thread(
						target=record_cctv, 
						args=(
							sticker_data["id_parking"],
							sticker_data["ip_cctv"],
							sticker_data["username_cctv"],
							sticker_data["password_cctv"],
						)
					)
					t_capture.start()

					track += 1
					print("Kartu sukses")
				else :
					print("Kartu tidak terdaftar / rusak.")
					pass
			else :
				# do something with error
				pass

			# clear data
			del GRAB_QRID[:]
			del GRAB_QRID_STATUS[:]
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
