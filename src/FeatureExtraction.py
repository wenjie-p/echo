import numpy
eps = 0.00000001

def StZCR(frame):

    """calculate the zero crossing rate for a given frame"""

    count = len(frame)
    countZ = numpy.sum(numpy.abs(numpy.diff(numpy.sign(frame)))) / 2

    return (numpy.float64(countZ)) / numpy.float64(count - 1.0)


def StHarmonic(sr, frame):
    #sr: sampling-rate, frame: audio signal
    M = numpy.round(0.016 * sr).astype(numpy.int) - 1
    R = numpy.correlate(frame, frame, mode = "full")

    g = R[len(frame) - 1]
    R = R[len(frame): -1]

    [a, ] = numpy.nonzero(numpy.diff(numpy.sign(R)))

    if len(a) == 0:
        m0 = len(R) - 1
    else:
        m0 = a[0]

    if M > len(R):
        M = len(R) - 1

    Gamma = numpy.zeros((M), dtype = numpy.float64)
    CSum = numpy.cumsum(frame ** 2)

    Gamma[m0: M] = R[m0: M]/ (numpy.sqrt((g * CSum[M:m0:-1])) + eps)

    ZCR = StZCR(Gamma)

    if ZCR > 0.15:
        HR = 0.0
        f0 = 0.0
    else:
        if len(Gamma) == 0:
            HR = 1.0
            blag = 0
            Gamma = numpy.zeros((M), dtype = numpy.float64)
        else:
            HR = numpy.max(Gamma)
            blag = numpy.argmax(Gamma)

        f0 = sr / (blag + eps)
#        if f0 > 5000:
##       F0 should be in the range of [75, 600]
#        if f0 > 500 or f0 < 100:
#            f0 = 0.0
#        if HR < 0.1:
#            f0 = 0.0

    return (HR, f0)


