from __future__ import annotations

from composites.Block import Block

from components.SceneObject import Cell
from components.Updatable import Updatable
from components.Liquidable import Liquidable, State
from components.Clickable import Clickable
from components.Rotatable import Rotatable
from components.Switchable import Switchable

from ui.Widgets import AutoUI

class Pump(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.components[Switchable] = Switchable(self, False)
        self.components[Rotatable] = Rotatable(self)
        self.components[Updatable] = Updatable(self, [(1000, self.upd)])
        self.components[Clickable] = Clickable(self, lambda obj: AutoUI(obj).Show())
        self.components[Liquidable] = Liquidable(self, State.ACTIVE)

        self.finish()

    def upd(self, dt):
        if not self.components[Switchable].state:
            return
        angle = self.components[Liquidable].opens
        block_start = self.w.block_map.get(Cell(self.cell.x-angle[0].x, self.cell.y-angle[0].y), [])
        blocks_end = self.w.block_map.get(Cell(self.cell.x+angle[1].x, self.cell.y+angle[1].y), [])
        for block in block_start:
            if Liquidable in block_start:
                block.components[Liquidable].volume -= 0
                block.components[Liquidable].pressure -= 0
                break
        
        for block in blocks_end:
            if Liquidable in block.components:
                block.components[Liquidable].volume += 1
                block.components[Liquidable].pressure += 1
                break
