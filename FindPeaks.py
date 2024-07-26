import math
import numpy as np


def find_raw_peaks(raw_data, params):

    max_height = max(raw_data)
    width_ratio = max(1, round(math.log(max_height/params.width_ratio)))
    widths = params.widths
    print(widths)

    from scipy.signal import find_peaks_cwt
    indices = find_peaks_cwt(raw_data, widths, min_snr = params.min_snr)
    print('find_peaks_cwt() found %d peaks' % len(indices))

    # filter for absolute heights within proximity
    raw_peaks = []
    max_len = len(raw_data)
    for idx in indices:

        # print(idx)

        if not (params.min_rtime < idx < params.max_rtime):
            continue

        height, index = max([(raw_data[i], i) for i in range(max(0, idx-3), min(max_len,idx+3) )])
        # print(height, index)

        if height < params.min_height: continue
        if (index, height) in raw_peaks: continue
        raw_peaks.append((index, height))

    print(len(raw_peaks))

    return raw_peaks
