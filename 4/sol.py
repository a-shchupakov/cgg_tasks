import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter
import math
from PyQt5.QtCore import Qt

sqrt32 = math.sqrt(3.0) / 2

class DrawingWidget(QWidget):
    def __init__(self, func):
        super().__init__()

        self.initUI(func)

    def initUI(self, func):
        self.function = func

        self.setGeometry(150, 150, 1280, 720)

        self.setWindowTitle('Drawing')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.setPen(Qt.black)
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def draw(self, qp):
        mx, my = self.size().width(), self.size().height()
        x1, x2, y1, y2 = -3, 3, -3, 3
        n = 50
        m = mx * 2
        top = [math.inf] * (mx + 1)
        bottom = [-math.inf] * (mx + 1)
        minx = math.inf
        maxx = -minx
        miny = minx
        maxy = maxx

        for i in range(n + 1):
            x = x2 + i * (x1 - x2) / n
            for j in range(n + 1):
                y = y2 + j * (y1 - y2) / n
                z = self.function(x, y)
                xx, yy = get_isometric_coords(x, y, z)
                if xx > maxx:
                    maxx = xx
                if yy > maxy:
                    maxy = yy
                if xx < minx:
                    minx = xx
                if yy < miny:
                    miny = yy

        for i in range(mx):
            top[i] = my
            bottom[i] = 0

        for i in range(n + 1):
            x = x2 + i * (x1 - x2) / n
            for j in range(m + 1):
                y = y2 + j * (y1 - y2) / m
                z = self.function(x, y)
                xx, yy = get_isometric_coords(x, y, z)

                xx = int((xx - minx) / (maxx - minx) * mx)
                yy = int((yy - miny) / (maxy - miny) * my)

                if yy > bottom[xx]:
                    qp.setPen(Qt.darkMagenta)
                    qp.drawPoint(xx, yy)
                    bottom[xx] = yy

                if yy < top[xx]:
                    qp.setPen(Qt.darkCyan)
                    qp.drawPoint(xx, yy)
                    top[xx] = yy

        top = [math.inf] * (mx + 1)
        bottom = [-math.inf] * (mx + 1)
        for i in range(n + 1):
            y = y2 + i * (y1 - y2) / n
            for j in range(m):
                x = x2 + j * (x1 - x2) / m
                z = self.function(x, y)
                xx, yy = get_isometric_coords(x, y, z)

                xx = int((xx - minx) / (maxx - minx) * mx)
                yy = int((yy - miny) / (maxy - miny) * my)

                if yy > bottom[xx]:
                    qp.setPen(Qt.darkMagenta)
                    qp.drawPoint(xx, yy)
                    bottom[xx] = yy

                if yy < top[xx]:
                    qp.setPen(Qt.darkCyan)
                    qp.drawPoint(xx, yy)
                    top[xx] = yy


def get_isometric_coords(x, y, z):
    xx = (y - x) * sqrt32
    yy = (x + y) / 2 - z
    return xx, yy


def f(x, y):
    return math.cos((math.gcd(int(x), int(y))))


def my_exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':
    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook
    app = QApplication(sys.argv)
    ex = DrawingWidget(f)
    sys.exit(app.exec_())
