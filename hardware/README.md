# FluOpti Electrónica

FluOpti es una dispositivo controlador de LEDs para aplicaciones optogenéticas dentro del contexto del proyecto FluOpti.

La placa desarrollada contiene la electrónica necesaria para controlar fuentes de iluminación de alto consumo basadas en LEDS. Dependiendo de la cantidad de LEDs utilizadas y el tipo de conexión en que se dispongan estas matrices de LEDs pueden variar tanto en consumo como el el voltaje de operación.

Es por esto que la electrónica diseñada fue desarrollada considerando flexibilidad en su implementación para abordar un gran  numero de escenarios.


Cuenta con 4 canales de alta potencia para aborar cargas de 24 20 16 12 V configurables y potencias de ahasta



### Features

 La placa cuenta principalmente con 4 canales para controlar canales de LEDS

 - Canal de alta potencia para LEDs azules
 - 3 canales de baja potencia para LEDs Rojos, Verdes, Blancas.

Adicionalmente la placa implementa un controlador de temperatura, para esto cuenta con la electrónica necesaria para drivear 2 heaters resistivos, y con la capacidad de conectar hasta 4 sensores de temperatura NTC analógicos.

## Descripción de Hardware

El esquema presentado en la siguiente figura presenta una descripción general de la estructura del hardware desarrollado.  


![Esquema de la solución electrónica propuesta](/README_images/solución_propuesta.png)


El principal criterio de diseño considerado es la modularidad, con el objetivo de poder entregar una solución adaptable y escalable. El esquema general consiste en un módulo que genera señales PWM, el cual es controlado por protocolo serial I2C. Este módulo genera 16 señales de PWM permitiendo controlar hasta 16 canales. Estas señales PWM controlan los módulos driver que se encargan de adaptarse a los requerimientos de corriente y voltaje de las cargas asociadas. Cada driver puede poseer uno o más canales dependiendo de la cantidad de subcircuitos independientes que se deseen controlar por tipo de LED. Del mismo modo, algunas de estas señales de control PWM fueron dejadas a disposición del usuario en caso que necesite controlar una placa con driver ya existente, como es el caso de este proyecto (compatibilidad con diseños anteriores).

El otro bloque importante es el sistema de distribución de poder, el cual se encarga de generar todos los voltajes necesarios para los distintos bloques y etapas del circuito, dependiendo de cada requerimiento. La idea principal es que la placa reciba una única alimentación y que, internamente, genere los distintos voltajes y corrientes, contribuyendo, así, a la adaptabilidad de la solución.

Por último, la placa considera la inclusión de un ADC de 4 canales, controlado por I2C, el cual permite leer hasta 4 sensores analógicos para implementar los sensores de corriente. Es necesario contar con un ADC, ya que la Raspberry Pi no cuenta con ADC. Esto permite otorgar una alta adaptabilidad, ya que es posible conectar distintos tipos de sensores analógicos, dependiendo de la aplicación. Para esto, la placa considera etapas de acondicionamiento de señal, las cuales se deben configurar para el sensor específico.

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
