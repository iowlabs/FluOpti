# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')  # 'Agg' es un backend sin interfaz

from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import  QMainWindow, QApplication, QFileDialog, QWidget
from PyQt5.uic import loadUi


from GUI.gui import Ui_MainWindow
from hardware.FluOpti import FluOpti

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

debug = True
DATA_PATH = "data/"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi('GUI/gui_test.ui', self)

        # Nueva interfaz###########
        self.sec = Secuenciador()
        self.sec.setWindowModality(2) # 2 = Qt.ApplicationModal
        self.dic_bloques = {}
        self.sec.senal_dic_final.connect(self.recibir_diccionario)
        self.button_aceptar.clicked.connect(self.configurar_secuenciador)

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

        #MGMT UPDATE DATA
        self.run_timer = QtCore.QTimer()
        self.run_timer.setInterval(1000*self.sample_time)
        self.run_timer.timeout.connect(self.updateData)
        self.run_timer.start()

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
        self.capture = cv2.VideoCapture(0)
        self.image = None
        #video timer
        self.video_timer = QtCore.QTimer()
        self.video_timer.setInterval(10)
        self.video_timer.timeout.connect(self.updateFrame)
        #self.video_timer.start()

        #timer for Video

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


    def updateTime(self):
        pass

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
    def LEDOn(self, ch):
        self.Fluo.LEDSetPWR(self.channel[ch],self.led_pwr[ch])
        self.Fluo.LEDon(self.channel[ch])
        self.btnOn[ch].setDisabled(True)
        self.btnOff[ch].setDisabled(False)

    def LEDOff(self, ch):
        self.Fluo.LEDoff(self.channel[ch])
        self.btnOn[ch].setDisabled(False)
        self.btnOff[ch].setDisabled(True)

    def LEDset(self,ch):
        val = self.sliders[ch].value()
        self.sBox[ch].setValue(val)
        self.led_pwr[ch] = val
        if self.Fluo._default_modules[self.channel[ch]]['status']:
            self.LEDOn(ch)

    def LEDset2(self,ch):
        val = self.sBox[ch].value()
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


# VENTANA SECUENCIADOR
            
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



if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    main = MainWindow()
    main.show()
    #
    #def exit_program():
    #    print("exitinig from program")
    #    main.StopAll()
    #    main.closeAll()
    #    app.exec_()
    #sys.exit(exit_program())
    ret = app.exec_()
    main.Close()
    print("stoped")
    sys.exit(ret)
