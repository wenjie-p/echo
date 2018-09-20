import numpy
from FeatureExtraction import StHarmonic
from Wrapper import ProcessingDir
from AudioIO import ReadAudioFile


@ProcessingDir
def ExtractF0s(fp):

    sr, sig = ReadAudioFile(fp)

    sig = numpy.double(sig)

    sig = sig / (2.0 ** 15)
    DC = sig.mean()
    MAX = (numpy.abs(sig)).max()
    sig = (sig - DC)/(MAX + 0.0000000001)

    N = len(sig)

    cur_pos = 0
    win = int(0.020 * sr)
    step = int(0.010 * sr)

    F0s = []
    while (cur_pos + win - 1 < N):
        x = sig[cur_pos:cur_pos + win]
        cur_pos += step
        _, F0 = StHarmonic(sr, x)
        F0s.append(F0)

    return F0s


