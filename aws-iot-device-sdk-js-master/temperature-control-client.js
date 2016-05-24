/*
 * Copyright 2010-2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */

//node.js deps

//npm deps

//app deps
const blessed = require('blessed');
const contrib = require('blessed-contrib');
const thingShadow = require('./').thingShadow;
const isUndefined = require('./common/lib/is-undefined');
const cmdLineProcess   = require('./lib/cmdline');

/*
testMode=1

var express=require ('express')
var app=express()
app.get('/', function(req,res) {
  res.send('hello world')
})
var server=app.listen(3000,function() {
 console.log('server run at '+server.address().port)
})
*/

function processTest( args ) {
//
// Construct user interface
//


var screen = blessed.screen( { enableInput: true });

screen.title = 'AWS IoT Food Dehydrator Temperature Control Simulation';

var grid = new contrib.grid( { rows: 8, cols: 12, screen: screen } );

//
// The Food Dehydrator Temperature control device's control state contains:
//
//   setPoint - If enabled, heat will be transferred between the interior
//              and exterior until the interior temperature equals this
//              value
//
//              Type: Integer
//              Units: Degrees Celsius
//              Read/Write
//
//    enabled - Operational status of heat transfer device
//
//              Type: Boolean
//              Units: N/A
//              Read/Write
var deviceControlState={ setPoint: 42, enabled: true , option:5, end:3600};


var items={options:[
            {name:"herbs",id:1, ends:333,setpoint:35},            
            {name:"Raising Bread",id:2, ends:633,setpoint:26}, 
            {name:"Making Yougurt",id:3, ends:533,setpoint:43}, 
            {name:"Vegetable",id:4, ends:4333,setpoint:40}, 
            {name:"Fruit leather",id:5, ends:3333,setpoint:42}, 
            {name:"Fruit",id:6, ends:4333,setpoint:48}]};

items={"options":[
            {"name":"herbs","id":1, "ends":333},            
            {"name":"Raising Bread","id":2, "ends":633}, 
            {"name":"Making Yougurt","id":3, "ends":533}, 
            {"name":"Vegetable","id":4, "ends":4333}, 
            {"name":"Fruit leather","id":5, "ends":3333}, 
            {"name":"Fruit","id":6, "ends":4333}]};
var options=[333,633,533,4333,3333,4333]
var setpoint=[35,26,43,40,42,48]
//
// The Food Dehydrator Temperature control device's monitor state contains:
//
//
//    intTemp - Interior temperature
//
//              Type: Integer
//              Units: Degrees Fahrenheit
//              Read Only
//
//    extTemp - Exterior temperature
//
//              Type: Integer
//              Units: Degrees Fahrenheit
//              Read Only
//
//   curState - Current state of heat transfer device
//
//              Type: Enum (heating|cooling|stopped)
//              Units: N/A
//              Read Only
//
var deviceMonitorState={ intTemp: 42, extTemp: 25, curState: 'stopped' , fromstart:333};

var networkEnabled=true;

var lcd1 = grid.set( 1, 1, 2, 3, contrib.lcd, {
label: 'Setpoint',
    segmentWidth: 0.06,
    segmentInterval: 0.11,
    strokeWidth: 0.1,
    elements: 3,
    elementSpacing: 4,
    elementPadding: 2, color: 'green'
 
} );

var lcd2 = grid.set( 3, 1, 2, 3, contrib.lcd, { 
label: 'Interior',
    segmentWidth: 0.06,
    segmentInterval: 0.11,
    strokeWidth: 0.1,
    elements: 3,
    elementSpacing: 4,
    elementPadding: 2, color: 'white'
} );

var lcd3 = grid.set( 5, 1, 2, 3, contrib.lcd, { 
label: 'Exterior',
    segmentWidth: 0.06,
    segmentInterval: 0.11,
    strokeWidth: 0.1,
    elements: 3,
    elementSpacing: 4,
    elementPadding: 2, color: 'white'
} );

var lcd4 = grid.set( 3, 4, 2, 3, contrib.lcd, { 
label: 'Status',
    segmentWidth: 0.06,
    segmentInterval: 0.11,
    strokeWidth: 0.1,
    elements: 3,
    elementSpacing: 4,
    elementPadding: 2, color: 'white'
} );

var lcd5 = grid.set( 5, 4, 2, 3, contrib.lcd, { 
label: 'Network',
    segmentWidth: 0.06,
    segmentInterval: 0.11,
    strokeWidth: 0.1,
    elements: 3,
    elementSpacing: 4,
    elementPadding: 2, color: 'white'
} );

var lcd6 = grid.set( 1, 4, 2, 3, contrib.lcd, {
label: 'Options',
    segmentWidth: 0.06,
    segmentInterval: 0.11,
    strokeWidth: 0.1,
    elements: 3,
    elementSpacing: 3,
    elementPadding: 1, color: 'white'
} );

var lcd7 = grid.set( 5, 7, 2, 5, contrib.lcd, { 
label: 'Duty cycle',
    segmentWidth: 0.06,
    segmentInterval: 0.11,
    strokeWidth: 0.1,
    elements: 4,
    elementSpacing: 2,
    elementPadding: 2, color: 'white'
} );

var lcd8 = grid.set( 3, 7, 2, 5, contrib.lcd, { 
label: 'Run Duty cycle in min',
    segmentWidth: 0.06,
    segmentInterval: 0.11,
    strokeWidth: 0.1,
    elements: 4,
    elementSpacing: 2,
    elementPadding: 2, color: 'white'
} );

var log = grid.set( 1, 7, 2, 5, contrib.log, {
label: 'Log'
} );

screen.key(['escape', 'q', 'C-c'], function(ch, key) {
// if exit, then process stopped  
  if (networkEnabled)
   {
      deviceControlState.enabled='stopped'
      opClientToken = thingShadows.update('FoodDehydratorTemperatureControl', { state: { desired: deviceControlState } });
   }
  return process.exit(0);
});

lcd1.setDisplay(deviceControlState.setPoint+'C');
lcd2.setDisplay(deviceMonitorState.intTemp+'C');
lcd3.setDisplay(deviceMonitorState.extTemp+'C');
lcd4.setDisplay(deviceControlState.enabled===true?' ON':'OFF');
lcd5.setDisplay(networkEnabled===true?' ON':'OFF');
lcd6.setDisplay(deviceControlState.option);
lcd7.setDisplay(deviceControlState.end);
lcd8.setDisplay(deviceMonitorState.fromstart);

screen.render();

//
// The thing module exports the thing class through which we
// can register and unregister interest in thing shadows, perform
// update/get/delete operations on them, and receive delta updates
// when the cloud state differs from the device state.
//
const thingShadows = thingShadow({
  keyPath: args.privateKey,
  certPath: args.clientCert,
  caPath: args.caCert,
  clientId: args.clientId,
  region: args.region,
  reconnectPeriod: args.reconnectPeriod
});

var opClientToken;

var title;
if (args.testMode === 2)
{
title = blessed.text( {
   top: 0,
   left: 'center',
   align: 'center',
   content: 'DEVICE SIMULATOR'
} );
}
else
{
title = blessed.text( {
   top: 0,
   left: 'center',
   align: 'center',
   content: 'MOBILE APPLICATION SIMULATOR'
} );
}
var help = blessed.text( {
   top: 1,
   left: 'left',
   align: 'left',
   content: 'Options:1-herbs|2-Raising Bread|3-Making Yougurt|4-Vegetables|5-Fruit leather|6-Fruits(use arrow keys to change temp,use u/d keys to change options)'
} );

var bar = blessed.listbar({
  //parent: screen,
  bottom: 0,
  left: 'center',
//  right: 3,
  height: 'true' ? 'shrink' : 3,
//  mouse: true,
  keys: true,
  autoCommandKeys: false,
  border: 'line',
  vi: true,
  style: {
    bg: 'black',
    item: {
      bg: 'black',
      hover: {
        bg: 'blue'
      }
    },
    selected: {
      bg: 'blue'
    }
  },
  commands: {
    'mode': {
      callback: function() {
        var enabledStatus=( deviceControlState.enabled===true?'OFF':' ON');
        deviceControlState.enabled=(deviceControlState.enabled===true?false:true);
        log.log('Food Dehydrator Temperature control '+(deviceControlState.enabled?'enabled':'disabled'));

        if (networkEnabled===true)
        {
           opClientToken = thingShadows.update('FoodDehydratorTemperatureControl', { state: { desired: deviceControlState } });
        }
        lcd4.setDisplay( enabledStatus );
        screen.render();
      }
    },
    'network': {
      callback: function() {
        var networkStatus=( networkEnabled===true ? 'OFF' : ' ON');
        networkEnabled=( networkEnabled===true ? false : true);
        lcd5.setDisplay( networkStatus );
        log.log( 'network '+(networkEnabled?'connected':'disconnected'));
//
// Simulate a network connection/disconnection 
//
        if (networkEnabled)
        {
           thingShadows.setConnectionStatus(true);

//
// After re-connecting, try to update with our current state; this will
// get a 'rejected' status if another entity has updated this thing shadow
// in the meantime and we will have to re-sync.
//
           thingShadows.update( 'FoodDehydratorTemperatureControl', { state: { desired: deviceControlState } } );
        }
        else
        {
           thingShadows.setConnectionStatus(false);
        }
        screen.render();
      }
    },
    'exit': {

      callback: function() {
        if (networkEnabled)
        {
           deviceControlState.enabled='stopped'
           opClientToken = thingShadows.update('FoodDehydratorTemperatureControl', { state: { desired: deviceControlState } });
        }
        process.exit(0);
      }
    }
  }
});

screen.append(bar);
screen.append(help);
screen.append(title);

bar.focus();
screen.key('up', function( ch, key ) {
if (deviceControlState.setPoint < 57)
{
   deviceControlState.setPoint++;
   lcd1.setDisplay(deviceControlState.setPoint+'C');
   if (networkEnabled===true)
   {
      opClientToken = thingShadows.update('FoodDehydratorTemperatureControl', { state: { desired: deviceControlState } });
   }
   screen.render();
}
});
screen.key('down', function( ch, key ) {
if (deviceControlState.setPoint > 33)
{
   deviceControlState.setPoint--;
   deviceControlState.end=options[deviceControlState.option-1]
   lcd1.setDisplay(deviceControlState.setPoint+'C');
   if (networkEnabled===true)
   {
      opClientToken = thingShadows.update('FoodDehydratorTemperatureControl', { state: { desired: deviceControlState } });
   }
   screen.render();
}
});
//TODO https://github.com/chjj/blessed
//https://github.com/chjj/blessed
screen.key('u', function( ch, key ) {
if (deviceControlState.option < 6)
{
   deviceControlState.option++;
   deviceControlState.setPoint=setpoint[deviceControlState.option-1]+'C';
   deviceControlState.end=options[deviceControlState.option-1];
   lcd1.setDisplay(deviceControlState.setPoint);
   lcd6.setDisplay(deviceControlState.option);
   lcd7.setDisplay(deviceControlState.end);
   log.log('Food Dehydrator Temperature control '+deviceControlState.option+' '+deviceControlState.end);
   if (networkEnabled===true)
   {
      opClientToken = thingShadows.update('FoodDehydratorTemperatureControl', { state: { desired: deviceControlState } });
   }
   screen.render();
}
});

screen.key('d', function( ch, key ) {
if (deviceControlState.option > 1)
{
   deviceControlState.option--;
   deviceControlState.setPoint=setpoint[deviceControlState.option-1]+'C';
   deviceControlState.end=options[deviceControlState.option-1];
   lcd1.setDisplay(deviceControlState.setPoint);
   lcd6.setDisplay(deviceControlState.option);
   lcd7.setDisplay(deviceControlState.end);
   log.log('Food Dehydrator Temperature control '+deviceControlState.option+' '+deviceControlState.end);
   if (networkEnabled===true)
   {
      opClientToken = thingShadows.update('FoodDehydratorTemperatureControl', { state: { desired: deviceControlState } });
   }
   screen.render();
}
});



//
// Simulate the interaction of a mobile application and a remote device via the
// AWS IoT service.  The simulated remote device is a temperature controller.
// Two thing shadows are used: one for control properties (setpoint and on/off) 
// and the other for monitoring properties (interior/exterior temperature, current
// state).
//
thingShadows
  .on('connect', function() {
    log.log('connected to AWS IoT...');

    thingShadows.register( 'FoodDehydratorTemperatureControl', { 
                                              persistentSubscribe: true } );
    thingShadows.register( 'FoodDehydratorTemperatureStatus', { 
                                              persistentSubscribe: true } );
    log.log('registered thing shadows...');
//
// After registering, wait for a few seconds and then ask for the
// current state of the thing shadow.
//
    setTimeout( function() {
       opClientToken = thingShadows.get('FoodDehydratorTemperatureControl');
    }, 2000 );
    });

thingShadows 
  .on('close', function() {
    thingShadows.unregister( 'FoodDehydratorTemperatureControl' );
    thingShadows.unregister( 'FoodDehydratorTemperatureStatus' );
    log.log('close');
  });

thingShadows 
  .on('reconnect', function() {
    log.log('reconnect/re-register');
//
// Upon reconnection, re-register our thing shadows.
//
    thingShadows.register( 'FoodDehydratorTemperatureControl', { 
                                              persistentSubscribe: true } );
    thingShadows.register( 'FoodDehydratorTemperatureStatus', { 
                                              persistentSubscribe: true } );
//
// After re-registering, wait for a few seconds and then try to update
// with our current state
//
    setTimeout( function() {
       opClientToken = thingShadows.update('FoodDehydratorTemperatureControl', { state: { desired: deviceControlState } });
    }, 2000 );
  });

thingShadows 
  .on('offline', function() {
    log.log('offline');
  });

thingShadows
  .on('error', function(error) {
    log.log('error', error);
  });

thingShadows
  .on('message', function(topic, payload) {
    log.log('message', topic, payload.toString());
  });

thingShadows
  .on('status', function(thingName, statusType, clientToken, stateObject) {
      if ((networkEnabled===true) && (statusType === 'rejected'))
      {
//
// If an operation is rejected it is likely due to a version conflict;
// request the latest version so that we synchronize with the thing
// shadow.  The most notable exception to this is if the thing shadow
// has not yet been created or has been deleted.
//
         if (stateObject.code !== 404)
         {
            log.log('resync with thing shadow');
            opClientToken = thingShadows.get(thingName);
         }
      }
      if (statusType === 'accepted')
      {
         if (thingName==='FoodDehydratorTemperatureControl')
         {
            deviceControlState = stateObject.state.desired;
            lcd1.setDisplay(deviceControlState.setPoint+'C');
            lcd4.setDisplay(deviceControlState.enabled===true?' ON':'OFF');
            screen.render();
         }
      }
  });

thingShadows
  .on('delta', function(thingName, stateObject) {
      if (networkEnabled===true)
      {
         if (thingName==='FoodDehydratorTemperatureControl')
         {
            if (!isUndefined(stateObject.state.enabled) && 
                (stateObject.state.enabled !== deviceControlState.enabled))
            {
               log.log('FoodDehydratorTemperature control '+(stateObject.state.enabled?'enabled':'disabled'));
            }
            deviceControlState=stateObject.state;
            lcd1.setDisplay(deviceControlState.setPoint+'C');
            lcd4.setDisplay(deviceControlState.enabled===true?' ON':'OFF');
         }
         else if (thingName==='FoodDehydratorTemperatureStatus')
         {
            if (!isUndefined(stateObject.state.intTemp))
            {
               deviceMonitorState.intTemp=stateObject.state.intTemp;
            }
            if (!isUndefined(stateObject.state.extTemp))
            {
               deviceMonitorState.extTemp=stateObject.state.extTemp;
            }
            if (!isUndefined(stateObject.state.curState))
            {
               deviceMonitorState.curState=stateObject.state.curState;
            }
            if (!isUndefined(stateObject.state.fromstart))
            {
               deviceMonitorState.fromstart=stateObject.state.fromstart;
            }
         }
         screen.render();
      }
  });

//
// If we are acting in the device simulation role, we simulate the
// action of the heat transfer device here.
//
   if (args.testMode === 2)
   {
      var transferRate = 0.1;  // degrees Fahrenheit/second
      var leakRate = 0.005;     // degrees Fahrenheit/second
      var interiorTemp = deviceMonitorState.intTemp;

      setInterval( function() {
         var difference;
//
// If the device is enabled, the internal temperature will move towards
// the setpoint; otherwise, it will move towards the external temperature.
//
         if (deviceControlState.enabled)
         {
            difference=deviceMonitorState.intTemp-deviceControlState.setPoint;
         }
         else
         {
            difference=deviceMonitorState.intTemp-deviceMonitorState.extTemp;
         }
         interiorTemp -= (difference * transferRate);
         interiorTemp -= leakRate;
         deviceMonitorState.intTemp = Math.floor(interiorTemp);
         if (deviceControlState.enabled)
         {
            if (difference > transferRate)
            {
               deviceMonitorState.curState = 'cooling';
            }
            else if (difference < -transferRate)
            {
               deviceMonitorState.curState = 'heating';
            }
            else
            {
               deviceMonitorState.curState = 'stopped';
            }
         }
         else
         {
            deviceMonitorState.curState = 'stopped';
         }
         if (networkEnabled===true)
         {
            opClientToken = thingShadows.update('FoodDehydratorTemperatureStatus', 
                                { state: { desired: deviceMonitorState } });
         }
      }, 1000 );
   }
//
// The interior temperature LCD also displays the status of the heat
// transfer device.
//
   setInterval( function() {
      var displayOptions = { color: 'white' };
      if (deviceMonitorState.curState === 'cooling')
      {
         displayOptions = { color: 'cyan' };
      }
      else if (deviceMonitorState.curState === 'heating')
      {
         displayOptions = { color: 'red' };
      }
      else if (deviceMonitorState.curState === 'false')
      {
         displayOptions = { color: 'yellow' };
      }
      lcd2.setDisplay(deviceMonitorState.intTemp+'C');
      lcd3.setDisplay(deviceMonitorState.extTemp+'C');
      lcd8.setDisplay(deviceMonitorState.fromstart);
      lcd2.setOptions( displayOptions );
      screen.render();
   }, 250 );
}

module.exports = cmdLineProcess;

if (require.main === module) {
  cmdLineProcess('connect to the AWS IoT service and demonstrate thing shadow APIs, test modes 1-2',
                 process.argv.slice(2), processTest );
}
