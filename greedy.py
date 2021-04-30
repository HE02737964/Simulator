import numpy as np
import tools

def initial_parameter(**parameter):
    assignmentD2D = np.zeros((parameter['numD2D'], parameter['numRB']))
    d2d_use_rb_List = np.zeros((parameter['numD2D'], parameter['numRB']), dtype=int)

    parameter.update({'powerD2DList' : np.zeros(parameter['numD2D'])})
    parameter.update({'nStartD2D' : np.asarray([])})
    parameter.update({'assignmentD2D' : assignmentD2D})
    parameter.update({'d2d_use_rb_List' : d2d_use_rb_List})
    parameter.update({'throughput' : 0})
    
    parameter = cal_num_interfered_neighbor(**parameter)
    parameter = cal_priority(**parameter)
    return parameter

#計算D2D的干擾鄰居數量
def cal_num_interfered_neighbor(**parameter):
    i_len = np.zeros(parameter['numD2D'])
    #干擾鄰居的數量
    for tx in range(parameter['numD2D']):
        i_len[tx] = len(parameter['i_d2d'][tx]['cue']) + len(parameter['i_d2d'][tx]['d2d']) + 1
    parameter.update({'num_interference' : i_len})
    return parameter

#計算D2D的priority(越大優先權越高)
def cal_priority(**parameter):
    priority = (parameter['data_d2d'] / parameter['num_interference']) * (1 / parameter['scheduleTimes'])
    sort_priority = (-priority).argsort()
    parameter.update({'priority' : priority})
    parameter.update({'priority_sort_index' : sort_priority})
    return parameter

#得到d2d能使用的rb
def get_d2d_use_rb(d2d, **parameter):
    d2dUseRBList = np.ones(parameter['numRB'], dtype=int)
    cueUseRBList = np.zeros(parameter['numRB'], dtype=int)
    dijUseRBList = np.zeros(parameter['numRB'], dtype=int)
    bitmap = np.zeros(parameter['numRB'], dtype=int)

    #cue干擾d2d
    # for c_tx in range(parameter['numCellTx']):
    #     if d2d in parameter['t_c2d'][c_tx]:
    #         cueUseRBList = np.logical_or(cueUseRBList, parameter['assignmentTxCell'][c_tx])
    #d2d干擾cue
    for c_rx in range(parameter['numCellRx']):
        if c_rx in parameter['t_d2c'][d2d]:
            cueUseRBList = np.logical_or(cueUseRBList, parameter['assignmentRxCell'][c_rx])
    
    for d in range(parameter['numD2D']):
        if d2d != d:
            if d in parameter['t_d2d'][d2d] or d2d in parameter['t_d2d'][d]:
                dijUseRBList = np.logical_or(dijUseRBList, parameter['assignmentD2D'][d])

    bitmap = np.logical_or(cueUseRBList, dijUseRBList) 
    d2dUseRBList = d2dUseRBList - bitmap
    parameter['d2d_use_rb_List'][d2d] = d2dUseRBList
    return parameter

def get_d2d_sys_info(tbs):
    convert = tools.Convert()
    cqi = convert.TBS_CQI_mapping(tbs)
    sinr = convert.CQI_SINR_mapping(cqi)
    sinr = convert.dB_to_mW(sinr)
    return cqi, sinr

#計算d2d每個rx在每個rb上的干擾
def cal_d2d_interference(tx, rx, rb, **parameter):
    interference = 0
    for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
        if parameter['assignmentD2D'][tx][rb] == 1 and parameter['assignmentD2D'][i][rb] == 1:
            interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
    for i in parameter['i_d2d_rx'][tx][rx]['cue']:
        if parameter['assignmentD2D'][tx][rb] == 1 and parameter['assignmentTxCell'][i][rb] == 1:
            interference = interference + (parameter['powerCUEList'][i] * parameter['g_c2d'][i][tx][rx][rb])
    return interference

#計算cue在每個rb上的干擾
def cal_cue_interference(cue, rb, **parameter):
    interference = 0
    for i in parameter['i_d2c'][cue]:
        if parameter['assignmentRxCell'][cue][rb] == 1 and parameter['assignmentD2D'][i][rb] == 1:
            interference = interference + (parameter['powerD2DList'][i] * parameter['g_d2c'][i][cue][rb])
    return interference

