from __future__ import annotations

from base.functions import get_texture

from components.Updatable import Updatable

from components.SceneObject import SceneObject, Cell, Size

from composites.Unit import Unit, Position

from PyQt6.QtCore import QPointF

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.World import World

import math

def angle_to(turret_x: float, turret_y: float, target_x: float, target_y: float) -> float:
    dx = target_x - turret_x
    dy = target_y - turret_y
    return math.degrees(math.atan2(dy, dx))

class Projectile(SceneObject):
    __slots__ = ("w", "cell", "pos", "name", "pixmap", "pixmap_item", "components", "target", "size", "exists")
    def __init__(self, w:World, target, cell:Position, name:str):
        self.pixmap = get_texture(name)
   
        super().__init__(w, Cell(int(cell.x), int(cell.y)), Size(1, 1), name, 1)

        self.pos = Position(cell.x, cell.y)

        self.target:SceneObject|None = target

        self.components[Updatable] = Updatable(self, [(30, Projectile.upd)])

        self.place()

    def draw(self):
        if self.w.scene is not None:
            self.pixmap_item = self.w.scene.addPixmap(self.pixmap)
            self.pixmap_item.setTransformOriginPoint(self.pixmap.width() / 2, self.pixmap.height()  / 2)
            self.pixmap_item.setPos(self.pos.x*32, self.pos.y*32)
            self.pixmap_item.setZValue(40)

    def place(self):             
        self.draw()
        self.w.append_projectile(self)

    @staticmethod
    def upd(obj:Projectile, task, dt):
            if not obj.target.exists:
                obj.remove()
                return
            
            dx = obj.target.cell.x - obj.pos.x
            dy = obj.target.cell.y - obj.pos.y
            dist = math.hypot(dx, dy)

            if dist > 0:
                obj.pos.x += dx / dist * dt/100
                obj.pos.y += dy / dist * dt/100
                obj.pixmap_item.setPos(QPointF(obj.pos.x*32, obj.pos.y*32))
                obj.cell = Cell(round(obj.pos.x), round(obj.pos.y))

            target = None
            if (t:=obj.w.get_unit_at(obj.cell.x, obj.cell.y)) is not None:
                target:SceneObject = t
            elif (t:=obj.w.get_block_at(obj.cell.x, obj.cell.y)) is not None:
                target:SceneObject = t

            if target is not None:
                target.integrity -= 1
                if target.integrity <= 0:
                    target.remove()
                obj.remove()

    def remove(self):
        if not self.exists:
            return
        
        self.exists = False 
        self.w.remove_projectile(self)
