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
    
    def CQI_MCS_mapping(self, CQI):
        Qm = 0
        if CQI >= 1 and CQI <=6:
            Qm = 2
        elif CQI >= 7 and CQI <= 9:
            Qm = 4
        elif CQI >= 10 and CQI <= 15:
            Qm = 6
        return Qm

    def MCS_TBS_mapping(self, MCS):
        if MCS == 2:
            return np.random.randint(0,9)
        elif MCS == 4:
            return np.random.randint(9,15)
        elif MCS == 6:
            return np.random.randint(15,26)
    
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
        snr_mw = self.dB_to_mW(snr)
        return ((snr_mw * N0) / gain)

class Tool:
    def TBS(self):
        with open("Throughput.json", "r") as f:
            tbs = json.load(f)
            f.close()
        return tbs

    def Throughput(self, index, data):
        tbs = self.TBS()
        rb = 0
        for throughput in tbs[str(index)]:
            if data > throughput:
                rb += 1
        return rb+1
    
    def perRB_TBS_mapping(self, numRB, data):
        tbs = self.TBS()
        tbs_index = 0
        for index in tbs:
            if index == '26A':
                break
            if tbs[index][numRB-1] >= data:
                tbs_index = index
                break
        return int(tbs_index)

    # def tbs_rb__throughput(self, index, rb):
    #     tbs = self.TBS()
    #     throughput = tbs[str(index)]

    def isInsideSector(self, u, v):
        return -u[0]*v[1] + u[1]*v[0] > 0

    def calculate_SNR(self, uePower, gain, N0):
        return (uePower * gain) / N0