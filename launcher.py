from __future__ import annotations

import win32com.client
import os, sys, zipfile

from PyQt6.QtWidgets import QFileDialog, QWidget, QApplication, QMainWindow, QHBoxLayout, QPushButton, QWidget, QStackedWidget, QLabel, QVBoxLayout

class Page(QWidget):
    def __init__(self, window:MainWindow, *args, **kwargs):
        super().__init__(window)
        self.w = window
        self.layout:QHBoxLayout = QHBoxLayout(self)
        self.__post_init__()

    def __post_init__(self):
        ...

class WelcomePage(Page):
    def __post_init__(self):
        label = QLabel("Привет! Это установщик приложения")
        self.layout.addWidget(label)

class DirPage(Page):
    def __post_init__(self):
        self.btn_choise = QPushButton("Выберите путь установки")
        self.btn_choise.clicked.connect(self.choose_dir)
        self.layout.addWidget(self.btn_choise)
        
    def choose_dir(self):
        start = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs")
        path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку установки",
            start,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        if path:
            self.btn_choise.setText(f"Выбранный путь: {path}")
            self.w.install_path = path

class InstallPage(Page):
    def __post_init__(self):
        self.btn = QPushButton("Установить приложение?")
        self.btn.clicked.connect(self.install)
        self.layout.addWidget(self.btn)

    def install(self):
            if self.w.install_path is None:
                self.btn.setText("Выбран не правильный путь! Попробуйте снова, изменя путь установки")
                return
            
            with zipfile.ZipFile(os.path.join(sys._MEIPASS, "archive-win64.zip")) as z:
                z.extractall(self.w.install_path)

            exe_path = os.path.join(self.w.install_path, "Lows.exe")
            shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", "Low-Level.lnk")

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.IconLocation = exe_path 
            shortcut.Description = "Low-Level"
            shortcut.Save()

            self.w.close()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Установка")
        self.install_path = None

        root = QVBoxLayout(self)

        self.widget = QStackedWidget(self)
        self.setFixedSize(600, 400)

        self.WelcomePage = WelcomePage(self)
        self.DirPage = DirPage(self)
        self.InstallPage = InstallPage(self)

        self.widget.setStyleSheet("QStackedWidget { border: 2px solid #262E36}")

        self.widget.addWidget(self.WelcomePage)
        self.widget.addWidget(self.DirPage)
        self.widget.addWidget(self.InstallPage)

        self.active = 0
        self.widget.setCurrentIndex(0)

        nav = QHBoxLayout()
        nav.addStretch()
        self.btn_back = QPushButton("< Назад")
        self.btn_next = QPushButton("Далее >")
        self.btn_cancel = QPushButton("Отмена")
        nav.addStretch()
        nav.addWidget(self.btn_back)
        nav.addWidget(self.btn_next)
        nav.addWidget(self.btn_cancel)

        root.addWidget(self.widget)
        root.addLayout(nav)

        self.btn_back.clicked.connect(self.go_back)
        self.btn_next.clicked.connect(self.go_next)
        self.btn_cancel.clicked.connect(self.close)

        self.update_buttons()

    def go_back(self):
        if self.active > 0:
            self.active -= 1
            self.widget.setCurrentIndex(self.active)
            self.update_buttons()

    def go_next(self):
        if self.active < self.widget.count() - 1:
            self.active += 1
            self.widget.setCurrentIndex(self.active)
            self.update_buttons()

    def update_buttons(self):
        self.btn_back.setEnabled(self.active > 0)
        self.btn_next.setEnabled(self.active < self.widget.count() - 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())