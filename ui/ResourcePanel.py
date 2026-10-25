from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from ui.Widgets import Labels

class ResourcePanel(QtWidgets.QWidget):
    def __init__(self, window):
        super().__init__(window)
        self.w = window
        
        self.layout_ = QtWidgets.QHBoxLayout(self)
        
        self.label_base = Labels.Mono()
        self.label_operator = Labels.Mono()

        self.layout_.addWidget(self.label_base)
        self.layout_.addWidget(self.label_operator)
        
        self.setMinimumSize(150, 50)
        self.reposition()
        self.update({}, {})

    def reposition(self):
        self.move((self.parent().width() - self.width()) // 2, 10)
        self.show()
        self.raise_()
    
    def update(self, dct_base:dict, dct_operator:dict):
        self.label_base.setText(f'Base\n{"\n".join(f"{k}: {v}" for k, v in dct_base.items())}')
        self.label_operator.setText(f'Operator\n{"\n".join(f"{k}: {v}" for k, v in dct_operator.items())}')

        self.adjustSize()
