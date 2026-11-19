from __future__ import annotations

from PyQt6 import QtWidgets
from dataclasses import dataclass

from base.MusicPlayer import MusicPlayer
from components.Storable import Storable

from ui.SandboxWindow import SandboxWindow

from ui.Widgets import Labels

from PyQt6 import QtWidgets, QtCore
from base.functions import safe_class
from base.folders import folder, localization
from base.composites import composites
import time

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from MainWindow import MainWindow

def training_0(w:CampaignWindow) -> bool:
    if w.manager.current.operator.inventory.dict():
        return True
    return False

def training_1(w:CampaignWindow) -> bool:
    for block in w.manager.current.blocks:
        if isinstance(block, composites["Drill"]):
            for cell in block.get_occupied_cells():
                for i in w.manager.current.block_map.get(cell, []):
                    if i.name in ["ore-titan1", "ore-titan2", "ore-titan3"]:
                        return True
    return False

def training_2(w:CampaignWindow) -> bool:
    if "titan" in w.manager.current.operator.inventory.dict():
        return True
    return False

def training_3(w:CampaignWindow) -> bool:
    if w.manager.current.Base is None:
        return False
    if "titan" in w.manager.current.Base.components[Storable].dict():
        for block in w.manager.current.blocks:
            if isinstance(block, composites["Conveyor"]):
                return True
    return False

def training_4(w:CampaignWindow) -> bool:
    for block in w.manager.current.blocks:
            if isinstance(block, composites["Drill"]):
                for cell in block.get_occupied_cells():
                    for i in w.manager.current.block_map.get(cell, []):
                        if i.name in ["ore-coal1", "ore-coal2", "ore-coal3"]:
                            return True
    return False

def training_5(w:CampaignWindow) -> bool:
    if (count:=w.manager.current.exported.dict().get("titan", 50)) >= 50:
        w.manager.current.exported.reduce("titan", count)
        return True
    return False

def training_6(w:CampaignWindow) -> bool:
    if "pipe" in w.manager.current.opened:
        return True
    return False

@dataclass
class Step:
    title:str
    subtitle:str
    func:Callable
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class CampaignViewer(QtWidgets.QFrame):
    def __init__(self, window):
        super().__init__(window)
        self.setProperty("role", "CampaignViewer") 
        layout = QtWidgets.QVBoxLayout(self)
        self.title = Labels.Title("")
        self.subtitle = Labels.Subtitle("")

        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)

        self.setFixedSize(QtCore.QSize(500, 200))
        self.hide()

    def refresh(self, step:Step):
        self.title.setText(step.title)
        self.subtitle.setText(step.subtitle)

    def reposition(self):
        if self.parent():
            y = self.parent().height()-self.height()-10
            self.move(10, y)
        self.show()

@safe_class
class Campaign:
    def __init__(self, window):
        self.viewer = CampaignViewer(window)
        self.window:CampaignWindow = window             
        self.steps = [
                      Step(f"{localization["various-training"]}({localization["various-step"]} 0)", localization["campaign-training-0"], training_0),
                      Step(f"{localization["various-training"]}({localization["various-step"]} 1)", localization["campaign-training-1"], training_1),
                      Step(f"{localization["various-training"]}({localization["various-step"]} 2)", localization["campaign-training-2"], training_2),
                      Step(f"{localization["various-training"]}({localization["various-step"]} 3)", localization["campaign-training-3"], training_3),
                      Step(f"{localization["various-training"]}({localization["various-step"]} 4)", localization["campaign-training-4"], training_4),
                      Step(f"{localization["various-training"]}({localization["various-step"]} 5)", localization["campaign-training-5"], training_5),
                      Step(f"{localization["various-training"]}({localization["various-step"]} 6)", localization["campaign-training-6"], training_6),
                      Step(localization["campaign-notasksmore"], localization["various-empty"], lambda w: False)
                      ]
        
        self.active:int=folder.config.get("campaign_step", 0)
        self.viewer.refresh(self.steps[self.active])

    def update(self):
        if (step:=self.steps[self.active])(self.window):
            MusicPlayer.play("complete-1")
            self.active+=1
            self.viewer.refresh(self.steps[self.active])

@safe_class
class CampaignWindow(SandboxWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campaign = Campaign(self)

    def closeEvent(self, event):
        folder.config.set("campaign_step", self.campaign.active)
        return super().closeEvent(event)

    def update(self):
        super().update()
        self.campaign.update()

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.campaign.viewer.reposition()

    def show(self):
        self.main_window.widget.currentWidget().close()
        self.last_time = time.time()
        self.manager.switch_to("__CAMPAIGN__")
        self.main_window.widget.setCurrentIndex(5)
        super().reposition()
        self.campaign.viewer.reposition()
        self.timer.start()
        MusicPlayer.play("beep-1")
        MusicPlayer.start()
