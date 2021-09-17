import scipy.interpolate as si
import numpy as np
import matplotlib.pyplot as plt


y = np.array([75, 0, 25, 100, 20, 40, 200, 80, 20])
x = np.array([k for k in range(len(y))])
limit = np.array([60 for _ in range(len(y))])

x_new = np.linspace(1, 9, 300)
a_BSpline = si.make_interp_spline(x, y)
y_new = a_BSpline(x_new)


color_master = []
for elt in y_new:
    if elt <= 20:
        color_master.append('y')
    elif elt <= 60:
        color_master.append('b')
    elif elt > 60 and elt <= 100:
        color_master.append('cyan')
    else:
        color_master.append('r')


color_0 = color_master[0]
start_seg = 0

for cnt in range(len(color_master)):
    if color_0 == color_master[cnt+1]:
        color_0 = color_master[cnt+1]
    else:
        plt.plot(x_new[start_seg:cnt+1],
                 y_new[start_seg:cnt+1], c=color_0)
        start_seg = cnt
        color_0 = color_master[cnt+1]
    if (cnt + 2) == len(color_master):

        plt.plot(x_new[start_seg:cnt+1],
                 y_new[start_seg:cnt+1], c=color_0)
        break
plt.show()
