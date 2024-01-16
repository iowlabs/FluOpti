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
instalar las librerias necesarias para el funcionamiento de la placa:
```
sudo pip install adafruit-ADS1x15
sudo pip install adafruit-pca9685
sudo  pip install simple-pid
```
Ejecutar *sudo raspi-config*, ir a *opciones de interface* y activar la comunicación I2C.

# Solución de problemas

1. Se recomienda instalar el scan de i2c para revisar si los módulos estan:
  - https://learn.adafruit.com/scanning-i2c-addresses/raspberry-pi
  - sudo apt-get install i2c-tools
  - run: i2cdetect -y 1

Se desplegará la lista de direcciones de los módulos conectados:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- 49 -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- 5c -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: 70 -- -- -- -- -- -- --  
```
vemos que hay módulos conectados en 0x49, 0x5c y 0x77

En caso de que los módulos no se encuentren conectados, se desplegará la lista vacia:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --  
```

# Testeo

En la terminal, navegar hasta el directorio del software */FluOpti/software* (usando comando cd).
(debe estar clonado el repositorio FluOpti en la raspberry).

Luego ejecutamos la rutina de testeo mediante el comando:
```
python3 simple_test.py
```
es necesario chequear que los LEDs esten conectados de manera correspondiente a las posiciones indicadas en el código *FluOpti.py*
```
 self._default_modules  = {
        #MODULE  #CHANNEL    #VALUE
        'R'    :{ 'chan':6, 'value': 0,'status':0},
        'G'    :{ 'chan':7, 'value': 0,'status':0},
        'B'    :{ 'chan':8, 'value': 0,'status':0},
        'W'    :{ 'chan':9, 'value': 0,'status':0},
        'H1'   :{ 'chan':10, 'value': 0,'status':0},
        'H2'   :{ 'chan':11, 'value': 0,'status':0}
        }
```
