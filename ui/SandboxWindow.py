from __future__ import annotations

from PyQt6 import QtWidgets
from PyQt6.QtGui import QBrush, QColor, QPainter, QIcon, QPen
from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QListWidget, QListWidgetItem, QGraphicsItem, QGraphicsPixmapItem

from PyQt6 import QtCore

from base.functions import safe_class, get_texture
from base.font import Font
from base.cursors import Cursor
from base.MusicPlayer import MusicPlayer
from base.folders import folder, block_config, unit_config, settings

from ui.Widgets import Labels
from ui.PauseMenu import PauseMenu

import time, math

from world.WorldManager import WorldManager
from world.WorldLoader import WorldLoader
from world.World import World

from ui.ResourcePanel import ResourcePanel

from components.Storable import Storable
from components.SceneObject import Cell, Angle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.MainWindow import MainWindow
    from ui.Menu import Menu

round = math.floor

@safe_class
class FPSViewer(QtWidgets.QWidget):
    def __init__(self, window:SandboxWindow):
        self._frame_count = 0
        self._frame_times = []
        self._last_report = time.time()

        super().__init__(window)
        layout = QtWidgets.QVBoxLayout(self)
        self.fps = Labels.Mono()
        self.avg = Labels.Mono()
        self.max_fps = Labels.Mono()
        self.min_fps = Labels.Mono()

        layout.addWidget(self.fps)
        layout.addWidget(self.avg)
        layout.addWidget(self.max_fps)
        layout.addWidget(self.min_fps)

        self.move(10, 10)
        self.setFixedSize(QtCore.QSize(250, 100))
        self.show()

    def refresh(self, now, dt):   
        self._frame_count += 1
        self._frame_times.append(dt)

        if now - self._last_report >= 1.0:
            elapsed = now - self._last_report

            fps = self._frame_count / elapsed

            frame_fps = [1 / t for t in self._frame_times if t > 0]

            avg_fps = sum(frame_fps) / len(frame_fps)
            max_fps = max(frame_fps)
            min_fps = min(frame_fps)

            self.fps.setText(f"FPS: {fps:.0f}")
            self.avg.setText(f"AVG: {avg_fps:.0f}")
            self.max_fps.setText(f"MAX: {max_fps:.0f}")
            self.min_fps.setText(f"MIN: {min_fps:.0f}")

            self._frame_count = 0
            self._frame_times.clear()
            self._last_report = now

@safe_class
class VersionViewer(QtWidgets.QWidget):
    def __init__(self, window):
        super().__init__(window)
        layout = QtWidgets.QVBoxLayout(self)
        self.label = Labels.Dim(folder.version)
        layout.addWidget(self.label)

        self.setFixedSize(QtCore.QSize(400, 50))
        self.hide()

    def reposition(self):
        if self.parent():
            x = (self.parent().width() - self.width())//2
            y = self.parent().height()-50
            self.move(x, y)
        self.show()

@safe_class
class MapScene(QGraphicsScene):
    def __init__(self, intensity, window:SandboxWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window=window
        self.intensity = intensity

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QColor("#EBE5E5"))     
        painter.setPen(QPen(QColor("#2a2a2a"), 1))   
        w = self.window.manager.current.size[0]*32
        h = self.window.manager.current.size[1]*32
        for x in range(0, w + 1, 32):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h + 1, 32):
            painter.drawLine(0, y, w, y)

@safe_class
class MapView(QGraphicsView):
    def __init__(self, window:SandboxWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.w=window

        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)
        
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.item:QGraphicsPixmapItem = None

    def remove_item(self):
        if self.item is not None and self.scene() is not None:
            self.item.setVisible(False)

    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        self.remove_item()
    
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        if self.scene() is None:
            return
        
        scene_pos = self.mapToScene(event.pos())
        _x, _y = round(scene_pos.x()), round(scene_pos.y())
        x, y = math.floor((_x/32)), math.floor(_y/32)

        size = (int(get_texture(self.w.manager.current.placing_block).width()/32), int(get_texture(self.w.manager.current.placing_block).height()/32))

        for dx in range(size[0]):
            for dy in range(size[1]):
                blocks = self.w.manager.current.block_map.get(Cell(dx+x, dy+y))
                if blocks is None:
                    continue
                for block in blocks:
                    if block_config[block.name]["z"] < 20:
                        continue
                    self.remove_item()
                    return

        self.update_item()
        self.item.setPos(x*32, y*32)

    def update_item(self):
        size = (int(get_texture(self.w.manager.current.placing_block).width()/32), int(get_texture(self.w.manager.current.placing_block).height()/32))

        if self.item is None:
            self.item = self.scene().addPixmap(get_texture(self.w.manager.current.placing_block))
            self.item.setZValue(100)
            self.item.setOpacity(0.5)
        else:   
            self.item.setPixmap(get_texture(self.w.manager.current.placing_block))

        self.item.setTransformOriginPoint((size[0]/2)*32, (size[1]/2)*32)
        self.item.setRotation(self.w.manager.current.place_angle.value)
        self.item.setVisible(True)

