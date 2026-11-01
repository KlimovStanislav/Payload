from __future__ import annotations

from dataclasses import dataclass, field

from enum import Enum, auto

from typing import TYPE_CHECKING, TypeVar, Type, NamedTuple
if TYPE_CHECKING:
    from world.World import World

T = TypeVar("T")

class Dict(dict[type, object]):
    def __getitem__(self, key: Type[T]) -> T:
        return super().__getitem__(key) 

    def __setitem__(self, key, value):
        if key != value.__class__:
            raise KeyError("Types of keys and values not match")
        return super().__setitem__(key, value)

class Cell(NamedTuple):
    x:int
    y:int

class Size(NamedTuple):
    w:int
    h:int

class Angle(Enum):
    UP = 0
    RIGHT = 90
    DOWN = 180
    LEFT = 270

    def __call__(cls, value):
        dct = {Angle.UP: 0, Angle.DOWN: 180, Angle.LEFT: 270, Angle.RIGHT: 90}
        return dct[value-((value//360)*360)]

@dataclass
class SceneObject:
    w:World
    cell:Cell
    size:Size
    name:str
    integrity:int|float
    angle:Angle

    components:Dict[Type[T], Type[T]] = field(default_factory=Dict)
    networks:Dict[Type[T], Type[T]] = field(default_factory=Dict)
    exists:bool=True
    
    def get_occupied_cells(self) -> set[Cell]:
        cells = set()
        for dx in range(self.size[0]):
            for dy in range(self.size[1]):
                cells.add(Cell(self.cell.x + dx, self.cell.y + dy))
        return cells

    def get_around(self) -> set[Cell]:
        cells = set()
        for cell in self.get_occupied_cells():
            for coef in ((1, 0), (-1, 0), (0, 1), (0,-1)):
                cells.add(Cell(cell[0]+coef[0], cell[1]+coef[1]))
        return cells 

    def __repr__(self):
        return f"<{type(self).__name__}>"
