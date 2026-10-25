from world.World import World
from world.WorldLoader import WorldLoader

from composites.Block import Block
from components.SceneObject import SceneObject, Cell

from enum import Enum, auto

from time import perf_counter

import pyclr, applib, importlib, traceback, sys

from PyQt6.QtWidgets import QApplication
import base.font
import base.cursors
    
application = QApplication(sys.argv)
base.font.__dict__[...] = application
base.cursors.__dict__[...] = application

FULL_TESTS = []
SMOKE_TESTS = []

class Mode(Enum):
    SMOKE = auto()
    FULL = auto()

def full(func):
    FULL_TESTS.append(func)
    return func

def smoke(func):
    SMOKE_TESTS.append(func)
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
    block = Block(world, Cell(128, 128), "air")
    assert block.exists
    block.remove()
    assert not block.exists

def start(mode:Mode) -> list:
    start_time = perf_counter()
    world = World(devmode=True)
    failed = []
    critical = []
    for func in SMOKE_TESTS:
        try:
            func(world)
        except AssertionError as e:
            failed.append(f"{func.__name__.replace("_", " ").title()}: {e}")
        except Exception:
            critical.append(f"{func.__name__.replace("_", " ").title()}: {traceback.format_exc()}")
            break

    if mode is Mode.FULL:
        for func in FULL_TESTS:
            try:
                func(world)
            except AssertionError as e:
                failed.append(f"{func.__name__.replace("_", " ").title()}: {e}")
            except Exception:
                critical.append(f"{func.__name__.replace("_", " ").title()}: {traceback.format_exc()}")
                break

    return failed, critical, (perf_counter()-start_time)*1000

if __name__ == "__main__":
    failed, critical, time = start(Mode.FULL)
    pyclr.cprint(f"Full tests completed in {time:.0f} miliseconds", style=pyclr.Bold)
    if critical:
        pyclr.cprint(f"Found {len(critical)} critical:", *critical, sep="\n---", style=pyclr.Bold, color="red")
        sys.exit(1)
    if failed:
        pyclr.cprint(f"Found {len(failed)} failed tests:", *failed, sep="\n---", style=pyclr.Bold, color="red")
        sys.exit(1)
    else:
        pyclr.cprint("All systems online", style=pyclr.Bold, color="#2aa7f0")
        