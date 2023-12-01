#!/usr/bin/python3

# import general libraries
import json, signal, sys, os, glob, datetime, io
from time import sleep,time
from picamera import PiCamera, Color

#from FluOpti.camera_pi import Camera
from FluOpti.pi_pwm import pi_pwm
from FluOpti.pi_adc import pi_temperature


import threading
from simple_pid import PID

# GPIO setup
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) # set BOARD PIN nomenclature

class FluOpti():
    def __init__(self):

        self._default_modules  = {
                
        #MODULE  #CHANNEL   #VALUE  #STATUS
        
        #CHANNEL refer to related pin conection in the FluOpti Board
        
        'R'    :{ 'chan':5, 'value': 0,'status':0},
        'G'    :{ 'chan':6, 'value': 0,'status':0},
        'B'    :{ 'chan':7, 'value': 0,'status':0},
        'W'    :{ 'chan':8, 'value': 0,'status':0},
        'H1'   :{ 'chan':10, 'value': 0,'status':0},
        'H2'   :{ 'chan':11, 'value': 0,'status':0}
        }
        
        #correct the digital position (digital start from 0 instead of 1)
        for mod in list(self._default_modules.keys()):
            self._default_modules[mod]['chan'] += -1
        
        # GPIO PIN to control directly with the raspberry
        self.GPIO = {         
        #MODULE  #PIN  #STATUS

        'B'    :{ 'pin':37,'status':0}
        }
        
        # define all the PIN as OUT
        for mod in list(self.GPIO.keys()):
            pin = self.GPIO[mod]['pin']
            GPIO.setup(pin, GPIO.OUT)
        
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
        #self.startNTC()
        self.startADC()
    
    def get_chan(self,module):
        chan = self._default_modules[module]['chan']
        return(chan + 1)
        
    def gen_frame(self):
        """Video streaming generator function."""
        while True:
            frame = Camera().get_frame()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def startPWM(self):
        try:
            print('pwm start')
            self.pwm = pi_pwm(0x5c)
            self.pwm_status = True
        except Exception as e:
            print('Problem with the i2c modules')
            self.pwm_status = False
            print(e, flush=True)

    def startADC(self):
        try:
            print('adc start (temp sensor)')
            self.adc = pi_temperature()
            self.adc_status = True
        except  Exception as e:
            print('Problem with the adc module')
            self.adc_status = False
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

    def LEDSetPWR(self,color, p):
        self._default_modules[color]['value'] = p

    def LEDon(self,color):
        self.pwm.set_pwm(self._default_modules[color]['chan'],self._default_modules[color]['value'])
        self._default_modules[color]['status'] = 1

    def LEDoff(self,color): #not change the value stored
        self.pwm.set_pwm(self._default_modules[color]['chan'],0)
        self._default_modules[color]['status'] = 0

    def updateTemps(self):
        self.t1,self.t2 = self.adc.get_temps()
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
        for k in list(self._default_modules.keys()):
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
    
    def add_GPIO(self, module, pin):
        
        self.GPIO[module] = { 'pin': pin,'status':0}
        GPIO.setup(pin, GPIO.OUT)
    
    def pin_control(self, module, state):
        
        pin = self.GPIO[module]['pin']
        
        if state == 0:
            # Turn OFF
            GPIO.output(pin,GPIO.LOW)
            
            #update the state
            self.GPIO[module]['state'] = state
            print('GPIO PIN ' + str(pin) + ' OFF')
            
        elif state == 1:
            #Turn ON
            GPIO.output(pin,GPIO.HIGH)
            
            #update the state
            self.GPIO[module]['state'] = state
            print('GPIO PIN ' + str(pin) + ' ON')
        
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
