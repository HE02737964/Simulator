import numpy as np
import json
import matplotlib.pyplot as plt

class Genrator():
###############################################初始化########################################################
    def __init__(self):
        with open("config.json", "r") as f:
            config = json.load(f)
            f.close()

        self.numCUE = config["numCUE"]                                                          #CUE的數量
        self.numD2D = config["numD2D"]                                                          #D2D的數量
        self.maxReciver = config["maxReciver"]                                                  #D2D Rx的最大數量
        self.radius = config["radius"]                                                          #Cell半徑(m)
        self.d2dDistance = config["d2dDistance"]                                                #D2D最長距離
        self.c_x = np.zeros(self.numCUE)                                                        #CUE的x座標
        self.c_y = np.zeros(self.numCUE)                                                        #CUE的y座標
        self.d_x = np.zeros(self.numD2D)                                                        #D2D Tx的x座標
        self.d_y = np.zeros(self.numD2D)                                                        #二維陣列, D2D Rx的x座標
        self.r_x = np.zeros((self.numD2D, self.maxReciver))                                     #D2D Rx的x座標
        self.r_y = np.zeros((self.numD2D, self.maxReciver))

        self.numD2DReciver = np.random.randint(low=1, high=self.maxReciver+1, size=self.numD2D) #根據參數隨機生成D2D Rx數量 
        self.dis_C2BS = np.zeros((self.numCUE))                                                 #一維陣列, CUE - BS的距離
        self.dis_D = np.zeros((self.numD2D, self.maxReciver))                                   #二維陣列, D2D Tx - RX的距離
        self.dis_C2D = np.zeros((self.numCUE, self.numD2D, self.maxReciver))                    #三維陣列, CUE - D2D所有RX的距離
        self.dis_D2C = np.zeros((self.numD2D, self.numCUE))                                     #二維陣列, D2D Tx - CUE的距離
        self.dis_BS2D = np.zeros((self.numD2D, self.maxReciver))                             #三維陣列, BS - D2D所有RX的距離
        self.dis_DiDj = np.zeros((self.numD2D, self.numD2D, self.maxReciver))                   #三維陣列, D2D Tx i - D2D RX j的距離
        self.dis_D2BS = np.zeros((self.numD2D))                                                 #一維陣列, D2D Tx - BS的距離    

#############################################生成CUE位置######################################################
    def genrator(self):
        self.c_x = 2*self.radius*np.random.rand(1,self.numCUE)-self.radius                      #隨機生成CUE的x座標
        self.c_y = 2*self.radius*np.random.rand(1,self.numCUE)-self.radius                      #隨機生成CUE的y座標
        location = (self.c_x**2 + self.c_y**2).flatten()                                        #.flatten() 轉為一維陣列
        index_out = np.where(location > self.radius**2)[0]                                      #找出超過BS範圍的點的index, [0]轉為一維陣列
        len1 = len(index_out)                                                                   #超過BS範圍的點的數量
        self.c_x = np.delete(self.c_x, index_out)                                               #超過BS範圍的點移除
        self.c_y = np.delete(self.c_y, index_out)

        while len1:                                                                             #重新生成點,直到數量滿足
            xt = 2*self.radius*np.random.rand(1,len1)-self.radius
            yt = 2*self.radius*np.random.rand(1,len1)-self.radius
            index_tmp = np.where((xt**2+yt**2).flatten() > self.radius**2)[0]
            len1 = len(index_tmp)
            xt = np.delete(xt, index_tmp)
            yt = np.delete(yt, index_tmp)
            self.c_x = np.append(self.c_x, xt)
            self.c_y = np.append(self.c_y, yt)

#############################################生成D2D Tx位置####################################################
        self.d_x = 2*self.radius*np.random.rand(1,self.numD2D)-self.radius                      #隨機生成D2D Tx的x座標
        self.d_y = 2*self.radius*np.random.rand(1,self.numD2D)-self.radius                      #隨機生成D2D Tx的y座標
        location = (self.d_x**2 + self.d_y**2).flatten()
        index_out = np.where(location > self.radius**2)[0]
        len1 = len(index_out)
        self.d_x = np.delete(self.d_x, index_out)
        self.d_y = np.delete(self.d_y, index_out)

        while len1:
            xt = 2*self.radius*np.random.rand(1,len1)-self.radius
            yt = 2*self.radius*np.random.rand(1,len1)-self.radius
            index2 = np.where((xt**2+yt**2).flatten() > self.radius**2)[0]
            len1 = len(index2)
            xt = np.delete(xt, index2)
            yt = np.delete(yt, index2)
            self.d_x = np.append(self.d_x, xt)
            self.d_y = np.append(self.d_y, yt)

