import numpy as np
import genrator
import channel
import tools

tool = tools.Tool()
convert = tools.Convert()

numRB = 2
numD2D = 3
D2Ddistance = 50
numReciver = np.ones(3, dtype=int)
numD2DReciver = np.random.randint(low=1, high=1+1, size=numD2D+1)
N_dBm = -174
bw = 180e3
N0 = (10**(N_dBm / 10)) #* 10**(-3)
N0 = N0 * bw  

g = genrator.Genrator(250)
c = channel.Channel(numRB, numD2DReciver)

# txPoint = g.generateTxPoint(numD2D+1)
# rxPoint = g.generateRxPoint(txPoint, D2Ddistance, numD2DReciver)

txPoint = [
    [-228.10631841, 12.18536332],
    [150.49652462, -38.85344253],
    [207.86582436, 121.16980971],
    [1.70079532, 232.55600547]
]

rxPoint = [
    [[-226.87879303, 0.71728428]],
    [[137.51357439, 5.23157723]],
    [[177.7757355, 157.92530709]],
    [[-16.50956784, 218.33551265]]
]

# print(txPoint)
# print("--------------------------------------------------------")
# print(rxPoint)

distance = g.distanceD2DRx(txPoint, rxPoint, numD2DReciver)
d_d2d = g.distanceTx2D2DRx(txPoint, rxPoint, numD2DReciver)

print(distance)
print(d_d2d)
print("==================================================================")

g_d = c.gainD2DRx(distance)
g_d2d = c.gainTx2D2DRx(d_d2d)

# print(g_d)
# print("---------------------------------------------------------------")
# print(g_d2d)

g_d = [
    [[6.53323133e-07, 7.85497645e-06]],
    [[3.58761859e-08, 6.61425123e-10]],
    [[4.29567321e-11, 7.84536611e-08]],
    [[4.16480546e-07, 9.21532120e-08]]
]

g_d2d = [
    [
        [[1.10711938e-05, 9.97775956e-07]],
        [[1.35452639e-11, 1.50621862e-11]],
        [[1.44129849e-11, 9.24640128e-13]],
        [[1.68109817e-11, 7.87657471e-12]]
    ],
    [
        [[8.56188546e-12, 2.25593586e-12]],
        [[4.76014128e-08, 3.36092245e-08]],
        [[5.62541374e-12, 2.74516889e-11]],
        [[4.05721488e-11, 7.71390522e-11]]
    ],
    [
        [[1.26516485e-13, 3.39166116e-12]],
        [[3.93689618e-10, 6.06444997e-11]],
        [[4.74911279e-08, 1.98545661e-08]],
        [[8.54614121e-12, 1.66827886e-10]]
    ],
    [
        [[1.80215028e-12, 3.06283351e-12]],
        [[1.88060371e-10, 4.35777797e-11]],
        [[2.88751899e-10, 4.23968396e-11]],
        [[1.05400185e-06, 1.66940282e-06]]
    ]
]

# powerList = [-35.5, -5.7, 6.6]
powerList = [-35.5, -5.7, 6.6]
powerList_mW = [0, 0, 0]
for i in range(numD2D):
    powerList_mW[i] = convert.dB_to_mW(powerList[i]) #/ 1000

data = [440, 336, 100]
background = convert.dB_to_mW(3) #/ 1000

# for d2d in range(numD2D):
#     tbs, rb = tool.data_tbs_mapping(data[d2d], 1)
#     cqi = convert.TBS_CQI_mapping(tbs)
#     sinr = convert.CQI_SINR_mapping(cqi)
#     minSinr = convert.dB_to_mW(sinr)
#     i = background * g_d2d[3][d2d][0][0]
#     power = ((minSinr * (N0 + i)) / g_d[d2d][0][0])
#     print(power)
#     print(convert.mW_to_dB(power))
#     powerList_mW[d2d] = power

# tbs, rb = tool.data_tbs_mapping(data[2], 2)
# cqi = convert.TBS_CQI_mapping(tbs)
# sinr = convert.CQI_SINR_mapping(cqi)
# minSinr = convert.dB_to_mW(sinr)
# i = background * g_d2d[3][2][0][0]
# power = ((minSinr * (N0 + i)) / g_d[2][0][0])
# print(power)
# print(convert.mW_to_dB(power))
# powerList_mW[2] = power

