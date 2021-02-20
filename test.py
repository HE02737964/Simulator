import numpy as np
import matplotlib.pyplot as plt
import json
import genrator
import draw
import channel1

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
numD2DReciver = np.random.randint(low=1, high=maxReciver+1, size=numD2D)

g = genrator.Genrator(radius)
c = channel1.Channel(numRB, numD2DReciver)
ue_point = g.generateTxPoint(numCUE)
tx_point = g.generateTxPoint(numD2D)
rx_point = g.generateRxPoint(tx_point, d2dDistance, numD2DReciver)

dist_c2b = g.distanceTx2BS(ue_point)
gain_c2b = c.gainTx2BS(dist_c2b)
dist_d2b = g.distanceTx2BS(tx_point)
gain_d2b = c.gainTx2BS(dist_d2b)

dist_d2c = g.distanceTx2UE(tx_point, ue_point)
gain_d2c = c.gainTx2UE(dist_d2c)

dist_d2d = g.distanceD2DRx(tx_point, rx_point, numD2DReciver)
gain_d2d = c.gainD2DRx(dist_d2d)

dist_b2d = g.distanceBS2Rx(rx_point, numD2DReciver)
gain_b2d = c.gainBS2Rx(dist_b2d)

dist_c2d = g.distanceTx2D2DRx(ue_point, rx_point, numD2DReciver)
gain_c2d = c.gainTx2D2DRx(dist_c2d)
dist_dij = g.distanceTx2D2DRx(tx_point, rx_point, numD2DReciver)
gain_dij = c.gainTx2D2DRx(dist_dij)

directCUE, omnidirectCUE = g.ueSignalType(numCUE, directCUE)
directD2D, omnidirectD2D = g.ueSignalType(numD2D, directD2D)

draw.deawCell(radius, ue_point, tx_point, rx_point, numD2DReciver)