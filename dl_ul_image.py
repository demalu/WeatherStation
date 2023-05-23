import time
from hybrid import *
import requests
import base64
import json

#DOWNLOAD IMAGE FROM OLGYAY SERVER
download_url = "http://130.192.20.228:8190/work/camera"

res = requests.get(download_url, stream=True)

if res.status_code == 200:
    name = str(time.strftime("%Y-%m-%d-%H-%M-%S"))
    path= "./ToBeProcessed/" + name +".jpg"
    with open(path, 'wb') as f:
        f.write(base64.b64decode(res.text))

#image = cv2.imread(path)
#cv2.imshow("output", image)
#cv2.waitKey(0)

#IMAGE PROCESSING
value = processing(path)

#UPLOAD THE RESULTS TO OLGYAY SERVER
upload_url = "http://130.192.20.228:8190/work/"
message = {
    "command": "cloudiness",
    "payload": {
        "Timestamp": time.time(),
        "Cloudiness": value
    }
}
json_data = json.dumps(message)
headers = {"Content-Type": "application/json"}

# Send the POST request to the server
response = requests.post(upload_url, data=json_data, headers=headers)

# Check the response status code
if response.status_code == 200:
    print("Data successfully sent to server!")
else:
    print("Error sending data to server:", response.status_code)

print(response.text)
