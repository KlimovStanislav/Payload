from __future__ import annotations

from PyQt6 import QtWidgets

from ui.Widgets import Labels, AutoUI

from typing import TYPE_CHECKING
import math
if TYPE_CHECKING:
    from components.SceneObject import SceneObject

def efficiency(x, x_min, x_opt, x_max) -> float:
    if x <= x_opt:
        t = (x - x_min) / (x_opt - x_min)  
    else:
        t = (x_max - x) / (x_max - x_opt)  
    t = max(0.0, min(1.0, t))            
    return math.sin(t * math.pi / 2)

class Temperaturable:
    def __init__(self, owner:SceneObject, min:int, opt:int, max:int):
        self.owner = owner
        self.min = min
        self.opt = opt
        self.max = max

    @property
    def value(self) -> float:
        return self.owner.w.temperature.field[self.owner.cell.y, self.owner.cell.x]

    @value.setter
    def value(self, value):
        for i in self.owner.get_occupied_cells():
            self.owner.w.temperature.field[i[1], i[0]] = value

    @property
    def coef(self) -> float:
        return efficiency(self.value, self.min, self.opt, self.max)

    def ui(self):
        class w(AutoUI.Component):
            def __init__(self, obj:Temperaturable):
                super().__init__(obj)
                        
                layout = QtWidgets.QVBoxLayout(self)  

                self.caution = Labels.Danger()
                self.label = Labels.Body(f"Temperature: {self.obj.value:.0f}℃\n Efficiency: {self.obj.coef:.2f}")

                layout.addWidget(self.label)
                layout.addWidget(self.caution)
        
            def refresh(self):
                coef = self.obj.coef
                self.label.setText(f"Temperature: {self.obj.value:.0f}℃\n Efficiency: {coef*100:.0f}%")
                self.caution.setText(f"OVERHEATING" if self.obj.value/self.obj.max >= 0.75 else "")
        
        return w(self)