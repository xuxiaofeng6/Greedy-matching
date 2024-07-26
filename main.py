# create alleles based on these peaks
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')

from fsmodels import Channel
from const import peaktype,binningmethod,ladder
import params
from tools import txt2array,plot_peaks,generate_scoring_function,txt2array_
import pickle

from FindPeaks import find_raw_peaks
from PeakInfo import peaks_info
from SortPeaks import sort_peaks
from pre import pre_data
from PreAnnotate import preannotate
from SizePeaks import size_peaks
from pkl_io import plot_result

#### 0 读取数据，转成numpy array形式
raw_data = txt2array_(r"D:\afterdata.txt")

#### 1 扫峰
scanning_parameter = params.Params().ladder
raw_peaks = find_raw_peaks(raw_data, scanning_parameter)
plot_peaks(raw_data, raw_peaks)

#### 2 计算峰信息
peaks_info = peaks_info(raw_data,scanning_parameter,raw_peaks)
plot_peaks(raw_data, peaks_info)

#### 3.1 筛选峰
sorted_peaks = sort_peaks(peaks_info,scanning_parameter)
plot_peaks(raw_data,sorted_peaks)

#### 3.2 计算qscore 根据峰类型打分
pre_peaks = pre_data(raw_data,sorted_peaks)
preannotate(pre_peaks,scanning_parameter)
print(len(pre_peaks.alleles))

#### 4 内标匹配
ladder_size = ladder['sizes']
ladder_qc_func = generate_scoring_function(ladder['strict'], ladder['relax'] )
scores = size_peaks(pre_peaks, scanning_parameter, ladder_size, qcfunc = ladder_qc_func)

#### 5 最后一步：保存匹配结果
with open('test_result/1.pkl', 'wb') as f:
    pickle.dump(scores, f)

#### 6 显示内标匹配结果
plot_result()

