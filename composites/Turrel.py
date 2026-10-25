from __future__ import annotations

from composites.Block import Block

from base.folders import block_config
from base.functions import get_texture

from components.Updatable import Updatable
from components.Storable import Storable
from components.Removable import Removable

from PyQt6.QtCore import QPointF

from composites.Projectile import Projectile

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from composites.Unit import Unit

import math

def angle_to(turret_x: float, turret_y: float, target_x: float, target_y: float) -> float:
    dx = target_x - turret_x
    dy = target_y - turret_y
    return math.degrees(math.atan2(dy, dx))

class Turrel(Block):
    def __init__(self, *args, **kwargs):
        self.stored = 0
        super().__init__(*args, **kwargs)
        max_stored = block_config[self.name].get("max_stored", 10)

        self.target:Unit|None = None

        if self.w.scene is not None:
            self.center = self.w.scene.addPixmap(get_texture("pulsar"))
            self.center.setPos(self.cell.x*32, self.cell.y*32)
            self.center.setTransformOriginPoint(QPointF(16, 16))
            self.center.setZValue(40)

        self.components[Storable] = Storable(self, {}, max_stored)
        self.components[Updatable] = Updatable(self, [(500, Turrel.upd_shoot), (250, Turrel.upd_target)])
        self.components[Removable] = Removable(self, Turrel.remove)

    def remove(self):
        if self.center is not None:
            if self.center.scene() is not None:
                self.center.scene().removeItem(self.center)
        super().remove()

    @staticmethod
    def upd_shoot(obj:Turrel):
        if obj.target is None:
            return
        
        if obj.center is not None:
            obj.center.setRotation(angle_to(obj.cell.x, obj.cell.y, obj.target.pos.x, obj.target.pos.y)+90)

        Projectile(obj.w, obj.target, obj.cell, "missile")

    @staticmethod
    def upd_target(obj:Turrel):
        nearest = 10
        obj.target = None
        for unit in obj.w.units:
            if (len:=(unit.cell.x-obj.cell.x)**2+(unit.cell.y-obj.cell.y)**2) < nearest*nearest:
                nearest = len
                obj.target = unit