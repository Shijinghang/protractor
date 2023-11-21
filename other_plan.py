import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QRegion, QPainterPath
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QLabel, QMenu, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from projector import Protractor


class ProtractorWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__drag_win = False
        self.mindpi = 60
        self.maxdpi = max(QApplication.desktop().height(), QApplication.desktop().width()) // 10
        self.protractor = Protractor(angle=180, figsize=(10, 10), dpi=80, constrained_layout=True)
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
        # self.canvas.show()
        # vlayout = QVBoxLayout()
        # vlayout.addWidget(self.canvas)
        self.setCentralWidget(self.canvas)
        # self.setLayout(vlayout)
        self.qlabel = QLabel(self)
        self.qlabel.setScaledContents(True)
        self.update_protractor()

    def update_protractor(self):
        self.canvas.figure.draw_protractor()
        # self.canvas.draw()
        self.canvas.show()
        # self.pixmap = QPixmap(self.canvas.grab().toImage())
        # self.qlabel.setFixedSize(self.pixmap.width(), self.pixmap.height())
        # self.qlabel.setPixmap(self.pixmap)
        self.update_protractor_windows()

    def update_protractor_windows(self):
        fw = int(self.canvas.figure.get_figwidth() * self.canvas.figure.get_dpi())
        fh = int(self.canvas.figure.get_figheight() * self.canvas.figure.get_dpi())
        w = fw if fw % 2 else fw + 1
        h = fh if fh % 2 else fh + 1
        fx = self.frameGeometry().center().x()
        fy = self.frameGeometry().center().y()
        print(fx, fy)

        self.setGeometry(fx - w // 2, fy - h // 2, w, h)  # 根据图像大小设置窗口

        x, y = 0, 0
        painter_path = QPainterPath()
        painter_path.moveTo((x + w) // 2, (y + h) // 2)
        start_angle = -4 if self.canvas.figure.angle == 180 else 0
        end_angle = 188 if self.canvas.figure.angle == 180 else 360
        painter_path.arcTo(x, y, w, h, start_angle, end_angle)  # Ensure a half circle
        painter_path.lineTo(painter_path.elementAt(1).x, painter_path.elementAt(1).y)
        region = QRegion(painter_path.toFillPolygon().toPolygon())
        self.setWindowOpacity(0.6)
        self.setMask(region)

    def move_center(self):
        fs = self.frameGeometry().size()
        cp = QApplication.desktop().availableGeometry().center()
        self.move(cp.x() - fs.width() // 2, cp.y() - fs.height() // 2)

    def mousePressEvent(self, e):
        print("mousePressEvent")
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
        dpi = max(min(self.canvas.figure.get_dpi() + e.angleDelta().y() / 120 * 0.3, self.maxdpi), self.mindpi)
        if dpi in [self.maxdpi, self.mindpi]:
            return
        self.set_protractor_size(dpi)

    def set_protractor_size(self, dpi):
        self.canvas.figure.set_dpi(dpi)
        self.canvas.setFixedSize(*(int(self.canvas.figure.get_dpi() * s) for s in self.canvas.figure.get_size_inches()))
        self.update_protractor()

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        switch_action = menu.addAction(f"{360 if self.canvas.figure.angle == 180 else 180}°量角器")
        change_color1 = menu.addAction("change color")
        change_color2 = menu.addAction("change green")

        quit_action = menu.addAction("退出")

        action = menu.exec_(self.mapToGlobal(e.pos()))
        if switch_action == action:
            self.canvas.figure.angle = 360 if self.canvas.figure.angle == 180 else 180
            self.update_protractor()
        elif action == quit_action:
            self.close()
        elif action == change_color1:
            self.canvas.figure.draw_text("red")
            self.canvas.draw()
            # self.canvas.show()
        elif action == change_color2:
            self.canvas.figure.draw_text("green")
            self.canvas.draw()
            # self.canvas.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProtractorWidget()
    ex.show()
    sys.exit(app.exec_())
