# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')  # 'Agg' es un backend sin interfaz
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
import time
from PyQt5.uic import loadUi
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import  QMainWindow, QApplication, QFileDialog, QVBoxLayout, QWidget

from GUI.gui import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import cv2
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from time import sleep
from pandas import *
import numpy as np
from simple_pid import PID
import threading
import json
import datetime
import csv
import time
import sys
import collections

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('GUI/gui_test_v3.ui', self)
        self.sec = Secuenciador()
        self.sec.setWindowModality(2) # 2 = Qt.ApplicationModal
        self.dic_bloques = {}
        self.sec.senal_dic_final.connect(self.recibir_diccionario)
        self.button_aceptar.clicked.connect(self.configurar_secuenciador)
        self.pushButton_run.clicked.connect(self.comenzar_experimentos)
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)
        #aumentar fuente de status bar
        font = self.status.font()
        font.setPointSize(12)
        self.status.setFont(font)

        self.colores = {0: 'blue', 1: 'yellowgreen', 2: 'red', 3: 'lightgray'}
        self.map_color_to_label = {0: self.label_luz_azul, 1: self.label_luz_verde, 2: self.label_luz_roja, 3: self.label_luz_blanca}

    def comenzar_experimentos(self):
        self.experimentos = ExperimentosManagerThread(self.dic_bloques, self)
        self.experimentos.start()
        self.experimentos.senal_final.connect(self.experimentos_terminados)
        self.experimentos.senal_inicio_bloque.connect(self.inicio_bloque)
        self.experimentos.senal_fin_bloque.connect(self.fin_bloque)
        self.tabWidget.setEnabled(False)

    def inicio_bloque(self, bloque, t_exp):
        self.time_elapsed = 0
        print(f'Iniciando bloque {bloque}')

        # DESCOMENTAR ESTO AL PASAR EL T_EXP A MINUTOS        
        # hours, remainder = divmod(t_exp * 60, 3600)
        # minutes, seconds = divmod(remainder, 60)
        # time_format = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
        # self.status.showMessage(f'Corriendo {bloque} de duración {time_format}')

        self.status.showMessage(f'Corriendo {bloque} de duración {t_exp}')
        # crear timer para actualizar el tiempo desde el inicio del bloque
        self.bloque_timer = QtCore.QTimer()
        self.bloque_timer.setInterval(1000)
        self.bloque_timer.timeout.connect(self.updateTime)
        self.bloque_timer.start()

    def fin_bloque(self, bloque):
        print(f'Finalizando  {bloque}')
        self.status.showMessage(f'Finalizando {bloque}', 3000)
        self.bloque_timer.stop()

    def updateTime(self):
        #print('Actualizando tiempo...')
        self.time_elapsed += 1
        # convertir self.time_elapsed a formato hh:mm:ss
        hours, remainder = divmod(self.time_elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_format = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
        self.label_tiempo.setText(f'Tiempo transcurrido: {time_format}')

    def experimentos_terminados(self):
        print('Experimentos terminados')
        self.tabWidget.setEnabled(True)
        self.label_tiempo.setText('Experimentos terminados')

    def configurar_secuenciador(self):
        n_bloques = int(self.run_spinBox_bloques.value())
        self.sec.bloques_activos = n_bloques
        self.sec.show()

    def recibir_diccionario(self, diccionario):
        print('Recibiendo diccionario...')
        self.dic_bloques = diccionario
        print(self.dic_bloques)
        self.sec.close()
        self.mostrar_bloques()
        self.graficar_bloques()

    def mostrar_bloques(self):
        print('Mostrando bloques...')
        # borrar todos los objetos dentro de self.groupBox_estado_bloques
        for i in reversed(range(self.groupBox_estado_bloques.layout().count())):
            self.groupBox_estado_bloques.layout().itemAt(i).widget().setParent(None)
        # agregar los nuevos objetos
        for bloque, dic in self.dic_bloques.items():
            str_label = ""
            for key, value in dic.items():
                # label = QtWidgets.QLabel(f'{key}: {value}')
                # self.groupBox_estado_bloques.layout().addWidget(label)
                if key != "N_fotos":
                    str_label += f'{key}: {value} min\n'
                else:
                    str_label += f'{key}: {value}\n'
            new_group = QtWidgets.QGroupBox()
            new_group.setTitle(bloque)
            new_group.setStyleSheet("QGroupBox { font: bold; }")
            new_group.setLayout(QtWidgets.QVBoxLayout())
            label = QtWidgets.QLabel(str_label)
            #center label
            label.setAlignment(QtCore.Qt.AlignCenter)
            #grow font size
            font = label.font()
            font.setPointSize(10)
            label.setFont(font)
            new_group.layout().addWidget(label)
            self.groupBox_estado_bloques.layout().addWidget(new_group)

    def graficar_bloques(self):
        # Inicializar variables para la suma acumulativa
        t_exp_acum = []
        I_rojo_acum = []
        I_verde_acum = []
        T_control_acum = []
        tiempos_cambio_bloque = []
        ultimo_tiempo = 0

        # Iterar sobre los bloques en dict_sec
        for bloque, valores in self.dic_bloques.items():
            # Obtener el valor de t_exp del bloque actual
            if bloque == 'bloque 1':
                t_exp = valores['t_exp'] + 1
            else:
                t_exp = valores['t_exp']
            # Crear un array de tiempo acumulado
            t_exp_acum += range(ultimo_tiempo, t_exp + ultimo_tiempo)
            tiempos_cambio_bloque.append(t_exp_acum[-1])

            # Crear un array de intensidad de LED Rojo acumulado
            I_rojo_acum += [valores['I_rojo']] * t_exp
            # Crear un array de intensidad de LED Verde acumulado
            I_verde_acum += [valores['I_verde']] * t_exp
            # Crear un array de temperatura de control acumulado
            T_control_acum += [valores['t_control']] * t_exp
            # Actualizar el último tiempo
            ultimo_tiempo += t_exp

        print(f't_exp_acum: {t_exp_acum}')
        print(f'I_rojo_acum: {I_rojo_acum}')
        print(f'I_verde_acum: {I_verde_acum}')
        print(f'T_control_acum: {T_control_acum}')
        # graficar
        for i in range(3):
            self.grafico_bloques.canvas.axes[i].clear()

        # self.grafico_bloques.canvas.axes[0].plot(t_exp_acum, I_rojo_acum, label='Rojo', color='red')
        # self.grafico_bloques.canvas.axes[1].plot(t_exp_acum, I_verde_acum, label='Verde', color='green')

        self.grafico_bloques.canvas.axes[0].step(t_exp_acum, I_rojo_acum, where='post', label='Rojo', color='red')
        self.grafico_bloques.canvas.axes[1].step(t_exp_acum, I_verde_acum, where='post', label='Verde', color='green')

        # self.grafico_bloques.canvas.axes[2].step(t_exp_acum, T_control_acum, where='post', label='Control', color='blue')
        self.grafico_bloques.canvas.axes[2].plot(t_exp_acum, T_control_acum, label='Control')
        self.grafico_bloques.canvas.axes[2].set_xticks(t_exp_acum)

        for tiempo_cambio in tiempos_cambio_bloque:
            self.grafico_bloques.canvas.axes[0].axvline(x=tiempo_cambio, color='gray', linestyle='--', linewidth=0.8)
            self.grafico_bloques.canvas.axes[1].axvline(x=tiempo_cambio, color='gray', linestyle='--', linewidth=0.8)
            self.grafico_bloques.canvas.axes[2].axvline(x=tiempo_cambio, color='gray', linestyle='--', linewidth=0.8)

        # Añadir títulos encima de la figura
        for i, tiempo_cambio in enumerate(tiempos_cambio_bloque, start=1):
            bloque_text = f'Bloque {i}'
            # mitad del tiempo del bloque
            if i == 1:
                pos_x = tiempo_cambio / 2
            else:
                pos_x = (tiempo_cambio + tiempos_cambio_bloque[i - 2]) / 2

                # Añadir área bajo la curva

            self.grafico_bloques.canvas.axes[0].fill_between(t_exp_acum[:tiempo_cambio], 0, I_rojo_acum[:tiempo_cambio], alpha=0.3, color='red')
            self.grafico_bloques.canvas.axes[1].fill_between(t_exp_acum[:tiempo_cambio], 0, I_verde_acum[:tiempo_cambio], alpha=0.3, color='green')
            #self.grafico_bloques.canvas.axes[2].fill_between(t_exp_acum[:tiempo_cambio], 0, T_control_acum[:tiempo_cambio], alpha=0.3, color='blue')


            #self.grafico_bloques.canvas.axes[0].fill_between(t_exp_acum[:tiempo_cambio + 1], 0, I_rojo_acum[:tiempo_cambio], alpha=0.3, color='red')
            #self.grafico_bloques.canvas.axes[1].fill_between(t_exp_acum[:tiempo_cambio + 1], 0, I_verde_acum[:tiempo_cambio], alpha=0.3, color='green')
            
            #self.grafico_bloques.canvas.axes[2].fill_between(t_exp_acum[:tiempo_cambio + 1], 0, T_control_acum[:tiempo_cambio], alpha=0.3, color='blue')

            self.grafico_bloques.canvas.axes[0].text(pos_x, max(I_rojo_acum) + 2, bloque_text, rotation=0, ha='center', va='bottom')

        # Configurar leyendas y etiquetas
        self.grafico_bloques.canvas.axes[0].legend()
        self.grafico_bloques.canvas.axes[0].set_ylabel('LED Rojo')

        self.grafico_bloques.canvas.axes[1].legend()
        self.grafico_bloques.canvas.axes[1].set_ylabel('LED Verde')

        self.grafico_bloques.canvas.axes[2].legend()
        self.grafico_bloques.canvas.axes[2].set_xlabel('Tiempo acumulado (horas)')
        self.grafico_bloques.canvas.axes[2].set_ylabel('T Control (°C)')

        # Actualizar la visualización del lienzo
        # dejar resolucion completa en eje x
        self.grafico_bloques.canvas.axes[0].set_xlim([0, t_exp_acum[-1]])
        self.grafico_bloques.canvas.draw()
        


    def actualizar_estilo_led(self, label, estado, color):
        # Actualizar el estilo del QLabel para representar el estado del LED
        if estado:
            label.setStyleSheet(f'QLabel {{ background-color: {color}; border-radius: 50px; }}')
            print(f'stylesheet LED {color}')
        else:
            label.setStyleSheet('QLabel {}')

    def LEDOn(self, channel):
        print(f"Encendiendo LED {channel} desde app")
        color = self.colores[channel]
        label = self.map_color_to_label[channel]
        self.actualizar_estilo_led(label, True, color)

    def LEDOff(self, channel):
        print(f"Apagando LED {channel} desde app")
        color = self.colores[channel]
        label = self.map_color_to_label[channel]
        self.actualizar_estilo_led(label, False, color)

class Secuenciador(QMainWindow):
    senal_dic_final = QtCore.pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        loadUi('GUI/secuenciador_v3.ui', self)
        #create status bar
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage('Secuenciador de luces', 3000)
        self.tabs = [self.tab_1, self.tab_2, self.tab_3, self.tab_4, self.tab_5, self.tab_6]
        self.actualizar_dics()
        
        self.button_guardar.clicked.connect(self.guardar_secuenciador)
        
    # redefinir show() para inicializar los tabs
        
    def actualizar_dics(self):
        self.dict_b1 = {'t_exp': self.b1_t_exp.value(), 't_control' : self.b1_T_control.value(), 'I_rojo': self.b1_slider_led_rojo.value(), 'I_verde': self.b1_slider_led_verde.value()}
        self.dict_b2 = {'t_exp': self.b2_t_exp.value(), 't_control' : self.b2_T_control.value(), 'I_rojo': self.b2_slider_led_rojo.value(), 'I_verde': self.b2_slider_led_verde.value()}
        self.dict_b3 = {'t_exp': self.b3_t_exp.value(), 't_control' : self.b3_T_control.value(), 'I_rojo': self.b3_slider_led_rojo.value(), 'I_verde': self.b3_slider_led_verde.value()}
        self.dict_b4 = {'t_exp': self.b4_t_exp.value(), 't_control' : self.b4_T_control.value(), 'I_rojo': self.b4_slider_led_rojo.value(), 'I_verde': self.b4_slider_led_verde.value()}
        self.dict_b5 = {'t_exp': self.b5_t_exp.value(), 't_control' : self.b5_T_control.value(), 'I_rojo': self.b5_slider_led_rojo.value(), 'I_verde': self.b5_slider_led_verde.value()}
        self.dict_b6 = {'t_exp': self.b6_t_exp.value(), 't_control' : self.b6_T_control.value(), 'I_rojo': self.b6_slider_led_rojo.value(), 'I_verde': self.b6_slider_led_verde.value()}
        self.dict_sec = {'bloque 1': self.dict_b1, 'bloque 2': self.dict_b2, 'bloque 3': self.dict_b3, 'bloque 4': self.dict_b4, 'bloque 5': self.dict_b5, 'bloque 6': self.dict_b6}

    def show(self):
        #herencia de show original
        super().show()
        #inicializar tabs
        for i in range(len(self.tabs)):
            if i < self.bloques_activos:
                self.tabs[i].setEnabled(True)
            else:
                self.tabs[i].setEnabled(False)

    def guardar_secuenciador(self):
        print('Guardardando secuenciador...')
        self.actualizar_dics()
        bloques = ["bloque 1", "bloque 2", "bloque 3", "bloque 4", "bloque 5", "bloque 6"]
        dic_final = {}
        for i in range(self.bloques_activos):
            dic_final[bloques[i]] = self.dict_sec[bloques[i]]

        self.senal_dic_final.emit(dic_final)
        return dic_final
 

class LedThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, color, duracion, tiempo_inicial, channel, app):
        super(LedThread, self).__init__()
        self.color = color
        self.duracion = duracion
        self.tiempo_inicial = tiempo_inicial
        self.channel = channel
        self.app = app

    def run(self):
        time.sleep(self.tiempo_inicial)
        #time.sleep(self.tiempo_inicial * 60)

        mensaje_encendido = f"{self.tiempo_inicial:.2f}s - Encendiendo LED {self.color}"
        self.update_signal.emit(mensaje_encendido)
        self.app.LEDOn(self.channel)
        print(mensaje_encendido)

        time.sleep(self.duracion)
        #time.sleep(self.duracion * 60)
        tiempo_actual = self.tiempo_inicial + self.duracion
        mensaje_apagado = f"{tiempo_actual:.2f}s - Apagando LED {self.color}"
        self.update_signal.emit(mensaje_apagado)
        self.app.LEDOff(self.channel)
        print(mensaje_apagado)

