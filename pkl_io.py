import pickle
from tools import plot_peaks,txt2array,txt2array_
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

def plot_result():

    with open('test_result/1.pkl', 'rb') as f:
        data = pickle.load(f)

    result = data[2][3]
    print(result)
    print(type(result))

    print('score is %d' % data[0])

    x = []
    y = []
    z = []

    for (ladder,peak) in result:
        print(ladder,peak)
        x.append(peak.rtime)
        y.append(peak.height)
        z.append(int(ladder))

    raw_data = txt2array_(r"D:\afterdata.txt")

    xs = np.arange(0, len(raw_data), 1)

    plt.plot(xs, raw_data)
    plt.plot(x, y, 'o')
    for a, b, c in zip(x, y, z):
        plt.text(a, b, c, ha='center', va='bottom', weight= 'bold', fontsize=8)

    plt.show()