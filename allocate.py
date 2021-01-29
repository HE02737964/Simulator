import scenario
import channel
import tools
import json
import numpy as np

x = scenario.Genrator()
dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver = x.genrator()
# x.draw_model()
c_x, c_y, d_x, d_y, r_x, r_y = x.get_position()

class Allocate():
    def __init__(self, dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver):
        with open("config.json", "r") as f:
            config = json.load(f)
            f.close()
        
        self.N_dBm = config["N_dBm"]
        self.bw = config["bw"]
        self.N0 = (10**(self.N_dBm / 10))
        self.N0 = self.N0 * self.bw
        self.numCUE = config["numCUE"]
        self.numD2D = config["numD2D"]
        self.numRB = config["numRB"]
        self.maxReciver = config["maxReciver"]
        self.radius = config["radius"]
        self.totalBeam = config["totalBeam"]
        self.scheduleBeam = config["scheduleBeam"]
        self.firPb = config["firPb"]
        self.secPb = config["secPb"]
        self.dataUEMax = config["dataUEMax"]
        self.dataUEMin = config["dataUEMin"]

        self.convert = tools.Convert()
        self.tool = tools.Tool()
        
        self.schedule = np.zeros((self.totalBeam, 4))
        x = channel.Channel(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver)
        self.g_b, self.g_d = x.cell_downlink()

        self.scheduleUE = np.full(self.numCUE, -1)
    
    def alloc_downlink(self, time, c_x, c_y):
        #Get beam sector position
        for n in range(self.totalBeam):
            theta = 2 * np.pi * n / self.totalBeam
            x = self.radius * np.cos(theta)
            y = self.radius * np.sin(theta)
            if -1 < x < 1:
                x = 0
            if -1 < y < 1:
                y = 0
            self.schedule[n][0] = x
            self.schedule[n][1] = y
            if n != 0:
                self.schedule[n-1][2] = x
                self.schedule[n-1][3] = y
            if n == self.totalBeam-1:
                self.schedule[n][2] = self.schedule[0][0]
                self.schedule[n][3] = self.schedule[0][1]
        
        
        #
        self.selectBeam = np.full(self.totalBeam, -1)
        self.selectBeam[time % self.totalBeam] = 0
        candicate = np.where(self.selectBeam < 0)[0]
        beamCandicate = np.random.choice(candicate, self.scheduleBeam-1, replace=False)
        beamCandicate = np.insert(beamCandicate, 0, time % self.totalBeam)
        
        for cue in range(self.numCUE):
            for beam in beamCandicate:
                sectorStart = (self.schedule[beam][0], self.schedule[beam][1])
                sectorEnd = (self.schedule[beam][2], self.schedule[beam][3])
                if not self.isInsideSector(sectorStart, (c_x[cue], c_y[cue])) and self.isInsideSector(sectorEnd, (c_x[cue], c_y[cue])):
                    if np.where(beamCandicate == beam)[0] > 0:
                        self.scheduleUE[cue] = np.where(beamCandicate == beam)[0]
                    else:
                        self.scheduleUE[cue] = np.where(beamCandicate == beam)[0]
        
        candicateUE = np.where(self.scheduleUE >= 0)[0]
        ueData = np.random.randint(low=self.dataUEMin, high=self.dataUEMax, size=len(self.scheduleUE))
        ueMinSINR_dB = np.zeros(len(self.scheduleUE))
        ueMinCQI = np.zeros(len(self.scheduleUE))
        ueMinTbs = np.zeros(len(self.scheduleUE))
        for i in range(len(self.scheduleUE)):
            tbs = self.tool.perRB_TBS_mapping(1, ueData[i])
            cqi = self.convert.TBS_CQI_mapping(tbs)
            sinr = self.convert.CQI_SINR_mapping(cqi)
            ueMinCQI[i] = cqi
            ueMinSINR_dB[i] = sinr
        
        ueSNR = np.zeros((self.numCUE, self.numRB))
        ueSNR_db_rb = np.zeros((self.numCUE, self.numRB))
        ueSNR_db = np.zeros(self.numCUE)
        
        assignRB = np.zeros((self.numCUE, self.numRB))
        rbStatus = np.zeros(self.numRB)
        for index in candicateUE:
            for rb in range(self.numRB):
                if self.scheduleUE[index] == 0:
                    snr = self.calculate_SNR(self.firPb, self.g_b[index][rb], self.N0)
                    snr_db = self.convert.mW_to_dB(snr)
                    ueSNR[index][rb] = snr
                    ueSNR_db_rb[index][rb] = snr_db

                elif self.scheduleUE[index] == 1 or self.scheduleUE[index] == 2:
                    snr = self.calculate_SNR(self.secPb, self.g_b[index][rb], self.N0)
                    snr_db = self.convert.mW_to_dB(snr)
                    ueSNR[index][rb] = snr
                    ueSNR_db_rb[index][rb] = snr_db
        sortSNR = (-ueSNR_db_rb).argsort(axis=1,)

        for ue in candicateUE:
            i = 0
            while i < self.numRB:
                if rbStatus[sortSNR[ue][i]] == 0:
                    rbStatus[sortSNR[ue][i]] = 1
                    assignRB[ue][sortSNR[ue][i]] = 1
                    break
                else:
                    i += 1
        
        for i in range(self.numCUE):
            for j in range(self.numRB):
                if assignRB[i][j] == 1:
                    ueSNR_db[i] = ueSNR_db_rb[i][j]

        self.scheduleUE = np.full(self.numCUE, -1)
    
    def isInsideSector(self, u, v):
        return -u[0]*v[1] + u[1]*v[0] > 0

    def alloc_uplink(self, c_x, c_y):
        

    def calculate_SNR(self, uePower, gain, N0):
        return (uePower * gain) / N0
        #基地台打Power , CUE可以算SNR然後得到CQI可得TBS Index


                

# u = scenario.Genrator()
# dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver = u.genrator()
# x = channel.Channel(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver)
allocate = Allocate(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver)
# allocate.alloc_downlink(0, c_x, c_y)
# x.draw_model()
# numbeam = 8
# for i in range(100):
#     print("{} time with {} beam".format(i, i%numbeam+1))
for i in range(8):
    allocate.alloc_downlink(i, c_x, c_y)
# allocate.alloc_downlink(0, c_x, c_y)
x.draw_model()