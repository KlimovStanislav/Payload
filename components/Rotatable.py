from __future__ import annotations
from enum import Enum, auto

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from components.SceneObject import SceneObject

class Side(Enum):
    RIGHT = auto()
    LEFT = auto()
    UP = auto()
    DOWN = auto()

class Rotatable:
    def __init__(self, owner:SceneObject, min:int, opt:int, max:int):
        self.owner = owner
        self.value = Side.UP

    def __call__(self, value):
        self.value = value