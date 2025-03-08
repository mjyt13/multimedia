functions = ['-x/5', 'x', 'math.exp(-x**2+math.cos(x))', '1/x', '-2*x']
import math


# просто списки для точек с одинаковым аргументом
def graph_points(a, b, n):
    fvalues = []
    i = a
    while i <= b:
        values = []
        for function in functions:
            expr = function
            func = lambda x, e=expr: eval(e, {"math": math, "x": x})
            try:
                values.append((i, func(i)))
            except:
                values.append((i, 0))
        fvalues.append(values.copy())
        values.clear()
        i += abs(b - a + 1) / n
    return fvalues

f = graph_points(-1, 5, 7)

# Нужно для создания чего-нибудь с накоплением
def define_graph(used_points):
    cones = []
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
    return cones

f = define_graph(f)

def define_cones(points):
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
            radius = 1
            ratio = radius/cone_height
            for j in range(i):
                if dots[i] >= 0 and dots[j] >= 0:
                    height += dots[j]
                    cone_height -= dots[j]
                if dots[i] < 0 and dots[j] < 0:
                    height += dots[j]
                    cone_height -= dots[j]
            radius = round(ratio * cone_height,digits_number)
            cone_data.append((round(height,digits_number),round(cone_height,digits_number),radius))
        cones_data.append((arg,cone_data))
    return cones_data

c_data = define_cones(f)

for c in c_data:
    print(c)