class ExperimentoThread(QThread):
    def __init__(self, bloque, app):
        super(ExperimentoThread, self).__init__()
        self.bloque = bloque
        self.app = app

    def run(self):
        t_exp = self.bloque['t_exp']
        threads = []
        #map chanel to color
        channel_dic = {'roja': 2, 'verde': 1, 'azul': 0, 'blanca': 3}
        for color in ['roja', 'verde', 'azul', 'blanca']:
            ti_color = self.bloque[f'ti_{color}']
            td_color = self.bloque[f'td_{color}']

            if ti_color >= 0 and td_color > 0:
                led_thread = LedThread(color, td_color, ti_color, channel_dic[color], self.app)
                led_thread.update_signal.connect(self.actualizar_interfaz)
                threads.append(led_thread)
                led_thread.start()

        time.sleep(t_exp) # Esperar el tiempo total del experimento
        #time.sleep(t_exp * 60)  
        
        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.wait()

    def actualizar_interfaz(self, mensaje):
        pass
        #print("mensaje: ", mensaje)


class ExperimentosManagerThread(QThread):
    senal_final = pyqtSignal()
    senal_inicio_bloque = pyqtSignal(str, int)
    senal_fin_bloque = pyqtSignal(str)
    def __init__(self, bloques, app):
        super(ExperimentosManagerThread, self).__init__()
        self.bloques = bloques
        self.app = app

    def run(self):
        for nombre_bloque, bloque in self.bloques.items():
            print(f"Ejecutando experimento en {nombre_bloque}")
            experimento_thread = ExperimentoThread(bloque, self.app)
            experimento_thread.start()
            self.senal_inicio_bloque.emit(nombre_bloque, int(bloque["t_exp"]))
            experimento_thread.wait()
            self.senal_fin_bloque.emit(nombre_bloque)

        self.senal_final.emit()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())