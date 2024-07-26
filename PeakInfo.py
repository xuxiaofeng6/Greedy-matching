import numpy as np
from tools import calculate_area
from const import ladder

def peaks_info(raw_data, params, raw_peaks = None):
    """
    find all peaks based on the criteria defined in params, and assign as peak-scanned
    raw_data is baseline-normalized & smoothed trace

    parameters used are:
    method: 'cwt' or 'mlpy'
    widths: window size for peak scanning
    cwt_min_snr:
    min_height:
    min_relative_ratio:
    max_relative_ratio:
    min_height_ratio:
    max_peak_number:

    """

    # # only retain 2 * max_peak_number and discard the rest
    # raw_peaks = sorted(raw_peaks, key = lambda x: x[1], reverse = True )[:params.max_peak_number * 2]
    # print(len(raw_peaks))

    # if params.min_relative_ratio > 0 or params.max_relative_ratio > 0:
    #     med = np.median( list(p[1] for p in raw_peaks) )
    #     if params.min_relative_ratio > 0:
    #         median_min = med * params.min_relative_ratio
    #         raw_peaks = [ p for p in raw_peaks if p[1] > median_min ]
    #     if params.max_relative_ratio > 0:
    #         median_max = med * params.max_relative_ratio
    #         raw_peaks = [ p for p in raw_peaks if p[1] < median_max ]

    if not raw_peaks:
        return raw_peaks

    # # filter for minimum height ratio
    # if params.min_height_ratio > 0:
    #     min_height = max( list( p[1] for p in raw_peaks) ) * params.min_height_ratio
    #     raw_peaks = [p for p in raw_peaks if p[1] > min_height]

        # if len(raw_peaks_) >= ladders['Orange600']['strict']['min_sizes']:
        #     raw_peaks = raw_peaks_
        #     print(len(raw_peaks))

    # calculate area

    (q50, q75) = np.percentile(raw_data, [ 50, 75 ] )
    peaks = []
    for (peak, height) in raw_peaks:
        area, brtime, ertime, srtime, ls, rs = calculate_area( raw_data, peak, 5e-2, q50 )
        wrtime = ertime - brtime
        if wrtime < 3:
            continue
        beta = area / height
        theta = height / wrtime
        if height >= 25 and beta * theta < 6: #10:
            continue
        if height < 25 and beta * theta < 3: #6:
            continue
        peaks.append((peak, height, area, brtime, ertime, srtime, beta, theta))

    peaks.sort()
    print('peaks stage 1 size: %d' % len(peaks))
    # print(3, 'peaks stage 1: %s' % repr(peaks))

    # if len(peaks) < ladder['strict']['min_sizes']:
    #     for (peak, height) in raw_peaks:
    #         area, brtime, ertime, srtime, ls, rs = calculate_area(raw_data, peak, 5e-2, q50)
    #         wrtime = ertime - brtime
    #         beta = area / height
    #         theta = height / wrtime
    #         peaks.append((peak, height, area, brtime, ertime, srtime, beta, theta))

    non_artifact_peaks = []

    for idx in range(len(peaks)):
        peak = peaks[idx]

        if idx > 0:
            prev_p = peaks[idx-1]
            if peak[3] - prev_p[4] < 5 and peak[1] < params.artifact_ratio * prev_p[1]:
                # we are artifact, just skip
                continue
        if idx < len(peaks)-1:
            next_p = peaks[idx+1]
            if next_p[3] - peak[4] < 5 and peak[1] < params.artifact_ratio * next_p[1]:
                # we are another artifact, just skip
                continue

        non_artifact_peaks.append(peak)

    print('max_peak_number: %d' % params.max_peak_number)

    sorted_peaks = sorted( non_artifact_peaks, key = lambda x: (x[1], x[6] * x[7]),
                        reverse=True )[:params.max_peak_number]
    peaks = sorted(sorted_peaks)
    print('peaks stage 3 size: %d' % len(peaks))

    return peaks
