Resumen de características de la solución propuesta
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Las principales características de la solución propuesta son:

1. Adaptabilidad: La placa total solo se controla por medio de un bus
   I2C (3 pines), independiente de la cantidad de LEDs y sensores que se
   deseen utilizar.

2. Integración: La disposición de canales de control PWM permite
   integrar tanto las soluciones existentes como soluciones creadas por
   distintos fabricantes.

3. Escalabilidad: Gracias a la utilización del protocolo I2C, es posible
   controlar múltiples de estas placas con una sola Raspberry Pi (o un
   solo microcontrolador/procesador en general). Si se integran dos
   placas en serie se puede llegar a disponer de 32 canales de control
   de LEDs y 8 canales de sensores analógicos.

A continuación, se describen en detalle los módulos a implementar. Es
importante mencionar que se utilizó como guía el `documento
tutorial <https://www.overleaf.com/4759732231nspqcngnnhdq>`__ generado
en el marco de este proyecto.