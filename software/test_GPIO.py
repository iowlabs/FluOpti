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
        
        channel = sys.argv[1]
        print('\n**Testing input channel**\n')
    except:

        print('input parameter seems to be invalid...')
        print ('It should be a string')
        sys.exit()

else:
    print ('\n**Testing default channels**\n')


## Test GPIO ###
GPIO_module = 'B'
#Fluopti.add_channel(module_name, pin_number, board = 'RPI_GPIO')  #to add a new GPIO pin to be controled

# Turn ON  --> status = 1
Fluopti.GPIO_control(GPIO_module, 1)

# -- Testing channels -- #
    
position = Fluopti.get_chan(channel)
print('\nChannel '+ channel +' in position '+ str(position)+':\n')
    
for prcnt in power:
    sys.stdout.flush()
    Fluopti.LEDSetPWR(channel,prcnt)
    Fluopti.LEDon(channel)
    sleep(3)

## Turn OFF the FLuOpti Channel    
Fluopti.LEDoff(channel)

# Turn OFF the GPIO PIN --> status = 0
Fluopti.GPIO_control(GPIO_module, 0)


#Fluo.stopTempCtrl()