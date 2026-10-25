from __future__ import annotations

from composites.Block import Block
from composites.Unit import Unit

from PyQt6.QtCore import QPointF

from base.composites import composites
from base.MusicPlayer import MusicPlayer
from base.folders import folder, block_config, unit_config
from base.functions import safe_class, get_texture

from components.Clickable import Clickable
from components.Updatable import Updatable
from components.Removable import Removable
from components.Placable import Placable
from components.Storable import Storable

from world.TempField import TempField

from components.SceneObject import SceneObject, Cell, Size
from components.Network import Network

import applib, random
from functools import partialmethod

from typing import TYPE_CHECKING, Literal, cast
if TYPE_CHECKING:
    from composites.StorageBlock import StorageBlock
    from composites.Unit import Unit
    from composites.Projectile import Projectile

    from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem

class Storage:
    def __init__(self, max_size:int):
        self.storage = {}
        self.max_size = max_size

    def dict(self) -> dict:
        return self.storage
            
    def add(self, item, count):
        if count == 0:
            return True
        
        if item in self.dict():
            self.storage[item] += count
        else:
            self.storage[item] = count
    
        if self.storage[item] > self.max_size: 
            self.storage[item] = self.max_size
            return False
        return True
    
    def empty(self):
        if len(self.dict()) == 0:
            return True
        return False
        
    def reduce(self, item, count):
        if item in self.dict():
            self.dict()[item] -= count
        else:
            return False
            
        if self.dict()[item] < 0: 
            del self.dict()[item]
            return False
        return True    

class Operator:
    def __init__(self, world:World, name):
        self.w = world
        self.name = name
        self.inventory = Storage(100)

