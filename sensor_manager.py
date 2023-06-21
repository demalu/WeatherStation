# ---------------
# --- IMPORTS ---
# ---------------

# -- generic --
from rich import print as rprint
from datetime import datetime
import time
import serial
import requests
import json
import argparse
import os, os.path
import re

#import pandas as pd

# -- DHT --
import adafruit_dht
from board import D4
dht_sensor = adafruit_dht.DHT22(D4)
# -- SENSIRION SCD41 --
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection
from sensirion_i2c_scd import Scd4xI2cDevice
parser = argparse.ArgumentParser()
parser.add_argument('--i2c-port', '-p', default='/dev/i2c-1')
args = parser.parse_args()
# -- RAIN GAUGE --
import RPi.GPIO as GPIO
CALIBRATION = 0.2794
PIN = 17
GPIO.setmode(GPIO.BCM)  
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
rain = 0
def cb(channel):
	global rain
	rain = rain + CALIBRATION
GPIO.add_event_detect(PIN, GPIO.FALLING, callback=cb, bouncetime=300)
#LPPYRA LiteS
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.register_read_message import ReadInputRegistersResponse
client = ModbusClient(method='rtu', port='/dev/ttyUSB6', stopbits=2, bytesize=8, parity='E', baudrate=19200, timeout=0.3)
connection = client.connect()
#WAVESHARE 4G/GPS HAT
from GPS_IP import send_at, get_gps_position, power_on, power_down
gps_ser = serial.Serial('/dev/ttyS0',115200)
gps_ser.flushInput()
power_key = 6
rec_buff = ''
rec_buff2 = ''
time_count = 0

def correctPosition(position):
	comma_pos = position.find('.')
	integer_part = ''.join(list(filter(str.isdigit, position[:comma_pos-2])))
	tmp = ''.join(list(filter(str.isdigit, position[comma_pos-2::])))
	#print("!!!!! ", tmp)
	tmp2 = str(float(tmp)/6)
	floating_part = ''.join(list(filter(str.isdigit, tmp2))[:8])
	corrected_position = float(''.join([integer_part, '.', floating_part]))
	return corrected_position




# SETUP
arduino = serial.Serial('/dev/ttyUSB0', 57600, timeout=.1)
url = "http://130.192.20.228:8190/work/"
headers = {"Content-Type": "application/json"}
MAX_IMAGES = 1440 #int(5*24*60/5)
MAX_MEASUREMENTS = 1440 #int(5*24*60/5)
filename = "measurements/measurements.json"
images_dir_path = os.getcwd() + "/camera_images"
meas_dir_path = os.getcwd() + "/measurements/measurements.json"

# read GPS and publish position
#time.sleep(60)   #  !!! DA SCOMMENTARE QUANDO MONTEREMO TUTTO
try:
	latitude = 0
	longitude = 0

	power_on(power_key, gps_ser)
	pos_str = get_gps_position(gps_ser)
	print("!!!! ----", pos_str)
	pos = re.split(": |,", pos_str)
	lat_tmp = pos[1]
	lon_tmp = pos[3]
	latitude = correctPosition(lat_tmp)
	longitude = correctPosition(lon_tmp)

	timestamp = datetime.now().strftime('%y/%m/%d %H:%M:%S')
	payload = {
			"command": "position",
			"payload":{
				"Timestamp": timestamp,
				"latitude": latitude,
				"longitude": longitude
				}
			}
	payload_json = json.dumps(payload, indent=4)
	print(payload_json)	
except:
	pass	
 

