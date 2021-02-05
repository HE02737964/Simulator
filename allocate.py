import scenario
import channel
import tools
import json
import numpy as np

class Allocate():
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
        self.perScheduleCUE = config["perScheduleCUE"]              #Uplink排程時挑選CUE的比例
        self.CQILevel = config["CQILevel"]                          #Uplink時BS提高多少CQI等級(避免使用最小CQI傳輸)
        self.maxReciver = config["maxReciver"]                      #D2D group最多接收端數量
        self.radius = config["radius"]                              #Cell半徑
        self.totalBeam = config["totalBeam"]                        #Downlink排程時，BS總共有多少個波束
        self.numScheduleBeam = config["numScheduleBeam"]            #當前排程要使用多少波束
        self.firPb = config["firPb"]                                #主要波束的傳輸功率
        self.secPb = config["secPb"]                                #次要波束的傳輸功率

        self.dataCUEMax = config["dataCUEMax"]                        #UE的最大資料量
        self.dataCUEMin = config["dataCUEMin"]                        #UE的最小資料量
        self.perUeRb = config["perUeRb"]                            #1個UE能分到多少RB

        self.convert = tools.Convert()                              #一些轉換用函式
        self.tool = tools.Tool()                                    #一些計算用函式
        
        self.schedule = np.zeros((self.totalBeam, 4))               #波束範圍座標(此處假設為扇形的兩端點座標，所以有4個點)

#############################################Uplink CUE排程##################################################
    def alloc_uplink(self, c_x, c_y, g_c, g_d):
        cueIndex = np.arange(self.numCUE)                                               #CUE索引
        candicateUE = np.sort(np.random.choice(cueIndex, size=int(self.numCUE * (self.perScheduleCUE/100)), replace=False))     #根據比例隨機挑選要傳資料的CUE
        
        ueData = np.random.randint(low=self.dataCUEMin, high=self.dataCUEMax, size=len(candicateUE))                              #候選UE生成資料量
        bsMinSINR_dB = np.zeros(len(candicateUE))                                       #基地台的最小SINR
        bsMinCQI = np.zeros(len(candicateUE))                                           #基地台的最小CQI                                                               

        bsSNR_db = np.zeros(self.numCUE)                                                #基地台SNR
        powerUE_rb = np.zeros((self.numCUE, self.numRB))                                #UE在每個RB上的傳輸功率
        powerUE = np.zeros(self.numCUE)                                                 #UE的傳輸功率
        
        #計算BS的最小SINR和CUE在每個RB上使用的power
        upperCqi = 0
        for i in range(len(candicateUE)):
            tbs = self.tool.perRB_TBS_mapping(self.perUeRb, ueData[i])                  #TBS index
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
                power = self.convert.SNR_to_Power(upperSinr, g_c[candicateUE[i]][rb], self.N0)
                power_db = self.convert.mW_to_dB(power)
                if power_db > 23:
                    power_db = 23
                if power_db < -40:
                    power_db = -40
                powerUE_rb[candicateUE[i]][rb] = power_db
        
        assignRB = np.zeros((self.numCUE, self.numRB))                                  #二維陣列,每個UE使用的RB狀況(1=使用,0=未使用)
        rbStatus = np.zeros(self.numRB)                                                 #RB的使用狀態(1=使用,0=未使用)
        sortPower = powerUE_rb.argsort(axis=1)                                          #每個UE根據在RB上使用的power由小到大排序

        #由候選者UE依序分配擁有最小傳輸power的RB
        for ue in candicateUE:
            i = 0                                           #RB索引
            perUeRb = self.perUeRb                          #UE能分配多少RB
            while i < self.numRB:
                while perUeRb > 0 and i < self.numRB:
                    if rbStatus[sortPower[ue][i]] == 0:
                        rbStatus[sortPower[ue][i]] = 1
                        assignRB[ue][sortPower[ue][i]] = 1
                        perUeRb -= 1
                    else:
                        i += 1
                break
        
        #UE使用的RB的最大傳輸power就是目前UE的傳輸power            
        for i in range(self.numCUE):
            maxPower = -50
            for j in range(self.numRB):
                if assignRB[i][j] == 1 and powerUE_rb[i][j] > maxPower:
                    maxPower = powerUE_rb[i][j]
                    powerUE[i] = powerUE_rb[i][j]

        return candicateUE, bsMinSINR_dB, bsSNR_db, powerUE, assignRB

