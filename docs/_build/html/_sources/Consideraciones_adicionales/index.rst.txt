Consideraciones de diseño adicionales
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Consideraciones de operación: El dispositivo debe ser diseñado para
   funcionar en espacios interiores y dentro de una cápsula cerrada, en
   la se realiza el análisis de las muestras, por lo que no es necesaria
   la resistencia al agua o a condiciones de humedad extremas. La placa
   estará, además, dentro de una caja, por lo que tampoco estará
   expuesta a polvo u otros contaminantes. Una vez instalado el
   dispositivo, este permanecerá siempre en el mismo lugar (a menos que
   se deba extraer por alguna situación en particular), por lo que no es
   necesario que el diseño considere la exposición a posibles golpes o
   vibraciones muy significativas.

2. La única etapa del circuito que puede significar un peligro para el
   usuario es la alimentación, puesto que esta proviene desde la red
   eléctrica, por lo cual es prudente que la carcasa del producto cumpla
   con normas acorde al voltaje y corriente de operación, por ejemplo,
   IP67. Sin embargo, esta protección será ajena al circuito mismo. Es
   pertinente, de todas formas, la inclusión de disipadores en algunos
   integrados, en el caso que operen con altas corrientes. Esto, para
   evitar fallas durante la operación o incluso que se quemen
   componentes.

Propuesta


Teniendo presente los requerimientos planteados en la sección anterior
se propone una solución basada en el siguiente esquema

.. figure:: ../README_images/solución_propuesta.png
   :alt: Esquema de la solución electrónica propuesta

   Esquema de la solución electrónica propuesta

El principal criterio de diseño considerado es la modularidad, con el
objetivo de poder entregar una solución adaptable y escalable. Los
parámetros prácticos de elección de componentes dependen de los
requerimientos específicos del sistema. El esquema general consiste en
un módulo que genera señales PWM, el cual es controlado por protocolo
serial I2C. Este módulo genera 16 señales de PWM permitiendo controlar
hasta 16 canales. Estas señales PWM controlan los módulos driver. Estos
últimos ajustan la señal PWM a los requerimientos que necesitan los
distintos tipos de circuitos de LEDs. Cada driver puede poseer uno o más
canales dependiendo de la cantidad de subcircuitos independientes que se
deseen controlar por tipo de LED. Del mismo modo, algunas de estas
señales de control PWM pueden dejarse a disposición del usuario en caso
que necesite controlar una placa con driver ya existente, como es el
caso de este proyecto.

El otro bloque importante es el sistema de distribución de poder, el
cual se encarga de generar todos los voltajes necesarios para los
distintos bloques y etapas del circuito, dependiendo de cada
requerimiento. La idea principal es que la placa reciba una única
alimentación y que, internamente, genere los distintos voltajes y
corrientes, contribuyendo, así, a la adaptabilidad de la solución.

Por último, la placa considera la inclusión de un ADC de 4 canales,
controlado por I2C, el cual permite leer hasta 4 sensores analógicos. Es
necesario contar con un ADC, ya que la Raspberry Pi no cuenta con ADC.
Esto permite otorgar una alta adaptabilidad, ya que es posible conectar
distintos tipos de sensores analógicos, dependiendo de la aplicación.
Para esto, la placa considera etapas de acondicionamiento de señal, las
cuales se deben configurar para el sensor específico.