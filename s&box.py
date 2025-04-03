import numpy as np
minh = 0
maxh = 0.5

cells_x = np.linspace(minh,maxh,num=8)
print(cells_x,type(cells_x))

cells_poss = cells_x.tolist()
print(cells_poss,type(cells_poss))