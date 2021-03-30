import numpy as np
import json
import genrator
import draw
import channel
import allocate
import measure
import proposed
import method
import juad

with open('config.json', 'r') as f:
    config = json.load(f)

maxReciver = config["maxReciver"]
d2dDistance = config["d2dDistance"]
directCUE = config["directCUE"]
directD2D = config["directD2D"]
N_dBm = config["N_dBm"]
bw = config["bw"]
N0 = (10**(N_dBm / 10)) #1Hz的熱噪聲，單位mW
N0 = N0 * bw            #1個RB的熱噪聲，單位mW
dataCUEMax = config["dataCUEMax"]
dataCUEMin = config["dataCUEMin"]
dataD2DMax = config["dataD2DMax"]
dataD2DMin = config["dataD2DMin"]

initial = {
    'radius' : config["radius"],
    'numCUE' : config["numCUE"],
    'numD2D' : config["numD2D"],
    'numRB' : config["numRB"],
    'perScheduleCUE' : config["perScheduleCUE"],
    'N0' : N0,
    'Pmax' : config["Pmax"],
    'Pmin' : config["Pmin"],
    'cqiLevel' : config["cqiLevel"],
    'beamWide' : config["beamWide"],
    'totalBeam' : config["totalBeam"],
    'numScheduleBeam' : config["numScheduleBeam"],
    "numD2DCluster" : config["numD2DCluster"],
	"clusterRadius" : config["clusterRadius"],
    "numDensity" : config["numDensity"],
}

numD2DReciver = np.random.randint(low=1, high=maxReciver+1, size=initial['numD2D'])

g = genrator.Genrator(initial['radius'])
c = channel.Channel(initial['numRB'], numD2DReciver)

bs_point = [[0,0]]
ue_point = g.generateTxPoint(initial['numCUE'])
# tx_point = g.generateTxPoint(initial['numD2D'])
tx_point = g.generateGroupTxPoint(initial['numD2D'], initial['clusterRadius'], initial['numD2DCluster'], initial['numDensity'])
rx_point = g.generateRxPoint(tx_point, d2dDistance, numD2DReciver)

dist_c2b = g.distanceTx2Cell(ue_point, bs_point)
dist_b2c = g.distanceTx2Cell(bs_point, ue_point)
dist_d2b = g.distanceTx2Cell(tx_point, bs_point)
dist_d2c = g.distanceTx2Cell(tx_point, ue_point)
dist_d2d = g.distanceD2DRx(tx_point, rx_point, numD2DReciver)
dist_b2d = g.distanceBS2Rx(rx_point, numD2DReciver)
dist_c2d = g.distanceTx2D2DRx(ue_point, rx_point, numD2DReciver)
dist_dij = g.distanceTx2D2DRx(tx_point, rx_point, numD2DReciver)

directCUE, omnidirectCUE = g.ueSignalType(initial['numCUE'], directCUE)
directD2D, omnidirectD2D = g.ueSignalType(initial['numD2D'], directD2D)

sectorPoint = allocate.getSectorPoint(initial['radius'], initial['totalBeam'])
# scheduleTimes_ul = np.zeros(initial['numD2D'])
scheduleTimes_ul = np.array([3,4,2,1,6])
scheduleTimes_dl = np.zeros(initial['numD2D'])

environment = {
    'numD2DReciver' : numD2DReciver,

    'bs_point' : bs_point,
    'ue_point' : ue_point,
    'tx_point' : tx_point,
    'rx_point' : rx_point,

    'd_c2b' : dist_c2b,
    'd_b2c' : dist_b2c,
    'd_d2b' : dist_d2b,
    'd_d2c' : dist_d2c,
    'd_d2d' : dist_d2d,
    'd_b2d' : dist_b2d,
    'd_c2d' : dist_c2d,
    'd_dij' : dist_dij,

    'directCUE' : directCUE,
    'omnidirectCUE' : omnidirectCUE,
    'directD2D' : directD2D,
    'omnidirectD2D' : omnidirectD2D,

    'scheduleTimes' : scheduleTimes_ul
}

