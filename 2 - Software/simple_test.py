# -*- coding: utf-8 -*-
import time
import sys
from time import sleep
import threading
import os

from FluOpti.FluOpti import FluOpti


print('Testing Fluo\n')
Fluopti =  FluOpti()
print('Testing PWM, press Ctrl-C to quit...')
# [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
seq = list(range(0,101,10))
#seq.extend( list(range(90,-1,-10)) )
Fluopti.setTempSampleTime(1)
Fluopti.setTempSP(1,30)
Fluopti.setTempSP(2,35)
#miniFluo.startTempCtrl()
for prcnt in seq:
    sys.stdout.flush()
    print(f"seteando color azul a {prcnt} \%" )
    Fluopti.LEDSetPWR('B',prcnt)
    Fluopti.LEDon('B')
    sleep(1)
#Fluo.stopTempCtrl()
Fluopti.LEDoff('B')
