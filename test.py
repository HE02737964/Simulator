import numpy as np
import matplotlib.pyplot as plt
import json
import genrator
import draw
import channel
import allocate
import measure
import proposed

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
dataD2DMax = config["dataD2DMax"]
dataD2DMin = config["dataD2DMin"]
Pmax = config["Pmax"]
Pmin = config["Pmin"]
cqiLevel = config["cqiLevel"]
beamWide = config["beamWide"]

numD2DReciver = np.random.randint(low=1, high=maxReciver+1, size=numD2D)
bs_point = [[0,0]]

g = genrator.Genrator(radius)
c = channel.Channel(numRB, numD2DReciver)
ue_point = g.generateTxPoint(numCUE)
tx_point = g.generateTxPoint(numD2D)
rx_point = g.generateRxPoint(tx_point, d2dDistance, numD2DReciver)

dist_c2b = g.distanceTx2Cell(ue_point, bs_point)
dist_d2b = g.distanceTx2Cell(tx_point, bs_point)
dist_d2c = g.distanceTx2Cell(tx_point, ue_point)
dist_d2d = g.distanceD2DRx(tx_point, rx_point, numD2DReciver)
dist_b2d = g.distanceBS2Rx(rx_point, numD2DReciver)
dist_c2d = g.distanceTx2D2DRx(ue_point, rx_point, numD2DReciver)
dist_dij = g.distanceTx2D2DRx(tx_point, rx_point, numD2DReciver)

directCUE, omnidirectCUE = g.ueSignalType(numCUE, directCUE)
directD2D, omnidirectD2D = g.ueSignalType(numD2D, directD2D)

sectorPoint = allocate.getSectorPoint(500, 8)
scheduleTimes_ul = np.zeros(numD2D)
scheduleTimes_dl = np.zeros(numD2D)

for i in range(0,1):
    gain_c2b = c.gainTx2Cell(dist_c2b)
    gain_d2b = c.gainTx2Cell(dist_d2b)
    gain_d2c = c.gainTx2Cell(dist_d2c)
    gain_d2d = c.gainD2DRx(dist_d2d)
    gain_b2d = c.gainBS2Rx(dist_b2d)
    gain_c2d = c.gainTx2D2DRx(dist_c2d)
    gain_dij = c.gainTx2D2DRx(dist_dij)

    beamPoint = allocate.selectBeamSector(sectorPoint, i, 3)
    candicate = allocate.allSectorCUE(beamPoint, ue_point)

    data_cue_ul = np.random.randint(low=dataCUEMin, high=dataCUEMax, size=numCUE)
    data_cue_dl = np.random.randint(low=dataCUEMin, high=dataCUEMax, size=numCUE)
    data_d2d_ul = np.random.randint(low=dataD2DMin, high=dataD2DMax, size=numD2D)
    data_d2d_dl = np.random.randint(low=dataD2DMin, high=dataD2DMax, size=numD2D)

    candicate_ul, minCUEsinr_ul, powerList_ul, assignmentUE_ul, data_ul = allocate.cellAllocateUl(numCUE, numRB, perScheduleCUE, gain_c2b, N0, data_cue_ul, Pmax, Pmin, cqiLevel)
    candicate_dl, minCUEsinr_dl, powerList_dl, assignmentUE_dl, data_dl = allocate.cellAllocateDl(numCUE, numRB, candicate, gain_c2b, N0, data_cue_dl , Pmax, Pmin, cqiLevel)

    i_d2d_rx_ul = measure.UplinkCUE(numCUE, numD2D, beamWide, dist_c2b, dist_c2d, ue_point, rx_point, numD2DReciver, candicate, directCUE, omnidirectCUE)
    i_d2d_rx_dl = measure.DownlinkBS(numD2D, rx_point, numD2DReciver, beamPoint)
    
    i_d2c_ul = measure.Cell_in_OmniD2D(1, numD2D, dist_d2d, dist_d2b, candicate, omnidirectD2D)
    i_d2c_dl = measure.Cell_in_OmniD2D(numCUE, numD2D, dist_d2d, dist_d2c, candicate, omnidirectD2D)
    
    i_d2c_ul = measure.Cell_in_DirectD2D(1, numD2D, ue_point, tx_point, rx_point, numD2DReciver, candicate, i_d2c_ul, directD2D, beamWide)
    i_d2c_dl = measure.Cell_in_DirectD2D(numCUE, numD2D, ue_point, tx_point, rx_point, numD2DReciver, candicate, i_d2c_dl, directD2D, beamWide)
    
    i_d2d_rx_ul, nStartD2D_ul = measure.BetweenD2D(numD2D, numRB, data_d2d_ul, N0, beamWide, dist_d2d, dist_dij, gain_d2d, numD2DReciver, i_d2d_rx_ul, tx_point, rx_point, directD2D, omnidirectD2D)
    i_d2d_rx_dl, nStartD2D_dl = measure.BetweenD2D(numD2D, numRB, data_d2d_dl, N0, beamWide, dist_d2d, dist_dij, gain_d2d, numD2DReciver, i_d2d_rx_dl, tx_point, rx_point, directD2D, omnidirectD2D)
    
    i_d2d_ul = measure.InterferenceD2D(i_d2d_rx_ul)
    i_d2d_dl = measure.InterferenceD2D(i_d2d_rx_dl)

    root_ul, scheduleTimes_ul, assignmentD2D_ul, minD2Dsinr_ul, powerListD2D_ul = proposed.find_d2d_root(1, numD2D, numRB, nStartD2D_ul, i_d2d_ul, i_d2c_ul, i, scheduleTimes_ul, data_d2d_ul)
    root_dl, scheduleTimes_dl, assignmentD2D_dl, minD2Dsinr_dl, powerListD2D_dl = proposed.find_d2d_root(numCUE, numD2D, numRB, nStartD2D_ul, i_d2d_dl, i_d2c_dl, i, scheduleTimes_dl, data_d2d_dl)

    graph_ul, noCellInterference_ul, cellInterference_ul = proposed.create_interference_graph(1, numD2D, i_d2d_ul, i_d2c_ul)
    graph_dl, noCellInterference_dl, cellInterference_dl = proposed.create_interference_graph(numCUE, numD2D, i_d2d_dl, i_d2c_dl)

    longestPath_ul = proposed.find_longest_path(root_ul, noCellInterference_ul, graph_ul, i_d2d_ul)

    proposed.phase2_power_configure(numRB, root_ul, i_d2d_rx_ul, gain_d2d, gain_dij, N0, longestPath_ul, minD2Dsinr_ul, powerListD2D_ul, assignmentD2D_ul, numD2DReciver)

    # print(root_ul)
    # print(scheduleTimes_ul)
    # print()
    # print(root_dl)
    # print(scheduleTimes_dl)
    # print()
    # print(longestPath_ul)
    # print(i_d2d_ul)
    # print(i_d2c_ul)
    # print(omnidirectCUE)
    # print(omnidirectD2D)
    # print(i_d2d_ul)
    # print(ue_point)
    # print()
    # print(tx_point)
    # print()
    # print(rx_point)
    
    # print()
    # print(i_d2d_dl)
    # print()
    # print(i_d2d_rx_dl)
    # print()
    # print(i_d2d_rx_dl)
    # print(candicate)
    # print(i_d2c_ul)
    # print(i_d2c_dl)

# draw.deawCell(radius, ue_point, tx_point, rx_point, numD2DReciver)