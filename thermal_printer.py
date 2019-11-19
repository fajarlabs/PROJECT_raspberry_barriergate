from escpos.printer import Usb

"""
Define Thermal USB 
View info : sudo lsusb -vvv -d 0483:5840
"""
ID_VENDOR = 0x0483
ID_PRODUCT = 0x5840
TIMEOUT = 0
EP_1_IN = 0x81
EP_1_OUT = 0x03

p = Usb(ID_VENDOR,ID_PRODUCT,TIMEOUT,EP_1_IN,EP_1_OUT)
p.set("CENTER", "B", "A", 2, 2)
p.text("KARCIS PARKIR\n\n")
p.set("CENTER", "A", "normal", 1, 1)
p.text("MALL EPICENTRUM\n")
p.text("Gedung Epicentrum Kuningan\n")
p.text("Tanggal : 11/20/2019   12:39\n\n") 
#p.barcode("123456789", "CODE128", function_type="B")
p.qr("S4353453",0,10)
p.text("\nPintu Masuk : Gate 1\n*** TERIMAKASIH ***\n\n\n")

