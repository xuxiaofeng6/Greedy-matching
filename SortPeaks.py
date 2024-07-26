from const import ladder

def sort_peaks(initial_peaks, params):
    """
    scan for peaks based on the criteria defined in params, set as peak-scanned,
    and prepare the channel data structure
    """

    # initial_peaks = find_peaks(raw_data, params, raw_peaks)
    print('initial peaks: %d' % len(initial_peaks))
    print(initial_peaks)

    # perform futher cleaning for ladder channels
    if params.expected_peak_number:
        epn = params.expected_peak_number
        peak_qualities = sorted([ (p[6] * p[7], p) for p in initial_peaks ], reverse=True)
        low_scores = [q[0] for q in peak_qualities[round(epn/3):round(epn * 1.5)]]

        print(peak_qualities)
        print(low_scores)


        avg_low_score = sum(low_scores) / len(low_scores)
        ratio_low_score = (avg_low_score - low_scores[-1]) / low_scores[-1]

        print(avg_low_score)
        print(ratio_low_score)


        if avg_low_score < 75:
            # questionable quality, please use more peaks
            score_threshold = 4 #avg_low_score * 0.1
            height_threshold = 6
        else:
            if avg_low_score - low_scores[-1] > low_scores[-1]:
            # peaks' height are likely not to evenly distributed
                score_threshold = max(low_scores[-1] * 0.90, 4)
            else:
                score_threshold = avg_low_score * 0.25
            height_threshold = 10
            print('using score threshold: %f' % score_threshold)
            print('using height_threshold: %d' % height_threshold)
        peaks = [ q for q in peak_qualities
                            if q[0] > score_threshold and q[1][1] > height_threshold ]
        print('after peak quality filtering: %d' % len(peaks))
        if len(peaks) > 1.5 * params.expected_peak_number:
            # try to remove peaks further
            saved_peaks = peaks
            while len(peaks) - len(saved_peaks) < 0.30 * len(peaks) and height_threshold < 20:
                height_threshold += 1
                saved_peaks = [ q for q in saved_peaks if q[0] > height_threshold ]
            peaks = saved_peaks
            print('after reducing peaks number by height: %d' % len(peaks))
        peaks = sorted([ q[1] for q in peaks ])

    else:
        peaks = initial_peaks

    if len(peaks) < ladder['strict']['min_sizes']:
        peaks = initial_peaks

    return peaks