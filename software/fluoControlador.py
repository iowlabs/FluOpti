# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')  # 'Agg' es un backend sin interfaz

from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import  QMainWindow, QApplication, QFileDialog, QWidget

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
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

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
        self.ui.graphicsView.setBackground("w")
        self.ui.graphicsView.setTitle("Temperature",color = "b",size = "15pt")
        styles = {"color": "#f00", "font-size": "10px"}
        self.ui.graphicsView.setLabel("left", "Temp °C", **styles)
        self.ui.graphicsView.setLabel("bottom", "tiempo (s)", **styles)
        self.ui.graphicsView.showGrid(x=True, y=True)
        self.ui.graphicsView.setXRange(-0.05, 1.05, padding=0)
        self.ui.graphicsView.setYRange(-0.05, 1.05, padding=0)
        self.ui.graphicsView.plot(self.t_, self.t1_, pen=pen)
        self.ui.graphicsView.plot(self.t_, self.t2_, pen=pen)
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
        self.ui.lineEdit.setText(str(self.temp_sp[0]))
        self.ui.lineEdit_2.setText(str(self.temp_sp[1]))
        self.ui.lineEdit_3.setText(str(self.temp[0]))
        self.ui.lineEdit_5.setText(str(self.temp[1]))
        self.ui.lineEdit_4.setText(str(self.temp_pwr[0]))
        self.ui.lineEdit_6.setText(str(self.temp_pwr[1]))


        self.ui.lineEdit.setReadOnly(True)
        self.ui.lineEdit_2.setReadOnly(True)
        self.ui.lineEdit_3.setReadOnly(True)
        self.ui.lineEdit_4.setReadOnly(True)
        self.ui.lineEdit_5.setReadOnly(True)
        self.ui.lineEdit_6.setReadOnly(True)

        self.ui.pushButton_2.setDisabled(True)
        self.ui.pushButton_6.setDisabled(True)
        self.ui.pushButton_7.setDisabled(True)
        self.ui.pushButton_8.setDisabled(True)
        self.ui.pushButton_10.setDisabled(True)
        self.ui.pushButton_13.setDisabled(True)
        self.ui.pushButton_14.setDisabled(True)

        self.sliders = [self.ui.horizontalSlider,self.ui.horizontalSlider_2,self.ui.horizontalSlider_3,self.ui.horizontalSlider_4,self.ui.horizontalSlider_5,self.ui.horizontalSlider_6]
        self.sBox    = [self.ui.spinBox,self.ui.spinBox_2,self.ui.spinBox_3,self.ui.spinBox_4,self.ui.spinBox_5,self.ui.spinBox_6]
        self.btnOn   = [self.ui.pushButton,self.ui.pushButton_3,self.ui.pushButton_4,self.ui.pushButton_5,self.ui.pushButton_11,self.ui.pushButton_12]
        self.btnOff  = [self.ui.pushButton_2,self.ui.pushButton_6,self.ui.pushButton_7,self.ui.pushButton_8,self.ui.pushButton_13,self.ui.pushButton_14]
        self.sdBox   = [self.ui.doubleSpinBox,self.ui.doubleSpinBox_2]
        self.ledit_temp_sp  = [self.ui.lineEdit,self.ui.lineEdit_2]
        self.ledit_temp     = [self.ui.lineEdit_3,self.ui.lineEdit_5]

        #Define behaivor of LEDs
        self.ui.pushButton.clicked.connect(  lambda: self.LEDOn(0))
        self.ui.pushButton_3.clicked.connect(lambda: self.LEDOn(1))
        self.ui.pushButton_4.clicked.connect(lambda: self.LEDOn(2))
        self.ui.pushButton_5.clicked.connect(lambda: self.LEDOn(3))
        self.ui.pushButton_11.clicked.connect(lambda: self.LEDOn(4))
        self.ui.pushButton_12.clicked.connect(lambda: self.LEDOn(5))

        self.ui.pushButton_2.clicked.connect(lambda: self.LEDOff(0))
        self.ui.pushButton_6.clicked.connect(lambda: self.LEDOff(1))
        self.ui.pushButton_7.clicked.connect(lambda: self.LEDOff(2))
        self.ui.pushButton_8.clicked.connect(lambda: self.LEDOff(3))
        self.ui.pushButton_13.clicked.connect(lambda: self.LEDOff(4))
        self.ui.pushButton_14.clicked.connect(lambda: self.LEDOff(5))

        self.ui.horizontalSlider.valueChanged.connect(lambda:self.LEDset(0))
        self.ui.horizontalSlider_2.valueChanged.connect(lambda:self.LEDset(1))
        self.ui.horizontalSlider_3.valueChanged.connect(lambda:self.LEDset(2))
        self.ui.horizontalSlider_4.valueChanged.connect(lambda:self.LEDset(3))
        self.ui.horizontalSlider_5.valueChanged.connect(lambda:self.LEDset(4))
        self.ui.horizontalSlider_6.valueChanged.connect(lambda:self.LEDset(5))


        self.ui.spinBox.valueChanged.connect(lambda: self.LEDset2(0))
        self.ui.spinBox_2.valueChanged.connect(lambda: self.LEDset2(1))
        self.ui.spinBox_3.valueChanged.connect(lambda: self.LEDset2(2))
        self.ui.spinBox_4.valueChanged.connect(lambda: self.LEDset2(3))
        self.ui.spinBox_5.valueChanged.connect(lambda: self.LEDset2(4))
        self.ui.spinBox_6.valueChanged.connect(lambda: self.LEDset2(5))

        #Temperature Control interface
        self.ui.pushButton_9.clicked.connect(lambda: self.setTempSP(0))
        self.ui.pushButton_18.clicked.connect(lambda: self.setTempSP(1))
        self.ui.pushButton_19.clicked.connect( self.startTempCtrl)
        self.ui.pushButton_10.clicked.connect(self.stopTempCtrl)

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


        self.ui.imgLabel.setPixmap(QPixmap.fromImage(outImage))
        self.ui.imgLabel.setScaledContents(True)


    def changeDir(self):
        self.data_path = QFileDialog.getExistingDirectory(self, caption = 'Seleccione nuevo directorio',directory = DATA_PATH)+"/"
        if debug:
            print (self.data_path)
        self.ui.lineEdit_2.setText(self.data_path)




    def updateData(self):
        self.Fluo.updateTemps()
        self.temp[0] = self.Fluo.t1
        self.temp[1] = self.Fluo.t2
        self.ui.lineEdit_3.setText(f"{self.temp[0]:.2f}")
        self.ui.lineEdit_5.setText(f"{self.temp[1]:.2f}")
        if self.run_state:
            self.t1_.append(self.temp[0])
            self.t2_.append(self.temp[1])
            self.elapsed_time +=1
            self.t_.append(self.elapsed_time)
            self.ui.graphicsView.clear()
            self.ui.graphicsView.setXRange( self.t_[0] - 0.1, self.elapsed_time + 0.1, padding=0)
            self.ui.graphicsView.setYRange( -0.5, 80.5, padding=0)
            pen = pg.mkPen(color = (0, 0, 255),width = 2)
            self.ui.graphicsView.plot(self.t_,self.t1_, pen=pen)
            pen = pg.mkPen(color = (0, 255, 255),width = 2)
            self.ui.graphicsView.plot(self.t_,self.t2_, pen=pen)
            #update pid controllers and send heater pwr to the module
            self.temp_pwr[0] = self.pid_temp1(self.temp[0])
            self.temp_pwr[1] = self.pid_temp2(self.temp[1])
            self.ui.lineEdit_4.setText(format(self.temp_pwr[0],'.2f'))
            self.ui.lineEdit_6.setText(format(self.temp_pwr[1],'.2f'))

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
        self.ui.pushButton_10.setDisabled(False)
        self.ui.pushButton_19.setDisabled(True)
        self.elapsed_time = 0

        time_now  =  datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        self.file_name = time_now+".csv"
        self.data_file   = open( self.data_path + self.file_name,"w", newline = '')
        self.data_writer = csv.writer( self.data_file)
        self.data_writer.writerow(["time","tsp1","t1","pwr1","tsp2","t2","pwr2"])
        self.data_file.close()

    def stopTempCtrl(self):
        self.run_state = False
        self.ui.pushButton_19.setDisabled(False)
        self.ui.pushButton_10.setDisabled(True)
        self.elapsed_time = 0
        self.Fluo.LEDoff('H1')
        self.Fluo.LEDoff('H2')

    """
    def start(self):
        if self.dl.connected:
            self.run_state = True
            self.ui.pushButton_7.setDisabled(True)
            self.ui.pushButton_8.setDisabled(False)

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
        self.ui.pushButton_7.setDisabled(False)
        self.ui.pushButton_8.setDisabled(True)

    def setSampleTime(self):
        self.sample_time = float(self.ui.lineEdit_3.text())
        if self.sample_time < 0.1:
            self.sample_time = 0.1
        if self.connected:
            self.run_timer.stop()
            self.run_timer.setInterval(1000*self.sample_time)
            self.run_timer.start()

    def updateTime(self):
        current_time = QtCore.QTime.currentTime()
        label_time   = current_time.toString('hh:mm:ss')
        self.ui.lineEdit_11.setText(label_time)
        if self.run_state:
            self.elapsed_time += 1
            self.ui.lineEdit_12.setText(str(datetime.timedelta(seconds = self.elapsed_time)))

    def updateData(self):
        if self.run_state:

            print("updating data")
            self.t_.append(self.elapsed_time)
            self.ui.lineEdit_13.setText(format(self.dl.i,'.2f'))
            self.ui.lineEdit_5.setText( format(self.dl.v,'.2f'))
            self.ui.lineEdit_10.setText(format(self.dl.pwr,'.2f'))
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
