import numpy as np

class Channel():
    def __init__(self, numRB, numD2DReciver):
        self.numRB = numRB
        self.numD2DReciver = numD2DReciver

    def pathLossScale(self, distance):
        pathLoss = 128.1 + 37.6 * np.log10(distance)        #計算 Tx - Rx的path loss
        pathLossScale = 10**(pathLoss/10)                   #將path loss轉為linear scale
        return pathLossScale

    def gainTx2Cell(self, distance):
        gain = np.zeros((len(distance), len(distance[0]), self.numRB))      #三維陣列, D2D Tx - CUE在每個RB上的Gain
        
        pathLossScale = self.pathLossScale(distance)
        
        fading = np.random.rayleigh(1, [len(distance), len(distance[0])])   #全部RB的rayleigh fading相同
        for tx in range(len(distance)):
            for rx in range(len(distance[0])):
                gain[tx][rx] = (fading[tx][rx]**2) / pathLossScale[tx][rx]
        return gain

    def gainD2DRx(self, distance):
        gain = np.zeros((len(distance), max(self.numD2DReciver), self.numRB))   #三維陣列, D2D Tx - RX在每個RB上的Gain

        pathLossScale = self.pathLossScale(distance)

        fading = np.random.rayleigh(1, [len(distance), max(self.numD2DReciver)])
        for tx in range(len(distance)):
            for rx in range(self.numD2DReciver[tx]):
                gain[tx][rx] = (fading[tx][rx]**2) / pathLossScale[tx][rx]
        return gain

    def gainBS2Rx(self, distance):
        gain = np.zeros((len(distance), max(self.numD2DReciver), self.numRB))   #二維陣列, BS - D2D所有RX在每個RB上的Gain

        pathLossScale = self.pathLossScale(distance)
        
        fading = np.random.rayleigh(1, [len(distance), max(self.numD2DReciver)])
        for tx in range(len(distance)):
            for rx in range(self.numD2DReciver[tx]):
                gain[tx][rx] = (fading[tx][rx]**2) / pathLossScale[tx][rx]
        return gain

    def gainTx2D2DRx(self, distance):
        gain = np.zeros((len(distance), len(distance[0]), max(self.numD2DReciver), self.numRB))     #四維陣列, TX - D2D所有RX在每個RB上的Gain

        pathLossScale = self.pathLossScale(distance)
        
        fading = np.random.rayleigh(1, [len(distance), len(distance[0]), max(self.numD2DReciver)])
        for i in range(len(distance)):
            for tx in range(len(distance[0])):
                for rx in range(self.numD2DReciver[tx]):
                    gain[i][tx][rx] = (fading[i][tx][rx]**2) / pathLossScale[i][tx][rx]
        return gain