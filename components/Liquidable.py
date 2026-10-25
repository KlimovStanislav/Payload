from __future__ import annotations
import traceback, applib

from typing import Callable, TYPE_CHECKING

from PyQt6 import QtWidgets

from typing import TYPE_CHECKING

from ui.Widgets import Labels, AutoUI, Buttons

if TYPE_CHECKING:
    from components.SceneObject import SceneObject

class Liquidable:
    def __init__(self, owner:SceneObject):
        self.owner = owner
        self.pressure: float = 0.0
        self.fluids: dict[str, float] = {}
        self.volume: float = 1.0      
        self.conductivity: float = 1.0

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