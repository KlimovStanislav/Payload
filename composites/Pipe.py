from __future__ import annotations

from composites.Block import Block

from components.Liquidable import Liquidable, State
from components.Clickable import Clickable
from components.Rotatable import Rotatable

from ui.Widgets import AutoUI

class Pipe(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.components[Rotatable] = Rotatable(self)
        self.components[Liquidable] = Liquidable(self, State.PASSIVE)
        self.components[Clickable] = Clickable(self, lambda obj: AutoUI(obj).Show())

        self.finish()