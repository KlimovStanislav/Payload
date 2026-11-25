from __future__ import annotations
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from base.functions import safe_class
from base.folders import settings, localization
from base.font import Font

from ui.Widgets import Labels, Buttons, Sliders

from base.MusicPlayer import MusicPlayer
from base.functions import safe_class
from base.folders import folder, mainfolder, localization

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from SandboxWindow import SandboxWindow

branchs:dict = mainfolder.read("branch_config.json", type="json")

from ui.Menu import Menu

class VariousComponent(QtWidgets.QWidget):
    def __init__(self, main_window:SandboxWindow):
        self.main_window = main_window
        super().__init__()
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

    def reposition(self):
        ...

class MarketComponent(QtWidgets.QWidget):
    def __init__(self, main_window:SandboxWindow):
        self.main_window = main_window
        super().__init__()
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

    def reposition(self):
        ...

@safe_class
class TechTreeComponent(QtWidgets.QWidget):
    def __init__(self, opened_branches: list, main_window:SandboxWindow):
        super().__init__()
        self.opened_branches = opened_branches
        self.main_window = main_window
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        self.title_label = Labels.Body(localization["menu-general-techtree"])
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(16)
        font.setBold(True)
        self.title_label.setFont(font)
        self.main_layout.addWidget(self.title_label)
        
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        
        self.content = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setSpacing(10)

        self.btns:list[QtWidgets.QPushButton] = []
        
        self.scroll.setWidget(self.content)
        self.main_layout.addWidget(self.scroll)
        
        self.refresh()

    def reposition(self):
        self.refresh()

    def refresh(self):
        for btn in self.btns:
            btn.deleteLater()

        self.btns = []
        
        coef = folder.config["craft_coef"]
        
        for name, value in branchs.items():
            cost_lines = [f"{item.capitalize()}: {int(count * coef)}" for item, count in value["cost"].items()]
            text = f"{localization[f'branchs-{name}']}\n" + "\n".join(cost_lines)
            
            btn = Buttons.Secondary()
            btn.setFixedHeight(150)

            self.btns.append(btn)
            
            if name in self.opened_branches:
                btn.setEnabled(False)
                btn.setText(f"{text}\n[ОТКРЫТО]")
            else:
                btn.setText(text)
                btn.clicked.connect(lambda *args, i=[name, value, btn]: self._try_unlock(*i))
            
            self.content_layout.addWidget(btn)
        
        self.content_layout.addStretch()

    def _try_unlock(self, name, data:dict, btn:QtWidgets.QPushButton):
        coef = folder.config["craft_coef"]
        cost = data["cost"]
        
        inv_dict = self.main_window.manager.current.operator.inventory.dict()
        for item, count in cost.items():
            required = int(count * coef)
            if inv_dict.get(item, 0) < required:
                MusicPlayer.play("error-1")
                return
        
        for item, count in cost.items():
            required = int(count * coef)
            self.main_window.manager.current.operator.inventory.reduce(item, required)
        
        if name not in self.opened_branches:
            self.opened_branches.append(name)
        
        btn.setEnabled(False)
        btn.setText(btn.text() + f'\n<{localization["menu-general-opened"]}>')

@safe_class
class DatapadMenu(Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        title = Labels.Title(localization["menu-general-datapad"])

        self.various = VariousComponent(self.Window)
        self.market = MarketComponent(self.Window)
        self.techtree = TechTreeComponent([], self.Window)

        layout.addWidget(title)

        self.tabs = QtWidgets.QTabWidget()

        self.tabs.addTab(self.various, localization["menu-general-various"])
        self.tabs.addTab(self.market, localization["menu-general-market"])
        self.tabs.addTab(self.techtree, localization["menu-general-techtree"])

        layout.addWidget(self.tabs)

        self.reposition()
        self.setFixedSize(800, 600)

    def reposition(self):
        super().reposition()
        self.tabs.currentWidget().reposition()
