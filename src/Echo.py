import sys
import shutil
import os
import numpy
from AudioIO import ReadAudioFile
from BasicIO import load_data, write_data
from FocusVisualization import FocusVisualization
from ExtractF0s import ExtractF0s
from SegmentsExtraction import SegmentsExtraction
from ExtractStUsingPraat import StExtraction

def RemoveInvaildST(vec):

    std = numpy.std(vec)

    mean = numpy.mean(vec)
    bot = mean - 2*std
    top = mean + 2*std

    new = [e for e in vec if e > bot and e < top]

    return new

def GetSt(phn, sts, xmin, xmax):

    beg = int(xmin / 0.01)
    end = int(xmax / 0.01)
    
    vec = []
    for idx in list(range(beg, end+1)):
        if idx in sts:
            vec.append(sts[idx])
    #print("{}: ".format(phn), vec)

    #print("beg: {} end: {} ".format(beg, end))
    #print("sts: ", sts)
    if len(vec) == 0:
        return 0.0, 0.0
    vec = RemoveInvaildST(vec)
    #print(vec)

   # if phn.endswith("3"):
   #     st = min(vec)
   # else:
   #     st = max(vec)

    return max(vec), min(vec)

def SmoothingST(param):

    new = []
    for idx in range(len(param)):
        dic = param[idx]
        st = dic["st"]
        if st == 0.0:
            if idx > 0:
                st = param[idx-1]["st"]
            else:
                st = param[idx+1]["st"]
        dic["st"] = st
        new.append(dic)

    return new


def FeatureAnalysis(sts, phns):

    param = []
    sen_st_min = 999

    for ele in phns:
        xmin = ele["xmin"]
        xmax = ele["xmax"]
        phn = ele["text"]
        dur = ele["dur"]

        #print("phn: {}".format(phn))
        #print("xmin: {}, xmax: {}".format(xmin, xmax))
        st_max, st_min = GetSt(phn, sts, xmin, xmax)
        if st_min != 0.0 and st_min < sen_st_min:
            sen_st_min = st_min

        val = {"phn": phn, "dur": dur, "st": st_max}
        param.append(val)

    param = SmoothingST(param)
    return param, sen_st_min
        
def SaveInfo(f, param):

    vec = []
    first = "\t".join(["text", "duration", "semitone"])
    vec.append(first)

    for val in param:
        ele = "\t".join([val["phn"], str(val["dur"]), str(val["st"])])
        vec.append(ele)

    write_data(f, vec)


def GetParams(sts, phns, out):

    params = {}

    for f in phns:
        if f not in sts:
            print("File: {} not in wav dir!".format(f))
            exit(1)
        sts_ = sts[f]
        phns_ = phns[f]
        
        #print("filename: {}".format(f))
        #print("F0s: ", f0s_)
        params[f] = {}
        params[f]["param"], params[f]["st_min"] = FeatureAnalysis(sts_, phns_)
        
        fp = out + os.sep + f + ".dat"
        SaveInfo(fp, params[f]["param"])

    return params


def CalculateK(y, r):

    yy_max = max(y)
    yy_min = min(y)
    k = 1/(yy_max - yy_min)

    return k, yy_max, yy_min


def Normalization(x, y, p):

    x_len = sum(x)
    x_nor = [e/x_len for e in x]
    r = [e/2 for e in x_nor]
    x_ = numpy.cumsum(x_nor)
    x_axis = [x_[i]-r[i] for i in range(len(x_))]
    
    r_ori = [e/2 for e in x]
    k, yy_max, yy_min = CalculateK(y, r_ori)

    y_axis = [k*(e - yy_min) for e in y]
    y_max = -99
    y_min = 99
    p1 = p2 = 0
    for i in range(len(y_axis)):
        a = y_axis[i] + r[i]
        b = y_axis[i] - r[i]
        if a > y_max :
            y_max = a
            p1 = i
        if b < y_min :
            y_min = b
            p2 = i
    yy_max = y[p1] + r_ori[p1]
    yy_min = y[p2] - r_ori[p2]
    
    #print ("y_axis:", y_axis)
    #print("r:", r)
    
    res = []
    for idx in range(len(r)):
        dic = {"x": x_axis[idx],"y_max": y_max+r[p2], "y_min": y_min+r[p2], "y": y_axis[idx], "r": r[idx], "p": p[idx]}
        res.append(dic)

    return res, yy_max, yy_min, r[p2], k


def PostProcessingInfo(info):

    new_info = {}
    for f in info:
        params = info[f]
        x = []
        y = []
        p = []
        
        for param in params["param"]:
            x.append(param["dur"])
            y.append(param["st"])
            p.append(param["phn"])
        print("filename: {}".format(f))
        #print("x: ", x)
        #print("y: ", y)
        #print("p: ", p)
        new_params, yy_max, yy_min, r_min, k = Normalization(x, y, p)
        new_info[f] = {}
        new_info[f]["param"] = new_params
        new_info[f]["st_min"] = params["st_min"]
        new_info[f]["st_max"] = yy_max
        new_info[f]["st_min"] = yy_min
        new_info[f]["r_min"] = r_min
        new_info[f]["k"] = k

    return new_info


def PostProcessingDir(d):

    if os.path.exists(d):
        shutil.rmtree(d)
        

def main(wav, txt, out, gender):

    sts = StExtraction([wav, gender])

    phns = SegmentsExtraction(txt)

    info = GetParams(sts, phns, out)

    info = PostProcessingInfo(info)
    
    FocusVisualization(info, out)

    PostProcessingDir("../pitch")


if __name__ == "__main__":

    if len(sys.argv) != 5:
        print("Usage: {} wav txt out gender".format(sys.argv[0]))
        exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
