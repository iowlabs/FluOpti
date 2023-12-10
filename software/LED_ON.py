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
from FluOpti.FluOpti import FluOpti


Fluopti =  FluOpti()

#################################################################
######### Functions #############################################

def indicate_leds(options, str_options):
    
    valid = False
    
    while not valid:
        
        input_leds = input('\nEnter the channel(s) name(s) separated by "," '
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

def turn_on(leds):

    for led in leds:
        
        c_board = Fluopti.modules[led]['board']  # board where channel is connected
        
        if c_board == 'FluOpti':    
                sys.stdout.flush()
                
                # turn ON at defined power
                Fluopti.LEDSetPWR(led,power)
                Fluopti.LEDon(led)
            
        elif c_board == 'RPI_GPIO':
            
            # turn ON --> state = 1
            Fluopti.GPIO_control(led, state = 1)
            
        else:
            print('Indefined action for board '+ c_board +' of channel '+ str(led) +'\n')


def turn_off(leds):

    for led in leds:
        
        c_board = Fluopti.modules[led]['board']  # board where channel is connected
        
        if c_board == 'FluOpti':    
            sys.stdout.flush()
            
            # turn OFF
            Fluopti.LEDoff(led)
            
        elif c_board == 'RPI_GPIO':
            
            # turn OFF --> state = 0
            Fluopti.GPIO_control(led, state = 0)
            
        else:
            print('Indefined action for board '+ c_board +' of channel '+ str(led) +'\n')

####################################################################
#######   Rutine ###################################################

# Initial messages
print('\nTesting FluOpti\n')


## power definition
if len(sys.argv) > 1:
    
    try:
        power = int(sys.argv[1])
        if power >= 0 and power <= 100:
            print('\nChannel power defined at '+sys.argv[1]+'% PWM\n')
        
        else:
    
            print('Invalid input...Default 100% PWM power will be used.')
            power = 100
    except:
        print('Invalid input...Default 100% PWM power will be used.')
        power = 100
else:
    print ('\nDefault 100% PWM power will be used')
    power = 100
    


### Channels definition ####

options = list()
for mod in list(Fluopti.modules.keys()):
    if Fluopti.modules[mod]['type'] == 'LED':
        options.append(mod)

# create a string with the options to display in text
str_options = ''

for c in options:
    
    str_options= str_options + c + "," 

# LEDs input by the user

input_leds = indicate_leds(options, str_options)

# -- Turning ON -- 
turn_on(input_leds)


# -- Turning OFF --
leds_on = Fluopti.get_on_channels(mod_type = 'LED') # list of LEDs in ON state

str_ledons = ''

while len(leds_on) > 0:
    
    for led_name in leds_on:
    
        str_ledons = str_ledons + str(led_name) + ","
    
    print('Current LED(s) in state ON: '+ str_ledons)    
    leds_off = input('Turn OFF? (indicate the channel(s) separated by ","): ').split(',')
    
    turn_off(leds_off)
    
    #update the list of leds in ON state 
    leds_on = Fluopti.get_on_channels(mod_type = 'LED')
    str_ledons = ''



