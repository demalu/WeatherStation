import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS



class ToInflux():

    def __init__(self):
        
        self.bucket = "Prova2"
        self.org = "Polito"
        self.token = "your-token"
        self.url = "https://olgyay.polito.it:8090"
        self.measuremet = "Oudoor_data"

    def valuesToInflux(self,data):

        #Client definition
        client = influxdb_client.InfluxDBClient(url = self.url, token = self.token, org = self.org, verify_ssl=False)

        #write_api in order to configurate the writer object
        write_api = client.write_api(write_options=SYNCHRONOUS)

        p = []
        measurement = self.measuremet
        print(data[0])
        Co2 = influxdb_client.Point(measurement).field("Co2", float(data[0]))
        p.append(Co2)
        temp = influxdb_client.Point(measurement).field("Humidity", float(data[2]))
        p.append(temp)
        hum = influxdb_client.Point(measurement).field("Temperature", float(data[1]))
        p.append(hum)
        mrt = influxdb_client.Point(measurement).field("Mrt", float(data[3]))
        p.append(mrt)
        wind_d = influxdb_client.Point(measurement).field("Wind Direction", float(data[4]))
        p.append(wind_d)
        part = influxdb_client.Point(measurement).field("Dust density", float(data[5]))
        p.append(part)
        rain_l = influxdb_client.Point(measurement).field("Rain Level", float(data[6]))
        p.append(rain_l)
        irr = influxdb_client.Point(measurement).field("Irradiation", float(data[7]))
        p.append(irr)
        wind_s = influxdb_client.Point(measurement).field("Wind Speed", float(data[8]))
        p.append(wind_s)
        pr = influxdb_client.Point(measurement).field("Pressure",float(data[9]))
        p.append(pr)
        aiq = influxdb_client.Point(measurement).field("Air quality Index", float(data[10]))
        p.append(aiq)
        humidex = influxdb_client.Point(measurement).field("Humidex", float(data[11]))
        p.append(humidex)
        moci = influxdb_client.Point(measurement).field("Moci", float(data[12]))
        p.append(moci)
        ah = influxdb_client.Point(measurement).field("Absolute Humidity",float(data[13]))
        p.append(ah)
        

        utci = influxdb_client.Point(measurement).field("UTCI",float(data[14]))
        p.append(utci)
        pet = influxdb_client.Point(measurement).field("PET",float(data[15]))
        p.append(pet)
        twb = influxdb_client.Point(measurement).field("twb",float(data[16]))
        p.append(twb)
        tdp = influxdb_client.Point(measurement).field("tdp",float(data[17]))
        p.append(tdp)
        wbgt = influxdb_client.Point(measurement).field("WBGT",float(data[18]))
        p.append(wbgt)
        hiri = influxdb_client.Point(measurement).field("HIRI",float(data[19]))
        p.append(hiri) 
        t_op = influxdb_client.Point(measurement).field("operative temperature",float(data[20]))
        p.append(t_op) 
        try:
            dif = influxdb_client.Point(measurement).field("dif",float(data[21]))
            p.append(dif)
            dni = influxdb_client.Point(measurement).field("dni",float(data[22]))
            p.append(dni)
        except:
            print("erore nello split - 2")

        # -- da completare in KPI.py --
        '''
        
        # hiri = influxdb_client.Point(measurement).field("hiri",float(data[12]))
        # p.append(hiri)
        '''
        
       
        write_api.write(bucket=self.bucket, org = self.org, record = p)



    def cloudinessToInflux(self, cloud, clear):
        #Client definition
        client = influxdb_client.InfluxDBClient(url = self.url, token = self.token, org = self.org, verify_ssl=False)

        measurement = self.measuremet
        p = []
        #write_api in order to configurate the writer object
        write_api = client.write_api(write_options=SYNCHRONOUS)

        cloudiness = influxdb_client.Point(measurement).field("Cloudiness", cloud)
        p.append(cloudiness)
        clearness = influxdb_client.Point(measurement).field("Clearness", clear)
        p.append(clearness)

        write_api.write(bucket=self.bucket, org = self.org, record = p)
        

    def positionToINflux(self, lat, long):

         #Client definition
        client = influxdb_client.InfluxDBClient(url = self.url, token = self.token, org = self.org, verify_ssl=False)

        measurement = self.measuremet
        #write_api in order to configurate the writer object
        write_api = client.write_api(write_options=SYNCHRONOUS)

        latitude = influxdb_client.Point(measurement).field("Latitude", lat)
        longitude =  influxdb_client.Point(measurement).field("Longitude", long)

        write_api.write(bucket=self.bucket, org = self.org, record = [latitude, longitude])

        
