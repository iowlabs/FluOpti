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
        self.pat = PatronConfig()
        self.pat.setWindowModality(2)
        self.dic_bloques = {}
        self.sec.senal_dic_final.connect(self.recibir_diccionario)
        self.button_aceptar.clicked.connect(self.configurar_secuenciador)
        self.pat.senal_config_ready.connect(self.recibir_patrones)
        self.button_fotos.clicked.connect(self.configurar_patrones)
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
        self.experimentos.senal_inicio_total.connect(self.inicio_total_experimentos)
        self.experimentos.senal_fin_bloque.connect(self.fin_bloque)
        self.tabWidget.setEnabled(False)

    def inicio_total_experimentos(self, tiempo_total):

        self.tiempo_total_exp = tiempo_total
        self.time_elapsed = 0

        self.bloque_timer = QtCore.QTimer()
        self.bloque_timer.setInterval(1000)
        self.bloque_timer.timeout.connect(self.updateTime)
        self.bloque_timer.start()

    def inicio_bloque(self, bloque, t_exp):
        #self.time_elapsed = 0
        print(f'Iniciando bloque {bloque}')
        self.status.showMessage(f'Corriendo {bloque} de duración {t_exp:02} horas')
        

    def fin_bloque(self, bloque):
        print(f'Finalizando  {bloque}')
        self.status.showMessage(f'Finalizando {bloque}', 3000)

    def updateTime(self):
        #print('Actualizando tiempo...')
        self.time_elapsed += 1
        # convertir self.time_elapsed a formato hh:mm:ss
        hours, remainder = divmod(self.time_elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_format = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
        string_label = "Tiempo transcurrido: {} / {}:00:00".format(time_format, self.tiempo_total_exp)
        self.label_tiempo.setText(string_label)

    def experimentos_terminados(self):
        print('Experimentos terminados')
        self.tabWidget.setEnabled(True)
        self.label_tiempo.setText('Experimentos terminados')
        self.bloque_timer.stop()

    def configurar_patrones(self):
        self.pat.show()
    
    def recibir_patrones(self, dic_patrones):
        print('Recibiendo patrones...')
        self.dic_patrones = dic_patrones
        print(self.dic_patrones)
        self.pat.close()

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
                if key == "t_exp":
                    str_label += f'{key}: {value} h\n'
                elif key == "t_control":
                    str_label += f'{key}: {value} °C\n'
                else:
                    str_label += f'{key}: {value} %\n'
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

        self.grafico_bloques.canvas.axes[0].step(t_exp_acum, I_rojo_acum, where='pre', label='Rojo', color='red')
        self.grafico_bloques.canvas.axes[1].step(t_exp_acum, I_verde_acum, where='pre', label='Verde', color='green')

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
            #rint(t_exp_acum[:tiempo_cambio + 1])
            #self.grafico_bloques.canvas.axes[0].fill_between(t_exp_acum[:tiempo_cambio + 1], 0, I_rojo_acum[:tiempo_cambio] + [I_rojo_acum[-1]], step='pre', alpha=0.3, color='red')
            #self.grafico_bloques.canvas.axes[1].fill_between(t_exp_acum[:tiempo_cambio + 1], 0, I_verde_acum[:tiempo_cambio], step='pre', alpha=0.3, color='green')
            #self.grafico_bloques.canvas.axes[2].fill_between(t_exp_acum[:tiempo_cambio + 1], 0, T_control_acum[:tiempo_cambio], step='pre', alpha=0.3, color='blue')

            #self.grafico_bloques.canvas.axes[0].fill_between(t_exp_acum[:tiempo_cambio + 1], 0, I_rojo_acum[:tiempo_cambio], alpha=0.3, color='red')
            #self.grafico_bloques.canvas.axes[1].fill_between(t_exp_acum[:tiempo_cambio + 1], 0, I_verde_acum[:tiempo_cambio], alpha=0.3, color='green')
            
            #self.grafico_bloques.canvas.axes[2].fill_between(t_exp_acum[:tiempo_cambio + 1], 0, T_control_acum[:tiempo_cambio], alpha=0.3, color='blue')

            self.grafico_bloques.canvas.axes[0].text(pos_x, 100 + 2, bloque_text, rotation=0, ha='center', va='bottom')

        self.grafico_bloques.canvas.axes[0].fill_between(t_exp_acum, 0, I_rojo_acum, step='pre', alpha=0.3, color='red')
        self.grafico_bloques.canvas.axes[1].fill_between(t_exp_acum, 0, I_verde_acum, step='pre', alpha=0.3, color='green')
        self.grafico_bloques.canvas.axes[0].set_yticks([0, 50, 100])
        self.grafico_bloques.canvas.axes[0].set_yticklabels(['', '50%', '100%'])
        self.grafico_bloques.canvas.axes[1].set_yticks([0, 50, 100])
        self.grafico_bloques.canvas.axes[1].set_yticklabels(['', '50%', '100%'])


        # Configurar leyendas y etiquetas
        self.grafico_bloques.canvas.axes[0].legend()
        self.grafico_bloques.canvas.axes[0].set_ylabel('Rojo')

        self.grafico_bloques.canvas.axes[1].legend()
        self.grafico_bloques.canvas.axes[1].set_ylabel('Verde')

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
        else:
            label.setStyleSheet('QLabel {}')

    def LEDOn(self, channel, intensidad):
        print(f"Encendiendo LED {channel} con intensidad {intensidad} desde app")
        color = self.colores[channel]
        label = self.map_color_to_label[channel]
        self.actualizar_estilo_led(label, True, color)

    def LEDset(self, channel, intensidad):
        self.LEDOn(channel, intensidad)

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

class PatronConfig(QMainWindow):
    senal_config_ready = pyqtSignal(dict)
    def __init__(self, fluo):
        super().__init__()
        loadUi('GUI/patron_config.ui', self)
        self.fluo = fluo
        self.guardar_patron()
        self.button_f1_preview.clicked.connect(lambda: self.ver_preview("f1"))
        self.button_guardar.clicked.connect(lambda: self.guardar_patron(True))

    def ver_preview(self, f):
        print('Viendo preview...')
        self.guardar_patron()
        capture_controls = self.dic_final[f]['config']
        self.fluo.startCamera()
        # define the camera configuration
        self.fluo.setCamera(configuration_values = capture_controls)
        request = self.fluo.camera.capture_request()
        im_array = request.make_array("main")  # array from the "main" stream
        request.release()
        # convert the array to a QImage
        height, width, channel = im_array.shape
        bytesPerLine = 3 * width
        qImg = QImage(im_array.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # convert the QImage to a QPixmap
        pixmap = QPixmap.fromImage(qImg)
        # display the QPixmap
        self.label_f1_preview.setPixmap(pixmap)
        

    def guardar_patron(self, ready=False):
        print('Guardando patrón...')
        self.dic_f1 = {
                'config' :{                                                                                    #(min, max, default_value)
                    'AeConstraintMode': self.f1_AeConstraintMode.value(),                   #(0, 3, 0) - AEC/AGC constrain mode - 0 = Normal
                    'AeEnable': self.f1_AeEnable.currentText(),                                   #(False, True, None) - When if is False ( = AEC/AGC off), there will be no automatic updates to the camera’s gain or exposure settings
                    'AeExposureMode': self.f1_AeExposureMode.value(),                       #(0, 3, 0) - 0 = normal exposures, 1 = shorter exposures, 2 = longer exposures, 3= custom exposures
                    'AeMeteringMode': self.f1_AeMeteringMode.value(),                       #(0, 3, 0) - Metering mode for AEC/AGC
                    'AnalogueGain': self.f1_AnalogueGain.value(),                           #(1.0, 10.666666984558105, Undefined) - Analogue gain applied by the sensor
                    'AwbEnable': self.f1_AwbEnable.currentText(),                                 #(False, True, None) When it is False (AutoWhiteBalance off), there will be no automatic updates to the colour gains
                    'AwbMode': self.f1_AwbMode.value(),                                     #(0, 7, 0)
                    'Brightness': self.f1_Brightness.value(),                               #(-1.0, 1.0, 0.0) - (-1.0) is very dark, 1.0 is very brigh
                    'ColourGains': (self.f1_ColourGains_0.value(), self.f1_ColourGains_1.value()),  #tuple (red_gain, blue_gain), each value: (0.0, 32.0, Undefined) - Setting these numbers disables AWB.
                    'Contrast': self.f1_Contrast.value(),                                   #(0.0, 32.0, 1.0) -  zero means "no contrast", 1.0 is the default "normal" contrast
                    'ExposureTime': self.f1_ExposureTime.value(),                           #(75, 11766829, Undefined). unit microseconds.
                    'ExposureValue': self.f1_ExposureValue.value(),                         #(-8.0, 8.0, 0.0) - Zero is the base exposure level. Positive values increase the target brightness, and negative values decrease it 
                    'FrameDurationLimits': (self.f1_FrameDurationLimits_0.value(), self.f1_FrameDurationLimits_1.value()),   # tuple, each value: (47183, 11767556, Undefined). The maximum and minimum time that the sensor can take to deliver a frame (microseconds). Reciprocal of frame rate
                    'NoiseReductionMode': self.f1_NoiseReductionMode.value(),               #(0, 4, 0) - 0 is off.
                    'Saturation': self.f1_Saturation.value(),                               #(0.0, 32.0, 1.0) - zero greyscale images, 1.0 "normal" saturation, higher values for more saturated colours.
                    'ScalerCrop': eval(self.f1_ScalerCrop.currentText()),                         #((0, 0, 64, 64), (0, 0, 3280, 2464), (0, 2, 3280, 2460)) - to use just a sub part of the sensor area: (x_offset, y_offset, width, height)
                    'Sharpness': self.f1_Sharpness.value()                                  #(0.0, 16.0, 1.0)} - zero no additional sharpening, 1.0 is "normal" level of sharpening, larger values apply proportionately stronger sharpening
                    },
                'mode': self.f1_CamMode.value(),
                'n_fotos': self.f1_nfotos.value(),
                'color_led': self.f1_ColorLed.currentText(),
                'I_led': self.f1_IntensidadLed.value()
            }
        
       
        # self.dic_f = {'f1': self.dic_f1, 'f2': self.dic_f2, 'f3': self.dic_f3, 'f4': self.dic_f4, 'f5': self.dic_f5, 'f6': self.dic_f6}
        fs = ['f1', 'f2', 'f3', 'f4', 'f5', 'f6']
        dic_final = {}
        if ready:
            for i in range(self.bloques_activos):
                dic_final[fs[i]] = self.dict_sec[fs[i]]
            self.senal_config_ready.emit(self.dic_final)
            return self.dic_final
        else:
            return

    def show(self):
        #herencia de show original
        super().show()
        #inicializar tabs
        # for i in range(len(self.tabs)):
        #     if i < self.bloques_activos:
        #         self.tabs[i].setEnabled(True)
        #     else:
        #         self.tabs[i].setEnabled(False)




class ExperimentoThread(QThread):
    def __init__(self, bloque, app):
        super(ExperimentoThread, self).__init__()
        self.bloque = bloque
        self.app = app

    def run(self):
        t_exp = self.bloque['t_exp']
        threads = []
        #map chanel to color
        channel_dic = {'rojo': 2, 'verde': 1, 'azul': 0, 'blanca': 3}
        intensidad_rojo = self.bloque['I_rojo']
        intensidad_verde = self.bloque['I_verde']
        
        print(f"Bloque de {t_exp} minutos")
        print(f"LED Rojo: {intensidad_rojo}")
        print(f"LED Verde: {intensidad_verde}")
        print("Encendiendo LEDs...")
        self.app.LEDset(channel_dic['rojo'], intensidad_rojo)
        self.app.LEDset(channel_dic['verde'], intensidad_verde)

        time.sleep(t_exp) # Esperar el tiempo total del experimento
        #time.sleep(t_exp * 60 * 60) # Esperar el tiempo total del experimento

        print("Apagando LEDs...")
        self.app.LEDOff(channel_dic['rojo'])
        self.app.LEDOff(channel_dic['verde'])


    def actualizar_interfaz(self, mensaje):
        pass
        #print("mensaje: ", mensaje)


class ExperimentosManagerThread(QThread):
    senal_final = pyqtSignal()
    senal_inicio_total = pyqtSignal(int)
    senal_inicio_bloque = pyqtSignal(str, int)
    senal_fin_bloque = pyqtSignal(str)
    def __init__(self, bloques, app):
        super(ExperimentosManagerThread, self).__init__()
        self.bloques = bloques
        self.app = app

    def run(self):
        tiempo_total = 0
        for nombre_bloque, bloque in self.bloques.items():
            tiempo_total += int(bloque["t_exp"])
        print(f"Tiempo total de experimentos: {tiempo_total} minutos")
        self.senal_inicio_total.emit(tiempo_total)
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