import os
import numpy
import aifc
from pydub import AudioSegment

def ReadAudioFile(path):
    #Take an audio file as input, sampling-rate and audio signal returned
    
    extention = os.path.splitext(path)[1]

    try:
        if extention.lower() == ".aif" or extention.lower() == "aiff":
            sig = aifc.open(path, "r")
            nframes = sig.getnframes()
            strsig = sig.readframes(nframes)
            x = numpy.fromstring(strsig, numpy.short).byteswap()
            sr = sig.getframerate()

        elif extention.lower() == ".mp3" or extention.lower() == ".wav" or extention.lower() == "au" or extention.lower() == "ogg":
            try:
                audiof = AudioSegment.from_file(path)
            except:
                print("Error occurs when decoding. DECODING FAILED.")
                return (-1, -1)
            
            if audiof.sample_width == 2:
                data = numpy.fromstring(audiof._data, numpy.int16)
            elif audiof.sample_width == 4:
                data = numpy.fromstring(audiof._data, numpy.int32)
            else:
                return (-1, -1)

            sr = audiof.frame_rate
            x = []

            for chn in list(range(audiof.channels)):
                x.append(data[chn::audiof.channels])
            x = numpy.array(x).T

        else:
            print("Unknown audio file format: {}".format(extention))
            return (-1, -1)

    except IOError:
        print("Error occured in reading audio file format: {}".format(extention))
        return (-1, -1)
        
    if x.ndim == 2:
        if x.shape[1] == 1:
            x = x.flatten()

    return sr, x


