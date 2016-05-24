#!/usr/bin/python3

#required libraries
from multiprocessing import Process, Queue
import sys                               
import ssl
import paho.mqtt.client as mqtt
import json
import yaml 
message = 'ON'
global queueSub

class iot_mqtt_subscriber2:
   global message

   def __init__(self,thing,cert,queue):
    self.cert     = cert
    self.thing    = thing
    self.queue    = queue
    self.mqttc = mqtt.Client(client_id="RPI-id")
# Assign event callbacks
    self.mqttc.on_message = self.on_message
    self.mqttc.on_connect = self.on_connect
    self.mqttc.on_subscribe = self.on_subscribe
#Configure network encryption and authentication options. Enables SSL/TLS support.
#adding client-side certificates and enabling tlsv1.2 support as required by aws-iot service
    self.mqttc.tls_set("/home/pi/certificate/root-CA.crt",
		certfile="/home/pi/certificate/bfe9fd14ce-certificate.pem",
		keyfile="/home/pi/certificate/bfe9fd14ce-private.pem",
                tls_version=ssl.PROTOCOL_SSLv23,
                ciphers=None)

#conecting to aws-account-specific-iot-endpoint
    self.mqttc.connect("A9HHD5G1IXZ9I.iot.eu-west-1.amazonaws.com", port=8883) #AWS IoT service hostname and portno

# Continue the network loop
    #self.mqttc.loop_forever()
    self.mqttc.loop_start()


   def on_connect(self,mqttc, obj, flags, result):
#   def on_connect(self, userdata, flags_dict, result):#self,mosq, obj, rc):
  #  mqttc.subscribe("f", 0)
    if result==0:
	print ("Publisher Connection status code: "+str(result)+" | Connection status: successful")
    elif result==1:
	print ("Publisher Connection status code: "+str(result)+" | Connection status: Connection refused")


    mqttc.subscribe('$aws/things/FoodDehydratorTemperatureControl/shadow/update/accepted', qos=1)


   def on_message(self,mqttc, obj, msg):
    global message
    print(msg.topic + " " + str(msg.qos))# + " " + str(msg.payload))
    message = msg.payload
    m=yaml.safe_load(message)["state"]["desired"]
    list=[]
    list=m.iteritems()
    print 'on_message list',''.join('{}:{},'.format(key, val) for key, val in sorted(m.items()))
    for key, value in m.iteritems():
      if key == 'enabled' and value==False: #'False':
         print "on_message  ",key, value
   #      self.queue.put("")
         self.queue.put("False")             # Write 'state' into the queue
         self.queue.put("False")             # Write 'state' into the queue
         self.queue.put("False")             # Write 'state' into the queue
         self.queue.put('DONE')
         self.queue.put("False")             # Write 'state' into the queue
         self.queue.put("False")             # Write 'state' into the queue
         self.queue.put("False")             # Write 'state' into the queue
         self.queue.put('DONE')
      if key == 'enabled' and value==True: #'False':
         print "on_message  ",key, value
 #        self.queue.put("")
         self.queue.put("True")             # Write 'state' into the queue
         self.queue.put("True")             # Write 'state' into the queue
         self.queue.put("True")             # Write 'state' into the queue
         self.queue.put('DONE')
         self.queue.put("True")             # Write 'state' into the queue
         self.queue.put("True")             # Write 'state' into the queue
         self.queue.put("True")             # Write 'state' into the queue
         self.queue.put('DONE')

      if key == 'enabled' and value=='stopped': 
         print "on_message ",key, value
 #        self.queue.put("")
         self.queue.put("stopped")             # Write 'state' into the queue
         self.queue.put("stopped")             # Write 'state' into the queue
         self.queue.put("stopped")             # Write 'state' into the queue
         self.queue.put("stopped")             # Write 'state' into the queue
         self.queue.put('DONE')

   def on_subscribe(self,mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

   def on_log(self,mosq, obj, level, string):
    print(string)

   def on_loop(self, queueSub):
      pass
   #   while True:
   #     msg = queueSub.get()         # Read from the queue and do nothing
   #     print"on_loop", msg
   #     if (msg == 'DONE'):
   #         break



if __name__ == '__main__':
        from multiprocessing import Process, Pipe
        cert='f03f954dd6-' 
        thing= "FoodDehydratorTemperatureControl"  
        print("iot_mqtt_subscriber2",thing)

        queueSub = Queue()   # reader() reads from queue
                          # writer() writes to queue

        iotstat= iot_mqtt_subscriber2( thing,cert,queueSub)
        p = Process(target=iotstat.on_loop, args=((queueSub),))
        p.daemon = True
        p.start()
        print "queue ",queueSub.get() 
 #       p.join()
        print("iot_mqtt_subscriber5",thing)
        while 1:
          msg = queueSub.get()         # Read from the queue and do nothing
          print"main", msg
          if (msg == 'DONE'):
            break
        print"main", msg

        print("iot_mqtt_subscriber6",thing)
