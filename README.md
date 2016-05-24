# Raspberry Pi controllered Smart Food Dehydrator (over a Web or IOT Interface)

## Raspberry Pi Dehydrator Controller for drying Fruit, Fruit leather, Vegetables, Yoghurt making, Raising Bread 

This system is an inexpensive and flexible wireless  Web or IOT (internet of things) based controller for drying Fruit, Fruit leather, Vegetables, Yoghurt making and Raising Bread.  You can use your own homemade or some commercial dehydrator. The system is connected to Amazon cloud using AWS internet of things to smart control. It's based on https://github.com/steve71/RasPiBrew project.


This program will control an electric heating element in a dehydrator to set the air temperature.  All status included temperature, humidity is logged localy to file  in CSV format to display on web  browser or android device wirelessly approx. every fwe seconds (sleep time).   The duty cycle and temperature is plotted in real time.  A Type C PID algorithm has been successfully implemented to automatically control the heating element when the desired temperature is set.  CSV  is transformed to  JSON file and both send to AWS S3 to display  temperature, humidity, weight diagram and spreadsheet for analytical purpose.  Status is also logged to AWS IOT to display on Android device and to control dehydrator by Android device. So there no need to run web server on Raspberry PI.

For bootstrap multi-heater and GPIO switch control version set template element to raspidry_bootstrap.html in config.xml.  For original version set template to raspidry.html.  The config.xml file explains how to setup for one, two or three heaters.  The number of heaters and GPIO switches can easily be expanded in the software.
The same raspidry.py code supports both versions.    

* Programmable [PID Controller]  for precise air heater temperature control
* Programmable  duty cycle time, and dry time
* Selectable options (Fruit, Fruit leather, Vegetables, Yoghurt making, Raising Bread)
* Controllable from web browser, Android device (iPhone  coming soon) on Wifi network
* LCD readout for system status, toggle buttons for operation
* AWS S3 data archiving for analysing
* AWS IOT register a status of dehydrator and commands from Android device
* AWS Simple Notification Service (SNS) send an alarm, when temperature exceeded high level or process is interupted 
* Visualization using open source  spreadsheet and plot javascript


