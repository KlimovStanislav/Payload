from __future__ import annotations

from PyQt6 import QtWidgets

from typing import TYPE_CHECKING

from base.font import Font
from base.cursors import Cursor
from base.functions import safe_class
from base.MusicPlayer import MusicPlayer

from ui.Widgets import Labels, AutoUI, Buttons

if TYPE_CHECKING:
    from components.SceneObject import SceneObject

@safe_class
class Storable:
    save = ("storage",)
    def __init__(self, owner:SceneObject, storage:dict|None, max_size:int):
        self.owner = owner
        if storage is None:
            storage = {}

        if self.owner.w.scene is not None:
            self.center = self.owner.w.scene.addText("Empty")
            self.center.setPos((self.owner.cell.x+self.owner.size[0]/2)*32-25, (self.owner.cell.x+self.owner.size[1])*32)
            self.center.setZValue(40)
            self.center.setFont(Font.Bold)
            self.center.setOpacity(0)

        self.old_dict = {}

        self.storage = storage
        self.max_size = max_size

    def clear(self):
        self.storage.clear()
        self.old_dict.clear()

    def add(self, item, count):
        if count == 0:
            return True
        
        if item in self.dict():
            self.storage[item] += count
        else:
            self.storage[item] = count
    
        if self.storage[item] > self.max_size: 
            self.storage[item] = self.max_size
            self.upd()
            return False
        self.upd()
        return True
    
    def empty(self):
        if len(self.dict()) == 0:
            return True
        return False
        
    def reduce(self, item, count):
        if item in self.dict():
            self.dict()[item] -= count
        else:
            self.upd()
            return False
            
        if self.dict()[item] < 0: 
            del self.dict()[item]
            self.upd()
            return False
        self.upd()
        return True
    
    def dict(self) -> dict:
        return self.storage
    
    def show(self):
        if len(self.dict()) == 0:
            return "Empty"
            
        ex = ""
    
        for name, value in self.dict().items():
            ex += f"{name}: {value}\n"
    
        return ex[:-1]
        
    def __eq__(self, f:Storable):
        return self.dict() == f.dict()
    
    def __len__(self):
        return len(self.dict())

    def upd(self):
        if self.owner.w.scene is not None:
            if self.old_dict != self.dict():
                self.old_dict = self.dict().copy()
                text = self.show()
                self.center.setPlainText(text)

    def ui(self):
        @safe_class
        class cusbtn(QtWidgets.QWidget):
            def __init__(self, inverted, obj:Storable, name, value, *args, **kwargs):
                self.obj = obj
                self.name = name
                self.inverted = inverted
                super().__init__(*args, **kwargs)

                layout = QtWidgets.QHBoxLayout(self)

                self.label = Labels.Body(f"{name}: {value}")
                layout.addWidget(self.label)

                self.spin = QtWidgets.QSpinBox()
                self.setCursor(Cursor.Ibeam)
                self.spin.lineEdit().setCursor(Cursor.Ibeam)
                self.spin.setFont(Font.Bold)
                self.spin.setRange(1, 9999)
                self.spin.setValue(1)
                layout.addWidget(self.spin)

                self.btn = Buttons.Secondary("→")
                self.btn.clicked.connect(self.on_take)
                layout.addWidget(self.btn)

                self.refresh()

            def on_take(self, *args, **kwargs):
                amount = self.spin.value()
                if not self.inverted:
                    available = self.obj.dict().get(self.name, 0)
                    if available >= amount:
                        self.obj.reduce(self.name, amount)
                        self.obj.owner.w.operator.inventory.add(self.name, amount)
                else:
                    available = self.obj.owner.w.operator.inventory.dict().get(self.name, 0)
                    if available >= amount:
                        self.obj.owner.w.operator.inventory.reduce(self.name, amount)
                        self.obj.add(self.name, amount)

                self.refresh()
            def refresh(self):
                if self.inverted:
                    value = self.obj.owner.w.operator.inventory.dict().get(self.name, 0)
                else:
                    value = self.obj.dict().get(self.name, 0)
                self.label.setText(f"{self.name}: {value}")
                self.spin.setMaximum(max(1, value))

        @safe_class 
        class w(AutoUI.Component):
            def __init__(self, obj:Storable):
                super().__init__(obj)
                self.obj = obj

                root = QtWidgets.QHBoxLayout(self)

                #блок
                self.layout1 = QtWidgets.QVBoxLayout()  
                title = Labels.Title(obj.owner.name.replace("_", " ").title(), centered=True)
                self.layout1.addWidget(title)

                self.btns_block:dict[str, cusbtn] = {}
                for name, value in obj.dict().items():
                    btn = cusbtn(False, obj, name, value)
                    self.layout1.addWidget(btn)
                    self.btns_block[name] = btn
                root.addLayout(self.layout1)

                #игрок
                self.layout2 = QtWidgets.QVBoxLayout()  
                title = Labels.Title(obj.owner.w.operator.name, centered=True)
                self.layout2.addWidget(title)
                
                self.btns_player:dict[str, cusbtn] = {}
                for name, value in obj.dict().items():
                    btn = cusbtn(True, obj, name, value)
                    self.layout2.addWidget(btn)
                    self.btns_player[name] = btn
                root.addLayout(self.layout2)

            def refresh(self):
                for name, value in self.obj.dict().items():
                    if name in self.btns_block:
                        self.btns_block[name].refresh()
                    else:
                        btn = cusbtn(False, self.obj, name, self.obj.dict().get(name, 0))
                        self.layout1.addWidget(btn)
                        self.btns_block[name] = btn

                for name, value in self.obj.owner.w.operator.inventory.dict().items():
                    if name in self.btns_player:
                        self.btns_player[name].refresh()
                    else:
                        btn = cusbtn(True, self.obj, name, self.obj.owner.w.operator.inventory.dict().get(name, 0))
                        self.layout2.addWidget(btn)
                        self.btns_player[name] = btn

        return w(self)

    @staticmethod
    def remove(block:SceneObject):
        if block.w.scene is not None:
            block.w.scene.removeItem(block.components[Storable].center)

    @staticmethod
    def click(block:SceneObject):
        if block.w.scene is not None:
            block.components[Storable].center.setOpacity(1 if block.components[Storable].center.opacity() == 0 else 0)
            MusicPlayer.play("click_1")