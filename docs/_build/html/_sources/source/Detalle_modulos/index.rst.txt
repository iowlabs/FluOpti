Detalle de módulos
~~~~~~~~~~~~~~~~~~

ADC
^^^

El ADC escogido es el
`ADC <https://cdn-shop.adafruit.com/datasheets/ads1115.pdf>`__ de la
empresa Texas Instruments. La empresa
`adafruit <https://www.adafruit.com/product/1085>`__ posee un módulo
autocontenido para integrar este ADC a la Raspberry Pi, así como una
completa documentación y las bibliotecas para utilizarlo.

Las principales características de este ADC se enlistan a continuación

-  4 canales, single-ended.
-  16 bits de resolución
-  Voltaje de alimentación entre 2V a 5V
-  Interfaz I2C
-  Referencia interna

Acondicionamiento de señal
^^^^^^^^^^^^^^^^^^^^^^^^^^

Los sensores que se utilizarán permiten implementar el proceso de
medición gracias a la variación de sus propiedades eléctricas. En
general, estas variaciones se evidencian mediante un cambio de voltaje.
En consecuencia, este es el voltaje que debe ser adquirido por el
circuito electrónico. Por ello, en primera instancia, se dispone de un
circuito divisor que, al ser conectado con el respectivo sensor, permite
obtener el voltaje asociado a la medición. En la siguiente figura se
muestra un ejemplo de esta conexión circuital, para el caso de un sensor
de temperatura del tipo termistor (NTC):

.. figure:: /README_images/divisor_ntc.png
   :alt: Divisor

   Divisor

Para realizar correctamente la adquisición de las señales desde los
sensores es necesario contar con una etapa de acondicionamiento de
señal. De esta forma, se asegura que los valores de voltaje que
entreguen los sensores se encuentren dentro de los límites que permiten
las entradas del ADC y de la Raspberry. No solo es deseable que se opere
dentro de los límites, sino también aprovechar el rango de lectura al
máximo, es decir, que el voltaje mínimo de medición sea igual (o lo más
cercano posible) al voltaje mínimo que permiten los pines del ADC. Y, la
misma relación con el voltaje máximo de medición.

Dado que aún no existe 100% de certeza sobre los sensores a utilizar, se
implementó una circuito genérico de acondicionamiento, el cual se
compone de una etapa de amplificación y otra de adición de offset. En la
siguiente figura se muestra este circuito:

.. figure:: /README_images/acondicionador.png
   :alt: Acondicionador

   Acondicionador

Los símbolos de switches corresponden, en la práctica, a un solder
jumper, el cual conecta la entrada con la salida solo si se unen con
soldadura sus terminales. Si se conectan S1, S2 y S3 el circuito queda
configurado como un buffer, lo cual, de todas formas, beneficia a la
señal adquirida puesto que el buffer disminuye su impedancia. Conectando
o no S1, S2 y S3 se pueden obtener distintas configuraciones: solo
amplificador, solo adición de offset, o ambas. Además, los valores de
las resistencias se pueden ajustar dependiendo de los sensores que se
utilicen, de tal forma de fijar correctamente la ganancia y el offset,
según sea el caso.

Generador de PWM
^^^^^^^^^^^^^^^^

La generación de PWM se realiza por medio de un circuito integrado
`PCA9685 <https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf>`__. La
empresa `adafruit <https://www.adafruit.com/product/2928>`__ posee un
módulo autocontenido para integrar este módulo a la Raspberry Pi, así
como una documentación completa y las bibliotecas para utilizarlo.

Principales características:

-  16 canales dimeables por PWM.
-  12 bits de resolución
-  Voltaje de alimentación etre 2.3V a 5.5V
-  Interfaz I2C

Driver de baja corriente
^^^^^^^^^^^^^^^^^^^^^^^^

Para los canales de bajo consumo de corriente, tales como los arreglos
de LEDs rojos y verdes, se utilizará el integrado
`ULN2803 <https://www.electroschematics.com/wp-content/uploads/2013/07/uln2803a-datasheet.pdf>`__.
Este integrado implementa un arreglo de 8 transistores tipo darlington,
haciendo posible el control de hasta 8 canales en un único integrado.

