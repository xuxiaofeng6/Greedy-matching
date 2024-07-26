import numpy as np
from const import peaktype

def preannotate(channels, params):
    """
    pre-annotate peaks as peak-scanned / peak-broad / peak-stutter/ peak-overlap
    based on criteria defined in params
    """

    # peak_1 is overlap of peak_2 if
    #   brtime2 < ertime1 and ertime1 < ertime2
    #   and height1 at rtime1 is a_fraction of height2 at rtime1 and
    #   height1 at rtime2 is a_fraction of height2 at rtime2.

    # peak is broad if beta > beta_broad_threshold

    channel_peaks = [ (list(channels.alleles), np.median(channels.data))]
    # print(channel_peaks)

    # reset all peak type, score the peaks and set the peak type to peak-noise,
    # peak-broad

    # collect beta * theta first, and used beta * theta as descriptor for noise
    # also if height at either brtime or ertime is higher than 50% at rtime, it is
    # likely a noise

    for (peaks, med_baseline) in channel_peaks:

        if len(peaks) == 0: continue

        beta_theta = sorted([ p.beta * p.theta for p in peaks ])
        sampled_beta_theta = beta_theta[2:len(beta_theta)-2]
        if len(sampled_beta_theta) == 0: sampled_beta_theta = beta_theta
        avg_beta_theta = sum(sampled_beta_theta) / len(sampled_beta_theta)


        for p in peaks:
            p.type = peaktype.scanned
            p.size = -1
            p.bin = -1

            peak_beta_theta = p.beta * p.theta
            score = 1.0

            # extreme noise

            if p.height < 2 * med_baseline:
                p.qscore = 0.25
                p.type = peaktype.noise
                continue

            if p.wrtime < 6 or (p.wrtime < 10 and peak_beta_theta < 0.275 * avg_beta_theta):
                p.qscore = 0.25
                p.type = peaktype.noise
                continue

            # moderately noise

            if peak_beta_theta < 0.33 * avg_beta_theta:
                if (channels.data[p.brtime] > 0.5 * p.height or channels.data[p.ertime] > 0.5 * p.height):
                    p.qscore = 0.25
                    p.type = peaktype.noise
                    continue
                score -= 0.15

            score = 1.0
            if p.beta > params.max_beta:
                p.type = peaktype.broad
                score -= 0.20
            elif p.beta < 5:
                score -= 0.20

            # check theta
            if p.theta < 4:
                # perhaps an artifact
                score -= 0.20

            # penalty by height
            if p.height < 75:
                # decrease the score
                score -= 0.1
            if p.height < 50:
                # decrease even further
                score -= 0.1

            # penalty by symmetrics
            if not ( -1.32 < p.srtime < 1.32 ):
                score -= 0.1

            p.qscore = score
            if p.qscore < 0.5 and p.type == peaktype.scanned:
                p.type = peaktype.noise

            if p.qscore < 0:
                p.qscore = 0.0  # reset to zero

    # checking overlaps against channel !

    # for channel in channels:
    #     for channel_r in channels:
    #         if channel == channel_r:
    #             continue
    #
    #         for p in channel.alleles:
    #             if p.type == peaktype.noise:
    #                 continue
    #
    #             if p.ertime - p.brtime < 3:
    #                 brtime = p.brtime
    #                 ertime = p.ertime
    #             elif p.ertime - p.brtime < 6:
    #                 brtime = p.brtime + 1
    #                 ertime = p.ertime - 1
    #             else:
    #                 brtime = p.brtime + 3
    #                 ertime = p.ertime - 3
    #
    #             if brtime > p.rtime: brtime = p.rtime
    #             if ertime < p.rtime: ertime = p.rtime
    #
    #             brtime = max(0, brtime)
    #             ertime = min(len(channel.data), len(channel_r.data), ertime)
    #
    #             #cerr('checking %d | %s with channel %s' % (p.rtime, channel.dye,
    #             #            channel_r.dye))
    #
    #             if (    channel.data[brtime] < channel_r.data[brtime] and
    #                     channel.data[ertime] < channel_r.data[ertime] and
    #                     p.height < channel_r.data[p.rtime] ):
    #
    #                 # check how much is the relative height of this particular peak
    #                 rel_height = p.height / channel_r.data[p.rtime]
    #                 if rel_height > 1.0:
    #                     continue
    #
    #                 (o_state, o_ratio, o_sym) = calc_overlap_ratio( channel.data,
    #                                                     channel_r.data, p.rtime,
    #                                                     brtime, ertime )
    #
    #                 # if not really overlap, just continue reiteration
    #                 if not o_state:
    #                     continue
    #
    #                 print('peak: %d | %s | %s <> %f | %f | %f' % (p.rtime, p.channel.dye, p.type, rel_height, o_ratio, o_sym))
    #                 if rel_height < 0.15:
    #                     if p.type != peaktype.noise:
    #                         p.type = peaktype.overlap
    #                         print('peak: %d | %s -> overlap' % (p.rtime, p.channel.dye))
    #                     p.qscore -= 0.10
    #                     continue
    #
    #                 if ((rel_height < params.overlap_height_threshold and -0.5 < o_sym < 0.5) or
    #                     (o_ratio < 0.25 and -1.5 < o_sym < 1.5 ) or
    #                     (o_ratio < 0.75 and -0.5 < o_sym < 0.5 )):
    #                     if p.type != peaktype.noise:
    #                         p.type = peaktype.overlap
    #                         print('peak: %d | %s -> overlap' % (p.rtime, p.channel.dye))
    #                     p.qscore -= 0.10
    #                     continue

    # checking for stutter peaks based on minimum rtime & rfu

    for (peaks, med_baseline) in channel_peaks:
        alleles = sorted( [ p for p in peaks ],
                        key = lambda x: x.rtime )

        for idx in range( len(alleles) ):
            allele = alleles[idx]
            if idx > 0:
                allele_0 = alleles[idx-1]
                if allele.rtime - allele_0.rtime < params.stutter_rtime_threshold:
                    if allele_0.height * params.stutter_height_threshold > allele.height:
                        allele.type = peaktype.stutter
                        allele.qscore -= 0.2
            if idx < len(alleles) - 1:
                allele_1 = alleles[idx+1]
                if allele_1.rtime - allele.rtime < params.stutter_rtime_threshold:
                    if allele_1.height * params.stutter_height_threshold > allele.height:
                        allele.type = peaktype.stutter
                        allele.qscore -= 0.2

    # for (peaks, med_baseline) in channel_peaks:
    #
    #     if len(peaks) == 0: continue
    #
    #
    #
    #     for p in peaks:
    #         p.type = peaktype.scanned
    #         p.size = -1
    #         p.bin = -1
    #
    #         peak_beta_theta = p.beta * p.theta
    #         score = 1.0
    #
    #         p.rtime
    #
    #         if p.beta > params.max_beta:
    #             p.type = peaktype.broad
    #             score -= 0.20
    #
    #         p.qscore = score