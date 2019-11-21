import requests

def get_tiket():
	url = 'http://ridwansyah/parking_system/api/gate/gate_in_sticker.php?action=send_ticket&loc=loc_191023112935_48125&gate=gt_191024120244_11252'
	myobj = {'somekey': 'somevalue'}
	x = requests.post(url, data = myobj)
	print(x.text)