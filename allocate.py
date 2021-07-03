import numpy as np
import tools

def cellAllocateUl(**parameter):
    tool = tools.Tool()
    convert = tools.Convert()
    candicate = np.sort(np.random.choice(range(0,parameter['numCUE']), size=int(parameter['numCUE'] * (parameter['perScheduleCUE']/100)), replace=False))     #根據比例隨機挑選要傳資料的CUE
    
    P = parameter['Pmax']
    minSINR = np.zeros(parameter['numCUE'])
    minCQI = np.zeros(parameter['numCUE'])
    rbList = np.zeros(parameter['numCUE'])

    power_prb = np.zeros((parameter['numCUE'], parameter['numRB']))
    powerList = np.zeros(parameter['numCUE'])

    #計算BS的最小SINR和CUE在每個RB上使用的power
    deleteCandicate = []
    for i in candicate:
        tbs, rb = tool.data_tbs_mapping(parameter['data_cue'][i], parameter['numRB'])
        cqi, sinr = get_ue_system_info(tbs)
        rbList[i] = rb
        minCQI[i] = cqi
        minSINR[i] = sinr
        cal_ue_power(i, sinr, P, deleteCandicate, power_prb, **parameter)
    
    assignmentUE = np.zeros((parameter['numCUE'], parameter['numRB']))    #二維陣列,每個UE使用的RB狀況(1=使用,0=未使用)
    assignmentRB = np.zeros(parameter['numRB'])              #RB的使用狀態(1=使用,0=未使用)
    sortPower = power_prb.argsort(axis=1)       #每個UE根據在RB上使用的power由小到大排序
    sort_list = np.argsort(rbList)


    #由候選UE依序分配擁有最小傳輸power的RB
    emptyRB = parameter['numRB']
    for ue in sort_list:
        if ue in candicate and emptyRB != 0:
            rbIndex = 0                 #RB索引
            if rbList[ue] > emptyRB:
                tbs = 26
                cqi, sinr = get_ue_system_info(tbs)
                throughput = tool.TBS_Throughput_mapping(tbs, emptyRB)
                rbList[ue] == emptyRB
                minCQI[i] = cqi
                minSINR[i] = sinr
                parameter['data_cue'][ue] = throughput
                cal_ue_power(i, sinr, P, deleteCandicate, power_prb, **parameter)
            rb = rbList[ue]             #CUE需要多少個RB
            if ue in deleteCandicate:
                continue
            while rb > 0 and rbIndex < parameter['numRB']:
                if assignmentRB[sortPower[ue][rbIndex]] == 0:       #判斷RB有無被使用
                    assignmentRB[sortPower[ue][rbIndex]] = 1        #標記RB為已使用
                    assignmentUE[ue][sortPower[ue][rbIndex]] = 1    #將該RB分配給CUE
                    #為了使CUE使用的所有RB都能滿足其最小SINR,設置CUE使用的RB中最大的Power為CUE所使用
                    powerList[ue] = max(powerList[ue], power_prb[ue][sortPower[ue][rbIndex]])
                    emptyRB = emptyRB - 1
                    rb = rb - 1
                else:
                    rbIndex = rbIndex + 1
        if not any(assignmentUE[ue]):
            deleteCandicate.append(ue)

    candicate = np.setdiff1d(candicate, deleteCandicate)
    for ue in deleteCandicate:
        minCQI[ue] = 0
        minSINR[ue] = 0
        power_prb[ue] = 0

    assignmentBS = np.reshape(assignmentRB, (-1, parameter['numRB'])) #BS使用RB接收資料的資料型態是1d array，np.reshape可以轉為2d array (-1會根據輸入的array推斷出新array的大小)
    parameter.update({'candicateCUE' : candicate})
    parameter.update({'minCUEsinr' : minSINR})
    parameter.update({'powerCUEList' : powerList})
    parameter.update({'assignmentTxCell' : assignmentUE})
    parameter.update({'assignmentRxCell' : assignmentBS})
    return parameter

