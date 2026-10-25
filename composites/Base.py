from __future__ import annotations

from base.MusicPlayer import MusicPlayer
from base.folders import block_config

from composites.Block import Block

from components.Storable import Storable
from components.Clickable import Clickable

from ui.Widgets import AutoUI

class Base(Block):
    def __init__(self, *args, resource_panel=None, **kwargs):
        super().__init__(*args, **kwargs)
        max_size = block_config.get(self.name).get("max_storage", 10)

        self.components[Storable] = Storable(self, None, max_size)
        self.components[Clickable] = Clickable(self, lambda obj: AutoUI(obj).Show())

        self.panel = resource_panel