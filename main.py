import sys

import matplotlib
from matplotlib.figure import Figure
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QPixmap, QRegion, QPainterPath
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QLabel
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.collections import LineCollection
from matplotlib.patheffects import withStroke

matplotlib.use('qtagg')


class ProtractorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__drag_win = False
        self.init_ui()

    def init_ui(self):
        self.set_window_properties()
        self.create_canvas_and_label()
        self.set_protractor_windows()
        self.center()

    def set_window_properties(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(0.5)

    def create_canvas_and_label(self):
        self.canvas = FigureCanvas(Figure(figsize=(8, 8), dpi=144, constrained_layout=True))
        self.ax = self.canvas.figure.add_subplot(projection="polar")

        self.qlabel = QLabel(self)
        self.qlabel.setScaledContents(True)

        self.update_protractor()

    def update_protractor(self):
        self.draw_protractor()
        self.pixmap = QPixmap(self.canvas.grab().toImage())
        print(self.canvas.figure.get_size_inches())

        self.qlabel.setFixedSize(self.pixmap.width(), self.pixmap.height())
        self.qlabel.setPixmap(self.pixmap)
        print("update_pro")
        self.set_protractor_windows()

    def set_protractor_windows(self):
        w, h = self.pixmap.width(), self.pixmap.height()
        self.setGeometry(0, 0, w, h)  # 根据图像大小设置窗口
        x, y = 0, 0
        path = QPainterPath()
        path.moveTo((x + w) // 2, (y + h) // 2)
        path.arcTo(x, y, w, h, -3, 180 + 6)  # Ensure a half circle
        path.lineTo(path.elementAt(1).x, path.elementAt(1).y)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, e):
        self.__drag_win = True
        self.__drag_win_x = e.x()
        self.__drag_win_y = e.y()
        self.setCursor(Qt.OpenHandCursor)

    def mouseMoveEvent(self, e):
        if self.__drag_win:
            pos = e.globalPos()
            self.move(pos.x() - self.__drag_win_x, pos.y() - self.__drag_win_y)

    def mouseReleaseEvent(self, e):
        self.__drag_win = False
        self.setCursor(Qt.ArrowCursor)

    def wheelEvent(self, e):
        self.set_protractor_size(15, 15)

    def set_protractor_size(self, w, h):
        self.canvas.figure.set_size_inches(w, h)
        self.canvas.setFixedSize(w * self.canvas.figure.dpi, h * self.canvas.figure.dpi)

        self.update_protractor()

    def draw_protractor(self):
        self.ax.clear()
        self.ax.set_thetamin(0)
        self.ax.set_thetamax(360)
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.ax.set_rlim(0, 1)
        self.ax.grid(False)

        scales = np.zeros((181, 2, 2))
        angles = np.linspace(0, np.deg2rad(180), 181)
        scales[:, :, 0] = np.stack((angles, angles), axis=1)
        scales[:, 0, 1] = 0.96
        scales[::5, 0, 1] = 0.93
        scales[::10, 0, 1] = 0.2
        scales[::90, 0, 1] = 0
        scales[:, 1, 1] = 1

        scales_coll = LineCollection(scales, linewidths=[2, 1, 1, 1, 1], color="k", linestyles="solid")
        self.ax.add_collection(scales_coll)

        for r in [0.999, 0.82, 0.7, 0.2]:
            semi = np.linspace(0, np.deg2rad(180) if r != 0.999 else np.deg2rad(360), 1000)
            rs = np.full_like(semi, fill_value=r)
            self.ax.plot(semi, rs, color="k")

        text_kw = dict(rotation_mode='anchor',
                       va='top', ha='center', color='black', clip_on=False,
                       path_effects=[withStroke(linewidth=12, foreground='white')])

        for i in range(0, 181, 10):
            theta = np.deg2rad(i)
            if theta == np.pi / 2:
                self.ax.text(theta, 0.85, i, fontsize=40, **text_kw)
                continue
            elif theta == np.pi * 1.5:
                self.ax.text(theta, 0.85, 90, rotation=i - 90, fontsize=40, **text_kw)
                continue

            self.ax.text(theta, 0.89, (i % 180 if i != 180 else 180), rotation=i - 90, fontsize=25, **text_kw)
            self.ax.text(theta, 0.79, ((180 - i) % 180 if i not in (0, 360) else 180), rotation=i - 90, fontsize=20,
                    **text_kw)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProtractorWidget()
    ex.show()
    sys.exit(app.exec_())
