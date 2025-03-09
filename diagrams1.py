import sys  # Импорт модуля sys для работы с системными функциями (например, завершение программы).
import math  # Импорт модуля math для математических операций (sin, cos, sqrt и т.д.).

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout)
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath  # Импорт классов для рисования и работы с цветами.
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
            i = a
            while i <= b:
                try:
                    values.append((i, func(i)))
                except:
                    values.append((i, 0))
                i += round(abs(b - a) / (n-1),3)
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
        i = a
        while i <= b:
            values = []
            for function in self.functions:
                expr = function
                func = lambda x, e=expr: eval(e, {"math": math, "x": x})
                try:
                    values.append((i, func(i)))
                except:
                    values.append((i, 0))
            fvalues.append(values.copy())
            values.clear()
            i += round(abs(b - a) / (n-1),3)
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
        self.used_functions = ['-x/5','x','math.exp(-x**2+math.cos(x))','1/x','-2*x']

    def setfunctions(self,funcs):
        self.functions = funcs.copy()
"""        self.funcs = self.function_points(-1,5,7)
# print("непонятно чето, дадим массивы аргументов, отрицательных и положительных значений для этих аргументов")
        self.masses = self.define_data(self.funcs)
        self.arg_funcs = self.graph_points(-1,5,7)
        self.cone_params = self.define_graph(self.arg_funcs)
        self.cones = self.define_cones(self.cone_params)"""

class PlotWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)  # Инициализация родительского класса QWidget.
        print(self.width(),self.height())
        self.cones_db = ConesDataBase()
        self.functions = []  # Список для хранения функций
        self.color_index = 0  # Индекс для перебора цветов из палитры.
        print("class PlotWidget",self.functions)
        # в первом построении пусть будет 40 пикселей на 1 клетку
        self.scale_y = 40;self.scale_x = 40

        self.funcs = None
        self.masses = None
        self.arg_funcs = None
        self.cones_params = None
        self.cones = None
        """
        self.funcs = self.cones_db.function_points(0,0,1)
        self.masses = self.cones_db.define_data(self.funcs)
        self.arg_funcs = self.cones_db.graph_points(0,0,1)
        
        self.cones_params = self.cones_db.define_graph(self.arg_funcs)
        for cone_params in self.cones_params:
            print(cone_params)
        self.cones = self.cones_db.define_cones(self.cones_params)
        for cone_data in self.cones:
            print(cone_data)

        self.height = math.ceil(abs(min(self.masses[0]))) + math.ceil(max(self.masses[0])) + 4
        self.width = math.ceil(abs(min(self.masses[2]))) + math.ceil(max(self.masses[1])) + 2
        """
        self.cell_height = 15
        self.cell_width = 20

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
        self.cell_height = math.ceil(max(self.masses[0]) - min(self.masses[0])) + 4  # высота в клетках
        self.cell_width = math.ceil(abs(min(self.masses[2]))) + math.ceil(max(self.masses[1])) + 2  # ширина в клетках
        # со вторым чуть сложнее
        # self.scale_y = 40; self.scale_x = 40
        self.scale_y = 640 // self.cell_width # для ширины
        self.scale_x = 480 // self.cell_height # для высоты

        print("parental", self.width(),self.height())
        print("cells ",self.cell_width,self.cell_height)
        print("scales ",self.scale_y,self.scale_x)
        self.update()

    def paintEvent(self, event):
        # Метод, вызываемый при перерисовке виджета.
        painter = QPainter(self)  # Создание объекта QPainter для рисования.
        painter.setRenderHint(QPainter.Antialiasing) # Сглаживание

        self.draw_grid(painter)

        if len(self.functions)>0:
            self.draw_grid(painter)
            self.draw_points(painter, self.funcs)
            self.draw_cones(painter, self.cones)
            self.draw_axes(painter)
            # self.draw_legend(painter, self.cones)

    def crosses_line (self):
        scale_x, scale_y = self.scale_x, self.scale_y
        w_width = self.cell_width * scale_y
        w_height = self.cell_height * scale_x # pixels height

        # print("размер crosses:", w_width, w_height)

        minw = min(math.floor(min(self.masses[2])), 0)
        maxw = max(math.ceil(max(self.masses[1])), 0)

        minh = math.floor(min(self.masses[0]))
        maxh = math.ceil(max(self.masses[0]))

        y_axes = []
        for i in range(minw, maxw + 1): y_axes.append(i)
        # print(f"y={y_axes}")
        cross_cell = y_axes.index(0) + 1
        cross_y = cross_cell * scale_y

        """x_axes = []
        for i in range(minh, maxh+1): x_axes.append(i)
        print(f"x={x_axes}")
        cross_cell = x_axes.index(0) + 2
        cross_x = w_height - cross_cell * scale_x
        """

        return cross_y

    def draw_axes(self, painter):

        scale_x, scale_y = self.scale_x, self.scale_y  # Масштаб для осей
        w_width, w_height = self.cell_width * scale_y, self.cell_height * scale_x  # размеры виджета

        crosses = self.crosses_line()


        minw = min(math.floor(min(self.masses[2])),0)
        maxw = max(math.ceil(max(self.masses[1])),0)
        used_width = (maxw-minw)*scale_y


        """часть для определения оси X"""
        minh = math.floor(min(self.masses[0])) #
        maxh = math.ceil(max(self.masses[0])) # задаваемое b)
        # может быть больше нуля
        used_height = (maxh-minh)*scale_x
        # used_height = crosses[0]

        cross_y = crosses
        print(f"линия нулевая{cross_y}")

        # Рисуем оси
        painter.setPen(QPen(Qt.black, 2))  # Устанавливаем черный цвет и толщину линии.

        """
        painter.drawLine(0, 20, w_width, 20)
        painter.drawLine(20, 0, 20, w_height)
        painter.drawLine(w_width-20, 0,w_width - 20, w_height)
        """
        painter.drawLine(cross_y, 0, cross_y, w_height)  # Ось X.
        # Подписи осей
        painter.drawText(w_width - scale_y, w_height - scale_x, "Y")  # Подпись оси Y.
        painter.drawText(cross_y + scale_y//4, scale_x, "X")  # Подпись оси X.

        print(f"height is {used_height}, all height is = {w_height}")
        # Подписи масштаба для оси Y
        # Сделать условие на проверку минимума (он больше 0 - ставим 0, меньше - оставляем)
        ys = []; xs=[]
        for y in range(minw, maxw+1):
            py = ((y-minw)/(maxw-minw)) * (used_width - 0) + scale_y # 0 здесь чисто из-за того, что виджет начинается с 0
            ys.append((y, py))
            painter.drawText(py, w_height - scale_x, f"{y}")  # Подпись значения.
        # print(ys)

        # Подписи масштаба для оси X (на самом деле начинать нужно со значения 2, ибо 0 отведен для доп. клетки)
        for x in range(minh, maxh+1):
            px = (1-((x - minh)/(maxh - minh))) * used_height + 2 *scale_x
            xs.append((x,px))
            painter.drawText(cross_y, px, f"{x}")
        # print(xs)

        """
        for x in range(minh,maxh+1):
            px = (1-((x - minh)/(maxh - minh)))*w_height - scale_x
            painter.drawText(cross_y, px, f"{x}")"""

    def draw_grid(self, painter):
        # сетка
        scale_x, scale_y = self.scale_x, self.scale_y  # Масштаб для осей
        w_width, w_height = self.cell_width * scale_y, self.cell_height * scale_x  # Получаем размеры виджета.

        # painter.setPen(QPen(Qt.gray, 2))
        painter.setPen(QPen(Qt.gray, 1.5, Qt.DotLine))
        for px in range(0,w_width+scale_y,scale_y):
            painter.drawLine(px,0,px,w_height)

        for py in range(0,w_height+scale_x,scale_x):
            painter.drawLine(0,py,w_width,py)

    def draw_points(self, painter, funcs):
        scale_x, scale_y = self.scale_x, self.scale_y
        w_width, w_height = self.cell_width * scale_y, self.cell_height * scale_x
        crosses = self.crosses_line()
        # cross_x = crosses[0]
        cross_y = crosses

        minh = math.floor(min(self.masses[0]))  #
        maxh = math.ceil(max(self.masses[0]))

        used_height = (maxh - minh) * scale_x

        color_num = 0
        for fval in funcs:
            color = COLOR_PALETTE[color_num % len(COLOR_PALETTE)]
            painter.setPen(QPen(color, 5))
            color_num+= 1
            for (x,y) in fval:
                px = (1 - ((x - minh) / (maxh - minh))) * used_height + 2 * scale_x
                painter.drawPoint(cross_y+y*scale_y,px)

    def draw_cones(self,painter,cones_data):
        scale_x, scale_y = self.scale_x, self.scale_y

        crosses = self.crosses_line()
        # cross_x = crosses[0]
        cross_y = crosses

        minh = math.floor(min(self.masses[0]))  #
        maxh = math.ceil(max(self.masses[0]))

        used_height = (maxh - minh) * scale_x

        # будет здесь отрисовка конусов
        for cones in cones_data:
            x = cones[0] # это аргумент в значении
            px = (1 - ((x - minh) / (maxh - minh))) * used_height + 2 * scale_x # это аргумент в пикселях
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
                painter.setBrush(color)
                color_num += 1
                # не могу так, надо вынести параметры
                height = cone[0]; cone_height = cone[1]; radius = cone[2]
                # это какой-то прикол

                # в эой строке рисуется нижняя линия треугольника (конуса)
                painter.drawLine(cross_y+(height+cone_height)*scale_y,px,
                                 cross_y+height*scale_y,px - radius*scale_x)
                # а в этой уже верхняя (там y2 просто использует cross_x-(x+radius)*scale_x для большего вычитаемого
                # ,что будет давать ПОДЪЁМ
                painter.drawLine(cross_y+(height+cone_height)*scale_y,px,
                                 cross_y+height*scale_y,px + radius*scale_x)
                #а сейчас вообще будет цикл, чтоб было заполнение
                heights = []
                for coord in range(math.floor((x - radius) * scale_x), math.floor((x + radius) * scale_x) + 1):
                    heights.append((coord - x * scale_x) ** 2)
                amortization = max(heights)
                # print(f"x {x} cross_y {cross_y} height {height} cone height {cone_height}")

                """for coord in range(math.floor((x-radius)*scale_x),math.ceil((x+radius)*scale_x)+1):
                    if radius !=0:
                        addition_height = (coord - x * scale_x) ** 2 / amortization
                    else:
                        addition_height = 0

                    if cone_height < 0:
                        if first_below_zero:
                            painter.drawLine(cross_y + (height + cone_height) * scale_y, cross_x - x * scale_x,
                                             cross_y + height * scale_y, cross_x - coord)
                        else:
                            painter.drawLine(cross_y + (height+cone_height) * scale_y, cross_x - x * scale_x,
                                         cross_y + (height - 1 + addition_height) * scale_y//4, cross_x - coord)
                    else:
                        painter.drawLine(cross_y + (height + cone_height) * scale_y, cross_x - x * scale_x,
                                         cross_y + height * scale_y, cross_x - coord)
                """
                # я молдаван, ещё ж основание осталось
                painter.drawLine(cross_y+height*scale_y,px - radius*scale_x,
                                 cross_y+height*scale_y,px + radius*scale_x)
                """старый варик
                # FURTHER BEYOND (первое применение QPainterPath)
                # ваще прикол - кривая линия
                path = QPainterPath()
                path.moveTo(cross_y+height*scale_y,cross_x-(x-radius)*scale_x)
                k = 0.5; angle = -0.5
                contr_y = height + k * angle
                path.quadTo(cross_y+contr_y*scale_y,cross_x-x*scale_x,cross_y+height*scale_y,cross_x-(x+radius)*scale_x)
                painter.drawPath(path)

                """
                """
                if cone_height >= 0 or (first_below_zero and not is_there_above_zero):
                    painter.drawEllipse(QPointF(cross_y+height*scale_y,cross_x-x*scale_x),scale_y//4,radius*scale_x)
                if first_below_zero and cone_height < 0:
                    first_below_zero = False
                """

    def draw_legend(self,painter,cones_data):
        scale_x, scale_y = self.scale_x, self.scale_y
        w_width,w_height = self.cell_width * scale_x, self.cell_height * scale_y
        legend_width, legend_height = w_width+scale_x, 2*scale_y
        color_num = 0
        for cone in cones_data[0][1]:
            color = COLOR_PALETTE[color_num % len(COLOR_PALETTE)]
            painter.setPen(QPen(color, 4))
            painter.drawLine(legend_width,legend_height,legend_width+scale_x,legend_height)
            function_name = self.functions[color_num % len(self.functions)]
            painter.drawText(legend_width+2*scale_x,legend_height,function_name)
            legend_height += scale_y
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