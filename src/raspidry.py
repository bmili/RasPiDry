#!/usr/bin/python

#Copyright (c) 2015 Boris Milikic
#Portions copyright(c) 2012 Stephen P. Smith
#
# Permission is hereby granted, free of charge, to any person obtaining 
# a copy of this software and associated documentation files 
# (the "Software"), to deal in the Software without restriction, 
# including without limitation the rights to use, copy, modify, 
# merge, publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:

# The software is free for non-commercial uses.  Commercial uses of this software 
# or any derivative must obtain a license from Dataworlds LLC (Austin TX)

# In addition, the above copyright notice and this permission notice shall 
# be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR 
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



from multiprocessing import Process, Pipe, Queue,  current_process, Lock
from Queue import Empty, Full
from subprocess import Popen, PIPE, call
from datetime import datetime

import time, random, serial, os
from smbus import SMBus
import RPi.GPIO as GPIO
from pid import pidpy as PIDController
import xml.etree.ElementTree as ET

#from flask import Flask, render_template, request, jsonify

import Display
import time,datetime
import sys,signal
#import psutil

from s3Upload3 import s3Upload
from iot_mqtt_publisher2 import iot_mqtt_publisher2
from iot_mqtt_subscriber2 import iot_mqtt_subscriber2
import Temp2Wire


import logging
import logging.handlers
import argparse


global  queueSub,  statusQ ,statusQ_B ,statusQ_C ,pinHeatList,  dry_time,   parent_connB,parent_connC, parent_conn  #parent_connIOT,
global xml_root, template_name,  cert,thing,runtime, filename, sleep, iottime, pinHeatList, pinGPIOList, pinTempGPIOList,DEBUG, lck, pinFanList

# Deafults
LOG_FILENAME = "/tmp/raspidry.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"
LOG_LEVEL= logging.DEBUG
app = Flask(__name__, template_folder='templates')
#url_for('static', filename='raspidry.css')


# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

#'MyLogger' object has no attribute 'flush'
        def flush(self):
             pass

	 #Parameters that are used in the temperature control process
class param:
   status = {
        "numTempSensors" : 2,
        "temp" : "0",
        "tempUnits" : "C",
        "elapsed" : "0",
        "mode" : "off",
        "dry_time" : 600, #min
        "cycle_time" : 2.0, #cikel 2 sek
        "duty_cycle" : 50.0, # dejanska moc cycle
        "duty_cycle_temp" : 0, # temp moc cycle
        "dry_time" : 60, # min
        "dry_duty_cycle" : 60, # %
        "set_point" : 0.0, # temp
        "dry_manage_temp" : 36, #temp
        "num_pnts_smooth" : 5,
        "k_param" : 44,
        "i_param" : 165,
        "d_param" : 4,             
        "option" : 6             
    } 

   @staticmethod
   def unPackParamInitAndPost(paramStatus):
    #paramStatus=self.status
    #temp = paramStatus["temp"]
    #tempUnits = paramStatus["tempUnits"]
    #elapsed = paramStatus["elapsed"]
    mode = paramStatus["mode"]
    cycle_time = paramStatus["cycle_time"]
    duty_cycle = paramStatus["duty_cycle"]
    dry_duty_cycle = paramStatus["dry_duty_cycle"]
    set_point = paramStatus["set_point"]
    dry_manage_temp = paramStatus["dry_manage_temp"]
    num_pnts_smooth = paramStatus["num_pnts_smooth"]
    k_param = paramStatus["k_param"]
    i_param = paramStatus["i_param"]
    d_param = paramStatus["d_param"]
    option  = paramStatus["option"]
    return mode, cycle_time, duty_cycle, dry_duty_cycle, set_point, dry_manage_temp, num_pnts_smooth, \
    k_param, i_param, d_param, option

"""

items={"options":[
            {"name":"herbs","id":1, "ends":333},            
            {"name":"Raising Bread","id":2, "ends":633}, 
            {"name":"Making Yougurt","id":3, "ends":533}, 
            {"name":"Vegetable","id":4, "ends":4333}, 
            {"name":"Fruit leather","id":5, "ends":3333}, 
            {"name":"Fruit","id":6, "ends":4333}]};
var options=[333,633,533,4333,3333,4333]
var setpoint=[35,26,43,40,42,48]
"""

# main web page    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        #render main page
        return render_template(template_name, mode = param.status["mode"], set_point = param.status["set_point"], \
                               k_param = param.status["k_param"],d_param = param.status["d_param"], i_param = param.status["i_param"],\
                               duty_cycle = param.status["duty_cycle"], cycle_time = param.status["cycle_time"], option = param.status["option"]  )
        
    else: #request.method == 'POST' (first temp sensor / backwards compatibility)
        # get command from web browser or Android   
        #print request.form
        param.status["option"] = request.form["option"] 
        param.status["mode"] = request.form["mode"] 
        param.status["set_point"] = float(request.form["setpoint"])
        param.status["duty_cycle"] = float(request.form["dutycycle"]) 
        param.status["cycle_time"] = float(request.form["cycletime"])
        param.status["dry_manage_temp"] = float(request.form.get("dryManageTemp", param.status["dry_manage_temp"])) 
        param.status["num_pnts_smooth"] = int(request.form.get("numPntsSmooth", param.status["num_pnts_smooth"])) 
        param.status["k_param"] = float(request.form["k"])
        param.status["i_param"] = float(request.form["i"])
        param.status["d_param"] = float(request.form["d"])
                
        #send to main temp control process 
        #if did not receive variable key value in POST, the param class default is used
        parent_conn.send(param.status)     
        return 'OK'

