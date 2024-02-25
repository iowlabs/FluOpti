# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 16:33:45 2024

@author: Prosimios
"""

import sys
import os
from time import sleep,time,ctime, localtime

# import FluOpti library
import hardware.FluOpti as flp

################################################
## get the indicated configuration file
param_msg = "\nRequired parameter: folder_name/configuration_file.txt\n"
#example of calling: python3 timelapse.py experiment_folder/tl_config.txt

if len(sys.argv) > 1: # sys.argv[0] is the name of the rutine
    
    fpath = sys.argv[1]
    
    # check filename extension    
    try: 
        fpath.split('.')[1]
    
    except:
        fpath+='.txt'
        print('\nNo filename extension indicated. It is assumed as ".txt"\n')
    
    # in case folder was indicated, split the folder name from the filename
    if fpath.find('/') > 0:
        
        folder = fpath.split('/')[0]
        fname = fpath.split('/')[-1]
    
    # check filename path is correct 
    try:
        os.path.exists(fpath) #it checks inside the current directory
        
    except:
        print ('\n'+ fpath + ' not found' )
        print('[RUTINE ABORTED]\n')
        sys.exit()
    
else:
    print (param_msg )
    sys.exit()

##########################################################################

## read the configuration file:
input_values = flp.read_settings(fpath)
    
# init FluOpti object
Fluopti =  flp.FluOpti(model=input_values['board_model']) 

# transform the input_values in Fluopti parameters
Fluopti.get_setting_parameters(input_values)

# Initial messages
print('\n--- Running FluOpti ---\n')

# Perform autotest if was indicated in input file
Fluopti.autotest()

# get let modules
leds = Fluopti.get_modules(m_type = 'LED')

# init and set the camera object
Fluopti.startCamera()
Fluopti.setCamera()  # input the camera configuration dictionary here.

# different picture camera controls:
capture_controls = {
        'B':{
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
            'ExposureTime': 50000,                   #(75, 11766829, Undefined). unit microseconds.
            'ExposureValue': 0.0,                   #(-8.0, 8.0, 0.0) - Zero is the base exposure level. Positive values increase the target brightness, and negative values decrease it 
            'FrameDurationLimits': (47183,11767556),   # tuple, each value: (47183, 11767556, Undefined). The maximum and minimum time that the sensor can take to deliver a frame (microseconds). Reciprocal of frame rate
            'NoiseReductionMode': 0,                #(0, 4, 0) - 0 is off.
            'Saturation': 1.0,                      #(0.0, 32.0, 1.0) - zero greyscale images, 1.0 "normal" saturation, higher values for more saturated colours.
            'ScalerCrop': (0, 2, 3280, 2460),       #((0, 0, 64, 64), (0, 0, 3280, 2464), (0, 2, 3280, 2460)) - to use just a sub part of the sensor area: (x_offset, y_offset, width, height)
            'Sharpness': 0.0                        #(0.0, 16.0, 1.0)} - zero no additional sharpening, 1.0 is "normal" level of sharpening, larger values apply proportionately stronger sharpening
            },
        
        'W':{
 
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
        }

# optogenetic schedule definition 
Fluopti.sch['times']['th']= [24,72] # light induction time schedule limits in hours
Fluopti.sch['leds'] = {     
'R' : [0,100],    # R light power percetage in each schedule module
'G' : [100,0]     # G light power percetage in each schedule module
}

# check the schedule
Fluopti.check_sch()
Fluopti.sch['times']['ts'] = [i * 3600 for i in Fluopti.sch['times']['th']]  # convert the hour values to seconds

# update the LEDs power accord the schedule
Fluopti.update_power()

# init the timelapse
h_total = Fluopti.sch['times']['th'][-1]     #timelapse total hours
cicles_per_h = 4                # cicles per hour
pLEDs = ['B','W']               # LEDs turned on to take pictures

cicles = h_total*cicles_per_h   # total number of cicles
tpc = 3600/cicles_per_h         # "time per cicle" = cicle duration in segs

display = True

ltime = localtime()
print('\nTimelapse starting at:')
print(f'{ltime[3]}:{ltime[4]}:{ltime[5]} - '+ f'{ltime[2]}/{ltime[1]}/{ltime[0]}')

temperatures = list()

Fluopti.init_timer(tpc)

while Fluopti.cicle <= cicles:
    
    time_init = time()   # to display the time elapsed taking the pictures
    
    print('\nCicle '+str(Fluopti.cicle)+' ('+ '%.2f'%(Fluopti.cicle/cicles_per_h)+' h) running...\n')
    
    # turn OFF all the LEDs
    for led in leds:
        Fluopti.module_switch(led,'OFF', msg = False)
    print('--All LEDs OFF--')
    sleep(1) # wait one second to be sure all LEDs are off
    
    # take pictures
    
    for led in pLEDs:
        # turn ON the LED
        Fluopti.module_switch(led, 'ON', msg = True)
        sleep(1)
        print('\nTaking picture\n')
        #'''
        # modify the camera configurations:
        Fluopti.camera.set_controls(capture_controls[led])
        
        # take a picture
        impath = folder+'/'+str(led)+"%03d"%(Fluopti.cicle)+imformat
        mfpath = folder+'/'+str(led)+"%03d"%(Fluopti.cicle)+'.txt'
        Fluopti.camera.start() #start the camera
        Fluopti.im_capture(impath, n_imgs = 3, mfpath = mfpath, printm = False, display = display)
        #'''
        # turn OFF the LED
        Fluopti.module_switch(led, 'OFF', msg = True)
        sleep(1) # wait one second to be sure all LEDs are off
        
    #turn ON the proper optogenetics lights
    Fluopti.opto_ON()
    
    # Read current temperature
    t1,t2 = Fluopti.updateTemps()
    
    print('\nt1 = '+'%.2f'%(t1)+ '°C')
    print('t2 = '+'%.2f'%(t2)+ '°C')
    temperatures.append([Fluopti.cicle,t1,t2])
    
    # update some variables
    Fluopti.cicle+=1
    display  = False  # just to display the first image
    
    
    print('Cicle time: '+ str(time()-time_init) + ' seconds')
    
    print(' --- Wainting the time to the next cicle... ---')
    
    # wait until cicle time is finished
    if Fluopti.cicle < cicles: # not wait if the last cicle was reached.
        
        # the end of the cicle is indicated by the timer
        while Fluopti.check_timer():
            
            # Check the schedule time
            Fluopti.update_schedule()
            
            sleep(Fluopti.update_freq) # time windows span to check

# turn OFF all the LEDs
for led in leds:
    Fluopti.module_switch(led,'OFF', msg = False)
print('-- All LEDs OFF --')  

#save the temperatures in a file:       
tfpath = folder+'/'+'temperatures.txt'
with open(tfpath, 'w') as f:
    # Headers
    f.write('Cicle,Sensor_1[°C],Sensor_2[°C]\n')
    
    for values in temperatures:
        f.write(str(values[0]) + ','+ '%.2f'%(values[1])+ ','+'%.2f'%(values[2])+'\n')

# Final mesages and information
print('-- Timelapse completed --')
ltime = localtime()
print(f'{ltime[2]}/{ltime[1]}/{ltime[0]} - 'f'{ltime[3]}:{ltime[4]}:{ltime[5]}')






