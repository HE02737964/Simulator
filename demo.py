import numpy as np
import genrator
import channel
import tools

tool = tools.Tool()
convert = tools.Convert()

numRB = 2
numD2D = 3
D2Ddistance = 100
numReciver = np.ones(3, dtype=int)
numD2DReciver = np.random.randint(low=1, high=1+1, size=numD2D)
N_dBm = -174
bw = 180e3
N0 = (10**(N_dBm / 10)) #1Hz的熱噪聲，單位mW
N0 = N0 * bw  

g = genrator.Genrator(250)
c = channel.Channel(numRB, numD2DReciver)

txPoint = g.generateTxPoint(numD2D)
rxPoint = g.generateRxPoint(txPoint, D2Ddistance, numD2DReciver)

distance = g.distanceD2DRx(txPoint, rxPoint, numD2DReciver)
d_d2d = g.distanceTx2D2DRx(txPoint, rxPoint, numD2DReciver)

g_d = c.gainD2DRx(distance)
g_d2d = c.gainTx2D2DRx(d_d2d)

data = [336, 224, 72]

for i in range(numD2D):
    tbs, rb = tool.data_tbs_mapping(data[i], 1)
    cqi = convert.TBS_CQI_mapping(tbs)
    sinr = convert.CQI_SINR_mapping(cqi)
    minSinr = convert.dB_to_mW(sinr)
    power = convert.SNR_to_Power(minSinr, g_d[i][0][rb], N0)
    print(power)
    print(convert.mW_to_dB(power*1000))
    print(convert.mW_to_dB(power))
    print()