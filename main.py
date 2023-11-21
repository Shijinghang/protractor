import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QRegion, QBitmap
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QMenu
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from protractor import Protractor


class ProtractorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.full_mask = None
        self.semi_mask = None
        self.qlabel = None
        self.canvas = None
        self.__drag_win = False
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
        self.semi_mask = QPixmap(FigureCanvas(self.protractor.get_mask(180)).grab().toImage())
        self.full_mask = QPixmap(FigureCanvas(self.protractor.get_mask(360)).grab().toImage())
        self.qlabel = QLabel(self)
        self.qlabel.setScaledContents(True)
        self.qlabel.setPixmap(QPixmap(self.canvas.grab().toImage()))
        self.update_protractor_window(self.bsize)

    def update_protractor_window(self, size):

        size = int(size if size % 2 else size+1)
        self.qlabel.setFixedSize(size, size)
        fx = self.frameGeometry().center().x()
        fy = self.frameGeometry().center().y()
        self.setGeometry(fx - size // 2, fy - size // 2, size, size)  # 根据图像大小设置窗口

        mask_qpm = self.semi_mask if self.canvas.figure.angle == 180 else self.full_mask
        mask_qbm = QBitmap(mask_qpm.scaled(self.qlabel.width(), self.qlabel.height()))
        region = QRegion(mask_qbm)
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
        print(e.angleDelta().y())
        size = max(min(self.size().width() + e.angleDelta().y() / 120 * 4, self.maxsize), self.minsize)
        if size in [self.maxsize, self.minsize]:
            return
        self.update_protractor_window(size)

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        switch_action = menu.addAction(f"{360 if self.canvas.figure.angle == 180 else 180}°量角器")
        change_style = menu.addAction("切换风格")
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
        elif action == quit_action:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProtractorWidget()
    ex.show()
    sys.exit(app.exec_())