#post params (selectable temp sensor number)    
@app.route('/postparams/<sensorNum>', methods=['POST'])
def postparams(sensorNum=None):
    param.status["option"] = request.form["option"] 
    param.status["mode"] = request.form["mode"] 
    param.status["set_point"] = float(request.form["setpoint"])
    param.status["duty_cycle"] = float(request.form["dutycycle"]) #is boil duty cycle if mode == "boil"
    param.status["cycle_time"] = float(request.form["cycletime"])
    param.status["dry_manage_temp"] = float(request.form.get("dryManageTemp", param.status["dry_manage_temp"])) 
    param.status["num_pnts_smooth"] = int(request.form.get("numPntsSmooth", param.status["num_pnts_smooth"]))
    param.status["k_param"] = float(request.form["k"])
    param.status["i_param"] = float(request.form["i"])
    param.status["d_param"] = float(request.form["d"])
    if DEBUG:
        lck.acquire()
        print   ("postparams:senssornum: ", sensorNum,param.status) 
        lck.release()    
    #send to main temp control process 
    #if did not receive variable key value in POST, the param class default is used
    if sensorNum == "1":
        lck.acquire()
        print "got post to temp sensor 1"
        lck.release()
        parent_conn.send(param.status)
    elif sensorNum == "2":
        lck.acquire()
        print "got post to temp sensor 2"
        lck.release()
        if len(pinHeatList) >= 2:
            parent_connB.send(param.status)
        else:
            param.status["mode"] = "No Temp Control"
            param.status["set_point"] = 0.0
            param.status["duty_cycle"] = 0.0 
            parent_connB.send(param.status)
            print "no heat GPIO pin assigned"
    elif sensorNum == "3":
        lck.acquire()
        print "got post to temp sensor 3"
        lck.release()
        if len(pinHeatList) >= 3:
            parent_connC.send(param.status)
        else:
            param.status["mode"] = "No Temp Control"
            param.status["set_point"] = 0.0
            param.status["duty_cycle"] = 0.0 
            parent_connC.send(param.status)
            print "no heat GPIO pin assigned"
    else:
        print "Sensor doesn't exist (POST)"
        
    return 'OK'

#post GPIO     
@app.route('/GPIO_Toggle/<GPIO_Num>/<onoff>', methods=['GET'])
def GPIO_Toggle(GPIO_Num=None, onoff=None):
    
    if len(pinHeatList) >= int(GPIO_Num):
        out = {"pin" : pinHeatList[int(GPIO_Num)-1], "status" : "off"}
        if onoff == "on":
            GPIO.output(pinHeatList[int(GPIO_Num)-1], ON)
            out["status"] = "on"
            print "GPIO Pin #%s is toggled on" % pinGPIOList[int(GPIO_Num)-1] 
        else: #off
            GPIO.output(pinHeatList[int(GPIO_Num)-1], OFF)
    #        print "GPIO Pin #%s is toggled off" % pinGPIOList[int(GPIO_Num)-1] 
    else:
        out = {"pin" : 0, "status" : "off"}
        
    return jsonify(**out)


#get status from RasPiBrew using firefox web browser (first temp sensor / backwards compatibility)
@app.route('/getstatus') #only GET
def getstatusB():          
    #blocking receive - current status    
    param.status = statusQ.get()        
    return jsonify(**param.status)

#get status from RasPiDry using firefox web browser (selectable temp sensor)
@app.route('/getstatus/<sensorNum>') #only GET
def getstatus(sensorNum=None):          
    #blocking receive - current status
    if sensorNum == "1":
        param.status = statusQ.get()
    elif sensorNum == "2":
        param.status = statusQ_B.get()
    elif sensorNum == "3":
        param.status = statusQ_C.get()
    else:
        print "Sensor doesn't exist (GET)"
        param.status["temp"] = "-999"
        
    return jsonify(**param.status)


#duty_cycle = pid.calcPID_reg4(temp_ma, set_point, True)
#duty = duty_cycle/100.0
#on_time = cycle_time*(duty)
#off_time = cycle_time*(1.0-duty)


def logdata(tank, temp, heat):
    f = open("dryer" + str(tank) + ".csv", "ab")
    f.write("%3.1f;%3.3f;%3.3f\n" % (getruntime(), temp, heat))
    f.close()
	
def packParamGet (numTempSensors,myTempSensorNum,temp,tempUnits,elapsed,mode,cycle_time,duty_cycle,\
                 dry_duty_cycle,set_point, dry_manage_temp, num_pnts_smooth, k_param, i_param, d_param,option):
    
    param.status["numTempSensors"] = numTempSensors
    param.status["temp"] = temp
    param.status["tempUnits"] = tempUnits
    param.status["elapsed"] = elapsed
    param.status["mode"] = mode
    param.status["cycle_time"] = cycle_time
    param.status["duty_cycle"] = duty_cycle
 #   param.status["duty_cycle_temp"] = duty_cycle_temp
    param.status["dry_duty_cycle"] = dry_duty_cycle
    param.status["set_point"] = set_point
    param.status["dry_manage_temp"] = dry_manage_temp
    param.status["num_pnts_smooth"] = num_pnts_smooth
    param.status["k_param"] = k_param
    param.status["i_param"] = i_param
    param.status["d_param"] = d_param
    param.status["option"] = option
    return param.status


	
