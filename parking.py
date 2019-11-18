import RPi.GPIO as gpio
import time
import os
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
gpio.setup(PIN_OUT1, gpio.OUT)
gpio.setup(PIN_OUT2, gpio.OUT)
gpio.setup(PIN_OUT3, gpio.OUT)
gpio.setup(PIN_OUT4, gpio.OUT)

# setup pin as input
gpio.setup(PIN_IN1, gpio.IN)
gpio.setup(PIN_IN2, gpio.IN)
gpio.setup(PIN_IN3, gpio.IN)
gpio.setup(PIN_IN4, gpio.IN)

while True:
    if (gpio.input(PIN_IN1) == False):
        print("CETAK TIKET")
        file = "welcome.mp3"
        os.system("mpg123 " + file)
    time.sleep(0.2)
