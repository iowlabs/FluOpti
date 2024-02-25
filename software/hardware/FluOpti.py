#!/usr/bin/python3

# import general libraries
import json, signal, sys, os, glob, datetime, io
from time import sleep, time, localtime
import numpy as np
from picamera2 import Picamera2, Preview
from PIL import Image
from pprint import pprint
#from picamera import PiCamera, Color #Pruebas en IOWLABS con Raspi 4 genera errores

#from FluOpti.camera_pi import Camera #Esta libreria no esta en la carpeta
#from FluOpti.pi_pwm import pi_pwm
#from FluOpti.pi_adc import pi_temperature

#correcion de importacion de elementos
from hardware.pi_pwm import pwm_module
from hardware.pi_adc import pi_temperature
from hardware.pi_ntc import ntc_module

import threading
from simple_pid import PID

# GPIO setup
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) # set BOARD PIN nomenclature

## Fluoti class and functions
class FluOpti():
    def __init__(self, model = "normal"):

        self.board_model = model        # It is important for temperature sensor functions and default modules.
        
        if self.board_model == 'normal':
            
            # Default modules
            self.modules = {
            #MODULE_NAME  #BOARD           #CHANNEL  #VALUE    #STATUS  
            'R'    :{ 'board': 'FluOpti' , 'chan':5, 'value': 0, 'status':0, 'm_type': 'LED'},
            'G'    :{ 'board': 'FluOpti' , 'chan':6, 'value': 0, 'status':0, 'm_type': 'LED'},
            'B'    :{ 'board': 'FluOpti', 'chan':9,'value': 100, 'status':0, 'm_type': 'LED'},
            'W'    :{ 'board': 'FluOpti' , 'chan':10, 'value': 100, 'status':0, 'm_type': 'LED'},
            'H1'   :{ 'board': 'FluOpti' , 'chan':11,'value': 0, 'status':0, 'm_type': 'Heater'},
            'H2'   :{ 'board': 'FluOpti' , 'chan':12,'value': 0, 'status':0, 'm_type': 'Heater'},
            '37'    :{ 'board': 'GPIO','chan':37, 'value': 100,'status':0, 'm_type': 'LED'}
        	}
            ## ** CHANNEL refers to related pin connection in the FluOpti Board or Raspberry Pi GPIO Pin
            
        if self.board_model == 'mini':
            
            # Default modules
            self.modules  = {
            #MODULE_NAME   #BOARD               #CHANNEL  #VALUE    #STATUS
            'R'    :{ 'board': 'FluOpti' , 'chan':5, 'value': 0,'status':0, 'm_type': 'LED'},
            'G'    :{ 'board': 'FluOpti' , 'chan':4, 'value': 0,'status':0, 'm_type': 'LED'},
            'B'    :{ 'board': 'FluOpti' , 'chan':3, 'value': 0,'status':0, 'm_type': 'LED'},
            'W'    :{ 'board': 'FluOpti' , 'chan':2, 'value': 0,'status':0, 'm_type': 'LED'},
            'H1'   :{ 'board': 'FluOpti' , 'chan':0, 'value': 0,'status':0, 'm_type': 'Heater'},
            'H2'   :{ 'board': 'FluOpti' , 'chan':1, 'value': 0,'status':0, 'm_type': 'Heater'}
            }


        for mod in list(self.modules.keys()):
            #correct the digital position (digital start from 0 instead of 1)
            if self.modules[mod]['board'] == 'FluOpti':
                # perform the correction just for FluOpti board
                self.modules[mod]['chan'] += -1
            # define all the RPi GPIO pin as OUT
            elif self.modules[mod]['board'] == 'GPIO':

                pin = self.modules[mod]['chan']
                GPIO.setup(pin, GPIO.OUT)

        #data path
        self.data_path = '/data'
        
        # list of parameters to set from input file
        self.autotest = True
        self.date = 'automatic'
        
        self.total_time = 0
        self.control_leds = ['R','G']
        self.control_heaters = ['H1']
        
        
        #schedule control regimes --> typically obtained from setting file
        self.sch = dict()        
        self.sch['times'] = {
                'th': [24,48],   # schedule module time limits
                }
        
        self.sch['leds'] = {
                'R': [100,0],   # R light power percetage in each schedule module
                'G': [0,100]    # G light power percetage in each schedule module
                }
        self.css = 0            # current schedule step number
        
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
        
        #Timelapse parameters
        self.cicle = 0          # current cicle
        self.time = {
                'init' : 0, # to store the time at the begginig of the timelapse
                'cicle_init' : 0, # time from the beggining of the cicle
                'cicle_end' : 0, #to store the time to finish the current cicle
                'cicle' : 0 # time per cicle
                } 
        
        # Start hardware components
        self.camera_status = False

        self.startPWM()
        self.startTemperatureSensor()
    
    def get_setting_parameters(self, settings):
        """
        This function transform the information read from input file to
        FluOpti parameters attributes values.
        It corrects the type() of values, assign them to propper attributes and so on.
        """
        # match between backend parameters and input file parameters names:
        # backen_name = input_file_string_name 
        date = 'date'
        autotest = 'autotest'
        total_time = 'total_time'
        update_freq = 'update_frequency'
        display_t0 = 'display_t0'
        modules = 'mod_'
        control_modules = 'control_modules'
        control_times = 'control_times'
        control_value = 'control_value'
        camera_controls = 'cc_'
        camera_options = 'co_' 
        
        #use strip to remove leading and trailing whitespaces from parameters
        
        # cuando lea los schedule segments, tiene que subdividirlos de acuerdo al más pequeño.
        
        
        #date
        date_value = settings[date].strip()
        if date_value == 'automatic':
            
            ltime = localtime()
            self.date = f'{ltime[2]}_{ltime[1]}_{ltime[0]}'
        
        else:
            self.date = date_value
        
    def init_timer(self, tpc):
        # tpc = time per cicle in seconds
        
        self.time['init'] = time()  # the init of the timelapse in seconds
        self.time['cicle'] = tpc
        self.time['cicle_end'] = tpc
        
    def check_timer(self):
        #return true if the end of the cicle time was reached
        
        t0 = self.time['init']
        tf = self.time['cicle_end']
        elapsed = time() - t0
        
        if elapsed < tf:
            return(True)
        
        else:
            
            #update the cicle end time
            self.time['cicle_end'] = (self.cicle + 1) * self.time['cicle']
            return(False)
    
    def update_power(self):
        # to update the optogenetic LEDs power accord the schedule
        for led in self.sch['leds'].keys():
            
            power = self.sch['leds'][led][self.css]
            self.LEDSetPWR(led,power)
    
    def opto_ON(self):
        #turn ON the optogenetics light control
        for led in self.sch['leds'].keys():
            
            self.module_switch(led, 'ON', msg = True)
    
    def update_schedule(self, t_key = 'ts'):
        # Check the schedule time
        t0 = self.time['init']
        
        if time() - t0 > self.sch['times'][t_key][self.css]:
            
            # go to next schedule step
            self.css += 1
            
            #update and turn ON the proper optogenetics lights
            self.update_power()
            self.opto_ON()
        
    def get_chan(self,name):
        # return the phisical channel conection of a module
        chan = self.modules[name]['chan']
        return(chan + 1)


    def get_modules(self, msg = True, **properties):
        '''
        To get the list with the name of all the present modules on self
        or a subset based on the properties of its modules.
        e.g: get_modules('m_type'='LED', 'status' = 1) will retrieve the
        list of LED modules in ON state.
        '''

        mod_names = list(self.modules.keys())
        input_props = list(properties.keys())

        # if no properties were indicated --> return the full list of modules names
        if len(input_props) == 0:
            return(mod_names)

        else:
            ##################
            # check if input properties are defined in modules

            #use the fist module as reference (it asume all have the same property classes)
            fluopti_props = list(self.modules[mod_names[0]].keys())

            for prop in input_props:
                if prop not in fluopti_props:

                    print('[Error] - Property "' + str(prop) + '" not present in all the modules')
                    exit()

            #######################
            # Select the modules based on the given properties and its values
            selected_modules = list()

            for m_name in mod_names:

                mod_i = self.modules[m_name]

                selected = True

                for prop in input_props:

                    input_value = properties[prop]
                    module_value = mod_i[prop]

                    # if any property value doesn´t match, module_i is not selected
                    if input_value != module_value:
                        selected = False

                if selected:

                    selected_modules.append(m_name)

            if len(selected_modules) == 0 and msg:
                print('\nThere is no modules with the given characteristics\n')

            return(selected_modules)
    
    def check_sch(self):
        
        n_modules = len(self.sch['times']['th']) # number of schedule modules

        for key in self.sch['leds'].keys():
            m_number = len(self.sch['leds'][key])
            
            if m_number != n_modules:
                print("\n[Fatal Error] - Optogenetics Schedule definition lengths doesn't match\n")
                sys.exit()

    def gen_frame(self):
        """Video streaming generator function."""
        while True:
            frame = Camera().get_frame()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def startPWM(self):
        try:
            print('pwm start')
            self.pwm = pwm_module(0x5c)
            self.pwm_status = True
        except Exception as e:
            print('Problem with the i2c modules')
            self.pwm_status = False
            print(e, flush=True)

    def startTemperatureSensor(self):
        try:
            if self.board_model == "normal":
                self.temp_sensor = pi_temperature()
            elif self.board_model == "mini":
                self.temp_sensor = ntc_module()
            else:
                print('Error undefined FluOpti board model')

            print('temperature sensor module initialized')
            self.temp_status = True

        except  Exception as e:
            print('Problem with the temperature sensor module')
            self.temp_status = False
            print(e, flush=True)

    def startCamera(self):
        try:
            print("\nStarting camera\n", flush=True)
            try: self.camera.close()
            except: pass
            #init the camera object
            self.camera = Picamera2()
            self.camera_status = True
            
        except Exception as e:
            self.camera_status = False
            print(e, flush=True)
    
    def setCamera(self, fpath = False, mode_number = 3, 
                  configuration_values = False, capture_options = False):
        # to set the camera configurations
        # fpath = full path of txt file to store the camera configuration values
        
        try:
            try:
                camera = self.camera
            except:
                # start camera object if neccesary
                self.startCamera()
                
            modes = camera.sensor_modes
            mode = modes[mode_number]
            print('\nSelected sensor mode properties:')
            pprint(mode)
            
            print('\n')
            
            msize = mode['size']
            mformat = mode['format']
            
            # use default configuration values in case they were not indicated
            if type(configuration_values) != dict:
                
                configuration_values = {
                # high resolution still configuration  
                                                    #(min, max, default_value)
                'AeConstraintMode': 0,                  #(0, 3, 0) - AEC/AGC constrain mode - 0 = Normal
                'AeEnable': False,                      #(False, True, None) - When if is False ( = AEC/AGC off), there will be no automatic updates to the camera’s gain or exposure settings
                'AeExposureMode': 0,                    #(0, 3, 0) - 0 = normal exposures, 1 = shorter exposures, 2 = longer exposures, 3= custom exposures
                'AeMeteringMode': 0,                    #(0, 3, 0) - Metering mode for AEC/AGC
                'AnalogueGain': 1,                      #(1.0, 10.666666984558105, Undefined) - Analogue gain applied by the sensor
                'AwbEnable': False,                     #(False, True, None) When it is False (AutoWhiteBalance off), there will be no automatic updates to the colour gains
                'AwbMode': 0,                           #(0, 7, 0)
                'Brightness': 0.0,                      #(-1.0, 1.0, 0.0) - (-1.0) is very dark, 1.0 is very brigh
                'ColourGains': (1,1),                   #tuple (red_gain, blue_gain), each value: (0.0, 32.0, Undefined) - Setting these numbers disables AWB.
                'Contrast': 1.0,                        #(0.0, 32.0, 1.0) -  zero means "no contrast", 1.0 is the default "normal" contrast
                'ExposureTime': 10000,                   #(75, 11766829, Undefined). unit microseconds.
                'ExposureValue': 0.0,                   #(-8.0, 8.0, 0.0) - Zero is the base exposure level. Positive values increase the target brightness, and negative values decrease it 
                'FrameDurationLimits': (47183,11767556),   # tuple, each value: (47183, 11767556, Undefined). The maximum and minimum time that the sensor can take to deliver a frame (microseconds). Reciprocal of frame rate
                'NoiseReductionMode': 0,                #(0, 4, 0) - 0 is off.
                'Saturation': 1.0,                      #(0.0, 32.0, 1.0) - zero greyscale images, 1.0 "normal" saturation, higher values for more saturated colours.
                'ScalerCrop': (0, 2, 3280, 2460),       #((0, 0, 64, 64), (0, 0, 3280, 2464), (0, 2, 3280, 2460)) - to use just a sub part of the sensor area: (x_offset, y_offset, width, height)
                'Sharpness': 0.0                        #(0.0, 16.0, 1.0)} - zero no additional sharpening, 1.0 is "normal" level of sharpening, larger values apply proportionately stronger sharpening
                }
            
            capture_config = camera.create_still_configuration(
                    controls=configuration_values,
                    main={'size': msize},
                    raw ={'format': mformat}
                    ) 

            # AEC/AGC = Automatic Exposure Control/Automatic Gain Control Mode
            
            # assign the configuration
            camera.configure(capture_config)
            
            # use the default configurations in case capture options were not indicated
            if type(capture_options) != dict:
                capture_options = {
               
                'quality': 90,                #JPEG quality level, 90 is default, 0 is the worst quality and 95 is best
                'compress_level': 1           #PNG compression level, where 0 gives no compression, 1 is the fastest that actually does any compression, and 9 is the slowest

                }
            
            # Asssign the capture options
            for option in capture_options.keys():
                camera.options[option] = capture_options[option]          
 
            
            #save the camera and sensor mode properties to a file:
            # These are not the capture configurations
            if type(fpath) == str:
                cam_props = camera.camera_configuration()
                
                with open(fpath, 'w') as f:
                    
                    for key in cam_props.keys():
                        f.write(str(key)+': ')
                        f.write(str(cam_props[key])+'\n')        
                     
        # in case something fails at camera configuration                
        except Exception as e:
    
            print(e, flush=True)
            print('\n[Error]Fail to configure the camera\n')
    
    def im_capture(self, impath, n_imgs = 1, mfpath = False, printm = False, display = False):
        # to capture an image
        # mfpath: filename/path to store the metadata
        
        camera = self.camera
        
        ## Capture the image
        request = camera.capture_request()
        im_array = request.make_array("main")  # array from the "main" stream
        metadata = request.get_metadata()
        request.release()                      # requests must always be returned to libcamera
        
        if printm:
            print('\nMetadata of image:\n')
            pprint(metadata)
        
        # create a dict to store all the metadata values
        metadata_all = dict()
        
        for key in metadata.keys():
            metadata_all[key] = list() #make a list for each parameter
            metadata_all[key].append(metadata[key])
    
            
        sumv = np.longdouble(im_array)
            
        for i in range(1,n_imgs):
            
            request = camera.capture_request()
            metadata = request.get_metadata()
            sumv += np.longdouble(request.make_array("main"))
            request.release()
            
            if printm:
                print('\nMetadata of image '+str(i)+':')
                pprint(metadata)
            
            
            #Store the metadata in just one file
            for key in metadata.keys():
                try:
                    metadata_all[key].append(metadata[key])
                except:
                    if key not in metadata.keys():
                        metadata_all[key] = list()
                        metadata_all[key].append(metadata[key])
                    else:
                        print(str(key)+' value fail to be stored')
            
        #save the metadata of the captures in one file:       
        if type(mfpath) == str:
            with open(mfpath, 'w') as f:
                
                for key in metadata_all.keys():
                    f.write(str(key)+': ')
                    f.write(str(metadata_all[key])+'\n')
                
        # average them
        img = Image.fromarray(np.uint8(sumv / n_imgs))
        img.save(impath)
        
        if display == True:
            img.show() # display the image
        
        print('\nFilename '+impath+' stored successfully\n')
        
       # return(img)
    
    def LEDSetPWR(self,name, p):
        # just to set the power of module indicated by name
        self.modules[name]['value'] = p

        
    def module_switch(self,names, turn, msg = True):
        # it replaces LEDon LEDoff/moduleOFF
        # Turn ON or OFF the LED module indicated by name
        # It doesn't change the stored power value
        
        #make names a list in case it is a single string
        if type(names) != list:
            names = [names]
        
        for name in names:
        
            if turn == 'ON':
                # The actual power is obtained from its module's attribute
                power = self.modules[name]['value']
                status = 1
                switch_msg = "Channel "+ name + f" turned ON at {power} %\n"
            
            elif turn == 'OFF':
                
                power = 0
                status = 0
                switch_msg = "\nChannel "+ name + " turned OFF\n"
                
            else:
                print('\nIt is a toggle switch. "turn" parameter accept only "ON" or "OFF"\n')
                sys.exit()
                
            # board where channel is connected
            board = self.modules[name]['board']  
            
            # for LEDs conected at FluOpti board
            if board == 'FluOpti':    
                
                    # switch the power and the status
                    self.pwm.set_pwm(self.modules[name]['chan'],power)
                    self.modules[name]['status'] = status
                    
                    if msg == True:
                        print(switch_msg)
            
            # for LEDs conected at GPIO board
            elif board == 'GPIO':
                
                # Switch the value
                self.GPIO_control(name, status = status, msg = msg)
            
            # if use another non-defined board
            else:
                print('Indefined action for board '+ board +' of channel '+ str(name) +'\n')
            

    def updateTemps(self):
        self.t1,self.t2 = self.temp_sensor.get_temps()
        print(f"t1: {self.t1},\t t2: {self.t2} ")
        return self.t1,self.t2

    def startTempCtrl(self) :
        self.temp_ctrl_run = True
        self.temp_thread = threading.Thread(target = self.tempCtrl,)
        self.temp_thread.deamon = True
        self.temp_thread.start()
        self.temp_thread.join(0.1)


    def stopTempCtrl(self):
        self.temp_ctrl_run = False
        self.module_switch('H1','OFF')
        self.module_switch('H2','OFF')

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
            self.module_switch('H1','ON')
            self.module_switch('H2','ON')
            print(f"CH1 - t:\t{self.t1} tsp:\t{self.t_sp1} pwr :\t{self.t_pwr1}\nCH2 - t:\t{self.t2} tsp:\t{self.t_sp2} pwr :\t{self.t_pwr2}")
            sleep(self.temp_ctrl_update_time)

    def add_channel(self, name, channel, board = 'FluOpti'):
        # board = 'FluOpti' or 'GPIO'

        self.modules[name] = {'board': board,'chan': channel, 'value': 0, 'status':0}

        if board == 'GPIO':
            GPIO.setup(channel, GPIO.OUT)
            print('\nModule '+ str(name) + 'set as output in GPIO '+str(channel)+ '\n')

    def GPIO_control(self, name, status, msg = True):

        pin = self.modules[name]['chan']

        if status == 0:
            # Turn OFF
            GPIO.output(pin,GPIO.LOW)

            #update the status
            self.modules[name]['status'] = status

            if msg == True:
                print('\nModule '+ str(name) + ' (GPIO Pin ' + str(pin) + ') turned OFF')

        elif status == 1:
            #Turn ON
            GPIO.output(pin,GPIO.HIGH)

            #update the status
            self.modules[name]['status'] = status

            if msg == True:
                print('\nModule '+ str(name) + ' (GPIO Pin ' + str(pin) + ') turned ON')

        else:

            print('Invalid GPIO state. It have to be 0 or 1')
    
    def autotest(self, values = [30,65,100]):
        # to perform an autotest of the hardware
        # values: list with the power values to test. each value int between [0-100]
        
        if self.autotest:
        
            leds = self.get_modules(m_type = 'LED')
            
            for led in leds:
                
                basal_pwr = self.modules[led]['value']
                
                board = self.modules[led]['board']  
            
                # for LEDs conected at FluOpti board
                if board == 'FluOpti':
                    # test different power values
                    for power in values:
                        
                        self.LEDSetPWR(led,power)
                        self.module_switch(led,'ON')
                        sleep(0.5)
                # for LEDs conected to GPIO at RPI
                elif board == 'GPIO':
                    self.module_switch(led,'ON')
                    sleep(1)
                    
                #turn OFF
                self.module_switch(led, 'OFF')
                #return to basal power    
                self.LEDSetPWR(led,basal_pwr)
            
            print('\n-- AutoTest Finished --\n')
            
    
    def get_attrs(self, attrs):
        """
        Return a list with the values of attrs
        attrs: list of strings
            list with the names of the attributes of interest
        """
        values = []
        if type(attrs) != list:
            attrs = [attrs]
            
        for attr in attrs:
            values.append(getattr(self, attr))
        return(values)
    
    def attr_names(self):
        return(list(self.__dict__.keys()))
    
    
    def close(self, *args):
        ''' Clean exit '''
        try:
            self.camera.close()
        except Exception as e:
            print(e, flush=True)