######################################＃#####Downlink CUE排程##################################################
    def alloc_downlink(self, time, c_x, c_y, g_b, g_d):
        #得到所有波束的扇形座標
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
        
        #選擇當前排程要使用的波束
        self.selectBeam = np.full(self.totalBeam, -1)                                               #預設值-1,當前排程要使用哪些波束,0是主要波束,1,2是次要波束
        self.selectBeam[time % self.totalBeam] = 0                                                  #波束是根據時間而變化,根據當前時間選擇對應的波束
        candicate = np.where(self.selectBeam < 0)[0]                                                #剩下的波束就是次要波束的候選者
        beamCandicate = np.random.choice(candicate, self.numScheduleBeam-1, replace=False)          #隨機選擇次要波束
        beamCandicate = np.insert(beamCandicate, 0, time % self.totalBeam)                          #將主要波束更新到波束候選者列表裡(存放內容是index)
        
        #判斷CUE有沒有在波束的涵蓋範圍內
        scheduleUE = np.full(self.numCUE, -1)                                                       #預設值-1,會得到當前排程的CUE所使用的波束編號
        for cue in range(self.numCUE):
            for beam in beamCandicate:
                sectorStart = (self.schedule[beam][0], self.schedule[beam][1])                      #扇形波束的起始座標
                sectorEnd = (self.schedule[beam][2], self.schedule[beam][3])                        #扇形波束的結束座標
                if not self.tool.isInsideSector(sectorStart, (c_x[cue], c_y[cue])) and self.tool.isInsideSector(sectorEnd, (c_x[cue], c_y[cue])):
                    scheduleUE[cue] = np.where(beamCandicate == beam)[0]

        candicateUE = np.where(scheduleUE >= 0)[0]                                                  #要排程的UE索引
        ueData = np.random.randint(low=self.dataCUEMin, high=self.dataCUEMax, size=len(scheduleUE))   #BS生成要傳輸給UE的資料量
        ueMinSINR_dB = np.zeros(len(scheduleUE))                                                    #UE接收所需的最小SINR
        ueMinCQI = np.zeros(len(scheduleUE))                                                        #UE接收所需的最小CQI

        #計算UE需要的最小SINR和CQI
        for i in range(len(scheduleUE)):
            tbs = self.tool.perRB_TBS_mapping(self.perUeRb, ueData[i])
            cqi = self.convert.TBS_CQI_mapping(tbs)
            sinr = self.convert.CQI_SINR_mapping(cqi)
            ueMinCQI[i] = cqi
            ueMinSINR_dB[i] = sinr
        
        ueSNR = np.zeros((self.numCUE, self.numRB))                                                 #UE接收的SNR
        ueSNR_db_rb = np.zeros((self.numCUE, self.numRB))                                           #UE在每個RB上接收的SNR
        ueSNR_db = np.zeros(self.numCUE)                                                            #分配RB後,UE的SNR
        
        assignRB = np.zeros((self.numCUE, self.numRB))                                              #二維陣列，CUE被分配用哪些RB
        rbStatus = np.zeros(self.numRB)                                                             #哪些RB被使用過(1=使用,0=未使用)
        
        #計算UE在每個RB上的SNR
        for index in candicateUE:
            for rb in range(self.numRB):
                if scheduleUE[index] == 0:
                    snr = self.tool.calculate_SNR(self.firPb, g_b[index][rb], self.N0)
                    snr_db = self.convert.mW_to_dB(snr)
                    ueSNR[index][rb] = snr
                    ueSNR_db_rb[index][rb] = snr_db

                elif scheduleUE[index] == 1 or scheduleUE[index] == 2:
                    snr = self.tool.calculate_SNR(self.secPb, g_b[index][rb], self.N0)
                    snr_db = self.convert.mW_to_dB(snr)
                    ueSNR[index][rb] = snr
                    ueSNR_db_rb[index][rb] = snr_db

        #UE根據每個RB上的SNR由大至小排序
        sortSNR = (-ueSNR_db_rb).argsort(axis=1,)

        #由第一個UE開始分配其擁有最高SNR的RB
        for ue in candicateUE:
            i = 0                                           #RB索引
            perUeRb = self.perUeRb                          #UE能分配到多少RB
            while i < self.numRB:
                while perUeRb > 0 and i < self.numRB:
                    if rbStatus[sortSNR[ue][i]] == 0:
                        rbStatus[sortSNR[ue][i]] = 1
                        assignRB[ue][sortSNR[ue][i]] = 1
                        perUeRb -= 1
                    else:
                        i += 1
                break
        
        #UE使用的RB的SNR就是目前UE的SNR
        for i in range(self.numCUE):
            minSNR = 1000
            for j in range(self.numRB):
                if assignRB[i][j] == 1 and ueSNR_db_rb[i][j] < minSNR:
                    minSNR = ueSNR_db_rb[i][j]
                    ueSNR_db[i] = ueSNR_db_rb[i][j]
        
        return beamCandicate, candicateUE, ueMinSINR_dB, ueSNR_db, self.firPb, assignRB 

if __name__ == '__main__':
    x = scenario.Genrator()
    c_x, c_y, d_x, d_y, r_x, r_y = x.genrator()
    dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS = x.distance()
    numD2DReciver = x.get_numD2DReciver()

    gain = channel.Channel(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver)
    g_b, g_d = gain.cell_downlink()
    g_c, g_d = gain.cell_uplink()

    allocate = Allocate()

    # allocate.alloc_downlink(0, c_x, c_y, g_b, g_d)
    # allocate.alloc_uplink(c_x, c_y, g_c, g_d, directCUE, omnidirectCUE)

    for i in range(8):
        beamCandicate, candicateUE, ueMinSINR_dB, ueSNR_db, firPb, assignRB  = allocate.alloc_downlink(i, c_x, c_y, g_b, g_d)
        candicateUE, bsMinSINR_dB, bsSNR_db, powerUE, assignRB = allocate.alloc_uplink(c_x, c_y, g_c, g_d)

    # x.draw_model()