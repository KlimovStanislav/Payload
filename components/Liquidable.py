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
    PRESSURE_FULL: float = 100.0
    save = ("fluids", "capacity")
    def __init__(self, owner:SceneObject, type:State, opens:list[Cell]|None=None):
        self.owner = owner
        self.type = type
        if opens is not None:
            self.opens = opens
        elif Rotatable in owner.components:
            self.opens = ANGLE_CNV[owner.components[Rotatable].value]
        else:
            raise NotImplementedError(f"Obj {owner} dont have <Rotatable> component and the <opens> parameter not passed")

        self._pressure = 0
        self.fluids: dict[str, float] = {}
        self.capacity: float = 10

    @property
    def pressure(self) -> float:
        return self.PRESSURE_FULL * self.fill_ratio

    @pressure.setter
    def pressure(self, v: float):
        self._pressure = v

    @property
    def target_pressure(self) -> float:
        return self.PRESSURE_FULL * self.fill_ratio

    @property
    def volume(self) -> float:
        return sum(self.fluids.values())

    @property
    def fill_ratio(self) -> float:
        if self.capacity <= 1e-12:
            return 0.0
        return min(1.0, self.volume / self.capacity)

    @property
    def free_space(self) -> float:
        return max(0.0, self.capacity - self.volume)

    def recompute_pressure(self):
        self.pressure = self.PRESSURE_FULL * self.fill_ratio

    def ui(self):
        class w(AutoUI.Component):
            def __init__(self, obj:Liquidable):
                super().__init__(obj)
                self.obj = obj
                layout = QtWidgets.QHBoxLayout(self)

                self.pressure_label = Labels.Body(f"Pressure: {self.obj.pressure}\nFluids: {self.obj.fluids}")

                layout.addWidget(self.pressure_label)

            def refresh(self):
                self.pressure_label.setText(f"Pressure: {self.obj.pressure}\nFluids: {self.obj.fluids}")
    
        return w(self)