Principales características:

-  Arreglo de 8 canales
-  Poseen alimentación común
-  La corriente máxima por canal es de 500mA, pudiendo aumentar esta
   cantidad si se consideran canales en paralelo.

Driver de alta corriente
^^^^^^^^^^^^^^^^^^^^^^^^

Para los canales de alto consumo se utilizará un transistor mosfet
`IRF740 <https://datasheet.lcsc.com/szlcsc/1808281645_Infineon-Technologies-IRF7402TRPBF_C169089.pdf>`__.
Es necesario contar con un transistor por canal. Y, para casos de alta
corriente (superiores a 1A) es necesario considerar la inclusión de
disipadores (heatsink) o pads de disipación que permitan una evacuación
efectiva del calor.

Principales características:

-  Altas frecuencias de switching
-  Bajo consumo de operación
-  Control de hasta 10A (ó 40A en corrientes pulsantes)
-  Simple implementación

Sistema de distribución de poder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Como se mencionará más adelante, la alimentación que llegará al circuito
electrónico implementado será de 12VDC, por lo que es necesario contar
con convertidores de voltaje DC-DC para generar los distintos voltajes
de alimentación que se requieren en el circuito. En particular, es
necesario generar 5V y 3.3V para alimentar los circuitos analógicos y
digitales, y un set de voltajes para alimentar los distintos arreglos de
LEDs y el Heater. Se decidió disponer de los siguientes voltajes para
este último uso: 9V, 16V, 20V y 24V. A continuación se especifican los
convertidores empleados para generar cada uno de los voltajes
mencionados.

5V
''

-  Integrado:
   `LM2596R-5.0 <https://datasheet.lcsc.com/szlcsc/1811131510_HTC-Korea-TAEJIN-Tech-LM2596R-5-0_C77782.pdf>`__
-  Tipo: Step-down, regulador switching
-  Frecuencia de switcheo: 150kHz
-  Corriente máxima de salida: 3A

.. _v-1:

3.3V
''''

-  Integrado:
   `AP2112K-3.3 <https://datasheet.lcsc.com/szlcsc/1809192242_Diodes-Incorporated-AP2112K-3-3TRG1_C51118.pdf>`__
-  Tipo: LDO, regulador lineal
-  Corriente máxima de salida: 600mA

.. _v-2:

9V
''

-  Integrado:
   `LM2696SX-ADJ <https://datasheet.lcsc.com/szlcsc/1809192335_Texas-Instruments-LM2596SX-ADJ-NOPB_C29781.pdf>`__
-  Tipo: Step-down, regulador switching ajustable (voltaje de salida es
   configurable según indicaciones de conexión en el datasheet)
-  Frecuencia de switcheo: 150kHz
-  Corriente máxima de salida: 3A

16V, 20V, 24V
'''''''''''''

-  Integrado:
   `XL6008E1 <https://datasheet.lcsc.com/szlcsc/1809200019_XLSEMI-XL6008E1_C73012.pdf>`__
-  Tipo: Step-up, regulador switching ajustable (voltaje de salida es
   configurable según indicaciones de conexión en el datasheet)
-  Frecuencia de switcheo: 400kHz
-  Corriente máxima de salida: 3A

Fuente de alimentación
^^^^^^^^^^^^^^^^^^^^^^

Dado que el circuito electrónico funcionará con alimentación DC es
necesario emplear una fuente DC que se enchufe directamente a la red y
que entegue un voltaje de salida continuo. En particular, se decidió
emplear una `fuente DC
conmutada <https://afel.cl/producto/fuente-de-poder-12v-10a-120w/>`__.
Sus principales características son:

-  Voltaje de entrada: 100-120VAC / 60Hz, **200-240VAC / 50Hz**
-  Voltaje de salida: 12V
-  Corriente máxima de salida: 10A
-  Potencia máxima de salida: 120W