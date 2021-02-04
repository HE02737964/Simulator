import numpy as np
import json
import scenario
import channel
import allocate
import tools

class Method():
    def __init__(self):
        with open("config.json", "r") as f:
            config = json.load(f)
            f.close()
        
        self.bw = config["bw"]                                      #1個RB的頻寬
        self.N_dBm = config["N_dBm"]                                #1Hz的熱噪聲，單位分貝
        self.N0 = (10**(self.N_dBm / 10))                           #1Hz的熱噪聲，單位mW
        self.N0 = self.N0 * self.bw                                 #1個RB的熱噪聲，單位mW
        self.numCUE = config["numCUE"]                              #CUE的數量
        self.numD2D = config["numD2D"]                              #D2D的數量
        self.numRB = config["numRB"]                                #RB的數量

        self.dataD2DMax = config["dataD2DMax"]                      #D2D的最大資料量
        self.dataD2DMin = config["dataD2DMin"]                      #D2D的最小資料量

        self.convert = tools.Convert()                              #一些轉換用函式
        self.tool = tools.Tool()                                    #一些計算用函式

#####################################Uplink interference measurement########################################
    def inte_measure_uplink(self, dis_C2BS, dis_C2D, g_c2d, numD2DReciver):
        #以CUE為圓心，BS為半徑，判斷D2D Rx是否在圓形範圍裡
        for cue in range(self.numCUE):
            for d2d in range(self.numD2D):
                for rx in range(numD2DReciver[d2d]):
                    if dis_C2BS[cue] >= dis_C2D[cue][d2d][rx]:
                        print(d2d,'in',cue)
                    else:
                        print(d2d,'not in',cue)
        
        
if __name__ == '__main__':
    scenario = scenario.Genrator()
    allocate = allocate.Allocate()

    c_x, c_y, d_x, d_y, r_x, r_y = scenario.genrator()
    dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS = scenario.distance()
    numD2DReciver = scenario.get_numD2DReciver()

    gain = channel.Channel(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver)
    g_c2d, g_d2b, g_dij = gain.inte_uplink()

    interference = Method()

    interference.inte_measure_uplink(dis_C2BS, dis_C2D, g_c2d, numD2DReciver)

    # g_b2d, g_d2c, g_dij = gain.inte_downlink()
    print(c_x, c_y)
    print(r_x, r_y)
    scenario.draw_model()