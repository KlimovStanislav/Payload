from __future__ import annotations

from dataclasses import dataclass

import applib
from base.folders import folder
from base.MusicPlayer import MusicPlayer
from base.functions import safe_class, get_texture
from base.folders import unit_config
from components.SceneObject import SceneObject, Cell, Size

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.World import World

from dataclasses import dataclass

@dataclass
class Position:
    x: float
    y: float

@safe_class
class Unit(SceneObject):
    save = ("name",)
    def __init__(self, w:World, cell:Cell, name:str):
        self.pixmap = get_texture(name)
        integrity = unit_config[name].get("integrity", 1)

        super().__init__(w, cell,  Size(self.pixmap.width()//32, self.pixmap.height()//32), name, integrity)

        self.pos=Position(cell.x, cell.y)

        self.place()

    def draw(self):
        if self.w.scene is not None:
            self.pixmap_item = self.w.scene.addPixmap(self.pixmap)
            self.pixmap_item.setTransformOriginPoint(self.pixmap.width() / 2, self.pixmap.height()  / 2)
            self.pixmap_item.setPos(self.pos.x*32, self.pos.y*32)
            self.pixmap_item.setZValue(40)

    def place(self):             
        self.draw()
        self.w.append_unit(self)

    def get_occupied_cells(self):
        cells = set()
        width_tiles = self.pixmap_item.pixmap().width() // 32
        height_tiles = self.pixmap_item.pixmap().height() // 32
        
        for dx in range(width_tiles):
            for dy in range(height_tiles):
                cells.add((self.cell.x + dx, self.cell.y + dy))
        return cells

    def remove(self):
        if not self.exists:
            return
        self.exists = False
        
        self.w.remove_unit(self)

    def __repr__(self):
        output = ""
        for name, value in self.__dict__.items():
            output += f"{name}: {value}, "
        return f"<{type(self).__name__}({output[:-2]})>"