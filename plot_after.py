import pickle
from tools import plot_peaks,txt2array,txt2array_
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt


raw_data = txt2array_(r"D:\afterdata.txt")
peak_index = txt2array_(r"D:\peakIndexs.txt")

print(peak_index)
print(len(peak_index))

xs = np.arange(0, len(raw_data), 1)

plt.plot(xs, raw_data)
plt.plot(peak_index, raw_data[peak_index], 'o')
plt.show()

