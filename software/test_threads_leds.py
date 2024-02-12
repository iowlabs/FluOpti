import threading
import time

def prender_led(color, duracion, tiempo_inicial):
    time.sleep(tiempo_inicial)
    print(f"{tiempo_inicial:.2f}s - Encendiendo LED {color}")
    time.sleep(duracion)
    tiempo_actual = tiempo_inicial + duracion
    print(f"{tiempo_actual:.2f}s - Apagando LED {color}")
    return tiempo_actual

def ejecutar_experimento(bloque):
    t_exp = bloque['t_exp']
    tiempo_actual = 0
    threads = []

    for color in ['roja', 'verde', 'azul', 'blanca']:
        ti_color = bloque[f'ti_{color}']
        td_color = bloque[f'td_{color}']

        if ti_color >= 0 and td_color > 0:
            thread = threading.Thread(target=prender_led, args=(color, td_color, ti_color))
            thread.start()
            threads.append(thread)

    # Esperar el tiempo total del experimento
    time.sleep(t_exp)

    # Esperar a que todos los hilos terminen
    for thread in threads:
        thread.join()

# Diccionarios de ejemplo
bloques = {
    'bloque1': {'t_exp': 10, 'N_fotos': 0, 'ti_roja': 2, 'td_roja': 1, 'ti_verde': 0, 'td_verde': 1, 'ti_azul': 2, 'td_azul': 6, 'ti_blanca': 6, 'td_blanca': 1},
    'bloque2': {'t_exp': 3, 'N_fotos': 0, 'ti_roja': 0, 'td_roja': 0, 'ti_verde': 1, 'td_verde': 2, 'ti_azul': 0, 'td_azul': 0, 'ti_blanca': 0, 'td_blanca': 0},
    # Agrega más bloques si es necesario
}

# Ejecutar experimentos para cada bloque
for nombre_bloque, bloque in bloques.items():
    print(f"Ejecutando experimento en {nombre_bloque}")
    ejecutar_experimento(bloque)
