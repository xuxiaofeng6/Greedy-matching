import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
mpl.use('TkAgg')

def sim_data():
    N = 1000
    x = np.linspace(0, 200, N)
    y = 2 * np.cos(2 * np.pi * 300 * x) \
        + 5 * np.sin(2 * np.pi * 100 * x) \
        + 4 * np.random.randn(N)
    return y

def txt2array(txt_path):
    # 功能：读取只包含数字的txt文件，并转化为array形式
    # txt_path：txt的路径；delimiter：数据之间的分隔符

    with open(txt_path) as f:
        data = f.readlines()
        print(data)
        num = data[0].split(',')

        # line = line.strip(",")  # 去除末尾的换行符
        temp = list(map(float, num))

    data_array = np.array(temp)
    return data_array

def txt2array_(txt_path):
    # 功能：读取只包含数字的txt文件，并转化为array形式
    # txt_path：txt的路径；delimiter：数据之间的分隔符

    with open(txt_path) as f:
        data = f.readlines()

    dataset = []
    # 对每一行作循环
    for data in data:
        data1 = data.strip('\n')  # 去掉开头和结尾的换行符
        data1 = np.nan_to_num(data1)
        if data1 == 'NaN':
            data1 = '0'
        data1 = eval(data1)
        dataset.append(data1)  # 把这一行的结果作为元素加入列表dataset

    data_array = np.array(dataset)
    return data_array


def plot_peaks(raw_data,raw_peaks):
    raw_peaks_array = np.array(raw_peaks)
    xs = np.arange(0, len(raw_data), 1)

    x = np.transpose(raw_peaks_array)[0]
    y = np.transpose(raw_peaks_array)[1]

    print(raw_peaks_array.shape)

    plt.plot(xs, raw_data)
    plt.plot(x, y, 'o')
    plt.show()

def calculate_area(y, t, threshold, baseline):
    """ return (area, brtime, ertime, srtime)
        area: area
        brtime: begin rtime
        ertime: end rtime
    """

    # right area
    data = y[t:]
    r_area, ertime, r_shared = half_area(data, threshold, baseline)

    # left area
    data = y[:t+1][::-1] #反
    l_area, brtime, l_shared = half_area(data, threshold, baseline)


    return ( l_area + r_area - y[t], t - brtime, ertime + t, math.log2(r_area / l_area),
                l_shared, r_shared )

def half_area(y, threshold, baseline):
    """ return (area, ertime, shared_status)
    """

    winsize = 3
    threshold = threshold/2
    shared = False
    area = y[0]
    edge = float(np.sum(y[0:winsize]))/winsize
    old_edge = 2 * edge

    index = 1
    limit = len(y)

    while ( edge > area * threshold and edge < old_edge and
            index < limit and y[index] >= baseline ):
        old_edge = edge
        area += y[index]
        edge = float(np.sum(y[index:index+winsize]))/winsize
        index += 1
    if edge >= old_edge:
        shared = True
    index -= 1

    return area, index, shared

def generate_scoring_function( strict_params, relax_params ):

    def _scoring_func( alignment_result, method ):
        # alignment_result is (dp_score, dp_rss, dp_z, dp_peaks)
        dp_score, dp_rss, dp_z, dp_peaks = alignment_result

        if method == 'strict':
            if ( dp_score >= strict_params['min_dpscore'] and
                    dp_rss <= strict_params['max_rss'] and
                    len(dp_peaks) >= strict_params['min_sizes'] ):
                return (1, None)
            return (0, None)
        elif method == 'relax':
            msg = []
            # scoring based on parts of results

            # score based on DP score compared to minimum DP score
            delta_score = relax_params['min_dpscore'] - dp_score
            if delta_score <= 0:
                dp_score_part = 1
            else:
                dp_score_part = 1e-2 ** (1e-2 * delta_score)

            # score based on RSS compared to the maximum allowed RSS
            delta_rss = dp_rss - relax_params['max_rss']
            if delta_rss <= 0:
                dp_rss_part = 1
            else:
                dp_rss_part = 1e-2 ** ( 1e-3 * delta_rss )
                msg.append( 'RSS > %d' % ( relax_params['max_rss'] ) )

            # score based on how many peaks we might miss compared to minimum number of peaks
            delta_peaks = relax_params['min_sizes'] - len(dp_peaks)
            if delta_peaks <= 0:
                dp_peaks_part = 1
            else:
                dp_peaks_part = max( 0, - delta_peaks / 0.5 * relax_params['min_sizes'] - 1)
                msg.append( 'Missing peaks = %d' % delta_peaks )

            # total overall score
            score = 0.3 * dp_score_part + 0.5 * dp_rss_part + 0.2 * dp_peaks_part
            return (score, msg)

        raise RuntimeError("Shouldn't be here!")


    return _scoring_func