from __future__ import annotations
from typing import Callable

from composites.Block import Block

from components.Updatable import Updatable
from components.Liquidable import Liquidable
from components.Clickable import Clickable
from components.Removable import Removable
from components.Switchable import Switchable
from components.Temperaturable import Temperaturable

import random

from base.folders import block_config

from ui.Widgets import AutoUI

class Pipe(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.components[Liquidable] = Liquidable(self)
        self.components[Clickable] = Clickable(self, lambda obj: AutoUI(obj).Show())