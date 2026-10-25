from __future__ import annotations

from PyQt6 import QtWidgets
from dataclasses import dataclass

from base.MusicPlayer import MusicPlayer
from components.Storable import Storable

from base.functions import safe_class

from ui.SandboxWindow import SandboxWindow

from ui.Widgets import Labels

from composites.Drill import Drill

from PyQt6 import QtWidgets, QtCore
from base.folders import folder
import time

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from MainWindow import MainWindow

def training_1(w:CampaignWindow) -> bool:
    for block in w.manager.current.blocks:
        if isinstance(block, Drill):
            return True
    return False

def training_2(w:CampaignWindow) -> bool:
    if "lead" in w.manager.current.operator.inventory.dict():
        return True
    return False

def training_3(w:CampaignWindow) -> bool:
    if w.manager.current.exported.dict().get("lead", 0) >= 30:
        w.manager.current.exported.reduce("lead", 30)
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

        self.setFixedSize(QtCore.QSize(300, 200))
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
                      Step("Training(step 1)", "Place Drill on the lead-ore vein", training_1),
                      Step("Training(step 2)", "Turn on Drill and put lead-ore\nin Operator inventory", training_2),
                      Step("Training(step 3)", "Create a Launch Pad and launch\nyour first rocket with 30 lead", training_3),
                      Step("No tasks more", "Empty", lambda w: False)
                      ]
        
        self.active=folder.config.get("campaign_step", 0)
        self.viewer.refresh(self.steps[self.active])

    def update(self):
        if (step:=self.steps[self.active])(self.window):
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
        self.last_time = time.time()
        self.manager.switch_to("__CAMPAIGN__")
        self.main_window.widget.setCurrentIndex(5)
        self.version_viewer.reposition()
        self.resource_panel.reposition()
        self.campaign.viewer.reposition()
        self.timer.start()
        MusicPlayer.start()
