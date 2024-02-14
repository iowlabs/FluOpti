# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 17:35:39 2024

@author: Prosimios
"""

from picamera2 import Picamera2, Preview
import time
import sys
from PIL import Image
from pprint import *

# Basic settings at calling the rutine
param_msj = "\nRequired parameters: folder_name/filename\n, set_controls[True/False]"


if len(sys.argv) > 1: # sys.argv[0] is the name of the rutine
    
    fname = sys.argv[1]
    
    try:
        set_controls = bool(sys.argv[2])
    except:
        set_controls = False
        
else:
    fname = False

#create the camera object
picam2 = Picamera2()
modes = picam2.sensor_modes
# define the camera sensor mode
m_num = 3
modes = picam2.sensor_modes
mode = modes[m_num]
print('\nSelected sensor mode properties:')
pprint(mode)

print('\n')

# obtain the characteristic values of the selected mode to assign it to the camera
msize = mode['size']
mformat = mode['format']

if set_controls == True:
    capture_controls = {                                                    #(min, max, default_value)
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

else:
    capture_controls = {}

# define the camera configuration
camera_config = picam2.create_still_configuration(
        controls=capture_controls,
        main={'size': msize}, 
        raw ={'format': mformat}
        )
   
picam2.configure(camera_config)

'''
# start the preview
picam2.start_preview(Preview.QTGL) #NULL to not display at all, QT to display on VNC too, QTGL to hardware acelerate the display, DRM to don't
picam2.title_fields = ["FocusFoM","ExposureTime", "ColourGains", "AnalogueGain" ] # "Lux","DigitalGain",

stop = False
while stop == False:
    stop = input('Enter any key to stop: ')

print('Preview stopped')
'''
# start the camera
picam2.start()
time.sleep(2)

# capture the file
#picam2.capture_file(filename)
#array = picam2.capture_array("main")
image = picam2.capture_image("main")
image.show() # display the image
picam2.stop()

# if filename was indicates, then save the file
if fname != False:
    image.save(fname)  