# Main Temperature Controll Process
def tempControlProc (myTempSensor, display, pinNum, readOnly, paramStatus, statusQ, subscribeQ, conn):

        mode, cycle_time, duty_cycle, dry_duty_cycle, set_point, dry_manage_temp, num_pnts_smooth, \
        k_param, i_param, d_param ,option = param.unPackParamInitAndPost(paramStatus)
		
        p = current_process()
        print ("Starting , {}, pid {}, param {}".format( p.name, p.pid,paramStatus))	  
        #Pipe to communicate with "Get Temperature Process"
        parent_conn_temp, child_conn_temp = Pipe()    
        #Start Get Temperature Process        
        ptemp = Process(target=gettempProc, args=( myTempSensor,child_conn_temp))
        ptemp.daemon = True
        ptemp.start()  
        lck.acquire()
        print ("Starting , {}, pid {}".format( ptemp.name, ptemp.pid))
        lck.release() 

        #Pipe to communicate with "Heat Process"
        parent_conn_heat, child_conn_heat = Pipe() 
        #Start Heat Process   
        pheat = Process( name ="heatProcGPIO",target=heatProcGPIO, args=(cycle_time, duty_cycle, pinNum, child_conn_heat))
        pheat.daemon = True
        pheat.start() 
        lck.acquire()
        print " starting {} , pid {}, pin {},readOnly  {}".format( pheat.name, pheat.pid, pinNum,readOnly)
        lck.release() 
 
        #time interval to write to iot
        iottime=time.time()
	 			
        temp_ma_list = [] #MVA temp list
        manage_dry_trigger = True#False

        tempUnits = xml_root.find('Temp_Units').text.strip()


        temp_ma = 0.0 #MVA temp
        humidity=0

    #overwrite log file for new data log
    #    ff = open("dryer" + str(myTempSensor.sensorNum) + ".csv", "wb")
    #    ff.close()


        mode1 = None
        lastwrite=time.time()
        while (True):
            readytemp = False
            while parent_conn_temp.poll(): #Poll Get Temperature Process Pipe. Return whether there is any data available to be read.
                temp_C, humidity,tempSensorNum, elapsed = parent_conn_temp.recv() #non blocking receive from Get Temperature Process. Return an object sent from the other end of the connection using 
	
                if temp_C == -99:
                    print "Bad Temp Reading - retry"
                    continue

                if (tempUnits == 'F'):
                    temp = (9.0/5.0)*temp_C + 32
                else:
                    temp = temp_C

                temp_str = "%3.2f" % temp  #12.3456789 > 12.35
                display.showTemperature(temp_str)
                readytemp = True           
            if readytemp == True:
                lck.acquire()
                print "tempControlProc :readytemp {},  set_point {}, duty_cycle {}, pin {}, temp {}, mode  {},numTempSensors {} ".format(readytemp, set_point ,duty_cycle, pinNum, temp,  mode,numTempSensors )
                lck.release() 

                while (parent_conn_heat.poll()): #get last poll(1) 1sek blok
                   cycle_time, duty_cycle = parent_conn_heat.recv()


                 #get status from mqtt subsrciber 
                if cert is not None:
                 lck.acquire()
                 print"tempControlProc getting message from IOT subscription"
                 lck.release()
                 try:
                  while not queueSub.empty() or queueSub.get(block=False)== 'DONE':
                    msg = queueSub.get(block=False)         # Read from the queue and do nothing
                    print"tempControlProc queueSub ", msg
                    if (msg == 'DONE'):
                      #print "tempControlProc DONE, pin {}".format(pinNum)
                      break
                    elif msg == "False":
                      readOnly=True
                      if mode1 is None:
                        mode1=mode
                      mode="stopped"
                      duty_cycle=0
                      parent_conn_heat.send   ([cycle_time, duty_cycle])					
                      #print "tempControlProct queueSub readonly {}, mode {},mode1 {}, pin{}".format(readOnly, mode,mode1, pinNum)
                    elif msg == "stopped":
                      readOnly=True
                      mode="stopped"
                      #print "tempControlProct queueSub readonly {}, mode {}, mode1 {},pin{}".format(readOnly,  mode, mode1,pinNum)
                    elif msg == "True":
                      if mode1 is not None:
                         mode=mode1
                      mode1 = None
                      readOnly=False
                      #print "tempControlProct queueSub readonly {}, mode {}, mode1 {}, pin{}".format(readOnly,  mode, mode1,pinNum)
                      break
                 except Empty:
                   pass



                if mode == "off":
                  lck.acquire()
                  print ("stoped", (time.time()-stop))
                  lck.release()
                  import  offGPIO
                  GPIO.cleanup() # this ensures a clean exit 
                  os.killpg(0, signal.SIGKILL) # kill all processes in my group

                if  mode =="auto": 
                    temp_ma_list.append(temp)

                    #smooth data
                    temp_ma = 0.0 #moving temp avg init
                    while (len(temp_ma_list) > num_pnts_smooth):
                        temp_ma_list.pop(0) #remove oldest elements in list

                    if (len(temp_ma_list) < num_pnts_smooth):
                        for temp_pnt in temp_ma_list:
                            temp_ma += temp_pnt
                        temp_ma /= len(temp_ma_list)
                    else: #len(temp_ma_list) == num_pnts_smooth
                        for temp_idx in range(num_pnts_smooth):
                            temp_ma += temp_ma_list[temp_idx]
                        temp_ma /= num_pnts_smooth

                    #print "len(temp_ma_list) = %d" % len(temp_ma_list)
                    #print "Num Points smooth = %d" % num_pnts_smooth
                    #print "temp_ma = %.2f" % temp_ma
                    #print temp_ma_list
                    #calculate PID every cycle
                    if (readyPIDcalc == True):
                        #https://www.raspberrypi.org/forums/viewtopic.php?f=35&t=62438&p=463458
	                #https://www.raspberrypi.org/forums/viewtopic.php?t=63714&p=471636
                        set_point=dry_manage_temp
                        pid = PIDController.pidpy(cycle_time, k_param, i_param, d_param) #init pid
                        duty_cycle = pid.calcPID_reg4(temp_ma, set_point, True) #ogrevalna stopnja cikla
                        #send to heat process every cycle
                        parent_conn_heat.send([cycle_time, duty_cycle])
