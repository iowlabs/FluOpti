# -*- coding: utf-8 -*-

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
print('Testing PWM, press Ctrl-C to quit...')

####  PWM percentage list to be tested #####
# [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
seq = list(range(0,101,10))
#seq.extend( list(range(90,-1,-10)) )

#### Temperature control setpoint ### 
Fluopti.setTempSampleTime(1)
Fluopti.setTempSP(1,30)
Fluopti.setTempSP(2,35)
#miniFluo.startTempCtrl()


### Channels definition ####
print('\nNote: you can run this code with the list of channels to be tested as an input\n')

#default values
channels = ['B','R','G','W']

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


# -- Testing channels -- #
    
for c in channels:
    position = Fluopti.get_chan(c)
    print('\nChannel '+ c +' in position '+ str(position)+':\n')
    
    c_board = Fluopti.modules[c]['board']  # board where channel is connected
    
    if c_board == 'FluOpti':    
        for prcnt in seq:
            sys.stdout.flush()
            
            Fluopti.LEDSetPWR(c,prcnt)
            Fluopti.LEDon(c)
            sleep(1)
            
        Fluopti.LEDoff(c)
        
    elif c_board == 'RPI_GPIO':
        
        # turn ON --> state = 1
        Fluopti.GPIO_control(c, state = 1)
        sleep(3)
        
        # turn OFF --> state = 0
        Fluopti.GPIO_control(c, state = 0)
    
    else:
        print('Indefined action for board '+ c_board +' of channel '+ str(c) +'\n')

#Fluo.stopTempCtrl()

