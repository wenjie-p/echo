import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

idx = 0

def ToDiscreteVal(x, pos):
    global idx
    str_ = str(idx+1)
    idx += 1
    return str_
#Need change the parasm to echo
def FocusVisualization(params, out):

    for f in params:
        sent = params[f]
        circles = []
        r_min = sent["r_min"]
        for param in sent["param"]:
            x = param["x"] 
            y = param["y"] + r_min
            r = param["r"]
            p = param["p"]

            circles.append(plt.Circle((x, y), r, color = "yellow"))

        fig, ax = plt.subplots()

        #print(f)

        for circle in circles:
            ax.add_artist(circle)
#        ax.axis("equal")
    
        x_axis = []
        for param in sent["param"]:
            x = param["x"]
            y = param["y"]+r_min
            p = param["p"]
            ax.text(x,y,".", fontsize = 16)
            ax.text(x+0.02, y, p)
            x_axis.append(x)
        ax.set_aspect("equal", "box")

        k = 1/sent["k"]
        st_min = sent["st_min"]
        b = st_min - k*r_min

        y_max, y_min = sent["param"][0]["y_max"], sent["param"][0]["y_min"]
        x_max = y_max - y_min
        ax.set_xticks(x_axis)
        plt.gca().xaxis.set_major_formatter(FuncFormatter(ToDiscreteVal))
        ax.set_xlabel("the i-th syllbale: i")
        ax.set_ylim([y_min, y_max])
        ax.set_ylabel("semitone value: st")
        to_origin = lambda y, pos: str(round(k*y + b, 2))
        plt.gca().yaxis.set_major_formatter(FuncFormatter(to_origin))

        fig.savefig("{}/{}.png".format(out, f))
        plt.close("all")
        global idx 
        idx = 0
