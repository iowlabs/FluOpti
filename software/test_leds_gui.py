import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGroupBox, QLabel, QPushButton


class LEDApp(QWidget):
    def __init__(self):
        super(LEDApp, self).__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('LED App')
        self.setGeometry(100, 100, 400, 200)

        # Crear un QGroupBox para contener los labels
        led_group_box = QGroupBox('LEDs')
        vbox = QVBoxLayout()

        # Crear los labels para los LEDs
        self.label_rojo = QLabel('Rojo')
        self.label_verde = QLabel('Verde')
        self.label_azul = QLabel('Azul')
        self.label_blanco = QLabel('Blanco')

        # Añadir los labels al layout
        vbox.addWidget(self.label_rojo)
        vbox.addWidget(self.label_verde)
        vbox.addWidget(self.label_azul)
        vbox.addWidget(self.label_blanco)

        led_group_box.setLayout(vbox)

        # Botón para simular el cambio de estado de los LEDs
        btn_cambiar_estado = QPushButton('Cambiar Estado', self)
        btn_cambiar_estado.clicked.connect(self.cambiar_estado_leds)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(led_group_box)
        main_layout.addWidget(btn_cambiar_estado)

        self.setLayout(main_layout)

    def cambiar_estado_leds(self):
        # Simulación de cambio de estado de los LEDs
        # Aquí deberías implementar la lógica real para cambiar el estado de tus LEDs
        # Puedes cambiar estos valores según tu lógica
        estado_rojo = True
        estado_verde = True
        estado_azul = True
        estado_blanco = True

        # Actualizar el estilo de los labels según el estado de los LEDs
        self.actualizar_estilo_led(self.label_rojo, estado_rojo, 'red')
        self.actualizar_estilo_led(self.label_verde, estado_verde, 'yellowgreen')
        self.actualizar_estilo_led(self.label_azul, estado_azul, 'blue')
        self.actualizar_estilo_led(self.label_blanco, estado_blanco, 'lightgray')

    def actualizar_estilo_led(self, label, estado, color):
        # Actualizar el estilo del QLabel para representar el estado del LED
        if estado:
            label.setStyleSheet(f'QLabel {{ background-color: {color}; border-radius: 50px; }}')
        else:
            label.setStyleSheet('QLabel {}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = LEDApp()
    ventana.show()
    sys.exit(app.exec_())
