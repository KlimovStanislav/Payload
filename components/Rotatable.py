from __future__ import annotations
from enum import Enum, auto

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from components.SceneObject import SceneObject

class Rotatable:
    def __init__(self, owner:SceneObject):
        self.owner = owner

    def __call__(self, value):
        self.value = value