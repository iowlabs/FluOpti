# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 18:56:25 2024

@author: Prosimios
"""

# import FluOpti library
from hardware.FluOpti import FluOpti

# Initial messages
print('\nTurning LEDs OFF...\n')



Fluopti =  FluOpti()

leds = Fluopti.get_modules(m_type = 'LED')

for led in leds:
        
        # turn OFF
        Fluopti.module_switch(led, 'OFF', msg = True)
        
print('\nAll LEDs turned OFF successfully\n')

