from __future__ import annotations
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QRadioButton, QGroupBox

app = QApplication(sys.argv)

class Variants(QGroupBox):
    def __init__(self, window:Window):
        super().__init__(window)
        layout = QHBoxLayout(self)
        self.layout_1 = QVBoxLayout()
        self.layout_2 = QVBoxLayout()

        self.rbtn_1 = QRadioButton("Смурфики")
        self.rbtn_2 = QRadioButton("Энцы")
        self.rbtn_3 = QRadioButton("Русские")
        self.rbtn_4 = QRadioButton("Алауты")

        self.layout_1.addWidget(self.rbtn_1)
        self.layout_1.addWidget(self.rbtn_2)

        self.layout_2.addWidget(self.rbtn_3)
        self.layout_2.addWidget(self.rbtn_4)

        layout.addLayout(self.layout_1)
        layout.addLayout(self.layout_2)

    def check(self):
        for rbtn in [self.rbtn_1, self.rbtn_2, self.rbtn_3, self.rbtn_4]:
            rbtn.deleteLater()
        label = QLabel("Неправильно")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.rbtn_1.isChecked():
            for rbtn in [self.rbtn_1, self.rbtn_2, self.rbtn_3, self.rbtn_4]:
                rbtn.deleteLater()
            label.setText("Правильно")
        self.layout().addWidget(label)

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 400)
        self.setWindowTitle("Memory Card")

        self.variants = Variants(self)
        self.btn = QPushButton("Ответить")
        self.btn.clicked.connect(lambda *args: self.variants.check())
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Какой национальности не существует?"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.variants)
        layout.addStretch()
        layout.addWidget(self.btn)

window = Window()
window.show()
app.exec()