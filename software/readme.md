# Hardware

En la Raspberry Pi:
  - pin 3 (GPIO2): SDA
  - pin 5 (GPIO3): SCL
  - pin 6 :        GND

En la tarjeta FLuOpti
  Esquina superior izquierda:<br>
    1 - SCL &emsp; &emsp; &emsp; &emsp; &emsp;8 - PWM in 1<br>
    2 - SDA &emsp; &emsp; &emsp; &emsp; &ensp;&nbsp;7 - PWM in 2<br>
    3 - NotConnected   &emsp; 6 - GPIO1<br>
    4 - GND &emsp; &emsp; &emsp; &emsp; &ensp;5 - GPIO2<br>
  
  Los conectores GPIO y PWM estan diseñados para conectar cualquier pin de la Raspberry Pi, los cuales son clonados a la parte inferior de la placa. *e.g.* puedo conectar el pin15 de la raspberry Pi al conector GPIO1, y luego conectarme directamente al GPIO1 de la parte inferior de la placa para acceder a él.

 De manera alternativa, es preferible usar el conector i2c (esquina superior derecha) para mayor simpleza:<br>
  1 - SCL<br>
  2 - SDA<br>
  3 - GND

<p align="center">
<img width="600" src="/README_images/conectores_RPI.png">
</p>
  
# Instalación

## Sistemas operativos previos a BookWorm

Instalar las librerias necesarias para el funcionamiento de la placa:
```
sudo pip install adafruit-ADS1x15
sudo pip install adafruit-pca9685
sudo pip install simple-pid
```

## Sistema operativo BookWorm
Si se esta usando *BookWorm* como sistema operativo de la Raspberry Pi, es necesario crear un ambiente en el que instalar estas librerias.
Primero asegurarse de tener todo actualizado:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip
sudo apt install --upgrade python3-setuptools
sudo apt install python3.11-venv
```

Crear el ambiente *fluop_env*:
```
python3 -m venv fluop_env --system-site-packages
```
y activarlo
```
source fluop_env/bin/activate
```

ahora se deben instalar las librerias en él:
```
pip3 install adafruit-ADS1x15
pip3 install adafruit-pca9685
pip3 install simple-pid
```

Alternativamente se pueden instalar las librerias directamente en el sistema (sin crear ambientes), agregando el comando *--break-system-packages*. Ejemplo:
```
sudo pip install adafruit-ADS1x15 --break-system-packages
```

## Activar comunicación I2C

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

si se esta utilizando BookWorm como sistema operativo de la raspberry, se debe activar el ambiente en el cual se instalaron los paquetes. Si el ambiente creado se llama *fluop_env*:

```
source fluop_env/bin/activate
```

Luego ejecutamos la rutina de testeo mediante el comando:
```
python3 simple_test.py
```
es necesario chequear que los LEDs esten conectados de manera correspondiente a las posiciones indicadas en el código *FluOpti.py*
```
 self._default_modules  = {
        #MODULE  #CHANNEL    #VALUE
        'R'    :{ 'chan':5, 'value': 0,'status':0},
        'G'    :{ 'chan':6, 'value': 0,'status':0},
        'B'    :{ 'chan':9, 'value': 0,'status':0},
        'W'    :{ 'chan':10, 'value': 0,'status':0},
        'H1'   :{ 'chan':11, 'value': 0,'status':0},
        'H2'   :{ 'chan':12, 'value': 0,'status':0}
        }
```
