from __future__ import annotations

from components.Network import Network

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.SceneObject import SceneObject
    from world.World import World

class PipeNetwork(Network):
    def __init__(self, w):
        super().__init__(w)
        self.edges: list[tuple] = []

    def add(self, node):
        super().add(node)
        self._rebuild_edges()

    def remove(self, node):
        super().remove(node)
        self._rebuild_edges()

    def _rebuild_edges(self):
        self.edges = []
        cells = {n.cell: n for n in self.nodes}
        for n in self.nodes:
            for c in n.get_around():
                other = cells.get(c)
                if other is not None and n is not other:
                    if id(n) < id(other):
                        self.edges.append((n, other))

    def update(self, dt: float):
        self._step_flow(dt)
        self._step_heat(dt)
        self._step_mix(dt)