for d2d in range(numD2D-1):
    tbs, rb = tool.data_tbs_mapping(data[d2d], 1)
    cqi = convert.TBS_CQI_mapping(tbs)
    sinr = convert.CQI_SINR_mapping(cqi)
    minSinr = convert.dB_to_mW(sinr)
    print('When D2D',d2d,'use one RB')
    print('minSINR',sinr)

    ib = background * g_d2d[3][d2d][0][0]
    SINR = (powerList_mW[d2d] * g_d[d2d][0][0]) / (N0 + ib)
    SINR_DB = convert.mW_to_dB(SINR)
    print('sinr',SINR_DB)
    
    i3 = (powerList_mW[2] * g_d2d[2][d2d][0][0]) + (background * g_d2d[3][d2d][0][0])
    iSINR = (powerList_mW[d2d] * g_d[d2d][0][0]) / (N0 + i3)
    iSINR_DB = convert.mW_to_dB(iSINR)
    # print('power {} x gain {} / N0 {} + i {} = sinr {}'.format(powerList_mW[d2d], g_d[d2d][0][0], N0, i3, (powerList_mW[d2d] * g_d[d2d][0][0]) / (N0 + i3)))
    print('If d2d 3 use this RB, d2d',d2d,'sinr could be',iSINR_DB)
    print()

powerList_mW = [0.0001, 0.1051211128097532, 4.5549070090521395]

print()
tbs, rb = tool.data_tbs_mapping(data[0], 2)
cqi = convert.TBS_CQI_mapping(tbs)
sinr = convert.CQI_SINR_mapping(cqi)
minSinr = convert.dB_to_mW(sinr)
i0 = (powerList_mW[1] * g_d2d[1][0][0][0]) + (powerList_mW[2] * g_d2d[2][0][0][0]) + (background * g_d2d[3][0][0][0])

print('When D2D',0,'use two RB')
print('minSINR',sinr)
SINR0 = (powerList_mW[0] * g_d[0][0][0]) / (N0 + i0)
# SINR0 = (0.0001 * g_d[0][0][0]) / (N0 + i0)
SINR0_DB = convert.mW_to_dB(SINR0)
print('sinr',SINR0_DB)
# print('{} * {} + {} * {} + {} * {} = {}'.format(powerList_mW[1], g_d2d[1][0][0][0], powerList_mW[2], g_d2d[2][0][0][0], background, g_d2d[3][0][0][0], i0))
# print('{} * {} / ({} + {}) = {}'.format(powerList_mW[0], g_d[0][0][0], N0, i0, (powerList_mW[0] * g_d[0][0][0]) / (N0 + i0)))
print()
# p = ((minSinr * (N0 + i0)) / g_d[0][0][0])
# print('pp',p)

print()
tbs, rb = tool.data_tbs_mapping(data[1], 2)
cqi = convert.TBS_CQI_mapping(tbs)
sinr = convert.CQI_SINR_mapping(cqi)
minSinr = convert.dB_to_mW(sinr)
minSinr = 1.737801
i1 = (powerList_mW[0] * g_d2d[0][1][0][0]) + (powerList_mW[2] * g_d2d[2][1][0][0]) + (background * g_d2d[3][1][0][0])

print('When D2D',1,'use two RB')
print('minSINR',sinr)
SINR1 = (powerList_mW[1] * g_d[1][0][0]) / (N0 + i1)
# SINR1 = (0.16320901027917714 * g_d[1][0][0]) / (N0 + i1)
SINR1_DB = convert.mW_to_dB(SINR1)
print('sinr',SINR1_DB)
print()
# i1 = (0.0001 * g_d2d[0][1][0][0]) + (powerList_mW[2] * g_d2d[2][1][0][0]) + (background * g_d2d[3][1][0][0])
# p = ((1.737801 * (N0 + i1)) / g_d[1][0][0])
# print('pp',p)

tbs, rb = tool.data_tbs_mapping(data[2], 2)
cqi = convert.TBS_CQI_mapping(tbs)
sinr = convert.CQI_SINR_mapping(cqi)
minSinr = convert.dB_to_mW(sinr)
i2 = (powerList_mW[0] * g_d2d[0][2][0][0]) + (powerList_mW[1] * g_d2d[1][2][0][0]) + (background * g_d2d[3][2][0][0])

print('When D2D 3 use two RB')
print('minSINR',sinr)
SINR2 = (powerList_mW[2] * g_d[2][0][0]) / (N0 + i2)
# SINR2 = (4.557484569692823 * g_d[2][0][0]) / (N0 + i2)
SINR2_DB = convert.mW_to_dB(SINR2)
print('sinr',SINR2_DB)
print()
# i2 = (0.0001 * g_d2d[0][2][0][0]) + (0.16320901027917714 * g_d2d[1][2][0][0]) + (background * g_d2d[3][2][0][0])
p = ((minSinr * (N0 + i2)) / g_d[2][0][0])
print('pp',p)