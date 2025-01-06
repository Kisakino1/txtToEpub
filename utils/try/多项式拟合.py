import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal
from matplotlib import rcParams

# 设置不使用科学计数法
np.set_printoptions(suppress=True)

# 设置字体为 SimHei（黑体），如果你使用的是 Windows 系统
rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

x = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8])
y = np.array([0, 1, 8, 27, 64, 125, 216, 343, 512])

# 多项式插值
degree = 8  # 插值多项式的阶数，通常为 n-1, n 是数据点数量
coefficients = np.polyfit(x, y, degree)
poly_func = np.poly1d(coefficients)

# 绘制结果
x_smooth = np.linspace(min(x), max(x), 100)
y_smooth = poly_func(x_smooth)

plt.scatter(x, y, color='red', label='数据点')
plt.plot(x_smooth, y_smooth, label='多项式插值')  # 中文标签
plt.legend()
plt.show()

# 打印多项式函数，不使用科学计数法
print("多项式函数为：")
terms = [f"{Decimal(coef):.4f} * x^{i}" for i, coef in enumerate(reversed(coefficients))]
print(" + ".join(terms[::-1]))
