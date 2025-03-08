import sys
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QDoubleSpinBox, QLabel, QPushButton,
                               QHBoxLayout, QLineEdit)
from PySide6.QtGui import QPainter, QPen, QBrush, QFont
from PySide6.QtCore import Qt, QPointF

class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.x_min = -10.0
        self.x_max = 10.0
        self.y_min = self.x_min
        self.y_max = self.x_max
        self.step = 1.0
        self.available_functions = {
            "1": (lambda x: x, Qt.blue),         # f(x) = x
            "2": (lambda x: x ** 2, Qt.green),     # f(x) = x^2
            "3": (lambda x: 1 / x if x != 0 else None, Qt.red)  # f(x) = 1/x
        }
        self.function_formulas = {
            "1": "f(x) = x",
            "2": "f(x) = x²",
            "3": "f(x) = 1/x"
        }
        self.selected_functions = []  # Список выбранных функций

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width, height = self.width(), self.height()
        center_x, center_y = width // 2, height // 2
        grid_step = min(width, height) / (((self.x_max - self.x_min) / self.step) * 2)

        painter.fillRect(self.rect(), QBrush(Qt.white))

        # Рисуем сетку
        pen = QPen(Qt.lightGray, 1, Qt.DashLine)
        painter.setPen(pen)

        i = self.x_min
        while i <= self.x_max:
            x = center_x + i * grid_step
            painter.drawLine(x, 0, x, height)
            painter.drawLine(0, center_y - i * grid_step, width, center_y - i * grid_step)
            i += self.step

        # Рисуем оси
        pen.setColor(Qt.black)
        pen.setWidth(2)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(0, center_y, width, center_y)
        painter.drawLine(center_x, 0, center_x, height)

        # Подписи осей
        font = QFont()
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(width - 30, center_y - 5, "X")
        painter.drawText(center_x + 10, 15, "Y")

        # Подписи меток на осях
        font.setPointSize(10)
        painter.setFont(font)
        i = self.x_min + self.step
        while i <= self.x_max:
            x = center_x + i * grid_step
            y = center_y - i * grid_step
            if i != 0:
                painter.drawText(x - 15, center_y + 20, f"{i:.2f}")
                painter.drawText(center_x - 40, y + 5, f"{i:.2f}")
            i += self.step

        # Рисуем выбранные функции
        pen.setWidth(2)
        for key in self.selected_functions:
            if key in self.available_functions:
                func, color = self.available_functions[key]
                pen.setColor(color)
                painter.setPen(pen)
                self.draw_function(painter, func, center_x, center_y, grid_step)

        # Рисуем легенду
        self.draw_legend(painter, width, height)

    def draw_function(self, painter, func, cx, cy, scale):
        bar_width = scale * self.step * 0.8  # Ширина столбцов
        # Используем текущий цвет пера и делаем его светлее для заливки
        color = painter.pen().color()
        brush_color = color.lighter(150)
        painter.setBrush(QBrush(brush_color, Qt.SolidPattern))

        for i in np.arange(self.x_min, self.x_max, self.step):
            y = func(i)
            if y is not None and self.y_min <= y <= self.y_max:
                px = cx + i * scale
                py = cy - y * scale

                # Определяем положение верхней и нижней границы цилиндра
                if y >= 0:
                    bar_top = py  # Верхняя точка цилиндра
                    bar_bottom = cy  # Базовая линия графика
                else:
                    bar_top = cy
                    bar_bottom = py

                rect_y = min(bar_top, bar_bottom)
                rect_height = abs(bar_bottom - bar_top)
                # Рисуем прямоугольное тело цилиндра
                painter.drawRect(px - bar_width/2, rect_y, bar_width, rect_height)

                # Рисуем эллиптические окончания цилиндра
                ellipse_height = bar_width / 8  # регулировка эллиптичности
                painter.drawEllipse(QPointF(px, bar_top), bar_width/2, ellipse_height)
                painter.drawEllipse(QPointF(px, bar_bottom), bar_width/2, ellipse_height)

    def draw_legend(self, painter, width, height):
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)

        legend_x = width - 150
        legend_y = 30
        line_height = 20

        for key in self.selected_functions:
            if key in self.function_formulas:
                formula = self.function_formulas[key]
                painter.setPen(QPen(self.available_functions[key][1]))
                painter.drawText(legend_x, legend_y, f"{key}: {formula}")
                legend_y += line_height

    def update_settings(self, x_min, x_max, step, selected_functions):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = x_min
        self.y_max = x_max
        self.step = step
        self.selected_functions = selected_functions
        self.update()

class SettingsWindow(QWidget):
    def __init__(self, plot_widget):
        super().__init__()
        self.setWindowTitle("Настройки")
        layout = QVBoxLayout()

        self.x_min_spin = QDoubleSpinBox()
        self.x_min_spin.setRange(-1000.0, 1000.0)
        self.x_min_spin.setValue(plot_widget.x_min)
        self.x_min_spin.valueChanged.connect(self.update_plot)

        self.x_max_spin = QDoubleSpinBox()
        self.x_max_spin.setRange(-1000.0, 1000.0)
        self.x_max_spin.setValue(plot_widget.x_max)
        self.x_max_spin.valueChanged.connect(self.update_plot)

        self.step_spin = QDoubleSpinBox()
        self.step_spin.setRange(0.1, 10.0)
        self.step_spin.setValue(plot_widget.step)
        self.step_spin.valueChanged.connect(self.update_plot)

        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("Введите номера функций, например: 1,2,3")
        self.function_input.textChanged.connect(self.update_plot)

        layout.addWidget(QLabel("X min:"))
        layout.addWidget(self.x_min_spin)
        layout.addWidget(QLabel("X max:"))
        layout.addWidget(self.x_max_spin)
        layout.addWidget(QLabel("Step:"))
        layout.addWidget(self.step_spin)
        layout.addWidget(QLabel("Функции:"))
        layout.addWidget(self.function_input)
        self.setLayout(layout)

        self.plot_widget = plot_widget

    def update_plot(self):
        selected_functions = [f.strip() for f in self.function_input.text().split(",") if
                              f.strip() in self.plot_widget.available_functions]
        self.plot_widget.update_settings(self.x_min_spin.value(), self.x_max_spin.value(), self.step_spin.value(),
                                         selected_functions)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графики функций")
        self.setGeometry(100, 100, 900, 700)

        self.plot_widget = PlotWidget()
        self.settings_window = SettingsWindow(self.plot_widget)

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)

        settings_button = QPushButton("Настройки")
        settings_button.clicked.connect(self.settings_window.show)
        layout.addWidget(settings_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())







