from __future__ import annotations

from composites.Block import Block

from components.Liquidable import Liquidable, State
from components.Clickable import Clickable
from components.SceneObject import Cell

from ui.Widgets import AutoUI

class XPipe(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.components[Liquidable] = Liquidable(self, State.PASSIVE, opens=[Cell(1, 0), Cell(-1, 0), Cell(0, 1), Cell(0, -1)])
        self.components[Clickable] = Clickable(self, lambda obj: AutoUI(obj).Show())

        self.finish()