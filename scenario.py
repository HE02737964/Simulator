import numpy as np
import json
import matplotlib.pyplot as plt


def genrator():
###############################################初始化########################################################
    with open("config.json", "r") as f:
        config = json.load(f)
        f.close()

    numCUE = config["numCUE"]                                                   #CUE的數量
    numD2D = config["numD2D"]                                                   #D2D的數量
    maxReciver = config["maxReciver"]                                     #D2D Rx的最大數量
    radius = config["radius"]                                                   #Cell半徑(m)
    d2dDistance = config["d2dDistance"]                                         #D2D最長距離

    numD2DReciver = np.random.randint(low=1, high=maxReciver+1, size=numD2D) #根據參數隨機生成D2D Rx數量 
    dis_C2BS = np.zeros((numCUE))                                       #一維陣列, CUE - BS的距離
    dis_D = np.zeros((numD2D, maxReciver))                              #二維陣列, D2D Tx - RX的距離
    dis_C2D = np.zeros((numCUE, numD2D, maxReciver))                    #三維陣列, CUE - D2D所有RX的距離
    dis_D2C = np.zeros((numD2D, numCUE))                                #二維陣列, D2D Tx - CUE的距離
    dis_DiDj = np.zeros((numD2D, numD2D, maxReciver))                   #三維陣列, D2D Tx i - D2D RX j的距離
    dis_D2BS = np.zeros((numD2D))                                       #一維陣列, D2D Tx - BS的距離

#############################################生成CUE位置######################################################
    c_x = 2*radius*np.random.rand(1,numCUE)-radius                      #隨機生成CUE的x座標
    c_y = 2*radius*np.random.rand(1,numCUE)-radius                      #隨機生成CUE的y座標
    location = (c_x**2 + c_y**2).flatten()                              #.flatten() 轉為一維陣列
    index_out = np.where(location > radius**2)[0]                       #找出超過BS範圍的點的index, [0]轉為一維陣列
    len1 = len(index_out)                                               #超過BS範圍的點的數量
    c_x = np.delete(c_x, index_out)                                     #超過BS範圍的點移除
    c_y = np.delete(c_y, index_out)

    while len1:                                                         #重新生成點,直到數量滿足
        xt = 2*radius*np.random.rand(1,len1)-radius
        yt = 2*radius*np.random.rand(1,len1)-radius
        index_tmp = np.where((xt**2+yt**2).flatten() > radius**2)[0]
        len1 = len(index_tmp)
        xt = np.delete(xt, index_tmp)
        yt = np.delete(yt, index_tmp)
        c_x = np.append(c_x, xt)
        c_y = np.append(c_y, yt)

        # xt = np.delete(xt, 0)                                           #清空暫存的座標
        # yt = np.delete(yt, 0)

#############################################生成D2D Tx位置####################################################
    d_x = 2*radius*np.random.rand(1,numD2D)-radius                      #隨機生成D2D Tx的x座標
    d_y = 2*radius*np.random.rand(1,numD2D)-radius                      #隨機生成D2D Tx的y座標
    location = (d_x**2 + d_y**2).flatten()
    index_out = np.where(location > radius**2)[0]
    len1 = len(index_out)
    d_x = np.delete(d_x, index_out)
    d_y = np.delete(d_y, index_out)

    while len1:
        xt = 2*radius*np.random.rand(1,len1)-radius
        yt = 2*radius*np.random.rand(1,len1)-radius
        index2 = np.where((xt**2+yt**2).flatten() > radius**2)[0]
        len1 = len(index2)
        xt = np.delete(xt, index2)
        yt = np.delete(yt, index2)
        d_x = np.append(d_x, xt)
        d_y = np.append(d_y, yt)

        # xt = np.delete(xt, 0)
        # yt = np.delete(yt, 0)

#############################################生成D2D Rx位置####################################################
    r_x = np.zeros((numD2D, max(numD2DReciver)))
    r_y = np.zeros((numD2D, max(numD2DReciver)))

    for i in range(numD2D):
        for reciver in range(numD2DReciver[i]):
            while True:                                                 #一直重新生成座標,直到滿足在BS範圍內
                u = np.random.uniform(0,1)
                v = np.random.uniform(0,1)
                w = d2dDistance * np.sqrt(u)
                t = 2 * np.pi * v
                x = w * np.cos(t)
                y = w * np.sin(t)
                rx = x + d_x[i]
                ry = y + d_y[i]
                if ( ((rx**2)+(ry**2)) < radius**2):
                    r_x[i][reciver] = rx
                    r_y[i][reciver] = ry
                    break

###############################################系統環境圖######################################################
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

    plotted = 0
    for i in range(numCUE):
        if plotted == 0:
            plt.scatter(c_x[i], c_y[i], color="#FF00FF", zorder=1000, s=6, label="CUE")
            plotted = 1
        else:
            plt.scatter(c_x[i], c_y[i], color="#FF00FF", zorder=1000, s=6)

    plotted = 0
    for i in range(numD2D):
        for j in range(numD2DReciver[i]):
            t,r = (d_x[i], d_y[i]), (r_x[i][j], r_y[i][j])

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

###########################################計算各裝置間的距離##################################################
    dis_C2BS = np.sqrt( (c_x**2 + c_y**2) )

    for tx in range(numD2D):
        for Rx in range(numD2DReciver[tx]):
            dis_D[tx][Rx] = np.sqrt( (d_x[tx] - r_x[tx][Rx])**2 + (d_y[tx] - r_y[tx][Rx])**2 )

    for tx in range(numCUE):
        for d2d in range(numD2D):
            for rx in range(numD2DReciver[d2d]):
                dis_C2D[tx][d2d][rx] = np.sqrt( (c_x[tx] - r_x[d2d][rx])**2 + (c_y[tx] - r_y[d2d][rx])**2 )

    for tx in range(numD2D):
        for rx in range(numCUE):
            dis_D2C[tx][rx] = np.sqrt( (d_x[tx] - c_x[rx])**2 + (d_y[tx] - c_y[rx])**2 )

    for i in range(numD2D):
        for j in range(numD2D):
            for rx in range(numD2DReciver[j]):
                dis_DiDj[i][j][rx] = np.sqrt( (d_x[i] - r_x[j][rx])**2 + (d_y[i] - r_y[j][rx])**2 )

    dis_D2BS = np.sqrt( (d_x**2 + d_y**2) )

    return dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_DiDj, dis_D2BS

if __name__ == '__main__':
    genrator()