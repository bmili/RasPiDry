#!/usr/bin/env python

import threading, ssl

from multiprocessing import Process, Pipe, Queue, current_process, Lock

import paho.mqtt.client as mqtt
import time,sys
global mqttc

class iot_mqtt_publisher2:

    #def __init__(self,thing,cert,tempin,tempout,curState,setPoint,humidity,weight, dtime):
    def __init__(self,thing,cert):

        self.cert     = cert
        self.thing    = thing
        self.mqttc = mqtt.Client(client_id="RPI-id")
        self.mqttc.on_publish =  self.onpublish
        self.mqttc.on_connect =  self.onconnect
        self.mqttc.on_message =  self.onmessage
 #       self.mqttc.on_subscribe =  self.on_subscribe

        #adding client-side certificates and enabling tlsv1.2 support as required by aws-iot service
        self.mqttc.tls_set("/home/pi/certificate/root-CA.crt",
                  certfile="/home/pi/certificate/"+cert+"certificate.pem",
                  keyfile="/home/pi/certificate/"+cert+"private.pem",
                  tls_version=ssl.PROTOCOL_SSLv23,
                  ciphers=None)
  #      self.mqttc.connect("A9HHD5G1IXZ9I.iot.eu-west-1.amazonaws.com", port=8883) #AWS IoT service hostname and portno
  #      self.mqttc.loop_forever() 
  #      self.mqttc.loop_start()

	#called while client tries to establish connection with the server
    def onconnect(self,mqttc, obj, flags, rc):
            if rc==0:
                print ("Publisher Connection status code: "+str(rc)+" | Connection status: successful "+self.thing)
            elif rc==1:
                print ("Publisher Connection status code: "+str(rc)+" | Connection status: Connection refused "+self.thing)
  #          mqttc.subscribe('$aws/things/FoodDehydratorTemperatureControl/shadow/update/rejected', qos=1)
#            mqttc.subscribe('$aws/things/FoodDehydratorTemperatureStatus/shadow/update/accepted', qos=1)


    def onpublish(self,mqttc, userdata, mid):
            print("on_publish mid: "+str(mid)+" "+self.thing)

    def onmessage(self,mqttc, obj, msg):
        global message
        print("on_message topis "+msg.topic + " " + str(msg.qos) + " message " + str(msg.payload))
        message = msg.payload


#    def on_subscribe(self,mosq, obj, mid, granted_qos):
#        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def send(self,tempin,tempout,curState,setPoint,humidity,weight, dtime):
       self.tempout = tempout
       self.tempin = tempin
       self.humidity = humidity
       self.weight = weight
       self.curState    = curState
       self.dtime    = dtime
       self.mqttc.connect("A9HHD5G1IXZ9I.iot.eu-west-1.amazonaws.com", port=8883) #AWS IoT service hostname and portno
       print ("iot_mqtt_publisher2:send ",self.thing,tempin,tempout,curState,setPoint,humidity,weight, dtime)
       self.mqttc.loop_start() #start loop
       if self.thing.find("Status") != -1: # == 'FoodDehydratorTemperatureStatus': 
         #print('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"intTemp\":"+str(tempin) +" }  } }")
         #print ('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"extTemp\":"+str(tempout)+" }  } }")
         #print('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"curState\":"+str(curState)   +" } } }")
         #print ('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"weight\":"+str(weight)  +" } } }")
         #print ('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"fromstart\":"+str(dtime)+" } } }")

         (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"intTemp\":"+str(tempin) +" }}}", qos=1)
         (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"extTemp\":"+str(tempout)+" }}}", qos=1)
         (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"curState\":"+(curState)+" }}}", qos=1)
         (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"weight\":"+str(weight)  +" }}}", qos=1)
         (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"fromstart\":"+str(dtime)+" }}}", qos=1)
       else:
         (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"setPoint\":"+str(setPoint)+" }}}", qos=1)
         (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"enabled\":" +str(curState)+" }}}", qos=1)
         (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"end\":"+str(dtime)+      " }}}", qos=1)        
       self.mqttc.loop_stop()  #stop loop
       self.mqttc.disconnect()

