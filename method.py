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
        self.maxReciver = config["maxReciver"]
        self.Pmax = config["Pmax"]

        self.dataD2DMax = config["dataD2DMax"]                      #D2D的最大資料量
        self.dataD2DMin = config["dataD2DMin"]                      #D2D的最小資料量

        self.convert = tools.Convert()                              #一些轉換用函式
        self.tool = tools.Tool()                                    #一些計算用函式

#####################################Uplink interference measurement########################################
    def inte_measure_uplink(self, dis_C2BS, dis_C2D, g_c2d, numD2DReciver, candicateUE, directCUE, omnidirectCUE, directD2D, omnidirectD2D):
        #以CUE為圓心，BS為半徑，判斷D2D Rx是否在圓形範圍裡
        i_d2d = list()
        print(i_d2d)
        i_c2d = {}
        print(candicateUE)
        print(omnidirectCUE)
        for cue in candicateUE:
            for tx in range(self.numD2D):
                i_d[tx] = {}
                for rx in range(numD2DReciver[tx]):
                    if cue in omnidirectCUE and dis_C2BS[cue] >= dis_C2D[cue][tx][rx]:
                        # print('cue',cue,'interference d2d',tx,'rx',rx)
                        i_d[rx] = cue
                        i_d2d[tx][rx]
        print(i_d2d)

if __name__ == '__main__':
    scena = scenario.Genrator()
    alloc = allocate.Allocate()

    c_x, c_y, d_x, d_y, r_x, r_y = scena.genrator()
    dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS = scena.distance()
    directCUE, omnidirectCUE, directD2D, omnidirectD2D = scena.get_ue_signal_type()
    numD2DReciver = scena.get_numD2DReciver()

    gain = channel.Channel(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver)
    g_c2d, g_d2b, g_dij = gain.inte_uplink()
    g_c2b, g_d = gain.cell_uplink()

    candicateUE, bsMinSINR_dB, bsSNR_db, powerUE, assignRB = alloc.alloc_uplink(c_x, c_y, g_c2b, g_d)

    interference = Method()

    interference.inte_measure_uplink(dis_C2BS, dis_C2D, g_c2d, numD2DReciver, candicateUE, directCUE, omnidirectCUE, directD2D, omnidirectD2D)
    
    # g_b2d, g_d2c, g_dij = gain.inte_downlink()
    
    # print(c_x)
    # print(c_y)
    # print()
    # print(r_x)
    # print(r_y)
    # scena.draw_model()
    x = tools.Tool()
    point = (c_x[0], c_y[0])
    point = (0,-4)
    # print(point)
    az = x.azimuthAngle(point[0], point[1], 0, 0)
    deltaX = 2 * np.cos(az-90)
    deltaY = 2 * np.sin(az-90)
    deltaX = np.round(deltaX)
    deltaY = np.round(deltaY)
    # print(point[0] + deltaX, point[1] + deltaY)
    # print(point[0] - deltaX, point[1] - deltaY)
    # print(0 + deltaX, 0 + deltaY)
    # print(0 - deltaX, 0 - deltaY)
 
    p1 = (0 - deltaX, 0 - deltaY)
    p2 = (0 + deltaX, 0 + deltaY)
    p3 = (point[0] + deltaX, point[1] + deltaY)
    p4 = (point[0] - deltaX, point[1] - deltaY)

    pi = (1,-3)
    pj = (0,-2)
    pk = (3,-3)
    pl = (3,-6)
    i = x.IsPointInMatrix(p1, p2, p3, p4, pi)
    j = x.IsPointInMatrix(p1, p2, p3, p4, pj)
    k = x.IsPointInMatrix(p1, p2, p3, p4, pk)
    l = x.IsPointInMatrix(p1, p2, p3, p4, pl)
    
    # scena.draw_model()
