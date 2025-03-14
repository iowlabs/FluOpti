Descripción de problema electrónico
-----------------------------------

El sistema consiste en un dispositivo que permite observar muestras
biológicas, a las cuales se les realizan procesos de activación genética
por medio de otpogenética. En la práctica, el dispositivo consiste en
una cámara conectada a una raspberry, la que permite observar las
muestras, un set de LEDs, los que permiten realizar los procesos
optogenéticos, y la respectiva electrónica de control.

Los LEDs que se deben controlar realizan 3 tareas distintas: 1. Excitar
la muestra para poder adquirir imágenes de fluorescencia: LEDs azules.
2. Iluminar la muestra para obtener imágenes de campo claro que permitan
medir el crecimiento de las colonias bacterianas de manera apropiada:
LEDs blancos. 3. Generar estímulos para activación de procesos
optogenéticos. Estos LEDs son de longitudes de onda específicas
dependiendo del gen que se desee activar/desactivar: LEDs rojos y
verdes.

El proyecto también considera la necesidad de implementar sensores que
permitan calibrar el sistema y monitorear variables determinadas, tales
como intensidad o temperatura.

.. figure:: /README_images/Diagrama_1.PNG
   :alt: Diagrama General