from __future__ import annotations

from components.SceneObject import Various
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from components.SceneObject import SceneObject

class Rotatable:
    save = ("value",)
    def __init__(self, owner:SceneObject, value:int|None=None):
        self.owner = owner
        self._value = 0
        self.value:int = value if value is not None else owner.w.various[Various.place_angle]

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, v:int):
        self._value = int(v)%360
        if hasattr(self.owner, "pixmap_item"):
            self.owner.pixmap_item.setRotation(self.value)