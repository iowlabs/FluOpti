# Hardware

En la raspberry:
  - 3 GPIO2: SDA
  - 5 GPIO3: SCL
  - 6 GND

En la tarjeta FLuOpti
  Esquina superior izquierda:
    - 1 SCL             - 8 PWM in 1
    - 2 SDA             - 7 PWM in 2
    - 3 NotConnected    - 6 IO1
    - 4 GND             - 5 IO2

  De manera alternativa, es preferible usar el conector i2c (esquina superior derecha)
  para mayor simpleza:
    - 1 SCL
    - 2 SDA
    - 3 GND




# Instalación

sudo pip install adafruit-ADS1x15
sudo pip install adafruit-pca9685
sudo  pip install simple-pid

Ejectuar sudo raspi-config, ir a opciones de interface y activar la comunicación I2C.

# Solución de problemas

1. Se recomienda instalar el scan de i2c para revisar si los módulos estan:
  - https://learn.adafruit.com/scanning-i2c-addresses/raspberry-pi
  - sudo apt-get install i2c-tools
  - run: i2cdetect -y 1

Se desplegará la lista de direcciones de los módulos conectados:

     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- 49 -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- 5c -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: 70 -- -- -- -- -- -- --  

vemos que hay módulos conectados en 0x49, 0x5c y 0x77

En caso de que los módulos no se encuentren conectados, se desplegará esto:
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --  
