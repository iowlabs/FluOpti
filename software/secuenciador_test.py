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
        loadUi('GUI/gui_test.ui', self)
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
        loadUi('GUI/secuenciador_v2.ui', self)
        #create status bar
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage('Secuenciador de luces', 3000)
        self.tabs = [self.tab_1, self.tab_2, self.tab_3, self.tab_4, self.tab_5, self.tab_6]
        
        
        self.bloques_activos = 0

        self.spinBoxes_b1 = [self.b1_spinBox_t_exp, self.b1_spinBox_n_fotos, self.b1_spinBox_ti_roja, self.b1_spinBox_td_roja,
                        self.b1_spinBox_ti_verde, self.b1_spinBox_td_verde, self.b1_spinBox_ti_azul, self.b1_spinBox_td_azul,
                        self.b1_spinBox_ti_blanca, self.b1_spinBox_td_blanca]
        self.spinBoxes_b2 = [self.b2_spinBox_t_exp, self.b2_spinBox_n_fotos, self.b2_spinBox_ti_roja, self.b2_spinBox_td_roja, 
                        self.b2_spinBox_ti_verde, self.b2_spinBox_td_verde, self.b2_spinBox_ti_azul, self.b2_spinBox_td_azul,
                        self.b2_spinBox_ti_blanca, self.b2_spinBox_td_blanca]
        self.spinBoxes_b3 = [self.b3_spinBox_t_exp, self.b3_spinBox_n_fotos, self.b3_spinBox_ti_roja, self.b3_spinBox_td_roja,
                        self.b3_spinBox_ti_verde, self.b3_spinBox_td_verde, self.b3_spinBox_ti_azul, self.b3_spinBox_td_azul,
                        self.b3_spinBox_ti_blanca, self.b3_spinBox_td_blanca]
        self.spinBoxes_b4 = [self.b4_spinBox_t_exp, self.b4_spinBox_n_fotos, self.b4_spinBox_ti_roja, self.b4_spinBox_td_roja,
                        self.b4_spinBox_ti_verde, self.b4_spinBox_td_verde, self.b4_spinBox_ti_azul, self.b4_spinBox_td_azul,
                        self.b4_spinBox_ti_blanca, self.b4_spinBox_td_blanca]
        self.spinBoxes_b5 = [self.b5_spinBox_t_exp, self.b5_spinBox_n_fotos, self.b5_spinBox_ti_roja, self.b5_spinBox_td_roja,
                        self.b5_spinBox_ti_verde, self.b5_spinBox_td_verde, self.b5_spinBox_ti_azul, self.b5_spinBox_td_azul,
                        self.b5_spinBox_ti_blanca, self.b5_spinBox_td_blanca]
        self.spinBoxes_b6 = [self.b6_spinBox_t_exp, self.b6_spinBox_n_fotos, self.b6_spinBox_ti_roja, self.b6_spinBox_td_roja,
                        self.b6_spinBox_ti_verde, self.b6_spinBox_td_verde, self.b6_spinBox_ti_azul, self.b6_spinBox_td_azul,
                        self.b6_spinBox_ti_blanca, self.b6_spinBox_td_blanca]

        self.button_guardar.clicked.connect(self.guardar_secuenciador)
        self.button_b1_update.clicked.connect(lambda: self.update_bloque(self.spinBoxes_b1, self.Plot_b1))
        self.button_b2_update.clicked.connect(lambda: self.update_bloque(self.spinBoxes_b2, self.Plot_b2))
        self.button_b3_update.clicked.connect(lambda: self.update_bloque(self.spinBoxes_b3, self.Plot_b3))
        self.button_b4_update.clicked.connect(lambda: self.update_bloque(self.spinBoxes_b4, self.Plot_b4))
        self.button_b5_update.clicked.connect(lambda: self.update_bloque(self.spinBoxes_b5, self.Plot_b5))
        self.button_b6_update.clicked.connect(lambda: self.update_bloque(self.spinBoxes_b6, self.Plot_b6))


    # redefinir show() para inicializar los tabs
    def show(self):
        #herencia de show original
        super().show()
        #inicializar tabs
        for i in range(len(self.tabs)):
            if i < self.bloques_activos:
                self.tabs[i].setEnabled(True)
            else:
                self.tabs[i].setEnabled(False)


    def update_bloque(self, spinBoxes, plot):
        # spinBoxes_b6 = [self.b6_spinBox_t_exp, self.b6_spinBox_n_fotos, self.b6_spinBox_ti_roja, self.b6_spinBox_td_roja,
        #                 self.b6_spinBox_ti_verde, self.b6_spinBox_td_verde, self.b6_spinBox_ti_azul, self.b6_spinBox_td_azul,
        #                 self.b6_spinBox_ti_blanca, self.b6_spinBox_td_blanca]

        dict = {'t_exp': int(spinBoxes[0].value()), 'N_fotos': int(spinBoxes[1].value()), 'ti_roja': int(spinBoxes[2].value()), 'td_roja': int(spinBoxes[3].value()),
                'ti_verde': int(spinBoxes[4].value()), 'td_verde': int(spinBoxes[5].value()), 'ti_azul': int(spinBoxes[6].value()), 'td_azul': int(spinBoxes[7].value()),
                'ti_blanca': int(spinBoxes[8].value()), 'td_blanca': int(spinBoxes[9].value())}
        
        try:

            self.validar_diccionario("bloque actual", dict)

            t_exp = int(spinBoxes[0].value())
            N_fotos = int(spinBoxes[1].value())
            lights_on_times = [[(int(spinBoxes[i].value()), int(spinBoxes[i].value()) + int(spinBoxes[i+1].value()))] for i in range(2, len(spinBoxes), 2)]
            print(t_exp, N_fotos, lights_on_times)

            # Caso 1: Pulso equiespaciado
            #N_fotos = 10
            pulse_times = [int(t_exp / N_fotos) * i for i in range(N_fotos)]

            bins = list(range(0, t_exp + 1))
            lights_data = [np.zeros(len(bins) - 1) for _ in range(len(lights_on_times))]

            for i, on_times in enumerate(lights_on_times):
                for start, end in on_times:
                    start_bin = bins.index(start)
                    end_bin = bins.index(end)
                    lights_data[i][start_bin:end_bin] = 1

            print(lights_data)

            pulse_data = np.zeros(len(bins) - 1)
            for pulse_time in pulse_times:
                pulse_bin = bins.index(pulse_time)
                pulse_data[pulse_bin] = 1

            colors = ['red', 'green', 'blue', 'gray', 'black']  # Rojo, Verde, Azul, Blanco, Gris
            labels = ['red', 'green', 'blue', 'white', 'black']

            axes = plot.canvas.figure.get_axes()
            for ax in axes:
                ax.clear()

            for i, ax in enumerate(plot.canvas.axes):
                if i < len(lights_data):
                    ax.fill_between(bins[:-1], 0, lights_data[i], color=colors[i], alpha=0.5, label=f'Light {labels[i]}', step='post')
                    ax.set_yticks([0, 1])
                    ax.set_yticklabels(['', ''])
                    ax.legend()
                else:
                    ax.fill_between(bins[:-1], 0, pulse_data, color=colors[i], alpha=0.5, label='Cámara', step='post')
                    ax.set_yticks([0, 1])
                    ax.set_yticklabels(['', ''])
                    ax.legend()
            #set x axis tittle for plot
            axes[-1].set_xlabel('Tiempo [min]')
            plot.canvas.draw()
        
        except ValueError as e:
            print(e)
            self.status.showMessage(str(e), 3000)


        
    def guardar_secuenciador(self):
        print('Guardardando secuenciador...')
        dict_b1 = {'t_exp': int(self.spinBoxes_b1[0].value()), 'N_fotos': int(self.spinBoxes_b1[1].value()), 'ti_roja': int(self.spinBoxes_b1[2].value()), 'td_roja': int(self.spinBoxes_b1[3].value()),
                'ti_verde': int(self.spinBoxes_b1[4].value()), 'td_verde': int(self.spinBoxes_b1[5].value()), 'ti_azul': int(self.spinBoxes_b1[6].value()), 'td_azul': int(self.spinBoxes_b1[7].value()),
                'ti_blanca': int(self.spinBoxes_b1[8].value()), 'td_blanca': int(self.spinBoxes_b1[9].value())}
        dict_b2 = {'t_exp': int(self.spinBoxes_b2[0].value()), 'N_fotos': int(self.spinBoxes_b2[1].value()), 'ti_roja': int(self.spinBoxes_b2[2].value()), 'td_roja': int(self.spinBoxes_b2[3].value()),
                'ti_verde': int(self.spinBoxes_b2[4].value()), 'td_verde': int(self.spinBoxes_b2[5].value()), 'ti_azul': int(self.spinBoxes_b2[6].value()), 'td_azul': int(self.spinBoxes_b2[7].value()),
                'ti_blanca': int(self.spinBoxes_b2[8].value()), 'td_blanca': int(self.spinBoxes_b2[9].value())}
        dict_b3 = {'t_exp': int(self.spinBoxes_b3[0].value()), 'N_fotos': int(self.spinBoxes_b3[1].value()), 'ti_roja': int(self.spinBoxes_b3[2].value()), 'td_roja': int(self.spinBoxes_b3[3].value()),
                'ti_verde': int(self.spinBoxes_b3[4].value()), 'td_verde': int(self.spinBoxes_b3[5].value()), 'ti_azul': int(self.spinBoxes_b3[6].value()), 'td_azul': int(self.spinBoxes_b3[7].value()),
                'ti_blanca': int(self.spinBoxes_b3[8].value()), 'td_blanca': int(self.spinBoxes_b3[9].value())}
        dict_b4 = {'t_exp': int(self.spinBoxes_b4[0].value()), 'N_fotos': int(self.spinBoxes_b4[1].value()), 'ti_roja': int(self.spinBoxes_b4[2].value()), 'td_roja': int(self.spinBoxes_b4[3].value()),
                'ti_verde': int(self.spinBoxes_b4[4].value()), 'td_verde': int(self.spinBoxes_b4[5].value()), 'ti_azul': int(self.spinBoxes_b4[6].value()), 'td_azul': int(self.spinBoxes_b4[7].value()),
                'ti_blanca': int(self.spinBoxes_b4[8].value()), 'td_blanca': int(self.spinBoxes_b4[9].value())}
        dict_b5 = {'t_exp': int(self.spinBoxes_b5[0].value()), 'N_fotos': int(self.spinBoxes_b5[1].value()), 'ti_roja': int(self.spinBoxes_b5[2].value()), 'td_roja': int(self.spinBoxes_b5[3].value()),
                'ti_verde': int(self.spinBoxes_b5[4].value()), 'td_verde': int(self.spinBoxes_b5[5].value()), 'ti_azul': int(self.spinBoxes_b5[6].value()), 'td_azul': int(self.spinBoxes_b5[7].value()),
                'ti_blanca': int(self.spinBoxes_b5[8].value()), 'td_blanca': int(self.spinBoxes_b5[9].value())}
        dict_b6 = {'t_exp': int(self.spinBoxes_b6[0].value()), 'N_fotos': int(self.spinBoxes_b6[1].value()), 'ti_roja': int(self.spinBoxes_b6[2].value()), 'td_roja': int(self.spinBoxes_b6[3].value()),
                'ti_verde': int(self.spinBoxes_b6[4].value()), 'td_verde': int(self.spinBoxes_b6[5].value()), 'ti_azul': int(self.spinBoxes_b6[6].value()), 'td_azul': int(self.spinBoxes_b6[7].value()),
                'ti_blanca': int(self.spinBoxes_b6[8].value()), 'td_blanca': int(self.spinBoxes_b6[9].value())}
        
        dict_sec = {'bloque1': dict_b1, 'bloque2': dict_b2, 'bloque3': dict_b3, 'bloque4': dict_b4, 'bloque5': dict_b5, 'bloque6': dict_b6}
        bloques = ["bloque1", "bloque2", "bloque3", "bloque4", "bloque5", "bloque6"]
        dic_final = {}
        for i in range(self.bloques_activos):
            dic_final[bloques[i]] = dict_sec[bloques[i]]

        validacion = self.validar_dict_sec(dic_final)
        if validacion:
            print('Diccionario válido')
            # cerrar ventana
            #self.close()
            self.senal_dic_final.emit(dic_final)
            return dic_final
        else:
            print('Diccionario inválido')
            return None
       

       
    def validar_diccionario(self, bloque, diccionario):
        t_exp = diccionario['t_exp']
        ti_roja = diccionario['ti_roja']
        td_roja = diccionario['td_roja']
        ti_verde = diccionario['ti_verde']
        td_verde = diccionario['td_verde']
        ti_azul = diccionario['ti_azul']
        td_azul = diccionario['td_azul']
        ti_blanca = diccionario['ti_blanca']
        td_blanca = diccionario['td_blanca']

        # Verificar condiciones de error
        if ti_roja > t_exp or (ti_roja + td_roja) > t_exp:
            raise ValueError(f"Error en {bloque}: El tiempo total excede t_exp.")
        elif ti_verde > t_exp or (ti_verde + td_verde) > t_exp:
            raise ValueError(f"Error en {bloque}: El tiempo total excede t_exp.")
        elif ti_azul > t_exp or (ti_azul + td_azul) > t_exp:
            raise ValueError(f"Error en {bloque}: El tiempo total excede t_exp.")
        elif ti_blanca > t_exp or (ti_blanca + td_blanca) > t_exp:
            raise ValueError(f"Error en {bloque}: El tiempo total excede t_exp.")

    def validar_dict_sec(self, dict_sec):
        for bloque, diccionario in dict_sec.items():
            try:
                self.validar_diccionario(bloque, diccionario)
            except ValueError as e:
                print(e)  # Maneja el error como desees, por ejemplo, loguearlo o lanzar una excepción más específica.
                #self.status.showMessage('Secuenciador de luces', 3000)
                self.status.showMessage(str(e), 3000)
                return False
        return True

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