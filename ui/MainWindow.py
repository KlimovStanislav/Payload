from __future__ import annotations

from PyQt6 import QtWidgets
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget

import webbrowser

from ui.Widgets import Labels, Buttons

from base.functions import get_texture, safe_class
from base.MusicPlayer import MusicPlayer
from base.cursors import Cursor
from base.folders import folder, saves, settings

from ui.SandboxWindow import SandboxWindow
from ui.EditorWindow import EditorWindow
from ui.CampaignWindow import CampaignWindow

from ui.Widgets import Labels, Buttons, Sliders

GITHUB_PATH = "https://github.com/Stanislafv/Low-Level"

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
            
            layout = QtWidgets.QVBoxLayout(self)
            
            title = Labels.Title("Settings")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.fullscreen_check = Buttons.Toggle("Fullscreen")
    
            self.music_check = Buttons.Toggle("Music")
            self.music_check.setChecked(folder.config["music_volume"] == 0)
            
            volume_label = Labels.Body("Volume:")
            self.volume_slider = Sliders.Horizontal()
            self.volume_slider.setRange(0, 100)
            self.volume_slider.setValue(int(folder.config["volume"]*100))
    
            music_volume_label = Labels.Body("Music Volume:")
            self.music_volume_slider = Sliders.Horizontal()
            self.music_volume_slider.setRange(0, 100)
            self.music_volume_slider.setValue(int(folder.config["music_volume"]*100))
    
            fps_label = Labels.Body("FPS:")
            self.fps_slider = Sliders.Horizontal()
            self.fps_slider.setRange(10, 240)
            self.fps_slider.setValue(0)
            
            btn_back = Buttons.Secondary("Back")
            btn_back.clicked.connect(lambda: self.Back())
            
            btn_save = Buttons.Secondary("Save")
            btn_save.clicked.connect(lambda: self.save_settings())
            
            layout.addWidget(title)
            layout.addWidget(self.fullscreen_check)
            layout.addWidget(self.music_check)
            layout.addSpacing(5)
    
            layout.addWidget(volume_label)
            layout.addWidget(self.volume_slider)
            layout.addSpacing(5)
    
            layout.addWidget(music_volume_label)
            layout.addWidget(self.music_volume_slider)
            layout.addSpacing(5)
    
            layout.addWidget(fps_label)
            layout.addWidget(self.fps_slider)
            layout.addSpacing(20)
    
            layout.addWidget(btn_save)
            layout.addWidget(btn_back)
            
            self.setFixedSize(300, 400)
    
    def save_settings(self):
        music_volume = self.music_volume_slider.value()/100 if self.music_check.isChecked() else 0
        folder.config.write({"devmode": folder.config["devmode"], "volume": self.volume_slider.value()/100, "music_volume": music_volume, "craft_coef": folder.config["craft_coef"], "fps": self.fps_slider.value()})

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
        pixmap = QPixmap("bg.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio)
            image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(image_label)  
        
        btn_sandbox.clicked.connect(lambda *args: self.MainWindow.SectorChoiceWindow.show(self.MainWindow.SandboxWindow))
        btn_campaign.clicked.connect(lambda *args: self.MainWindow.CampaignWindow.show())
        btn_editor.clicked.connect(lambda *args: self.MainWindow.SectorChoiceWindow.show(self.MainWindow.EditorWindow))
        btn_github.clicked.connect(lambda *args: webbrowser.open(GITHUB_PATH))

        btn_settings.clicked.connect(lambda: self.MainWindow.SettingsWindow.show())
        btn_exit.clicked.connect(self.MainWindow.close)

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.widget.currentWidget().resizeEvent(event)

    def closeEvent(self, a0):
        self.widget.currentWidget().closeEvent(a0)
        folder.log._log_exit()
        a0.accept()