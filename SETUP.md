#Installation of iSPRESSO software on Raspberry Pi

##Installation of Raspberry PI / Debian - Raspbian

<http://elinux.org/RPi_Easy_SD_Card_Setup>


##Get Wireless up and running:

Edit /etc/network/interfaces, remove what™s there, and add:

```
auto lo
iface lo inet loopback
iface eth0 inet dhcp
allow-hotplug wlan0
auto wlan0
iface wlan0 inet dhcp
  wpa-ssid "ssid"
  wpa-psk "password"
```

##Setup Zeroconfig:

Set a clever  hostname from the raspi-config or using "hostname" executable.  Your system will broadcast its 
name on your local network as hostname.local for avahi (linux) or bonjour (apple) aware clients.

```
sudo apt-get install avahi-daemon
```

##Setting up Python:

```
sudo apt-get update
sudo apt-get install python-dev python-setuptools python-pip git
sudo pip install web.py
sudo pip install simplejson
sudo easy_install -U distribute
```

To enable i2c:

```
sudo apt-get install python-smbus
```

Comment out lines in:
/etc/modprobe.d/raspi-blacklist.conf

To enable temp sensor and i2c, add lines to /etc/modules:

for i2c
```
i2c-bcm2708
i2c-dev
```

To enable 1-wire temp sensor, modprobe these, and add to /etc/modules:

```
w1-gpio
w1-therm
```

To enable 1-wire humidity temp sensor DHT22 install Adafruit library
https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/wiring

git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
To install the Python library on either the Raspberry Pi
sudo apt-get update
sudo apt-get install build-essential python-dev python-openssl
sudo python setup.py install

cd examples
Now to run the example on a Raspberry Pi with an AM2302 sensor connected to GPIO #4, execute:
sudo ./AdafruitDHT.py 2302 4

Note:.For DHT11 and DHT22 sensors, don't forget to connect a 4.7K - 10K resistor from the data pin to VCC


Instaling boto library to connect to AWS S3

$ pip install boto
Install from source:

    $ git clone git://github.com/boto/boto.git
    $ cd boto
    $ python setup.py install
    
Installing paho library to connect to AWS IOT

$sudo pip install paho-mqtt

##Downloading code from GIT:

Create www directory, and clone the code:

```
sudo mkdir /var/www
cd /var/www

sudo git clone https://veggiebenz@bitbucket.org/veggiebenz/pyspresso.git

 # move stuff up one directory, to /var/www/
cd pyspresso
shopt -s dotglob
sudo cp * .. -R
cd ..
shopt -u dotglob
sudo rm -rf pyspresso
 # change ownership of files
sudo chown pi * -R
sudo chgrp pi * -R

 # set up the init script
sudo cp ./initscript/ispresso /etc/init.d/
sudo chmod +x /etc/init.d/ispresso
sudo update-rc.d ispresso defaults
```

##Now on to the wiring!

![Fritzing breadboard diagram](http://bitbucket.org/veggiebenz/pyspresso/raw/master/img/ispresso2_bb.png)



