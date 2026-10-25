from __future__ import annotations

from dataclasses import dataclass, field

from typing import TYPE_CHECKING, TypeVar, Type, NamedTuple
if TYPE_CHECKING:
    from world.World import World

T = TypeVar("T")

class Dict(dict[type, object]):
    def __getitem__(self, key: Type[T]) -> T:
        return super().__getitem__(key) 

class Cell(NamedTuple):
    x:int
    y:int

class Size(NamedTuple):
    w:int
    h:int

@dataclass
class SceneObject:
    w:World
    cell:Cell
    size:Size
    name:str
    integrity:int|float

    components:Dict[Type[T], Type[T]] = field(default_factory=Dict)
    networks:Dict[Type[T], Type[T]] = field(default=Dict)
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
