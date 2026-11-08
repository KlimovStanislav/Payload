from __future__ import annotations
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QRadioButton, QGroupBox

app = QApplication(sys.argv)

VARIANTS = [("1", "2", "3", "4", 1), ("1", "2", "3", "4", 1)]

class Variant(QGroupBox):
    def __init__(self, window:Variants, tuple:tuple):
        super().__init__(window)
        layout = QHBoxLayout(self)
        self.layout_1 = QVBoxLayout()
        self.layout_2 = QVBoxLayout()
        self.rbtn_1 = QRadioButton(tuple[0])
        self.rbtn_2 = QRadioButton(tuple[1])
        self.rbtn_3 = QRadioButton(tuple[2])
        self.rbtn_4 = QRadioButton(tuple[3])    

        dct = {1: self.rbtn_1, 2:self.rbtn_2, 3:self.rbtn_3, 4:self.rbtn_4}
        self.correct:QRadioButton = dct[tuple[4]]

        self.layout_1.addWidget(self.rbtn_1)
        self.layout_1.addWidget(self.rbtn_2)
        
        self.layout_2.addWidget(self.rbtn_3)
        self.layout_2.addWidget(self.rbtn_4)

        layout.addLayout(self.layout_1)
        layout.addLayout(self.layout_2)

class Variants(QWidget):
    def __init__(self, window:Window):
        super().__init__(window)
        self.variants:list[Variant] = []
        self.current = 0
        for var in VARIANTS:
            self.variants.append(Variant(self, var))
        self.layout_ = QVBoxLayout(self)

        self.layout_.addWidget(self.variants[self.current])

    def next(self, btn:QPushButton):
        self.variants[self.current].deleteLater()
        self.current += 1
        if len(self.variants) == self.current:
            print(123)
            self.current-=1
            self.layout_.addWidget(self.variants[self.current])
            for rbtn in [self.variants[self.current].rbtn_1, self.variants[self.current].rbtn_2, self.variants[self.current].rbtn_3, self.variants[self.current].rbtn_4]:
                rbtn.deleteLater()
            btn.setText("Конец")
            btn.clicked.disconnect()
            btn.clicked.connect(lambda *args: [app.exit()])
            return
        self.layout_.addWidget(self.variants[self.current])
        btn.clicked.disconnect()
        btn.clicked.connect(lambda *args: [self.check(btn), btn.setText("Следующий вопрос")])

    def check(self, btn:QPushButton):
        if len(self.variants)-1 == self.current:
            print(123)
            return
        for rbtn in [self.variants[self.current].rbtn_1, self.variants[self.current].rbtn_2, self.variants[self.current].rbtn_3, self.variants[self.current].rbtn_4]:
            rbtn.deleteLater()
        label = QLabel("Неправильно")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.variants[self.current].correct.isChecked():
            label.setText("Правильно")
        self.variants[self.current].layout().addWidget(label)

        btn.clicked.disconnect()
        if len(self.variants)-1 == self.current:
            print(123)
        else:
            btn.clicked.connect(lambda *args: [self.next(btn), btn.setText("Ответить")])

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 400)
        self.setWindowTitle("Memory Card")

        self.variants = Variants(self)
        self.btn = QPushButton("Ответить")
        self.btn.clicked.connect(lambda *args: [self.variants.check(self.btn), self.btn.setText("Следующий вопрос")])
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Выберете верное утверждение"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.variants)
        layout.addStretch()
        layout.addWidget(self.btn)

from pathlib import Path

rows = []
for p in Path(".").rglob("*.py"):
    if any(x in p.parts for x in {".venv","venv","__pycache__",".git"}):
        continue
    n = sum(1 for line in p.read_text(errors="ignore").splitlines()
            if line.strip() and not line.strip().startswith("#"))
    rows.append((n, str(p)))

rows.sort(reverse=True)
total = sum(n for n, _ in rows)
for n, p in rows:
    print(f"{n:5d}  {n/total*100:5.1f}%  {p}")

window = Window()
window.show()
app.exec()