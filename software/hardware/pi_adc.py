# Nori
# ASI 2018

"""This module controls an ADC I2C module, model Adafruit ADS1115.
"""

############ IMPLEMENTATION NOTES ##############################################
#
# ADC I2C raspberry pi 3B interface.
# See:
# https://github.com/adafruit/Adafruit_Python_ADS1x15/blob/master/examples/simpletest.py
#
# ------------------------------------------------------------------------------
#
# - 16 bit resolution
# - 4 channels single ended
# - default of 128 samples per second
#
# - I2C address configuration:
#     ADDR PIN CONNECTION     SLAVE ADDRESS
#     GND                     1001000   0x48
#     VDD                     1001001   0x49
#     SDA                     1001010   0x4A
#     SCL                     1001011   0x4B
#
# - Gain:
#   Choose a gain of 1 for reading voltages from 0 to 4.09V.
#   Or pick a different gain to change the range of voltages that are read:
#    - 2/3 = +/-6.144V
#    -   1 = +/-4.096V
#    -   2 = +/-2.048V
#    -   4 = +/-1.024V
#    -   8 = +/-0.512V
#    -  16 = +/-0.256V
#   See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
#
# - Used addresses:
#   - Red board:  0x4B
#   - Blue board: 0x49, 0x48
#
# - Data Rates:
#   Possible data rates: 8, 16, 32, 64, 128 (default), 250, 475, 860
#
#
################################################################################


# ----- Imports ---------------
import sys
import time
import threading

try:
  import Adafruit_ADS1x15
except:
  print("Required module 'Adafruit_ADS1x15' not found !")


N_CHANNELS = 4
default_resistor1 = 10873
default_resistor2 = 10820
default_resistor3 = 10000
default_resistor4 = 10000
# Temperature-ResistorValue table: the index indicates the temperature, starting with 0 deg C with a resistance of 32651 ohms.
# len is 126
temp_array = [  32651, 31031, 29500, 28054, 26687, 25395, 24172, 23016, 21921, 20885,
        19903, 18973, 18092, 17257, 16465, 15714, 15001, 14324, 13682, 13073,
        12493, 11943, 11420, 10923, 10450, 10000, 9572,  9165,  8777,  8408,
        8056,  7721,  7402,  7097,  6807,  6530,  6266,  6014,  5774,  5544,
        5325,  5116,  4916,  4724,  4542,  4367,  4200,  4040,  3887,  3741,
        3601,  3467,  3339,  3216,  3098,  2985,  2877,  2773,  2674,  2579,
        2487,  2399,  2315,  2234,  2157,  2082,  2011,  1942,  1876,  1813,
        1752,  1693,  1637,  1582,  1530,  1480,  1432,  1385,  1341,  1298,
        1256,  1216,  1178,  1141,  1105,  1070,  1037,  1005,  974,   945,
        916,   888,   862,   836,   811,   787,   764,   741,   720,   699,
        678,   659,   640,   622,   604,   587,   571,   555,   539,   524,
        510,   496,   482,   469,   457,   444,   432,   421,   410,   399,
        388,   378,   368,   359,   350,   341  ]
MIN_TEMP_RES = 341    # At 125 deg C
MAX_TEMP_RES = 32651  # At 000 deg C


class adc_module():
  '''Inits I2C module.

  :param address: int, I2C address, example 0x4A
  :param average_n_samples: int, number of samples to average
  :param gain: range of the ADC conversion, see datasheet for details
  '''

  def __init__(self, address=0x49, average_n_samples=5, gain=1,
          r0=default_resistor1, r1=default_resistor2, r2=default_resistor3, r3=default_resistor4):
    self.address = address
    self.GAIN    = gain   # ADC Gain, see notes above
    self.values  = [0] * N_CHANNELS

    # Resistors value
    self.R_0 = [r0, r1, r2, r3]

    self.adc = Adafruit_ADS1x15.ADS1115(address=address, busnum=1)    # ADS1115 16 bit, ADS1015 12 bit
    self.read_all()


  def adc_value_to_volts(self, val, gain=1.0):
    '''Converts adc data to voltage in the range +-4.096/GAIN volts.'''
    volts = val * 4.096 / gain / 2**15     # ADC is 16 bits, that is, 15 bits resolution plus 1 bit for sign. Thus, divide by 2**15
    #volts = val * 4.096 / gain / 2**11      # ADC is 12 bits, that is, 11 bits resolution plus 1 bit for sign. Thus, divide by 2**11
    return volts

  # True reads voltage, False reads temperature
  def read(self, chan=0, voltage_or_temperature=True):
    '''Reads adc data and converts to volts.'''
    adcval = self.adc.read_adc(chan, gain=self.GAIN)  #, data_rate=16)
    # print 'adcval', chan, adcval
    if voltage_or_temperature:
      self.values[chan] = self.adc_value_to_volts( adcval, self.GAIN )
    else:
      self.values[chan] = self.convert_temperature( self.adc_value_to_volts( adcval, self.GAIN ), chan )
    return self.values[chan]

  # True reads voltage, False reads temperature
  def read_all(self, voltage_or_temperature=True):
    '''Read all adc channels.'''
    for i in range(N_CHANNELS):
      self.read(i, voltage_or_temperature)
    return self.values

  def get_temps(self):
    self.read(0,False)
    self.read(1,False)
    return [self.values[0],self.values[1]]

  def convert_temperature(self, adc_in_v, r_idx):
    # print 'v', r_idx, adc_in_v
    # Calculate sensor resistance
    # Pull-up mode:   R_T = R_0 * (Vcc/Vadc - 1)
    # Pull-down mode: R_T = R_0 / (Vcc/Vadc - 1)
    vcc = 3.3
    ## Pull-up mode
    #resistance = float(self.R_0[r_idx]) * (vcc/adc_in_v - 1);
    # Pull-down mode
    resistance = float(self.R_0[r_idx]) / (vcc/adc_in_v - 1);

    # Lookup temperature table
    # If out of bounds, return -1
    if resistance < MIN_TEMP_RES or resistance > MAX_TEMP_RES:
      return -1

    # Search resistore range
    r0 = -1
    r1 = -1
    for i in range(len(temp_array)):
      if resistance <= temp_array[i]   and   resistance >= temp_array[i+1]:
        r0 = temp_array[i]
        r1 = temp_array[i+1]
        break
    if r0 < 0:
      return -1

    # Linear interpolation
    return ((resistance-r0) / (r1-r0))  + i




# --------------- Testing  -------------------------
if __name__ == '__main__':
  print('Testing ADC\n')

  if len(sys.argv) > 1:
    addr = int(sys.argv[1], 16)
  else:
    addr = 0x4A

  print('Init with address ' + hex(addr))
  adc = adc_module(addr)
  print('\tinit done !\n')

  print('Reading ADS1115 values, press Ctrl-C to quit...')
  print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*range(N_CHANNELS)))
  print('-' * 37)

  while True:
    adc.read_all(voltage_or_temperature=False)
    print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*adc.values))
    time.sleep(0.5)
