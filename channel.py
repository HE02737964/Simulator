import numpy as np

class Channel():
    def __init__(self, numRB, numD2DReciver):
        self.numRB = numRB
        self.numD2DReciver = numD2DReciver

    def pathLossScale(self, distance):
        pathLoss = 128.1 + 37.6 * np.log10(distance)        #計算 Tx - Rx的path loss
        pathLossScale = 10**(pathLoss/10)                   #將path loss轉為linear scale
        return pathLossScale

    def gainTx2BS(self, distance):
        gain = np.zeros((len(distance), self.numRB))        #二維陣列, Tx - BS在每個RB上的Gain
        
        pathLossScale = self.pathLossScale(distance)
        fading = np.random.rayleigh(1, [len(distance), self.numRB]) #Rayleigh fading

        gain = (fading**2) / pathLossScale[: , None]        #[: , None]轉變矩陣形狀(原始：NxK矩陣 / 1xN矩陣)
        return gain

    def gainTx2UE(self, distance):
        gain = np.zeros((len(distance), len(distance[0]), self.numRB))          #三維陣列, D2D Tx - CUE在每個RB上的Gain
        
        pathLossScale = self.pathLossScale(distance)
        fading = np.random.rayleigh(1, [len(distance), len(distance[0]), self.numRB])

        gain = (fading**2) / pathLossScale[:, :, None]
        return gain

    def gainD2DRx(self, distance):
        gain = np.zeros((len(distance), max(self.numD2DReciver), self.numRB))   #三維陣列, D2D Tx - RX在每個RB上的Gain

        pathLossScale = self.pathLossScale(distance)
        fading = np.random.rayleigh(1, [len(distance), max(self.numD2DReciver), self.numRB])

        # gain = (fading**2) / pathLossScale[:, :, None]                        #下面那行解決numpy的除0錯誤
        gain = np.divide((fading**2), pathLossScale[:, :, None], out=np.zeros_like(fading), where=pathLossScale[:,:,None] !=0)
        return gain

    def gainBS2Rx(self, distance):
        gain = np.zeros((len(distance), max(self.numD2DReciver), self.numRB))   #二維陣列, BS - D2D所有RX在每個RB上的Gain

        pathLossScale = self.pathLossScale(distance)
        fading = np.random.rayleigh(1, [len(distance), max(self.numD2DReciver), self.numRB])
        
        gain = np.divide((fading**2), pathLossScale[:, :, None], out=np.zeros_like(fading), where=pathLossScale[:, :, None] !=0)
        return gain

    def gainTx2D2DRx(self, distance):
        gain = np.zeros((len(distance), len(distance[0]), max(self.numD2DReciver), self.numRB))     #四維陣列, CUE - D2D所有RX在每個RB上的Gain

        pathLossScale = self.pathLossScale(distance)
        fading = np.random.rayleigh(1, [len(distance), len(distance[0]), max(self.numD2DReciver), self.numRB])

        gain = np.divide((fading**2), pathLossScale[: ,:, :, None], out=np.zeros_like(fading), where=pathLossScale[: ,:, :, None] !=0)
        return gain