#############################################生成D2D Rx位置####################################################
        self.r_x = np.zeros((self.numD2D, max(self.numD2DReciver)))
        self.r_y = np.zeros((self.numD2D, max(self.numD2DReciver)))

        for i in range(self.numD2D):
            for reciver in range(self.numD2DReciver[i]):
                while True:                                                                     #一直重新生成座標,直到滿足在BS範圍內
                    u = np.random.uniform(0,1)
                    v = np.random.uniform(0,1)
                    w = self.d2dDistance * np.sqrt(u)
                    t = 2 * np.pi * v
                    x = w * np.cos(t)
                    y = w * np.sin(t)
                    rx = x + self.d_x[i]
                    ry = y + self.d_y[i]
                    if ( ((rx**2)+(ry**2)) < self.radius**2):
                        self.r_x[i][reciver] = rx
                        self.r_y[i][reciver] = ry
                        break

###########################################計算各裝置間的距離##################################################
        self.dis_C2BS = np.sqrt( (self.c_x**2 + self.c_y**2) ) / 1000

        for tx in range(self.numD2D):
            for Rx in range(self.numD2DReciver[tx]):
                self.dis_D[tx][Rx] = np.sqrt( (self.d_x[tx] - self.r_x[tx][Rx])**2 + (self.d_y[tx] - self.r_y[tx][Rx])**2 ) / 1000

        for tx in range(self.numCUE):
            for d2d in range(self.numD2D):
                for rx in range(self.numD2DReciver[d2d]):
                    self.dis_C2D[tx][d2d][rx] = np.sqrt( (self.c_x[tx] - self.r_x[d2d][rx])**2 + (self.c_y[tx] - self.r_y[d2d][rx])**2 ) / 1000

        for tx in range(self.numD2D):
            for rx in range(self.numCUE):
                self.dis_D2C[tx][rx] = np.sqrt( (self.d_x[tx] - self.c_x[rx])**2 + (self.d_y[tx] - self.c_y[rx])**2 ) / 1000

        for d2d in range(self.numD2D):
            for rx in range(self.numD2DReciver[d2d]):
                self.dis_BS2D[d2d][rx] = np.sqrt( (self.r_x[d2d][rx])**2 + (self.r_y[d2d][rx])**2 ) / 1000

        for i in range(self.numD2D):
            for j in range(self.numD2D):
                for rx in range(self.numD2DReciver[j]):
                    self.dis_DiDj[i][j][rx] = np.sqrt( (self.d_x[i] - self.r_x[j][rx])**2 + (self.d_y[i] - self.r_y[j][rx])**2 ) / 1000

        self.dis_D2BS = np.sqrt( (self.d_x**2 + self.d_y**2) ) / 1000

        return self.dis_C2BS, self.dis_D, self.dis_C2D, self.dis_D2C, self.dis_BS2D, self.dis_DiDj, self.dis_D2BS, self.numD2DReciver

###############################################系統環境圖######################################################
    def draw_model(self):
        x0 = 0
        y0 = 0
        theta = np.arange(0, 2*np.pi, 0.01)
        x1 = x0 + self.radius * np.cos(theta)
        y1 = y0 + self.radius * np.sin(theta)

        fig = plt.figure()
        axes = fig.add_subplot(111)
        axes.plot(x1, y1, color='blue',)
        axes.set_xlabel("distance (m)")
        axes.set_ylabel("distance (m)")
        axes.axis('equal')

        plt.scatter(0, 0, color="#888888", zorder=1000, s=8, label="BS")

        plotted = 0
        for i in range(self.numCUE):
            if plotted == 0:
                plt.scatter(self.c_x[i], self.c_y[i], color="#FF00FF", zorder=1000, s=6, label="CUE")
                plotted = 1
            else:
                plt.scatter(self.c_x[i], self.c_y[i], color="#FF00FF", zorder=1000, s=6)

        plotted = 0
        for i in range(self.numD2D):
            for j in range(self.numD2DReciver[i]):
                t,r = (self.d_x[i], self.d_y[i]), (self.r_x[i][j], self.r_y[i][j])

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

    def get_position(self):
        return self.c_x, self.c_y, self.d_x, self.d_y, self.r_x, self.r_y

    def get_numD2DReciver(self):
        return self.numD2DReciver

if __name__ == '__main__':
    model = Genrator()
    dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver = model.genrator()
    model.draw_model()