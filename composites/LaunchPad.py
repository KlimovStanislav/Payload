from __future__ import annotations
from typing import Callable

from composites.Block import Block

from components.Updatable import Updatable
from components.Storable import Storable
from components.Clickable import Clickable
from components.Removable import Removable
from components.Switchable import Switchable
from components.Temperaturable import Temperaturable

from ui.Widgets import Labels, Widget, Buttons, AutoUI
from ui.Menu import Menu
from PyQt6 import QtWidgets

from ui.Widgets import AutoUI

class Launchable:
    def __init__(self, owner:LaunchPad):
        self.owner = owner

    def ui(self):
        class w(AutoUI.Component):
            def __init__(self, obj:Launchable):
                super().__init__(obj)
                self.obj = obj

                self.btn = Buttons.Danger("Launch")
                self.btn.clicked.connect(lambda *args: self.obj.owner.clicked())
                self.btn.setEnabled(False)

                layout = QtWidgets.QVBoxLayout(self)  
                layout.addWidget(self.btn)

            def refresh(self):
                if self.obj.owner.components[Storable].dict() == {}:
                    self.btn.setEnabled(False)
                else:
                    self.btn.setEnabled(True)

        return w(self)

class LaunchPad(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.components[Storable] = Storable(self, None, 100)
        self.components[Clickable] = Clickable(self, lambda obj: AutoUI(obj).Show())
        self.components[Removable] = Removable(self, Storable.remove)

        self.components[Launchable] = Launchable(self)

    def clicked(self):
        for name, value in self.components[Storable].storage.items():
            self.w.exported.add(name, value)
        self.components[Storable].clear()
