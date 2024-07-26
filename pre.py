from fsmodels import Channel
from const import peaktype,binningmethod

def pre_data(raw_data,sorted_peaks):

    pre_peaks = Channel()
    pre_peaks.data = raw_data

    alleles = []
    for peak in sorted_peaks:
        (rtime, height, area, brtime, ertime, srtime, beta, theta) = peak
        wrtime = ertime - brtime
        height = round(height)
        # print(rtime, height, area, brtime, ertime, srtime, beta, theta)
        allele = pre_peaks.new_allele(rtime=rtime,
                                    height=height,
                                    area=area,
                                    brtime=brtime,
                                    ertime=ertime,
                                    wrtime=wrtime,
                                    srtime=srtime,
                                    beta=beta,
                                    theta=theta,
                                    type=peaktype.scanned,
                                    method=binningmethod.notavailable)

        # allele.marker = channel.marker
        # print(allele)

        alleles.append(allele)

    pre_peaks.alleles = alleles
    # peak_alleles = pre_peaks.alleles
    # # print(peak_alleles)
    return pre_peaks

    # for peak in peak_alleles:
    #     print(peak)