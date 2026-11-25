from __future__ import annotations

from PyQt6 import QtWidgets
from PyQt6.QtGui import QPixmap, QIcon, QShortcut, QKeySequence, QPainter, QColor, QCursor
from PyQt6.QtCore import Qt, QSize, QTimer, QPointF
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget

import os, webbrowser
from datetime import datetime
from ui.Widgets import Labels, Buttons
from terminal import init

from base.functions import get_texture, safe_class, onerror, TEXTURE_CACHE
from base.MusicPlayer import MusicPlayer
from base.cursors import Cursor
from base.OnlineGetter import OnlineGetter, Release
from base import composites
from base.folders import folder, saves, settings, block_config, unit_config, localization

from ui.SandboxWindow import SandboxWindow
from ui.EditorWindow import EditorWindow
from ui.CampaignWindow import CampaignWindow

from ui.Widgets import Labels, Buttons

class NotificationViewer(QtWidgets.QFrame):
    def __init__(self, window):
        super().__init__(window)

        layout = QtWidgets.QHBoxLayout(self)
        self.label = Labels.Body()
        self.btn = Buttons.Primary("OK")

        self.btn.clicked.connect(lambda: [self.hide(), self.label.setText("")])

        layout.addWidget(self.btn)
        layout.addWidget(self.label)

        self.setProperty("role", "NotificationViewer") 

        self.hide()

    def __call__(self, t:str):
        self.label.setText(t)

        self.label.adjustSize()
        self.btn.adjustSize()
        self.adjustSize()

        self.reposition()
        self.show()

    def reposition(self):
        if self.parent():
            x = (self.parent().width() - self.width()) - 10
            y = self.parent().height() - self.height() - 10
            self.move(x, y)

@safe_class
class SectorChoiceWindow(QWidget):
    def __init__(self, window:MainWindow):
        super().__init__(window)

        self.MainWindow = window
        self.setCursor(Cursor.Cursor)

        layout = QtWidgets.QVBoxLayout(self)

        self.hide()

    @staticmethod
    def clear_layout(layout:QtWidgets.QVBoxLayout):
        if layout is None:
            return
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    SectorChoiceWindow.clear_layout(child_layout)

    def update_layout(self, window:SandboxWindow):
        title = Labels.Title(localization["menu-label-sectorchoice"])
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout:QtWidgets.QVBoxLayout = self.layout()

        SectorChoiceWindow.clear_layout(layout)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(5)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)

        layout.addWidget(self.scroll)

        self.content = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content)
        
        self.scroll.setWidget(self.content)
        
        for save_name in saves.list():
            if save_name.startswith("__"):
                continue
            save = saves.mkdir(save_name)
            btn = Buttons.Icon()
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setProperty("role", "secondary")
            btn.setText(save_name.replace("_", " ".title())) 
            btn.setIcon(QIcon(QPixmap(save.path("ViewMap.png"))))
            btn.setIconSize(QSize(256, 256))
    
            btn.clicked.connect(lambda a=None, w=window, name=save_name: [w.manager.switch_to(name), w.show()])
        
            self.content_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(10)
        
        btn_back = Buttons.Secondary(localization["menu-btn-back"])
        layout.addWidget(btn_back)
        btn_back.clicked.connect(lambda: self.MainWindow.MenuWindow.show())
        
        layout.addStretch()

    def show(self, window:SandboxWindow):
        if len(saves.list()) == 0:
            window.show()
            return

        self.MainWindow.widget.setCurrentIndex(3)
        self.update_layout(window)

@safe_class
class SettingsWindow(QWidget):
    def __init__(self, window:MainWindow, *args, **kwargs):
            self.MainWindow = window
            super().__init__(window, *args, **kwargs)

            layout = QtWidgets.QVBoxLayout(self)
            self.btn_exit = Buttons.Secondary(localization["menu-btn-exit"])
            self.btn_exit.clicked.connect(lambda: self.MainWindow.MenuWindow.show())

            layout.addStretch()
            layout.addWidget(Labels.Body(localization["various-nothing"]), alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.btn_exit)
            layout.addStretch()
            
    def show(self):
        self.MainWindow.widget.setCurrentIndex(4)

