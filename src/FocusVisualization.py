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

        ax.axis([0, 2.0, 0, 2.0])
        fig.savefig("{}/{}.png".format(out, f))
        plt.close("all")
