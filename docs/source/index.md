# FluOpti
Este proyecto consiste en la realización de un control integrado para la iluminación del proyecto FluOpti. Más información respecto al poyecto se puede encontrar en los siguientes enlaces:
1. https://docs.google.com/document/d/1PmyignsIkzQdomBdSQQ2lFlBKneosc83GTr52-iTTBQ/edit?usp=sharing
2. [Git](https://github.com/SynBioUC/FluoPi/tree/master/Hardware_design_files/PCB)
3. [OSF](https://osf.io/dy6p2/)
4. [Manual de diseño de proyectos de LEDs estandar](https://www.overleaf.com/4759732231nspqcngnnhdq)

## Descripción de problema electrónico
El sistema consiste en un dispositivo que permite observar muestras biológicas, a las cuales se les realizan procesos de activación genética por medio de otpogenética.
En la práctica, el dispositivo consiste en una cámara conectada a una raspberry, la que permite observar las muestras, un set de LEDs, los que permiten realizar los procesos optogenéticos, y la respectiva electrónica de control.

Los LEDs que se deben controlar realizan 3 tareas distintas:
1. Excitar la muestra para poder adquirir imágenes de fluorescencia: LEDs azules.
2. Iluminar la muestra para obtener imágenes de campo claro que permitan medir el crecimiento de las colonias bacterianas de manera apropiada: LEDs blancos.
3. Generar estímulos para activación de procesos optogenéticos. Estos LEDs son de longitudes de onda específicas dependiendo del gen que se desee activar/desactivar: LEDs rojos y verdes.

El proyecto también considera la necesidad de implementar sensores que permitan calibrar el sistema y monitorear variables determinadas, tales como intensidad o temperatura.

![Diagrama General](/README_images/Diagrama_1.PNG)



## Requerimientos

### Requerimientos generales
A continuación se enlista un set de requerimientos generales del proyecto:
1. Implementar una electrónica compatible con los componentes actuales disponibles.
2. Proponer una solución completa al problema.
3. Considerar diseños modulares que permitan adaptarse a parámetros futuros.

### Requerimientos específicos

A continuación se enlista un set de requerimientos específicos del proyecto:
1. Los LEDs azules empleados para iluminar la muestra corresponden a los [Super Bright 5mm Blue](https://www.superbrightleds.com/moreinfo/through-hole/5mm-blue-led-120-degree-viewing-angle-flat-tipped-1200-mcd/265/1192/):
   * Longitud de onda: 470nm
   * Forward current: 30mA @ 3.3V
   * Peak forward current: 100mA
   * Max voltage forward: 3.8V

2. Actualmente, se está pensando en una placa de LEDs azules con distribución física del tipo circular. Esto implicaría una cantidad de 55 LEDs. En la siguiente imagen se muestra esta topología propuesta:


![Propuesta nueva disposición LEDs azules](/README_images/disposicionBLUE.PNG)

3. Los LEDs verdes empleados para la activación de genes corresponden a los [Kingbright WP7083ZGD/G](http://www.kingbrightusa.com/images/catalog/SPEC/WP7083ZGD-G.pdf):
   * Longitud de onda: 520nm
   * Forward current (typ): 20mA @ 3.2V
   * Peak forward current: 100mA
   * Max voltage forward: 4V

4. Los LEDs rojos empleados para la desactivación de genes corresponden a los [Deep-Red 5mm LED](https://www.ledsupply.com/leds/5mm-led-deep-red-660nm-50-degree-viewing-angle):
   * Longitud de onda: 660nm
   * Forward current (typ): 20mA @ 2.2V
   * Peak forward current: 100mA
   * Max voltage forward: 2.8V

5. Los LEDs blancos se implementan por medio de una tira LED comercial. Típicamente su operación se caracteriza por:
   * Forward current: 20mA @ 12V

6. El control implementado debe corresponder a PWM, con el fin de regular la intensidad lumínica de los LEDs. Se opta por este control debido a su sencilla implementación.

7. El sistema  debe contar con un sistema de distribución de potencia para alimentar todos los sub-módulos, LEDs y raspberry.

8. El sistema debe contar, además, con la posibilidad de leer sensores que permitan medir y calibrar la intensidad de luz proveniente desde los LEDs. Dado que el control se implementa por medio de una raspberry, es necesario utilizar sensores digitales o incluir en el diseño un ADC que permita realizar la conversión. En este último caso será necesaria la inclusión de una etapa que acondicione las señales provenientes desde los sensores.

9. El sensor de intensidad lumínica tiene que cumplir:
* Bajo costo
* Fácil de conseguir
* Respuesta plana para los LED Rojo y Verde

Una alternativa es el fototransistor [TEMT6000](https://learn.sparkfun.com/tutorials/temt6000-ambient-light-sensor-hookup-guide/all).

10. El sensor de temperatura es un NTC (termistor). [Aquí](https://www.adafruit.com/product/372) se presenta una alternativa.

11. El heater es del tipo resistivo y se debe poder alimentar con 9V ó 12V. Se debe implementar un control PWM de corriente utilizando un transistor. Una posible alternativa de heater es el [Film Heating Panel](http://www.icstation.com/heating-thin-film-polyimide-heating-plate-panel-25x50mm-b1221-p-9887.html).


### Consideraciones de diseño adicionales

1. Consideraciones de operación: El dispositivo debe ser diseñado para funcionar en espacios interiores y dentro de una cápsula cerrada, en la se realiza el análisis de las muestras, por lo que no es necesaria la resistencia al agua o a condiciones de humedad extremas. La placa estará, además, dentro de una caja, por lo que tampoco estará expuesta a polvo u otros contaminantes. Una vez instalado el dispositivo, este permanecerá siempre en el mismo lugar (a menos que se deba extraer por alguna situación en particular), por lo que no es necesario que el diseño considere la exposición a posibles golpes o vibraciones muy significativas.

2. La única etapa del circuito que puede significar un peligro para el usuario es la alimentación, puesto que esta proviene desde la red eléctrica, por lo cual es prudente que la carcasa del producto cumpla con normas acorde al voltaje y corriente de operación, por ejemplo, IP67. Sin embargo, esta protección será ajena al circuito mismo. Es pertinente, de todas formas, la inclusión de disipadores en algunos integrados, en el caso que operen con altas corrientes. Esto, para evitar fallas durante la operación o incluso que se quemen componentes.


## Propuesta
Teniendo presente los requerimientos planteados en la sección anterior se propone una solución basada en el siguiente esquema


![Esquema de la solución electrónica propuesta](/README_images/solución_propuesta.png)


El principal criterio de diseño considerado es la modularidad, con el objetivo de poder entregar una solución adaptable y escalable. Los parámetros prácticos de elección de componentes dependen de los requerimientos específicos del sistema. El esquema general consiste en un módulo que genera señales PWM, el cual es controlado por protocolo serial I2C. Este módulo genera 16 señales de PWM permitiendo controlar hasta 16 canales. Estas señales PWM controlan los módulos driver. Estos últimos ajustan la señal PWM a los requerimientos que necesitan los distintos tipos de circuitos de LEDs. Cada driver puede poseer uno o más canales dependiendo de la cantidad de subcircuitos independientes que se deseen controlar por tipo de LED. Del mismo modo, algunas de estas señales de control PWM pueden dejarse a disposición del usuario en caso que necesite controlar una placa con driver ya existente, como es el caso de este proyecto.

El otro bloque importante es el sistema de distribución de poder, el cual se encarga de generar todos los voltajes necesarios para los distintos bloques y etapas del circuito, dependiendo de cada requerimiento. La idea principal es que la placa reciba una única alimentación y que, internamente, genere los distintos voltajes y corrientes, contribuyendo, así, a la adaptabilidad de la solución.

Por último, la placa considera la inclusión de un ADC de 4 canales, controlado por I2C, el cual permite leer hasta 4 sensores analógicos. Es necesario contar con un ADC, ya que la Raspberry Pi no cuenta con ADC. Esto permite otorgar una alta adaptabilidad, ya que es posible conectar distintos tipos de sensores analógicos, dependiendo de la aplicación. Para esto, la placa considera etapas de acondicionamiento de señal, las cuales se deben configurar para el sensor específico.

### Resumen de características de la solución propuesta

Las principales características de la solución propuesta son:

1. Adaptabilidad: La placa total solo se controla por medio de un bus I2C (3 pines), independiente de la cantidad de LEDs y sensores que se deseen utilizar.

2. Integración: La disposición de canales de control PWM permite integrar tanto las soluciones existentes como soluciones creadas por distintos fabricantes.

3. Escalabilidad: Gracias a la utilización del protocolo I2C, es posible controlar múltiples de estas placas con una sola Raspberry Pi (o un solo microcontrolador/procesador en general). Si se integran dos placas en serie se puede llegar a disponer de 32 canales de control de LEDs y 8 canales de sensores analógicos.

A continuación, se describen en detalle los módulos a implementar. Es importante mencionar que se utilizó como guía el [documento tutorial](https://www.overleaf.com/4759732231nspqcngnnhdq) generado en el marco de este proyecto.


### Detalle de módulos

#### ADC
El ADC escogido es el [ADC](https://cdn-shop.adafruit.com/datasheets/ads1115.pdf) de la empresa Texas Instruments. La empresa [adafruit](https://www.adafruit.com/product/1085) posee un módulo autocontenido para integrar este ADC a la Raspberry Pi, así como una completa documentación y las bibliotecas para utilizarlo.

Las principales características de este ADC se enlistan a continuación

* 4 canales, single-ended.
* 16 bits de resolución
* Voltaje de alimentación entre 2V a 5V
* Interfaz I2C
* Referencia interna

#### Acondicionamiento de señal
Los sensores que se utilizarán permiten implementar el proceso de medición gracias a la variación de sus propiedades eléctricas. En general, estas variaciones se evidencian mediante un cambio de voltaje. En consecuencia, este es el voltaje que debe ser adquirido por el circuito electrónico. Por ello, en primera instancia, se dispone de un circuito divisor que, al ser conectado con el respectivo sensor, permite obtener el voltaje asociado a la medición. En la siguiente figura se muestra un ejemplo de esta conexión circuital, para el caso de un sensor de temperatura del tipo termistor (NTC):

![Divisor](/README_images/divisor_ntc.png)

Para realizar correctamente la adquisición de las señales desde los sensores es necesario contar con una etapa de acondicionamiento de señal. De esta forma, se asegura que los valores de voltaje que entreguen los sensores se encuentren dentro de los límites que permiten las entradas del ADC y de la Raspberry. No solo es deseable que se opere dentro de los límites, sino también aprovechar el rango de lectura al máximo, es decir, que el voltaje mínimo de medición sea igual (o lo más cercano posible) al voltaje mínimo que permiten los pines del ADC. Y, la misma relación con el voltaje máximo de medición.

Dado que aún no existe 100% de certeza sobre los sensores a utilizar, se implementó una circuito genérico de acondicionamiento, el cual se compone de una etapa de amplificación y otra de adición de offset. En la siguiente figura se muestra este circuito:

![Acondicionador](/README_images/acondicionador.png)

Los símbolos de switches corresponden, en la práctica, a un solder jumper, el cual conecta la entrada con la salida solo si se unen con soldadura sus terminales. Si se conectan S1, S2 y S3 el circuito queda configurado como un buffer, lo cual, de todas formas, beneficia a la señal adquirida puesto que el buffer disminuye su impedancia. Conectando o no S1, S2 y S3 se pueden obtener distintas configuraciones: solo amplificador, solo adición de offset, o ambas. Además, los valores de las resistencias se pueden ajustar dependiendo de los sensores que se utilicen, de tal forma de fijar correctamente la ganancia y el offset, según sea el caso.


#### Generador de PWM
La generación de PWM se realiza por medio de un circuito integrado [PCA9685](https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf). La empresa [adafruit](https://www.adafruit.com/product/2928) posee un módulo autocontenido para integrar este módulo a la Raspberry Pi, así como una documentación completa y las bibliotecas para utilizarlo.


Principales características:

* 16 canales dimeables por PWM.
* 12 bits de resolución
* Voltaje de alimentación etre 2.3V a 5.5V
* Interfaz I2C


#### Driver de baja corriente

Para los canales de bajo consumo de corriente, tales como los arreglos de LEDs rojos y verdes, se utilizará el integrado [ULN2803](https://www.electroschematics.com/wp-content/uploads/2013/07/uln2803a-datasheet.pdf). Este integrado implementa un arreglo de 8 transistores tipo darlington, haciendo posible el control de hasta 8 canales en un único integrado.

Principales características:

* Arreglo de 8 canales
* Poseen alimentación común
* La corriente máxima por canal es de 500mA, pudiendo aumentar esta cantidad si se consideran canales en paralelo.

#### Driver de alta corriente
Para los canales de alto consumo se utilizará un transistor mosfet [IRF740](https://datasheet.lcsc.com/szlcsc/1808281645_Infineon-Technologies-IRF7402TRPBF_C169089.pdf). Es necesario contar con un transistor por canal. Y, para casos de alta corriente (superiores a 1A) es necesario considerar la inclusión de disipadores (heatsink) o pads de disipación que permitan una evacuación efectiva del calor.

Principales características:

* Altas frecuencias de switching
* Bajo consumo de operación
* Control de hasta 10A (ó 40A en corrientes pulsantes)
* Simple implementación

#### Sistema de distribución de poder

Como se mencionará más adelante, la alimentación que llegará al circuito electrónico implementado será de 12VDC, por lo que es necesario contar con convertidores de voltaje DC-DC para generar los distintos voltajes de alimentación que se requieren en el circuito. En particular, es necesario generar 5V y 3.3V para alimentar los circuitos analógicos y digitales, y un set de voltajes para alimentar los distintos arreglos de LEDs y el Heater. Se decidió disponer de los siguientes voltajes para este último uso: 9V, 16V, 20V y 24V. A continuación se especifican los convertidores empleados para generar cada uno de los voltajes mencionados.

##### 5V
* Integrado: [LM2596R-5.0](https://datasheet.lcsc.com/szlcsc/1811131510_HTC-Korea-TAEJIN-Tech-LM2596R-5-0_C77782.pdf)
* Tipo: Step-down, regulador switching
* Frecuencia de switcheo: 150kHz
* Corriente máxima de salida: 3A

##### 3.3V
* Integrado: [AP2112K-3.3](https://datasheet.lcsc.com/szlcsc/1809192242_Diodes-Incorporated-AP2112K-3-3TRG1_C51118.pdf)
* Tipo: LDO, regulador lineal
* Corriente máxima de salida: 600mA

##### 9V
* Integrado: [LM2696SX-ADJ](https://datasheet.lcsc.com/szlcsc/1809192335_Texas-Instruments-LM2596SX-ADJ-NOPB_C29781.pdf)
* Tipo: Step-down, regulador switching ajustable (voltaje de salida es configurable según indicaciones de conexión en el datasheet)
* Frecuencia de switcheo: 150kHz
* Corriente máxima de salida: 3A

##### 16V, 20V, 24V
* Integrado: [XL6008E1](https://datasheet.lcsc.com/szlcsc/1809200019_XLSEMI-XL6008E1_C73012.pdf)
* Tipo: Step-up, regulador switching ajustable (voltaje de salida es configurable según indicaciones de conexión en el datasheet)
* Frecuencia de switcheo: 400kHz
* Corriente máxima de salida: 3A

#### Fuente de alimentación

Dado que el circuito electrónico funcionará con alimentación DC es necesario emplear una fuente DC que se enchufe directamente a la red y que entegue un voltaje de salida continuo. En particular, se decidió emplear una [fuente DC conmutada](https://afel.cl/producto/fuente-de-poder-12v-10a-120w/). Sus principales características son:

* Voltaje de entrada: 100-120VAC / 60Hz, **200-240VAC / 50Hz**
* Voltaje de salida: 12V
* Corriente máxima de salida: 10A
* Potencia máxima de salida: 120W

## Esquemático

En la siguiente figura se muestra el diagrama de bloques del esquemático implementado

![Diagrama de bloques del esquemático](/README_images/diagrama_bloques.png)