for currentTime in range(0,1):
    gain_ul = {
        'g_c2b' : c.gainTx2Cell(dist_c2b),
        'g_d2c' : c.gainTx2Cell(dist_d2b),
        'g_d2d' : c.gainD2DRx(dist_d2d),
        'g_c2d' : c.gainTx2D2DRx(dist_c2d),
        'g_dij' : c.gainTx2D2DRx(dist_dij)
    }

    gain_dl = {
        'g_c2b' : c.gainTx2Cell(dist_b2c),
        'g_d2c' : c.gainTx2Cell(dist_d2c),
        'g_d2d' : c.gainD2DRx(dist_d2d),
        'g_c2d' : c.gainBS2Rx(dist_b2d),
        'g_dij' : c.gainTx2D2DRx(dist_dij)
    }

    beamPoint = allocate.selectBeamSector(sectorPoint, currentTime, initial['numScheduleBeam'])
    inSectorCUE = allocate.allSectorCUE(beamPoint, ue_point) #有在波束範圍內的CUE

    data_cue_ul = np.random.randint(low=dataCUEMin, high=dataCUEMax, size=initial['numCUE'])
    data_cue_dl = np.random.randint(low=dataCUEMin, high=dataCUEMax, size=initial['numCUE'])
    data_d2d_ul = np.random.randint(low=dataD2DMin, high=dataD2DMax, size=initial['numD2D'])
    data_d2d_dl = np.random.randint(low=dataD2DMin, high=dataD2DMax, size=initial['numD2D'])

    uplink = {
        'numCellTx' : config["numCUE"],
        'numCellRx' : config["numBS"],

        'data_cue' : data_cue_ul,
        'data_d2d' : data_d2d_ul,

        'currentTime' : currentTime
    }

    sys_parameter_ul = {**initial, **environment, **gain_ul, **uplink}

    sys_parameter_ul = allocate.cellAllocateUl(**sys_parameter_ul)
    sys_parameter_ul = measure.UplinkCUE(**sys_parameter_ul)
    sys_parameter_ul = measure.Cell_in_OmniD2D(**sys_parameter_ul)
    sys_parameter_ul = measure.Cell_in_DirectD2D(**sys_parameter_ul)
    sys_parameter_ul = measure.BetweenD2D(**sys_parameter_ul)
    sys_parameter_ul = measure.InterferenceD2D(**sys_parameter_ul)
    sys_parameter_ul = method.initial_parameter(**sys_parameter_ul)
    # sys_parameter_ul['i_d2d'] = 
    sys_parameter_ul = method.phase1(**sys_parameter_ul)
    print(sys_parameter_ul['i_d2d'])
    print(sys_parameter_ul['i_d2c'])
    # sys_parameter_ul = proposed.find_d2d_root(**sys_parameter_ul)
    # sys_parameter_ul = proposed.create_interference_graph(**sys_parameter_ul)
    # sys_parameter_ul = proposed.find_longest_path(**sys_parameter_ul)
    # sys_parameter_ul = proposed.phase2_power_configure(**sys_parameter_ul)
    # sys_parameter_ul = proposed.phase3_power_configure(**sys_parameter_ul)
    # print(sys_parameter_ul['i_d2d'])
    # print(sys_parameter_ul['i_d2c'])
    
    downlink = {
        'numCellTx' : config["numBS"],
        'numCellRx' : config["numCUE"],

        'beamPoint' : beamPoint,
        'inSectorCUE' : inSectorCUE,

        'data_cue' : data_cue_dl,
        'data_d2d' : data_d2d_dl,

        'currentTime' : currentTime
    }

    sys_parameter_dl = {**initial, **environment, **gain_dl, **downlink}

    # sys_parameter_dl = allocate.cellAllocateDl(**sys_parameter_dl)
    # sys_parameter_dl = measure.DownlinkBS(**sys_parameter_dl)
    # sys_parameter_dl = measure.Cell_in_OmniD2D(**sys_parameter_dl)
    # sys_parameter_dl = measure.Cell_in_DirectD2D(**sys_parameter_dl)
    # sys_parameter_dl = measure.BetweenD2D(**sys_parameter_dl)
    # sys_parameter_dl = measure.InterferenceD2D(**sys_parameter_dl)
    # sys_parameter_dl = proposed.find_d2d_root(**sys_parameter_dl)
    # sys_parameter_dl = proposed.create_interference_graph(**sys_parameter_dl)
    # sys_parameter_dl = proposed.find_longest_path(**sys_parameter_dl)
    # sys_parameter_dl = proposed.phase2_power_configure(**sys_parameter_dl)
    # sys_parameter_dl = proposed.phase3_power_configure(**sys_parameter_dl)


    #JUAD Method test
    # sys_parameter_ul = allocate.cellAllocateUl(**sys_parameter_ul)
    # sys_parameter_ul = measure.UplinkCUE(**sys_parameter_ul)
    # sys_parameter_ul = measure.Cell_in_OmniD2D(**sys_parameter_ul)
    # sys_parameter_ul = measure.Cell_in_DirectD2D(**sys_parameter_ul)
    # sys_parameter_ul = measure.BetweenD2D(**sys_parameter_ul)

    # weight_matrix = np.zeros((sys_parameter_ul['numD2D'], sys_parameter_ul['numCUE']))
    # weight_cue = np.zeros((sys_parameter_ul['numD2D'], sys_parameter_ul['numCUE']))
    # weight_d2d = np.zeros((sys_parameter_ul['numD2D'], sys_parameter_ul['numCUE']))
    # power_cue = np.zeros((sys_parameter_ul['numD2D'], sys_parameter_ul['numCUE']))
    # power_d2d = np.zeros((sys_parameter_ul['numD2D'], sys_parameter_ul['numCUE']))
    
    # sys_parameter_ul.update({'weight_matrix' : weight_matrix})
    # sys_parameter_ul.update({'weight_cue' : weight_cue})
    # sys_parameter_ul.update({'weight_d2d' : weight_d2d})

    # for j in range(sys_parameter_ul['numD2D']):
    #     for i in sys_parameter_ul['candicateCUE']:
    #         sys_parameter_ul = juad.juad_ul(i, j, **sys_parameter_ul)
    #         power_cue[j][i] = sys_parameter_ul['power_cue']
    #         power_d2d[j][i] = sys_parameter_ul['power_d2d']
    # # print(sys_parameter_ul['weight_matrix'])
    # sys_parameter_ul = juad.bipartite_matching(i, j, **sys_parameter_ul)
    
    # for d2d,cue in sys_parameter_ul['matching_index']:
    #     sinr_cue = (power_cue[d2d][cue] * sys_parameter_ul['g_c2b'][cue][0][0]) / (sys_parameter_ul['N0'] + power_d2d[d2d][cue] * sys_parameter_ul['g_d2c'][d2d][0][0])
    #     sinr_d2d = (power_d2d[d2d][cue] * sys_parameter_ul['g_d2d'][d2d][0][0]) / (sys_parameter_ul['N0'] + power_cue[d2d][cue] * sys_parameter_ul['g_c2d'][cue][d2d][0][0])
    #     print('matching',sys_parameter_ul['matching_index'])
    #     print(d2d,cue)
    #     print('power cue',power_cue[d2d][cue])
    #     print('power d2d',power_d2d[d2d][cue])
    #     print(sinr_cue)
    #     print(sys_parameter_ul['minCUEsinr'])
    #     print(sinr_d2d)
    #     print(sys_parameter_ul['minD2Dsinr'])
    #     print()

    # draw.drawCell(**{**initial, **environment})


# draw.drawCell(**{**initial, **environment})