import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import sys
import threading
import time

import matplotlib
import numpy as np
from PyQt5.QtCore import Qt, QSizeF,QSize
from PyQt5.QtGui import QPixmap, QRegion, QPainterPath
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QMenu
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
from matplotlib.patheffects import withStroke

matplotlib.use('qtagg')


class ProtractorWidget(QtWidgets.QGraphicsView):
    def __init__(self):
        super().__init__()

        self.__drag_win = False
        self.angle = 180
        self.figure_size = (10, 10)
        self.base_dpi = 80
        self.mindpi = 60
        self.maxdpi = max(QtWidgets.QApplication.desktop().height(), QtWidgets.QApplication.desktop().width()) // \
                      self.figure_size[0]

        self.init_ui()

    def init_ui(self):
        self.setScene(QtWidgets.QGraphicsScene())
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(0.5)

        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.protractor = self.create_protractor()
        self.scene().addItem(self.protractor)

        self.update_protractor_windows()

    def create_protractor(self):
        self.canvas = FigureCanvas(Figure(figsize=self.figure_size, dpi=self.base_dpi, constrained_layout=True))
        self.ax = self.canvas.figure.add_subplot(projection="polar")

        graphics_item = QtWidgets.QGraphicsProxyWidget()
        graphics_item.setWidget(self.canvas)
        graphics_item.resize(QSizeF(self.canvas.size()))
        self.draw_protractor()

        return graphics_item

    def update_protractor(self):
        self.scene().removeItem(self.protractor)
        self.protractor = self.create_protractor()
        self.scene().addItem(self.protractor)

        self.update_protractor_windows()

    def update_protractor_windows(self):
        size = self.protractor.size()
        self.resize(int(size.width()), int(size.height()))
        x, y = 0, 0
        painter_path = QPainterPath().simplified()
        painter_path.moveTo((x + int(size.width())) // 2, (y + int(size.height())) // 2)
        start_angle = -4 if self.angle == 180 else 0
        end_angle = 188 if self.angle == 180 else 360
        painter_path.arcTo(x, y, int(size.width()), int(size.height()), start_angle, end_angle)  # Ensure a half circle
        painter_path.lineTo(painter_path.elementAt(1).x, painter_path.elementAt(1).y)
        region = QRegion(painter_path.toFillPolygon().toPolygon())
        self.setWindowOpacity(0.5)
        self.setMask(region)
        # Set the window position to be centered on the screen
        # screen_width = QtWidgets.QApplication.desktop().width()
        # screen_height = QtWidgets.QApplication.desktop().height()
        # window_x = (screen_width - size.width()) // 2
        # window_y = (screen_height - size.height()) // 2
        # self.move(int(window_x), int(window_y))

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.MouseButton.LeftButton:
            self.__drag_win = True
            self.__drag_win_x = e.x()
            self.__drag_win_y = e.y()
            self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)

    def mouseMoveEvent(self, e):
        if self.__drag_win:
            pos = e.globalPos()
            self.move(pos.x() - self.__drag_win_x, pos.y() - self.__drag_win_y)

    def mouseReleaseEvent(self, e):
        if e.button() == QtCore.Qt.MouseButton.LeftButton:
            self.__drag_win = False
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

    def set_protractor_size(self, dpi):
        self.canvas.figure.set_dpi(dpi)
        self.canvas.setFixedSize(*(int(self.canvas.figure.get_dpi() * s) for s in self.canvas.figure.get_size_inches()))
        self.update_protractor()

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        switch_action = menu.addAction(f"{360 if self.angle == 180 else 180}°量角器")
        quit_action = menu.addAction("退出")
        action = menu.exec_(self.mapToGlobal(e.pos()))
        if switch_action == action:
            self.angle = 360 if self.angle == 180 else 180
            self.update_protractor()
        elif action == quit_action:
            self.close()

    def wheelEvent(self, e):
        print(e.angleDelta().y())
        dpi = max(min(self.canvas.figure.get_dpi() + e.angleDelta().y()/120 * 0.5, self.maxdpi), self.mindpi)
        if dpi in [self.maxdpi, self.mindpi]:
            return
        # self.setWindowOpacity(0.01)
        self.base_dpi = dpi
        self.set_protractor_size(dpi)
    def draw_protractor(self):
        self.ax.clear()
        self.ax.set_thetamin(0)
        self.ax.set_thetamax(360)
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.ax.set_rlim(0, 1)
        self.ax.grid(False)

        scales = np.zeros((self.angle + 1, 2, 2))
        angles = np.linspace(0, np.deg2rad(self.angle), self.angle + 1)
        scales[:, :, 0] = np.stack((angles, angles), axis=1)
        scales[:, 0, 1] = 0.96
        scales[::5, 0, 1] = 0.93
        scales[::10, 0, 1] = 0.2
        scales[::90, 0, 1] = 0
        scales[:, 1, 1] = 1

        scales_coll = LineCollection(scales, linewidths=[2, 1, 1, 1, 1], color="k", linestyles="solid")
        zero_line = LineCollection([[[0, 0.9], [0, 1]], [[np.pi, 0.9], [np.pi, 1]]], linewidths=[2], color="r",
                                   linestyles="solid")
        self.ax.add_collection(scales_coll)
        self.ax.add_collection(zero_line)

        for r in [0.999, 0.815, 0.7, 0.2]:
            semi = np.linspace(0, np.deg2rad(self.angle) if r != 0.999 else np.deg2rad(360), 1000)
            rs = np.full_like(semi, fill_value=r)
            self.ax.plot(semi, rs, color="k")

        text_kw = dict(rotation_mode='anchor',
                       va='top', ha='center', clip_on=False,
                       path_effects=[withStroke(linewidth=12, foreground='white')])

        for i in range(0, self.angle + 1, 10):
            theta = np.deg2rad(i)
            if theta == np.pi / 2:
                self.ax.text(theta, 0.85, i, fontsize=40, **text_kw)
                continue
            elif theta == np.pi * 1.5:
                self.ax.text(theta, 0.85, 90, rotation=i - 90, fontsize=40, **text_kw)
                continue

            self.ax.text(theta, 0.89, ((180 - i) % 180 if i not in (0, 360) else 180), rotation=i - 90, fontsize=24,
                         **text_kw)
            self.ax.text(theta, 0.79, (i % 180 if i != 180 else 180), rotation=i - 90, fontsize=18,
                         color='blue', **text_kw)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProtractorWidget()
    ex.show()
    sys.exit(app.exec_())
