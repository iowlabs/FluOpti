import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QPropertyAnimation, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Ventana Principal")

        self.button = QPushButton("Abrir Segunda Ventana", self)
        self.button.clicked.connect(self.abrir_segunda_ventana)

        self.label_animation = QLabel("¡La primera ventana está deshabilitada!", self)
        self.label_animation.setStyleSheet("color: red;")
        self.label_animation.setAlignment(Qt.AlignCenter)
        self.label_animation.hide()

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.label_animation)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def abrir_segunda_ventana(self):
        self.second_window = SecondWindow(self)

        # Deshabilitar la ventana principal temporalmente
        self.setEnabled(False)

        # Mostrar la etiqueta de animación
        self.label_animation.show()

        # Animación para resaltar el estado
        animation = QPropertyAnimation(self.label_animation, b"opacity")
        animation.setDuration(2000)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.finished.connect(self.restore_main_window)

        animation.start()

        self.second_window.show()

    def restore_main_window(self):
        # Restaurar la ventana principal cuando la animación ha terminado
        self.setEnabled(True)
        self.label_animation.hide()

class SecondWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SecondWindow, self).__init__(parent)

        self.setWindowTitle("Segunda Ventana")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
