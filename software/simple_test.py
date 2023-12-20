# -*- coding: utf-8 -*-
import time
import sys
from time import sleep
import threading
import os

from hardware.FluOpti import fluOpti


print('Testing Fluo\n')
Fluopti =  fluOpti()
print('Testing PWM, press Ctrl-C to quit...')
# [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
seq = list(range(0,101,10))
#seq.extend( list(range(90,-1,-10)) )
Fluopti.setTempSampleTime(1)
Fluopti.setTempSP(1,30)
Fluopti.setTempSP(2,35)
#miniFluo.startTempCtrl()
# -- Testing channel BLUE
for prcnt in seq:
    sys.stdout.flush()
    print(f"seteando color azul a {prcnt} %" )
    Fluopti.LEDSetPWR('B',prcnt)
    Fluopti.LEDon('B')
    sleep(1)
Fluopti.LEDoff('B')
# -- Testing channel RED
for prcnt in seq:
    sys.stdout.flush()
    print(f"seteando color rojo a {prcnt} %" )
    Fluopti.LEDSetPWR('R',prcnt)
    Fluopti.LEDon('R')
    sleep(1)
Fluopti.LEDoff('R')
# -- Testing channel Blue
for prcnt in seq:
    sys.stdout.flush()
    print(f"seteando color Verde a {prcnt} %" )
    Fluopti.LEDSetPWR('G',prcnt)
    Fluopti.LEDon('G')
    sleep(1)
Fluopti.LEDoff('G')
for prcnt in seq:
    sys.stdout.flush()
    print(f"seteando color Blanco a {prcnt} %" )
    Fluopti.LEDSetPWR('W',prcnt)
    Fluopti.LEDon('W')
    sleep(1)
Fluopti.LEDoff('W')
for prcnt in seq:
    sys.stdout.flush()
    print(f"seteando todos los  canales a {prcnt} %" )
    Fluopti.LEDSetPWR('G',prcnt)
    Fluopti.LEDSetPWR('B',prcnt)
    Fluopti.LEDSetPWR('W',prcnt)
    Fluopti.LEDSetPWR('R',prcnt)
    Fluopti.LEDon('G')
    Fluopti.LEDon('B')
    Fluopti.LEDon('W')
    Fluopti.LEDon('R')
    sleep(1)
#Fluo.stopTempCtrl()
Fluopti.LEDoff('G')
Fluopti.LEDoff('R')
Fluopti.LEDoff('W')
Fluopti.LEDoff('B')
