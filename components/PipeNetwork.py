from __future__ import annotations

from components.Network import Network
from components.Liquidable import Liquidable, State

from components.SceneObject import SceneObject, Cell

import math

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.World import World

class PipeNetwork(Network):
    PRESSURE_TARGET_RATE: float = 3.0    
    PRESSURE_DIFFUSE_RATE: float = 3.0  
    FLUID_RATE: float = 1.0
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

    # ---------- уникальные рёбра между пассивными узлами ----------
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

        edges = list(self._liquid_edges())

        # ---- 1a. Подтягиваем давление к fill-based у ВСЕХ узлов ----
        k_t = 1.0 - math.exp(-self.PRESSURE_TARGET_RATE * dt)
        for n in liquid_nodes:
            l = n.components[Liquidable]
            l.pressure += k_t * (l.target_pressure - l.pressure)

        # ---- 1b. Диффузия давления по ВСЕМ рёбрам ----
        k_d = 1.0 - math.exp(-self.PRESSURE_DIFFUSE_RATE * dt)
        deltas = {id(n.components[Liquidable]): 0.0 for n in liquid_nodes}
        for a, b in edges:
            la = a.components[Liquidable]
            lb = b.components[Liquidable]
            ca, cb = la.capacity, lb.capacity
            total = ca + cb
            if total <= self.EPS:
                continue
            # симметричный обмен с сохранением P*C
            dPa = k_d * (lb.pressure - la.pressure) * (cb / total)
            dPb = k_d * (la.pressure - lb.pressure) * (ca / total)
            deltas[id(la)] += dPa
            deltas[id(lb)] += dPb
        for n in liquid_nodes:
            l = n.components[Liquidable]
            l.pressure = max(0.0, l.pressure + deltas[id(l)])

        # ---- 2. Перенос массы по градиенту давления ----
        k_f = 1.0 - math.exp(-self.FLUID_RATE * dt)
        flows = []
        for a, b in edges:
            la = a.components[Liquidable]
            lb = b.components[Liquidable]
            dp = la.pressure - lb.pressure
            if abs(dp) <= self.EPS:
                continue
            if dp > 0.0:
                src, dst = la, lb
            else:
                src, dst = lb, la
                dp = -dp
            src_vol = src.volume
            if src_vol <= self.EPS:
                continue
            flow_frac = max(0.0, min(1.0, k_f * self.FLUID_CONDUCTIVITY * dp))
            amount = min(flow_frac * src_vol, dst.free_space, src_vol)
            if amount <= self.EPS:
                continue
            flows.append((src, dst, amount))

        for src, dst, amount in flows:
            src_vol = src.volume
            if src_vol <= self.EPS:
                continue
            amount = min(amount, src_vol, dst.free_space)
            if amount <= self.EPS:
                continue
            frac = amount / src_vol
            for name, val in list(src.fluids.items()):
                moved = val * frac
                src.fluids[name] = max(0.0, val - moved)
                dst.fluids[name] = dst.fluids.get(name, 0.0) + moved
            for name in [k for k, v in src.fluids.items() if v <= self.EPS]:
                del src.fluids[name]