#                       readyPIDcalc = False
                        lck.acquire()
                        print "tempControlProc : duty_cycle {}, k {}, i {}, d  {},temp_ma {} ".format(duty_cycle, k_param, i_param, d_param, temp_ma )
                        lck.release() 



                if  mode =="heating" :
                    if (temp >= dry_manage_temp):# and (manage_dry_trigger == True): 
			   #send  0% heat power
                        manage_dry_trigger = False
                        duty_cycle = 0 
                        parent_conn_heat.send   ([cycle_time, duty_cycle])					
                    elif (temp < set_point-4): #dry_manage_temp-4):# and (manage_dry_trigger == True): 
			   #send  100% heat power
                        manage_dry_trigger = False
                        duty_cycle = 100 
                        parent_conn_heat.send      ([cycle_time, duty_cycle])#2.0,100
                    elif (temp <= set_point-2): #dry_manage_temp-2):# and (manage_dry_trigger == True):
			#60% heat power to lower heater
                        manage_dry_trigger = False
                        if pinNum == 22:
                          duty_cycle = 100
                        else:
                          duty_cycle = 0
                        parent_conn_heat.send([cycle_time, duty_cycle])#2.0,600
                    elif (temp < set_point):#dry_manage_temp):# and (manage_dry_trigger == True):
			 #send  0% heat power and 50% heat power to lower heater
                        manage_dry_trigger = False
                        if pinNum == 22:
                          duty_cycle = 50
                        else:
                          duty_cycle = 0
                        parent_conn_heat.send([cycle_time, duty_cycle])#2.0,600
                    elif (temp >= set_point):#dry_manage_temp):# and (manage_dry_trigger == True):
					#send  0% heat power to  heater
                        manage_dry_trigger = False
                        duty_cycle = 0
                        parent_conn_heat.send([cycle_time, duty_cycle])#2.0,600

                #put current status in queue
                try:
                    paramStatus = packParamGet(numTempSensors, myTempSensor.sensorNum, temp_str, tempUnits, elapsed, mode, cycle_time, duty_cycle, \
                            dry_duty_cycle, set_point, dry_manage_temp, num_pnts_smooth, k_param, i_param, d_param,option )
                    statusQ.put(paramStatus) #GET request
                except Full:
                    pass

                while (statusQ.qsize() >= 2):
                    statusQ.get() #remove old status

              #  print "Current Temp: %3.2f deg %s, Heat Output: %3.1f%%" \
              #                                          % (temp, tempUnits, duty_cycle)

                logdata(myTempSensor.sensorNum, temp, duty_cycle)#senzorPin namesto Num

                readytemp == False   

                 #if mode is stopped and only reading temperature (no temp control)
                if mode == 'stopped' and readOnly:
                    duty_cycle = 0
                    parent_conn_heat.send([cycle_time, duty_cycle])
                    if DEBUG:
                      lck.acquire()
                      print "loop continue, mode {}, Pin {}".format(mode, pinNum)
                      lck.release()

                 #if only reading temperature (no temp control)
                if readOnly: 
                    if DEBUG:
                       lck.acquire()
                       print "loop continue, readonly {}, Pin {}".format(readOnly, pinNum)
                       lck.release()
                    continue
 
 
                if getruntime() >= (dry_time*60):
                   lck.acquire()
                   print "exit dtime {}> dry_time {} ".format(getruntime(), dry_time*60) 
                   lck.release()
                   GPIO.cleanup() # this ensures a clean exit 
                   os.killpg(0, signal.SIGKILL) # kill all processes in my group		 

                if time.time()-iottime > sleep  and  cert is not None: 
                  iottime=time.time()
                  weight=10
                  humidity=10  
                  mode0="'"+str(mode)+"'"
                  mode0=str(mode0)
                  iot= iot_mqtt_publisher2( thing,cert)
                  lck.acquire()
                  print ("Send to IOT from temp_control",thing,cert,round(temp),round(temp),mode0,set_point,round(humidity),round(weight),round(getruntime()))
                  lck.release()
                  iot.send(round(temp,2),round(temp,2),mode0,set_point,round(humidity,2),round(weight,2),round(getruntime(),0))
              #    parent_connIOT.send([round(temp,2),round(temp,2),mode0,set_point,round(humidity,2),round(weight,2),round(getruntime(),0)])
                print "Write pin {}, time {}, sleep {}".format(pinNum , time.time()- lastwrite , sleep)
                if pinNum == 22 and time.time()- lastwrite > sleep: #and temp > 0 
                  tab="	"
                  line="{d}{t}{l}{t}{m}{t}{n}{t}{o}\r\n".format(d=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),l=(format(temp,'.2f')),m=(format(temp-1,'.2f')),n=format(humidity,'.2f'),o=0,t=tab)
                  lck.acquire()
                  print("write {} to {}.csv".format( line,filename))
                  lck.release()
                  with open( filename+".csv", "a") as myfile:
                    myfile.write(line)
                    myfile.close()
                    lastwrite=time.time()

 #               print "next loop"
         #   while parent_conn_heat.poll(): #Poll Heat Process Pipe
         #       cycle_time, duty_cycle = parent_conn_heat.recv() #non blocking receive from Heat Process
         #       display.showDutyCycle(duty_cycle)
         #       print "tempControlProc parent_conn_heat",parent_conn_heat.poll(), cycle_time, duty_cycle				
         #       readyPIDcalc = True

            readyPOST = False
            while conn.poll(): #POST settings - Received POST from web browser or Android device
                paramStatus = conn.recv()
                mode, cycle_time, duty_cycle, dry_duty_cycle, set_point, dry_manage_temp, num_pnts_smooth, \
                k_param, i_param, d_param ,option = param.unPackParamInitAndPost(paramStatus)
                readyPOST = True
            if readyPOST == True:
                #print "tempControlProc  POST conn_poll duty_cycle {}, pin {} ,mode {}, cycle_time {} ".format(  duty_cycle, pinNum, mode, cycle_time)
                if mode == "auto":
                    display.showAutoMode(set_point)
                    lck.acquire()
                    print "auto selected"
                    lck.release()

                    for pin in pinFanList: 
                       if not GPIO.input(pin):  # returns 1
                         print "Fan started", pin
                         GPIO.output(pin, ON)

                    pid = PIDController.pidpy(cycle_time, k_param, i_param, d_param) #init pid
                    duty_cycle = pid.calcPID_reg4(temp_ma, set_point, True)
                    parent_conn_heat.send([cycle_time, duty_cycle])
                if mode == "heating":
                    display.showDryMode()
                    lck.acquire()
                    print "heating selected"
                    lck.release()
                    for pin in pinFanList: 
                       if not GPIO.input(pin):  # returns 1
                         print "Fan started", pin
                         GPIO.output(pin, ON)
                  #  dry_duty_cycle = duty_cycle_temp
                    duty_cycle = dry_duty_cycle #100 #full power to dry manage temperature
                    manage_dry_trigger = True
                    parent_conn_heat.send([cycle_time, duty_cycle])
                if mode == "manual":
                    display.showManualMode()
                    lck.acquire()
                    print "manual selected"
                    lck.release()
                    for pin in pinFanList: 
                       if GPIO.input(pin):  # returns 1
                         print "Fan started", pin
                         GPIO.output(pin, HIGH)
                    duty_cycle = dry_duty_cycle
                    parent_conn_heat.send([cycle_time, duty_cycle])
                if mode == "off":
                    display.showOffMode()
                    lck.acquire()
                    print "off selected"
                    lck.release()
                    duty_cycle = 0
                    readonly=True
                    parent_conn_heat.send([cycle_time, duty_cycle])
                if mode == "stopped":
                    display.showOffMode()
                    lck.acquire()
                    print "stop  selected"
                    lck.release()
                    GPIO.output(piNum,  GPIO.LOW)
                    for pin in pinFanList: 
                       print "Fan stopped", pin
                       GPIO.output(pin, LOW)
                    duty_cycle = 0
                    parent_conn_heat.send([cycle_time, duty_cycle])
                readyPOST = False
            time.sleep(.01)
