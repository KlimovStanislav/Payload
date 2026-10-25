from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from base.functions import safe_class
from base.folders import settings

from ui.Widgets import Labels, Buttons, Sliders

from ui.Menu import Menu

@safe_class
class SettingsMenu(Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        title = Labels.Title("Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.fullscreen_check = Buttons.Toggle("Fullscreen")
        self.fullscreen_check.clicked.connect(lambda *args: self.check())

        self.music_check = Buttons.Toggle("Music")

        volume_label = Labels.Body("Volume:")
        self.volume_slider = Sliders.Horizontal()
        self.volume_slider.setRange(0, 100)

        music_volume_label = Labels.Body("Music Volume:")
        self.music_volume_slider = Sliders.Horizontal()
        self.music_volume_slider.setRange(0, 100)

        fps_label = Labels.Body("FPS:")
        self.fps_slider = Sliders.Horizontal()
        self.fps_slider.setRange(1, 240)
        
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

        self.reposition()
        self.setFixedSize(300, 400)

    def check(self):
        if self.Window.main_window.fullscreen:
            self.Window.main_window.showMaximized()
            self.Window.main_window.fullscreen = False
            settings.set("fullscreen", False)
            self.fullscreen_check.setCheckState(Qt.CheckState.Unchecked)
        else:
            self.Window.main_window.showFullScreen() 
            self.Window.main_window.fullscreen = True
            settings.set("fullscreen", True)
            self.fullscreen_check.setCheckState(Qt.CheckState.Checked)
        self.Window.resizeEvent(None)

    def reposition(self):
        super().reposition()
        self.fullscreen_check.setCheckState(Qt.CheckState.Checked if self.Window.main_window.fullscreen else Qt.CheckState.Unchecked)
        self.music_check.setChecked(settings.get("music"))
        self.volume_slider.setValue(settings.get("volume"))
        self.fps_slider.setValue(settings.get("fps"))
        self.music_volume_slider.setValue(settings.get("music_volume"))

    def save_settings(self):
        settings.update({"volume": self.volume_slider.value(), "music_volume": self.music_volume_slider.value(), "music": self.music_check.isChecked(), "fps": self.fps_slider.value()})
        settings.save()
