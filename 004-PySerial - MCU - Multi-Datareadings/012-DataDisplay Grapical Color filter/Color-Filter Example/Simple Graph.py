import scipy.interpolate as si
import numpy as np
import matplotlib.pyplot as plt


y = np.array([75, 0, 25, 100, 20, 40, 200, 80, 20])
x = np.array([k for k in range(len(y))])

x_new = np.linspace(1, 9, 300)
a_BSpline = si.make_interp_spline(x, y)
y_new = a_BSpline(x_new)
# limit = np.array([60 for _ in range(len(y_new))])
limit = 100
plt.plot(x_new, y_new, c='b')

plt.show()
