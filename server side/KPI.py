import numpy as np
import math
import datetime
import copy

from sympy.solvers import solve
from sympy import Symbol

from pythermalcomfort.models import utci
from climate_indices.indices import pet
from pythermalcomfort.models import wbgt
from metpy.calc import wet_bulb_temperature
from influxdb_client import InfluxDBClient
from metpy.units import units
from math import atan

class Kpi_Evaluator():

    def __init__(self, cleaned_value):
        self.complete_value:list = cleaned_value
        self.co2 = cleaned_value[0] #co2 
        self.T = cleaned_value[1] - 6 #temperature (-6 for calibration)
        self.RH = cleaned_value[2] #rel humidity
        self.WS = cleaned_value[8] #windspeed
        self.t_dew = self.t_dew_point()
        self.mrt, self.t_globe = self.T_glob_evaluation(cleaned_value[3]) # mrt e t_globe termocopia adattato
        self.press = cleaned_value[9] # ?? # pressione
        self.C_P = cleaned_value[5]#particolato
        if cleaned_value[7] < 10000:
            self.irr = cleaned_value[7] #irradiation
        else:
            self.irr = 0
            self.complete_value[7] = 0
        self.twb = self.twb_calculator()#wet temp bulb
        self.lat = 45.6291515 #latitudine 
        self.long = 7.65973938 #longitudine
        

    def Compute(self):
        '''
        complete_value:
            0) co2
            1) Temp
            2) relat hum
            3) mrt
            4) wind dir
            5) dust density
            6) rain level
            7) ghi
            8) wind speed
            9) pressure
            --- da qua in poi calcolati
            10) AIQ
            11) HUMIDEX
            12) MOCI
            13) AH
            14) UTCI
            15) PET
            16) TWB -- wet bulb
            17) TDP -- dew point
            ) T_GLOBE  # non la manderei
            18) WBGT
            19) HIRI
            20) t_op # operative temperature
            21) DIFF        
            22) DNI         
        '''

        ## - 6 degrees to temp (for calibration)
        self.complete_value[1] = self.complete_value[1] - 6

        ## subst mrt taken from sensors with the one computed
        self.complete_value[3] = self.mrt

        aiq = round(self.AIQ(), 2)
        self.complete_value.append(aiq)

        humidex = round(self.HUMIDEX(), 2)
        self.complete_value.append(humidex)
        
        moci = round(self.MOCI(), 2)
        self.complete_value.append(moci)

        ah = round(self.AH(), 2)
        self.complete_value.append(ah)

        utc = self.compute_utci()
        self.complete_value.append(utc)

        pe = self.compute_pet()[0]
        self.complete_value.append(pe)

        self.complete_value.append(self.twb)
        self.complete_value.append(self.t_dew)

        #self.complete_value.append(self.t_globe) # secondo me possiamo non mandarla

        wbgt_value = self.compute_wbgt()
        self.complete_value.append(wbgt_value)

        HIRI_value = self.compute_HIRI()
        self.complete_value.append(HIRI_value)

        t_oper = self.compute_top()
        self.complete_value.append(t_oper)

        kt_d, kt_h_list = self.get_clearness()
        try:
            diff, dni = self.brl_model(self.irr, kt_d, kt_h_list)
            self.complete_value.append(diff)
            self.complete_value.append(dni)
        except:
            print("erore nello split - 1")

        return self.complete_value

        
    def Breakpoints(self):
        if self.C_P <= 54:
            BP_LO = 0
            BP_HI = 54
            I_LO = 0
            I_HI = 50
            category = "Good"
        elif 55 <= self.C_P <= 154:
            BP_LO = 55
            BP_HI = 154
            I_LO = 51
            I_HI = 100
            category = "Moderate"
        elif 155 <= self.C_P <= 254:
            BP_LO = 155
            BP_HI = 254
            I_LO = 101
            I_HI = 150
            category = "Unhealty for sensitive groups"
        elif 255 <= self.C_P <= 354:
            BP_LO = 255
            BP_HI = 354
            I_LO = 151
            I_HI = 200
            category = "Unhealty"
        elif 355 <= self.C_P <= 424:
            BP_LO = 355
            BP_HI = 424
            I_LO = 201
            I_HI = 300
            category = "Very unhealty"
        elif 425 <= self.C_P <= 504:
            BP_LO = 425
            BP_HI = 504
            I_LO = 301
            I_HI = 400
            category = "Hazardous"
        elif 505 <= self.C_P <= 604:
            BP_LO = 505
            BP_HI = 604
            I_LO = 401
            I_HI = 500
            category = "Hazardous"
        else:
            raise ValueError
        return BP_LO, BP_HI, I_LO, I_HI, category


    def T_glob_evaluation(self, t_globe):
        
        globe_emissivity = 0.95
        diameter = 40 # [mm]
        try:
            mrt = (((t_globe + 273.15)**4) + ((1.335*(10**8) * (self.WS)**0.71)/(globe_emissivity * (diameter)**0.4)) * (t_globe - self.T))**0.25 - 273.15
        except:
            mrt = t_globe
        
        # inverse to get t_glob for wbgt
        eg = 0.95
        D = 150
        a = 1
        b = round(4*273.15, 3)
        c = round(6*(273.15)**2, 3)
        d = round(4*(273.15)**3, 3) + round((1.335*(10**8)*(self.WS**0.71))/(eg*(D**0.4)), 3)
        e = round(273.15**4, 3) - (mrt + 273.15)**4 - round((1.335*(10**8)*(self.WS**0.71)*self.T)/(eg*(D**0.4)), 3)

        x = Symbol('x')
        eq = a*x**4 + b*x**3 + c*x**2 + d*x + e
        res = solve(eq, x)

        for ele in res:
            try: 
                float(ele)
            except:
                pass
            else:
                if float(ele) > 0:
                    sol = float(ele)

        t_glob = sol
        

        return mrt, t_glob

    def twb_calculator(self):
        # Normand's rule
        twb = wet_bulb_temperature(self.press* units.hPa, self.T * units.degC, self.t_dew * units.degC)
        twb_value = twb.magnitude
        return twb_value


    def AIQ(self):
        #C_P is the rounded concentration of pollutant p
        #BP_HI is the breakpoint greater than or equal to C_P
        #BP_LO is the breakpoint less than or equal to C_P
        #I_HI = the AQI value corresponding to BP_HI
        #I_LO = the AQI value corresponding to BP_LO
        BP_LO, BP_HI, I_LO, I_HI, category = self.Breakpoints()
        AIQ = int((I_HI - I_LO)/(BP_HI - BP_LO) * (self.C_P - BP_LO) + I_LO)
        return AIQ#, category

    def HUMIDEX(self):
        #T is the air temperature
        #RH is the relative humidity
        H = self.T + (0.5555 * (0.06 * self.RH/100 * 10**(0.03*self.T) - 10))
        if H < 27:
            category = "Comfort"
        elif 27 <= H < 30:
            category = "Cautela"
        elif 30 <= H < 40:
            category = "Estrema cautela"
        elif 40 <= H < 55:
            category = "Pericolo"
        else:
            category = "Estremo pericolo"
        return H#, category

    def MOCI(self, I_cl = 3):
        #WS is the wind speed
        #Rh is the relative humidity
        #T_globe is the globe temperature (MRP)
        #T_a is the air temperature
        #I_cl is the thermal clothing insulation, we picked 3 as default values
        #Compute the T_mr (mean radiant temperature)
        #epsilon = 1 #DA SETTARE
        #D = 3 # DA SETTARE (DIAMETRO?)
        #T_mr = ((self.t_globe + 273.15)**4 + ((1.1*10**8*self.WS**0.6)/(epsilon * D**0.4)) * (self.T_globe-self.T))**0.25 - 275.15
        moci = -4.068 - 0.272*self.WS + 0.05*self.RH + 0.083*self.mrt + 0.058*self.T + 0.264*I_cl
        return moci

    def AH(self):
        ah = (self.RH/100) * 6.112 * np.exp(17.67*self.T/(self.T + 243.5)) * 1000/(461.5*(self.T + 273.15))
        return ah

    def brl_model(self, g0, kt_d, kt_h_list, dt=2):
        """Boland-Ridley-Lauret model for diffuse/direct radiation split from
        global radiation.

        :param g0: [description]
        :type g0: [type]
        :param kt_d: [description]
        :type kt_d: [type]
        :param kt_h_list: [description]
        :type kt_h_list: [type]
        :param t: [description]
        :type t: [type]
        :param lat: [description]
        :type lat: [type]
        :param long: [description]
        :type long: [type]
        :param dt: [description], defaults to 2
        :type dt: int, optional
        :return: [description]
        :rtype: [type]
        """
        # const
        omega0 = 2*math.pi/365.2422
        
        # daytime
        if g0 != 0:
            
            # compute psi - persistence
            # sunrise
            if kt_h_list[-1] == 0 and kt_h_list[-2] != 0 and kt_h_list[-3] != 0 :
                psi = kt_h_list[-3]
            # sunset
            elif kt_h_list[-1] != 0 and kt_h_list[-2] != 0 and kt_h_list[-3] == 0:
                psi = kt_h_list[-1]
            # daytime
            else:
                psi = (kt_h_list[-1]+kt_h_list[-3])/2
            
            date = datetime.datetime.now()
            dy = date.timetuple().tm_yday #t.dayofyear
            y = date.year #t.year 
            h = date.hour #t.hour
            
            n0 = 78.8946+0.2422*(y-1957)-int((y-1957)/4)
            t1 = -0.5-self.long/(2*math.pi)-n0
            omegat = omega0*(dy+t1)
            
            # compute solar angle
            # reference https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time
            b = (360*(dy-81)/365)*math.pi/180 
            eot = 9.87*math.sin(2*b) - 7.53*math.cos(b) -1.5*math.sin(b)  
            time_offset = eot + 4*(self.long*180/math.pi - dt*15)
            st = h + time_offset/60 + 1/2 # solar time: 0.5 added to center at mid hour
            omegas = ((st-12)*15)*math.pi/180 # hourly angle/ solar time in radians
            
            # compute declination 
            delta = 0.0064979+0.405906*math.sin(omegat)+0.0020054*math.sin(2*omegat) -\
                    0.002988*math.sin(3*omegat) - 0.0132296*math.cos(omegat) +\
                    0.0063809*math.cos(2*omegat) + 0.0003508*math.cos(3*omegat)
            
            # compute elevation/solar angle
            hs = math.asin(math.sin(self.lat)*math.sin(delta)+math.cos(self.lat)*math.cos(delta)*math.cos(omegas))
            hs = hs*180/math.pi
            
            # BRL model generic parameters reference http://dx.doi.org/10.1016/j.rser.2013.08.023
            d = 1/(1 + math.exp(-5.38 + 6.63*kt_h_list[-2]+0.006*st-0.007*hs+\
                                    1.75*kt_d+1.31*psi))
            
            # Params specific for Lisbon reference http://dx.doi.org/10.1016/j.rser.2013.08.023
            # d = 1/(1 + math.exp(-5.08 + 6.12*kt_h_list[1]+0.0027*st-0.009*hs+\
            #                           1.40*kt_d+1.51*psi))
            
            # Params for Alps locations reference http://eprints-phd.biblio.unitn.it/1484/1/TESI.pdf
            # d = 1/(1 + math.exp(1.2655 - 6.5092*kt_h_list[1]+0.0849*st-0.0062*hs+\
            #                           2.9967*kt_d+0.6482*psi))
            
            # direct and diffuse split
            g_diff = d*g0
            g_dir = (g0-g_diff) / math.sin(hs*math.pi/180)
            # avoid strange values due to high kt at low elevation angles (no reference)
            g_dir=min(1366, g_dir)
            
            if g_dir < 0:
                g_dir = 0
        
        # nighttime
        else:
            g_dir = 0
            g_diff = 0 
            
        return g_diff, g_dir
    
        #
    def t_dew_point(self):
        """Compute dew point temperature according to Meteonorm formula.

        :param t_db: Dry bulb temperature in °C
        :type t_db: float
        :param rh: Relative humidity
        :type rh: float
        :return: Dew point temperature in °C
        :rtype: float
        """
        # needed params are T dry bulb in celsius and Relative Humidity in %
        if self.RH != 0:
            t_dp = pow((1/(self.T+273.15)-(1.85*pow(10,-4))*math.log(self.RH/100)),-1) - 273.15
        else:
            t_dp = float("nan")
        return t_dp

    """
    - UTCI
    - PET - ET
    - WBGT outdoor
    - grafico psicometrico
    """

    def compute_utci(self):

        # ----- UTCI ------
        # Ha bisogno di: - tdb: dry bulb air temperature in *C
        #                - tr: mean radiant temperature
        #                - v: wind speed
        #                - rh: relative humidity
        utci_value = utci(tdb= self.T, tr=self.mrt, v= self.WS, rh=self.RH)
        return utci_value

    def compute_pet(self):
        # ----- PET ------
        # Ha bisogno di: - temperature_celsius
        #                - latitude_degrees
        #                - data_start_year
        # possiamo dargli un vettore di temp e la data della prima temperatura e lui ci da un vettore di pet (x ogni temperatura)
        tem = []
        tem.append(self.T)
        tem = np.array(tem)

        date = datetime.datetime.now()   
        y = date.year #t.year

        pet_value = pet(temperature_celsius=tem, latitude_degrees=self.lat, data_start_year=y)
        return pet_value

    def compute_wbgt(self):
        # ----- WBGT -----
        # Ha bisogno di: - twb: natural wet bulb temperature in *C
        #                - tg: globe temperature in *C
        #                - tdb: dry bulb air temperature in *C
        #                - with_solar_load: True if the globe sensor is exposed to direct solar radiation
        wbgt_value = wbgt(twb=self.twb, tg= self.t_globe, tdb=self.T, with_solar_load= True)
        return wbgt_value
    
    def get_clearness(self):
        TOKEN = 'Gczy5kItGBG5cjWaDqM8-8OnbEE4jW_hJ3f3x0yGdPjQgxzBYFw34c5l9IWYeF_P_AQQBlJq_u5K7UEXM7DfPg=='
        ORG = 'Polito'
        BUCKET = 'Prova2'
        URL = 'https://olgyay.polito.it:8090'  # l'URL di connessione al tuo database InfluxDB
        client = InfluxDBClient(url=URL, token=TOKEN, org=ORG, verify_ssl=False)

        now = datetime.datetime.now()
        now = now - datetime.timedelta(hours=72) # get last 3 days to avoid nan and night
        time = str(now.year) +"-"+ str(now.month).zfill(2) + "-" + str(now.day).zfill(2) + " " + str(now.hour).zfill(2) + ":" + str(now.minute).zfill(2) + ":" + str(now.second).zfill(2)
        formato_data = "%Y-%m-%d %H:%M:%S"
        data_ora = datetime.datetime.strptime(time, formato_data)
        query_api = client.query_api()

        p = {
        "_bucket": BUCKET,
        "_start" : data_ora,
        "_measurement": "Oudoor_data",
        "_field": "Clearness" # FAR RIPARTIRE IL SERVER
        }
        q = '''
        from(bucket: "Prova2")
            |> range(start: _start)
            |> filter(fn: (r) => r["_measurement"] == "Oudoor_data")
            |> filter(fn: (r) => r._field == _field)
            |> aggregateWindow(every: 1h, fn: mean)
        '''

        kt_h_list = np.ones(24)

        tables = query_api.query(query=q, params=p)
        for table in tables:
            for row in table.records:
                point_data=row.values
                irr = point_data["_value"]
                #print(row.values)
                if isinstance(irr, float) or isinstance(irr, int):
                    if 0 <= irr <= 1:
                        kt_h_list = np.roll(kt_h_list, -1)
                        kt_h_list[-1] = irr

        kt_d = np.mean(kt_h_list)

        return kt_d, kt_h_list
    
    def compute_HIRI(self):

        TOKEN = 'Gczy5kItGBG5cjWaDqM8-8OnbEE4jW_hJ3f3x0yGdPjQgxzBYFw34c5l9IWYeF_P_AQQBlJq_u5K7UEXM7DfPg=='
        ORG = 'Polito'
        BUCKET = 'Prova2'
        URL = 'https://olgyay.polito.it:8090'  # l'URL di connessione al tuo database InfluxDB


        client = InfluxDBClient(url=URL, token=TOKEN, org=ORG, verify_ssl=False)


        now = datetime.datetime.now()
        now = now - datetime.timedelta(minutes=10)
        time = str(now.year) +"-"+ str(now.month).zfill(2) + "-" + str(now.day).zfill(2) + " " + str(now.hour).zfill(2) + ":" + str(now.minute).zfill(2) + ":" + str(now.second).zfill(2)
        formato_data = "%Y-%m-%d %H:%M:%S"
        data_ora = datetime.datetime.strptime(time, formato_data)
        query_api = client.query_api()

        p = {
            "_bucket": BUCKET,
            "_start" : data_ora,
            "_measurement": "Oudoor_data",
            "_field": "Cloudiness"
            }
        q = '''
        from(bucket: "Prova2")
            |> range(start: _start)
            |> filter(fn: (r) => r["_measurement"] == "Oudoor_data")
            |> filter(fn: (r) => r._field == _field)
        '''

        import math

        tables = query_api.query(query=q, params=p)
        table = tables[0]
        row = table.records
        point_data = row[-1].values
        cloud = point_data["_value"]
        N = cloud*10 #cloudiness in tenths
        sigma_Boltzmann = 5.6697*(10**(-8))
        emissivity = (0.787 + 0.764*math.log(self.t_dew/273))*(1 + 0.224*N - 0.0035*(N**2) + 0.00028*(N**3))

        HIRI = emissivity*sigma_Boltzmann*(self.T**4)
        return(HIRI)
    
    def compute_top(self):

        t_op = (self.T*(math.sqrt(10*self.WS)) + self.mrt)/(1 + math.sqrt(10*self.WS))

        return t_op


