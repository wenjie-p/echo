import sys
import shutil
import os
import numpy
from AudioIO import ReadAudioFile
from BasicIO import load_data
from FocusVisualization import FocusVisualization
from ExtractF0s import ExtractF0s
from SegmentsExtraction import SegmentsExtraction
from ExtractStUsingPraat import StExtraction


def GetSt(phn, sts, xmin, xmax):

    beg = int(xmin / 0.01)
    end = int(xmax / 0.01)
    
    vec = []
    for idx in list(range(beg, end+1)):
        if idx in sts:
            vec.append(sts[idx])


    if phn.endswith("3"):
        st = min(vec)
    else:
        st = max(vec)

    return st


def FeatureAnalysis(sts, phns):

    param = []
    for ele in phns:
        xmin = ele["xmin"]
        xmax = ele["xmax"]
        phn = ele["text"]
        dur = ele["dur"]

        st = GetSt(phn, sts, xmin, xmax)
        val = {"phn": phn, "dur": dur, "st": st}
        param.append(val)

    return param
        

def GetParams(sts, phns):

    params = {}

    for f in phns:
        if f not in sts:
            print("File: {} not in wav dir!".format(f))
            exit(1)
        sts_ = sts[f]
        phns_ = phns[f]
        
        print("filename: {}".format(f))
        #print("F0s: ", f0s_)
        params[f] = FeatureAnalysis(sts_, phns_)

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


def PostProcessingDir(d):

    if os.path.exists(d):
        shutil.rmtree(d)
        

def main(wav, txt, out):

    sts = StExtraction(wav)

    phns = SegmentsExtraction(txt)

    info = GetParams(sts, phns)

    info = PostProcessingInfo(info)
    
    FocusVisualization(info, out)

    PostProcessingDir("../pitch")


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: {} wav txt out".format(sys.argv[0]))
        exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
