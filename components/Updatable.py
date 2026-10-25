from __future__ import annotations
import traceback, applib

from typing import Callable, TYPE_CHECKING

from base.functions import safe_class

if TYPE_CHECKING:
    from components.SceneObject import SceneObject

from dataclasses import dataclass
import inspect

@dataclass(slots=True)
class Task:
    ms:int
    func:Callable
    n_args:int
    progress:float=0

@safe_class
class Updatable:
    def __init__(self, owner:SceneObject, tasks:list[tuple[int, Callable]]):
        self.owner = owner
        self.tasks:list[Task] = []
        for task in tasks:
            self.every(task[0], task[1])

    def every(self, ms:int, func:Callable):
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        n_args = sum(1 for p in params if p.default is inspect.Parameter.empty)
        task = Task(ms, func, n_args)
        self.tasks.append(task)
        return task

    def __call__(self, dt):
        if self.owner.exists is False:
            return
        for task in self.tasks:
            task.progress += dt
            while task.progress >= task.ms:
                task.progress -= task.ms
                if task.n_args == 2:
                        task.func(self.owner, task)
                elif task.n_args == 3:
                        task.func(self.owner, task, dt) 
                elif task.n_args == 1:
                        task.func(self.owner)
                else:
                    print(task.n_args)