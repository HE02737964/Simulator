import numpy as np
import json
import scenario
import channel
import allocate
import tools

class Method():
    def __init__(self, c_x, c_y, d_x, d_y, r_x, r_y):
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
        self.maxReciver = config["maxReciver"]                      #D2D Rx最大接收端數量

        self.dataD2DMax = config["dataD2DMax"]                      #D2D的最大資料量
        self.dataD2DMin = config["dataD2DMin"]                      #D2D的最小資料量

        self.beamWide = config["beamWide"]                          #波束的寬度半徑

        self.convert = tools.Convert()                              #一些轉換用函式
        self.tool = tools.Tool()                                    #一些計算用函式

        self.cue_pos = (c_x, c_y)                                   #CUE座標
        self.tx_pos = (d_x, d_y)                                    #D2D Tx座標
        self.rx_pos = (r_x, r_y)                                    #D2D Rx座標

#####################################Uplink interference measurement########################################
    def inte_measure_uplink(self, dis_C2BS, dis_C2D, dis_D, dis_D2BS, dis_DiDj, numD2DReciver, candicateUE, directCUE, omnidirectCUE, directD2D, omnidirectD2D):
        #CUE對D2D的干擾
        i_d2d_rx = []                                               #Dict,每個D2D Rx包含被哪些CUE和D2D Tx干擾
        i_d2d_up = []                                               #Dict,每個D2D被哪些CUE和D2D Tx干擾
        i_d2b_up = []                                               #List,BS被哪些D2D Tx干擾

        for tx in range(self.numD2D):
            t = []
            for rx in range(numD2DReciver[tx]):
                r = {}
                r_cue = {'cue':[]}                                  #每個rx被哪些CUE干擾
                for cue in candicateUE:
                    #以CUE為圓心，BS為半徑，判斷D2D Rx是否在圓形範圍裡
                    if cue in omnidirectCUE and dis_C2BS[cue] >= dis_C2D[cue][tx][rx]:
                        r_cue['cue'].append(cue)
                    #以CUE和BS兩點,判斷D2D Rx是否在矩形範圍裡
                    elif cue in directCUE:
                        #先求出CUE與BS的方位角
                        p = (self.rx_pos[0][tx][rx], self.rx_pos[1][tx][rx])
                        azimuth = self.tool.azimuthAngle(self.cue_pos[0][cue], self.cue_pos[1][cue], 0, 0)
                        #利用方位角與距離求出偏移量,即可得到矩形的4個頂點
                        deltaX = np.round(self.beamWide * np.cos(azimuth-90))
                        deltaY = np.round(self.beamWide * np.sin(azimuth-90))
                        p1 = (0 - deltaX, 0 - deltaY)
                        p2 = (0 + deltaX, 0 + deltaY)
                        p3 = (self.cue_pos[0][cue] + deltaX, self.cue_pos[1][cue] + deltaY)
                        p4 = (self.cue_pos[0][cue] - deltaX, self.cue_pos[1][cue] - deltaY)
                        #判斷D2D Rx(p點)是否在矩形的4個頂點(p1,p2,p3,p4)內
                        if self.tool.IsPointInMatrix(p1, p2, p3, p4, p):
                            r_cue['cue'].append(cue)
                r.update(r_cue)
                t.append(r)
            i_d2d_rx.append(t)
        
        #D2D對BS和其他D2D的干擾
        for tx in range(self.numD2D):
            r_d2d = []
            for rx in range(numD2DReciver[tx]):
                r = {}
                r_dij = {'d2d':[]}
                for d2d in range(self.numD2D):
                    #以D2D Tx為圓心，最遠的Rx為半徑，判斷BS是否在圓形範圍裡
                    if d2d in omnidirectD2D and max(dis_D[d2d]) >= dis_D2BS[d2d] and d2d not in i_d2b_up:
                        i_d2b_up.append(d2d)
                    #以D2D Tx為圓心，最遠的Rx為半徑，判斷其他D2D Rx是否在圓形範圍裡
                    if d2d in omnidirectD2D and max(dis_D[d2d]) >= dis_DiDj[d2d][tx][rx] and d2d != tx:
                        r_dij['d2d'].append(d2d)
                    #以D2D Tx和他所有的D2D Rx兩點,判斷其他D2D Rx是否在矩形範圍裡
                    elif d2d in directD2D and d2d != tx:
                        #D2D Tx(干擾端)的每一個Rx
                        for d_rx in range(numD2DReciver[d2d]):
                            #先求出Tx與Rx的方位角
                            p_rx = (self.rx_pos[0][tx][rx], self.rx_pos[1][tx][rx])
                            p_bs = (0, 0)
                            azimuth = self.tool.azimuthAngle(self.tx_pos[0][d2d], self.tx_pos[1][d2d], self.rx_pos[0][d2d][d_rx], self.rx_pos[1][d2d][d_rx])
                            #利用方位角與距離求出偏移量,即可得到矩形的4個頂點
                            deltaX = np.round(self.beamWide * np.cos(azimuth-90))
                            deltaY = np.round(self.beamWide * np.sin(azimuth-90))
                            p1 = (self.rx_pos[0][d2d][d_rx] - deltaX, self.rx_pos[1][d2d][d_rx] - deltaY)
                            p2 = (self.rx_pos[0][d2d][d_rx] + deltaX, self.rx_pos[1][d2d][d_rx] + deltaY)
                            p3 = (self.tx_pos[0][d2d] + deltaX, self.tx_pos[1][d2d] + deltaY)
                            p4 = (self.tx_pos[0][d2d] - deltaX, self.tx_pos[1][d2d] - deltaY)
                            #判斷D2D Rx(p點)是否在矩形的4個頂點(p1,p2,p3,p4)內
                            if self.tool.IsPointInMatrix(p1, p2, p3, p4, p_rx) and d2d not in r_dij['d2d']:
                                r_dij['d2d'].append(d2d)
                            if self.tool.IsPointInMatrix(p1, p2, p3, p4, p_bs) and d2d not in i_d2b_up:
                                i_d2b_up.append(d2d)
                                sorted(i_d2b_up)
                i_d2d_rx[tx][rx].update(r_dij)
        for tx in i_d2d_rx:
            i = {'cue':[], 'd2d':[]}
            for rx in tx:
                for inte in rx['cue']:
                    if inte not in i['cue']:
                        i['cue'].append(inte)
                for inte in rx['d2d']:
                    if inte not in i['d2d']:
                        i['d2d'].append(inte)
            i_d2d_up.append(i)
        # i_d2d_rx = np.asarray(i_d2d_rx, dtype=object)
        # i_d2d_up = np.asarray(i_d2d_up, dtype=object)
        # i_d2b_up = np.sort(np.asarray(i_d2b_up, dtype=object))
        return i_d2d_rx, i_d2d_up, i_d2b_up