#http://code.activestate.com/recipes/577223-blocking-polling-pipes-queues-in-multiprocessing-a/
            #print "tempcontrol end loop mode {}".format(mode)





	# Stand Alone Get Temperature Process               
def gettempProc (myTempSensor, conn):
    p = current_process()
    print ('Starting gettempProc p.name {}, p.pid {}'.format( p.name, p.pid))
    while (True):
        t = time.time()
        time.sleep(.5) #.1+~.83 = ~1.33 seconds
        temp,humidity = myTempSensor.readTempC()
        elapsed = "%.2f" % (time.time() - t)
        conn.send([temp,humidity, myTempSensor.sensorNum, elapsed])


        
# Stand Alone Heat Process using I2C (optional)
def heatProcI2C(cycle_time, duty_cycle, conn):
    p = current_process()
    print 'Starting:', p.name, p.pid
    bus = SMBus(0)
    bus.write_byte_data(0x26,0x00,0x00) #set I/0 to write
    while (True):
        while (conn.poll()): #get last
            cycle_time, duty_cycle = conn.recv()
        conn.send([cycle_time, duty_cycle])  
        if duty_cycle == 0:
            bus.write_byte_data(0x26,0x09,0x00)
            time.sleep(cycle_time)
        elif duty_cycle == 100:
            bus.write_byte_data(0x26,0x09,0x01)
            time.sleep(cycle_time)
        else:
            on_time, off_time = getonofftime(cycle_time, duty_cycle)
            bus.write_byte_data(0x26,0x09,0x01)
            time.sleep(on_time)
            bus.write_byte_data(0x26,0x09,0x00)
            time.sleep(off_time)

