import math, time,random

def project_3d_to_2d(x, y, z, scale=80, distance=5):
    factor = distance / (distance + z)
    return x * factor * scale, y * factor * scale

class Point3D:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, -z, y

    def project(self, scale=100, distance=5):
        return project_3d_to_2d(self.x, self.y, self.z, scale, distance)

vertices_cube = [
    Point3D(-1, -1, -1),  # 0
    Point3D(1, -1, -1),   # 1
    Point3D(1, 1, -1),    # 2
    Point3D(-1, 1, -1),   # 3
    Point3D(-1, -1, 1),   # 4
    Point3D(1, -1, 1),    # 5
    Point3D(1, 1, 1),     # 6
    Point3D(-1, 1, 1)     # 7
]

verticesП = [
    # внешний каркас
    Point3D(-2,-2,-2), # 0
    Point3D(2,-2,-2),
    Point3D(2,2,-2),
    Point3D(-2,2,-2),

    Point3D(-2,-2,2), # 4
    Point3D(2, -2, 2),
    Point3D(2, 2, 2),
    Point3D(-2, 2, 2),
    # для П
    Point3D(-2,-1,-2), # 8
    Point3D(2,-1,-2),
    Point3D(2,1,-2),
    Point3D(-2,1,-2),
    # для П
    Point3D(-2,-1,1.2), # 12
    Point3D(2, -1, 1.2),
    Point3D(2, 1, 1.2),
    Point3D(-2, 1, 1.2)
]

vertices = [
    # внешний каркас
    Point3D(-2,-2,-2), # 0
    Point3D(2,-2,-2),
    Point3D(2,2,-2),
    Point3D(-2,2,-2),

    Point3D(-2,-2,2), # 4
    Point3D(2, -2, 2),
    Point3D(2, 2, 2),
    Point3D(-2, 2, 2),
    # для лева
    Point3D(-2,-1,-2), # 8
    Point3D(2,-1,-2),
    Point3D(2,1,-2),
    Point3D(-2,1,-2),
    # для права
    Point3D(-2,-1,1.2), # 12
    Point3D(2, -1, 1.2),
    Point3D(2, 1, 1.2),
    Point3D(-2, 1, 1.2),
    # нижние соединения
    Point3D(-2,0,0.4), #16
    Point3D(2,0,0.4),
    # верхние соединения
    Point3D(-2,0,1.2), #18
    Point3D(2,0,1.2)
]

edgesП = [
    (0, 1), (1, 9), (9, 8), (8, 0),  # Нижняя грань 1
    (2, 10), (10, 11), (11, 3), (3, 2),  # Нижняя грань 2
    (4, 5), (5, 6), (6, 7), (7, 4),  # Верхняя грань 1
    (12, 13), (13, 14), (14, 15), (15, 12),  # Нижняя грань 1
    (0, 4), (1, 5), (2, 6), (3, 7),   # Вертикальные рёбра 1
    (8, 12), (9, 13), (10, 14), (11,15)   # Вертикальные рёбра 2
]

edges = [
    (0, 1), (1, 9), (9, 8), (8, 0),  # Нижняя грань 1
    (2, 10), (10, 11), (11, 3), (3, 2),  # Нижняя грань 2
    (7, 6), (6, 19), (19, 18), (18, 7),  # Верхняя угловая грань 1
    (4, 5), (5, 19), (19, 18), (18, 4),  # Верхняя угловая грань 2
    (12, 13), (13, 17), (17, 16), (16, 12),  # Нижняя угловая грань 1
    (15, 14), (14, 17), (17, 16), (16, 15),  # Нижняя угловая грань 2
    (0, 4), (1, 5), (2, 6), (3, 7),  # Вертикальные рёбра 1
    (8, 12), (9, 13), (10, 14), (11, 15)  # Вертикальные рёбра 2
]

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout, QMessageBox)
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPoint, QTimer


class CubeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Cube Wireframe")
        self.resize(700, 800)
        self.angle_x, self.angle_y, self.angle_z = 0, 0, 0

        self.angle_a = 0
        self.angle_b = 0
        self.angle_c = 0
        print(self.angle_a,self.angle_b)
        layout = QVBoxLayout()
        btn_xz = QPushButton("рандом")
        btn_xz.clicked.connect(self.rotate_cube(
            self.angle_x+self.angle_a,
            self.angle_y+self.angle_b,
            self.angle_z+self.angle_c
        ))

        layout.addWidget(btn_xz)

        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.blue, 2))

        center = QPoint(self.width() // 2, self.height() // 2)

        # рёбра
        golden_frieza = 0
        for edge in edges:
            p1 = self.project(vertices[edge[0]])
            p2 = self.project(vertices[edge[1]])
            # print(f"p1={p1}, p2={p2}")
            painter.drawLine(
                center.x() + p1[0], center.y() + p1[1],
                center.x() + p2[0], center.y() + p2[1]
            )
        # подписи для точек
        for point in vertices:
            p1 = self.project(point)
            painter.drawText(center.x() + p1[0], center.y() + p1[1],
                             str((point.x,point.z,-point.y))+" "+str(golden_frieza)+" "+str((round(p1[0],1),round(p1[1],1))))
            golden_frieza+=1

    def rotate_cube(self, angle_x, angle_y, angle_z):
        self.angle_x = angle_x
        self.angle_y = angle_y
        self.angle_z = angle_z
        # print(f"angle_x={self.angle_x}, angle_y={self.angle_y}")
        self.update()

    def project(self, point):
        # Простая реализация вращения вокруг осей X и Y
        x, y, z = point.x, point.y, point.z

        # Вращение вокруг оси X
        new_x = x
        new_y = y * math.cos(self.angle_x) + z * math.sin(self.angle_x)
        new_z = - y * math.sin(self.angle_x) + z * math.cos(self.angle_x)
        x, y, z = new_x, new_y, new_z

        # Вращение вокруг оси Y
        new_x = x * math.cos(self.angle_y) + z * math.sin(self.angle_y)
        new_y = y
        new_z = - x * math.sin(self.angle_y) + z * math.cos(self.angle_y)
        x, y, z = new_x, new_y, new_z

        # Вращение вокруг оси Z
        new_x = x * math.cos(self.angle_z) + y * math.sin(self.angle_z)
        new_y = - x * math.sin(self.angle_z) + y * math.cos(self.angle_z)
        new_z = z
        x, y, z = new_x, new_y, new_z

        return project_3d_to_2d(x, y, z)


if __name__ == "__main__":
    app = QApplication([])
    widget = CubeWidget()
    widget.show()

    stopper = 0

    # Анимация вращения (пример)
    def update_rotation():
        global stopper
        widget.rotate_cube(widget.angle_x + 0.00,
                           widget.angle_y + 0.01,
                           widget.angle_z + 0.00)
        stopper+=1
        print(stopper)
        if stopper == 1000:
            timer.stop()
            stopper = 0
            time.sleep(5)
            timer.start(10)
        return

    timer = QTimer()
    timer.timeout.connect(update_rotation)

    timer.start(10)


    app.exec()