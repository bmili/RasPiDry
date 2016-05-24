#!/usr/bin/python

import Adafruit_DHT
import sys

class Temp2Wire:
    numSensor = 0
    def __init__(self,sensor,pin):
        #self.tempSensorId = tempSensorId
        self.sensorNum = Temp2Wire.numSensor
        #Temp2Wire.numSensor += 1
        #self.pin = Temp2Wire.pin
        self.sensorNum = sensor
        self.DHT_PIN  =  pin
        Temp2Wire.numSensor += 1

        sensor_args = { 11: Adafruit_DHT.DHT11, 22: Adafruit_DHT.DHT22,2302: Adafruit_DHT.AM2302 }
        if sensor not in sensor_args:
          print "sensor",sensor
          print 'usage:  Temp2Wire( [11|22|2302] GPIOpin#)'
       #   print 'example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO #4'
          sys.exit(1)

        self.DHT_TYPE = sensor_args[sensor]

    def f(self,conn):
      conn.send( Adafruit_DHT.read_retry(self.DHT_TYPE,self.DHT_PIN))
      #conn.send([42, None, 'hello'])
      conn.close()

    def readTempC(self):   
      humidity, temperature=Adafruit_DHT.read_retry(self.DHT_TYPE,self.DHT_PIN)
      if (temperature == None):
         temperature = -99 #bad temp reading    
      return temperature,humidity

if __name__ == '__main__':
  x= Temp2Wire(22,4)
  y=x.readTempC()
  print y


