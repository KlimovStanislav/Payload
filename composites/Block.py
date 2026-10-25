from __future__ import annotations

from base.folders import folder, block_config
import applib
import base.functions as func
from base.MusicPlayer import MusicPlayer
from PyQt6.QtWidgets import QGraphicsItem

from components.SceneObject import SceneObject, Cell, Size

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.World import World

@func.safe_class
class Block(SceneObject):
    save = ("name",)
    def __init__(self, w:World, cell:Cell, name:str):
        if cell.x >= w.size.w or cell.y >= w.size.h or cell.x < 0 or cell.y < 0:
            self.exists = False
            folder.log.write(f"Block <{name}(x:{cell.x}, y:{cell.y})> Located behind the world", type="BlockData")

        integrity = block_config[name].get("integrity", 1)
        self.pixmap = func.get_texture(name)

        super().__init__(w, cell, Size(self.pixmap.width()//32, self.pixmap.height()//32), name, integrity)

        self.place()
    
    def draw(self):
        if self.exists and self.w.scene is not None:
            self.pixmap_item = self.w.scene.addPixmap(self.pixmap)
            if block_config[self.name].get("centered", False):
                self.pixmap_item.setPos((self.cell.x-(self.size[0]/4))*32, (self.cell.y-(self.size[1]/4))*32)
            else:
                self.pixmap_item.setPos(self.cell.x*32, self.cell.y*32)
            self.pixmap_item.setZValue(block_config[self.name]["z"])  
            self.pixmap_item.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def place(self):
        if hasattr(self, "pixmap_item"):
            folder.log.write("2 раза ставишь", type=applib.ERROR)
            return
        
        for cell in self.get_occupied_cells():
            blocks = self.w.block_map.get(cell)
            if blocks is None:
                continue
            for block in blocks:
                if block is self or block_config[block.name]["z"] < 20:
                    continue
                return
            
        self.draw()
        MusicPlayer.play("place", volume=0.7)
        self.w.append_block(self)

    def remove(self):
        if not self.exists:
            return
        self.exists = False
            
        self.w.remove_block(self)

    def info(self):
            output = ""
            for name, value in self.__dict__.items():
                output += f"{name}: {value}, "
            return f"<{type(self).__name__}({output[:-2]})>"

    def __repr__(self):
        return f"TEMPERATURE: {self.temperature}, <{type(self).__name__}>"