# Stand Alone Heat Process using GPIO
def heatProcGPIO(cycle_time, duty_cycle, pinNum, conn):
        if pinNum <= 0:
           return
        p = current_process()
        print 'Starting ', p.name, p.pid, pinNum, p._parent_pid
            
        GPIO.setup(pinNum, GPIO.OUT)
        while (True):
            while (conn.poll(1)): #get last poll(1) 1sek blok
                cycle_time, duty_cycle = conn.recv()
              #  print "heatProcGPIO, con,pool pinNum {}, cycle {}, duty {} ".format(pinNum, cycle_time, duty_cycle) 
            conn.send([cycle_time, duty_cycle])
            lck.acquire()
            print "heatProcGPIO-0, conn receive cycle_time {}, duty_cycle {} for Pin {}".format (cycle_time, duty_cycle, pinNum)
            lck.release()
            if duty_cycle == 0:
                GPIO.output(pinNum, OFF)
                time.sleep(cycle_time)
            elif duty_cycle == 100:
                GPIO.output(pinNum, ON)
                time.sleep(cycle_time)
            elif duty_cycle < 35:
                GPIO.output(pinNum, OFF)
                time.sleep(cycle_time)	
            elif duty_cycle == 50:
                on_time, off_time = getonofftime(cycle_time, duty_cycle)
                GPIO.output(pinNum, ON)
                time.sleep(on_time)
                GPIO.output(pinNum, OFF)
                time.sleep(off_time)
            else:
                on_time, off_time = getonofftime(cycle_time, duty_cycle)
#                print "heatProcGPIO-x, conn receive on_time {},  off_time  {}".format (on_time, off_time)
                GPIO.output(pinNum, ON)
                time.sleep(on_time)
                GPIO.output(pinNum, OFF)
                time.sleep(off_time)
#            time.sleep(.01)

				
#Get time heating element is on and off during a set cycle time
def getonofftime(cycle_time, duty_cycle):
    duty = duty_cycle/100.0
    on_time = cycle_time*(duty)
    off_time = cycle_time*(1.0-duty)   
    return [on_time, off_time]
	
def getruntime():
    return (time.time() - runtime)   

#keyboard interrupt
def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    #import  offGPIO 
    GPIO.cleanup()
    sys.exit(0)




if __name__ == '__main__':
   # logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
   # logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s')
   # info = {'stop': False}
   # logging.debug('Hello from main')
    DEBUG=True
# Define and parse command line arguments
    parser = argparse.ArgumentParser(description="My simple Python service")
    parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

# If the log file is specified on the command line then override the default
    args = parser.parse_args()
    if args.log:
        LOG_FILENAME = args.log

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
    logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
    logger.setLevel(LOG_LEVEL)

# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
    handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
    handler.setFormatter(formatter)
# Attach the handler to the logger
    logger.addHandler(handler)
