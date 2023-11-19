import sys
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

class QLabelExample(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Dynamic QLabel Image Size')

        # 创建 QLabel 显示图片
        self.image_label = QLabel(self)
        self.update_image()  # 初始化显示图片

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # 使用定时器定期更新图片大小
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(2000)  # 每隔两秒更新一次图片大小

    def update_image(self):
        # 创建一个随机大小的 QPixmap
        pixmap = QPixmap("test.png")  # 替换为你的图像路径
        new_width = pixmap.width() * 0.8  # 缩小图片到80%的宽度
        new_height = pixmap.height() * 0.8  # 缩小图片到80%的高度
        pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio)

        # 设置 QLabel 的图片
        self.image_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QLabelExample()
    ex.show()
    sys.exit(app.exec_())