#http://robomq.readthedocs.org/en/latest/MQTT/
    def send_p(self,sleep, conn):
        #connecting to aws-account-specific-iot-endpoint
        self.mqttc.connect("A9HHD5G1IXZ9I.iot.eu-west-1.amazonaws.com", port=8883) #AWS IoT service hostname and portno
        print ("iot_mqtt_publisher2:send_p ",self.thing)
        self.mqttc.loop_start() #start loop
        while (conn.poll()): #get last
            tempin,tempout,curState,setPoint,humidity,weight, dtime = conn.recv()
            print ("send_p ",tempin,tempout,curState,setPoint,humidity,weight, dtime)

            self.mqttc.loop_start() #start loop
            if self.thing.find("Status") != -1: # == 'FoodDehydratorTemperatureStatus': 
              print ('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"intTemp\":"  +str(tempin) +" } } }")
              print ('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"extTemp\":"  +str(tempout)+" } } }")
              print ('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"curState\":" +curState   +" } } }")
              print ('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"weight\":"   +str(weight)  +" } } }")
              print ('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"fromstart\":"+str(dtime)+" } } }")

              (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"intTemp\":" +str(tempin)  +"}}}",qos=1)
              (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"extTemp\":" +str(tempout) +"}}}", qos=1)
              (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"curState\":"+curState     +"}}}", qos=1)
              (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"weight\":"  +str(weight)  +"}}}", qos=1)
              (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"fromstart\":"+str(dtime)  +"}}}", qos=1)
            else:
             print ('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"setPoint\":"+str(setPoint) +" } } }")
             print ('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"enabled\":"+str(curState)  +" } } }")
             print ('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"end\":"    +str(dtime)     +" } } }")

             (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"setPoint\":"+str(setPoint)+" }}}", qos=1)
             (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"enabled\":" +str(curState)+" }}}", qos=1)
             (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"end\":"+str(dtime)+      " }}}", qos=1)        
            time.sleep(sleep)
        self.mqttc.loop_stop()  #stop loop
        self.mqttc.disconnect()


    def send_p1(self,sleep, conn):
           while (conn.poll()): #get last
            tempin,tempout,curState,setPoint,humidity,weight, dtime = conn.recv()
            print ("send_p1 ",self.thing, tempin,tempout,curState,setPoint,humidity,weight, dtime)
            if self.thing.find("Status") != -1: # == 'FoodDehydratorTemperatureStatus': 
              (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"intTemp\":"+str(tempin)    +"}}}",qos=1)
              (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"extTemp\":"+str(tempout)   +"}}}",qos=1)
              (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"curState\":"+str(curState) +"}}}",qos=1)
              (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"weight\":"+str(weight)     +"}}}",qos=1)
              (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"fromstart\":"+str(dtime)   +"}}}",qos=1)
            else:
             (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"setPoint\":"+str(setPoint)+" }}}", qos=1)
             (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"enabled\":" +str(curState)+" }}}", qos=1)
             (rc, mid) = self.mqttc.publish('$aws/things/'+self.thing+'/shadow/update' , "{ \"state\": {\"desired\": {\"end\":"+str(dtime)+      " }}}", qos=1)         
           time.sleep(10)
 


if __name__ == '__main__':
   import datetime
   import time

   try:
        TIME=datetime.datetime.now()
        #IOT setup
        cert='f03f954dd6-' 
        thing= "FoodDehydratorTemperatureControl"  
        print("iot_mqtt_publisher",thing)
        sleep=10
        iotstat= iot_mqtt_publisher2( thing,cert)
        parent_conn, child_conn = Pipe() 
#        p = Process(target=iotstat1.send_p1, args=(sleep,child_conn, ))
        p = Process(target=iotstat.send_p, args=(sleep,child_conn, ))
        p.daemon = True
        p.start()
        set_point=34
        mode= '"True"'
        dtime= 601
        parent_conn.send([None,None,mode,set_point,None,None,dtime])
        time.sleep(20)

        set_point=32.5
        mode= '"False"'
        dtime= 602
        parent_conn.send([None,None,mode,set_point,None,None,dtime])
        time.sleep(10)

        thing= "FoodDehydratorTemperatureStatus"  
        #for thing in ThingList:
        # if "Status" in thing: 
        print("iot_mqtt_publisher",thing)
#        sleep=10
        iotstat= iot_mqtt_publisher2( thing,cert)
        parent_conn, child_conn = Pipe() 
        p = Process(target=iotstat.send_p, args=(sleep,child_conn, ))
        p.daemon = True
        p.start()
        print "1"
        tempin=33.6
        tempout=22
        humidity=27.55
        weight=26.5   
        mode= '"heating"' 
        set_point=34
        dtime=datetime.datetime.now()-TIME
        dtime=round((dtime.total_seconds() / 60.0),2)
        print "tempin {},tempout {},mode {},set_point {},humidity {},weight {},dtime {}".format( tempin,tempout,mode,set_point,humidity,weight,dtime)
        parent_conn.send([tempin,tempout,mode,set_point,humidity,weight,dtime])
        time.sleep(10)
        print "2"
        tempin=36.6
        tempout=32
        humidity=22.55
        weight=21.5  
        dtime=datetime.datetime.now()-TIME
        dtime=round((dtime.total_seconds() / 60.0),2)
        print "tempin {},tempout {},mode \"{}\",set_point {},humidity {},weight {},dtime {}".format( tempin,tempout,mode,set_point,humidity,weight,dtime)
        parent_conn.send([tempin,tempout,mode,set_point,humidity,weight,dtime])
        time.sleep(20)
   except Exception, e:
      print (str(e))
   sys.exit()
"""

        time.sleep(10)
        tempin=44.6
        tempout=42
        humidity=12.55
        weight=11.5  
        dtime=datetime.datetime.now()-TIME
        dtime=round((dtime.total_seconds() / 60.0),2)
        print ( tempin,tempout,mode,set_point,humidity,weight,dtime)
        parent_conn.send([tempin,tempout,mode,set_point,humidity,weight,dtime])
        time.sleep(10)
        #p.join()
        p.terminate()
   except Exception, e:
      print (str(e))
   sys.exit()

   TIME=datetime.datetime.now()
   topic='$aws/things/BBQ/shadow/update'
   tempin=33.6
   tempout=22
   humidity=27.55
   weight=26.5   
   my_curState=["heating" ,"cooling","stopped"]
   setPoint=43
   cert='f03f954dd6-'
   thing='FoodDehydratorTemperatureStatus'
   thing='FoodDehydratorTemperatureControl'
   my_array = ['FoodDehydratorTemperatureControl','FoodDehydratorTemperatureStatus']

   for i in range(0, 13):
      if i>0:
       thing =my_array [1]
      else:
       thing =my_array [0]

      x= iot_mqtt_publisher2( thing,cert)
      tempin=tempin+i
      tempout=tempout+i
      weight=weight-i
      humidity=humidity-i
      curState=my_curState[0]
      if thing == 'FoodDehydratorTemperatureStatus':
        time.sleep(10)
        dtime=datetime.datetime.now()-TIME
        print(dtime.total_seconds() / 60.0)
        dtime=round((dtime.total_seconds() / 60.0),2)
      else:
        curState="true"#false" #true"
        dtime=800.0

      print thing ,tempin,tempout,curState,setPoint,humidity,weight,dtime

      x.send(tempin,tempout,curState,setPoint,humidity,weight,dtime)
      print x.curState
      print x.weight
      print x.tempin
      print x.tempout
      print x.dtime
      if tempin > 42:
        curState=my_curState[2]
  # x= iot_mqtt_publisher1( thing,cert)
        x.send(tempin,tempout,curState,setPoint,humidity,weight,dtime)
        print x.curState
        print x.weight
        print x.tempin
        print x.tempout
        print x.dtime

        curState="false" #true"
        thing =my_array [0]
 #  x= iot_mqtt_publisher1( thing,cert)
        x.send(tempin,tempout,curState,setPoint,humidity,weight,dtime)  
        print x.curState
        print x.weight
        print x.tempin
        print x.tempout
        print x.dtime
        break
"""
