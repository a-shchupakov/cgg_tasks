import sys
import math
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt


class DrawingWidget(QWidget):
    def __init__(self, func, a, b):
        super().__init__()

        self.initUI(func, a, b)

    def get_center(self):
        size = self.size()
        return size.width() // 2, size.height() // 2

    def initUI(self, func, a, b):
        self.function = func
        self.a = a
        self.b = b

        self.setGeometry(150, 150, 1280, 720)
        self.center = self.get_center()

        self.setWindowTitle('Drawing')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.setPen(Qt.black)
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def draw(self, qp):
        cache_y = dict()

        qp.translate(0, self.size().height())
        qp.scale(1.0, -1.0)

        size = self.size()
        a, b = self.a, self.b
        y_min, y_max = self.function(a), self.function(a)

        for xx in range(size.width()):
            x = a + xx*(b-a)/size.width()
            y = self.function(x)
            cache_y[xx] = y
            if y < y_min:
                y_min = y
            if y > y_max:
                y_max = y

        start = (self.function(a) - y_min) * size.height() / (y_max - y_min)
        self.draw_axes(qp, y_min, y_max)
        qp.drawPoint(0, start)

        prev = (0, start)
        for xx in range(size.width()):
            y = cache_y[xx]
            yy = (y - y_min) * size.height() / (y_max - y_min)

            qp.drawLine(prev[0], prev[1], xx, yy)
            prev = (xx, yy)

    def draw_axes(self, qp, y_min, y_max):
        a, b = self.a, self.b

        if a < 0 < b:
            y_0 = ((-a) / (b - a)) * self.size().width()

            qp.drawLine(y_0, 0, y_0, self.size().height())

        if y_min < 0 < y_max:
            x_0 = ((-y_min) / (y_max - y_min)) * self.size().height()

            qp.drawLine(0, x_0, self.size().width(), x_0)


def f(x):
    return x * math.sin(1/2*x**2) + 3


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DrawingWidget(f, -15, 15)
    sys.exit(app.exec_())
