from __future__ import annotations

from PyQt6 import QtWidgets

from base.cursors import Cursor
from base.functions import safe_class

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.SandboxWindow import SandboxWindow

@safe_class
class Menu(QtWidgets.QWidget):
    def __init__(self, window:SandboxWindow, parent:Menu = None):
        self.Window = window
        self.Parent = parent
        super().__init__(window)
        self.setCursor(Cursor.Cursor)
        self.hide()

    def reposition(self):
        if self.parent():
            x = (self.parent().width() - self.width()) // 2
            y = (self.parent().height() - self.height()) // 2
            self.move(x, y)

    def Show(self, *args):
        self.Window.menu_active = self
        self.reposition()
        self.show()
        self.raise_()
        if self.Parent is not None:
            self.Parent.hide()
        else:
            self.Window.tool_panel.hide()
            self.Window.blur()

    def Back(self, *args):
        self.hide()
        self.Window.menu_active = self.Parent

        if self.Parent is not None:
            self.Parent.Show()
        else:
            self.Window.tool_panel.show()
            self.Window.unblur()