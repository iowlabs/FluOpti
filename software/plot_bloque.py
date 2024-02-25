# ------------------------------------------------------
# -------------------- mplwidget.py --------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import*
from PyQt5.QtCore import QSize
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure


# class MiToolbar(NavigationToolbar):
#     def __init__(self, canvas, parent, coordinates=True):
#         super().__init__(canvas, parent, coordinates)

#         # Puedes personalizar la apariencia aquí
#         self.setIconSize(QSize(18, 18))

#         # Personalizar la apariencia
#         self.setStyleSheet("""
#             QToolButton {
#                 background-color: #4CAF50;
#                 color: white;
#                 border: 1px solid #4CAF50;
#                 border-radius: 4px;
#                 margin: 2px;
#             }
#             QToolButton:hover {
#                 background-color: #45a049;
#                 color: blue;
#             }
#             QToolButton:pressed {
#                 background-color: #3c8e41;
#             }
#         """)

#         # Quitar bordes
#         self.layout().setContentsMargins(0, 0, 0, 0)
#         self.layout().setSpacing(2)
#         self.setStyleSheet("border: none;")

#         # Agregar ícono personalizado
#         # icon = self.setIcon("path/to/your/icon.png")

#         # # Personalizar los botones de la barra de herramientas
#         # self.addAction(self.actionZoom, icon=icon, text='Zoom', tip='Zoom In/Out', triggered=self.zoom)
#         # self.addAction(self.actionHome, icon=icon, text='Inicio', tip='Inicio', triggered=self.home)
#         # self.addAction(self.actionBack, icon=icon, text='Atrás', tip='Atrás', triggered=self.back)
#         # self.addAction(self.actionForward, icon=icon, text='Adelante', tip='Adelante', triggered=self.forward)
#         # self.addAction(self.actionPan, icon=icon, text='Pan', tip='Pan', triggered=self.pan)
#         # self.addAction(self.actionSave, icon=icon, text='Guardar', tip='Guardar', triggered=self.save_figure)

#     def set_message(self, s):
#         # Personalizar el mensaje en la barra de estado
#         if s:
#             s = "DummyReceiver: " + s
#         super().set_message(s)
    
class Plot_bloque(QWidget):
    
    def __init__(self, parent = None):

        QWidget.__init__(self, parent)
        
        self.canvas = FigureCanvas(Figure())
        
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        
        self.canvas.axes =  self.canvas.figure.subplots(nrows= 3, sharex=True)
        self.canvas.figure.set_facecolor('#F2F2F2')
        self.canvas.figure.subplots_adjust(hspace=0)
        # clear the axes and redraw the plot
        #self.canvas.axes.figure.tight_layout()
        self.setLayout(vertical_layout)

