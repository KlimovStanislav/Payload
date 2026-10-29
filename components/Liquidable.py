from __future__ import annotations
import traceback, applib

from typing import TYPE_CHECKING

from PyQt6 import QtWidgets

from typing import TYPE_CHECKING

from ui.Widgets import Labels, AutoUI, Buttons

from enum import auto, Enum

if TYPE_CHECKING:
    from components.SceneObject import SceneObject

class State(Enum):
    ACTIVE = auto()
    PASSIVE = auto()

class Liquidable:
    def __init__(self, owner:SceneObject, type:State):
        self.owner = owner
        self.type = type
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