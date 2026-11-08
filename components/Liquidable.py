from __future__ import annotations

from PyQt6 import QtWidgets
from ui.Widgets import Labels, AutoUI

from components.Rotatable import Angle, Rotatable
from enum import auto, Enum
from components.SceneObject import SceneObject, Cell

class State(Enum):
    ACTIVE = auto()
    PASSIVE = auto()

ANGLE_CNV = {Angle.UP:[Cell(0, 1), Cell(0, -1)],
             Angle.RIGHT:[Cell(-1, 0), Cell(1, 0)],
             Angle.DOWN:[Cell(0, -1), Cell(0, 1)],
             Angle.LEFT:[Cell(1, 0), Cell(-1, 0)]}

class Liquidable:
    save = ("pressure", "fluids", "volume")
    def __init__(self, owner:SceneObject, type:State, opens:list[Cell]|None=None):
        self.owner = owner
        self.type = type
        if opens is not None:
            self.opens = opens
        elif Rotatable in owner.components:
            self.opens = ANGLE_CNV[owner.components[Rotatable].value]
        else:
            raise NotImplementedError(f"Obj <{owner}> dont have <Rotatable> compoent and the <opens> parameter not passed")

        self.pressure: float = 0
        self.fluids: dict[str, float] = {}
        self.volume: float = 1   

    def ui(self):
        class w(AutoUI.Component):
            def __init__(self, obj:Liquidable):
                super().__init__(obj)
                self.obj = obj
                layout = QtWidgets.QHBoxLayout(self)

                self.pressure_label = Labels.Body(f"Pressure: {self.obj.pressure}")

                layout.addWidget(self.pressure_label)

            def refresh(self):
                self.pressure_label.setText(f"Pressure: {self.obj.pressure}")
    
        return w(self)