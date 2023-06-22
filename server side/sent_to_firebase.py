import firebase_admin
import influxdb_client
import datetime
from firebase_admin import credentials
from firebase_admin import db
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
import pytz

TOKEN = 'your-token'
ORG = 'Polito'
BUCKET = 'Prova2'
URL = 'https://olgyay.polito.it:8090'  # l'URL di connessione al tuo database InfluxDB

class Firebase():
  def __init__(self):

    # Imposta le credenziali di Firebase
    if not firebase_admin._apps:
      cred = credentials.Certificate("credentials.json")
      firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://prova-app-weather-station-default-rtdb.europe-west1.firebasedatabase.app/'
      })

    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG, verify_ssl=False)

    
    timezone = pytz.timezone('Europe/Rome')
    now = datetime.datetime.now()
    now = now - datetime.timedelta(hours=1) # prendiamo dati dai 1 h prima in poi

    
    time = str(now.year) +"-"+ str(now.month).zfill(2) + "-" + str(now.day).zfill(2) + " " + str(now.hour).zfill(2) + ":" + str(now.minute).zfill(2) + ":" + str(now.second).zfill(2)
    # Formato della stringa
    formato_data = "%Y-%m-%d %H:%M:%S"
    # Trasformare la stringa in oggetto datetime
    data_ora = datetime.datetime.strptime(time, formato_data)

    print("Invio a Firebase...")
    print("ora:", data_ora)
    print(f"RANGE TIME FOR FIREBASE: {datetime.datetime.now() - now}")

    
    query_api = client.query_api()
    p = {
        "_bucket": BUCKET,
        "_start" : data_ora,
        "_measurement": "Oudoor_data"
    }
    q = '''
    from(bucket: "Prova2")
      |> range(start: _start)
      |> filter(fn: (r) => r["_measurement"] == "Oudoor_data")
      |> group(columns: ["_time"], mode:"by")
    '''

    tables = query_api.query(query=q, params=p)
    
    """

    tables = query_api.query(f'from(bucket: "{BUCKET}") |> range(start: 2020-06-04T18:45:20Z)\
                            |> filter(fn: (r) => r["_measurement"] == "Indoor_data") ' ) 
    
    """
    print("Data sent to Firebase succesfully")
    firebase_ref = db.reference('measurement')
    table = tables[-1] # take last measurements

    for row in table.records:
      point_data=row.values
      for key, value in point_data.items():
        if isinstance(value, datetime.datetime):
            point_data[key] = value.strftime('%Y-%m-%d %H:%M:%S')

      firebase_ref.push(point_data)