def cellAllocateDl(**parameter):
    tool = tools.Tool()
    convert = tools.Convert()

    P = parameter['Pbs']
    minSINR = np.zeros(parameter['numCUE'])
    minCQI = np.zeros(parameter['numCUE'])
    sinrList = np.zeros(parameter['numCUE'])
    rbList = np.zeros(parameter['numCUE'])

    power_prb = np.zeros((parameter['numCUE'], parameter['numRB']))
    powerList = np.zeros(1)

    #計算CUE的最小SINR和BS在每個RB上使用的power
    deleteCandicate = []
    for i in parameter['inSectorCUE']:
        tbs, rb = tool.data_tbs_mapping(parameter['data_cue'][i], parameter['numRB'])
        cqi, sinr = get_ue_system_info(tbs)
        rbList[i] = rb
        minCQI[i] = cqi
        minSINR[i] = sinr
        cal_ue_power(i, sinr, P, deleteCandicate, power_prb, **parameter)
    
    assignmentUE = np.zeros((parameter['numCUE'], parameter['numRB']))    #二維陣列,每個UE使用的RB狀況(1=使用,0=未使用)
    assignmentRB = np.zeros(parameter['numRB'])              #RB的使用狀態(1=使用,0=未使用)
    sortPower = power_prb.argsort(axis=1)       #每個UE根據在RB上使用的power由小到大排序
    sort_list = np.argsort(rbList)
    
    #由候選UE依序分配擁有最小傳輸power的RB
    emptyRB = parameter['numRB']
    for ue in sort_list:
        if ue in parameter['inSectorCUE']:
            rbIndex = 0                 #RB索引
            if rbList[ue] > emptyRB and emptyRB != 0:
                tbs = 26
                cqi, sinr = get_ue_system_info(tbs)
                throughput = tool.TBS_Throughput_mapping(tbs, emptyRB)
                rbList[ue] == emptyRB
                minCQI[i] = cqi
                minSINR[i] = sinr
                parameter['data_cue'][ue] = throughput
                cal_ue_power(i, sinr, P, deleteCandicate, power_prb, **parameter)
            rb = rbList[ue]             #CUE需要多少個RB
            if ue in deleteCandicate:
                continue
            while rb > 0 and rbIndex < parameter['numRB']:
                if assignmentRB[sortPower[ue][rbIndex]] == 0:       #判斷RB有無被使用
                    assignmentRB[sortPower[ue][rbIndex]] = 1        #標記RB為已使用
                    assignmentUE[ue][sortPower[ue][rbIndex]] = 1    #將該RB分配給CUE
                    #為了使CUE使用的所有RB都能滿足其最小SINR,設置CUE使用的RB中最大的Power為CUE所使用
                    powerList[0] = max(powerList, power_prb[ue][sortPower[ue][rbIndex]])
                    emptyRB = emptyRB - 1
                    rb = rb - 1
                else:
                    rbIndex = rbIndex + 1
            if not any(assignmentUE[ue]):
                deleteCandicate.append(ue)

    candicate = np.setdiff1d(parameter['inSectorCUE'], deleteCandicate)
    for ue in deleteCandicate:
        minCQI[ue] = 0
        minSINR[ue] = 0
        sinrList[ue] = 0
        power_prb[ue] = 0

    assignmentBS = np.reshape(assignmentRB, (-1, parameter['numRB']))
    parameter.update({'candicateCUE' : candicate})
    parameter.update({'minCUEsinr' : minSINR})
    parameter.update({'powerCUEList' : powerList})
    parameter.update({'assignmentTxCell' : assignmentBS})
    parameter.update({'assignmentRxCell' : assignmentUE})
    return parameter

def get_ue_system_info(tbs):
    convert = tools.Convert()
    cqi = convert.TBS_CQI_mapping(tbs)
    sinr = convert.CQI_SINR_mapping(cqi)
    sinr = convert.dB_to_mW(sinr)
    return cqi, sinr

def cal_ue_power(cue, sinr, MAX, deleteCandicate, power_prb, **parameter):
    tx = 0
    rx = 0
    if parameter['numCellRx'] == 1:
        tx = cue
    else:
        rx = cue
    tool = tools.Tool()
    convert = tools.Convert()
    power = convert.SNR_to_Power(sinr, parameter['g_c2b'][tx][rx][0], parameter['N0'])
    
    if power < parameter['Pmin']:
        power = parameter['Pmin']
    if power > MAX:
        power = 0
        deleteCandicate.append(cue)
    power_prb[cue] = power

def getSectorPoint(radius, totalBeam):
    #得到所有波束的扇形座標
    beamSectorPoint = np.zeros((totalBeam, 4))          #波束範圍座標(此處假設為扇形的兩端點座標，所以有4個點)
    for n in range(totalBeam):
        theta = 2 * np.pi * n / totalBeam
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        if -1 < x < 1:
            x = 0
        if -1 < y < 1:
            y = 0
        beamSectorPoint[n][0] = x
        beamSectorPoint[n][1] = y
        if n != 0:
            beamSectorPoint[n-1][2] = x
            beamSectorPoint[n-1][3] = y
        if n == totalBeam-1:
            beamSectorPoint[n][2] = beamSectorPoint[0][0]
            beamSectorPoint[n][3] = beamSectorPoint[0][1]
    return beamSectorPoint

def selectBeamSector(beamSectorPoint, time, numScheduleBeam):
    #選擇當前排程要使用的波束
    selectBeam = np.full(len(beamSectorPoint), -1)      #預設值-1,當前排程要使用哪些波束,0是主要波束,1,2是次要波束
    selectBeam[time % len(beamSectorPoint)] = 0     #波束是根據時間而變化,根據當前時間選擇對應的波束
    candicate = np.where(selectBeam < 0)[0]             #剩下的波束就是次要波束的候選者
    beamCandicate = np.random.choice(candicate, numScheduleBeam-1, replace=False)   #隨機選擇次要波束
    beamCandicate = np.insert(beamCandicate, 0, time % len(beamSectorPoint))    #將主要波束更新到波束候選者列表裡(存放內容是index)
    candicatePoint = np.zeros((len(beamCandicate), 4))
    for i in range(len(beamCandicate)):
        candicatePoint[i] = beamSectorPoint[beamCandicate[i]]
    return candicatePoint

def allSectorCUE(beam_Point, ue_point):
    #所有在波束範圍內的CUE
    tool = tools.Tool()
    candicate = []
    for cue in range(len(ue_point)):
        for beam in beam_Point:
            if tool.IsPointInSector(beam, ue_point[cue]):
                candicate.append(cue)
    return np.asarray(candicate)