import numpy as np
import json
import genrator
import channel
import allocate
import measure


def get_initial():
    with open('config.json', 'r') as f:
        config = json.load(f)

    maxReciver = config['maxReciver']
    d2dDistance = config['d2dDistance']
    directCUE = config['directCUE']
    directD2D = config['directD2D']
    N_dBm = config['N_dBm']
    bw = config['bw']
    N0 = (10**(N_dBm / 10)) #1Hz的熱噪聲，單位mW
    N0 = N0 * bw            #1個RB的熱噪聲，單位mW

    initial = {
        'radius' : config['radius'],
        'numCUE' : config['numCUE'],
        'numD2D' : config['numD2D'],
        'numRB' : config['numRB'],
        'numBS' : config['numBS'],
        'perScheduleCUE' : config['perScheduleCUE'],
        'N0' : N0,
        'Pmax' : config['Pmax'],
        'Pmin' : config['Pmin'],
        'cqiLevel' : config['cqiLevel'],
        'beamWide' : config['beamWide'],
        'totalBeam' : config['totalBeam'],
        'numScheduleBeam' : config['numScheduleBeam'],
        'numD2DCluster' : config['numD2DCluster'],
        'clusterRadius' : config['clusterRadius'],
        'numDensity' : config['numDensity'],
        'dataCUEMax' : config['dataCUEMax'],
        'dataCUEMin' : config['dataCUEMin'],
        'dataD2DMax' : config['dataD2DMax'],
        'dataD2DMin' : config['dataD2DMin'],
    }

    numD2DReciver = np.random.randint(low=1, high=maxReciver+1, size=initial['numD2D'])

    g = genrator.Genrator(initial['radius'])

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

        'numAssignment' : 0,

        'sectorPoint' : sectorPoint
    }

    initial_parameter = {**initial, **environment}
    return initial_parameter

def initial_ul(**parameter):
    c = channel.Channel(parameter['numRB'], parameter['numD2DReciver'])
    scheduleTimes_ul = np.zeros(parameter['numD2D'])

    ul = {
        'scheduleTimes' : scheduleTimes_ul
    }

    gain_ul = {
        'g_c2b' : c.gainTx2Cell(parameter['d_c2b']),
        'g_d2c' : c.gainTx2Cell(parameter['d_d2b']),
        'g_d2d' : c.gainD2DRx(parameter['d_d2d']),
        'g_c2d' : c.gainTx2D2DRx(parameter['d_c2d']),
        'g_dij' : c.gainTx2D2DRx(parameter['d_dij'])
    }

    parameter = {**parameter, **ul, **gain_ul}
    return parameter

def initial_dl(**parameter):
    c = channel.Channel(parameter['numRB'], parameter['numD2DReciver'])
    scheduleTimes_dl = np.zeros(parameter['numD2D'])

    dl = {
        'scheduleTimes' : scheduleTimes_dl
    }

    gain_dl = {
        'g_c2b' : c.gainTx2Cell(parameter['d_b2c']),
        'g_d2c' : c.gainTx2Cell(parameter['d_d2c']),
        'g_d2d' : c.gainD2DRx(parameter['d_d2d']),
        'g_c2d' : c.gainBS2Rx(parameter['d_b2d']),
        'g_dij' : c.gainTx2D2DRx(parameter['d_dij'])
    }

    parameter = {**parameter, **dl, **gain_dl}
    return parameter

def initial_UDL(**parameter):
    c = channel.Channel(parameter['numRB'], parameter['numD2DReciver'])
    
    scheduleTimes_ul = np.zeros(parameter['numD2D'])
    scheduleTimes_dl = np.zeros(parameter['numD2D'])
    
    ul = {
        'scheduleTimes' : scheduleTimes_ul
    }

    dl = {
        'scheduleTimes' : scheduleTimes_dl
    }

    gain_ul = {
        'g_c2b' : c.gainTx2Cell(parameter['d_c2b']),
        'g_d2c' : c.gainTx2Cell(parameter['d_d2b']),
        'g_d2d' : c.gainD2DRx(parameter['d_d2d']),
        'g_c2d' : c.gainTx2D2DRx(parameter['d_c2d']),
        'g_dij' : c.gainTx2D2DRx(parameter['d_dij'])
    }

    gain_dl = {
        'g_c2b' : c.gainTx2Cell(parameter['d_b2c']),
        'g_d2c' : c.gainTx2Cell(parameter['d_d2c']),
        'g_d2d' : c.gainD2DRx(parameter['d_d2d']),
        'g_c2d' : c.gainBS2Rx(parameter['d_b2d']),
        'g_dij' : c.gainTx2D2DRx(parameter['d_dij'])
    }

    parameter = {**parameter, **dl, **gain_ul, **gain_dl}
    return parameter

def get_ul_system_info(currentTime, **parameter):
    data_cue_ul = np.random.randint(low=parameter['dataCUEMin'], high=parameter['dataCUEMax'], size=parameter['numCUE'])
    data_d2d_ul = np.random.randint(low=parameter['dataD2DMin'], high=parameter['dataD2DMax'], size=parameter['numD2D'])
    
    uplink = {
        'numCellTx' : parameter['numCUE'],
        'numCellRx' : parameter['numBS'],

        'data_cue' : data_cue_ul,
        'data_d2d' : data_d2d_ul,

        'currentTime' : currentTime
    }

    parameter = {**parameter, **uplink}

    parameter = allocate.cellAllocateUl(**parameter)
    parameter = measure.UplinkCUE(**parameter)
    parameter = measure.Cell_in_OmniD2D(**parameter)
    parameter = measure.Cell_in_DirectD2D(**parameter)
    parameter = measure.BetweenD2D(**parameter)
    parameter = measure.InterferenceD2D(**parameter)
    return parameter

def get_dl_system_info(currentTime, **parameter):
    beamPoint = allocate.selectBeamSector(parameter['sectorPoint'], currentTime, parameter['numScheduleBeam'])
    inSectorCUE = allocate.allSectorCUE(beamPoint, parameter['ue_point']) #有在波束範圍內的CUE

    data_cue_dl = np.random.randint(low=parameter['dataCUEMin'], high=parameter['dataCUEMax'], size=parameter['numCUE'])
    data_d2d_dl = np.random.randint(low=parameter['dataD2DMin'], high=parameter['dataD2DMax'], size=parameter['numD2D'])
    downlink = {
        'numCellTx' : parameter['numBS'],
        'numCellRx' : parameter['numCUE'],

        'beamPoint' : beamPoint,
        'inSectorCUE' : inSectorCUE,

        'data_cue' : data_cue_dl,
        'data_d2d' : data_d2d_dl,

        'currentTime' : currentTime
    }

    parameter = {**parameter, **downlink}

    parameter = allocate.cellAllocateDl(**parameter)
    parameter = measure.DownlinkBS(**parameter)
    parameter = measure.Cell_in_OmniD2D(**parameter)
    parameter = measure.Cell_in_DirectD2D(**parameter)
    parameter = measure.BetweenD2D(**parameter)
    parameter = measure.InterferenceD2D(**parameter)
    return parameter