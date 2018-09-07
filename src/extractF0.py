import sys
sys.path.append("./")
from pyAudioAnalysis.audioFeatureExtraction import stHarmonic
from pyAudioAnalysis import audioBasicIO
import numpy
import codecs
import os
import matplotlib.pyplot as plt
plt.switch_backend("agg")

f = codecs.open("pinyin/finals", "r", encoding = "utf8")
finals = set([x.strip() for x in f.readlines()])
f.close()

f = codecs.open("pinyin/initials", "r", encoding = "utf8")
initials = set([x.strip() for x in f.readlines()])
f.close()

sil = set(["sp", "sil"])
def isFinal(phn):
    return phn in finals

sp = set(["sp", "sil"])

def process_dir(ori_func):
    def wrapper_func(path):
        info = {}
        for f in os.listdir(path):

            key = f.split(".")[0]
            
            val, fs = ori_func(path + os.sep + f)
            info[key] = val
        return info, fs

    return wrapper_func

@process_dir
def extractF0(wav):
    [Fs, signal] = audioBasicIO.readAudioFile(wav)
    signal = numpy.double(signal)

    signal = signal / (2.0**15)
    DC = signal.mean()
    MAX = (numpy.abs(signal)).max()
    signal = (signal - DC)/(MAX + 0.0000000001)

    N = len(signal)
    print N
    curPos = 0
    Win = int(0.020 * Fs)
    Step = int(0.010 * Fs)
    
    F0s = []
    while (curPos + Win - 1 < N):
        x = signal[curPos:curPos + Win]
        curPos += Step
        _, F0 = stHarmonic(x, Fs)
        F0s.append(F0)

    return F0s, Fs

@process_dir
def extractFinals(text):
    f = codecs.open(text, "r", encoding = "utf8")
    content = f.readlines()
    f.close()
    xmin = 0
    xmax = 0
    res = []
    pre = ""
    beg = 0.0
    sy_t = 0
    total = 0.0
    started = False
    for line in content:

        line = line.strip().split(" ")
        if line[0] == "name":
            if line[-1].strip('"') == "SY":
                started = True
            else:
                started = False
        if not started:
            continue
        if line[0] == "xmin":
            xmin = float(line[-1])
        elif line[0] == "xmax":
            xmax = float(line[-1])
            if xmax > total:
                total = xmax
        elif line[0] == "text":
            text = line[-1].strip('"')
            if text is None:
                continue
            if text in sp:
                if pre in finals:
                    #sp_dur += (xmax-xmin)
                    pass
                elif pre is "":
                    pass
                else:
                    print "Error: pre is {}, cur is {}".format(pre, text)
                    exit(1)
            elif text in finals:
                if pre in initials:
                    dur = xmax - beg
                    dic = {}
                    
                    dic["sy"] = {"beg": beg, "end": xmax, "phn": text}
                    dic["final"] = {"beg": xmin, "end": xmax}
                    sy_t += (xmax - beg)
                    res.append(dic)
                   
                elif pre in finals:
                    dic = {}
                    dic["final"]  = {"beg": xmin, "end": xmax}
                    dic["sy"] = {"beg": xmin, "end": xmax, "phn": text}
                    res.append(dic)
                    sy_t += xmax - xmin
                    
                else:
                    print "error: cur is {} pre is {}".format(text, pre)
                    exit(1)
            elif text in initials:
                beg = xmin
            else:
                pass
                #print "error: {} in the lex".format(text) 
                #exit(1)
            pre = text

    res.append([sy_t, total])

    return res, ""

def pickMax(vec):
    val = vec[0]
    for v in vec[1:]:
        if v > val:
            val = v
    return val

def pickMin(vec):
    val = vec[0]

    for v in vec[1:]:
        if v < val:
            val = v

    return val

def calculateParams(vec, beg, end, final, fs):
    #how to represent a circle, just a centroid and a val?
#    print "beg:{} end:{} fs:{}".format(beg, end, fs)
    beg = int(beg * 100)
    end = int(end * 100)
    v = vec[beg:end]
#    print "total: {}, beg:{} end:{}".format(len(vec), beg, end)
    
    val = 0
    if final.endswith("3"):
        val = pickMin(v)
    else:
        val = pickMax(v)
    val = 12 * numpy.log2(val/100)

    return val


def calculateST(vec, finals, fs):
    temp = []
 
    print finals
    for final in finals[:-1]:
        phn = final["sy"]["phn"]
        xmin = final["final"]["beg"]
        xmax = final["final"]["end"]
        st = calculateParams(vec, xmin, xmax, phn, fs)
        temp.append(st)
    
    t = finals[-1][-1]
    sy_t = finals[-1][0]
    k = 1.0 / sy_t
    print sy_t

    max_st = max(temp)
    min_st = min(temp)

    res = []
    dur = 0
    for idx in range(len(finals)-1):
        final = finals[idx]["sy"]["phn"]
        beg = finals[idx]["sy"]["beg"]
        end = finals[idx]["sy"]["end"]
        d = (end - beg)
        x = (dur + d/2) * k
        dur += d
        r = (end-beg)/2 * k
        y = (temp[idx] - min_st)/(max_st - min_st) + 0.5
        print "beg:{} end:{} st:{} dur:{}".format(str(beg), str(end), str(temp[idx]), str(dur))
        print "x:{} y:{} r:{} t:{} t_st:{}".format(str(x), str(y), str(r), str(t), str(max_st))
        res.append({"phn": final, "x": x, "y": y, "r": r})
   
    return res

def draw(info):
    for f in info:
        sent = info[f]
        circles = []
        for param in sent:
            x = param["x"]
            y = param["y"]
            r = param["r"]
#            print "x:{} y:{} r:{}".format(str(x), str(y), str(r))
            circles.append(plt.Circle((x,y), r, color = "yellow"))
        fig, ax = plt.subplots()
        for circle in circles:
            ax.add_artist(circle)
        ax.axis("equal")
        
        ax.axis([0,2.0,0,2.0 ])
        #plt.show()
        fig.savefig("{}.png".format(f))
        plt.close("all")


def main(wav_dir, lab_dir):
    wav_info, fs = extractF0(wav_dir)
    lab_info, _ = extractFinals(lab_dir)
    res = {}
    for k in wav_info:
        vec = wav_info[k]
        finals = lab_info[k]
        params =  calculateST(vec, finals, fs)
        res[k] = params
    draw(res)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage {} wav text".format(sys.argv[0])
        exit(1)

    main(sys.argv[1], sys.argv[2])
