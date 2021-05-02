# import numpy as np
# import matplotlib.pyplot as plt
# import genrator

# def drawCell(**parameter):
#     numCUE = len(parameter['ue_point'])
#     numD2D = len(parameter['tx_point'])

#     x0 = 0
#     y0 = 0
#     theta = np.arange(0, 2*np.pi, 0.01)
#     x1 = x0 + parameter['radius'] * np.cos(theta)
#     y1 = y0 + parameter['radius'] * np.sin(theta)

#     fig = plt.figure()
#     axes = fig.add_subplot(111)
#     axes.plot(x1, y1, color='blue',)
#     axes.set_xlabel("distance (m)")
#     axes.set_ylabel("distance (m)")
#     axes.axis('equal')

#     plt.scatter(0, 0, color="#888888", zorder=1000, s=8, label="BS")

#     #Draw CUE
#     plotted = 0
#     for i in range(numCUE):
#         if plotted == 0:
#             plt.scatter(parameter['ue_point'][i][0], parameter['ue_point'][i][1], color="#FF00FF", zorder=1000, s=6, label="CUE")
#             plotted = 1
#         else:
#             plt.scatter(parameter['ue_point'][i][0], parameter['ue_point'][i][1], color="#FF00FF", zorder=1000, s=6)

#     #Draw D2D
#     plotted = 0
#     for i in range(numD2D):
#         for j in range(parameter['numD2DReciver'][i]):
#             t,r = (parameter['tx_point'][i][0], parameter['tx_point'][i][1]), (parameter['rx_point'][i][j][0],parameter['rx_point'][i][j][1])

#             p1 = np.asarray(t)  
#             p2 = np.asarray(r)
#             alphas = np.arange(0, 1, 1 / 100)
#             diff = p2 - p1
#             line = [(p1 + (alpha * diff)) for alpha in alphas]

#             if(plotted == 0):
#                 plt.scatter(t[0], t[1], color="red", zorder=1000, s=8, label="D2D Transmitter")
#                 plt.scatter(r[0], r[1], color="green", zorder=1000, s=8, label="D2D Receiver")
#                 xx, yy = zip(*line)
#                 plt.plot(xx, yy, color="#888888", zorder = 999, linewidth=1)
#                 plotted = 1
#             else:
#                 plt.scatter(t[0], t[1], color="red", zorder=1000, s=8)
#                 plt.scatter(r[0], r[1], color="green", zorder=1000, s=8)
#                 xx, yy = zip(*line)
#                 plt.plot(xx, yy, color="#888888", zorder = 999, linewidth=1)
#     axes.legend(loc="upper right")
#     plt.show()

# def draw_test():
#     p_values = [25,37,46,29,38,29,38,29,38,29,38,38,29,29]
#     m_values = [18,29,38,29,38,29,38,29,38,29,38,29,38,29]
#     x_labels = [10,15,20,25,30,35,40,45,50,55,60,65,70,75]
    
#     plt.plot(x_labels, p_values,'s-',color = 'r', label="Proposed")
#     plt.plot(x_labels, m_values,'o-',color = 'g', label="GCRS")

#     # plt.title("Python 畫折線圖(Line chart)範例", x=0.5, y=1.03)

#     # 设置刻度字体大小
#     # plt.xticks(fontsize=10)

#     # plt.yticks(fontsize=10)

#     # 標示x軸(labelpad代表與圖片的距離)

#     plt.xlabel("D2D pair", labelpad = 15)

#     # 標示y軸(labelpad代表與圖片的距離)

#     plt.ylabel("Throughput", labelpad = 20)

#     # 顯示出線條標記位置

#     plt.legend(loc = "best")

#     plt.tight_layout()
#     # 畫出圖片
#     plt.savefig("Test.eps")
#     plt.show()
