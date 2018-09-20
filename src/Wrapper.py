import sys
import os


def ProcessingDir(func):
    
    def Wrapper(path):
        res = {}
        for f in os.listdir(path):
            k = f.split(".")[0]
            fp = "/".join([path, f])
            res[k] = func(fp)
        return res

    return Wrapper


