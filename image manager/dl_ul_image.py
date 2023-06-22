import time
from hybrid import *
#from hybrud2 import *
import requests
import base64
import json
from undistorted import undistort
import cv2
import os
from preprocessing import preprocessing
#from FISHEYE import undistort

def remove_files_in_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


if __name__=="__main__":
    while True:
        #EMPTY DIRECTORY
        remove_files_in_directory("./ToBeProcessed")
        # DOWNLOAD IMAGE FROM OLGYAY SERVER
        download_url = "http://130.192.20.228:8190/work/camera"
        res = requests.get(download_url, stream=True)

        if res.status_code == 200:
            name = str(time.strftime("%Y-%m-%d-%H-%M-%S"))
            path= "./ToBeProcessed/" + name +".jpg"
            with open(path, 'wb') as f:
                f.write(base64.b64decode(res.text))

        #path="D:/Universita/Polito/Interdisciplinary/ML/prova.png"
        #name = "prova"
        image = cv2.imread(path)
        #cv2.imwrite("./ToBeProcessed/" + name +".jpg", image)
        #cv2.imshow("output", image)
        #cv2.waitKey(0)
        #IMAGE PREPROCESSING
        image = preprocessing(image)
        #cv2.imwrite("./ToBeProcessed/" + name + "_preprocessed.jpg", image)
        value, processed_image = processing(image)
        #cv2.imwrite("./ToBeProcessed/" + name + "_processed.jpg", processed_image)
        #UPLOAD THE RESULTS TO OLGYAY SERVER
        upload_url = "http://130.192.20.228:8190/work/"
        message = {
            "command": "cloudiness",
            "payload": {
                "Timestamp": time.time(),
                "Cloudiness": value,
                "Clearness": 1-value
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
