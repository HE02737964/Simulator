import numpy as np
import matplotlib.pyplot as plt
import json
import genrator
import draw
import channel
import allocate
import measure

with open('config.json', 'r') as f:
    config = json.load(f)

radius = config["radius"]
numCUE = config["numCUE"]
numD2D = config["numD2D"]
numRB = config["numRB"]
maxReciver = config["maxReciver"]
d2dDistance = config["d2dDistance"]
directCUE = config["directCUE"]
directD2D = config["directD2D"]
perScheduleCUE = config["perScheduleCUE"]
N_dBm = config["N_dBm"]
bw = config["bw"]
N0 = (10**(N_dBm / 10)) #1Hz的熱噪聲，單位mW
N0 = N0 * bw            #1個RB的熱噪聲，單位mW
bw = config["bw"]
dataCUEMax = config["dataCUEMax"]
dataCUEMin = config["dataCUEMin"]
Pmax = config["Pmax"]
Pmin = config["Pmin"]
cqiLevel = config["cqiLevel"]
beamWide = config["beamWide"]

numD2DReciver = np.random.randint(low=1, high=maxReciver+1, size=numD2D)

g = genrator.Genrator(radius)
c = channel.Channel(numRB, numD2DReciver)
ue_point = g.generateTxPoint(numCUE)
tx_point = g.generateTxPoint(numD2D)
rx_point = g.generateRxPoint(tx_point, d2dDistance, numD2DReciver)

dist_c2b = g.distanceTx2BS(ue_point)
dist_d2b = g.distanceTx2BS(tx_point)
dist_d2c = g.distanceTx2UE(tx_point, ue_point)
dist_d2d = g.distanceD2DRx(tx_point, rx_point, numD2DReciver)
dist_b2d = g.distanceBS2Rx(rx_point, numD2DReciver)
dist_c2d = g.distanceTx2D2DRx(ue_point, rx_point, numD2DReciver)
dist_dij = g.distanceTx2D2DRx(tx_point, rx_point, numD2DReciver)

directCUE, omnidirectCUE = g.ueSignalType(numCUE, directCUE)
directD2D, omnidirectD2D = g.ueSignalType(numD2D, directD2D)





sectorPoint = allocate.getSectorPoint(500, 8)
for i in range(0,10):
    gain_c2b = c.gainTx2BS(dist_c2b)
    gain_d2b = c.gainTx2BS(dist_d2b)
    gain_d2c = c.gainTx2UE(dist_d2c)
    gain_d2d = c.gainD2DRx(dist_d2d)
    gain_b2d = c.gainBS2Rx(dist_b2d)
    gain_c2d = c.gainTx2D2DRx(dist_c2d)
    gain_dij = c.gainTx2D2DRx(dist_dij)

    candicate_ul, minSINR_ul, powerList_ul, assignmentUE_ul = allocate.cellAllocateUl(numCUE, numRB, perScheduleCUE, gain_c2b, N0, dataCUEMin, dataCUEMax, Pmax, Pmin, cqiLevel)
    beamPoint = allocate.selectBeamSector(sectorPoint, i, 1)
    candicate = allocate.allSectorCUE(beamPoint, ue_point)
    candicate_dl, minSINR_dl, powerList_dl, assignmentUE_dl = allocate.cellAllocateDl(numCUE, numRB, candicate, gain_c2b, N0, dataCUEMin, dataCUEMax, Pmax, Pmin, cqiLevel)
    i_d2d_rx_ul = measure.UplinkCUE(numCUE, numD2D, beamWide, dist_c2b, dist_c2d, ue_point, rx_point, numD2DReciver, candicate, directCUE, omnidirectCUE)
    i_d2d_rx_dl = measure.DownlinkBS(numD2D, rx_point, numD2DReciver, beamPoint)
    i_d2c_ul = measure.Cell_in_OmniD2D(1, numD2D, dist_d2d, dist_d2b, candicate, omnidirectD2D)
    i_d2c_dl = measure.Cell_in_OmniD2D(numCUE, numD2D, dist_d2d, dist_d2c, candicate, omnidirectD2D)
    i_d2d_ul, i_d2d_rx_ul, i_d2c_ul = measure.FromD2DInterference(1, numD2D, beamWide, dist_d2d, dist_dij, numD2DReciver, i_d2d_rx_ul, i_d2c_ul, ue_point, tx_point, rx_point, directD2D, omnidirectD2D, candicate_ul)
    i_d2d_dl, i_d2d_rx_dl, i_d2c_dl = measure.FromD2DInterference(numCUE, numD2D, beamWide, dist_d2d, dist_dij, numD2DReciver, i_d2d_rx_dl, i_d2c_dl, ue_point, tx_point, rx_point, directD2D, omnidirectD2D, candicate_dl)

    print(i_d2d_ul)
    print()
    print(i_d2d_dl)
    print()
    print(i_d2d_rx_ul)
    print()
    print(i_d2d_rx_dl)
    print(candicate)
    print(i_d2c_ul)
    print(i_d2c_dl)

# draw.deawCell(radius, ue_point, tx_point, rx_point, numD2DReciver)