import numpy as np
import matplotlib.pyplot as plt
import genrator

def drawCell(**parameter):
    numCUE = len(parameter['ue_point'])
    numD2D = len(parameter['tx_point'])

    x0 = 0
    y0 = 0
    theta = np.arange(0, 2*np.pi, 0.01)
    x1 = x0 + parameter['radius'] * np.cos(theta)
    y1 = y0 + parameter['radius'] * np.sin(theta)

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
            plt.scatter(parameter['ue_point'][i][0], parameter['ue_point'][i][1], color="#FF00FF", zorder=1000, s=6, label="CUE")
            plotted = 1
        else:
            plt.scatter(parameter['ue_point'][i][0], parameter['ue_point'][i][1], color="#FF00FF", zorder=1000, s=6)

    #Draw D2D
    plotted = 0
    for i in range(numD2D):
        for j in range(parameter['numD2DReciver'][i]):
            t,r = (parameter['tx_point'][i][0], parameter['tx_point'][i][1]), (parameter['rx_point'][i][j][0],parameter['rx_point'][i][j][1])

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

def draw_test():
    fixed_values1 = [525.660522 ,633.172286 ,716.835674 ,790.695622 ,782.893444 ,882.143046 ,992.58404 ,1082.217374 ,1056.872718 ,1192.83241]
    fixed_values2 = [525.045466 ,605.994134 ,679.932226 ,731.823092 ,827.03916 ,937.365108 ,1017.964052 ,1083.6777 ,1081.146828 ,1113.770642]
    fixed_value3 = [545.568432, 609.069646, 699.420256, 742.56326, 792.914766, 896.253694, 1002.271784, 985.07623,  1161.31785, 1137.322656]

    flexible_1000ms = [511.548636, 593.84806, 666.399189, 736.14967, 808.61329, 880.705499, 941.881326, 1006.75319, 1066.9373400000002, 1134.325642]
    flexible_500ms = [512.703684, 594.1119, 666.460892, 736.471596, 811.089578, 877.036142, 941.380454, 1011.842402, 1067.477328, 1129.793816]
    flexible_500ms_1 = [502.95154, 586.009308, 655.067642, 725.485298, 795.739872, 866.595186, 925.634746, 990.061358, 1051.194132, 1107.092976]
    flexible_1000ms_1 = [504.513089, 586.066517, 655.885513, 723.987047, 796.604173, 864.121465, 925.244553, 991.587952, 1051.021377, 1109.533657]
    
    x_labels = [30, 35, 40, 45,50, 55,60, 65, 70, 75]
    
    # plt.plot(x_labels, fixed_values1,'s-',color = 'r', label="fixed_1")
    # plt.plot(x_labels, fixed_values2,'o-',color = 'g', label="fixed_2")
    # plt.plot(x_labels, flexible_500ms,'^-', color = 'b', label="flexible_500ms")
    # plt.plot(x_labels, flexible_1000ms, 'd-', color = 'k', label="flexible_1000ms")

    plt.plot(x_labels, fixed_value3,'s-',color = 'r', label="fixed_1")
    plt.plot(x_labels, flexible_500ms_1,'^-', color = 'b', label="flexible_500ms")
    plt.plot(x_labels, flexible_1000ms_1, 'd-', color = 'k', label="flexible_1000ms")

    # plt.title("Python 畫折線圖(Line chart)範例", x=0.5, y=1.03)

    # 设置刻度字体大小
    # plt.xticks(fontsize=10)

    # plt.yticks(fontsize=10)

    # 標示x軸(labelpad代表與圖片的距離)

    plt.xlabel("D2D pair", labelpad = 15)
    plt.xticks(x_labels)

    # 標示y軸(labelpad代表與圖片的距離)

    plt.ylabel("Throughput (Mbps)", labelpad = 20)

    # 顯示出線條標記位置

    plt.legend(loc = "best")

    plt.tight_layout()
    # 畫出圖片
    plt.savefig("Test.eps")
    plt.show()

draw_test()