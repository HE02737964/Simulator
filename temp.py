import numpy as np
import random
import json

N_db = -174
N0 = (10**(N_db/10)) / 1000
N0 = N0 * 180e3

def w_to_dB(w):
    return 10*np.log10(w/0.001)

def db_to_w(db):
    return 10**(db/10)/1000

def TBS():
    with open('Throughput.json') as json_file:
        data = json.load(json_file)
    return data

def CQI_SINR_mapping(CQI):
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

def CQI_MCS_mapping(CQI):
    if CQI >= 1 and CQI <=6:
        Qm = 2
    elif CQI >= 7 and CQI <= 9:
        Qm = 4
    elif CQI <= 10 and CQI <= 15:
        Qm = 6
    return Qm

def RB(numRB):
    data = TBS()
    count = 0
    Throughput_RB = []
    for i in data:
        if i == '26A':
            break
        count = 0
        for j in data[i]:
            if count == numRB-1:
                Throughput_RB.append(j)
            count += 1
    return Throughput_RB

def Rate_CQI_mapping(rateList):
    Throughput = RB(25)
    Th = []
    TBS_Table = []
    Qm_Table = []
    CQI_Table = []
    for i in rateList:
        for j in Throughput:
            if i < j:
                TBS_Table.append(Throughput.index(j))
                Th.append(Throughput[Throughput.index(j)])
                break
    for i in TBS_Table:
        if i >= 0 and i <= 9:
            Qm_Table.append(2)
        elif i >= 10 and i <= 15:
            Qm_Table.append(4)
        elif  i >= 16 and i <= 26:
            Qm_Table.append(6)
    for i in Qm_Table:
        if i == 2:
            # CQI_Table.append(1)
            CQI_Table.append(random.randint(1,6))
        elif i == 4:
            # CQI_Table.append(7)
            CQI_Table.append(random.randint(7,9))
        elif i == 6:
            # CQI_Table.append(10)
            CQI_Table.append(random.randint(10,15))
    return CQI_Table,Th

SINR_db = []
inte = []
inter = 0

d_d2dR = np.random.randint(low=1,high=20,size=10) #D2D Tx - Rx distane
d_d2dI = np.random.randint(low=1,high=100,size=(10,9)) #D2D TX - other D2D Rx distance
g_d2dR = np.random.rayleigh(1) #Rayleigh fading

pathLoss = 128.1+37.6*np.log10(d_d2dR/1000)
pathLossScalar = 10**(pathLoss/10)

pathLossInter = 128.1+37.6*np.log10(d_d2dI/1000)
pathLossIn = 10**(pathLossInter/10)

gain = ((g_d2dR**2)/(pathLossScalar))
gainInter = ((g_d2dR**2)/(pathLossIn))

SINR_min = np.zeros(10)
# CQITable = np.random.randint(low=1,high=15,size=10)
need_Rate = np.random.randint(low=100,high=18336,size=10)
CQITable,Th = Rate_CQI_mapping(need_Rate)
# CQITable = np.ones(10)
for i in range(0,len(CQITable)):
    SINR_min[i] = np.asarray(CQI_SINR_mapping(CQITable[i]))

# SINR_min_w = 10**(SINR_min/10)/1000
SINR_min_w = db_to_w(SINR_min)

# interference = {
#     1: {7,8},
#     2: {1},
#     3: {8,9},
#     4: {9},
#     5: {1,4,8},
#     6: {7},
#     7: {1,6},
#     8: {1,8,3},
#     9: {3,4},
#     10: {5,6}
# }

# longPath = {
#     1 : [7],
#     3 : [9,2],
#     4 : [9,2],
#     6 : [7]
# }

# List1 = [1,3,4,6]
# List2 = [2,5,7,8,9,10]

interference = {
    1 : {4, 9},
    2 : {1, 3},
    3 : {6},
    4 : {5},
    5 : {7},
    6 : {3, 5},
    7 : {8},
    8 : {4, 7, 10},
    9 : {10},
    10: {}
}

longPath = {
    1 : [10, 9],
    3 : [6],
    5 : [7],
    8 : [7]
}

List1 = [1, 3, 5, 8]
List2 = [2, 4, 6, 7, 9, 10]

# interference = {
#     1 : {4},
#     2 : {1, 3},
#     3 : {2},
#     4 : {2, 5},
#     5 : {6},
#     6 : {8, 9},
#     7 : {5},
#     8 : {6, 10},
#     9 : {},
#     10 : {}
# }
# longPath = {
#     2 : [5, 4, 1],
#     6 : [8],
#     7 : [5],
#     10 : []
# }
# List1 = [2, 6, 7, 10]
# List2 = [1, 3, 4, 5, 8, 9]

powerList = np.zeros(10)

for j in List1:
    powerList[j-1] = 0.2

def getSINR(x,s):
    SINR = (powerList[x-1] * gain[x-1]) / (N0 + s)
    return SINR

