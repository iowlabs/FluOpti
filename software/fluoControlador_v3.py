# -*- coding: utf-8 -*-
"""
Created on Wed Feb 7 2024

@author: Cristobal Vasquez

Codigo modificado de fluoControlador.py para agregar nueva interfaz y funcionalidades
"""
import matplotlib
matplotlib.use('Agg')  # 'Agg' es un backend sin interfaz

from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import  QMainWindow, QApplication, QFileDialog, QGroupBox, QLabel, QVBoxLayout, QStatusBar
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt

from hardware.FluOpti import FluOpti

import cv2
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from time import sleep
from pandas import *
import numpy as np
from simple_pid import PID
import datetime
import csv
import time
import sys
import collections

debug = True
DATA_PATH = "data/"


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi('GUI/gui_test_v3.ui', self)

        # Nueva interfaz###########
        self.sec = Secuenciador()
        self.sec.setWindowModality(2) # 2 = Qt.ApplicationModal
        self.dic_bloques = {}
        self.sec.senal_dic_final.connect(self.recibir_diccionario)
        self.button_aceptar.clicked.connect(self.configurar_secuenciador)
        self.pushButton_run.clicked.connect(self.comenzar_experimentos)

        ############################

        self.Fluo   =  FluOpti("normal")
        self.temp       = [0.0, 0.0] #pH
        self.temp_sp    = [0.0, 0.0]
        self.temp_pwr   = [0,0]
        self.led_pwr    = [0,0,0,0,0,0]
        self.t_     = collections.deque([0.0],200)
        self.t1_    = collections.deque([self.temp[0]],200)
        self.t2_    = collections.deque([self.temp[1]],200)
        self.tsp1_  = collections.deque([self.temp_sp[0]],200)
        self.tsp2_  = collections.deque([self.temp_sp[1]],200)
        self.channel = ['B','G','R','W', 'H1','H2']
        self.collections = [self.t1_,self.t2_,self.tsp1_,self.tsp2_]

        pen = pg.mkPen(color = (0,0,255),width = 2)
        self.graphicsView.setBackground("w")
        self.graphicsView.setTitle("Temperature",color = "b",size = "15pt")
        styles = {"color": "#f00", "font-size": "10px"}
        self.graphicsView.setLabel("left", "Temp °C", **styles)
        self.graphicsView.setLabel("bottom", "tiempo (s)", **styles)
        self.graphicsView.showGrid(x=True, y=True)
        self.graphicsView.setXRange(-0.05, 1.05, padding=0)
        self.graphicsView.setYRange(-0.05, 1.05, padding=0)
        self.graphicsView.plot(self.t_, self.t1_, pen=pen)
        self.graphicsView.plot(self.t_, self.t2_, pen=pen)
        self.time_now       = ""
        self.file_name      = ""


        ##### CONFIGURACION DE PATRONES
        self.pat = PatronConfig(self.Fluo)
        self.pat.setWindowModality(2)
        self.pat.senal_config_ready.connect(self.recibir_patrones)
        self.button_fotos.clicked.connect(self.configurar_patrones)

        #PID modules to control temperature
        self.pid_temp1 = PID(1,0.1,0.05,setpoint = 1)
        self.pid_temp2 = PID(1,0.1,0.05,setpoint = 1)

        self.pid_temp1.output_limits = (0,100)
        self.pid_temp2.output_limits = (0,100)

        self.pid_temp1.setpoint      = self.temp_sp[0]
        self.pid_temp2.setpoint      = self.temp_sp[1]

        #FILE OBJ TO SAVE DATA
        self.data_path    = DATA_PATH
        self.data_file    = None
        self.data_writer  = None

        self.run_state = False

        self.elapsed_time   = 0
        self.sample_time    = 1# in seconds

        #TIME AND DATE
        self.date_now = QtCore.QDate.currentDate()

        #
        self.lineEdit.setText(str(self.temp_sp[0]))
        self.lineEdit_2.setText(str(self.temp_sp[1]))
        self.lineEdit_3.setText(str(self.temp[0]))
        self.lineEdit_5.setText(str(self.temp[1]))
        self.lineEdit_4.setText(str(self.temp_pwr[0]))
        self.lineEdit_6.setText(str(self.temp_pwr[1]))


        self.lineEdit.setReadOnly(True)
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_5.setReadOnly(True)
        self.lineEdit_6.setReadOnly(True)

        self.pushButton_2.setDisabled(True)
        self.pushButton_6.setDisabled(True)
        self.pushButton_7.setDisabled(True)
        self.pushButton_8.setDisabled(True)
        self.pushButton_10.setDisabled(True)
        self.pushButton_13.setDisabled(True)
        self.pushButton_14.setDisabled(True)

        self.sliders = [self.horizontalSlider,self.horizontalSlider_2,self.horizontalSlider_3,self.horizontalSlider_4,self.horizontalSlider_5,self.horizontalSlider_6]
        self.sBox    = [self.spinBox,self.spinBox_2,self.spinBox_3,self.spinBox_4,self.spinBox_5,self.spinBox_6]
        self.btnOn   = [self.pushButton,self.pushButton_3,self.pushButton_4,self.pushButton_5,self.pushButton_11,self.pushButton_12]
        self.btnOff  = [self.pushButton_2,self.pushButton_6,self.pushButton_7,self.pushButton_8,self.pushButton_13,self.pushButton_14]
        self.sdBox   = [self.doubleSpinBox,self.doubleSpinBox_2]
        self.ledit_temp_sp  = [self.lineEdit,self.lineEdit_2]
        self.ledit_temp     = [self.lineEdit_3,self.lineEdit_5]

        #Define behaivor of LEDs
        self.pushButton.clicked.connect(  lambda: self.LEDOn(0))
        self.pushButton_3.clicked.connect(lambda: self.LEDOn(1))
        self.pushButton_4.clicked.connect(lambda: self.LEDOn(2))
        self.pushButton_5.clicked.connect(lambda: self.LEDOn(3))
        self.pushButton_11.clicked.connect(lambda: self.LEDOn(4))
        self.pushButton_12.clicked.connect(lambda: self.LEDOn(5))

        self.pushButton_2.clicked.connect(lambda: self.LEDOff(0))
        self.pushButton_6.clicked.connect(lambda: self.LEDOff(1))
        self.pushButton_7.clicked.connect(lambda: self.LEDOff(2))
        self.pushButton_8.clicked.connect(lambda: self.LEDOff(3))
        self.pushButton_13.clicked.connect(lambda: self.LEDOff(4))
        self.pushButton_14.clicked.connect(lambda: self.LEDOff(5))

        self.horizontalSlider.valueChanged.connect(lambda:self.LEDset(0))
        self.horizontalSlider_2.valueChanged.connect(lambda:self.LEDset(1))
        self.horizontalSlider_3.valueChanged.connect(lambda:self.LEDset(2))
        self.horizontalSlider_4.valueChanged.connect(lambda:self.LEDset(3))
        self.horizontalSlider_5.valueChanged.connect(lambda:self.LEDset(4))
        self.horizontalSlider_6.valueChanged.connect(lambda:self.LEDset(5))


        self.spinBox.valueChanged.connect(lambda: self.LEDset2(0))
        self.spinBox_2.valueChanged.connect(lambda: self.LEDset2(1))
        self.spinBox_3.valueChanged.connect(lambda: self.LEDset2(2))
        self.spinBox_4.valueChanged.connect(lambda: self.LEDset2(3))
        self.spinBox_5.valueChanged.connect(lambda: self.LEDset2(4))
        self.spinBox_6.valueChanged.connect(lambda: self.LEDset2(5))

        #Temperature Control interface
        self.pushButton_9.clicked.connect(lambda: self.setTempSP(0))
        self.pushButton_18.clicked.connect(lambda: self.setTempSP(1))
        self.pushButton_19.clicked.connect( self.startTempCtrl)
        self.pushButton_10.clicked.connect(self.stopTempCtrl)

        #startVideo
        # self.capture = cv2.VideoCapture(0)
        # self.image = None
        #video timer
        # self.video_timer = QtCore.QTimer()
        # self.video_timer.setInterval(10)
        # self.video_timer.timeout.connect(self.updateFrame)
        #self.video_timer.start()
        #timer for Video


        #MGMT UPDATE DATA
        # self.run_timer = QtCore.QTimer()
        # self.run_timer.setInterval(1000*self.sample_time)
        # self.run_timer.timeout.connect(self.updateData)
        # self.run_timer.start()


        #STATUS BAR
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        #aumentar fuente de status bar
        font = self.status.font()
        font.setPointSize(12)
        self.status.setFont(font)

        # DICCIONARIOS PARA MOSTRAR COLORES EN INTERFAZ
        self.colores = {0: 'blue', 1: 'yellowgreen', 2: 'red', 3: 'lightgray'}
        self.map_color_to_label = {0: self.label_luz_azul, 1: self.label_luz_verde, 2: self.label_luz_roja, 3: self.label_luz_blanca}

    def comenzar_experimentos(self):
        self.experimentos = ExperimentosManagerThread(self.dic_bloques, self)
        self.experimentos.senal_inicio_total.connect(self.inicio_total_experimentos)
        self.experimentos.senal_inicio_bloque.connect(self.inicio_bloque)
        self.experimentos.senal_fin_bloque.connect(self.fin_bloque)
        self.experimentos.senal_final.connect(self.experimentos_terminados)
        self.experimentos.start()
        self.tabWidget.setEnabled(False)

    def inicio_total_experimentos(self, tiempo_total):

        self.tiempo_total_exp = tiempo_total
        self.time_elapsed = 0

        self.bloque_timer = QtCore.QTimer()
        self.bloque_timer.setInterval(1000)
        self.bloque_timer.timeout.connect(self.updateTime)
        self.bloque_timer.start()
        print("INICIANDO TIMER EXPERIMENTOS")

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


    def updateFrame(self):
        ret, self.image = self.capture.read()
        self.image = cv2.resize(self.image, (180, 120))
        qformat = QImage.Format_Indexed8
        if len(self.image.shape) == 3:
            if self.image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(self.image, self.image.shape[1], self.image.shape[0], self.image.strides[0], qformat)
        outImage = outImage.rgbSwapped()


        self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
        self.imgLabel.setScaledContents(True)


    def changeDir(self):
        self.data_path = QFileDialog.getExistingDirectory(self, caption = 'Seleccione nuevo directorio',directory = DATA_PATH)+"/"
        if debug:
            print (self.data_path)
        self.lineEdit_2.setText(self.data_path)




    def updateData(self):
        self.Fluo.updateTemps()
        self.temp[0] = self.Fluo.t1
        self.temp[1] = self.Fluo.t2
        self.lineEdit_3.setText(f"{self.temp[0]:.2f}")
        self.lineEdit_5.setText(f"{self.temp[1]:.2f}")
        if self.run_state:
            self.t1_.append(self.temp[0])
            self.t2_.append(self.temp[1])
            self.elapsed_time +=1
            self.t_.append(self.elapsed_time)
            self.graphicsView.clear()
            self.graphicsView.setXRange( self.t_[0] - 0.1, self.elapsed_time + 0.1, padding=0)
            self.graphicsView.setYRange( -0.5, 80.5, padding=0)
            pen = pg.mkPen(color = (0, 0, 255),width = 2)
            self.graphicsView.plot(self.t_,self.t1_, pen=pen)
            pen = pg.mkPen(color = (0, 255, 255),width = 2)
            self.graphicsView.plot(self.t_,self.t2_, pen=pen)
            #update pid controllers and send heater pwr to the module
            self.temp_pwr[0] = self.pid_temp1(self.temp[0])
            self.temp_pwr[1] = self.pid_temp2(self.temp[1])
            self.lineEdit_4.setText(format(self.temp_pwr[0],'.2f'))
            self.lineEdit_6.setText(format(self.temp_pwr[1],'.2f'))

            try:
                self.Fluo.LEDSetPWR('H1',self.temp_pwr[0])
                self.Fluo.LEDSetPWR('H2',self.temp_pwr[1])
                self.Fluo.LEDon('H1')
                self.Fluo.LEDon('H2')
                self.writeData()
            except Exception as e:
                print(e)
        print(f"CH1 - t:\t{self.temp[0]} tsp:\t{self.temp_sp[0]} pwr :\t{self.temp_pwr[0]}\nCH2 - t:\t{self.temp[1]} tsp:\t{self.temp_sp[1]} pwr :\t{self.temp_pwr[1]}")

    def startTempCtrl (self):
        self.run_state =  True
        self.pushButton_10.setDisabled(False)
        self.pushButton_19.setDisabled(True)
        self.elapsed_time = 0

        time_now  =  datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        self.file_name = time_now+".csv"
        self.data_file   = open( self.data_path + self.file_name,"w", newline = '')
        self.data_writer = csv.writer( self.data_file)
        self.data_writer.writerow(["time","tsp1","t1","pwr1","tsp2","t2","pwr2"])
        self.data_file.close()

    def stopTempCtrl(self):
        self.run_state = False
        self.pushButton_19.setDisabled(False)
        self.pushButton_10.setDisabled(True)
        self.elapsed_time = 0
        self.Fluo.LEDoff('H1')
        self.Fluo.LEDoff('H2')

    """
    def start(self):
        if self.dl.connected:
            self.run_state = True
            self.pushButton_7.setDisabled(True)
            self.pushButton_8.setDisabled(False)

            time_now  =  datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            self.file_name = time_now+".csv"
            self.data_file   = open( self.data_path + self.file_name,"w", newline = '')
            self.data_writer = csv.writer( self.data_file)
            self.data_writer.writerow(["time","v","i","pwr"])
            self.data_file.close()
            self.run_timer.start()

    def stop(self):
        self.run_state = False
        self.run_timer.stop()
        self.pushButton_7.setDisabled(False)
        self.pushButton_8.setDisabled(True)

    def setSampleTime(self):
        self.sample_time = float(self.lineEdit_3.text())
        if self.sample_time < 0.1:
            self.sample_time = 0.1
        if self.connected:
            self.run_timer.stop()
            self.run_timer.setInterval(1000*self.sample_time)
            self.run_timer.start()

    def updateTime(self):
        current_time = QtCore.QTime.currentTime()
        label_time   = current_time.toString('hh:mm:ss')
        self.lineEdit_11.setText(label_time)
        if self.run_state:
            self.elapsed_time += 1
            self.lineEdit_12.setText(str(datetime.timedelta(seconds = self.elapsed_time)))

    def updateData(self):
        if self.run_state:

            print("updating data")
            self.t_.append(self.elapsed_time)
            self.lineEdit_13.setText(format(self.dl.i,'.2f'))
            self.lineEdit_5.setText( format(self.dl.v,'.2f'))
            self.lineEdit_10.setText(format(self.dl.pwr,'.2f'))
            self.v_.append(self.dl.v)
            self.i_.append(self.dl.i)
            self.pwr_.append(self.dl.pwr)
            pen = pg.mkPen(color = (0, 0, 255),width = 2)

            for i in range(3):
                self.graphics[i].clear()
                self.graphics[i].setXRange( self.t_[0] - 0.001, self.elapsed_time + 0.001, padding=0)
                self.graphics[i].setYRange( min(self.collections[i])-0.5, max(self.collections[i]) + 0.5, padding=0)
                self.graphics[i].plot(self.t_,self.collections[i], pen=pen)
            self.writeData()

    def writeData(self):
        self.data_file   = open(self.data_path+self.file_name,"a", newline = '')
        self.data_writer = csv.writer(self.data_file)
        row = [ self.elapsed_time,self.dl.v,self.dl.i,self.dl.pwr]
        print(f"saving {row} to {self.data_path+self.file_name}")
        self.data_writer.writerow(row)
        self.data_file.close()
"""

    def actualizar_estilo_led(self, label, estado, color):
        # Actualizar el estilo del QLabel para representar el estado del LED EN INTERFAZ
        if estado:
            label.setStyleSheet(f'QLabel {{ background-color: {color}; border-radius: 50px; }}')
            print(f'stylesheet LED {color}')
        else:
            label.setStyleSheet('QLabel {}')

    def LEDOn(self, ch, intensidad=-1):
        if intensidad < 0:
            self.Fluo.LEDSetPWR(self.channel[ch],self.led_pwr[ch])
        else:
            self.Fluo.LEDSetPWR(self.channel[ch],intensidad)
        self.Fluo.LEDon(self.channel[ch])
        self.btnOn[ch].setDisabled(True)
        self.btnOff[ch].setDisabled(False)
        # Se AGREGAN LOS COLORES DE LAS LUCES A LA INTERFAZ
        color = self.colores[ch]
        label = self.map_color_to_label[ch]
        self.actualizar_estilo_led(label, True, color)


    def LEDOff(self, ch):
        #self.Fluo.LEDoff(self.channel[ch])
        self.Fluo.LEDSetPWR(self.channel[ch],0)  ## Solucion temporal. Reemplazar despues por module_switch
        self.btnOn[ch].setDisabled(False)
        self.btnOff[ch].setDisabled(True)
        # Se AGREGAN LOS COLORES DE LAS LUCES A LA INTERFAZ
        color = self.colores[ch]
        label = self.map_color_to_label[ch]
        self.actualizar_estilo_led(label, False, color)


    def LEDset(self,ch, intensidad=-1):
        if intensidad < 0:
            val = self.sliders[ch].value()
        else:
            val = intensidad
        self.sBox[ch].setValue(val)
        self.led_pwr[ch] = val
        #if self.Fluo._default_modules[self.channel[ch]]['status']:
        if self.Fluo.modules[self.channel[ch]]['status']:
        
            self.LEDOn(ch)

    def LEDset2(self,ch, intensidad=-1):
        if intensidad < 0:
            val = self.sBox[ch].value()
        else:
            val = intensidad
        self.sliders[ch].setValue(val)
        self.led_pwr[ch] = val

    def setTempSP(self,ch):
        val =  self.sdBox[ch].value()
        self.temp_sp[ch] = val
        if ch == 0:
            self.pid_temp1.setpoint = self.temp_sp[ch]
        else:
            self.pid_temp2.setpoint = self.temp_sp[ch]

        self.ledit_temp_sp[ch].setText(format(val,'.2f'))

    def writeData(self):
        self.data_file   = open(self.data_path+self.file_name,"a", newline = '')
        self.data_writer = csv.writer(self.data_file)
        row = [ self.elapsed_time,self.temp_sp[0],self.temp[0],self.temp_pwr[0],self.temp_sp[1],self.temp[1],self.temp_pwr[1]]
        print(f"saving {row} to {self.data_path+self.file_name}")
        self.data_writer.writerow(row)
        self.data_file.close()

    def Close(self):
        self.video_timer.stop()
        self.run_timer.stop()
        self.Fluo.close()

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


    # FUNCIONALIDADES CON SECUENCIADOR
        
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
            new_group = QGroupBox()
            new_group.setTitle(bloque)
            new_group.setStyleSheet("QGroupBox { font: bold; }")
            new_group.setLayout(QVBoxLayout())
            label = QLabel(str_label)
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
    

