import numpy as np
import matplotlib.pyplot as plt
import genrator

def drawCell(radius, ue_point, tx_point, rx_point, numD2DReciver):
    numCUE = len(ue_point)
    numD2D = len(tx_point)

    x0 = 0
    y0 = 0
    theta = np.arange(0, 2*np.pi, 0.01)
    x1 = x0 + radius * np.cos(theta)
    y1 = y0 + radius * np.sin(theta)

    fig = plt.figure()
    axes = fig.add_subplot(111)
    axes.plot(x1, y1, color='blue',)
    axes.set_xlabel("distance (m)")
    axes.set_ylabel("distance (m)")
    axes.axis('equal')

    plt.scatter(0, 0, color="#888888", zorder=1000, s=8, label="BS")

    #Draw CUE
    plotted = 0
    for i in range(numCUE):
        if plotted == 0:
            plt.scatter(ue_point[i][0], ue_point[i][1], color="#FF00FF", zorder=1000, s=6, label="CUE")
            plotted = 1
        else:
            plt.scatter(ue_point[i][0], ue_point[i][1], color="#FF00FF", zorder=1000, s=6)

    #Draw D2D
    plotted = 0
    for i in range(numD2D):
        for j in range(numD2DReciver[i]):
            t,r = (tx_point[i][0], tx_point[i][1]), (rx_point[i][j][0], rx_point[i][j][1])

            p1 = np.asarray(t)  
            p2 = np.asarray(r)
            alphas = np.arange(0, 1, 1 / 100)
            diff = p2 - p1
            line = [(p1 + (alpha * diff)) for alpha in alphas]

            if(plotted == 0):
                plt.scatter(t[0], t[1], color="red", zorder=1000, s=8, label="D2D Transmitter")
                plt.scatter(r[0], r[1], color="green", zorder=1000, s=8, label="D2D Receiver")
                xx, yy = zip(*line)
                plt.plot(xx, yy, color="#888888", zorder = 999, linewidth=1)
                plotted = 1
            else:
                plt.scatter(t[0], t[1], color="red", zorder=1000, s=8)
                plt.scatter(r[0], r[1], color="green", zorder=1000, s=8)
                xx, yy = zip(*line)
                plt.plot(xx, yy, color="#888888", zorder = 999, linewidth=1)
    axes.legend(loc="upper right")
    plt.show()