def getInterferencePower(x):
    strenge = 0
    for i in interference[x]:
        if  i < x:
            strenge = strenge + (powerList[i-1] * gainInter[i-1][x-2])
        else:
            strenge = strenge + (powerList[i-1] * gainInter[i-1][x-1])
    return strenge

# while True:
for i in longPath:
    while longPath[i]:
        j = longPath[i][0]
    # for j in longPath[i]:
        if getInterferencePower(j) == 0:
            power = (SINR_min_w[j-1] * N0) / gain[j-1]
        else:
            s = getInterferencePower(j)
            power = (SINR_min_w[j-1] * (N0 + s)) / gain[j-1]
        if power < 1e-7:
            power = 1e-7
        if power > 0.2:
            power = 0.2
        powerList[j-1] = power
        for x in List1:
            if j in interference[x]:
                s = getInterferencePower(x)
                if getSINR(x,s) < SINR_min_w[x-1]:
                    if j in longPath[i]:
                        print("S1NR of {} . {} less than {}, power of {} set 0".format(x,getSINR(x, s),SINR_min_w[x-1], j))
                        powerList[j-1] = 0
                        longPath[i].remove(j)
        for x in longPath[i]:
            if j in longPath[i]:
                if longPath[i].index(x) < longPath[i].index(j):
                    s = getInterferencePower(x)
                    if getSINR(x,s) < SINR_min_w[x-1]:
        
                        print("SINR of {}. {} less than {}, power oof {} set 0".format(x,getSINR(x,s),SINR_min_w[x-1],j))
                        powerList[j-1] = 0
                        longPath[i].remove(j)
        if j in longPath[i]:
            powerList[j-1] = power
            List1.append(j)
            longPath[i].remove(j)

for i in List1:
    s = getInterferencePower(i)
    power = (SINR_min_w[i-1] * (N0 + s)) / gain[i-1]
    # print(power)
    if power < 1e-7:
        power = 1e-7
    if power > 0.2:
        power = 0.2
    # print(power)
    powerList[i-1] = power

No = list()
n = list()
for i in range(0,10):
    uu = -np.sort(-need_Rate)
    if powerList[i] == 0:
        No.append(uu[i])
        n.append(i+1)
for i in n:
    s = getInterferencePower(i)
    power = (SINR_min_w[i-1] * (N0 + s)) / gain[i-1]
    if power < 1e-7:
        power = 1e-7
    if power > 0.2:
        power = 0.2
    for j in range(1,11):
        if i in interference[j]:
            current_power = ((powerList[j-1] * gain[j-1]) / SINR_min_w[j-1]) - N0/gain[i-1]
            if current_power > power:
                power = current_power
            elif current_power < power:
                power = 0
                print("{} fail".format(i))
                break
    powerList[i-1] = power

sinr = []
for i in interference:
    s = getSINR(i, getInterferencePower(i))
    sinr.append(s)
    # x = 10*np.log10(s*1000)
    x = w_to_dB(s)
    # print(x)
    SINR_db.append(x)

for x,y in zip(SINR_db,SINR_min):
    if x < y:
        print("{} < {}".format(x,y))
        

print("min sinr = {}".format(SINR_min))
print("cal sinr = {}".format(np.round(SINR_db,decimals=1)))
print("cal powr = {}".format(np.round(w_to_dB(powerList))))
# print(Th)
# print(CQITable)
rate = np.where(powerList >= 1e-7, Th, 0)
# print(rate)

print("Data rate = {} Mb/s".format(rate.sum()/1000))
print("Data rate = {} Mbps".format((rate.sum()/1000)*0.125))

CUE = {
    #1 -> D2D, 2->CUE
    11 : {22},
    12 : {11},
    13 : {12, 23},
    14 : {11},
    15 : {14, 24},
    21 : {12},
    22 : {},
    23 : {13},
    24 : {14},
    25 : {11}
}
D2D1 = [11,12,13,14,15]
CUE1 = [21,22,23,24,25]

d_d2d = np.random.randint(low=1,high=20,size=10) #D2D Tx - Rx distane
d_d2dI = np.random.randint(low=1,high=100,size=(10,9)) #D2D TX - other D2D Rx distance
# g_d2dR = np.random.rayleigh(1) #Rayleigh fading

pathLoss = 128.1+37.6*np.log10(d_d2dR/1000)
pathLossScalar = 10**(pathLoss/10)

pathLossInter = 128.1+37.6*np.log10(d_d2dI/1000)
pathLossIn = 10**(pathLossInter/10)

gain = ((g_d2dR**2)/(pathLossScalar))
gainInter = ((g_d2dR**2)/(pathLossIn))

CSINR_min = np.zeros(5)
DSINR_min = np.zeros(5)
# CQITable = np.random.randint(low=1,high=15,size=10)
Bneed_Rate = np.random.randint(low=100,high=18336,size=10)
BCQITable,Th1 = Rate_CQI_mapping(Bneed_Rate)
# CQITable = np.ones(10)
for i in range(0,5):
    DSINR_min[i] = np.asarray(CQI_SINR_mapping(BCQITable[i]))
