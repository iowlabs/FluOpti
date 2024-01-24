#!/usr/bin/python3

# import general libraries
import json, signal, sys, os, glob, datetime, io
from time import sleep,time
from picamera import PiCamera, Color

#from FluOpti.camera_pi import Camera
from hardware.pi_pwm import pwm_module
from hardware.pi_adc import adc_module
from hardware.pi_ntc import ntc_module

import threading
from simple_pid import PID

class fluOpti():
    def __init__(self, type = "normal"):

		self.type = type # normal =  FluOpti ; mini =  miniFluOpti
		if self.type == "normal":
        	self._default_modules  = {
        	#Alias 	  #CHANNEL    #VALUE  #status
        	'R'    :{ 'chan':6, 'value': 0,'status':0},
        	'G'    :{ 'chan':7, 'value': 0,'status':0},
        	'B'    :{ 'chan':8, 'value': 0,'status':0},
        	'W'    :{ 'chan':9, 'value': 0,'status':0},
        	'H1'   :{ 'chan':10, 'value': 0,'status':0},
        	'H2'   :{ 'chan':11, 'value': 0,'status':0}
        	}
		if self.type == "mini":
			self._default_modules  = {
        	#MODULE  #CHANNEL    #VALUE
        	'R'    :{ 'chan':5, 'value': 0,'status':0},
        	'G'    :{ 'chan':4, 'value': 0,'status':0},
        	'B'    :{ 'chan':3, 'value': 0,'status':0},
        	'W'    :{ 'chan':2, 'value': 0,'status':0},
        	'H1'   :{ 'chan':0, 'value': 0,'status':0},
        	'H2'   :{ 'chan':1, 'value': 0,'status':0}
        	}
        #data data path
        self.data_path = "/data"

        #Temperature control parameters
        self.t1 = 0.0
        self.t2 = 0.0
        self.tsp1 = 0.0
        self.tsp2 = 0.0
        self.t_pwr1 = 0
        self.t_pwr2 = 0
        self.temp_ctrl_run = False
        self.temp_ctrl_update_time = 5 # in sec

        #PID modules to control temperature
        self.pid_temp1 = PID(1,0.1,0.05,setpoint = 1)
        self.pid_temp2 = PID(1,0.1,0.05,setpoint = 1)

        self.pid_temp1.output_limits = (0,100)
        self.pid_temp2.output_limits = (0,100)

        self.pid_temp1.setpoint      = self.tsp1
        self.pid_temp2.setpoint      = self.tsp2

        #Temp threading
        self.temp_thread = None

        # Start hardware components
        self.camera_status = False
        #self.startCamera()

        self.startPWM()
		self.startTemperatureSensor()


                for prop in input_props:

                    input_value = properties[prop]
                    module_value = mod_i[prop]

                    # if any property value doesn´t match, module_i is not selected
                    if input_value != module_value:
                        selected = False

                if selected:

                    selected_modules.append(m_name)

            if len(selected_modules) == 0 and msj:
                print('\nThere is no modules with the given characteristics\n')

            return(selected_modules)


    def gen_frame(self):
        """Video streaming generator function."""
        while True:
            frame = Camera().get_frame()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def startPWM(self):
        try:
            self.pwm = pwm_module(0x5c)
            self.pwm_status = True
			print('pwm module initialized')
        except Exception as e:
            print('Problem with the i2c modules')
            self.pwm_status = False
            print(e, flush=True)

    def startTemperatureSensor(self):
        try:
			if self.type == "normal":
				self.temp_sensor = adc_module()
			elif self.type == "mini":
				self.temp_sensor = ntc_module()
			else:
				print('Error undefined type')

			print('temperature sensor module initialized')
			self.temp_status = True

        except  Exception as e:
            print('Problem with the temperature sensor module')
            self.temp_status = False
            print(e, flush=True)

	def startCamera(self):
        try:
            print("Starting camera", flush=True)
            try: self.camera.close()
            except: pass
            self.camera = PiCamera()
            self.camera_status = True
        except Exception as e:
            self.camera_status = False
            print(e, flush=True)

	"""
	This function updates the power value of a channel in the global dictionary
	args: 	color 	= the channel to update ;
			p 		= a value between 0 to 100 for the power.
	"""
    def LEDSetPWR(self,color, p):
        self.modules[color]['value'] = p

	"""
	Turns on a given channel with the last power value set in the global dictionary.
	args: 	color 	= the channel to turn on ;

	"""
    def LEDon(self,color):
        self.pwm.set_pwm(self._default_modules[color]['chan'],self._default_modules[color]['value'])
        self._default_modules[color]['status'] = 1

	"""
	Turns off a given channel without losing the last power value set in the global dictionary.
	args: 	color 	= the channel to turn on ;

	"""
    def LEDoff(self,color): #not change the value stored
        self.pwm.set_pwm(self._default_modules[color]['chan'],0)
        self._default_modules[color]['status'] = 0

	"""
	updates the temperature readings from the sensor module.
	"""
    def updateTemps(self):
        self.t1,self.t2 = self.temp_sensor.get_temps()
        #print(f"t1: {self.t1},\t t2: {self.t2} ")
        return self.t1,self.t2

    def startTempCtrl(self) :
        self.temp_ctrl_run = True
        self.temp_thread = threading.Thread(target = self.tempCtrl,)
        self.temp_thread.deamon = True
        self.temp_thread.start()
        self.temp_thread.join(0.1)


    def stopTempCtrl(self):
        self.temp_ctrl_run = False
        self.LEDoff('H1')
        self.LEDoff('H2')

    def setTempSP(self, ch,new_tsp):
        if ch == 1:
            self.t_sp1 = new_tsp
            self.pid_temp1.setpoint = self.t_sp1
            print(f"new temperature setpoint {self.t_sp1}°C added on channel {ch}")
        elif ch == 2:
            self.t_sp2 = new_tsp
            self.pid_temp2.setpoint = self.t_sp2
            print(f"new temperature setpoint {self.t_sp2}°C added on channel {ch}")
        else:
            print("error")

    def setTempSampleTime(self, new_time):
        self.temp_ctrl_update_time = new_time

    def tempCtrl(self):
        while self.temp_ctrl_run ==  True :
            self.updateTemps()
            self.t_pwr1 = self.pid_temp1(self.t1)
            self.t_pwr2 = self.pid_temp2(self.t2)
            self.LEDSetPWR('H1',self.t_pwr1)
            self.LEDSetPWR('H2',self.t_pwr2)
            self.LEDon('H1')
            self.LEDon('H2')
            print(f"CH1 - t:\t{self.t1} tsp:\t{self.t_sp1} pwr :\t{self.t_pwr1}\nCH2 - t:\t{self.t2} tsp:\t{self.t_sp2} pwr :\t{self.t_pwr2}")
            sleep(self.temp_ctrl_update_time)

    def takePicture(self, led,end=False, preview_time = 5, speed = 100000, _contrast = 0, res = [960,600]):
        for k in list(self.modules.keys()):
            if k == led:
                self.LEDon(k)
            else:
                self.LEDoff(k)
        self.camera.resolution = res
        self.camera.start_preview()
        sleep(preview_time)
        self.camera.shutter_speed = speed
        self.camera.contrast = _contrast
        self.photo_counter  += 1
        self.photo_output   = self.photo_path + led +str(self.photo_counter)+'.jpg'
        self.camera.capture(file_output_photo)

    def add_channel(self, module, channel, board = 'FluOpti'):
        # board = 'FluOpti' or 'RPI_GPIO'

        self.modules[module] = {'board': board,'chan': channel, 'value': 0, 'status':0}

        if board == 'RPI_GPIO':
            GPIO.setup(channel, GPIO.OUT)
            print('\nModule '+ str(module) + 'set as output in GPIO '+str(channel)+ '\n')

    def GPIO_control(self, module, status, msj = True):

        pin = self.modules[module]['chan']

        if status == 0:
            # Turn OFF
            GPIO.output(pin,GPIO.LOW)

            #update the status
            self.modules[module]['status'] = status

            if msj == True:
                print('\nGPIO Pin ' + str(pin) + ' (module '+ str(module) +') turned OFF')

        elif status == 1:
            #Turn ON
            GPIO.output(pin,GPIO.HIGH)

            #update the status
            self.modules[module]['status'] = status

            if msj == True:
                print('\nGPIO Pin ' + str(pin) + ' (module '+ str(module) +') turned ON')

        else:

            print('Invalid GPIO state. It have to be 0 or 1')

    ''' Clean exit '''
    def close(self, *args):
        try:
            self.camera.close()
        except Exception as e:
            print(e, flush=True)

# --------------- Testing  -------------------------
if __name__ == '__main__':

    print('Testing miniFluo\n')
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
        Fluopti.LEDSetPWR('B',prcnt)
        Fluopti.LEDon('B')
        sleep(5)
    #Fluo.stopTempCtrl()
    Fluopti.LEDoff('B')
