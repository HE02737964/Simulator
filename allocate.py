import scenario
import channel
import tools
import json
import numpy as np

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
        self.perScheduleCUE = config["perScheduleCUE"]
        self.CQILevel = config["CQILevel"]
        self.maxReciver = config["maxReciver"]
        self.radius = config["radius"]
        self.totalBeam = config["totalBeam"]
        self.scheduleBeam = config["scheduleBeam"]
        self.firPb = config["firPb"]
        self.secPb = config["secPb"]
        self.sinrBS = config["sinrBS"]
        self.dataUEMax = config["dataUEMax"]
        self.dataUEMin = config["dataUEMin"]

        self.convert = tools.Convert()
        self.tool = tools.Tool()
        
        self.schedule = np.zeros((self.totalBeam, 4))
        x = channel.Channel(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver)
        self.g_b, self.g_d = x.cell_downlink()
        self.g_c, self.g_d = x.cell_uplink()
    
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
        scheduleUE = np.full(self.numCUE, -1)
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
                        scheduleUE[cue] = np.where(beamCandicate == beam)[0]
                    else:
                        scheduleUE[cue] = np.where(beamCandicate == beam)[0]
        
        candicateUE = np.where(scheduleUE >= 0)[0]
        ueData = np.random.randint(low=self.dataUEMin, high=self.dataUEMax, size=len(scheduleUE))
        ueMinSINR_dB = np.zeros(len(scheduleUE))
        ueMinCQI = np.zeros(len(scheduleUE))
        ueMinTbs = np.zeros(len(scheduleUE))
        for i in range(len(scheduleUE)):
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
                if scheduleUE[index] == 0:
                    snr = self.calculate_SNR(self.firPb, self.g_b[index][rb], self.N0)
                    snr_db = self.convert.mW_to_dB(snr)
                    ueSNR[index][rb] = snr
                    ueSNR_db_rb[index][rb] = snr_db

                elif scheduleUE[index] == 1 or scheduleUE[index] == 2:
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

    def isInsideSector(self, u, v):
        return -u[0]*v[1] + u[1]*v[0] > 0

    def alloc_uplink(self, c_x, c_y, directCUE, omnidirectCUE):
        cueIndex = np.arange(self.numCUE)
        candicateUE = np.sort(np.random.choice(cueIndex, size=int(self.numCUE * (self.perScheduleCUE/100)), replace=False))
        
        ueData = np.random.randint(low=self.dataUEMin, high=self.dataUEMax, size=len(candicateUE))
        bsMinSINR_dB = np.zeros(len(candicateUE))
        bsMinCQI = np.zeros(len(candicateUE))
        bsMinTbs = np.zeros(len(candicateUE))
        upperCqi = 0

        bsSNR_db = np.zeros(self.numCUE)
        powerUE_rb = np.zeros((self.numCUE, self.numRB))
        powerUE = np.zeros(self.numCUE)
        
        for i in range(len(candicateUE)):
            tbs = self.tool.perRB_TBS_mapping(1, ueData[i])
            cqi = self.convert.TBS_CQI_mapping(tbs)
            sinr = self.convert.CQI_SINR_mapping(cqi)
            if cqi >= 12:
                upperCqi = 15
            else:
                upperCqi = cqi + self.CQILevel
            upperSinr = self.convert.CQI_SINR_mapping(upperCqi)
            bsMinCQI[i] = cqi
            bsMinSINR_dB[i] = sinr
            bsSNR_db[candicateUE[i]] = upperSinr
            for rb in range(self.numRB):
                power = self.SNR_to_Power(upperSinr, self.g_c[candicateUE[i]][rb])
                power_db = self.convert.mW_to_dB(power)
                if power_db > 23:
                    power_db = 23
                if power_db < -40:
                    power_db = -40
                powerUE_rb[candicateUE[i]][rb] = power_db
        
        assignRB = np.zeros((self.numCUE, self.numRB))
        rbStatus = np.zeros(self.numRB)
        sortPower = powerUE_rb.argsort(axis=1)

        for ue in candicateUE:
            i = 0
            while i < self.numRB:
                if rbStatus[sortPower[ue][i]] == 0:
                    rbStatus[sortPower[ue][i]] = 1
                    assignRB[ue][sortPower[ue][i]] = 1
                    break
                else:
                    i += 1
        
        for i in range(self.numCUE):
            for j in range(self.numRB):
                if assignRB[i][j] == 1:
                    powerUE[i] = powerUE_rb[i][j]

    def calculate_SNR(self, uePower, gain, N0):
        return (uePower * gain) / N0
        #基地台打Power , CUE可以算SNR然後得到CQI可得TBS Index
    
    def SNR_to_Power(self, snr, gain):
        snr_mw = self.convert.dB_to_mW(snr)
        return (snr * self.N0) / gain

x = scenario.Genrator()
dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver = x.genrator()
directCUE, omnidirectCUE, directD2D, omnidirectD2D = x.get_ue_signal_type()
c_x, c_y, d_x, d_y, r_x, r_y = x.get_position()
allocate = Allocate(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver)


for i in range(8):
    # allocate.alloc_downlink(i, c_x, c_y)
    allocate.alloc_uplink(c_x, c_y, directCUE, omnidirectCUE)
# allocate.alloc_downlink(0, c_x, c_y)
# x.draw_model()