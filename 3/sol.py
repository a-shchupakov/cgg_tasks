import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPolygonF
from PyQt5.QtCore import Qt, QPointF


class DrawingWidget(QWidget):
    def __init__(self, polygon=None):
        super().__init__()

        self.clicked_points = [] if polygon is None else polygon
        self.selected = polygon is not None
        self.polygon = [] if polygon is None else polygon

        self.mouseReleaseEvent = self.click
        self.keyReleaseEvent = self.key_release
        self.initUI()

    def key_release(self, event):
        if event.key() == Qt.Key_Space and self.selected:
            self.polygon = self.clicked_points
            self.repaint()

    def click(self, event):
        if not self.selected:
            x, y = event.x(), event.y()

            if len(self.clicked_points) > 0:
                first = self.clicked_points[0]
                if abs(x - first[0]) < 10 and abs(y - first[1]) < 10:
                    self.selected = True
                    self.repaint()
                    return

            self.clicked_points.append((x, y))
            self.repaint()

    def initUI(self,):
        self.setGeometry(150, 150, 1280, 720)

        self.setWindowTitle('Drawing')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.setPen(Qt.black)
        qp.begin(self)

        self.draw(qp)

        qp.end()

    def fill_polygon(self, qp, q_polygon, color=Qt.darkCyan):
        qp.setBrush(color)
        qp.drawPolygon(q_polygon)

    def draw_choice(self, qp):
        if self.selected:
            qp.setPen(Qt.green)
        else:
            qp.setPen(Qt.red)
        first = None
        prev_p = None
        for point in self.clicked_points:
            if prev_p is None:
                prev_p = point
                first = point
                qp.drawPoint(*point)
            else:
                qp.drawLine(*prev_p, *point)
                prev_p = point

        if self.selected:
            qp.drawLine(*prev_p, *first)

    def draw(self, qp):
        if not self.polygon:
            self.draw_choice(qp)

            return

        initial_polygon = self.polygon
        lines = get_lines(initial_polygon)
        visible_polygon = initial_polygon

        print('initial polygon', initial_polygon)
        for line in lines:
            extended_polygon = slice_with_line(visible_polygon, line)
            visible_polygon = delete_not_visible(extended_polygon, line)
            print('line', line)
            print('polygon', visible_polygon)
            print('#################')

        self.fill_polygon(qp, get_q_polygon(visible_polygon))
        self.draw_choice(qp)


def get_eps(polygon, line):
    sum_ = 0
    count = 0
    line_v = (line[1][0] - line[0][0], line[1][1] - line[0][1])
    for point in polygon:
        vector = (point[0] - line[0][0], point[1] - line[0][1])
        cross_pr = cross_product(line_v, vector)
        sum_ += abs(cross_pr)
        count += 1

    if count == 0:
        return 0

    return sum_ / (count * 16)


def cross_product(v1, v2):
    return v1[0] * v2[1] - v2[0] * v1[1]


def delete_not_visible(polygon, line):
    new_polygon = []
    line_v = (line[1][0] - line[0][0], line[1][1] - line[0][1])
    eps = get_eps(polygon, line)
    print(eps)
    for point in polygon:
        vector = (point[0] - line[0][0], point[1] - line[0][1])
        cross_pr = cross_product(line_v, vector)
        if cross_pr <= eps:  # todo: trouble #1
            new_polygon.append(point)

    return new_polygon


def slice_with_line(polygon, line):
    rotated_polygon = rotate_polygon(polygon, line[0])
    new_polygon = []
    out_of_polygon = False
    for line_p in line:
        if line_p in polygon:
            new_polygon.append(line_p)
            out_of_polygon = True

    if out_of_polygon:
        new_polygon = []

    lines = get_lines(rotated_polygon)
    i = 0
    while i < len(lines):
        cur_line = lines[i]
        start, end = cur_line

        new_polygon.append(start)

        intersection_point = get_intersection_point(line, cur_line)
        if intersection_point and intersection_point != start and intersection_point != end:
            new_polygon.append(intersection_point)

        new_polygon.append(end)

        i += 1

    return minify_polygon(new_polygon)


def minify_polygon(polygon):
    distinct_points = []
    for point in polygon:
        if point in distinct_points:
            continue
        distinct_points.append(point)

    return distinct_points


def rotate_polygon(polygon, vertex):
    if vertex not in polygon:
        return polygon
    # возвращает многоугольник, у которого первая вершина - vertex
    new_polygon = []
    prev_verts = []
    i = 0
    while polygon[i] != vertex:
        prev_verts.append(polygon[i])
        i += 1

    while i < len(polygon):
        new_polygon.append(polygon[i])
        i += 1

    new_polygon = new_polygon + prev_verts

    return new_polygon


def get_q_polygon(polygon):
    q_points = [QPointF(*point) for point in polygon]
    return QPolygonF(q_points)


def get_lines(polygon):
    lines = []
    prev = None
    first = None
    for vertex in polygon:
        if prev is None:
            prev = first = vertex
            continue
        lines.append((prev, vertex))
        prev = vertex

    lines.append((prev, first))
    if len(lines) <= 1:
        return []
    return lines


def get_intersection_point(line1, line2):
    def line(p1, p2):
        A = (p1[1] - p2[1])
        B = (p2[0] - p1[0])
        C = (p1[0] * p2[1] - p2[0] * p1[1])
        return A, B, -C

    l1_eq = line(*line1)
    l2_eq = line(*line2)

    D  = l1_eq[0] * l2_eq[1] - l1_eq[1] * l2_eq[0]
    Dx = l1_eq[2] * l2_eq[1] - l1_eq[1] * l2_eq[2]
    Dy = l1_eq[0] * l2_eq[2] - l1_eq[2] * l2_eq[0]
    if D != 0:
        x = (Dx / D)  # todo: trouble #2
        y = (Dy / D)  # todo: trouble #2
        if is_on_interval(line2, (x, y)):
            return x, y

        return False
    return False


def is_on_interval(interval, point):
    x, y = point
    x_0, y_0 = interval[0]
    x_1, y_1 = interval[1]

    on_x = (x_0 <= x <= x_1) or (x_1 <= x <= x_0)
    on_y = (y_0 <= y <= y_1) or (y_1 <= y <= y_0)

    return on_x and on_y


def my_exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':

    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook
    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook
    app = QApplication(sys.argv)
    # ex = DrawingWidget([(0, 0), (0, 100), (150, 100), (150, 70), (30, 70), (30, 50), (100, 50), (100, 0)])
    # ex = DrawingWidget([(0, 0), (0, 100), (150, 100), (150, 70), (30, 70), (30, 0)])
    # ex = DrawingWidget([(0, 0), (0, 100), (50, 100), (45, 70), (100, 70), (115, 0)])
    # ex = DrawingWidget([(0, 0), (50, 100), (200, 200), (100, 0), (75, 20)])
    # ex = DrawingWidget([(366, 364), (474, 290), (545, 390), (614, 130), (382, 114)])
    # ex = DrawingWidget([(156, 117), (161, 320), (362, 318), (365, 219), (233, 217), (234, 140), (384, 149), (349, 80)])
    ex = DrawingWidget()
    sys.exit(app.exec_())
