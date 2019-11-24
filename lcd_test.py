import lcddriver
import time

display = lcddriver.lcd()
try :
    display.lcd_display_string("Hello i2C top", 1)
    display.lcd_display_string("Hello i2C bottom", 2)
except Exception as e :
    print(e)

time.sleep(2)
display.lcd_clear()