from __future__ import annotations

from components.Network import Network
from components.Liquidable import Liquidable, State

from components.SceneObject import SceneObject, Cell

import math

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.World import World

class PipeNetwork(Network):
    PRESSURE_TARGET_RATE: float = 1   
    PRESSURE_DIFFUSE_RATE: float = 5
    FLUID_CONDUCTIVITY: float = 0.5
    EPS: float = 1e-9

    @staticmethod
    def _delta(a, b) -> Cell:
        ax, ay = a.cell
        bx, by = b.cell
        return Cell(bx - ax, by - ay)

    def _connected(self, a: SceneObject, b: SceneObject) -> bool:
        return (self._delta(a, b) in a.components[Liquidable].opens and
                self._delta(b, a) in b.components[Liquidable].opens)

    def _linked(self, node: SceneObject, cell_map):
        nx, ny = node.cell
        for dx, dy in node.components[Liquidable].opens:
            other = cell_map.get(Cell(nx + dx, ny + dy))
            if other is not None and self._connected(node, other):
                yield other

    def _liquid_edges(self):
        cell_map = {n.cell: n for n in self.nodes}
        seen = set()
        for n in self.nodes:
            ln = n.components.get(Liquidable)
            if ln is None or ln.type != State.PASSIVE:
                continue
            for nb in self._linked(n, cell_map):
                lnb = nb.components.get(Liquidable)
                if lnb is None or lnb.type != State.PASSIVE:
                    continue
                key = (min(n.cell, nb.cell), max(n.cell, nb.cell))
                if key in seen:
                    continue
                seen.add(key)
                yield n, nb

    def update(self, dt: float):
        liquid_nodes = [n for n in self.nodes if Liquidable in n.components]
        if not liquid_nodes:
            return

        cell_map = {n.cell: n for n in self.nodes}
        edges = list(self._liquid_edges())

        # 1. Считаем общее давление для каждого кластера (для UI и насосов)
        # (тот же BFS, что и выше)
        # ...
        
        # 2. Поток жидкости по разнице объемов (а не давлений)
        # Это гарантирует, что жидкость будет плавно перетекать 
        # оттуда, где её много, туда, где её мало.
        
        FLOW_SPEED = 2.0  # Скорость перетекания (литров в секунду на разницу объемов)
        
        flows = []
        for a, b in edges:
            la = a.components[Liquidable]
            lb = b.components[Liquidable]
            
            # Разница объемов (не давлений!)
            vol_diff = la.volume - lb.volume
            
            if abs(vol_diff) <= 1e-9:
                continue
                
            if vol_diff > 0:
                src, dst = la, lb
            else:
                src, dst = lb, la
                vol_diff = -vol_diff
                
            # Сколько перетечет за этот тик?
            amount = vol_diff * FLOW_SPEED * dt
            
            # Ограничиваем тем, что есть, и свободным местом
            amount = min(amount, src.volume, dst.free_space)
            
            if amount > 1e-9:
                flows.append((src, dst, amount))
                
        # 3. Применяем потоки
        for src, dst, amount in flows:
            actual_amount = min(amount, src.volume, dst.free_space)
            if actual_amount <= 1e-9:
                continue
                
            frac = actual_amount / src.volume
            for name, val in list(src.fluids.items()):
                moved = val * frac
                src.fluids[name] = max(0.0, val - moved)
                dst.fluids[name] = dst.fluids.get(name, 0.0) + moved
                
            for name in [k for k, v in src.fluids.items() if v <= 1e-9]:
                del src.fluids[name]