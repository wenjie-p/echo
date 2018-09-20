import codecs
from BasicIO import load_data, write_data
from Wrapper import ProcessingDir


def SaintCheck(durs):

    for i in range(1,len(durs)):
        if durs[i-1][1] != durs[i][0]:
            return False

    return True


def PostProcessingDuration(durs):

    dur = 0.0

    if len(durs) > 1:
        if not SaintCheck(durs):
            print("Finals are not continious...")
            exit(1)

    dur = durs[-1][1] - durs[0][0]
    return dur


def GetFinalInfo(xmin, xmax, SYItems, finals):

    item = []
    
    text = []
    durs = []

    sy = [ele for ele in SYItems if ele["xmin"] >= xmin and ele["xmax"] <= xmax]
    #print (xmin,xmax)
    #print(PYItems)
    #print(finals)
    for ele in sy:
        if ele["text"] in finals:
            text.append(ele["text"])
            durs.append((ele["xmin"], ele["xmax"]))

    dur = PostProcessingDuration(durs)
    
    return {"text": " ".join(text), "xmin": durs[0][0], "xmax": durs[-1][1]}


def LoadConf(fp):

    data = load_data(fp)
    finals = set([x.strip() for x in data])

    return finals


def ProcessingItems(PYItems, SYItems):
    
    finals = LoadConf("../conf/finals")
    sil = set(["sp", "sil"])
    
    items = []

    for py in PYItems:
        if py["text"] in sil:
            continue
        py_dur = py["xmax"] - py["xmin"]

        item = GetFinalInfo(py["xmin"], py["xmax"], SYItems, finals)
        item["dur"] = py_dur
        
        items.append(item)

    return items


def Extraction(tier):

    items = []

    for idx in list(range(0, len(tier), 4)):
        interval = [line.strip().split() for line in tier[idx: idx + 4]]
        xmin = float(interval[1][-1])
        xmax = float(interval[2][-1])
        text = interval[-1][-1].split('"')[1]

        item = {"text": text, "xmin": xmin, "xmax": xmax}
        items.append(item)

    return items


def GetInfo(name, content):

    t_name = content[2].strip().split()[2].strip('"')
    if t_name == name:
        t_size = int(content[5].strip().split()[-1])
        return t_size

    print("Something wrong. Check the TextGrid format carefully...")
    print("The tier name is {} and the first element is {}".format(t_name, content[0]))
    exit(1)


def SplitItems(content):

    
    py_size = GetInfo("PY", content)
    PY = content[6: py_size * 4 + 6]

    content = content[6 + py_size * 4:]
    sy_size = GetInfo("SY", content)
    SY = content[6: sy_size * 4 + 6]

    return PY, SY


def ItemExtraction(textgrid):

    content = textgrid[8:]

    PY, SY = SplitItems(content)
    
    PYItems = Extraction(PY)
    SYItems = Extraction(SY)

    #print(PYItems)
    #print(SYItems)

    items = ProcessingItems(PYItems, SYItems)

    return items

@ProcessingDir
def SegmentsExtraction(fp):

    textgrid = load_data(fp)

    segs = ItemExtraction(textgrid)

    return segs
