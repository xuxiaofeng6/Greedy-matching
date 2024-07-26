import numpy as np
from const import peaktype, binningmethod, allelemethod
from sortedcontainers import SortedListWithKey

def local_southern(ladder_alleles):
    """ southern local interpolation """

    ladder_allele_sorted = SortedListWithKey( ladder_alleles, key = lambda k: k.rtime )
    x = [p.rtime for p in ladder_allele_sorted]
    # y = [p.size for p in ladder_allele_sorted]
    y = [p.size for p in ladder_allele_sorted]


    # print(ladder_allele_sorted)
    # print(x)
    def _f(rtime):
        """ return (size, deviation)
            deviation is calculated as delta square between curve1 and curve2
        """

        idx = ladder_allele_sorted.bisect_key_right(rtime)

        # left curve
        z1 = np.polyfit( x[idx-2:idx+1], y[idx-2:idx+1], 2)
        size1 = np.poly1d( z1 )(rtime)
        min_score1 = min( x.qscore for x in ladder_allele_sorted[idx-2:idx+1] )

        # right curve
        z2 = np.polyfit( x[idx-1:idx+2], y[idx-1:idx+2], 2)
        size2 = np.poly1d( z2 )(rtime)
        min_score2 = min( x.qscore for x in ladder_allele_sorted[idx-1:idx+2] )

        return ( (size1 + size2)/2, (size1 - size2) ** 2, (min_score1 + min_score2)/2,
                allelemethod.localsouthern)

    return _f