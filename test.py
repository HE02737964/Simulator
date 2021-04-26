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
import gcrs
import greedy
import time
import sys

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
scheduleTimes_ul = np.zeros(initial['numD2D'])
# scheduleTimes_ul = np.array([3,4,2,1,6])
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

    'scheduleTimes' : scheduleTimes_ul,

    'numAssignment' : 0
}

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

total = 0
t_m = 0
juad_throughput = 0
gcrs_throughput = 0
start = time.time()
simu = 0
meth = 0
gcrt = 0
p_assign = 0
g_assign = 0
for currentTime in range(0,1):
    simu_start = time.time()
    
    beamPoint = allocate.selectBeamSector(sectorPoint, currentTime, initial['numScheduleBeam'])
    inSectorCUE = allocate.allSectorCUE(beamPoint, ue_point) #有在波束範圍內的CUE

    data_cue_ul = np.random.randint(low=dataCUEMin, high=dataCUEMax, size=initial['numCUE'])
    data_cue_dl = np.random.randint(low=dataCUEMin, high=dataCUEMax, size=initial['numCUE'])
    data_d2d_ul = np.random.randint(low=dataD2DMin, high=dataD2DMax, size=initial['numD2D'])
    data_d2d_dl = np.random.randint(low=dataD2DMin, high=dataD2DMax, size=initial['numD2D'])
    total = total + np.sum(data_d2d_ul) + np.sum(data_d2d_dl)
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

    
    #proposed
    method_ul = sys_parameter_ul.copy()
    # simu_end = time.time()
    # meth_start = time.time()
    method_ul = method.phase1(**method_ul)
    for i in range(method_ul['numD2D']):
        if method_ul['powerD2DList'][i] != 0:
            t_m = t_m + data_d2d_ul[i]
    p_assign = p_assign + method_ul['numAssignment']
    # meth_end = time.time()

    #juad
    # sys_parameter_ul = juad.initial_parameter(**sys_parameter_ul)
    # sys_parameter_ul = juad.maximum_matching(**sys_parameter_ul)
    
    # assignmentD2D = [i[0] for i in sys_parameter_ul['matching_index']]
    # assignmentCUE = [i[1] for i in sys_parameter_ul['matching_index']]

    # for i in range(len(assignmentCUE)):
    #     d2d = assignmentD2D[i]
    #     cue = assignmentCUE[i]
    #     if sys_parameter_ul['powerCUEList'][d2d][cue] != 0 and sys_parameter_ul['powerD2DList'][d2d][cue] != 0:
    #         # print('cal powr cue', assignmentCUE[i], sys_parameter_ul['powerCUEList'][i][assignmentCUE[i]])
    #         # print('min sinr cue', assignmentCUE[i], sys_parameter_ul['minCUEsinr'][assignmentCUE[i]])
    #         # print('cal sinr cue', assignmentCUE[i], sys_parameter_ul['sinrCUEList'][i][assignmentCUE[i]])
    #         # print('cal powr d2d', i, sys_parameter_ul['powerD2DList'][i][assignmentCUE[i]])
    #         # print('min sinr d2d', i,  sys_parameter_ul['minD2Dsinr'][i])
    #         # print('cal sinr d2d', i, sys_parameter_ul['sinrD2DList'][i][assignmentCUE[i]])
    #         # print()
    #         juad_throughput = juad_throughput + sys_parameter_ul['weight_d2d'][d2d][cue]

    
    #gcrs

    # sys.stdout = open('gcrs_debug', 'w')
    gcrs_ul = sys_parameter_ul.copy()
    # gcrs_start = time.time()
    # print('current time',time.ctime(time.time()))
    gcrs_ul = gcrs.vertex_coloring(**gcrs_ul)
    # print('data_d2d',gcrs_ul['data_d2d'])
    gcrs_throughput = gcrs_throughput + np.sum(gcrs_ul['d2d_total_throughput'])
    g_assign = g_assign + gcrs_ul['numAssignment']
    # gcrs_end = time.time()

    #greedy
    greedy_ul = sys_parameter_ul.copy()
    greedy_ul = greedy.greedy(**greedy_ul)
    # print(greedy_ul['priority_sort_index'])
    print('greedy throughput',greedy_ul['throughput'])
    assign = greedy_ul['numD2D'] - len(greedy_ul['nStartD2D'])
    print('greedy assign',assign)
    # print('nStartD2D',greedy_ul['nStartD2D'])
    # print('sum nstartD2D',len(greedy_ul['nStartD2D']))
    # for i in range(greedy_ul['numD2D']):
    #     print(greedy_ul['assignmentD2D'][i])
    #     print('d2d',i,greedy_ul['powerD2DList'][i])
    # print(greedy_ul['powerD2DList'])