####################################Downlink interference measurement#######################################
    def inte_measure_downlink(self, dis_D, dis_D2C, numD2DReciver, candicateUE, beamCandicate, beamSector, directCUE, omnidirectCUE, directD2D, omnidirectD2D):
        i_d2d_rx = [] #interfernece tx to each rx
        i_d2c_dw = [] #interference tx to each cue
        i_d2d_dw = [] #interference tx to each d2d

        for tx in range(self.numD2D):
            t = []
            for rx in range(numD2DReciver[tx]):
                r = {}
                r_bs = {'bs':[]}
                for beam in beamCandicate:
                    sectorStart = (beamSector[beam][0], beamSector[beam][1])                      #扇形波束的起始座標
                    sectorEnd = (beamSector[beam][2], beamSector[beam][3])                        #扇形波束的結束座標
                    if not self.tool.isInsideSector(sectorStart, (self.rx_pos[0][tx][rx], self.rx_pos[1][tx][rx])) and self.tool.isInsideSector(sectorEnd, (self.rx_pos[0][tx][rx], self.rx_pos[1][tx][rx])):
                        r_bs['bs'].append(beam)
                r.update(r_bs)
                t.append(r)
            i_d2d_rx.append(t)

        #D2D對CUE和其他D2D的干擾
        for cue in range(self.numCUE):
            r_c = []
            for d2d in range(self.numD2D):
                if d2d in omnidirectD2D and max(dis_D[d2d]) >= dis_D2C[d2d][cue] and d2d not in r_c:
                    r_c.append(d2d)
            i_d2c_dw.append(r_c)

        for tx in range(self.numD2D):
            r_d2d = []
            for rx in range(numD2DReciver[tx]):
                r = {}
                r_dij = {'d2d':[]}
                for d2d in range(self.numD2D):
                    #以D2D Tx為圓心，Rx最遠為半徑，判斷其他D2D Rx是否在圓形範圍裡
                    if d2d in omnidirectD2D and max(dis_D[d2d]) >= dis_DiDj[d2d][tx][rx] and d2d != tx:
                        r_dij['d2d'].append(d2d)
                    #以D2D Tx和他所有的D2D Rx兩點,判斷其他D2D Rx是否在矩形範圍裡
                    elif d2d in directD2D and d2d != tx:
                        #D2D Tx(干擾端)的每一個Rx
                        for d_rx in range(numD2DReciver[d2d]):
                            #先求出Tx與Rx的方位角
                            p = (self.rx_pos[0][tx][rx], self.rx_pos[1][tx][rx])
                            azimuth = self.tool.azimuthAngle(self.tx_pos[0][d2d], self.tx_pos[1][d2d], self.rx_pos[0][d2d][d_rx], self.rx_pos[1][d2d][d_rx])
                            #利用方位角與距離求出偏移量,即可得到矩形的4個頂點
                            deltaX = np.round(self.beamWide * np.cos(azimuth-90))
                            deltaY = np.round(self.beamWide * np.sin(azimuth-90))
                            p1 = (self.rx_pos[0][d2d][d_rx] - deltaX, self.rx_pos[1][d2d][d_rx] - deltaY)
                            p2 = (self.rx_pos[0][d2d][d_rx] + deltaX, self.rx_pos[1][d2d][d_rx] + deltaY)
                            p3 = (self.tx_pos[0][d2d] + deltaX, self.tx_pos[1][d2d] + deltaY)
                            p4 = (self.tx_pos[0][d2d] - deltaX, self.tx_pos[1][d2d] - deltaY)
                            #判斷D2D Rx(p點)是否在矩形的4個頂點(p1,p2,p3,p4)內
                            if self.tool.IsPointInMatrix(p1, p2, p3, p4, p) and d2d not in r_dij['d2d']:
                                r_dij['d2d'].append(d2d)
                            for cue in range(self.numCUE):
                                p_cue = (self.cue_pos[0][cue], self.cue_pos[1][cue])
                                if self.tool.IsPointInMatrix(p1, p2, p3, p4, p_cue) and d2d not in i_d2c_dw[cue]:
                                    i_d2c_dw[cue].append(d2d)
                                    sorted(i_d2c_dw[cue])
                i_d2d_rx[tx][rx].update(r_dij)

        for tx in i_d2d_rx:
            i = {'bs':[], 'd2d':[]}
            for rx in tx:
                for inte in rx['bs']:
                    if inte not in i['bs']:
                        i['bs'].append(inte)
                for inte in rx['d2d']:
                    if inte not in i['d2d']:
                        i['d2d'].append(inte)
            i_d2d_dw.append(i)
        # i_d2d_rx = np.asarray(i_d2d_rx, dtype=object)
        # i_d2d_dw = np.asarray(i_d2d_dw, dtype=object)
        return i_d2d_rx, i_d2d_dw, i_d2c_dw

    def find_root_d2d_uplink(self, i_d2d_rx, i_d2d, i_d2b, time, S, data):
        i_len = np.zeros(self.numD2D)
        for tx in range(self.numD2D):
            i_len[tx] = len(i_d2d[tx]['cue']) + len(i_d2d[tx]['d2d']) + 1

        i_len = np.ones(self.numD2D)
        priority = (data / i_len) * (time / S)
        priority = time / S
        sort_priority = (-priority).argsort()

        root_d2d = []
        for d2d in sort_priority:
            flag = True
            if not i_d2d[d2d]['cue'] and d2d not in i_d2b: #CUE not interfernece D2D and D2D not interference BS
                if not (set(i_d2d[d2d]['d2d']) & set(root_d2d)): #the root list any element not interference d2d
                    for root in root_d2d:
                        if d2d in i_d2d[root]['d2d']: #D2D interference root list element
                            flag = False
                    if flag:
                        root_d2d.append(d2d)
        for i in root_d2d:
            S[i] += 1
            
        return root_d2d, S

