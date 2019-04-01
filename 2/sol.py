import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QBasicTimer


# Уравнение в каноническом виде:
#   (y + (d-b))^2 = 2(x-c)/2a
#   p = 1/(2a)
#   f: [1/(4a) + c, b - d] - фокус
#   d: x = -1/(4a) + c - директриса

class DrawingWidget(QWidget):
    def __init__(self, scale=10, a=1.0, b=1.0, c=0.0, d=1.0):
        super().__init__()

        self.a, self.b, self.c, self.d = a, b, c, d
        self.scale_x, self.scale_y = scale, 0
        self.width, self.height = 0, 0
        self.dx, self.dy = 0, 0
        self.mouse_click_x = -1
        self.mouse_click_y = -1
        self.qp = QPainter()

        self.initUI()

    def initUI(self):
        self.setGeometry(150, 150, 900, 900)
        # self.timer = QBasicTimer()
        # self.timer.start(15, self)
        self.setWindowTitle('Drawing')
        self.show()

    def paintEvent(self, event):
        self.qp.setPen(Qt.black)
        self.qp.begin(self)

        self.draw()
        self.qp.end()

    def resizeEvent(self, event):
        new_width = event.size().width()
        new_height = event.size().height()
        self.width = new_width
        self.height = new_height
        self.scale_y = self.scale_x  # new_width * 6 / new_height

    def draw(self):
        # self.draw_parabola()
        # self.draw_parabola_dists()
        self.draw_parabola_deltas()
        self.draw_axes()

    def draw_axes(self):
        a_, b_, c_, d_ = self.a, self.b, self.c, self.d
        if a_ < 0:
            self.qp.scale(-1.0, 1.0)
            a_ = -a_
            c_ = -c_

        dx = self.get_screen_x(0) - self.get_screen_x(c_)
        dy = self.get_screen_y(d_ - b_) - self.get_screen_y(0)
        self.qp.setPen(Qt.black)
        self.qp.translate(dx, dy)

        self.qp.drawLine(-self.width / 2 - dx, 0, self.width / 2 - dx, 0)
        self.qp.drawLine(0, -self.height / 2 - dy, 0, self.height / 2 - dy)

    def draw_parabola_dists(self):
        self.qp.setPen(Qt.darkBlue)
        self.qp.resetTransform()
        self.qp.translate(self.width / 2, self.height / 2)
        self.qp.scale(1.0, -1.0)

        a_, c_ = self.a, self.c
        if a_ == 0:
            self.qp.drawLine(c_, self.height, c_, -self.height)
            return
        elif a_ < 0:
            self.qp.scale(-1.0, 1.0)
            a_ = -a_

        bound = self.width
        f = self.get_screen_x(1 / (4*a_)) - self.get_screen_x(0)
        x, y = 0, 0
        self.qp.drawPoint(x, y)

        while x <= bound:
            d1 = (f - x) ** 2 + (-(y + 1)) ** 2 - (-f - x) ** 2
            min_d = abs(d1)
            n_x, n_y = x, y + 1

            d2 = (f - (x + 1)) ** 2 + (-(y + 1)) ** 2 - (-f - (x + 1)) ** 2
            if abs(d2) < min_d:
                n_x, n_y = x + 1, y + 1
                min_d = abs(d2)

            d3 = (f - (x + 1)) ** 2 + (-y) ** 2 - (-f - (x + 1)) ** 2
            if abs(d3) < min_d:
                n_x, n_y = x + 1, y

            self.qp.drawPoint(n_x, n_y)
            self.qp.drawPoint(n_x, -n_y)
            x, y = n_x, n_y

    def draw_parabola_deltas(self):
        self.qp.setPen(Qt.red)
        self.qp.resetTransform()
        self.qp.translate(self.width / 2, self.height / 2)
        self.qp.scale(1.0, -1.0)

        a_, c_ = self.a, self.c
        if a_ == 0:
            self.qp.drawLine(c_, self.height, c_, -self.height)
            return
        elif a_ < 0:
            self.qp.scale(-1.0, 1.0)
            a_ = -a_

        bound = self.width
        p = self.get_screen_x(1/(2*a_)) - self.get_screen_x(0)
        x, y = 0, 0
        self.qp.drawPoint(x, y)

        p2 = 2 * p
        while x <= bound:
            delta = (y + 1)*(y + 1) - p2 * (x + 1)
            if delta < 0:
                other = delta + p2
                if abs(delta) < abs(other):
                    x, y = x + 1, y + 1
                else:
                    x, y = x, y + 1
            else:
                other = delta - 2 * y - 1
                if abs(delta) < abs(other):
                    x, y = x + 1, y + 1
                else:
                    x, y = x + 1, y

            self.qp.drawPoint(x, y)
            self.qp.drawPoint(x, -y)

    def draw_parabola(self):
        self.qp.setPen(Qt.black)
        self.qp.resetTransform()
        self.qp.translate(self.width / 2, self.height / 2)
        self.qp.scale(1.0, -1.0)

        a_, b_, c_, d_ = self.a, self.b, self.c, self.d
        if a_ == 0:
            self.qp.drawLine(c_, self.height, c_, -self.height)
            return
        elif a_ < 0:
            self.qp.scale(-1.0, 1.0)
            a_ = -a_
            c_ = -c_

        bound = self.width
        p = self.get_screen_x(1/(2*a_)) - self.get_screen_x(0)

        p2 = 2*p
        p4 = 2*p2
        x, y = 0, 0
        d = 1 - p

        while (y < p) and (x <= bound):
            self.qp.drawPoint(x, y)
            self.qp.drawPoint(x, -y)
            if d >= 0:
                x += 1
                d -= p2
            y += 1
            d += (2*y + 1)

        if d == 1:
            d = 1 - p4
        else:
            d = 1 - p2

        # self.qp.drawLine(x, 0, x, y)
        while x <= bound:
            self.qp.drawPoint(x, y)
            self.qp.drawPoint(x, -y)
            if d <= 0:
                y += 1
                d += 4 * y
            x += 1
            d -= p4

    def get_screen_x(self, x):
        return ((self.scale_x / 2 + x) / self.scale_x) * self.width

    def get_screen_y(self, y):
        return ((self.scale_y / 2 + y) / self.scale_y) * self.height

    def timerEvent(self, event):
        self.a += 0.15
        if self.a > 10:
            self.a = -10

        self.repaint()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DrawingWidget(a=0, b=1, c=.25, d=1, scale=1)

    sys.exit(app.exec_())
