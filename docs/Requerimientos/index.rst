Requerimientos
--------------

Requerimientos generales
~~~~~~~~~~~~~~~~~~~~~~~~

A continuación se enlista un set de requerimientos generales del
proyecto: 1. Implementar una electrónica compatible con los componentes
actuales disponibles. 2. Proponer una solución completa al problema. 3.
Considerar diseños modulares que permitan adaptarse a parámetros
futuros.

Requerimientos específicos
~~~~~~~~~~~~~~~~~~~~~~~~~~

A continuación se enlista un set de requerimientos específicos del
proyecto: 1. Los LEDs azules empleados para iluminar la muestra
corresponden a los `Super Bright 5mm
Blue <https://www.superbrightleds.com/moreinfo/through-hole/5mm-blue-led-120-degree-viewing-angle-flat-tipped-1200-mcd/265/1192/>`__:
\* Longitud de onda: 470nm \* Forward current: 30mA @ 3.3V \* Peak
forward current: 100mA \* Max voltage forward: 3.8V

2. Actualmente, se está pensando en una placa de LEDs azules con
   distribución física del tipo circular. Esto implicaría una cantidad
   de 55 LEDs. En la siguiente imagen se muestra esta topología
   propuesta:

.. figure:: /README_images/disposicionBLUE.PNG
   :alt: Propuesta nueva disposición LEDs azules

   Propuesta nueva disposición LEDs azules

3. Los LEDs verdes empleados para la activación de genes corresponden a
   los `Kingbright
   WP7083ZGD/G <http://www.kingbrightusa.com/images/catalog/SPEC/WP7083ZGD-G.pdf>`__:

   -  Longitud de onda: 520nm
   -  Forward current (typ): 20mA @ 3.2V
   -  Peak forward current: 100mA
   -  Max voltage forward: 4V

4. Los LEDs rojos empleados para la desactivación de genes corresponden
   a los `Deep-Red 5mm
   LED <https://www.ledsupply.com/leds/5mm-led-deep-red-660nm-50-degree-viewing-angle>`__:

   -  Longitud de onda: 660nm
   -  Forward current (typ): 20mA @ 2.2V
   -  Peak forward current: 100mA
   -  Max voltage forward: 2.8V

5. Los LEDs blancos se implementan por medio de una tira LED comercial.
   Típicamente su operación se caracteriza por:

   -  Forward current: 20mA @ 12V

6. El control implementado debe corresponder a PWM, con el fin de
   regular la intensidad lumínica de los LEDs. Se opta por este control
   debido a su sencilla implementación.

7. El sistema debe contar con un sistema de distribución de potencia
   para alimentar todos los sub-módulos, LEDs y raspberry.

8. El sistema debe contar, además, con la posibilidad de leer sensores
   que permitan medir y calibrar la intensidad de luz proveniente desde
   los LEDs. Dado que el control se implementa por medio de una
   raspberry, es necesario utilizar sensores digitales o incluir en el
   diseño un ADC que permita realizar la conversión. En este último caso
   será necesaria la inclusión de una etapa que acondicione las señales
   provenientes desde los sensores.

9. El sensor de intensidad lumínica tiene que cumplir:

-  Bajo costo
-  Fácil de conseguir
-  Respuesta plana para los LED Rojo y Verde

Una alternativa es el fototransistor
`TEMT6000 <https://learn.sparkfun.com/tutorials/temt6000-ambient-light-sensor-hookup-guide/all>`__.

10. El sensor de temperatura es un NTC (termistor).
    `Aquí <https://www.adafruit.com/product/372>`__ se presenta una
    alternativa.

11. El heater es del tipo resistivo y se debe poder alimentar con 9V ó
    12V. Se debe implementar un control PWM de corriente utilizando un
    transistor. Una posible alternativa de heater es el `Film Heating
    Panel <http://www.icstation.com/heating-thin-film-polyimide-heating-plate-panel-25x50mm-b1221-p-9887.html>`__.