if __name__ == '__main__':
    scena = scenario.Genrator()
    alloc = allocate.Allocate()

    c_x, c_y, d_x, d_y, r_x, r_y = scena.genrator()
    dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS = scena.distance()
    directCUE, omnidirectCUE, directD2D, omnidirectD2D = scena.get_ue_signal_type()
    numD2DReciver = scena.get_numD2DReciver()

    gain = channel.Channel(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, [1])
    g_c2b, g_d = gain.cell_uplink()
    g_b2c, g_d = gain.cell_downlink()

    # candicateUE, bsMinSINR_dB, bsSNR_db, powerUE, assignRB = alloc.alloc_uplink(c_x, c_y, g_c2b, g_d)
    beamCandicate, candicateUE, ueMinSINR_dB, ueSNR_db, firPb, assignRB, beamSector = alloc.alloc_downlink(0, c_x, c_y, g_b2c, g_d)

    interference = Method(c_x, c_y, d_x, d_y, r_x, r_y)

    # i_d2d_rx, i_d2d_up, i_d2b_up = interference.inte_measure_uplink(dis_C2BS, dis_C2D, dis_D, dis_D2BS, dis_DiDj, numD2DReciver, candicateUE, directCUE, omnidirectCUE, directD2D, omnidirectD2D)
    interference.inte_measure_downlink(dis_D, dis_D2C, numD2DReciver, candicateUE, beamCandicate, beamSector, directCUE, omnidirectCUE, directD2D, omnidirectD2D)

    S = np.ones(10)
    data = np.ones(10)
    for i in range(1,100):
        candicateUE, bsMinSINR_dB, bsSNR_db, powerUE, assignRB = alloc.alloc_uplink(c_x, c_y, g_c2b, g_d)
        i_d2d_rx, i_d2d_up, i_d2b_up = interference.inte_measure_uplink(dis_C2BS, dis_C2D, dis_D, dis_D2BS, dis_DiDj, numD2DReciver, candicateUE, directCUE, omnidirectCUE, directD2D, omnidirectD2D)
        data = np.random.randint(low=1, high=712, size=10)
        root, S = interference.find_root_d2d_uplink(i_d2d_rx, i_d2d_up, i_d2b_up, i, S, data)
        print(S)
        print(sorted(root))
    # scena.draw_model()