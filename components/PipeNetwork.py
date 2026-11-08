from __future__ import annotations

from components.Network import Network
from components.Liquidable import Liquidable, State

from components.SceneObject import SceneObject, Cell

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.World import World

from collections import deque
from enum import Enum

class PipeNetwork(Network):
    # ---------- helpers ----------

    @staticmethod
    def _liq(node) -> Liquidable:
        return node.components[Liquidable]

    @staticmethod
    def _delta(a, b) -> Cell:
        ax, ay = a.cell
        bx, by = b.cell
        return Cell(bx - ax, by - ay)

    def _connected(self, a, b) -> bool:
        # оба открыты друг на друга — с учётом дельт из .opens (список Cell)
        return (self._delta(a, b) in self._liq(a).opens and
                self._delta(b, a) in self._liq(b).opens)

    def _linked(self, node, cell_map):# -> Generator[Any, Any, None]:
        nx, ny = node.cell
        for dx, dy in self._liq(node).opens:
            other = cell_map.get(Cell(nx + dx, ny + dy))
            if other is not None and self._connected(node, other):
                yield other

    # ---------- add / remove ----------

    def add(self, node):
        if node in self.nodes:
            return

        super().add(node)
        self._merge_neighbors(node)

    def _merge_neighbors(self, node):
        for other in self.w.networks:
            if other is self or not isinstance(other, PipeNetwork):
                continue
            if any(self._connected(node, n) for n in other.nodes):
                other.merge_into(self)

    def remove(self, node):
        if node not in self.nodes:
            return
        self.nodes.remove(node)
        node.networks.pop(PipeNetwork, None)

        if not self.nodes:
            self.w.remove_network(self)
            self.exists = False
            return
        self._split()

    def _split(self):
        if len(self.nodes) < 2:
            return
        cell_map = {n.cell: n for n in self.nodes}
        remaining = list(self.nodes)
        components: list[list] = []

        while remaining:
            start = remaining[0]
            comp = [start]
            comp_cells = {start.cell}
            stack = [start]
            while stack:
                cur = stack.pop()
                for nb in self._linked(cur, cell_map):
                    if nb.cell not in comp_cells:
                        comp_cells.add(nb.cell)
                        comp.append(nb)
                        stack.append(nb)
            components.append(comp)
            remaining = [n for n in remaining if n.cell not in comp_cells]

        if len(components) == 1:
            return

        # первая компонента остаётся в self, остальные — в новые сети
        for comp in components[1:]:
            new_net = PipeNetwork(self.w)
            for n in comp:
                self.nodes.remove(n)
                n.networks.pop(PipeNetwork, None)
                new_net.nodes.append(n)
                n.networks[PipeNetwork] = new_net

    # ---------- update ----------

    def update(self, dt):
        # ACTIVE не трогаем — насосы сами разбираются со своим давлением/жидкостью
        passive = [self._liq(n) for n in self.nodes
                   if self._liq(n).type == State.PASSIVE]
        if not passive:
            return

        total_volume = sum(l.volume for l in passive)
        if total_volume <= 0:
            return

        # пул жидкостей по типам
        pool: dict[str, float] = {}
        for l in passive:
            for k, v in l.fluids.items():
                pool[k] = pool.get(k, 0.0) + v

        # раздача пропорционально объёму; fluids мутируем на месте —
        # ui() держит ссылку на dict, не ломаем её
        for l in passive:
            ratio = l.volume / total_volume
            l.fluids.clear()
            l.fluids.update({k: v * ratio for k, v in pool.items()})

        # давление — среднее с весом по объёму
        pressure = sum(l.pressure * l.volume for l in passive) / total_volume
        for l in passive:
            l.pressure = pressure