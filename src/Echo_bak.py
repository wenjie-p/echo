import sys
import os
import numpy
from AudioIO import ReadAudioFile
from BasicIO import load_data
from FocusVisualization import FocusVisualization
from ExtractF0s import ExtractF0s
from SegmentsExtraction import SegmentsExtraction

##This script has been deprecated because some unexpected value occurs in pitch extraction
##See the latest Echo.py which using the praat script to extract pitch instead.

def CalculateSt(phn, f0s, xmin, xmax):

    beg = int(xmin * 100)
    end = int(xmax * 100)
    vec = f0s[beg:end]
    #print (f0s)
    print("phn: {} xmin: {}, xmax: {} beg:{}, end: {}".format(phn, xmin, xmax, beg, end))
    print("vec: ", vec)

    vec = [e for e in vec if e != 0.0]
    if phn.endswith("3"):
        val = min(vec)
    else:
        val = max(vec)

    st = 12 * numpy.log2(val/ 100)

    return st


def FeatureAnalysis(f0s, phns):

    param = []
    for ele in phns:
        xmin = ele["xmin"]
        xmax = ele["xmax"]
        phn = ele["text"]
        dur = ele["dur"]

        st = CalculateSt(phn, f0s, xmin, xmax)
        val = {"phn": phn, "dur": dur, "st": st}
        param.append(val)

    return param
        

def GetParams(f0s, phns):

    params = {}

    for f in phns:
        if f not in f0s:
            print("File: {} not in wav dir!".format(f))
            exit(1)
        f0s_ = f0s[f]
        phns_ = phns[f]
        
        print("filename: {}".format(f))
        #print("F0s: ", f0s_)
        params[f] = FeatureAnalysis(f0s_, phns_)

    return params

def Normalization(x, y, p):

    x_len = sum(x)
    x_nor = [e/x_len for e in x]
    r = [e/2 for e in x_nor]
    x_ = numpy.cumsum(x_nor)
    x_axis = [x_[i]-r[i] for i in range(len(x_))]
    

    st_min = min(y)
    st_max = max(y)
    
    y_axis = [(e-st_min)/(st_max - st_min) + 0.5 for e in y]
    
    res = []
    for idx in range(len(r)):
        dic = {"x": x_axis[idx], "y": y_axis[idx], "r": r[idx], "p": p[idx]}
        res.append(dic)

    return res


def PostProcessingInfo(info):

    new_info = {}
    for f in info:
        params = info[f]
        x = []
        y = []
        p = []
        
        for param in params:
            x.append(param["dur"])
            y.append(param["st"])
            p.append(param["phn"])
        #print("filename: {}".format(f))
        #print("x: ", x)
        #print("y: ", y)
        #print("p: ", p)
        new_params = Normalization(x, y, p)
        new_info[f] = new_params

    return new_info


def main(wav, txt, out):

    f0s = ExtractF0s(wav)
    phns = SegmentsExtraction(txt)

    info = GetParams(f0s, phns)

    info = PostProcessingInfo(info)
    
    FocusVisualization(info, out)

if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: {} wav txt out".format(sys.argv[0]))
        exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
