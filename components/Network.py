from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.SceneObject import SceneObject
    from world.World import World

class Network:
    def __init__(self, w: World):
        self.w = w
        self.nodes: list[SceneObject] = []
        self.w.append_network(self)

    def add(self, node: SceneObject):
        self.nodes.append(node)
        node.networks[self.__class__] = self

    def remove(self, node: SceneObject):
        if node in self.nodes:
            self.nodes.remove(node)
            node.networks.pop(self.__class__, None)

    def __contains__(self, obj: SceneObject):
        return obj in self.nodes

    def suability(self, obj: SceneObject) -> bool:
        for node in self.nodes:
            if node.cell in obj.get_around():
                return True
        return False

    def merge_into(self, other: Network) -> None:
        for node in other.nodes:
            node.networks[self.__class__] = self
            self.nodes.append(node)
        other.nodes.clear()
        self.w.remove_network(other)