# -------------------------------------------------------------------------------------------------------------------------------------

    #downlink
    downlink = {
        'numCellTx' : config["numBS"],
        'numCellRx' : config["numCUE"],

        'beamPoint' : beamPoint,
        'inSectorCUE' : inSectorCUE,

        'data_cue' : data_cue_dl,
        'data_d2d' : data_d2d_dl,

        'currentTime' : currentTime
    }
    simu1_start = time.time()
    sys_parameter_dl = {**initial, **environment, **gain_dl, **downlink}

    sys_parameter_dl = allocate.cellAllocateDl(**sys_parameter_dl)
    sys_parameter_dl = measure.DownlinkBS(**sys_parameter_dl)
    sys_parameter_dl = measure.Cell_in_OmniD2D(**sys_parameter_dl)
    sys_parameter_dl = measure.Cell_in_DirectD2D(**sys_parameter_dl)
    sys_parameter_dl = measure.BetweenD2D(**sys_parameter_dl)
    sys_parameter_dl = measure.InterferenceD2D(**sys_parameter_dl)
    
    # # simu1_end = time.time()
    # # #proposed
    # meth1_start = time.time()
    # method_dl = sys_parameter_dl.copy()
    # method_dl = method.initial_parameter(**method_dl)
    # method_dl = method.phase1(**method_dl)
    # for i in range(method_dl['numD2D']):
    #     if method_dl['powerD2DList'][i] != 0:
    #         t_m = t_m + data_d2d_dl[i]
    # p_assign = p_assign + method_dl['numAssignment']
    # meth1_end = time.time()

    # simu = simu + (simu_end - simu_start) + (simu1_end - simu1_start)
    # meth = meth + (meth_end - meth_start) #+ (meth1_end - meth1_start)
    # gcrt = gcrt + (gcrs_end - gcrs_start)

    #juad
    # sys_parameter_dl = juad.initial_parameter(**sys_parameter_dl)
    # sys_parameter_dl = juad.maximum_matching(**sys_parameter_dl)

    # assignmentD2D = [i[0] for i in sys_parameter_dl['matching_index']]
    # assignmentCUE = [i[1] for i in sys_parameter_dl['matching_index']]

    # for i in range(len(assignmentCUE)):
    #     if sys_parameter_dl['powerCUEList'][i][assignmentCUE[i]] != 0 and sys_parameter_dl['powerD2DList'][i][assignmentCUE[i]] != 0:
    #         # print('min sinr cue', assignmentCUE[i], sys_parameter_dl['minCUEsinr'][assignmentCUE[i]])
    #         # print('cal sinr cue', assignmentCUE[i], sys_parameter_dl['sinrCUEList'][i][assignmentCUE[i]])
    #         # print('min sinr d2d', i,  sys_parameter_dl['minD2Dsinr'][assignmentCUE[i]])
    #         # print('cal sinr d2d', i, sys_parameter_dl['sinrD2DList'][i][assignmentCUE[i]])
    #         # print()
    #         juad_throughput = juad_throughput + sys_parameter_dl['weight_d2d'][i][assignmentCUE[i]]

    #gcrs
    # gcrs_dl = sys_parameter_dl.copy()
    # gcrs_dl = gcrs.initial_parameter(**gcrs_dl)
    # gcrs_dl = gcrs.vertex_coloring(**gcrs_dl)
    # g_assign = g_assign + gcrs_dl['numAssignment']
    # gcrs_throughput = gcrs_throughput + np.sum(gcrs_dl['d2d_total_throughput'])
    
    # draw.drawCell(**{**initial, **environment})
end = time.time()
# print("總執行時間：%f 秒" % (end - start))
# print("模擬器時間：%f 秒" % simu)
# print("方法的時間：%f 秒" % meth)
# print("GCRS的時間：%f 秒" % gcrt)
# print('Maximum throughput', total)
print('prop_throughput',t_m)
print('num assignment', p_assign)
# print('juad_throughput',juad_throughput)
print('gcrs_throughput',gcrs_throughput)
print('num assignment', g_assign)
# print(data_d2d_ul)
# print(data_d2d_dl)
sys.stdout.close()
# draw.drawCell(**{**initial, **environment})

# file1 = open('data1.txt', 'w')
# for key in sys_parameter_ul_p:
#     value = sys_parameter_ul_p[key]
#     file1.write(str(key))
#     file1.write(" ")
#     file1.write(str(value))
#     file1.write("\n")
# file1.close()