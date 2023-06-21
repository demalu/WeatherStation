# ---------------
# --- IMPORTS ---
# ---------------

# -- generic --
from datetime import datetime
import time
import base64
import requests
import json
# -- camera -- 
from picamera import PiCamera, Color

# --------------
# --- CAMERA ---
# --------------

camera = PiCamera()
time.sleep(2)
camera.rotation = 180
image_directory = './camera_images/'

# SETUP
url = "http://130.192.20.228:8190/work/"
headers = {"Content-Type": "application/json"}

while True:
	
	time_tmp = datetime.now()
	image_label = time_tmp.strftime('%y%m%d_%H%M%S.jpg')
	image_timestamp = time_tmp.strftime('%y/%m/%d %H:%M:%S')
	img_path = image_directory + image_label
	
	camera.capture(img_path)
	
	# send to olgyay
	image_64 = str(base64.b64encode(open(img_path,"rb").read()).decode("ascii"))
	payload = {
		"command": "camera",
		"payload": {
			"Timestamp": image_timestamp,
			 "MsgBody":image_64,
			 "img_label":image_label
			 }
		}
	#print("FATTO")
	payload_json = json.dumps(payload)
	headers = {'Content-Type': 'application/json', 'Accept':'text/plain'}
	try:
		response = requests.post(url, data=payload_json, headers=headers)
	except:
		print("Connection Error, retrying in 2 minutes")
		time.sleep(2*60)
	else:
		if(response.status_code == 200):
			print(f"Image successfully sent at {image_timestamp}")
	
	print(response.text)

	
	# wait for next capture
	time.sleep(5*60) 
