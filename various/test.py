from __future__ import annotations
import sys, time, json, random
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QRadioButton, QFrame
from PyQt6.QtGui import QIcon

app = QApplication(sys.argv)

with open("various/questions.json", "r", encoding="UTF-8") as f:
    VARIANTS:list[list] = json.load(f)
random.shuffle(VARIANTS)

style = """
QPushButton {background: #eef0f1; color: #313131; border: 3px solid #ebebeb; font-weight: 600; border-radius: 5px; font-family: "Consolas"}
QPushButton:hover    {background: #9e9e9e}
QPushButton:pressed  {border-color: #262E36}
QPushButton:disabled {background: #4A3A1A; color: #6B5B3A}

QLabel {font-size: 20px; font-weight: 600; color: #D6DEE6; font-family: "Consolas"}

QFrame {
    background: qlineargradient(
        x1:1, y1:0, x2:0, y2:0,
        stop:0   rgba(46, 56, 66, 180),
        stop:0.5 rgba(38, 46, 54, 150),
        stop:1   rgba(30, 36, 42, 130));
    border: 3px solid #252e36;
    border-radius: 32px;}
"""

app.setStyleSheet(style)

class Variant(QFrame):
    def __init__(self, window:Variants, tuple:tuple):
        super().__init__(window)
        layout = QHBoxLayout(self)
        self.layout_1 = QVBoxLayout()
        self.layout_2 = QVBoxLayout()
        self.rbtn_1 = QRadioButton(tuple[0])
        self.rbtn_2 = QRadioButton(tuple[1])
        self.rbtn_3 = QRadioButton(tuple[2])
        self.rbtn_4 = QRadioButton(tuple[3])    

        dct = {1:self.rbtn_1, 2:self.rbtn_2, 3:self.rbtn_3, 4:self.rbtn_4}
        self.correct:QRadioButton = dct[tuple[4]]

        self.layout_1.addWidget(self.rbtn_1)
        self.layout_1.addWidget(self.rbtn_2)
        
        self.layout_2.addWidget(self.rbtn_3)
        self.layout_2.addWidget(self.rbtn_4)

        layout.addLayout(self.layout_1)
        layout.addLayout(self.layout_2)

        self.hide()

class Variants(QWidget):
    def __init__(self, window:Window):
        super().__init__(window)
        self.w = window
        self.variants:list[Variant] = []
        self.current = 0
        self.correct = 0
        for var in VARIANTS:
            self.variants.append(Variant(self, var))
        self.layout_ = QVBoxLayout(self)

        self.variants[self.current].show()
        self.layout_.addWidget(self.variants[self.current])

    def next(self, btn:QPushButton):
        self.variants[self.current].deleteLater()
        self.current += 1
        self.variants[self.current].show()
        self.layout_.addWidget(self.variants[self.current])
        btn.clicked.disconnect()
        btn.clicked.connect(lambda *args: [self.check(btn), btn.setText("Следующий вопрос")])

    def check(self, btn:QPushButton):
        for rbtn in [self.variants[self.current].rbtn_1, self.variants[self.current].rbtn_2, self.variants[self.current].rbtn_3, self.variants[self.current].rbtn_4]:
            rbtn.deleteLater()
        label = QLabel("Неправильно")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.variants[self.current].correct.isChecked():
            label.setText("Правильно")
            self.correct+=1
        self.variants[self.current].layout().addWidget(label)

        btn.clicked.disconnect()
        if len(self.variants)-1 == self.current:
            str = f"Конец\nПравильных ответов: {self.correct}/{len(self.variants)}\nРейтинг: {self.correct/len(self.variants)*100:.0f}%\nВремя прохождения теста: {time.time()-self.w.start:.1f} секунд\n\n"
            label.setText(str)
            with open("various/result.txt", "a", encoding="UTF-8") as f:
                f.write(str)
            btn.clicked.connect(lambda *args: [app.exit()])
        else:
            btn.clicked.connect(lambda *args: [self.next(btn), btn.setText("Ответить")])

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(700, 400)
        self.setWindowTitle("Memory Card")
        self.setWindowIcon(QIcon("various/icon.png"))

        self.start = time.time()

        self.variants = Variants(self)
        self.btn = QPushButton("Ответить")
        self.btn.clicked.connect(lambda *args: [self.variants.check(self.btn), self.btn.setText("Следующий вопрос")])
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Выберете верное утверждение"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.variants)
        layout.addStretch()
        layout.addWidget(self.btn)

window = Window()
window.show()
app.exec()