@safe_class
class SandboxWindow(QWidget):
    def __init__(self, window:MainWindow, loader=WorldLoader):
        super().__init__()

        self.main_window:MainWindow = window
        
        self.scene:MapScene = MapScene(0, self)
        #self.scene.setSceneRect(QRectF(0, 0, 8192, 8192))

        self.view = MapView(self, self.scene, self)

        self.resource_panel = ResourcePanel(self)

        self.manager = WorldManager(self, self.update_tool_panel, loader=loader, resource_panel=self.resource_panel)

        self.manager.current = World()
        self.manager.current_name = None
        
        background_brush = QBrush(QColor(30, 30, 30))
        self.scene.setBackgroundBrush(background_brush)

        self.view.setCursor(Cursor.Cursor)
        
        self.keys_pressed:set[int] = set()

        self.view.wheelEvent = self.wheelEvent

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(int(1000/settings.get("fps")))

        self.view.setMouseTracking(True)

        central = QtWidgets.QHBoxLayout()

        central.addWidget(self.view)

        self.tool_panel = QListWidget()
        self.tool_panel.setIconSize(QtCore.QSize(64, 64))
        self.tool_panel.setGridSize(QtCore.QSize(96, 196))
        self.tool_panel.setViewMode(QListWidget.ViewMode.IconMode)
        self.tool_panel.setFlow(QListWidget.Flow.TopToBottom) 
        self.tool_panel.setWrapping(False)
        self.tool_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tool_panel.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.tool_panel.setDragEnabled(False)
        self.tool_panel.setFont(Font.Bold)
        self.tool_panel.setFixedWidth(200)
        self.tool_panel.setCursor(Cursor.Hand)

        self.last_time = time.time()

        if not self.manager.current.devmode:
            self.tool_names = {}
            for clt in [block_config, unit_config]:
                for name, value in clt.items():
                    if not value.get("relief", False):
                        self.tool_names[name] = value
        else:
            self.tool_names = block_config
            self.tool_names.update(unit_config)

        self.tool_panel.setCurrentRow(0)

        self.update_tool_panel()

        self.tool_panel.currentItemChanged.connect(self.on_tool_changed)

        central.addWidget(self.tool_panel)

        self.setLayout(central)

        self.vx = 0
        self.vy = 0
        self.max_speed = 10
        self.acceleration = 4
        self.target_scale:float = 1
        self.scale:float= 1
        self.sprint = False

        self.pause_menu = PauseMenu(self)
        self.menu_active:Menu|None = None

        self.fps_viewer = FPSViewer(self)
        self.version_viewer = VersionViewer(self)
        self.resource_panel.raise_()

    def update_tool_panel(self):
        if not hasattr(self, "tool_panel"):
            return
        
        self.tool_panel.clear()
        
        coef = folder.config.get("craft_coef", 1)

        for name, i in self.tool_names.items():
                    if not self.manager.current.devmode:
                        if name not in self.manager.current.opened:
                            continue
                    
                    pixmap = get_texture(name)
                    icon = QIcon(pixmap)
          
                    cost:dict = i.get("cost")
                    exc = ""
                    if cost is not None:
                        for namef, value in cost.items():
                            exc += f"\n{namef} x{int(value*coef)}"
        
                    item = QListWidgetItem(icon, f"{name.replace("_", " ").title()}{exc}")
                    item.setData(Qt.ItemDataRole.UserRole, name)
                    item.setToolTip(f"{name.replace("_", " ").title()}{exc}")

                    self.tool_panel.addItem(item)

    def blur(self):
        if self.manager.overlay is not None:
            self.manager.overlay.setOpacity(0.8)
            self.manager.overlay.show()

    def unblur(self):
        if self.manager.overlay is not None:
            self.manager.overlay.setOpacity(0)
            self.manager.overlay.show()

    def closeEvent(self, event):
        self.timer.stop()
        MusicPlayer.stop()
        MusicPlayer.play("click_2")
        if self.manager.current_name is not None:
            self.manager.save(self.manager.current_name)
        self.pause_menu.Back()
        self.main_window.MenuWindow.show()
        return event.accept()
    
    def on_tool_changed(self, current, f):
        if current is not None:
            self.view.setFocus()
            MusicPlayer.play("click_1")
            self.manager.current.placing_block = current.data(Qt.ItemDataRole.UserRole)

    def mousePressEvent(self, event):
        if self.menu_active is not None:
            return
        
        scene_pos = self.view.mapToScene(event.pos())
        x, y = round(scene_pos.x()/32), round(scene_pos.y()/32)

        if event.button() == Qt.MouseButton.LeftButton:
            self.manager.current.click("left", x, y)
      
        elif event.button() == Qt.MouseButton.RightButton:
            self.manager.current.click("right", x, y)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            MusicPlayer.play("click_2")
            if self.menu_active is not None:
                self.menu_active.Back()
            else:
                self.pause_menu.Show()

        key = event.nativeScanCode()

        self.keys_pressed.add(key)

        if key == 0x13:
            value = (self.manager.current.place_angle.value+90)
            value = value-((value//360)*360)
            self.manager.current.place_angle = Angle(value)
            self.view.update_item()

        if key == 42:
            self.sprint = True
            self.max_speed*=2
            self.acceleration*=2
    
    def keyReleaseEvent(self, event):
        key = event.nativeScanCode()
        self.keys_pressed.discard(key)
        if key == 42:
            self.sprint = False
            self.max_speed//=2
            self.acceleration//=2

    def update(self):
            self.now = time.time()
            dt = (self.now - self.last_time)
            self.last_time = self.now

            self.timer.setInterval(int(1000/settings.get("fps")))
            self.update_cam(dt)
            self.manager.current.update(dt)

            dct1={}
            if self.manager.current.Base is not None:
                dct1 = self.manager.current.Base.components[Storable].dict()        

            dct2=self.manager.current.operator.inventory.dict()
            self.resource_panel.update(dct1, dct2)

            self.fps_viewer.refresh(self.now, dt)

    def update_cam(self, dt):          
            if abs(self.target_scale - self.scale) > 0.01:
                old_scale = self.scale
                self.scale = self.scale + (self.target_scale - self.scale) * 6.0 * dt

                factor = self.scale / old_scale
                self.view.scale(factor, factor)

            dx:float = 0
            dy:float = 0

            if self.menu_active is None:
                if 17 in self.keys_pressed:
                    dy -= 1
                if 31 in self.keys_pressed:
                    dy += 1
                if 30 in self.keys_pressed:   
                    dx -= 1
                if 32 in self.keys_pressed:   
                    dx += 1

                if dx != 0 and dy != 0:
                    dx *= 0.7071
                    dy *= 0.7071

            target_vx = dx * self.max_speed
            target_vy = dy * self.max_speed
            
            self.vx += (target_vx - self.vx) * self.acceleration * dt
            self.vy += (target_vy - self.vy) * self.acceleration * dt
            
            if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
                current_x = self.view.horizontalScrollBar().value() # type: ignore
                current_y = self.view.verticalScrollBar().value() # type: ignore

                self.view.horizontalScrollBar().setValue(current_x + int(self.vx * dt * 60)) # type: ignore 
                self.view.verticalScrollBar().setValue(current_y + int(self.vy * dt * 60)) # type: ignore

    def wheelEvent(self, event):
        if self.menu_active is not None:
            return
        if event.angleDelta().y() > 0:
            self.target_scale *= 1.15
        else:
            self.target_scale /= 1.15
        
        self.target_scale = max(0.4, min(2.0, self.target_scale))

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if self.menu_active is not None:
            self.menu_active.reposition()
        self.version_viewer.reposition()
        self.resource_panel.reposition()

    def __repr__(self):
        return self.__class__.__name__

    def show(self):
        self.last_time = time.time()
        self.main_window.widget.setCurrentIndex(1)
        self.version_viewer.reposition()
        self.resource_panel.reposition()
        self.timer.start()
        MusicPlayer.start()
