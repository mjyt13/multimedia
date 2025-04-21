import sys  # Импорт модуля sys для работы с системными функциями (например, завершение программы).
import math  # Импорт модуля math для математических операций (sin, cos, sqrt и т.д.).
import numpy as np

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout, QMessageBox)
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QBrush  # Импорт классов для рисования и работы с цветами.
from PySide6.QtCore import Qt, QPointF  # Импорт базовых классов (флаги, точки и т.д.).

# Предопределённая палитра цветов для графиков
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

class ConesDataBase:
    """Это так называемый бэк..."""
    functions = None
    """ Тут делаются жилмассивы точек функций из списка"""
    # a - начало интервала
    # b - конец интервала
    # n - количество точек
    def function_points(self,a, b, n):
        fvalues = []
        for function in self.functions:
            expr = function
            func = lambda x, e=expr: eval(e, {"math": math, "x": x})
            values = []
            np_args = np.linspace(a, b, num=n)
            args = np_args.tolist()
            for i in args:
                try:
                    if func(i) < 1e6:
                        values.append((i, func(i)))
                    else:
                        values.append((i,0))
                except:
                    values.append((i, 0))
            fvalues.append(values.copy())
            values.clear()
        return fvalues

    def define_data(self,used_points):
        x = [];y_pos = [];y_neg = []
        for func_points in used_points:
            for i in range(0, len(func_points)):
                if i == len(x):
                    x.append(func_points[i][0])
                if i == len(y_neg):  # нет нужды проверять оба списка
                    y_pos.append(0)
                    y_neg.append(0)
                if func_points[i][1] > 0:
                    y_pos[i] += func_points[i][1]
                if func_points[i][1] < 0:
                    y_neg[i] += func_points[i][1]
        return x, y_pos, y_neg

    # функция, что даёт данные не в виде (функция: арг1, арг2,...), а в виде(арг: ф1, ф2,...)
    def graph_points(self,a, b, n):
        fvalues = []
        np_args = np.linspace(a, b, num=n)
        args = np_args.tolist()
        for i in args:
            values = []
            for function in self.functions:
                expr = function
                func = lambda x, e=expr: eval(e, {"math": math, "x": x})
                try:
                    if func(i) < 1e6:
                        values.append((i, func(i)))
                    else:
                        values.append((i,0))
                except:
                    values.append((i, 0))
            fvalues.append(values.copy())
            values.clear()
        return fvalues

    # эта функция для изначального списка точек, который просто имеет другой вид
    def define_graph(self,used_points):
        cones = []
        try:
            for points in used_points:
                cones_height = []
                sum_neg = 0
                sum_pos = 0
                for point in points:
                    cones_height.append(point[1])
                    if point[1] >= 0:
                        sum_pos += point[1]
                    else:
                        sum_neg += point[1]
                cones.append((points[0][0], cones_height, sum_pos, sum_neg))
        finally:
            return cones

    # вот эта функция нужна для преобразования точек в define_graph
    def define_cones(self,points):
        cones_data = []
        # сколько цифр после запятой
        digits_number = 3
        for group in points:
            arg = group[0]
            sum_pos = group[2]
            sum_neg = group[3]
            dots = group[1]
            cone_data = []
            for i in range(len(dots)):
                if dots[i] >= 0:
                    cone_height = sum_pos
                else:
                    cone_height = sum_neg
                height = 0
                radius = 0.5
                if cone_height != 0:
                    ratio = radius / cone_height
                else:
                    ratio = 1
                for j in range(i):
                    if dots[i] >= 0 and dots[j] >= 0:
                        height += dots[j]
                        cone_height -= dots[j]
                    if dots[i] < 0 and dots[j] < 0:
                        height += dots[j]
                        cone_height -= dots[j]
                radius = round(ratio * cone_height, digits_number)
                cone_data.append((round(height, digits_number), round(cone_height, digits_number), radius))
            cones_data.append((arg, cone_data))
        return cones_data

    def __init__(self):
        self.functions = []
        self.used_functions = ['-x/5','x','math.exp(-x**2+math.cos(x))','1/x','math.sin(x)','math.log2(x)',
                               'math.atan(math.exp(x)+7*x)','(math.sin(x))/x','math.cosh(-0.5*x**3+math.log10(x))']
    def setfunctions(self,funcs):
        self.functions = funcs.copy()

class PlotWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)  # Инициализация родительского класса QWidget.
        self.scale_x, self.scale_y = None, None
        self.vert_lines = 9
        print(self.width(),self.height())
        self.cones_db = ConesDataBase()
        self.functions = []  # Список для хранения функций
        self.color_index = 0  # Индекс для перебора цветов из палитры

        self.funcs = None
        self.masses = None
        self.arg_funcs = None
        self.cones_params = None
        self.cones = None
        self.cell_height = 15
        self.cell_width = 20
        self.razmetka = 16

    def update_data(self,functions,a,b,n):
        # считать функции
        self.functions = functions
        # к логике дать эти функции
        self.cones_db.setfunctions(functions)
        # определить оси и сетку
        self.funcs = self.cones_db.function_points(a, b, n)
        for func in self.funcs:
            print(func)
        self.masses = self.cones_db.define_data(self.funcs)
        print(self.masses)
        # определить размеры конусов и их положение
        self.arg_funcs = self.cones_db.graph_points(a, b, n)
        self.cones_params = self.cones_db.define_graph(self.arg_funcs)
        # for cone_params in self.cones_params:
        #     print(cone_params)
        self.cones = self.cones_db.define_cones(self.cones_params)
        for cone_data in self.cones:
            print(cone_data)

        # установить границы рисования
        print(f"for cells' height {(min(self.masses[0]))} -> {max(self.masses[0])}")
        self.cell_height  = n + 1 # высота в клетках
        self.cell_width = self.vert_lines + 1  # ширина в клетках
        # со вторым сложнее

        # новые штуки: специальный масштаб
        # надо посмотреть по разнице между образцами, сколько пикселей будет для сетки, осей
        self.scale_x = 480 / self.cell_height
        self.scale_y = 640 / self.cell_width

        print("parental", self.width(),self.height())
        print("cells width ",self.cell_width,", cells height",self.cell_height)
        print("scales ",self.scale_y,self.scale_x)
        self.update()

    def paintEvent(self, event):
        # Метод, вызываемый при перерисовке виджета.
        painter = QPainter(self)  # Создание объекта QPainter для рисования.
        painter.setRenderHint(QPainter.Antialiasing) # Сглаживание
        if len(self.functions)>0:
            try:
                self.draw_grid(painter)
            except:
                QMessageBox.warning(self, "уэуэу??", "сетка упала")
            try:
                self.draw_cones(painter, self.cones)
                print("KONUSI V PORYADE")
            except:
                QMessageBox.warning(self,"эуэуэ? конусы","конусы упали")
            try:
                self.draw_axes(painter)
            except:
                QMessageBox.warning(self,"дзэйз","оси упали")
            self.draw_legend(painter, self.cones)

    def crosses_line (self):
        minw = min(min(self.masses[2]), 0)
        maxw = max(max(self.masses[1]), 0)

        npcells_y = np.linspace(minw,maxw,num=self.vert_lines)
        cross_y = ((0-minw)/(maxw-minw)) * (640-2*self.scale_y) + self.scale_y

        return cross_y

    def draw_axes(self, painter):
        scale_x, scale_y = self.scale_x, self.scale_y  # Масштаб для осей
        w_width, w_height = self.cell_width * scale_y, self.cell_height * scale_x  # размеры виджета

        crosses = self.crosses_line()

        minw = min(min(self.masses[2]), 0)
        maxw = max(max(self.masses[1]), 0)
        used_width = 640 - 2 * scale_y

        minh = min(self.masses[0]) # a
        maxh = max(self.masses[0]) # b
        used_height = w_height - 1 * scale_x

        cross_y = crosses
        print(f"линия нулевая{cross_y}")

        painter.setPen(QPen(Qt.black, 2))  # Устанавливаем черный цвет и толщину линии.
        painter.drawLine(cross_y, 0, cross_y, 480)  # Ось X.

        print(f"height is {used_height}, all height is = {w_height}")
        # Подписи масштаба для оси Y
        # Сделать условие на проверку минимума (он больше 0 - ставим 0, меньше - оставляем)
        nps_y = np.linspace(minw, maxw, num=self.vert_lines)
        cells_y = nps_y.tolist()

        ys = []; xs=[]
        for i in range(len(cells_y)):
            py = scale_y * (1+i)
            y = cells_y[i]
            ys.append((y,py))
            painter.drawText(py-7, 490, f"{round(y, 2)}")

        # Подписи масштаба для оси X (на самом деле начинать нужно со значения 2, ибо 0 отведен для доп. клетки)
        cell_scale_x = len(self.masses[0]) # сколько клеток подписано
        npx_s = np.linspace(minh,maxh,num=cell_scale_x)
        x_s = npx_s.tolist()
        for i in range(len(x_s)):
            px = used_height - scale_x*i
            x = x_s[i]
            xs.append((x, px))
            painter.drawText(650, px + 3, f"{round(x, 2)}")

        print(xs)

    def draw_grid(self, painter):
        # сетка
        scale_x, scale_y = self.scale_x, self.scale_y  # Масштаб для осей
        print(f"GRID: scale_x={scale_x}, scale_y={scale_y}")
        if scale_y < self.razmetka:
            scale_y = self.razmetka
        if scale_x < self.razmetka:
            scale_x = self.razmetka
        w_width, w_height = 640,480

        # painter.setPen(QPen(Qt.gray, 2))
        painter.setPen(QPen(Qt.gray, 1.5, Qt.DotLine))
        px = 0
        print(f"px {scale_y} is here I HATE NI")
        while px<=640:
            painter.drawLine(px, 0, px, w_height)
            px += scale_y

        py = 0
        print(f"py {scale_x} is here I HATE NI")
        while py<=480:
            painter.drawLine(0, py, w_width, py)
            py += scale_x

        painter.setPen(QPen(Qt.black, 1.5,Qt.SolidLine))
        painter.drawLine(640, 0, 640, 480)
        painter.drawLine(0, 480, 640, 480)
        painter.drawLine(0, 0, 0, 480)
        painter.drawLine(0, 0, 640, 0)

    def draw_cones(self,painter,cones_data):
        scale_x, scale_y = self.scale_x, self.scale_y

        crosses = self.crosses_line()
        cross_y = crosses

        minw_minus = min(min(self.masses[2]), 0)
        maxw_minus = 0
        maxw_plus = max(max(self.masses[1]), 0)
        minw_plus = 0

        used_height = 480 - 1 * scale_x
        curve_scale = 30

        # будет здесь отрисовка конусов
        for i in range (len(cones_data)):
            cones = cones_data[i]
            x = cones[0] # это аргумент в значении
            px = used_height - i * scale_x # это аргумент в пикселях
            color_num = 0
            # часть сугубо на проверку наличия конуса с положительным значением + учитывание прикола с отрицательным
            first_below_zero = True
            is_there_above_zero = False
            for cone in cones[1]:
                height = cone[0]
                cone_height = cone[1]
                if height+cone_height > 0:
                    is_there_above_zero = True

            # пошла отрисовка
            for cone in cones[1]:
                color = COLOR_PALETTE[color_num % len(COLOR_PALETTE)]
                painter.setPen(QPen(color, 1))

                # не могу так, надо вынести параметры
                height = cone[0]; cone_height = cone[1]; radius = cone[2]
                # это какой-то прикол
                direction = 1 if (height + cone_height) > 0 else -1

                y_h = height
                y_ch = height+cone_height
                if direction < 0:
                    try:
                        h = ((y_h-maxw_minus)/(minw_minus-maxw_minus)) * (cross_y-scale_y) * direction
                        ch = ((y_ch-maxw_minus)/(minw_minus-maxw_minus)) * (cross_y-scale_y) * direction
                    except:
                        print(f"v minuse na y_h={y_h} ili y_ch={y_ch} naebulsya")
                        h = 0; ch = 0
                else:
                    try:
                        h = ((y_h-minw_plus)/(maxw_plus-minw_plus)) * (640-scale_y-cross_y)
                        ch = ((y_ch-minw_plus)/(maxw_plus-minw_plus)) * (640-scale_y-cross_y)
                    except:
                        print(f"v pluse na y_h={y_h} ili y_ch={y_ch} naebulsya")
                        h = 0; ch = 0
                print(f"ch={ch}, h={h}")
                apex_y = cross_y + ch
                apex_x = px

                base_center_y = cross_y + h
                base_left_x = px - radius * scale_x
                base_right_x = px + radius * scale_x
                control_y = base_center_y + radius * direction * curve_scale
                # я молдаван, ещё ж основание осталось
                path = QPainterPath()
                path.moveTo(apex_y,apex_x)
                path.lineTo(base_center_y,base_left_x)
                path.quadTo(control_y,px,
                            base_center_y,base_right_x)
                path.closeSubpath()

                brush = QBrush(color)
                painter.fillPath(path, brush)

                painter.setPen(QPen(Qt.black,1))
                painter.drawLine(apex_y,apex_x,base_center_y,base_left_x)
                painter.drawLine(apex_y,apex_x,base_center_y,base_right_x)

                # painter.drawLine(base_center_y,base_left_x,base_center_y,base_right_x)
                if cone_height < 0:
                    painter.drawPath(path)
                if cone_height >= 0 or (first_below_zero and not is_there_above_zero):
                    control_y_neg = base_center_y + radius * direction * (-curve_scale)
                    painter.setPen(QPen(color, 1))
                    # стереть черту основания конуса
                    path = QPainterPath()
                    path.moveTo(base_center_y, base_left_x)
                    path.quadTo(control_y,px,
                                base_center_y,base_left_x)
                    painter.drawPath(path)
                    # для основания(корыта) - цвет

                    path = QPainterPath()
                    path.moveTo(base_center_y,base_left_x)
                    path.quadTo(control_y, px,
                                base_center_y, base_right_x)
                    path.quadTo(control_y_neg,px,
                                base_center_y,base_left_x)
                    path.closeSubpath()
                    painter.fillPath(path,brush)

                    # черты для основания конуса
                    path = QPainterPath()
                    path.moveTo(base_center_y, base_left_x)
                    path.quadTo(control_y_neg, px,
                                base_center_y, base_right_x)
                    painter.setPen(QPen(Qt.black, 1))
                    painter.drawPath(path)
                if first_below_zero and cone_height < 0:
                    first_below_zero = False
                color_num += 1



    def draw_legend(self,painter,cones_data):
        scale_x, scale_y = self.scale_x, self.scale_y
        w_width,w_height = self.cell_width * scale_y, self.cell_height * scale_x
        legend_width, legend_height = 664, 40
        print(f"legend_width={legend_width}, legend_height={legend_height}")
        color_num = 0
        for cone in cones_data[0][1]:
            color = COLOR_PALETTE[color_num % len(COLOR_PALETTE)]
            painter.setPen(QPen(color, 4))
            painter.drawLine(legend_width,legend_height,legend_width+60,legend_height)
            function_name = self.functions[color_num % len(self.functions)]
            painter.drawText(legend_width+80,legend_height,function_name)
            legend_height += 20
            color_num+=1
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # Инициализация родительского класса QMainWindow.
        self.setWindowTitle("Графический анализатор")  # Устанавливаем заголовок окна.
        self.setMinimumSize(1000,700)  # Устанавливаем минимальный размер окна.

        central_widget = QWidget()  # Создаем центральный виджет.
        self.setCentralWidget(central_widget)  # Устанавливаем его как центральный.
        layout = QVBoxLayout()  # Создаем вертикальный компоновщик.
        central_widget.setLayout(layout)  # Устанавливаем компоновщик для центрального виджета.

        # Виджет для рисования
        self.plot_widget = PlotWidget()  # Создаем виджет для рисования графиков.
        layout.addWidget(self.plot_widget)  # Добавляем его в компоновщик.

        # Панель управления
        control_layout = QHBoxLayout()  # Создаем горизонтальный компоновщик для панели управления.

        self.func_input = QLineEdit()  # Создаем поле ввода для номеров функций.
        self.func_input.setPlaceholderText("Введите номера функций")
        control_layout.addWidget(self.func_input)  # Добавляем поле ввода в компоновщик.

        # точка начала построения
        self.a_input = QLineEdit()
        self.a_input.setPlaceholderText("введите точку начала интервала")
        control_layout.addWidget(self.a_input)

        # точка конца построения
        self.b_input = QLineEdit()
        self.b_input.setPlaceholderText("введите точку конца интервала")
        control_layout.addWidget(self.b_input)

        # сколько точек на интервале
        self.n_input = QLineEdit()
        self.n_input.setPlaceholderText("введите количество точек на интервале")
        control_layout.addWidget(self.n_input)

        btn_clear = QPushButton("Рисовать")
        btn_clear.clicked.connect(self.update_diagram)
        control_layout.addWidget(btn_clear)

        layout.addLayout(control_layout)  # Добавляем панель управления в вертикальный компоновщик.

        self.cones_db = ConesDataBase()

    def update_diagram(self):
        try:
            functions = []
            for f_num in self.func_input.text().split(","):
                functions.append(self.cones_db.used_functions[int(f_num)])
            print("Main Class update",functions)
            a = float(self.a_input.text())
            b = float(self.b_input.text())
            n = int(self.n_input.text())
            self.plot_widget.update_data(functions,a,b,n)
        except:
            print("пусто")

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Создаем экземпляр приложения.
    window = MainWindow()  # Создаем экземпляр главного окна.
    window.show()  # Отображаем окно.
    sys.exit(app.exec())  # Запускаем главный цикл обработки событий.