----------
##Hardware and Software Setup Information:  
![Hardware and Software ](http://iothome.s3.amazonaws.com/image/idea2.png)
 
## Configuration 
![configuration](http://iothome.s3.amazonaws.com/image/config.png)


## Bootstrap Web Interface in Browser
![Bootstrap Web interface in Browser](http://iothome.s3.amazonaws.com/image/web1.png)


## Original Web Interface in  Browser

<img src="https://github.com/bmili/RasPiDry/raw/images/PID_Tuning.png" alt="" width="954 height="476.5" />

## Plot and spreadsheet  in Browser
![Plot and spreadsheet in Browser](http://iothome.s3.amazonaws.com/image/web2.png)

## Setting  
 (https://github.com/bmili/RasPiDry/raw/images/PID_Temp_Control.png) 

The temp plot shows temperature in degrees F or C over time in seconds.  
The heat plot shows duty cycle percentage over time in seconds.

## Android application 

There is RasPiBrew New Version 1.1.4 of Android application on Google  Play

<img src="http://iothome.s3.amazonaws.com/image/android_set.jpg" alt="Android set"/> <img src="http://iothome.s3.amazonaws.com/image/android_chart.jpg" alt="Android chart"/></br>

RasPiDry of Android application is comming soon.  And also RasPiDry of Android AWS IOT application

## IOT interface

There is Node.js application,  which simulate simple IOT application. You need Node.js environment as described in https://github.com/aws/aws-iot-device-sdk-js/blob/master/README.md and install aws-iot-device-sdk-js-master on your Node server. Then you can run  
  "node temperature-control-client.js -f ~/certificate -g eu-west-1"
 ![Simulate IOT interface ](http://iothome.s3.amazonaws.com/image/sim1.2.png)
 
 
## Hardware

<img src="http://iothome.s3.amazonaws.com/image/hardware.jpg" alt="Hardware and Software "/>

A low cost credit card sized Raspberry Pi computer is an inexpensive and very expandable solution to controlling processes.  In our case heating process is controlled by measuring the   temperature, humidity and weight.  Used in combination with a Saint Smart    control relay ,   temperature sensors and a usb wifi dongle, a wirelessly controlled temperature controller is developed.  The Raspberry Pi can run a web server to communicate with a browser  on a PC or smartphone. In a case of connection to AWS IOT (internet of things), there is no need to run web server on RPI.  You need only Android device running android application .

Electronics used to test: 
- Raspberry Pi B+,
- Raspberry Pi  Accessories Prototype Pi Plate,
- Sain Smart 4 chanell control relay , 
- DS18B20 digital thermometer,
- 20x4 LCD and LCD117 kit (serial interface),
- 4.7k resistor, 1k resistor, 1N4001 diode, and 2N4401 transistor.,2K  resistor,10K resistor,TansistorR PN2222A  
- Edimax EW-7811UN dongle is used.

Information on Raspberry Pi low-level peripherals:  
[http://elinux.org/RPi_Low-level_peripherals](http://elinux.org/RPi_Low-level_peripherals)


## Software

Load Operating System onto SDCard

Download the raspberry pi operating system: [Raspberry Pi Downloads](http://www.raspberrypi.org/downloads) Use [Win32DiskImager](http://www.softpedia.com/get/CD-DVD-Tools/Data-CD-DVD-Burning/Win32-Disk-Imager.shtml) to install onto SDCARD. 

In terminal type: `sudo raspi-config`

Expand File System and set Internationalization options

Note: If using LCD go into Advanced Options and disable kernel messages on the serial connection

In terminal type:
 
    sudo apt-get update
    sudo apt-get upgrade

### Beginner’s Guide

Follow the [RasPi beginners guide](http://elinux.org/RPi_Beginners) to get up and running:

Run `sudo setupcon` once manually after the keyboard is setup otherwise you may have long boot times.

### Wireless Setup

Lookup [Compatible USB wifi devices](http://elinux.org/RPi_VerifiedPeripherals#USB_WiFi_Adapters) and install the drivers:

To set up a static ip address use the following in /etc/network/interfaces:

    auto lo

    iface lo inet loopback
    iface eth0 inet static

    auto wlan0
    iface wlan0 inet static
    address 192.168.1.103
    netmask 255.255.255.0
    gateway 192.168.1.1

If no wireless password use:

    wireless-essid linksys

Otherwise use the following:

    wpa-ssid "ssid"
    wpa-psk "wireless_key_passphrase" 

with the correct `ssid` (router name) and `wireless_key_passphrase`.

[Tutorial on setting up a static IP address](http://www.penguintutor.com/blog/viewblog.php?blog=6306)
[Tutorial on setting up wifi device on linux](https://help.ubuntu.com/community/WifiDocs/WiFiHowTo)

### Manual Installation

Python Modules:
Install easy_install
      'wget --no-check-certificate https://bootstrap.pypa.io/ez_setup.py'
      'python ez_setup.py --insecure'

Install pip (package installer):
     'sudo apt-get install python-setuptools'
     'sudo easy_install pip'

Install PySerial:
     sudo pip install pyserial
     [PySerial Info](http://pyserial.sourceforge.net/pyserial.html)

Install Python i2c and smbus:
     'sudo apt-get install python-smbus'
     [smbus info](http://www.acmesystems.it/i2c)

Install Flask:
     'sudo apt-get install python-dev'
     'sudo apt-get install libpcre3-dev'
     'sudo pip install Flask'
     [Flask Info](http://flask.pocoo.org/)

Install GPIO:
     'sudo apt-get install python-dev python-rpi.gpio'
     
In Raspberry Pi terminal window:
    'sudo bash'
    'cd /var'
    'mkdir www'

Copy software to `/var/www` preserving the directory structure.

At the command prompt type:
     'sudo nano /boot/config.txt'
At the bottom of the file add the line:
'dtoverlay=w1-gpio'
Save the file and then reboot.

Replace the temp sensor id in config.xml with the id of your DS18B20 temperature sensor found in the `/sys/bus/w1/devices/` directory on the Raspberry Pi.

Start Putty on Windows and type login name and password.
Program must be run as superuser: Type `sudo bash`
Start program by typing: `python raspibrew`
Next, start the web browser on a computer on your network. If ip address of the Raspberry Pi is `192.168.1.8` then point the browser to `http://192.168.1.8:88` 



# Connect Food Dehydrator to AWS IOT 

AWS IoT Makes Things Smarter  and   IOT Food Dehydrator  will bi smart Food Dehydrator. 

To start with AWS IOT frst install AWS CLI (Ubuntu 14):

    'sudo apt-get update;sudo apt-get install python'
    'sudo apt-get install python-pip'
    'sudo pip install awscli'

To connect  client to AWS, first run config command

    'sudo aws configure'
    
When you are asked, add your keys and region.

AWS Access Key ID [None]: AKIAIèèæYBTZUDMXWFUTA
AWS Secret Access Key [None]: 3Pp9eTt/j0Ahpol37žžèiSuuckmM581LFRUOZfo
Default region name [None]: eu-west-1
Default output format [None]: ENTER

The AWS credentials you configure in the AWS CLI must be the credentials for an IAM user that has permissions to perform IAM and IoT operations used in this quickstart. 

aws iam create-user --user-name Boris
{
    "User": {
        "UserName": "Boris",
        "Path": "/",
        "CreateDate": "2016-01-15T19:03:24.851Z",
        "UserId": "xyDAII32LV6WXXMOM63xy",
        "Arn": "arn:aws:iam::112200121337:user/Boris"
    }
}

## Create a Device in the Thing Registry
To connect a thing to AWS IoT, we  first create a device in the Thing Registry. 

aws iot create-thing --thing-name "FoodDehydrator"
{
    "thingArn": "arn:aws:iot:eu-west-1:112200121337:thing/FoodDehydrator",
    "thingName": "FoodDehydrator"
}


<img src="http://iothome.s3.amazonaws.com/image/awsiot.png" alt="Device"/>

Secure Communication Between a Device and AWS IoT
Communication between a thing and AWS IoT is protected through the use of X.509 certificates 

'aws iot create-keys-and-certificate --set-as-active --certificate-pem-outfile cert.pem --public-key-outfile publicKey.pem --private-key-outfile privateKey.pem'

'aws iot create-keys-and-certificate --set-as-active --certificate-pem-outfile cert.pem --public-key-outfile publicKey.pem --private-key-outfile privateKey.pem'

'aws iot create-policy --policy-name "PubSubFoodDehydratorTopic" --policy-document file://iot-policy'

Attach your Certificate to Your Device
You use the attach-thing-principal CLI command to attach a certificate to a thing. 
'aws iot attach-thing-principal --thing-name "FoodDehydrator" --principal "arn:aws:iot:eu-west-1:112200121337:cert/370c8ccf949787dab6aa7314b5ea4eb2ce016c30418e5bf4b338e06854c86516"'

Verify MQTT Subscribe and Publish
The steps in this section show you how to verify you can use your certificate to communicate with AWS IoT over MQTT. You will use an MQTT client to subscribe and publish to an MQTT topic. MQTT clients require a root CA certificate to authenticate with AWS IoT. Download the root CA certificate file from root certificate.

Install mosquitto:

    'sudo apt-get install mosquitto-clients on debian or
    
Check mosquitto
pi@raspberrypi ~ $ mosquitto_pub -t test -f mqtt/mosquitto/publish.txt -d
Client mosqpub/14824-raspberry sending CONNECT
Client mosqpub/14824-raspberry received CONNACK
Client mosqpub/14824-raspberry sending PUBLISH (d0, q0, r0, m1, 'test', ... (6 bytes))
Client mosqpub/14824-raspberry sending DISCONNECT

Run mosquitto subscriber:

    mosquitto_sub --cafile  $HOME/certificate/root-CA.crt --cert $HOME/fooddehydrator/cert.pem --key  $HOME/fooddehydrator/privateKey.pem  -h "A9HHD5G1IXZ9I.iot.eu-west-1.amazonaws.com" -p 8883 -q 1 -d -t '$aws/things/FoodDehydrator/shadow/update/rejected'


<img src="http://iothome.s3.amazonaws.com/image/sim1.png" alt="Hardware and Software "/>



##Running the temperature control Simulation over AWS IOT 

To tun mosquitto in Node.js to simulate temperature control over AWS IOT(Terminal Window 1) in  Node.js first install:

"npm install mqtt -g"
"npm install minimist"
"node temperature-control_client.js -f ~/certificate "

Check mqtt
"mqtt sub -t 'hello' -h 'test.mosquitto.org' -v"


To run mqtt in python install paho library

"pip install paho-mqtt"

In python you shuld add

import paho.mqtt.client as mqtt

client = paho.Client()
client.on_connect = on_connect
client.connect(“XXXXXYYYYY.iot.eu-west-1.amazonaws.com", port=8883) #AWS IoT service hostname and portno


To send data to AWS S3 in python, you need to install boto library. Boto3   provide native support in Python versions 2.6.5+, 2.7, 3.3, and 3.4.

"pip install boto3"


## How to Start RasPiDry on Boot up:

Create a new file: `/etc/init.d/raspibrew` as superuser and insert the following script:

    #! /bin/sh
    # /etc/init.d/raspidry

    ### BEGIN INIT INFO
    # Provides:          raspidry
    # Required-Start:    $remote_fs $syslog
    # Required-Stop:     $remote_fs $syslog
    # Default-Start:     2 3 4 5
    # Default-Stop:      0 1 6
    # Short-Description: Simple script to start a program at boot
    # Description:       A simple script from www.stuffaboutcode.com which will start / st$
    ### END INIT INFO

    # If you want a command to always run, put it here

    # Carry out specific functions when asked to by the system
    case "$1" in
        start)
            echo "Starting RasPiBrew"
            # run application you want to start
            python /var/www/raspidry.py
        ;;
        stop)
            echo "Stopping RasPiBrew"
            # kill application you want to stop
            killall python
            python /var/www/cleanupGPIO.py
        ;;
    *)
        echo "Usage: /etc/init.d/raspidry {start|stop}"
        exit 1
        ;;
    esac

    exit 0

Make script executable:
    `sudo chmod 755 /etc/init.d/raspibrew`

Register script to be run at start-up:
    `sudo update-rc.d raspibrew defaults`

To Remove script from start-up:
    `sudo update-rc.d -f raspibrew remove`

To test starting the program:
    `sudo /etc/init.d/raspibrew start`

To test stopping the program:
    `sudo /etc/init.d/raspibrew stop`

[Run RasPi Program at Start Up Info](http://www.stuffaboutcode.com/2012/06/raspberry-pi-run-program-at-start-up.html)


###IDE for Development:
 

Install [Eclipse Luna ](http://www.eclipse.org/downloads/packages/release/Luna/R)   on your computer:

This is used for programming in Python, Javascript, web page design and  a synchronization with Raspberry Pi

<img src="http://iothome.s3.amazonaws.com/image/dev.png" alt="Eclipse Luna" width="954 height="776.5" /> 

# Application  Details

The language for the server side software is Python for rapid development.  The web server/framework is web.py.  Multiple processes connected with pipes to communicate between them are used.  For instance, one process can only get the temperature while another turns a heating element on and off.  A third parent temp control process can control the heating process with information from the temp process and relay the information back to the web server.

On the client side jQuery and various plugins can be used to display data such as line charts and gauges. Mouse overs on the temperature plot will show the time and temp for the individual points.  It is currently working in a Firefox and Chrome Browser.   

jQuery and two jQuery plugins (jsGauge and Flot) are used in the client:  
[http://jquery.com](http://jquery.com "jQuery")  
[http://code.google.com/p/jsgauge/](http://code.google.com/p/jsgauge/ "jsgauge")  
[http://code.google.com/p/flot/](http://code.google.com/p/flot/ "flot")  

The PID algorithm was translated from C code to Python.  The C code was from "PID Controller Calculus with full C source source code" by Emile van de Logt
An explanation on how to tune it is from the following web site:  
[http://www.vandelogt.nl/nl_regelen_pid.php](http://www.vandelogt.nl/nl_regelen_pid.php)  

The PID can be tuned very simply via the Ziegler-Nichols open loop method.  Just follow the directions in the controller interface screen, highlight the sloped line in the temperature plot and the parameters are automatically calculated.  After tuning with the Ziegler-Nichols method the parameters still needed adjustment because there was an overshoot of about 2 degrees in my system. I did not want the temperature to go past the setpoint since it takes a long time to come back down. Therefore, the parameters were adjusted to eliminate the overshoot.  For this particular system the Ti term was more than doubled and the Td parameter was set to about a quarter of the open loop calculated value.  Also a simple moving average was used on the temperature data that was fed to the PID controller to help improve performance.  Tuning the parameters via the Integral of Time weighted Absolute Error (ITAE-Load) would provide the best results as described on van de Logt's website above.

## Displaying 

#Dehydrator 

##Dehydrator Equipment

##Dehydrator Hardware Links
 