#計算d2d的sinr
def cal_d2d_sinr(d2d, **parameter):
    sinr_list = np.zeros((parameter['numD2DReciver'][d2d], parameter['numRB']))
    for rx in range(parameter['numD2DReciver'][d2d]):
        for rb in range(parameter['numRB']):
            interference = cal_d2d_interference(d2d, rx, rb, **parameter)
            print('d2d',d2d,'rx',rx,'rb',rb,'i',interference)
            sinr_list[rx][rb] = (parameter['powerD2DList'][d2d] * parameter['g_d2d'][d2d][rx][rb]) / ( parameter['N0'] + interference)
    sinr_nonzero_list = sinr_list[np.nonzero(sinr_list)]
    return np.min(sinr_nonzero_list)

#計算cue的sinr
def cal_cue_sinr(cue, **parameter):
    sinr_list = np.zeros((parameter['numCellRx'], parameter['numRB']))
    for rx in range(parameter['numCellRx']):
        for rb in range(parameter['numRB']):
            interference = cal_cue_interference(rx, rb, **parameter)
            sinr_list[rx][rb] = (parameter['powerCUEList'][cue] * parameter['g_c2b'][cue][rx][rb]) / ( parameter['N0'] + interference)
    sinr_nonzero_list = sinr_list[np.nonzero(sinr_list)]
    return np.min(sinr_nonzero_list)

def cal_need_power(tx, **parameter):
    powerList = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
    parameter['assignmentD2D'][tx] = np.copy(parameter['d2d_use_rb_List'][tx])
    for rx in range(parameter['numD2DReciver'][tx]):
        for rb in range(parameter['numRB']):
            interference = cal_d2d_interference(tx, rx, rb, **parameter)
            print('in cal power d2d',tx,'rx',rx,'rb',rb,'i',interference)
            powerList[rx][rb] = (parameter['minD2Dsinr'][tx] * (parameter['N0'] + interference)) / parameter['g_d2d'][tx][rx][rb]
    print('d2d',tx,'power list',powerList)
    parameter['assignmentD2D'][tx].fill(0)
    power = np.max(powerList)
    print('d2d',tx,'power',power)

    if power < parameter['Pmin']:
        power = parameter['Pmin']
    if power > parameter['Pmax']:
        power = 0
    print('d2d',tx,'power',power)
    return power

def greedy(**parameter):
    tool = tools.Tool()
    parameter = initial_parameter(**parameter)
    print('interference relationship',parameter['i_d2d'])

    d2d_need_rb = [0 for i in range(parameter['numD2D'])]

    for d2d in parameter['priority_sort_index']:
        parameter = get_d2d_use_rb(d2d, **parameter)
        print('d2d',d2d,'d2d_use_rb_List',parameter['d2d_use_rb_List'][d2d])
        numRB = np.sum(parameter['d2d_use_rb_List'][d2d])
        print('d2d',d2d,parameter['data_d2d'][d2d])
        tbs, rb = tool.data_tbs_mapping(parameter['data_d2d'][d2d], parameter['numRB'])
        print('d2d',d2d,tbs, rb)
        d2d_need_rb[d2d] = rb
        if numRB == 0 or numRB < d2d_need_rb[d2d]:
            print('d2d',d2d,'numRB',numRB,'need rb',d2d_need_rb[d2d])
            parameter['nStartD2D'] = np.append(parameter['nStartD2D'],d2d)
        else:
            cqi, sinr = get_d2d_sys_info(tbs)
            parameter['minD2Dsinr'][d2d] = sinr

            power = cal_need_power(d2d, **parameter)
            
            if power != 0:
                parameter['powerD2DList'][d2d] = power
                parameter['assignmentD2D'][d2d] = parameter['d2d_use_rb_List'][d2d].copy()
            else:
                print('d2d',d2d,'power not enough')
                parameter['nStartD2D'] = np.append(parameter['nStartD2D'],d2d)
    
    for d2d in range(parameter['numD2D']):
        if parameter['powerD2DList'][d2d] != 0 and parameter['assignmentD2D'][d2d].any():
            parameter['throughput'] = parameter['throughput'] + parameter['data_d2d'][d2d]

    for d2d in range(parameter['numD2D']):
        if parameter['powerD2DList'][d2d] != 0:
            sinr = cal_d2d_sinr(d2d, **parameter)
            # print('need sinr',parameter['minD2Dsinr'][i])
            # print('cal d2d',i,sinr)
            if sinr < parameter['minD2Dsinr'][d2d]:
                print('d2d',d2d,'sinr',sinr,'min sinr',parameter['minD2Dsinr'][d2d])
    print('throughput',parameter['throughput'])
    print('power list greedy',parameter['powerD2DList'])
    return parameter