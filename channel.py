import numpy as np
import json
import scenario

class Channel():
###############################################初始化########################################################
    def __init__(self):
        self.distance = scenario.Genrator()
        self.dis_C2BS, self.dis_D, self.dis_C2D, self.dis_D2C, self.dis_BS2D, self.dis_DiDj, self.dis_D2BS, self.numD2DReciver = self.distance.genrator()

        with open("config.json", "r") as f:
            config = json.load(f)
            f.close()

        self.numCUE = config['numCUE']
        self.numD2D = config['numD2D']
        self.maxReciver = config['maxReciver']
        self.numRB = config['numRB']

        #Uplink transmit gain
        self.gain_C2BS = np.zeros((self.numCUE, self.numRB))                        #二維陣列, CUE - BS在每個RB上的Gain
        self.gain_D_up = np.zeros((self.numD2D, self.maxReciver, self.numRB))       #三維陣列, D2D Tx - RX在uplink每個RB上的Gain

        #Uplink interference gain
        self.gain_C2D = np.zeros((self.numCUE, self.numD2D, self.maxReciver))       #四維陣列, CUE - D2D所有RX在每個RB上的Gain
        self.gain_D2BS = np.zeros((self.numD2D))                                    #三維陣列, D2D Tx - BS在每個RB上的Gain
        self.gain_DiDj_up = np.zeros((self.numD2D, self.numD2D, self.maxReciver))   #四維陣列, D2D Tx i - D2D RX j在downlink每個RB上的Gain

        #Downlink transmit gain
        self.gain_BS2C = np.zeros((self.numCUE, self.numRB))                        #二維陣列, BS - CUE在每個RB上的Gain
        self.gain_D_dw = np.zeros((self.numD2D, self.numRB, self.maxReciver))       #三維陣列, D2D Tx - RX在downlink每個RB上的Gain

        #Downlink interference gain
        self.gain_BS2D = np.zeros((1, self.numD2D, self.maxReciver))                #四維陣列, BS - D2D所有RX在每個RB上的Gain
        self.gain_D2C = np.zeros((self.numD2D, self.numCUE))                        #三維陣列, D2D Tx - CUE在每個RB上的Gain
        self.gain_DiDj_dw = np.zeros((self.numD2D, self.numD2D, self.maxReciver))   #四維陣列, D2D Tx i - D2D RX j在downlink每個RB上的Gain 
        
###################################Channel Gain of Uplink in cell system####################################
    def cell_uplink(self):
        pathLoss_cue = 128.1 + 37.6 * np.log10(self.dis_C2BS)                       #計算CUE - BS的path loss
        pathLossScale_cue = 10**(pathLoss_cue/10)                                   #將path loss轉為linear scale
        
        pathLoss_d2d = 128.1 + 37.6 * np.log10(self.dis_D)                          #計算D2D Tx - D2D Rx的path loss
        pathLossScale_d2d = 10**(pathLoss_d2d/10)                                   #將path loss轉為linear scale

        fading_cue = np.random.rayleigh(1, [self.numCUE, self.numRB])               #Rayleigh fading
        fading_d2d = np.random.rayleigh(1, [self.numD2D, self.maxReciver, self.numRB])

        self.gain_C2BS = (fading_cue**2) / pathLossScale_cue[: , None]              #[: , None]轉變矩陣形狀(原始：NxK矩陣 / 1xN矩陣)
        # self.gain_D_up = (fading_d2d**2) / pathLossScale_d2d[:, :, None]          #下面那行解決numpy的除0錯誤
        self.gain_D_up = np.divide((fading_d2d**2), pathLossScale_d2d[:, :, None], out=np.zeros_like(fading_d2d), where=pathLossScale_d2d[:,:,None] !=0)

###################################Channel Gain of Downlink in cell system##################################
    def cell_downlink(self):
        pass

if __name__ == '__main__':
    Gain = Channel()
    Gain.cell_uplink()