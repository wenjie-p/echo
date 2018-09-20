import os
import subprocess
import codecs
from BasicIO import load_data
from numpy import log2
from Wrapper import ProcessingDir


def Pitch2St(data):

    sts = {}
    for line in data[1:]:
        line = line.strip().split(",")
        try:
            f0 = float(line[1])
        except:
            continue
        t = float(line[0])
        idx = int(t/0.01)
        st = 12 * log2(f0/100)
        sts[idx] = st

    return sts


def GenerateStFromPitch(wav):

    head, tail = os.path.split(wav)
    pitch = "../pitch" + os.sep + tail.replace("wav", "pitch")
    if not os.path.exists(pitch):
        print("Pitch of file: {} not exists.".format(pitch))
        exit(1)

    data = load_data(pitch)
    sts = Pitch2St(data)

    return sts


def GeneratePitch(wav):

    if not os.path.exists("../pitch"):
        os.mkdir("../pitch")
    
    head, tail = os.path.split(wav)
    
    pitch_name = tail.replace(".wav", "")
    pitch_dir = "../pitch"
    pitch = pitch_dir + os.sep + pitch_name + ".pitch"

    if os.path.exists(pitch):
        return 
    praat = "/Applications/Praat.app/Contents/MacOS/Praat"

    subprocess.call([praat, "--run", "ExtractF0.praat", wav, pitch_name, pitch_dir])


@ProcessingDir
def StExtraction(wav):

    GeneratePitch(wav)
    sts = GenerateStFromPitch(wav)

    return sts