@safe_class
class World:
    def __init__(self, size:Size=Size(256, 256), scene:QGraphicsScene|None=None, window=None, devmode:bool=folder.config.get("devmode"), temperature=20):
        self.size = size

        self.window = window
        self.operator = Operator(self, f"OPERATOR #{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}")

        self.blocks:list[Block] = []
        self.block_map:dict[Cell, list[Block]] = {}

        self.units:list[Unit] = []
        self.unit_map:dict[Cell, list[Unit]] = {}
    
        self.networks:list[Network] = []
        self.projectiles:list[Projectile] = []

        self.exported:Storage[str, int] = Storage(9999)

        self.Base:StorageBlock|None = None
        self.devmode = devmode

        self.selected:Block|Unit|None = None
        self.selected_scene_item:None|QGraphicsPixmapItem=None

        self.relief_map:None|QGraphicsPixmapItem=None

        self.temperature = TempField(size.h, size.w, temperature)

        self.placing_block:str = None
        self.opened:list[str] = []

        self.scene = scene

    def update(self, dt):
        folder.plugins.call("update", dt*1000)

        for block in self.blocks.copy():
            if Updatable in block.components:
                block.components[Updatable](dt*1000)
            
        for unit in self.units.copy():
            if Updatable in unit.components:
                unit.components[Updatable](dt*1000)

        for proj in self.projectiles.copy():
            if Updatable in proj.components:
                proj.components[Updatable](dt*1000)

        self.temperature.update(dt)

    def remove_block(self, block:Block):
        if block in self.blocks:
            self.blocks.remove(block)

        for xcoord, ycoord in block.get_occupied_cells():
            if (xcoord, ycoord) in self.block_map:
                blocks = cast(list[Block], self.block_map.get(Cell(xcoord, ycoord)))
                if block in blocks:
                    blocks.remove(block)
                if len(blocks) == 0:
                    del self.block_map[Cell(xcoord, ycoord)]

        if not self.devmode:
            cost:dict = block_config[block.name].get("cost")
            coef = folder.config.get("craft_coef", 1)
            if cost is not None and self.Base is not None:
                for name, value in cost.items():
                    self.Base.components[Storable].add(name, int(value*coef))

        if not self.devmode and block_config[block.name]["z"] < 20:
            return
        
        if Removable in block.components:
            block.components[Removable]()
                        
        block.exists = False
        if hasattr(block, 'pixmap_item'):
            MusicPlayer.play(random.choice(["destruction_1", "destruction_2"]), volume=0.7)
            scene = block.pixmap_item.scene()
            scene.removeItem(block.pixmap_item)
            scene.update()

    def append_block(self, block:Block):
        self.blocks.append(block)

        for xcoord, ycoord in block.get_occupied_cells():
            if (blocks:=self.block_map.get(Cell(xcoord, ycoord))) is not None:
                self.block_map[Cell(xcoord, ycoord)] = [block, *blocks]
                continue
            self.block_map[Cell(xcoord, ycoord)] = [block]

        for network in self.networks:
            if network.suability(block):
                network.add(block)

    def remove_unit(self, unit:Unit):
        if unit in self.units:
            self.units.remove(unit)
        
        if (unit.cell.x, unit.cell.y) in self.unit_map:
            units = cast(list[Unit], self.unit_map.get(unit.cell))
            if unit in units:
                units.remove(unit)
            if len(units) == 0:
                del self.unit_map[unit.cell]
                
        if Removable in unit.components:
            unit.components[Removable]()
                                
        unit.exists = False
        if hasattr(unit, 'pixmap_item'):
            scene = unit.pixmap_item.scene()
            scene.removeItem(unit.pixmap_item)
            scene.update()

    def append_unit(self, unit:Unit):
        self.units.append(unit)

        for cell in unit.get_occupied_cells():
            if (units:=self.unit_map.get(cell)) is not None:
                self.unit_map[cell] = [unit, *units]
                continue
            self.unit_map[cell] = [unit]

    def remove_projectile(self, proj:Projectile):
        if proj in self.blocks:
            self.projectiles.remove(proj)
                
        if Removable in proj.components:
            proj.components[Removable]()

        if hasattr(proj, 'pixmap_item'):
            scene = proj.pixmap_item.scene()
            scene.removeItem(proj.pixmap_item)
            scene.update()

    def append_projectile(self, proj:Projectile):
        self.projectiles.append(proj)

    def append_network(self, network:Network):
        self.networks.append(network)

    def remove_network(self, network:Network):
        self.networks.remove(network)

    def click(self, type:Literal["left", "right"], x, y) -> None:
        if type == "left":
            MusicPlayer.play("click_1")
            existing = self.get_block_at(x, y)
            if existing and block_config[existing.name]["z"] >= 20:
                if Clickable in existing.components and existing: # is self.selected для выделения
                    existing.components[Clickable]()
                else:
                    #выделение
                    return
                    self.selected = existing
                    if self.scene is not None:
                        if self.selected_scene_item is not None:
                            self.scene.removeItem(self.selected_scene_item)
                        self.selected_scene_item = self.scene.addPixmap(get_texture(f"outline({existing.size[0]}x{existing.size[1]})"))
                        self.selected_scene_item.setPos(QPointF(existing.cell.x*32, existing.cell.y*32))
                        self.selected_scene_item.setZValue(100)

            else:  
                type_name = None
                cost = None

                self.selected = None
                if self.selected_scene_item is not None:
                    self.scene.removeItem(self.selected_scene_item)
                    self.selected_scene_item = None

                if self.placing_block is None:
                    return
        
                if self.placing_block in block_config:
                    type_name = block_config[self.placing_block].get("type")
                    cost = block_config[self.placing_block].get("cost")
        
                if self.placing_block in unit_config:
                    type_name = unit_config[self.placing_block].get("type")
                    cost = unit_config[self.placing_block].get("cost")
        
                block_class = composites.get(type_name)
                if block_class is None:
                    folder.log.write(f"Class <{type_name}> not exists", type=applib.ERROR)
                    return
        
                if cost is not None and self.Base is not None:
                    for name, value in cost.items():
                        coef = folder.config.get("craft_coef", 1)
                        if not self.Base.components[Storable].reduce(name, int(value*coef)):
                            return
                                    
                obj:SceneObject = block_class(self, cell=Cell(x, y), name=self.placing_block)
                if Placable in obj.components:
                    obj.components[Placable]()
                
        elif type == "right":
            existing = self.get_block_at(x, y)
            if existing:            
                self.remove_block(existing)

            #выделение
            return
            self.selected = None
            if self.scene is not None:
                if self.selected_scene_item is not None:
                    self.scene.removeItem(self.selected_scene_item)
        else:
            raise Exception(f"type <{type}> has no handler")

    def get_block_at(self, x, y) -> Block|None:
        blocks = self.block_map.get(Cell(x, y), None)
        if blocks is not None:
            return max(blocks, key=lambda ex: block_config[ex.name]["z"])

    def get_unit_at(self, x, y) -> Unit|None:
        unit = self.unit_map.get(Cell(x, y), None)
        if unit is not None:
            return max(unit, key=lambda ex: ex.integrity)
    
    place = partialmethod(click, "left")
    remove = partialmethod(click, "right")
