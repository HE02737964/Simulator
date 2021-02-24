import  numpy as np
import json

class Convert:
    def mW_to_dB(self, mW):
        dB = 10*np.log10(mW)
        return np.round(dB, decimals=1)
    
    def dB_to_mW(self, dB):
        mW = 10**(dB/10)
        return mW
    
    def CQI_SINR_mapping(slef, CQI):
        if CQI == 1:
            return -6.7
        elif CQI == 2:
            return -4.7
        elif CQI == 3:
            return -2.3
        elif CQI == 4:
            return 0.2
        elif CQI == 5:
            return 2.4
        elif CQI == 6:
            return 4.3
        elif CQI == 7:
            return 5.9
        elif CQI == 8:
            return 8.1
        elif CQI == 9:
            return 10.3
        elif CQI == 10:
            return 11.7
        elif CQI == 11:
            return 14.1
        elif CQI == 12:
            return 16.3
        elif CQI == 13:
            return 18.7
        elif CQI == 14:
            return 21.0
        elif CQI == 15:
            return 22.7
    
    def SINR_CQI_mapping(self,sinr):
        if sinr >= -6.7 and sinr < -4.7:
            return 1
        elif sinr >= -4.7 and sinr < -2.3:
            return 2
        elif sinr >= -2.3 and sinr < 0.2:
            return 3
        elif sinr >= 0.2 and sinr < 2.4:
            return 4
        elif sinr >= 2.4 and sinr < 4.3:
            return 5
        elif sinr >= 4.3 and sinr < 5.9:
            return 6
        elif sinr >= 5.9 and sinr < 8.1:
            return 7
        elif sinr >= 8.1 and sinr < 10.3:
            return 8
        elif sinr >= 10.3 and sinr < 11.7:
            return 9
        elif sinr>= 11.7 and sinr < 14.1:
            return 10
        elif sinr >= 14.1 and sinr < 16.3:
            return 11
        elif sinr >= 16.3 and sinr < 18.7:
            return 12
        elif sinr >= 18.7 and sinr < 21.0:
            return 13
        elif sinr >= 21.0 and sinr < 22.7:
            return 14
        elif sinr >= 22.7:
            return 15
    
    def TBS_CQI_mapping(self, tbs):
        CQI = 0
        if tbs ==0 or tbs == 1:
            CQI = 1
        elif tbs == 2 or tbs == 3:
            CQI = 2
        elif tbs == 4 or tbs == 5:
            CQI = 3
        elif tbs == 6 or tbs == 7:
            CQI = 4
        elif tbs == 8:
            CQI = 5
        elif tbs == 9 or tbs == 10 or tbs == 11:
            CQI = np.random.randint(low=5, high=7)
        elif tbs == 12 or tbs == 13:
            CQI = 8
        elif tbs == 14:
            CQI = 9
        elif tbs == 15 or tbs == 16:
            CQI = np.random.randint(low=9, high=10)
        elif tbs == 17 or tbs == 18:
            CQI = 11
        elif tbs == 19 or tbs == 20:
            CQI = 12
        elif tbs == 21 or tbs == 22:
            CQI = 13
        elif tbs == 23 or tbs == 24:
            CQI = 14
        elif tbs == 25 or tbs == 26:
            CQI = 15
        return CQI

    def SNR_to_Power(self, snr, gain, N0):
        return ((snr * N0) / gain)

class Tool:
    def TBS(self):
        with open("Throughput.json", "r") as f:
            tbs = json.load(f)
            f.close()
        return tbs
    
    def RB_TBS_mapping(self, numRB, data):
        tbs = self.TBS()
        tbsIndex = 0
        for index in tbs:
            if index == '26A':
                break
            if tbs[index][numRB-1] >= data:
                tbsIndex = index
                break
        return int(tbsIndex)

    def data_tbs_mapping(self, data, numRB):
        tbs = self.TBS()
        # for rb in range(numRB):     #用較少RB,較高的TBS index
        #     for index in tbs:
        #         if index == "26A":
        #             break
        #         if tbs[index][rb] >= data:
        #             return int(index), rb+1
        for index in tbs:         #用較多RB,較低的TBS index
            if index == "26A":
                break
            for rb in range(numRB):
                if tbs[index][rb] >= data:
                    return int(index), rb+1

    def IsInsideSector(self, u, v):
        return -u[0]*v[1] + u[1]*v[0] > 0

    def GetRectanglePoint(self, tx, rx, beamWide):
        azimuth = self.azimuthAngle(tx[0], tx[1], rx[0], rx[1])
        #利用方位角與距離求出偏移量,即可得到矩形的4個頂點
        deltaX = np.round(beamWide * np.cos(azimuth-90))
        deltaY = np.round(beamWide * np.sin(azimuth-90))
        p1 = (rx[0] - deltaX, rx[1] - deltaY)
        p2 = (rx[0] + deltaX, rx[1] + deltaY)
        p3 = (tx[0] + deltaX, tx[1] + deltaY)
        p4 = (tx[0] - deltaX, tx[1] - deltaY)
        return p1, p2, p3, p4

    def azimuthAngle(self, x1, y1, x2, y2):
        angle = 0.0
        dx = x2 - x1
        dy = y2 - y1
        if x2 == x1:
            angle = np.pi / 2.0
            if y2 == y1 :
                angle = 0.0
            elif y2 < y1 :
                angle = 3.0 * np.pi / 2.0
        elif x2 > x1 and y2 > y1:
            angle = np.arctan(dx / dy)
        elif x2 > x1 and y2 < y1 :
            angle = np.pi / 2 + np.arctan(-dy / dx)
        elif x2 < x1 and y2 < y1 :
            angle = np.pi + np.arctan(dx / dy)
        elif x2 < x1 and y2 > y1 :
            angle = 3.0 * np.pi / 2.0 + np.arctan(dy / -dx)
        return (angle * 180 / np.pi)

    def GetCross(self, p1, p2, p):
        return (p2[0] - p1[0]) * (p[1] - p1[1]) - (p[0] - p1[0]) * (p2[1] - p1[1])

    def IsPointInMatrix(self, p1, p2, p3, p4, p):
        isPointIn = self.GetCross(p1, p2, p) * self.GetCross(p3, p4, p) >= 0 and self.GetCross(p2, p3, p) * self.GetCross(p4, p1, p) >= 0
        return isPointIn

    def IsPointInSector(self, beamPoint, ue_point):
        #判斷點有沒有在波束的涵蓋範圍內
        sectorStart = (beamPoint[0], beamPoint[1])  #扇形波束的起始座標
        sectorEnd = (beamPoint[2], beamPoint[3])    #扇形波束的結束座標
        isPointIn = not self.IsInsideSector(sectorStart, ue_point) and self.IsInsideSector(sectorEnd, ue_point)
        return isPointIn

    def calculate_SNR(self, uePower, gain, N0):
        return (uePower * gain) / N0

    def Calculate_SINR(self, power, gain, N0, interference):
        return (power * gain) / (N0 + interference)