import peakalign as pa
import time

def size_peaks(channel, params, ladders, qcfunc = None):

    data = channel.data
    scores = []

    start = time.perf_counter()
    # perform fast_align with both clean, high quality peaks and good peaks
    (score_0, msg_0, result_0, method_0) = pa.fast_align( data, ladders,
                                                channel.alleles, qcfunc )
    dur = time.perf_counter() - start
    print("time of fast_align is {:.2f}s".format(dur))

    if score_0 > 0.99:
        return (score_0, msg_0, result_0, method_0)
    print('fast_align(): %4.2f' % score_0)
    scores.append( (score_0, msg_0, result_0, method_0) )

    start = time.perf_counter()
    # perform shift_align with both clean, high quality peaks and good peaks
    (score_0, msg_0, result_0, method_0) = pa.shift_align( data, ladders,
                                                channel.alleles, qcfunc )
    dur = time.perf_counter() - start
    print("time of shift_align is {:.2f}s".format(dur))


    if score_0 > 0.99:
        return (score_0, msg_0, result_0, method_0)
    print('shift_align(): %4.2f' % score_0)
    scores.append( (score_0, msg_0, result_0, method_0) )


    start = time.perf_counter()
    # perform greedy alignment
    (score_1, msg_1, result_1, method_1) = pa.greedy_align( data, ladders,
                                                channel.alleles, qcfunc )
    dur = time.perf_counter() - start
    print("time of greedy_align is {:.2f}s".format(dur))

    scores.append( (score_1, msg_1, result_1, method_1) )

    scores.sort( key = lambda x: x[0] )
    return scores[-1]

