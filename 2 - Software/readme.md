# Hardware

En la raspi
  - 3 GPIO2: SDA
  - 5 GPIO3: SCL
  - 6 GND

En la tarjeta
  - 1 SCL             - 8 PWM in 1
  - 2 SDA             - 7 PWM in 2
  - 3 NotConnected    - 6 IO1
  - 4 GND             - 5 IO2

  Recomendado usar el conector i2c
    - 1 SCL
    - 2 SDA
    - 3 GND




# Instalación

sudo pip install adafruit-ADS1x15
sudo pip install adafruit-pca9685
sudo  pip install simple-pid

# Solución de problemas

1. Se recomienda instalar el scan de i2c para revisar si los módulos estan:
  - https://learn.adafruit.com/scanning-i2c-addresses/raspberry-pi
  - sudo apt-get install i2c-tools
  - run: i2cdetect -y 1
