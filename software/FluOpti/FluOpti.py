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

        self.modules = {
                
        #MODULE #BOARD #CHANNEL   #VALUE  #STATUS
        
        #CHANNEL refer to related pin conection in the FluOpti Board or Raspberry Pi GPIO Pin
        
        'R'    :{ 'board': 'FluOpti', 'chan':5, 'value': 0,'status':0, 'type': 'LED'},
        'G'    :{ 'board': 'FluOpti','chan':6, 'value': 0,'status':0, 'type': 'LED'},
        'B'    :{ 'board': 'RPI_GPIO','chan':37, 'value': 0,'status':0, 'type': 'LED'},
        'W'    :{ 'board': 'FluOpti','chan':8, 'value': 0,'status':0, 'type': 'LED'},
        'H1'   :{ 'board': 'FluOpti','chan':10, 'value': 0,'status':0, 'type': 'Heater'},
        'H2'   :{ 'board': 'FluOpti','chan':11, 'value': 0,'status':0, 'type': 'Heater'}
        }
        
        
        for mod in list(self.modules.keys()):
            
            #correct the digital position (digital start from 0 instead of 1)
            
            if self.modules[mod]['board'] == 'FluOpti':
                # perform the correction just for FluOpti board
                self.modules[mod]['chan'] += -1
                
            # define all the RPi GPIO pin as OUT
            elif self.modules[mod]['board'] == 'RPI_GPIO':
                
                pin = self.modules[mod]['chan']
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
        chan = self.modules[module]['chan']
        return(chan + 1)
        
    def get_on_channels(self, mod_type = None):
        # return a list with the names of channels in ON state (state == 1)
        # you can specify an specific module type (e.g. 'LED', 'Heater', 'Sensor')
        
        on_channels = list()
        
        if mod_type == None:
            #obtain all the ON channels
            for m_name in list(self.modules.keys()):
                mod = self.modules[m_name]
                
                if mod['status'] == 1:
                    on_channels.append(m_name)
            
            return(on_channels)
        
        else:
            # get a specific type of channels
            try:
                for m_name in list(self.modules.keys()):
                    
                    mod = self.modules[m_name]
                    
                    if mod['status'] == 1 and mod['type'] == mod_type:
                        
                        on_channels.append(m_name)
                
                return(on_channels)
            
            except:
                print('[Error] input an invalid channel type')
                
        
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
        self.modules[color]['value'] = p

    def LEDon(self,color, msj = True):
        
        power = self.modules[color]['value']
        
        self.pwm.set_pwm(self.modules[color]['chan'],power)
        self.modules[color]['status'] = 1
        
        if msj == True:
            print("Channel "+ color +f" turned ON at {power} %" )

    def LEDoff(self,color, msj = True): 
        # It doesn't change the stored value
        self.pwm.set_pwm(self.modules[color]['chan'],0)
        self.modules[color]['status'] = 0
        
        if msj == True:
            print("\nChannel "+ color +" turned OFF" )

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
    
    def GPIO_control(self, module, state, msj = True):
        
        pin = self.modules[module]['chan']
        
        if state == 0:
            # Turn OFF
            GPIO.output(pin,GPIO.LOW)
            
            #update the state
            self.modules[module]['state'] = state
            
            if msj == True:
                print('\nGPIO Pin ' + str(pin) + ' (module '+ str(module) +') turned OFF')
            
        elif state == 1:
            #Turn ON
            GPIO.output(pin,GPIO.HIGH)
            
            #update the state
            self.modules[module]['state'] = state
            
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
