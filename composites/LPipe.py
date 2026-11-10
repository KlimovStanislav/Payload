from __future__ import annotations

from composites.Block import Block

from components.Liquidable import Liquidable, State
from components.Clickable import Clickable
from components.Rotatable import Rotatable, Angle
from components.SceneObject import Cell

from ui.Widgets import AutoUI

ANGLE_CNV = {
    Angle.UP:    [Cell(0, -1), Cell(1, 0)],
    Angle.RIGHT: [Cell(1, 0),  Cell(0, 1)],
    Angle.DOWN:  [Cell(0, 1),  Cell(-1, 0)],
    Angle.LEFT:  [Cell(-1, 0), Cell(0, -1)],
}

class LPipe(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.components[Rotatable] = Rotatable(self)
        self.components[Liquidable] = Liquidable(self, State.PASSIVE, opens=ANGLE_CNV[self.components[Rotatable].value])
        self.components[Clickable] = Clickable(self, lambda obj: AutoUI(obj).Show())

        self.finish()