@safe_class
class PlayViewer(QtWidgets.QFrame):
    def __init__(self, window:MenuWindow, mainwindow:MainWindow):
        super().__init__(window)
        self.MainWindow = mainwindow

        self.setProperty("role", "PlayViewer") 

        layout = QtWidgets.QVBoxLayout(self)
        layout.addStretch()

        title = Labels.Title("Payload")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        btn_campaign = Buttons.Primary(localization["menu-btn-campaign"])
        btn_sandbox = Buttons.Primary(localization["menu-btn-sandbox"])
        btn_settings = Buttons.Secondary(localization["menu-general-settings"])
        btn_exit = Buttons.Secondary(localization["menu-btn-exit"])
        btn_editor = Buttons.Secondary(localization["menu-btn-editor"])
        btn_github = Buttons.Secondary(localization["menu-btn-github"])
                
        for btn in [btn_campaign, btn_sandbox, btn_settings, btn_editor, btn_github, btn_exit]:
            btn.setFixedSize(300, 80)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        btn_sandbox.clicked.connect(lambda *args: self.MainWindow.SectorChoiceWindow.show(self.MainWindow.SandboxWindow))
        btn_campaign.clicked.connect(lambda *args: self.MainWindow.CampaignWindow.show())
        btn_editor.clicked.connect(lambda *args: self.MainWindow.SectorChoiceWindow.show(self.MainWindow.EditorWindow))
        btn_github.clicked.connect(lambda *args: OnlineGetter.open())
        btn_settings.clicked.connect(lambda: self.MainWindow.SettingsWindow.show())
        btn_exit.clicked.connect(self.MainWindow.close)

        self.setFixedWidth(450)

