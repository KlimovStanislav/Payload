from __future__ import annotations

from components.Updatable import Updatable

import math, random
from base.folders import folder
from base.MusicPlayer import MusicPlayer
from base.functions import safe_class, get_texture
from base.folders import unit_config

from components.SceneObject import SceneObject, Cell

from composites.Unit import Unit
from composites.Projectile import Projectile

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from composites.Block import Block

@safe_class
class HoverUnit(Unit):
    def __init__(self, *args, filter:list[SceneObject]=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter = filter
        self.target:Block|None = None
        self.components[Updatable] = Updatable(self, [(250, HoverUnit.upd_target), (50, HoverUnit.update), (450, HoverUnit.upd_shoot)])
        self.speed = 10
        self.orbit_radius = 4
        self.state = "APPROACH"
        self.target = None

        self.orbit_angle = 0.0
        self.orbit_speed = 7
        self.orbit_sign = random.choice((-1, 1))  
        self.current_radius = self.orbit_radius 

    @staticmethod
    def upd_shoot(obj:HoverUnit):
        if obj.target is None:
            return
    
        Projectile(obj.w, obj.target, obj.cell, "missile")

    @staticmethod
    def update(obj: HoverUnit, task, dt):
        dt /= 1000
        if obj.target is None:
            return

        tx, ty = obj.target.cell.x, obj.target.cell.y
        dx, dy = tx - obj.pos.x, ty - obj.pos.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        if obj.state == "APPROACH":
            if dist <= obj.orbit_radius + 10:
                # входим в орбиту: запоминаем угол и знак вращения
                obj.state = "ORBIT"
                obj.orbit_angle = math.atan2(obj.pos.y - ty, obj.pos.x - tx)
                obj.orbit_sign = 1 if obj.orbit_sign >= 0 else -1  # сохраняем выбранное
                obj.current_radius = dist  # стартуем с текущего расстояния, потом сожмём до orbit_radius
            else:
                step = obj.speed * dt
                obj.pos.x += dx / dist * step
                obj.pos.y += dy / dist * step
                obj.cell = Cell(round(obj.pos.x), round(obj.pos.y))
                obj.pixmap_item.setPos(obj.pos.x*32, obj.pos.y*32)
                return

        # ---- ORBIT ----
        if dist > obj.orbit_radius + 40:
            obj.state = "APPROACH"
            return

        # плавно подтягиваем радиус к целевому
        radius_lerp = 1 - math.exp(-4.0 * dt)   # ~ сглаживание
        obj.current_radius += (obj.orbit_radius - obj.current_radius) * radius_lerp

        # крутимся
        obj.orbit_angle += obj.orbit_speed * obj.orbit_sign * dt

        obj.pos.x = tx + math.cos(obj.orbit_angle) * obj.current_radius
        obj.pos.y = ty + math.sin(obj.orbit_angle) * obj.current_radius

        obj.cell = Cell(round(obj.pos.x), round(obj.pos.y))
        obj.pixmap_item.setPos(obj.pos.x*32, obj.pos.y*32)

    @staticmethod
    def upd_target(obj:HoverUnit):
        nearest = float("inf")
        obj.target = None
        for block in obj.w.blocks:
            if obj.filter is not None:
                for cls in obj.filter:
                    if not isinstance(block) in cls:
                        continue

            if (len:=(block.cell.x-obj.cell.x)**2+(block.cell.y-obj.cell.y)**2) < nearest*nearest:
                nearest = len
                obj.target = block
