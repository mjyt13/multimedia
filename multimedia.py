import sys
import math
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout)
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPointF

COLOR_PALETTE = [
    QColor("blue"),  # Синий
    QColor("orange"),  # Оранжевый
    QColor("green"),  # Зелёный
    QColor("red"),  # Красный
    QColor("purple"),  # Фиолетовый
    QColor("brown"),  # Коричневый
    QColor("magenta"),  # Пурпурный
    QColor("darken")  # Темно-циановый
]

class PlotWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.functions = [] # создать список функций, фигурирующих
        self.color_index = 0

    # сама отрисовка
    def paintEvent(self,event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_grid(painter)
        self.draw_axes(painter)
        for func, color, label in self.functions:
            self.draw_curve(painter, func, color, label)

        self.draw_legend(painter)

    def draw_axes(self, painter):
        # Рисует оси координат и подписи к ним.
        width, height = self.width(), self.height()  # Получаем размеры виджета.
        center_x, center_y = width // 2, height // 2  # Вычисляем центр виджета.
        scale_x, scale_y = 20, 20  # Масштаб для осей (1 единица = 20 пикселей).

        # Рисуем оси
        painter.setPen(QPen(Qt.white, 2))  # Устанавливаем черный цвет и толщину линии.
        painter.drawLine(0, center_y, width, center_y)  # Ось X.
        painter.drawLine(center_x, 0, center_x, height)  # Ось Y.

        # Подписи осей
        painter.drawText(width - 20, center_y - 5, "X")  # Подпись оси X.
        painter.drawText(center_x + 5, 20, "Y")  # Подпись оси Y.

        # Подписи масштаба для оси X
        for x in range(-10, 11, 2):  # Перебор значений по оси X.
            px = center_x + x * scale_x  # Вычисление координаты X.
            painter.drawText(px - 10, center_y + 20, f"{x}")  # Подпись значения.

        # Подписи масштаба для оси Y
        for y in range(-10, 11, 2):  # Перебор значений по оси Y.
            py = center_y - y * scale_y  # Вычисление координаты Y.
            painter.drawText(center_x + 10, py + 5, f"{y}")  # Подпись значения.

    def draw_grid(self,painter):
        width, height = self.width(), self.height()  # Получаем размеры виджета.
        center_x, center_y = width // 2, height // 2  # Вычисляем центр виджета.
        scale_x, scale_y = 20, 20  # Масштаб для осей (1 единица = 20 пикселей).

        painter.setPen(QPen(QColor(200,200,200),1.5,Qt.DotLine))

        for x in range(-10,11):
            px = center_x + x * scale_x
            painter.drawLine(px,0,px,height)

        for y in range(-10,11):
            py = center_y - y * scale_y
            painter.drawLine(0,py,width,py)

    def draw_curve(self, painter, func, color, label):
        # Рисует график функции.
        width, height = self.width(), self.height()  # Получаем размеры виджета.
        center_x, center_y = width // 2, height // 2  # Вычисляем центр виджета.
        scale_x, scale_y = 20, 20  # Масштаб для осей.

        painter.setPen(QPen(color, 2))  # Устанавливаем цвет и толщину линии.
        points = []  # Список для хранения точек графика.

        for x in range(-100, 101):  # Перебор значений X с шагом 0.1.
            try:
                x_val = x / 10  # Преобразуем X в дробное значение.
                y = func(x_val)  # Вычисляем Y для текущего X.
                px = center_x + x_val * scale_x  # Вычисляем координату X на виджете.
                py = center_y - y * scale_y  # Вычисляем координату Y на виджете.
                points.append(QPointF(px, py))  # Добавляем точку в список.
            except:
                continue  # Пропускаем ошибки (например, деление на ноль).

        # Рисуем линию по точкам
        for i in range(len(points) - 1):  # Перебор точек.
            painter.drawLine(points[i], points[i + 1])

    def draw_legend(self, painter):
        # Рисует легенду с описанием функций.
        painter.setPen(QPen(Qt.white, 1))  # Устанавливаем белый цвет для текста.
        painter.drawText(20, 30, "Легенда:")  # Заголовок легенды.
        y_offset = 50  # Начальное смещение по Y.

        for func, color, label in self.functions:  # Перебор всех функций.
            painter.setPen(QPen(color, 2))  # Устанавливаем цвет функции.
            painter.drawText(20, y_offset, label)  # Рисуем метку функции.
            y_offset += 20  # Увеличиваем смещение для следующей метки.

    def add_function(self, func, color, label):
        # Добавляет функцию в список для отрисовки.
        self.functions.append((func, color, label))  # Добавляем кортеж (функция, цвет, метка).
        self.update()  # Обновляем виджет для перерисовки.

    def clear_functions(self):
        # Очищает список функций.
        self.functions.clear()  # Очищаем список.
        self.color_index = 0  # Сбрасываем индекс цвета.
        self.update()  # Обновляем виджет.

    def get_next_color(self):
        # Возвращает следующий цвет из палитры.
        color = COLOR_PALETTE[self.color_index % len(COLOR_PALETTE)]  # Получаем цвет по индексу.
        self.color_index += 1  # Увеличиваем индекс.
        return color  # Возвращаем цвет.


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графический анализатор")
        self.setMinimumSize(800, 600)

        widget = QWidget()
        self.setCentralWidget(widget)

        # Prikoli (Vertical)
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.plotter = PlotWidget()
        layout.addWidget(self.plotter)

        # Upravlenie (Horizontal)
        control_layout = QHBoxLayout()

        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("Жежда(x**2)")
        control_layout.addWidget(self.function_input)

        bnt_add = QPushButton("НА ХУЙ (draw)")
        bnt_add.clicked.connect(self.plotter.clear_functions)
        control_layout.addWidget(bnt_add)

        bnt_add2 = QPushButton("НА ХУЙ 2 (add)")
        bnt_add.clicked.connect(self.add_function)
        control_layout.addWidget(bnt_add2)

        layout.addLayout(control_layout)

    def add_function(self):
        # Добавляет функцию в виджет для отрисовки.
        try:
            expr = self.function_input.text()  # Получаем текст из поля ввода.
            func = lambda x, e=expr: eval(e, {"math": math, "x": x})  # Создаем лямбда-функцию.
            color = self.plotter.get_next_color()  # Получаем следующий цвет.
            self.plotter.add_function(func, color, f"y = {expr}")  # Добавляем функцию в виджет.
            self.function_input.clear()  # Очищаем поле ввода.
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())