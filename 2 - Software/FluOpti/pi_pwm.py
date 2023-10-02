"""
This module controls a PWM I2C module, model Adafruit PCA9685.

"""

############ IMPLEMENTATION NOTES ##############################################
#
# PWM I2C raspberry pi interface.
# See:
#	https://github.com/adafruit/Adafruit_Python_PCA9685/blob/master/examples/simpletest.py
#	https://learn.adafruit.com/adafruit-16-channel-servo-driver-with-raspberry-pi/library-reference
#
# ------------------------------------------------------------------------------
#
# - 12 bit resolution
# - Frequency from 40 to 1000 Hz (according to the lib)
# - 16 channels
#
# - Addresses:
#	- default address:	0x5C
#
################################################################################


# ----- Imports ---------------
import sys
import time
import threading

try:
	import Adafruit_PCA9685
except:
	print("Required module 'Adafruit_PCA9685' not found !")


# ----- Global Variables ---------------
N_CHANNELS = 16


class pi_pwm():

	def __init__(self, address=0x5c):
		self.address = address

		self.pwm = Adafruit_PCA9685.PCA9685(address=address, busnum=1)
		self.pwm.set_pwm_freq(1000)		# Set frequency to 1kHz (max)
		self.set_all(0)


	def set_pwm(self, chan, pwm_level_percentage):
		'''Sets pwm duty-cycle value on selected channel.'''
		if pwm_level_percentage < 0 or pwm_level_percentage > 100:
			print('pwm_level_percentage must be in range 0..100 (%i given)' % pwm_level_percentage)

		p = int( float(pwm_level_percentage)/100.0 * 4095 )
		if p < 0:
			p = 0
		if p > 4095:
			p = 4095

		self.pwm.set_pwm(chan, 0, p)
		return p

	def set_all(self, pwm_level_percentage):
		'''Sets all duty-cycles at once.'''
		for chan in range(N_CHANNELS):
			self.set_pwm(chan, pwm_level_percentage)




# --------------- Testing  -------------------------
if __name__ == '__main__':
	print('Testing PWM\n')

	if len(sys.argv) > 1:
		addr = int(sys.argv[1], 16)
	else:
		addr = 0x5C

	print('Init with address ' + hex(addr))
	pwm = pi_pwm(addr)
	print('\tinit done !\n')

	print('Testing PWM, press Ctrl-C to quit...')

	# [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
	seq = range(0,101,10)
	seq.extend( range(90,-1,-10) )

	while True:
		for prcnt in seq:
			print(prcnt)
			sys.stdout.flush()
			pwm.set_all(prcnt)
			time.sleep(0.5)