while True:
	
	sensors_timestamp = datetime.now().strftime('%y%m%d_%H%M%S.jpg')
	timestamp = datetime.now().strftime('%y/%m/%d %H:%M:%S')
	
	
	# -- READ FROM ARDUINO --
	data_byte = arduino.readline()[:-2]
	while(not data_byte):
		data_byte = arduino.readline()[:-2]
	
	data = data_byte.decode("utf-8")
	measures = data.split(",")
	#print(measures)
	#print(data)
	
	temp_MAX6675 = float(measures[1].split(":")[1])
	#print(type(temp_MAX6675))
	winddir_FX3001 = float(measures[2].split(":")[1])
	dustdensity_SHARP = float(measures[4].split(":")[1])
	wind_speed = float(measures[3].split(":")[1])
	pressure = float(measures[5].split(":")[1])
	
	
	'''
	# -- read from DHT --
	try:
		hum_DHT22 = dht_sensor.humidity
		temp_DHT22 = dht_sensor.temperature
	except:
		hum_DHT22 = -1
		temp_DHT22 = -1
		
	DHT22_results = {
			"temp": temp_DHT22, 
			"hum": hum_DHT22
			}
	'''
	try:
		# -- read from SCD41 --
		with LinuxI2cTransceiver(args.i2c_port) as i2c_transceiver:
		#with LinuxI2cTransceiver('/dev/i2c-1') as i2c_transceiver:
			scd41 = Scd4xI2cDevice(I2cConnection(i2c_transceiver))
			#i2c_connection = I2cConnection(i2c_transceiver)
			#scd41 = Scd4xI2cDevice(i2c_connection)
			scd41.stop_periodic_measurement()
			
			#print("scd41 Serial Number: {}".format(scd41.read_serial_number()))

			#print("scd4x Serial Number: {}".format(scd41.read_serial_number()))
			#Clean up potential SCD40 states
			
			scd41.start_periodic_measurement()
			time.sleep(5)
			co2_SCD41, temp_SCD41, hum_SCD41 = scd41.read_measurement()
		
		SCD41_results = {"co2_SCD41":co2_SCD41.co2, "temp_SCD41": temp_SCD41.degrees_celsius, "hum_SCD41":hum_SCD41.percent_rh}
	except:
		SCD41_results = {"co2_SCD41":0.0, "temp_SCD41": 0.0, "hum_SCD41":0.0}

	# -- read from rain gauge --
	# -- raing gauge read above using interrupts --
	
	# -- read from pyranometer --
	registers = client.read_input_registers(0, 6, unit=0x01)
	solar_radiation  = registers.registers[2]
	
	
	
	payload = {
		"command": "sensors",
		"payload":{
			#"Timestamp": timestamp,
			"SCD41_co2":SCD41_results["co2_SCD41"],
			"SCD41_temp":SCD41_results["temp_SCD41"],
			"SCD41_hum":SCD41_results["hum_SCD41"],
			"MAX6675":temp_MAX6675,
			"FX3001":winddir_FX3001,
			"SHARP":dustdensity_SHARP,
			"RAIN GAUGE":rain,
			"LPPYRA":solar_radiation,
			"SEN0170":wind_speed,
			"BME680":pressure
			}
		}
	print(payload)
	
	payload_json = json.dumps(payload, indent=4)
	#print(payload_json)
	
	#print(payload_json)
	
	try:
		response = requests.post(url, data=payload_json, headers=headers)
	except:
		print("Connection Error, retrying in 2 minutes")
		time.sleep(2*60)
	else:
		if response.status_code == 200:
			print(f"Data successfully sent at {timestamp}")
	
	print(response.text)
    

# ---------------------------------------------------------------------#

    # save measurements on a json file
	n_measur_old = 0
	n_measur_new = 0
	with open(filename, 'r') as infile: 
		try:
			measurements = json.load(infile)
			n_measur_old = len(measurements)
			measurements.append(payload)
			n_measur_new = len(measurements)
		except json.decoder.JSONDecodeError as e:
			measurements = [payload]
			n_measur_new = len(measurements)
	
	with open(filename, 'w') as outfile:
		outfile.write(json.dumps(measurements, indent=4))
	
	# resuming print

	rprint("[bold #32cd32]MEASUREMENT SAVING:[/bold #32cd32]")
	rprint("\t # old measurements: ", n_measur_old)
	rprint("\t # new measurements: ", n_measur_new)
	
	
# ---------------------------------------------------------------------#
	
	# manage the maximum number of images and measurements
	# saved locally
	
	# --- images --- DA SPOSTARE NEL FILE camerea_manager.py
	n_images_old = 0
	n_images_new = 0
	
	images_list = [name for name in os.listdir(images_dir_path)]
	images_list.sort()
	n_images = len(images_list)
	n_images_old = n_images
	
	if n_images > MAX_IMAGES:
		n_to_delete = n_images - MAX_IMAGES
		for ele in range(n_to_delete):
			ele_to_delete = images_dir_path + "/" + images_list[0]
			os.remove(ele_to_delete)
			images_list = [name for name in os.listdir(images_dir_path)]
			images_list.sort()
	n_images_new = len(images_list)
	
	rprint("[bold #76ff7a]IMAGES DELETING:[/bold #76ff7a]")
	rprint("\t # old images: ", n_images_old)
	rprint("\t # new images: ", n_images_new)
	
	# --- measurements ---
	n_measur_old = 0
	n_measur_new = 0
	deleted = False
	measurements_tmp = []
	with open(meas_dir_path,'r+') as file:
		measurements = json.load(file)
		n_meas = len(measurements)
		n_measur_old = n_meas
		if n_meas > MAX_MEASUREMENTS:
			n_to_delete = n_meas - MAX_MEASUREMENTS
			measurements_tmp = measurements[n_to_delete::]
			deleted = True
			
	if deleted:
		with open(meas_dir_path,'w', encoding='utf-8') as file:
			file.write(json.dumps(measurements_tmp,  indent=4))
		n_measur_new = len(measurements_tmp)
	else:
		n_measur_new = n_measur_old
	
	rprint("[bold #ffa500]MEASUREMENTS DELETING:[/bold #ffa500]")
	rprint("\t # old measurements: ", n_measur_old)
	rprint("\t # new measurements: ", n_measur_new)
			
	
#----------------------------------------------------------------------#
	# clear rain of rain gauge -- every tot min is cleared
	rain = 0
    
	time.sleep(5*60)