for i in range(0,5):
    CSINR_min[i] = np.asarray(CQI_SINR_mapping(BCQITable[i+5]))

CSINR_min_w = db_to_w(CSINR_min)
DSINR_min_w = db_to_w(DSINR_min)

CS = CSINR_min_w + w_to_dB(13)

CUEpowerList = np.zeros(5)
D2DpowerList = np.zeros(5)

for i in range(0,5):
    # power = (CSINR_min_w[i] * N0) / gain[i+5]
    power = (CS[i] * N0) / gain[i+5]
    if power < 1e-7:
        power = 1e-7
    if power > 0.2:
        power = 0.2
    CUEpowerList[i] = power

def getInterferencePow(x):
    strenge = 0
    for i in CUE[x]:
        if i >= 10 and i < 20:
            j = i-10
        if i > 20:
            j = i -20
        if  i < x:
            if i >= 10 and i < 20:
                g = i-10
                strenge = strenge + (D2DpowerList[g-1] * gainInter[g-1][j-2])
            elif i >20:
                g = i-20
                strenge = strenge + (CUEpowerList[g-1] * gainInter[g-1+5][j-2+5])
        elif i > x:
            if i >= 10 and i < 20:
                g = i-10
                strenge = strenge + (D2DpowerList[g-1] * gainInter[g-1+5][j-1])
            elif i >20:
                g = i-20
                strenge = strenge + (CUEpowerList[g-1] * gainInter[g-1+5][j-1])
    return strenge

No = list()
n = list()
for i in range(0,5):
    uu = -np.sort(-Bneed_Rate[:5])
    No.append(uu[i])
    result = np.where(Bneed_Rate == uu[i])
    n.append((result[0][0]+1))


for i in n:
    x = i+10
    s = getInterferencePow(x)
    power = (DSINR_min_w[i-1] * (N0 + s)) / gain[i-1]
    if power < 1e-7:
        power = 1e-7
    if power > 0.2:
        power = 0.2
    for j in range(11,16):
        xx = x+10
        if x in CUE[j]:
            if x >= 10 and x < 20 :
                g = x-10
                h = j-10
                current_power = ((D2DpowerList[h-1] * gain[h-1]) / DSINR_min_w[h-1]) - N0/gain[g-1]
            # elif x > 20:
            #     g = x-20
            #     h = j-20
            #     current_power = ((CUEpowerList[h-1] * gain[h-1+5]) / CSINR_min_w[h-1]) - N0/gain[g-1]
            if current_power > power:
                power = current_power
            elif current_power < power:
                power = 0
                print("{} fail".format(i))  
                break
        if xx in CUE[j]:
            if xx >= 10 and xx < 20 :
                g = xx-10
                h = j-10
                current_power = ((D2DpowerList[h-1] * gain[h-1]) / DSINR_min_w[h-1]) - N0/gain[g-1]
            elif xx > 20:
                g = xx-20
                h = j-10
                current_power = ((CUEpowerList[g-1] * gain[g-1+5]) / CSINR_min_w[g-1]) - N0/gain[h-1]
            if current_power > power:
                power = current_power
            elif current_power < power:
                power = 0
                print("{} fail".format(i))
                break
    D2DpowerList[i-1] = power


def getS1NR(x,s):
    if x > 20:
        n = x - 20
        SINR = (CUEpowerList[n-1] * gain[n-1+5]) / (N0 + s)
    else:
        n = x - 10
        SINR = (D2DpowerList[n-1] * gain[n-1+5]) / (N0 + s)
    return SINR

Bsinr = []
S1NR_db = []
for i in CUE:
    s = getS1NR(i, getInterferencePow(i))
    Bsinr.append(s)
    # x = 10*np.log10(s*1000)
    x = w_to_dB(s)
    # print(x)
    S1NR_db.append(x)

S1NR_min = np.concatenate((DSINR_min,CSINR_min))

for x,y in zip(S1NR_db,S1NR_min):
    if x < y:
        print("{} < {}".format(x,y))
        
print("Dmin sinr = {}".format(DSINR_min))
print("Dcal sinr = {}".format(np.round(S1NR_db[:5],decimals=1)))
print()
print("Cmin sinr = {}".format(CSINR_min))
print("Ccal sinr = {}".format(np.round(S1NR_db[5:],decimals=1)))
print()
print("Ccal powr = {}".format(np.round(w_to_dB(CUEpowerList))))
print("Dcal powr = {}".format(np.round(w_to_dB(D2DpowerList))))
# print(Th1)
# print(CQITable)

# print(PL)
D = np.round(w_to_dB(D2DpowerList))
Rate = np.where(D >= -40, Th1, 0)
print(powerList)
print(Rate)

Throughput1 = rate.sum() + Rate.sum()

print("Data rate = {} Mb/s".format(Throughput1/1000))
print("Data rate = {} Mbps".format((Throughput1/1000)*0.125))