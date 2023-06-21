// ---- includes ----
// -- generic --
#include <TimeLib.h>
#include <SoftwareSerial.h>

// -- max6675 --
#include "max6675.h" 
int SO = 12;
int CS = 9;
int sck = 8;
MAX6675 module(sck, CS, SO);

// -- REVC4 --
//#define analogPinForRV    1   // change to pins you the analog pins are using
//#define analogPinForTMP   0
//const float zeroWindAdjustment =  .2; 

//int TMP_Therm_ADunits;
//float RV_Wind_ADunits; 
//float RV_Wind_Volts;
//unsigned long lastMillis;
//int TempCtimes100;
//float zeroWind_ADunits;
//float zeroWind_volts;
//float WindSpeed_MPH;

// -- wind direction --
#define RXdir        10   //Serial Receive pin
#define TXdir        11    //Serial Transmit pin
#define RTS_pin1dir    2    //RS485 Direction control
#define RTS_pin2dir    3   //RS485 Direction control
#define RS485Transmit_dir    HIGH
#define RS485Receive_dir     LOW
SoftwareSerial RS485Serialdir(RXdir, TXdir);

// -- wind speed -- 
// WS_pin  A0; //wind speed read on analog A0

// SHARP GPY10 --
int measurePin = A5;
int ledPower = 7;
unsigned int samplingTime = 280;
unsigned int deltaTime = 40;
unsigned int sleepTime = 9680;
float voMeasured = 0;
float calcVoltage = 0;
float dustDensity = 0;

// bme 680

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME680 bme;


void setup() {   
  Serial.begin(57600);
  //dust sensor
  pinMode(ledPower,OUTPUT);

  if (!bme.begin()) {
    Serial.println(F("Could not find a valid BME680 sensor, check wiring!"));
    while (1);
  }

  // wind direction
  pinMode(RTS_pin1dir, OUTPUT);
  pinMode(RTS_pin2dir, OUTPUT);
  RS485Serialdir.begin(9600);
  RS485Serialdir.flush();  

  // bme 680
  // Set up oversampling and filter initialization
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320*C for 150 ms
  
  
  delay(5000);
}

void loop(){
  // ---- READ ----
  // -- MAX6675
  float temperature = module.readCelsius();
  // -- REVC4
  //TMP_Therm_ADunits = analogRead(analogPinForTMP);
  //RV_Wind_ADunits = analogRead(analogPinForRV);
  //RV_Wind_Volts = (RV_Wind_ADunits *  0.0048828125);
  //TempCtimes100 = (0.005 *((float)TMP_Therm_ADunits * (float)TMP_Therm_ADunits)) - (16.862 * (float)TMP_Therm_ADunits) + 9075.4;  
  //zeroWind_ADunits = -0.0006*((float)TMP_Therm_ADunits * (float)TMP_Therm_ADunits) + 1.0727 * (float)TMP_Therm_ADunits + 47.172;  //  13.0C  553  482.39
  //zeroWind_volts = (zeroWind_ADunits * 0.0048828125) - zeroWindAdjustment;    
  //WindSpeed_MPH =  pow(((RV_Wind_Volts - zeroWind_volts) /.2300) , 2.7265);
  // -- Wind Direction --
  float wind_direction = -1.0;
  digitalWrite(RTS_pin1dir, RS485Transmit_dir);     // init Transmit
  digitalWrite(RTS_pin2dir, RS485Transmit_dir);     // init Transmit
  byte Anemometer_request[] = {0x01, 0x03, 0x00, 0x17, 0x00, 0x01, 0x34, 0x0E};
  RS485Serialdir.write(Anemometer_request, sizeof(Anemometer_request));
  RS485Serialdir.flush();
  digitalWrite(RTS_pin1dir, RS485Receive_dir);      // Init Receive
  digitalWrite(RTS_pin2dir, RS485Receive_dir);      // Init Receive
  byte Anemometer_buf[8];
  RS485Serialdir.readBytes(Anemometer_buf, 8);
  switch(Anemometer_buf[4] & 0xFF){
    case 0x000F:
      wind_direction = 0.0;
      break;
    case 0x0000:
      wind_direction = 22.5;
      break;
    case 0x0001:
      wind_direction = 45;
      break;
    case 0x0002:
      wind_direction = 67.5;
      break;
    case 0x0003:
      wind_direction = 90.0;
      break;
    case 0x0004:
      wind_direction = 112.5;
      break;
    case 0x0005:
      wind_direction = 135.0;
      break;
    case 0x0006:
      wind_direction = 157.5;
      break;
    case 0x0007:
      wind_direction = 180.0;
      break;
    case 0x0008:
      wind_direction = 202.5;
      break;
    case 0x0009:
      wind_direction = 225.0;
      break;
    case 0x000A:
      wind_direction = 247.5;
      break;
    case 0x000B:
      wind_direction = 270.0;
      break;
    case 0x000C:
      wind_direction = 292.5;
      break;
    case 0x000D:
      wind_direction = 315.0;
      break;
    case 0x000E:
      wind_direction = 337.5;
      break;
    }
  // -- SHARP --
  digitalWrite(ledPower,LOW);
  delayMicroseconds(samplingTime);
  voMeasured = analogRead(measurePin);
  delayMicroseconds(deltaTime);
  digitalWrite(ledPower,HIGH);
  delayMicroseconds(sleepTime);
  calcVoltage = voMeasured*(5.0/1024);
  dustDensity = 170*calcVoltage-0.1;
  if ( dustDensity < 0)
  {
    dustDensity = 0.00;
  }
  // -- SEN0170 --
  int sensorValue = analogRead(A1);
  float outvolt = sensorValue * (5.0 / 1023.0);
  //Serial.println(outvolt);
  //int wind_speed = int(-5.3 + 7.06*outvolt);//The level of wind speed is proportional to the output voltage.
  int wind_speed = 6*outvolt;
  //if (wind_speed < 0){
    //wind_speed = 0.0;
  //}

  // -- bme680 --
  unsigned long endTime = bme.beginReading();
  if (!bme.endReading()) {
    Serial.println(F("Failed to complete reading :("));
    return;
  }
  float pressure = bme.pressure / 100.0;
  
  
  // ---- print on serial ----
  // -- MAX6675
  Serial.print(", Temperature_MAX :");
  Serial.print(temperature);
  // -- REVC4
  //Serial.print("\t  Temp_REVC4 ");
  //Serial.print(TempCtimes100 );

  //Serial.print(", WindSpeed_REVC4:");
  //Serial.print(WindSpeed_MPH);
  //Serial.println();
  // -- Wind Direction
  Serial.print(", Wind Direction :");
  Serial.print(wind_direction);
  // -- Wind Speed
  Serial.print(", Wind Speed :");
  Serial.print(wind_speed);
  //Serial.print(outvolt);
  // -- SHARP GPY10
  Serial.print(", Dust Density :");
  Serial.print(dustDensity);
  //Serial.print(calcVoltage);
  // -- bme680 --
  Serial.print(", Pressure :");
  Serial.print(pressure);
  
  
  // wait 2 min for next read
  delay(1000); 
  }
