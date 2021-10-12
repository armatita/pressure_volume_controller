# -*- coding: utf-8 -*-
"""
Created on Sun May 23 14:01:28 2021

@author: josecorreia
"""

import matplotlib.pyplot as pyplot
import numpy as np

y = [0, 1, 2, 3, 4, 5, 6, 7, 8,9,10] 
x = [0.0, 1.1, 2.2, 3.3, 4.3, 5.2, 6.1, 7.0, 7.9, 8.8, 9.7]

 
fig, plt = pyplot.subplots()
plt.grid()
plt.set_ylabel('Valores no padrão')
plt.set_xlabel('Valores no medidor') 
plt.set_title('CALIBRAÇÃO')
plt.scatter(x, y)
z = np.polyfit(x, y, 2)
p = np.poly1d(z)
plt.plot(x,p(x),"r--")
plt.text(5,0,"y=%.4fx^2+%.4fx"%(z[0],z[1]))




        # plt.scatter(x, y, c='b',s=30)
        # plt.plot(x,y,c='r', linestyle='--')
        # slope, intercept, r, p, se = linregress(x, y)
        # print(slope, intercept, r, p, se)
        # plt.plot([min(x), max(x)],[intercept + slope*min(x), intercept + slope*max(x)], c='g')
        # plt.show()