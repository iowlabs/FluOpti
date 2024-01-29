from hardware.FluOpti import FluOpti
from time import sleep,time
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

flu = FluOpti()

flu.updateTemps()

setTemp1 = 65
setTemp2 = 25

flu.setTempSampleTime(1)
flu.setTempSP(1,setTemp1)
flu.setTempSP(2,setTemp2)

flu.LEDSetPWR('H1',50)
flu.LEDon('H1')

flu.LEDSetPWR('H2',50)
flu.LEDon('H2')

sleep(5)

print('Acabo Prueba de conexion')

flu.LEDoff('H1')
flu.LEDoff('H2')

t1 = flu.adc.get_temps()[0]
t2 = flu.adc.get_temps()[1]

print(t1)
# Inicializacion
tiempo_inicial = time()
datos_tiempo = []
datos_temperatura = []

flu.startTempCtrl()


# Duracion total en segundos
minutos = 17
duracion_total = minutos * 60

try:
    while time() - tiempo_inicial < duracion_total:
        # Obtener tiempo actual y temperatura
        tiempo_actual = time() - tiempo_inicial
        if flu.adc.get_temps()[0]:
         temperatura_actual = flu.adc.get_temps()[0]

        # Almacenar datos
        datos_tiempo.append(tiempo_actual)
        datos_temperatura.append(temperatura_actual)

        # Esperar 1 segundo
        sleep(1)

except KeyboardInterrupt:
    # Detener la ejecucion si se presiona Ctrl+C
    pass

flu.stopTempCtrl()

# Guardar los datos en un archivo CSV
datos_guardar = np.column_stack((datos_tiempo, datos_temperatura))
np.savetxt('datos_temperatura.csv', datos_guardar, delimiter=',', header='Tiempo,Temperatura', comments='')


# Graficar los datos
plt.plot(datos_tiempo, datos_temperatura, label='Temperatura')
plt.axhline(y=setTemp1, color='r', linestyle='--', label=f'Temperatura de referencia ({setTemp1} C)')
plt.xlabel('Tiempo (segundos)')
plt.ylabel('Temperatura')
plt.title('Grafico de Tiempo vs Temperatura')
plt.legend()

plt.ylim(0, 70)
plt.show()
