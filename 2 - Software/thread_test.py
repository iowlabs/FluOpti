# -*- coding: utf-8 -*-
import time
import threading
import os

from FluOpti import pi_pwm
from FluOpti import pi_adc

MODE_MANUAL = 1
MODE_AUTO   = 2
MODE_DEBUGG = 3

N_channels = 4



class FluOpti():

  _default_modules  = {
    #MODULE  #CHANNEL
  'LED_1':{ 'chan':0, 'value': 0, 'time':0},
  'LED_2':{ 'chan':1, 'value': 0, 'time':0},
  'LED_3':{ 'chan':2, 'value': 0, 'time':0},
  'LED_4':{ 'chan':3, 'value': 0, 'time':0},

  'LED_5':{ 'chan':4, 'value': 0, 'time':0},
  'LED_6':{ 'chan':5, 'value': 0, 'time':0},
  'LED_7':{ 'chan':6, 'value': 0, 'time':0},
  'LED_8':{ 'chan':7, 'value': 0, 'time':0},

  'LED_B'   :{ 'chan':8, 'value': 0, 'time':0},
  'LED_W'   :{ 'chan':9, 'value': 0, 'time':0},
  'HEATER_1':{ 'chan':10, 'value': 0, 'time':0},
  'HEATER_2':{ 'chan':11, 'value': 0, 'time':0},

  'PWM_1':{ 'chan':4, 'value': 0, 'time':0},
  'PWM_2':{ 'chan':5, 'value': 0, 'time':0},
  'PWM_3':{ 'chan':6, 'value': 0, 'time':0},
  'PWM_4':{ 'chan':7, 'value': 0, 'time':0}
  }

  def __init__(self):

    self.mode = MODE_MANUAL

    try:
        self.pwm = pi_pwm.pi_pwm(0x5c)
        self.adc = pi_temperature.pi_temperature()
    except:
        print('Problem with the i2c modules')
        quti()

  def set_module(self,module,level,t_exp):
      if not module in self._default_modules:
          print('Module not in the FluOpti\'s modules')
          return False
      if level < 0 or level > 100:
          print('Try with a porcentaje level (0..100)')
          return False

      self._default_modules[module]['value'] = level
      self._default_modules[module]['time']  = t_exp

  def set_modules_off(self):
    self.pwm.set_all(0)

  def set_modules_on(self):
      for key in self._default_modules:
          self.pwm.set_pwm(self._default_modules[key]['chan'],self._default_modules[key]['value'])

  def pwm_routine(self,t_exp):
      self.set_modules_on()
      time.sleep(t_exp)
      self.set_modules_off()

  def read_temperature(self):
      print('Reading ADS1115 values, press Ctrl-C to quit...')
      print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*range(N_CHANNELS)))
      print('-' * 37)
      while 1:
          self.adc.read_all(voltage_or_temperature=False)
          print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*adc.values))
          time.sleep(0.5)

  def run(self,t_exp):
     PWM = threading.Thread(target = self.pwm_routine, args = (t_exp,))
     ADC = threading.Thread(target = self.read_temperature)
     PWM.start()
     ADC.start()


if __name__ == '__main__':

  flu = FluOpti()

  flu.set_module('LED_B', 50,10)
  flu.set_module('LED_W', 50,10)
  flu.set_module('LED_1', 80,10)
  flu.set_module('LED_2', 80,10)
  flu.set_module('HEATER_1', 10,10)
  flu.set_module('HEATER_2', 10,10)

  flu.run(20)
