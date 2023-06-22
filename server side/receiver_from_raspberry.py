from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
import base64
import os
import send_To_Influx as send
import numpy as np
import KalmanFilter as kf
import KPI as KPI
import sent_to_firebase as firebase
import time

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Method GET - It is used to retrive the images saved in the database 
        # It "return" the newest image
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        path_camera = '/work/camera'

        if self.path == path_camera:
            
            image_path = './camera'
            images = os.listdir(image_path)
            final_image = images[-1]

            final_path = image_path+"/"+str(final_image)

            file = open(final_path, 'rb').read()
            
            self.wfile.write(base64.b64encode(file))
            
        else:

            message = "Hello, World! Here is a GET response"
            self.wfile.write(bytes(message, "utf8"))

    def do_POST(self):
        #Method POST - It is used to send the values to Olgyay according with the type of "command"
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        
        m = (self.rfile.read(int(self.headers['content-length']))).decode('utf-8')
        
        params = json.loads(m)
        
        inf = send.ToInflux()
        #Images taken by the camera (Raspberry)
        if params['command'] == 'camera': 

            im_timestamp = params['payload']['Timestamp']
            image_label = params['payload']["img_label"]
            
            with open("./camera/"+image_label, "wb") as fh:
                fh.write(base64.b64decode(params['payload']["MsgBody"]))
            
            #message = f"Hello, World! Here is a CAMERA POST response {im_timestamp}"
            #self.wfile.write(bytes(message, "utf8"))

        #Values taken by the sensors (Raspberry)
        elif params['command'] == 'sensors':

            #manage data from sensors

            #with this comman we are writing what we received in a .txt file (in future it is not necessary o yes(?))
            with open("./prova.txt", "a") as f:
                f.write(json.dumps(params['payload']))
                f.write('\n')

            val = params['payload']
            param_name = ['SCD41_co2', 'SCD41_temp', 'SCD41_hum', 'MAX6675', 'FX3001', 'SHARP', 'RAIN GAUGE', 'LPPYRA', 'SEN0170', 'BME680']
            # we call the data cleaning function
            # for each field we call Kalaman filter function
            old_values = np.NaN * np.ones(shape=(len(val),3))
            #TODO
            ranging = [150, 3, 7, 3, 10000, 100, 10000, 1000, 10000, 1] # cambiare ancora la pioggia (o non lo facciamo come il vento?)
            cleaned_value = []

            for i in range(len(val)):
                
                # controllo di non passare una stringa al kalman filter
                # la velocità e la dir del vento cambiano velocemente, possiamo non passarle nel kalman filter
                if param_name[i] == 'FX3001' or param_name[i] == 'SEN0170':
                    cleaned_value.append(val[param_name[i]])
                    
                else:
                    tmp = kf.kalmanFilter(val[param_name[i]], old_values[i,:], ranging[i])
                    
                    old_values[i,:] = tmp[1]
                    cleaned_value.append(tmp[0])


            #We calculate the KPI with the clenaed data
            kpi = KPI.Kpi_Evaluator(cleaned_value)
            final_value = kpi.Compute() # return data to send to influx and the clearness index vector to be stored

            #The cleaned data and the KPI are sent to influx
            
            inf.valuesToInflux(final_value)
            time.sleep(10)
            firebase.Firebase()
            #sendToInflux(cl_val, kpi)

            #response
            #message = f"Hello, World! Here is a SENSOR POST response {time_sensor}"
            #self.wfile.write(bytes(message, "utf8"))

        #Percentage of cloudiness (HPC)
        elif params['command'] == 'cloudiness':

            #c_timestamp = params['payload']['Timestamp']
            
            
            with open("./prova_cloudiness.txt", "a") as f:
                f.write(json.dumps(params['payload']))
                f.write('\n')
            
            #To modify - delete int cast when we create the new bucket
            cloudi = params['payload']['Cloudiness']
            clearn = params['payload']['Clearness']
            inf.cloudinessToInflux(cloudi, clearn)
            firebase.Firebase()
            #message = f"Hello, World! Here is a CAMERA POST response {c_timestamp}"
            #self.wfile.write(bytes(message, "utf8"))

        elif params['command'] == 'position':

            p_timestamp = params['payload']['Timestamp']

            lat = params['payload']['latitude']
            long = params['payload']['longitude']

            inf.positionToINflux(lat, long)
            time.sleep(10)
            firebase.Firebase()
            #message = f"Hello, World! Here is a CAMERA POST response {c_timestamp}"
            #self.wfile.write(bytes(message, "utf8"))

        else:
            
            message = "Params value Error!!!"
            self.wfile.write(bytes(message, "utf8"))



with HTTPServer(('', 8190), handler) as server:
    server.serve_forever()