@safe_class
class ReleaseViewer(QtWidgets.QFrame):
    __cache__:list[Release] = []
    def __init__(self, window:MenuWindow, mainwindow:MainWindow):
        super().__init__(window)
        self.MainWindow = mainwindow

        self.setProperty("role", "ReleaseViewer")

        self.state_label = Labels.Subtitle()

        layout = QtWidgets.QVBoxLayout(self)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)

        self.content = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                
        scroll.setWidget(self.content)

        layout.addWidget(Labels.Title("Releases"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(scroll, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.state_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btns:list[QtWidgets.QPushButton] = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(16)

        scroll.setFixedSize(700, 300)
        self.setFixedSize(900, 400)

    def refresh(self):
        if OnlineGetter.releases != ReleaseViewer.__cache__:
            self.timer.setInterval(60000)
            ReleaseViewer.__cache__ = OnlineGetter.releases.copy()

        for btn in self.btns:
            btn.deleteLater()

        self.btns = []

        if not ReleaseViewer.__cache__:
            self.state_label.setText("No Ethernet Connection")
            return

        version = datetime.strptime(folder.version[6:], r"%d.%m.%Y")
        if version < ReleaseViewer.__cache__[0].date:
            self.state_label.setText("Update available")
        else:
            self.state_label.setText("Latest version")

        for release in ReleaseViewer.__cache__:
            btn = Buttons.Secondary(f"{release.date.strftime(r"%d.%m.%Y")}:\n{release.text}")
            btn.clicked.connect(lambda *args, r=release: OnlineGetter.open(r))
            self.btns.append(btn)
            self.content_layout.addWidget(btn)

@safe_class
class MenuWindow(QWidget):
    def __init__(self, window:MainWindow):
        super().__init__(window)

        self.MainWindow = window
        self.setCursor(Cursor.Cursor)

        layout = QtWidgets.QHBoxLayout(self)

        self.play_viewer = PlayViewer(self, self.MainWindow)
        self.release_viewer = ReleaseViewer(self, self.MainWindow)

        layout.addWidget(self.play_viewer) 
        layout.addWidget(self.release_viewer, alignment=Qt.AlignmentFlag.AlignCenter)

        self.bg = QPixmap("bg.png")

        if self.bg.isNull():
            folder.log.write("Background <bg.png> not founded at game folder", type="MenuWindow", set_error=True)

        self.current_offset = QPointF(0, 0)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_parallax)
        self.timer.start(int(1000/settings.get("fps")))

    def update_parallax(self):
        pos = self.mapFromGlobal(QCursor.pos())
        
        x = self.width() / 2
        y = self.height() / 2
        nx = (pos.x()-x)/x
        ny = (pos.y()-y)/y
        
        nx = max(-1.0, min(1.0, nx))
        ny = max(-1.0, min(1.0, ny))

        target_x = -nx*30
        target_y = -ny*30

        self.current_offset.setX(self.current_offset.x() + (target_x - self.current_offset.x())*0.1)
        self.current_offset.setY(self.current_offset.y() + (target_y - self.current_offset.y())*0.1)

        self.update()

    def paintEvent(self, ev):
        painter = QPainter(self)
        
        if not self.bg.isNull():
            scaled = self.bg.scaled(self.width()+60, self.height()+60, Qt.AspectRatioMode.KeepAspectRatioByExpanding,  Qt.TransformationMode.SmoothTransformation)
            
            x = (scaled.width() - self.width()) //2 
            y = (scaled.height() - self.height()) // 2
            
            x += int(self.current_offset.x())
            y += int(self.current_offset.y())
            
            painter.drawPixmap(-x, -y, scaled)
        else:
            painter.fillRect(self.rect(), QColor("#1e1e1e"))

    def play(self):
        MusicPlayer.play("click-2")
        self.MainWindow.SandboxWindow.show()

    def show(self):
        self.MainWindow.widget.setCurrentIndex(0)

@safe_class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fullscreen = settings.get("fullscreen")

        self.setWindowTitle("Payload")
        self.setWindowIcon(QIcon(get_texture("icon")))
        self.setCursor(Cursor.Cursor)

        self.widget = QStackedWidget()
        self.setCentralWidget(self.widget)

        self.SandboxWindow = SandboxWindow(self)
        self.MenuWindow = MenuWindow(self)
        self.EditorWindow = EditorWindow(self)
        self.SectorChoiceWindow = SectorChoiceWindow(self)
        self.SettingsWindow =  SettingsWindow(self)
        self.CampaignWindow = CampaignWindow(self)

        self.widget.addWidget(self.MenuWindow)
        self.widget.addWidget(self.SandboxWindow)
        self.widget.addWidget(self.EditorWindow)
        self.widget.addWidget(self.SectorChoiceWindow)
        self.widget.addWidget(self.SettingsWindow)
        self.widget.addWidget(self.CampaignWindow)

        self.notification = NotificationViewer(self)

        self.terminal = init(self, lambda cmd: self.parsing(cmd))
        self.terminal("Enter <help> to get assistance and information")

        QShortcut(QKeySequence("F11"), self).activated.connect(lambda: self.switch_fullscreen())
        QShortcut(QKeySequence("F4"), self).activated.connect(lambda: self.parsing("refresh"))
        QShortcut(QKeySequence("F3"), self).activated.connect(lambda: self.parsing("view"))
        QShortcut(QKeySequence("Shift+F1"), self).activated.connect(lambda: self.parsing("break"))

        onerror.functions.add(self.error)

    def error(self, str:str):
        self.notification(f"ERROR: {str}")

    def switch_fullscreen(self):
        if self.fullscreen:
            self.showMaximized()
            self.fullscreen = False
        else:
            self.showFullScreen() 
            self.fullscreen = True
        settings.set("fullscreen", self.fullscreen)
        return self.fullscreen

    def focusNextPrevChild(self, *a):
        return False

    def parsing(self, cmd:str):
        match cmd.lower().split():
            case ["help"]:
                self.terminal("view = view game folder\nrefresh - refresh game cache\ncurrent status - print info about current world\ncurrent pause - pause the world\ncurrent resume - resume the world\ncurrent tick <n> - tick n-times\ncurrent give <material> <n> - give operator n material\ncurrent quota <n> - set step of quota to n")

            case ["view"]:
                folder.view()

            case ["break"]:
                try:
                    folder.log.write("Forced closure of the application")
                finally:
                    os._exit(2)

            case ["refresh"]:
                global TEXTURE_CACHE
                TEXTURE_CACHE = {}
                block_config.load()
                unit_config.load()
                settings.load()

                composites.refresh()

                window:SandboxWindow|CampaignWindow = self.widget.currentWidget()
                if window in [self.SandboxWindow, self.CampaignWindow, self.EditorWindow]:
                    window.close()
                    window.show()
                    window.update_tool_panel()
                self.terminal("refreshed")

            case ["current", *args]:
                if not args:
                    self.terminal("what")
                window:SandboxWindow|CampaignWindow = self.widget.currentWidget()
                if window not in [self.SandboxWindow, self.CampaignWindow]:
                    self.terminal("not a chance")
                    return
                match args:
                    case ["status"]:
                        self.terminal(repr(window.manager.current))

                    case ["pause"]:
                        window.timer.stop()
                        self.terminal("paused")

                    case ["resume"]:
                        window.timer.start()
                        self.terminal("resumed")

                    case ["tick", num]:
                        if not num.isnumeric():
                            self.terminal("not a chance")
                            return
                        window.manager.current.update(int(num))
                        self.terminal(f"played {num} ticks")

                    case ["give", name, value]:
                        if not value.isnumeric():
                            self.terminal("not a chance")
                            return
                        window.manager.current.operator.inventory.add(name, int(value))
                        self.terminal(f"gived to operator {value} of {name}")

                    case ["quota", num]:
                        if window != self.CampaignWindow or not num.isnumeric(): 
                            self.terminal("not a chance")
                            return
                        window.campaign.active = int(num)
                        self.terminal(f"quota changed to {num}")
            case _:
                self.terminal(f"cmd <{cmd}> not found")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.notification.reposition()
        self.widget.currentWidget().resizeEvent(event)

    def closeEvent(self, a0):
        self.widget.currentWidget().closeEvent(a0)
        folder.log._log_exit()
        a0.accept()