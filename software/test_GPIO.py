# -*- coding: utf-8 -*-
"""
Created on Nov 2023

@author: Prosimios
"""


# Import general packages
import time
import sys
from time import sleep
import threading
import os


# GPIO setup
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD) # set BOARD PIN nomeclature

BASE_PIN = 37           # conected PIN
GPIO.setup(BASE_PIN, GPIO.OUT)

    
# import FluOpti library
from FluOpti.FluOpti import FluOpti


Fluopti =  FluOpti()

# Initial messages
print('\nTesting FluOpti\n')
print('Testing PWM and GPIO, press Ctrl-C to quit...')

####  PWM percentage list to be tested #####
# [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
power = [30,50,100]
#seq.extend( list(range(90,-1,-10)) )

#### Temperature control setpoint ### 
Fluopti.setTempSampleTime(1)
Fluopti.setTempSP(1,30)
Fluopti.setTempSP(2,35)
#miniFluo.startTempCtrl()


### Channels definition ####
print('\nNote: you can run this code with the list of channels to be tested as an input\n')

#default values
channel = 'R'

if len(sys.argv) > 1:
    try:
        # Channels should be separated by ','
        channels = sys.argv[1].split(',')
        print('\n**Testing input channels**\n')
    except:

        print('Some parameter(s) seems to be invalid...')
        print ('It should be a list separated by ","')
        sys.exit()

else:
    print ('\n**Testing default channels**\n')


## Test GPIO ###
    

GPIO.output(BASE_PIN,GPIO.HIGH)
print('GPIO PIN ' + str(BASE_PIN).split('_')[0] + ' ON')


# -- Testing channels -- #
    
position = Fluopti.get_chan(channel)
print('\nCanal '+ channel +' in position '+ str(position)+':\n')
    
for prcnt in power:
    sys.stdout.flush()
    print("Seteando color "+ channel +f" al {prcnt} %" )
    Fluopti.LEDSetPWR(channel,prcnt)
    Fluopti.LEDon(channel)
    sleep(3)

## Turn OFF the FLuOpti Channel    
Fluopti.LEDoff(channel)
print("Canal "+ channel +" OFF" )    


# Turn OFF the GPIO PIN
GPIO.output(BASE_PIN,GPIO.LOW)
print('GPIO PIN ' + str(BASE_PIN).split('_')[0] + ' OFF')


#Fluo.stopTempCtrl()