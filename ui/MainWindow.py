from __future__ import annotations

from PyQt6 import QtWidgets
from PyQt6.QtGui import QPixmap, QIcon, QShortcut, QKeySequence, QPainter, QColor
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget

import webbrowser

from ui.Widgets import Labels, Buttons

from terminal import init

from base.functions import get_texture, safe_class, TEXTURE_CACHE
from base.MusicPlayer import MusicPlayer
from base.cursors import Cursor
from base import composites
from base import components
from base.folders import folder, saves, settings, block_config, unit_config

from ui.SandboxWindow import SandboxWindow
from ui.EditorWindow import EditorWindow
from ui.CampaignWindow import CampaignWindow

from ui.Widgets import Labels, Buttons

GITHUB_PATH = "https://github.com/KlimovStanislav/Payload"

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
        title = Labels.Title("Choice sector")
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
        
        btn_back = Buttons.Secondary("Back")
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
            
    def show(self):
        self.MainWindow.widget.setCurrentIndex(4)

@safe_class
class MenuWindow(QWidget):
    def __init__(self, window:MainWindow):
        super().__init__(window)

        self.MainWindow = window

        self.setCursor(Cursor.Cursor)

        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)

        left_panel = QtWidgets.QVBoxLayout()
        left_panel.setSpacing(10)

        left_panel.addStretch()
        
        title = Labels.Title("Payload")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(title)

        btn_campaign = Buttons.Primary("Campaign")
        btn_sandbox = Buttons.Primary("Sandbox")
        btn_settings = Buttons.Secondary("Settings")
        btn_exit = Buttons.Secondary("Exit")
        btn_editor = Buttons.Secondary("Editor")
        btn_github = Buttons.Secondary("GitHub")
        
        for btn in [btn_campaign, btn_sandbox, btn_settings, btn_editor, btn_github, btn_exit]:
            btn.setFixedSize(300, 80)
            left_panel.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        left_panel.addStretch()  

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setFixedWidth(500)
        
        image_label = QtWidgets.QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(image_label)  
        
        btn_sandbox.clicked.connect(lambda *args: self.MainWindow.SectorChoiceWindow.show(self.MainWindow.SandboxWindow))
        btn_campaign.clicked.connect(lambda *args: self.MainWindow.CampaignWindow.show())
        btn_editor.clicked.connect(lambda *args: self.MainWindow.SectorChoiceWindow.show(self.MainWindow.EditorWindow))
        btn_github.clicked.connect(lambda *args: webbrowser.open(GITHUB_PATH))

        btn_settings.clicked.connect(lambda: self.MainWindow.SettingsWindow.show())
        btn_exit.clicked.connect(self.MainWindow.close)

        self._bg = QPixmap("bg.png")

    def paintEvent(self, ev):
        if not self._bg.isNull():
            scaled = self._bg.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            painter = QPainter(self)
            painter.drawPixmap(-x, -y, scaled)
        else:
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor("#1e1e1e"))

    def play(self):
        MusicPlayer.play("click_2")
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

        self.terminal = init(self, lambda cmd: self.parsing(cmd))
        self.terminal("Enter <help> to get assistance and information")

        QShortcut(QKeySequence("F11"), self).activated.connect(lambda: self.switch_fullscreen())

    def switch_fullscreen(self):
        if self.fullscreen:
            self.showMaximized()
            self.fullscreen = False
        else:
            self.showFullScreen() 
            self.fullscreen = True
        settings.set("fullscreen", self.fullscreen)
        return self.fullscreen

    def parsing(self, cmd:str):
        match cmd.lower().split():
            case ["help"]:
                self.terminal("view = view game folder\nrefresh - refresh game cache\ncurrent status - print info about current world\ncurrent pause - pause the world\ncurrent resume - resume the world\ncurrent tick <n> - tick n-times\ncurrent give <material> <n> - give operator n material\ncurrent quota <n> - set step of quota to n")

            case ["view"]:
                folder.view()

            case ["refresh"]:
                global TEXTURE_CACHE
                TEXTURE_CACHE = {}
                block_config.load()
                unit_config.load()
                settings.load()

                composites.refresh()

                window:SandboxWindow|CampaignWindow = self.widget.currentWidget()
                if window in [self.SandboxWindow, self.CampaignWindow]:
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
        self.widget.currentWidget().resizeEvent(event)

    def closeEvent(self, a0):
        self.widget.currentWidget().closeEvent(a0)
        folder.log._log_exit()
        a0.accept()