import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QRegion, QPainterPath, QBitmap
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QMenu
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from projector import Protractor
from matplotlib import pyplot as plt

class ProtractorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__drag_win = False
        self.mindpi = 60
        self.maxdpi = max(QApplication.desktop().height(), QApplication.desktop().width()) // 10
        self.bsize = 800
        self.minsize = 600
        self.maxsize = max(QApplication.desktop().height(), QApplication.desktop().width())
        self.protractor = Protractor(angle=180, figsize=(10, 10), dpi=242, constrained_layout=True)
        self.init_ui()

    def init_ui(self):
        self.set_window_properties()
        self.create_canvas_and_label()
        self.move_center()

    def set_window_properties(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(0.6)

    def create_canvas_and_label(self):
        self.canvas = FigureCanvas(self.protractor)
        self.canvas.figure.draw_protractor()
        self.qlabel = QLabel(self)
        self.qlabel.setScaledContents(True)
        self.qlabel.setPixmap(QPixmap(self.canvas.grab().toImage()))
        self.update_protractor_window(self.bsize)

    def update_protractor_window(self, size):
        self.qlabel.setFixedSize(int(size), int(size))
        w = self.qlabel.width() if self.qlabel.width() % 2 else self.qlabel.width() + 1
        h = self.qlabel.height() if self.qlabel.height() % 2 else self.qlabel.height() + 1
        fx = self.frameGeometry().center().x()
        fy = self.frameGeometry().center().y()
        self.setGeometry(fx - w // 2, fy - h // 2, w, h)  # 根据图像大小设置窗口

        fig = plt.figure(figsize=(5, 5), dpi=80, constrained_layout=True)
        ax = fig.add_subplot(projection="polar")
        ax.clear()
        ax.set_thetamin(0)
        ax.set_thetamax(360)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_rlim(0, 1)
        import numpy as np
        # 构建角度数组
        theta = np.linspace(0, 2 * np.pi, 1000)

        # 构建半径数组（这里使用常数1构建整个圆）
        r = np.ones_like(theta)

        # 填充颜色
        ax.fill(theta, r, color='k')  # 更改颜色这里的'orange'为你想要的颜色
        ax.grid(False)
        canvas1 = FigureCanvas(fig)
        qpixmap = QBitmap(QPixmap(canvas1.grab().toImage()))
        x, y = 0, 0
        painter_path = QPainterPath()
        painter_path.moveTo((x + w) // 2, (y + h) // 2)
        start_angle = -4 if self.canvas.figure.angle == 180 else 0
        end_angle = 188 if self.canvas.figure.angle == 180 else 360
        painter_path.arcTo(x, y, w, h, start_angle, end_angle)  # Ensure a half circle
        painter_path.lineTo(painter_path.elementAt(1).x, painter_path.elementAt(1).y)
        region = QRegion(qpixmap)
        self.setWindowOpacity(0.6)
        self.setMask(region)

    def move_center(self):
        fs = self.frameGeometry().size()
        cp = QApplication.desktop().availableGeometry().center()
        self.move(cp.x() - fs.width() // 2, cp.y() - fs.height() // 2)

    def mousePressEvent(self, e):
        self.__drag_win = True
        self.__drag_win_x = e.x()
        self.__drag_win_y = e.y()
        if e.button() != Qt.RightButton:
            self.setWindowOpacity(0.3)
        self.setCursor(Qt.OpenHandCursor)

    def mouseMoveEvent(self, e):
        if self.__drag_win:
            pos = e.globalPos()
            self.setWindowOpacity(0.3)
            self.move(pos.x() - self.__drag_win_x, pos.y() - self.__drag_win_y)

    def mouseReleaseEvent(self, e):
        self.__drag_win = False
        self.setCursor(Qt.ArrowCursor)
        self.setWindowOpacity(0.6)

    def wheelEvent(self, e):
        size = max(min(self.size().width() + e.angleDelta().y() / 120 * 2, self.maxsize), self.minsize)
        if size in [self.maxsize, self.minsize]:
            return
        self.update_protractor_window(size)

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        switch_action = menu.addAction(f"{360 if self.canvas.figure.angle == 180 else 180}°量角器")
        change_style = menu.addAction("切换风格")
        change_color = menu.addAction("切换颜色")
        quit_action = menu.addAction("退出")

        action = menu.exec_(self.mapToGlobal(e.pos()))
        if switch_action == action:
            self.canvas.figure.angle = 360 if self.canvas.figure.angle == 180 else 180
            self.canvas.figure.draw_protractor()
            self.qlabel.setPixmap(QPixmap(self.canvas.grab().toImage()))
            self.update_protractor_window(self.size().width())
        elif action == change_style:
            self.canvas.figure.change_style()
            self.canvas.figure.draw_protractor()
            self.qlabel.setPixmap(QPixmap(self.canvas.grab().toImage()))
        elif action == change_color:
            self.canvas.figure.draw_text("green")
            self.canvas.draw()
        elif action == quit_action:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProtractorWidget()
    ex.show()
    sys.exit(app.exec_())