# VENTANA SECUENCIADOR
            
class Secuenciador(QMainWindow):
    senal_dic_final = QtCore.pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        loadUi('GUI/secuenciador_v3.ui', self)
        #create status bar
        self.status = QStatusBar()
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
        #capture_controls = self.dic_final[f]
        #print("capture_controls: ", capture_controls)
        ######### ONLY FOR DEBUG
        capture_controls = {                                                    #(min, max, default_value)
            'AeConstraintMode': 0,                  #(0, 3, 0) - AEC/AGC constrain mode - 0 = Normal
            'AeEnable': False,                      #(False, True, None) - When if is False ( = AEC/AGC off), there will be no automatic updates to the camers gain or exposure settings
            'AeExposureMode': 0,                    #(0, 3, 0) - 0 = normal exposures, 1 = shorter exposures, 2 = longer exposures, 3= custom exposures
            'AeMeteringMode': 0,                    #(0, 3, 0) - Metering mode for AEC/AGC
            'AnalogueGain': 1,                      #(1.0, 10.666666984558105, Undefined) - Analogue gain applied by the sensor
            'AwbEnable': False,                     #(False, True, None) When it is False (AutoWhiteBalance off), there will be no automatic updates to the colour gains
            'AwbMode': 0,                           #(0, 7, 0)
            'Brightness': 0.0,                      #(-1.0, 1.0, 0.0) - (-1.0) is very dark, 1.0 is very brigh
            'ColourGains': (1,1),                   #tuple (red_gain, blue_gain), each value: (0.0, 32.0, Undefined) - Setting these numbers disables AWB.
            'Contrast': 1.0,                        #(0.0, 32.0, 1.0) -  zero means "no contrast", 1.0 is the default "normal" contrast
            'ExposureTime': 10000,                   #(75, 11766829, Undefined). unit microseconds.
            'ExposureValue': 0.0,                   #(-8.0, 8.0, 0.0) - Zero is the base exposure level. Positive values increase the target brightness, and negative values decrease it 
            'FrameDurationLimits': (47183,11767556),   # tuple, each value: (47183, 11767556, Undefined). The maximum and minimum time that the sensor can take to deliver a frame (microseconds). Reciprocal of frame rate
            'NoiseReductionMode': 0,                #(0, 4, 0) - 0 is off.
            'Saturation': 1.0,                      #(0.0, 32.0, 1.0) - zero greyscale images, 1.0 "normal" saturation, higher values for more saturated colours.
            'ScalerCrop': (0, 2, 3280, 2460),       #((0, 0, 64, 64), (0, 0, 3280, 2464), (0, 2, 3280, 2460)) - to use just a sub part of the sensor area: (x_offset, y_offset, width, height)
            'Sharpness': 0.0                        #(0.0, 16.0, 1.0)} - zero no additional sharpening, 1.0 is "normal" level of sharpening, larger values apply proportionately stronger sharpening
            }

        ######### ONLY FOR DEBUG
        self.fluo.startCamera()
        print("camera started")
        # define the camera configuration
        self.fluo.setCamera(mode_number = 0, configuration_values = capture_controls)
        print("camera seted")
        self.fluo.camera.start()
        request = self.fluo.camera.capture_request()
        print("request created")
        im_array = request.make_array("main")  # array from the "main" stream
        print("array created")
        request.release()
        print("request released")
        # # convert the array to a QImage
        # height, width, channel = im_array.shape
        # bytesPerLine = 3 * width
        # qImg = QImage(im_array.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # # convert the QImage to a QPixmap
        # pixmap = QPixmap.fromImage(qImg)
        # # display the QPixmap
        # self.label_f1_preview.setPixmap(pixmap)

            
        

    def guardar_patron(self, ready=False):
        print('Guardando patrón...')
        self.dic_f1 = {
                                                                                    #(min, max, default_value)
            'AeConstraintMode': self.f1_AeConstraintMode.value(),                   #(0, 3, 0) - AEC/AGC constrain mode - 0 = Normal
            'AeEnable': bool(self.f1_AeEnable.currentText()),                                   #(False, True, None) - When if is False ( = AEC/AGC off), there will be no automatic updates to the camera’s gain or exposure settings
            'AeExposureMode': self.f1_AeExposureMode.value(),                       #(0, 3, 0) - 0 = normal exposures, 1 = shorter exposures, 2 = longer exposures, 3= custom exposures
            'AeMeteringMode': self.f1_AeMeteringMode.value(),                       #(0, 3, 0) - Metering mode for AEC/AGC
            'AnalogueGain': self.f1_AnalogueGain.value(),                           #(1.0, 10.666666984558105, Undefined) - Analogue gain applied by the sensor
            'AwbEnable': bool(self.f1_AwbEnable.currentText()),                                 #(False, True, None) When it is False (AutoWhiteBalance off), there will be no automatic updates to the colour gains
            'AwbMode': self.f1_AwbMode.value(),                                     #(0, 7, 0)
            'Brightness': self.f1_Brightness.value(),                               #(-1.0, 1.0, 0.0) - (-1.0) is very dark, 1.0 is very brigh
            'ColourGains': (self.f1_ColourGains_0.value(), self.f1_ColourGains_1.value()),  #tuple (red_gain, blue_gain), each value: (0.0, 32.0, Undefined) - Setting these numbers disables AWB.
            'Contrast': self.f1_Contrast.value(),                                   #(0.0, 32.0, 1.0) -  zero means "no contrast", 1.0 is the default "normal" contrast
            'ExposureTime': self.f1_ExposureTime.value(),                           #(75, 11766829, Undefined). unit microseconds.
            'ExposureValue': self.f1_ExposureValue.value(),                         #(-8.0, 8.0, 0.0) - Zero is the base exposure level. Positive values increase the target brightness, and negative values decrease it 
            'FrameDurationLimits': (self.f1_FrameDurationLimits_0.value(), self.f1_FrameDurationLimits_1.value()),   # tuple, each value: (47183, 11767556, Undefined). The maximum and minimum time that the sensor can take to deliver a frame (microseconds). Reciprocal of frame rate
            'NoiseReductionMode': self.f1_NoiseReductionMode.value(),               #(0, 4, 0) - 0 is off.
            'Saturation': self.f1_Saturation.value(),                               #(0.0, 32.0, 1.0) - zero greyscale images, 1.0 "normal" saturation, higher values for more saturated colours.
            'ScalerCrop': tuple(eval(self.f1_ScalerCrop.currentText())),                         #((0, 0, 64, 64), (0, 0, 3280, 2464), (0, 2, 3280, 2460)) - to use just a sub part of the sensor area: (x_offset, y_offset, width, height)
            'Sharpness': self.f1_Sharpness.value()                                  #(0.0, 16.0, 1.0)} - zero no additional sharpening, 1.0 is "normal" level of sharpening, larger values apply proportionately stronger sharpening
            }
        
       
        # self.dic_f = {'f1': self.dic_f1, 'f2': self.dic_f2, 'f3': self.dic_f3, 'f4': self.dic_f4, 'f5': self.dic_f5, 'f6': self.dic_f6}
        fs = ['f1', 'f2', 'f3', 'f4', 'f5', 'f6']
        dic_final = {}
        self.dic_final = {"f1": self.dic_f1}
        if ready:
            for i in range(self.bloques_activos):
                dic_final[fs[i]] = self.dict_sec[fs[i]]
            self.senal_config_ready.emit(self.dic_final)
            return self.dic_final
        else:
            return

    def cargar_patron(self):
        print('Cargando patrón...')
        dic_patron = {'t_exp': 10, 't_control' : 37, 'I_rojo': 50, 'I_verde': 50}
        return dic_patron

class ExperimentoThread(QThread):
    def __init__(self, bloque, app):
        super(ExperimentoThread, self).__init__()
        self.bloque = bloque
        self.app = app

    def run(self):
        t_exp = self.bloque['t_exp']
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


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
