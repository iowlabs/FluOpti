# -*- coding: utf-8 -*-
"""
Created on Dec 2023

@author: Prosimios
"""

# -*- coding: utf-8 -*-

# Import general packages
import time
import sys
from time import sleep
import threading
import os

# import FluOpti library
from hardware.FluOpti import FluOpti


Fluopti =  FluOpti()

#################################################################
######### Functions #############################################

def indicate_leds(options, str_options):
    
    valid = False
    
    while not valid:
        
        input_leds = input('\nEnter the channel(s) name(s) to turn ON separated by "," '
                          +'(options = '+ str_options +') : ')
        
        input_leds = input_leds.split(',')
        
        for led in input_leds:
            
            valid = False
            
            for name in options:
                
                if led == name:
                    valid = True
                    break
            
            if not valid:
                print (led + ' not in ['+ str_options +'].\n')
                break       
                    
        if not valid:
            print ('[Error] - Invalid input. They have to be from ['+ str_options +'].\n')
                
    return(input_leds)

def turnON(leds, power):
    
    for led in leds:
        
        Fluopti.LEDSetPWR(led, power)
    
    Fluopti.module_switch(leds, 'ON')
####################################################################
#######   Rutine ###################################################

# Initial messages
print('\nTesting FluOpti\n')


## power definition
if len(sys.argv) > 1:
    
    try:
        power = int(sys.argv[1])
        if power >= 0 and power <= 100:
            print('\nPower of channels defined at '+sys.argv[1]+'% PWM\n')
        
        else:
    
            print('Invalid power input...Default 100% PWM power will be used.')
            power = 100
    except:
        print('Invalid power input...Default 100% PWM power will be used.')
        power = 100
else:
    print ('\nDefault 100% PWM power will be used')
    power = 100
    


### Channels definition ####

mtype = 'LED'

options = Fluopti.get_modules(m_type = mtype)

# create a string with the options to display in text
str_options = ''

for c in options:
    
    str_options= str_options + c + "," 

# LEDs input by the user

input_leds = indicate_leds(options, str_options)

# -- Turning ON -- 
turnON(input_leds, power)

# -- Turning OFF --
leds_on = Fluopti.get_modules(m_type = mtype, status = 1, msg = False) # list of LEDs in ON state

str_ledons = ''

while len(leds_on) > 0:
    
    for led_name in leds_on:
    
        str_ledons = str_ledons + str(led_name) + ","
    
    print('Current LED(s) in ON state: '+ str_ledons+'\n')    
    leds_off = input('Turn OFF? (indicate the channel(s) separated by ","): ').split(',')
    
    Fluopti.module_switch(leds_off, 'OFF')
    
    #update the list of leds in ON state
    leds_on = Fluopti.get_modules(m_type = mtype, status = 1, msg = False)
    str_ledons = ''

print('\nAll LED channels turned OFF.\nProgram Finished\n')


