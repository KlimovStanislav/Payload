from world.World import World
from world.WorldLoader import WorldLoader

from composites.UseBlock import UseBlock
from components.SceneObject import Cell

from enum import Enum, auto
from dataclasses import dataclass
from time import perf_counter

import applib, importlib, traceback, sys, os

from typing import Callable

from PyQt6.QtWidgets import QApplication
import base.font
from base.functions import safe
import base.cursors

@dataclass
class Test:
    func:Callable
    def __call__(self, *args, **k) -> float:
        st = perf_counter()
        try:
            self.func(*args, **k)
        except Exception as e:
            raise e
        else:
            return (perf_counter()-st)*1000

FULL_TESTS:list[Test] = []
SMOKE_TESTS:list[Test] = []

class Mode(Enum):
    SMOKE = auto()
    FULL = auto()

def full(func):
    FULL_TESTS.append(Test(func))
    return func

def smoke(func):
    SMOKE_TESTS.append(Test(func))
    return func

@full
def test_names(*a):
    def test(path):
        failed = []
        try:
            for module in applib.Storage(path).list():
                if not module.endswith(".py"):
                    continue
                name = module[:-3]
                mod = importlib.import_module(f"{path}.{name}")

                ex = mod.__dict__.get(module[:-3])
                if ex is None:
                    failed.append(f"The module <composites/{module}> lacks a final class")
            return failed
        except Exception as e:
            raise Exception(traceback.format_exc())
        
    failed = []      
    failed.extend(test("composites"))
    failed.extend(test("components"))
    failed.extend(test("ui"))
    failed.extend(test("world"))
    if failed:
        raise AssertionError(("\n---".join(failed)))

@smoke
def test_world(world:World):
    WorldLoader.save(world, "__TEST__")
    WorldLoader.load("__TEST__")
    WorldLoader.remove("__TEST__")

@smoke
def test_world_creates(world:World):
    assert world is not None
    assert world.size[0] > 0
    assert world.size[1] > 0
    assert world.size.h > 0
    assert world.size.w > 0

@smoke
def test_scene_objects(world:World):
    block = UseBlock(world, Cell(world.size.w//2, world.size.h//2), "air")
    assert world.block_map.get(Cell(world.size.w//2, world.size.h//2)) is not None
    assert block.exists
    block.remove()
    assert not block.exists
    assert world.block_map.get(Cell(world.size.w//2, world.size.h//2)) is None

def start(mode:Mode) -> list:
    start_time = perf_counter()
    if mode is Mode.FULL:
        application = QApplication(sys.argv)
        base.font.__dict__[...] = application
        base.cursors.__dict__[...] = application
    world = World(devmode=True, shadows=False)
    times:dict[str, float] = {}
    failed = []
    critical = []
    for func in SMOKE_TESTS:
        try:
            time = func(world)
        except AssertionError as e:
            failed.append(f"{func.func.__name__.replace("_", " ").title()}: {e}")
        except Exception:
            critical.append(f"{func.func.__name__.replace("_", " ").title()}: {traceback.format_exc()}")
            break
        else:
            times[func.func.__name__.replace("_", " ").title()] = time

    if mode is Mode.FULL:
        application = QApplication(sys.argv)
        base.font.__dict__[...] = application
        base.cursors.__dict__[...] = application
        for func in FULL_TESTS:
            try:
                time = func(world)
            except AssertionError as e:
                failed.append(f"{func.func.__name__.replace("_", " ").title()}: {e}")
            except Exception:
                critical.append(f"{func.func.__name__.replace("_", " ").title()}: {traceback.format_exc()}")
                break
            else:
                times[func.func.__name__.replace("_", " ").title()] = time

    critical.extend(safe.errors)

    return dict(sorted(times.items(), key=lambda x:x[1], reverse=True)), failed, critical, (perf_counter()-start_time)*1000

if __name__ == "__main__":
    times, failed, critical, time = start(Mode.FULL)
    print(f"Full tests completed in {time:.0f} miliseconds")
    print(times)
    if critical:
        print(f"Found {len(critical)} critical:", *critical, sep="\n---")
        os._exit(1)
    if failed:
        print(f"Found {len(failed)} failed tests:", *failed, sep="\n---")
        os._exit(1)
    else:
        print("All systems online")
        os._exit(0)
        