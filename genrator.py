import numpy as np

class Genrator():
    def __init__(self, radius):
        self.radius = radius

    def generateTxPoint(self, numUE):
        x = 2 * self.radius * np.random.rand(1,numUE) - self.radius            #隨機生成Tx UE的x座標
        y = 2 * self.radius * np.random.rand(1,numUE) - self.radius            #隨機生成Tx UE的y座標
        location = (x**2 + y**2).flatten()                                      #.flatten() 轉為一維陣列
        index_out = np.where(location > self.radius**2)[0]                      #找出超過BS範圍的點的index, [0]轉為一維陣列
        len1 = len(index_out)                                                   #超過BS範圍的點的數量
        x = np.delete(x, index_out)                                             #超過BS範圍的點移除
        y = np.delete(y, index_out)

        while len1:                                                             #重新生成點,直到數量滿足
            xt = 2 * self.radius * np.random.rand(1,len1) - self.radius
            yt = 2 * self.radius * np.random.rand(1,len1) - self.radius
            index_tmp = np.where((xt**2 + yt**2).flatten() > self.radius**2)[0]
            len1 = len(index_tmp)
            xt = np.delete(xt, index_tmp)
            yt = np.delete(yt, index_tmp)
            x = np.append(x, xt)
            y = np.append(y, yt)
        point = np.vstack([x,y]).T                                              #np.vstack() = zip(), .T = 轉置矩陣
        return point
        
    def generateRxPoint(self, tx_point, d2dDistance, numD2DReciver):
        numD2D = len(tx_point)

        x = np.zeros((numD2D, max(numD2DReciver)))
        y = np.zeros((numD2D, max(numD2DReciver)))

        for i in range(numD2D):
            for reciver in range(numD2DReciver[i]):
                while True:                                                     #一直重新生成座標,直到滿足在BS範圍內
                    u = np.random.uniform(0,1)
                    v = np.random.uniform(0,1)
                    w = d2dDistance * np.sqrt(u)
                    t = 2 * np.pi * v
                    xt = w * np.cos(t)
                    yt = w * np.sin(t)
                    rx = xt + tx_point[i][0]
                    ry = yt + tx_point[i][1]
                    if ( ((rx**2)+(ry**2)) < self.radius**2):
                        x[i][reciver] = rx
                        y[i][reciver] = ry
                        break
        point = np.dstack([x,y])
        return point
    
    def distanceTx2Cell(self, tx_point, rx_point):
        dis_Tx2Cell = np.zeros((len(tx_point), len(rx_point)))
        for tx in range(len(tx_point)):
            for rx in range(len(rx_point)):
                dis_Tx2Cell[tx][rx] = np.sqrt( (tx_point[tx][0] - rx_point[rx][0])**2 + (tx_point[tx][1] - rx_point[rx][1])**2 ) / 1000
        return dis_Tx2Cell

    def distanceD2DRx(self, tx_point, rx_point, numD2DReciver):
        dis_Tx2Rx = np.zeros((len(tx_point), max(numD2DReciver)))
        for tx in range(len(tx_point)):
            for rx in range(numD2DReciver[tx]):
                dis_Tx2Rx[tx][rx] = np.sqrt( (tx_point[tx][0] - rx_point[tx][rx][0])**2 + (tx_point[tx][1] - rx_point[tx][rx][1])**2 ) / 1000
        return dis_Tx2Rx

    def distanceBS2Rx(self, rx_point, numD2DReciver):
        dis_Tx2Rx = np.zeros((len(rx_point), max(numD2DReciver)))
        for tx in range(len(rx_point)):
            for rx in range(numD2DReciver[tx]):
                dis_Tx2Rx[tx][rx] = np.sqrt( (rx_point[tx][rx][0])**2 + (rx_point[tx][rx][1])**2 ) / 1000
        return dis_Tx2Rx

    def distanceTx2D2DRx(self, tx_point, rx_point, numD2DReciver):
        dis_Tx2Rx = np.zeros((len(tx_point), len(rx_point), max(numD2DReciver)))
        for i in range(len(tx_point)):
            for j in range(len(rx_point)):
                for rx in range(numD2DReciver[j]):
                    dis_Tx2Rx[i][j][rx] = np.sqrt( (tx_point[i][0] - rx_point[j][rx][0])**2 + (tx_point[i][1] - rx_point[j][rx][1])**2 ) / 1000
        return dis_Tx2Rx

    def ueSignalType(self, numUE, directUE):
        ueIndex = np.arange(numUE)

        directUE = np.random.choice(ueIndex, size=int(numUE * (directUE/100)),replace=False)
        directUE = np.sort(directUE)
        omnidirectUE = np.setdiff1d(ueIndex, directUE)
        
        return directUE, omnidirectUE