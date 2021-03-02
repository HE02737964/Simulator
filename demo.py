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
N0 = (10**(N_dBm / 10)) * 10**(-3) #1Hz的熱噪聲，單位mW
N0 = N0 * bw  

g = genrator.Genrator(30)
c = channel.Channel(numRB, numD2DReciver)

txPoint = g.generateTxPoint(numD2D+1)
rxPoint = g.generateRxPoint(txPoint, D2Ddistance, numD2DReciver)

print(txPoint)
print(rxPoint)

# txPoint = [
#     [ -36.45178991, 240.85655738],
#     [-220.22166836, -9.79381262],
#     [ 224.14173945, -87.99891978],
#     [ 103.60784244, 191.35542775]
# ]
# rxPoint = [
#     [[ -44.37468351, 201.47684126]],
#     [[-193.29184759,  17.51893835]],
#     [[ 207.41464108, -128.13631782]],
#     [[  64.34542723, 183.224726  ]]
# ]

distance = g.distanceD2DRx(txPoint, rxPoint, numD2DReciver)
d_d2d = g.distanceTx2D2DRx(txPoint, rxPoint, numD2DReciver)

g_d = c.gainD2DRx(distance)
g_d2d = c.gainTx2D2DRx(d_d2d)
# print(d_d2d*1000)
print(g_d)
print(g_d2d)


# g_d = [
#     [[2.52654070e-07, 7.86123808e-07]],
#     [[1.43375716e-08, 1.15423152e-08]],
#     [[1.50439730e-07, 1.20634622e-07]],
#     [[4.85914641e-08, 1.68893913e-08]]
# ]

# g_d2d = [
#     [
#         [[2.52654070e-07, 7.86123808e-07]],
#         [[6.57438677e-13, 1.00925710e-10]],
#         [[7.22180835e-10, 4.50687393e-10]],
#         [[6.12916282e-14, 8.39837051e-11]]
#     ],

#     [
#         [[7.74513601e-11, 4.80539163e-11]],
#         [[1.43375716e-08, 1.15423152e-08]],
#         [[6.55443400e-11, 1.26268250e-10]],
#         [[2.16496453e-08, 4.20074591e-09]]
#     ],

#     [
#         [[1.09471417e-10, 7.49686906e-10]],
#         [[2.34229552e-10, 1.58610780e-09]],
#         [[1.50439730e-07, 1.20634622e-07]],
#         [[1.25396661e-11, 1.16581788e-10]]
#     ],

#     [
#         [[7.57590311e-11, 3.12787270e-11]],
#         [[3.69387130e-09, 2.21505918e-09]],
#         [[6.09386531e-10, 3.19896926e-10]],
#         [[4.85914641e-08, 1.68893913e-08]]
#     ]
# ]

powerList = [-22, 3.3, -20]
powerList_mW = [0, 0, 0]
for i in range(numD2D):
    powerList_mW[i] = convert.dB_to_mW(powerList[i]) / 1000

data = [440, 336, 100]
background = convert.dB_to_mW(-5) / 1000

for d2d in range(numD2D-1):
    tbs, rb = tool.data_tbs_mapping(data[d2d], 1)
    cqi = convert.TBS_CQI_mapping(tbs)
    sinr = convert.CQI_SINR_mapping(cqi)
    minSinr = convert.dB_to_mW(sinr)
    i = background * g_d2d[3][d2d][0][0]

    print('When D2D',d2d,'use one RB')
    print('minSINR',sinr)
    SINR = (powerList_mW[d2d] * g_d[d2d][0][0]) / (N0 + i)
    SINR_DB = convert.mW_to_dB(SINR)
    print('sinr',SINR_DB)
    i3 = powerList_mW[2] * g_d2d[2][d2d][0][0] + background * g_d2d[3][d2d][0][0]
    iSINR = (powerList_mW[d2d] * g_d[d2d][0][0]) / (N0 + i3)
    iSINR_DB = convert.mW_to_dB(iSINR)
    print('power {} x gain {} / N0 {} + i {} = sinr {}'.format(powerList_mW[d2d], g_d[d2d][0][0], N0, i3, (powerList_mW[d2d] * g_d[d2d][0][0]) / (N0 + i3)))
    print('If d2d 3 use this RB, d2d',d2d,'sinr could be',iSINR_DB)
    print()



print()
tbs, rb = tool.data_tbs_mapping(data[0], 2)
print(tbs)
cqi = convert.TBS_CQI_mapping(tbs)
sinr = convert.CQI_SINR_mapping(cqi)
minSinr = convert.dB_to_mW(sinr)
i = powerList_mW[1] * g_d2d[1][0][0][0] + powerList_mW[2] * g_d2d[2][0][0][0] + background * g_d2d[3][0][0][0]

print('When D2D',0,'use two RB')
print('minSINR',sinr)
SINR = (powerList_mW[0] * g_d[0][0][0]) / (N0 + i)
SINR_DB = convert.mW_to_dB(SINR)
print('sinr',SINR_DB)
print('{} * {} + {} * {} + {} * {} = {}'.format(powerList_mW[1], g_d2d[1][0][0][0], powerList_mW[2], g_d2d[2][0][0][0], background, g_d2d[3][0][0][0], i))
print('{} * {} / ({} + {}) = {}'.format(powerList_mW[0], g_d[0][0][0], N0, i, (powerList_mW[0] * g_d[0][0][0]) / (N0 + i)))
print()

print()
tbs, rb = tool.data_tbs_mapping(data[1], 2)
cqi = convert.TBS_CQI_mapping(tbs)
sinr = convert.CQI_SINR_mapping(cqi)
minSinr = convert.dB_to_mW(sinr)
i = powerList_mW[0] * g_d2d[0][1][0][0] + powerList_mW[2] * g_d2d[2][1][0][0] + background * g_d2d[3][1][0][0]

print('When D2D',1,'use two RB')
print('minSINR',sinr)
SINR = (powerList_mW[1] * g_d[1][0][0]) / (N0 + i)
SINR_DB = convert.mW_to_dB(SINR)
print('sinr',SINR_DB)
print()

tbs, rb = tool.data_tbs_mapping(data[2], 2)
cqi = convert.TBS_CQI_mapping(tbs)
sinr = convert.CQI_SINR_mapping(cqi)
minSinr = convert.dB_to_mW(sinr)
i = powerList_mW[0] * g_d2d[0][2][0][0] + powerList_mW[1] * g_d2d[1][2][0][0] + background * g_d2d[3][2][0][0]

print('When D2D 3 use two RB')
print('minSINR',sinr)
SINR = (powerList_mW[2] * g_d[2][0][0]) / (N0 + i)
SINR_DB = convert.mW_to_dB(SINR)
print('sinr',SINR_DB)
print()