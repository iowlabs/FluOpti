# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')  # 'Agg' es un backend sin interfaz

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())