### Other -non FluOPti Object- Functions ### 
def read_settings(self, filename, key_sep = '=', com_sym = '#', 
                      notes_kw= 'notes', msg = True):    
    """
    To read the setting parameters included in the input text file (.txt).
    The key nomenclature can be customized with this function parameters.
    The default expected estructure of the input file is like this:

    param1 = some_value
    param2 = some_value or values
    # after this simbol text in the line is ommited
    param3 = some_value    # the text after this symbol is ommited too
    notes = some text
    more text
    and even more, and until the end will be included inside "notes_kw" parameters.

    ** notes_kw is a reserved parameter name ** 
    (be careful to not name another parameter with this exact word)

    Parameters
    ----------
    filename: string
        filename to be read
    
    key_sep: string
        simbol, character or specific string used to split the parameter name from 
        its value.
    
    com_sym: string
        simbol or character to identify the commentary portions.
        Everything after this simbol will be ommited.
    
    notes_kw: string
        Parameter keyword name of the extra comments. 
        Everyhting after this parameter (i.e. at its right and all the lines 
        to the end of the file) will be included in its value.
    
    msg: bool
        if True, print information message
    
    Return
    ------

    parameters: dictionary
        Dictionary with the parameters names as keys and their read value

    """
    
    if msg:
        print('Reading settings from "'+filename+'"')
    
    parameters = dict()
    parameters[notes_kw] = ''    # init the "notes" parameter

    with open(filename, 'r') as f:

        counter = 0

        for line in f:
            
            counter += 1
            
            # if the first element is the comment symbol, pass to next line
            if line[0] == com_sym:
                continue
            
            # if it is not a "comment line", get the parameter and its value
            else:

                # in case it reach the "notes" parameter
                if parameters[notes_kw] != '':
                    
                    parameters[notes_kw] += '\n' + line

                # until you start to fill the "notes" parameter
                else:    
                    # the parameter name is everything at the left of the first "key_sep"
                    
                    key = line.split(key_sep)[0].strip()  # strip eliminate front and back white spaces
                    
                    # the value is all between the first 'key_sep" and any other comment (indicated by "com_sym")
                    try:
                        value = line.split(key_sep)[1].split(com_sym)[0].strip()
                    except:
                        print("\n[Error]Cannot be able to split parameter and its value at line " + str(counter))
                        print("----- Check the separator character in tl_config file -----\n")
                        raise

                    parameters[key] = value.split('\n')[0]  #eliminate the break line symbol if present

    return(parameters)

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
        Fluopti.module_switch('B', 'ON')
        sleep(5)
    #Fluo.stopTempCtrl()
    Fluopti.module_switch('B','OFF')
    
    # Test temperature reading
    t1,t2 = Fluopti.updateTemps()
    
    print('\nt1 = '+str(t1)+ '°C')
    print('t2 = '+str(t2)+ '°C')
    
    print('-- Test Finished --')