# Replace stdout with logging to file at INFO level
    sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
    sys.stderr = MyLogger(logger, logging.ERROR)

    lck = Lock()

    #Configuring Your Pi for I2C
    #add the following lines to /etc/modules  i2c-dev i2c-bcm2708
    #sudo apt-get install python-smbus sudo apt-get install i2c-tools

    #call(["modprobe", "i2c-bcm2708"])
    #call(["modprobe", "i2c-dev"]) #load module i2c-dev
    # Retrieve root element from config.xml for parsing
    tree = ET.parse('config.xml')
    xml_root = tree.getroot()
    template_name = xml_root.find('Template').text.strip()
    root_dir_elem = xml_root.find('RootDir')
    if root_dir_elem is not None:
        os.chdir(root_dir_elem.text.strip())
    else:
        print("No RootDir tag found in config.xml, running from current directory")


    useLCD = xml_root.find('Use_LCD').text.strip()
    if useLCD == "yes":
        tempUnits = xml_root.find('Temp_Units').text.strip()
        display = Display.LCD(tempUnits)
    else:
        display = Display.NoDisplay()
    
    gpioNumberingScheme = xml_root.find('GPIO_pin_numbering_scheme').text.strip()
    if gpioNumberingScheme == "BOARD":
        GPIO.setmode(GPIO.BOARD)
    else:
	    GPIO.setmode(GPIO.BCM)

    gpioInverted = xml_root.find('GPIO_Inverted').text.strip()
    if gpioInverted == "0":
	  ON = 1
	  OFF = 0
    else:
	  ON = 0
	  OFF = 1
    elem = xml_root.find('mode')
    if elem is not None:
        param.status["mode"]=elem.text.strip()
    elem = xml_root.find('cycle_time')
    if elem is not None:
        param.status["cycle_time"]=float(elem.text.strip())
    elem = xml_root.find('dry_time')
    if elem is not None:
        param.status["dry_time"]=float(elem.text.strip())
        dry_time=int(elem.text.strip())*60
    elem = xml_root.find('dry_duty_cycle')
    if elem is not None:
        param.status["dry_duty_cycle"]=float(elem.text.strip())
    if   param.status["dry_duty_cycle"] > 100:
         print "wrong dry_duty_cycle {} ".format(param.status["dry_duty_cycle"])
         param.status["dry_duty_cycle"] = 100
         sys.exit(0)
    elem = xml_root.find('set_point')
    if elem is not None:
        param.status["set_point"]=float(elem.text.strip()) 
        set_point =int( xml_root.find('set_point').text.strip())
    else: 
         print "set_point not set exit! "
         sys.exit(0)

    elem = xml_root.find('dry_manage_temp')
    if elem is not None:
        param.status["dry_manage_temp"]=int(elem.text.strip())	
    elem = xml_root.find('num_pnts_smooth')
    if elem is not None:
        param.status["num_pnts_smooth"]=int(elem.text.strip())		
    elem = xml_root.find('k_param')
    if elem is not None:
      readyPIDcalc = True 
      try:
        param.status["k_param"]=int(elem.text.strip())
      except ValueError:
        param.status["k_param"]=float(elem.text.strip())	
    elem = xml_root.find('i_param')
    if elem is not None:
      readyPIDcalc = readyPIDcalc and True 
      try:
        param.status["i_param"]=int(elem.text.strip())
      except ValueError:
        param.status["i_param"]=float(elem.text.strip())
    elem = xml_root.find('d_param')
    if elem is not None:
      readyPIDcalc = readyPIDcalc and True 
      try:
        param.status["d_param"]=int(elem.text.strip())
      except ValueError:
        param.status["d_param"]=float(elem.text.strip())

    elem = xml_root.find('options')
    if elem is not None:
       print      elem.get('name').strip()
       option    =int(elem.get('id').strip())
       if option > 0:
         set_point =int(elem.get('setpoint').strip())
         dry_time  =int(elem.get('ends').strip())*60
         param.status["option"]=option 
         param.status["set_point"]=set_point
         param.status["dry_time"]=dry_time

	

    pinFanList=[]
    for pin in xml_root.iter('Fan_Pin'):
        pinFanList.append(int(pin.text.strip()))

    for pin in pinFanList: 
         GPIO.setup(pin, GPIO.OUT)
		 
    pinHeatList=[]
    for pin in xml_root.iter('Heat_Pin'):
        pinHeatList.append(int(pin.text.strip()))

    for pin in pinHeatList: 
         print "heat pin", pin
         GPIO.setup(pin, GPIO.OUT)

