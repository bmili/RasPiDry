#!/usr/bin/python

import RPi.GPIO as GPIO
import xml.etree.ElementTree as ET

tree = ET.parse('config.xml')
xml_root = tree.getroot()

gpioNumberingScheme = xml_root.find('GPIO_pin_numbering_scheme').text.strip()
if gpioNumberingScheme == "BOARD":
        GPIO.setmode(GPIO.BOARD)
else:
	 GPIO.setmode(GPIO.BCM)
		
GPIO.setwarnings(False)

GPIO.setup(4, GPIO.IN)
GPIO.setup(21, GPIO.IN)
GPIO.setup(22, GPIO.IN)
GPIO.setup(23,GPIO.IN)
print (GPIO.input(4))
print (GPIO.input(21))
print (GPIO.input(22))
print (GPIO.input(23))

GPIO.setup(4, GPIO.OUT)
GPIO.output(4,  GPIO.LOW)
GPIO.setup(21, GPIO.OUT)
GPIO.output(21,  GPIO.LOW)
GPIO.setup(22, GPIO.OUT)
GPIO.output(22,  GPIO.LOW)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23,  GPIO.LOW)
print (GPIO.input(4))
print (GPIO.input(21))
print (GPIO.input(22))
print (GPIO.input(23))
GPIO.cleanup()

