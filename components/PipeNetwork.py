from __future__ import annotations

from components.Network import Network

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.SceneObject import SceneObject
    from world.World import World

class PipeNetwork(Network):
    def __init__(self, w):
        super().__init__(w)

    def update(self, dt):
        ...