#pump pin
    pinGPIOList=[]
    for pin in xml_root.iter('GPIO_Pin'):
        pinGPIOList.append(int(pin.text.strip()))
		 
    pinTempGPIOList=[] 
    numTempSensors = 0
    for tempSensorId in xml_root.iter('Temp_Sensor_Id'):
            numTempSensors += 1
    for pin in xml_root.iter('Temp_Pin'):
         print "Temp_pin",pin.text.strip()
         pinTempGPIOList.append(int(pin.text.strip()))

    for pinNum in pinTempGPIOList:
        GPIO.setup(pinNum, GPIO.OUT)

    for sensor in xml_root.iter('Temp_Sensor'):
     #if sensor in ['DHT11','DHT22','AM2302']:
         TEMP_SENSOR=int(sensor.text.strip()[3:])
         #print "TEMP_SENSOR",TEMP_SENSOR

    elem =xml_root.find('mode')
    if elem is not None:
        mode=elem.text.strip()	
    if mode=="stopped":
	  #if only reading temperature (no temp control)
      readOnly=True
    else:
      readOnly = False		
    print mode
    filename =   xml_root.find('filename')
    Bucketname =   xml_root.find('Bucketname')
    if Bucketname  is not None:
      Bucketname =Bucketname.text.strip()

    if  filename  is not None:
      filename=filename.text.strip()
    else:
      print ("exit: no file")
      sys.exit()     
	
     #start fan
    if mode != "stopped":
      for pin in pinFanList: 
         print "Fan started", pin, mode
         GPIO.output(pin, ON)	

    cert = xml_root.find('cert')
    if  cert is not None:
         cert=cert.text.strip()


    sleep = int(xml_root.find('sleep').text.strip())
 #   DRYTIME=int(param.status["dry_time"])*60 

    if filename  is None :
        print ("file open error" ) # print value of counter 
        import  offGPIO 
        sys.exit(0) # quit Python
      #try:
       #f = open(filename+'.csv','w')   # Trying to create a new file or open one
       #f.close()
      #except "IOError":
        # print ("file open error" ) # print value of counter 
        #import  offGPIO 
        #sys.exit(0) # quit Python

    if filename  is not None and Bucketname  is not None:
      print (filename,Bucketname,sleep)
      upload= s3Upload(filename,Bucketname, sleep,lck)
      delimiter="	"
      p = Process(target=upload.Fileupload, args=(delimiter, ))
      p.start()

    ThingList=[]
    for elem in xml_root.iter('thing'):
         ThingList.append(elem.text.strip())

    for thing in ThingList:
      if "Control" in thing: 
           mode="'"+str(mode)+"'"
           print "{} publisher : mode {},set_point {},dry_time {}".format (thing,mode,set_point,dry_time)
           iot= iot_mqtt_publisher2( thing,cert)
           iot.send(None,None,mode,set_point,None,None,dry_time)


    if cert is not None:
      print "FoodDehydratorTemperatureStatus subscriber init"
      queueSub = Queue()   # reader() reads from queue
                      # writer() writes to queue
      # iotstat= iot_mqtt_subscriber2( thing,cert,child_Subconn)
      iotstat= iot_mqtt_subscriber2( thing,cert,queueSub)
      p = Process(target=iotstat.on_loop, args=((queueSub),))
      p.daemon = True
      p.start()

    runtime = time.time()
    stop  = runtime + dry_time/60
    #if Temp_Sensor probe
    for tempSensorId in xml_root.iter('Temp_Sensor_Id'):
        myTempSensor = Temp1Wire.Temp1Wire(tempSensorId.text.strip())  
        if len(pinHeatList) >= myTempSensor.sensorNum + 1:
            pinNum = pinHeatList[myTempSensor.sensorNum]
            readOnly = False
        else:
            pinNum = 0
            readOnly = True
        
        if myTempSensor.sensorNum >= 1:
            display = Display.NoDisplay()
             
        if myTempSensor.sensorNum == 0:
            statusQ = Queue(2) #blocking queue        
            parent_conn, child_conn = Pipe()
            p = Process(name = "tempControlProc", target=tempControlProc, args=(myTempSensor, display, pinNum, readOnly, \
                                                              param.status, statusQ, child_conn))
            p.start()
            
        if myTempSensor.sensorNum == 1:
            statusQ_B = Queue(2) #blocking queue    
            parent_connB, child_conn = Pipe()  
            p = Process(name = "tempControlProc", target=tempControlProc, args=(myTempSensor, display, pinNum, readOnly, \
                                                              param.status, statusQ_B, child_conn))
            p.start()
            
        if myTempSensor.sensorNum == 2:
            statusQ_C = Queue(2) #blocking queue 
            parent_connC, child_conn = Pipe()     
            p = Process(name = "tempControlProc", target=tempControlProc, args=(myTempSensor, display, pinNum, readOnly, \
                                                              param.status, statusQ_C, child_conn))
            p.start()

    procs = []
    try:
     i=0
     for pinNum in pinHeatList:
         print "main HeatPin",pinNum

         subscribeQ = Queue(2) #blocking queue 
         numTempSensors += 1
         if TEMP_SENSOR is not None:
          if len(pinHeatList) == len(pinTempGPIOList):
            myTempSensor = Temp2Wire.Temp2Wire(TEMP_SENSOR,pinTempGPIOList[i]) #pin.text.strip())
          elif len(pinTempGPIOList)==1:
            myTempSensor = Temp2Wire.Temp2Wire(TEMP_SENSOR,pinTempGPIOList[0]) #pin.text.strip())
         if i==0:
           statusQ = Queue(2) #blocking queue 
           parent_conn, child_conn = Pipe()
           p = Process(name = "tempControlProc", target=tempControlProc, args=(myTempSensor, display, pinNum, readOnly, \
                                                              param.status, statusQ, subscribeQ, child_conn)) 

         if i==1:
          statusQ_B = Queue(2) #blocking queue
          parent_connB, child_conn = Pipe()  
          p = Process(name = "tempControlProc", target=tempControlProc, args=(myTempSensor, display, pinNum, readOnly, \
                                                              param.status, statusQ_B, subscribeQ, child_conn))
         if i==2:
          statusQ_C = Queue(2) #blocking queue
          parent_connC, child_conn = Pipe()
          p = Process(name = "tempControlProc", target=tempControlProc, args=(myTempSensor, display, pinNum, readOnly, \
                                                              param.status, statusQ_B, subscribeQ, child_conn))
         p.start()
         print "Process start", p.name, pinNum	 
         procs.append(p)
         i+=1




    except KeyboardInterrupt:
        print ("Interrupt", (time.time()-stop)) # print value of counter 
        import  offGPIO 
        p.terminate()
        sys.exit(0) # quit Python


    except Exception, e:
     print ("Error " + str(e))
     import  offGPIO 
     p.terminate()
     sys.exit(0) # quit Python

  #  except (KeyboardInterrupt, SystemExit):
   #     raise

    signal.signal(signal.SIGINT, signal_handler)
    print 'Press Ctrl+C'

    app.debug = True 
    if cert is None:
      from flask import Flask, render_template, request, jsonify
    
      app.run(use_reloader=False, host='0.0.0.0',port=88,debug=True)


 



