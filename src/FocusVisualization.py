import matplotlib.pyplot as plt

#Need change the parasm to echo
def FocusVisualization(params, out):
    
    for f in params:
        sent = params[f]
        circles = []
        for param in sent:
            x = param["x"]
            y = param["y"]
            r = param["r"]
            p = param["p"]

            circles.append(plt.Circle((x, y), r, color = "yellow"))

        fig, ax = plt.subplots()
        for circle in circles:
            ax.add_artist(circle)
        ax.axis("equal")
    
        for param in sent:
            x = param["x"]
            y = param["y"]
            p = param["p"]
            ax.text(x, y, p)

#        ax.set_xlim([0, 1.0])
#        ax.set_ylim([0, 2.0])
        ax.axis([0, 1.8, 0, 2.0])

        fig.savefig("{}/{}.png".format(out, f))
        plt.close("all")
