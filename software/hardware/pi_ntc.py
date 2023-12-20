"""
This module read of an NTC temperature sensor through the integrated MAX6682

"""

############ IMPLEMENTATION NOTES ##############################################
#
# NTC SPI raspberry pi interface.
#
# https://learn.sparkfun.com/tutorials/raspberry-pi-spi-and-i2c-tutorial/all
# https://pypi.org/project/spidev/
# ------------------------------------------------------------------------------
#
# - 10 bit resolution
# - Frequency from up to 5MHz
# - Sample time 0.5Hz
# - 2 channels
#
################################################################################


# ----- Imports ---------------
import spidev
import time

# ----- Global Variables ---------------
BUS = 0
BYTES = 2

class ntc_module():
    def __init__(self):
        self.temps = [0.0,0.0]
        self.data  = [3, 248]
        self.data_bites = ""
        self.sig        = ""
        self.integer    = ""
        self.decimal    = ""
        self.temp_m     = 	1.1797
        self.temp_n     =	26.147
        self.spi_sensors = [spidev.SpiDev(),spidev.SpiDev()]
        self.spi_sensors[0].open(BUS,0)
        self.spi_sensors[1].open(BUS,1)
        self.spi_sensors[0].max_speed_hz = 5000000
        self.spi_sensors[1].max_speed_hz = 5000000
        self.spi_sensors[0].mode = 0
        self.spi_sensors[1].mode = 0

    def get_temp(self,ch):
        #read temp from sensor 1
        self.data = self.spi_sensors[ch].xfer2([0x00, 0x00 ])
        self.data_bites = "{0:0>8b}".format(self.data[0])+"{0:0>8b}".format(self.data[1])

        self.sig      = self.data_bites[0]
        self.integer  = self.data_bites[1:8]
        self.decimal  = self.data_bites[8:11]

        temp = (1-2*int(self.sig,2) ) * int(self.integer,2)+int(self.decimal,2)*0.125
        temp =  self.temp_m * temp + self.temp_n
        return temp

    def get_temps(self,ch=-1):
        if ch ==0:
            return [self.get_temp(0),0]
        if ch ==1:
            return [0,self.get_temp(1)]
        if ch ==-1:
            return [self.get_temp(0),self.get_temp(1)]

    def twos_comp(val, bits):
        """compute the 2's complement of int value val"""
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
            return val

# --------------- Testing  -------------------------
if __name__ == '__main__':
  print('Testing PW\n')

  print('Init ntc')
  ntc = ntc_module()
  print('\tinit done !\n')

  print('Reading temps')
  print('Reading CH0:')
  while 1:
      print(ntc.get_temps())
      time.sleep(2)
  #print('Reading CH1:')
  #print(ntc.get_temps(1))
  #print('Reading both:')
  #print(ntc.get_temps())
