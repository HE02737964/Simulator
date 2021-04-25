import numpy as np
import tools

def initial_parameter(**parameter):
    assignmentD2D = np.zeros((parameter['numD2D'], parameter['numRB']))

    parameter.update({'powerD2DList' : np.zeros(parameter['numD2D'])})
    parameter.update({'nStartD2D' : np.asarray([])})
    parameter.update({'assignmentD2D' : assignmentD2D})
    
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
    #cue干擾d2d
    for c_tx in range(parameter['numCellTx']):
        if d2d in parameter['t_c2d'][c_tx]:
            cueUseRBList = np.logical_or(cueUseRBList, parameter['assignmentTxCell'][c_tx])
    #d2d干擾cue
    for c_rx in range(parameter['numCellRx']):
        if c_rx in parameter['t_d2c'][d2d]:
            cueUseRBList = np.logical_or(cueUseRBList, parameter['assignmentRxCell'][c_rx])
    
    for d in range(parameter['numD2D']):
        if d in parameter['t_d2c'][d2d] or d2d in parameter['t_c2d'][d]:
            d2dUseRBList = np.logical_or(d2dUseRBList, parameter['assignmentD2D'][d])
    d2dUseRBList = d2dUseRBList - cueUseRBList
    parameter['d2d_use_rb_List'][d2d] = d2dUseRBList
    return parameter

def get_d2d_sys_info(tbs):
    convert = tools.Convert()
    cqi = convert.TBS_CQI_mapping(tbs)
    sinr = convert.CQI_SINR_mapping(cqi)
    sinr = convert.dB_to_mW(sinr)
    return cqi, sinr

def greedy(**parameter):
    tool = tools.Tool()
    parameter = initial_parameter(**parameter)

    d2d_need_rb = []

    #找出d2d所需RB數量、SINR、Power
    for d2d in range(parameter['numD2D']):
        parameter = get_d2d_use_rb(d2d, **parameter)
        numRB = np.sum(parameter['d2d_use_rb_list'][d2d])
        tbs, rb = tool.data_tbs_mapping(parameter['data_d2d'][d2d], parameter['numRB'])
        d2d_need_rb.append(rb)
        if numRB == 0 or numRB < d2d_need_rb[d2d]:
            parameter['nStartD2D'].append(d2d)
        else:
            cqi, sinr = get_d2d_sys_info(tbs)
            parameter['minD2Dsinr'][d2d] = sinr

    for candicate in parameter['priority_sort_index']:
        if candicate not in parameter['nStartD2D']:
            parameter['assignmentD2D'][candicate] = parameter['d2d_use_rb_list'][candicate].copy()
            gain = np.min(parameter['g_d2d'][d2d])
            parameter['powerD2DList'][d2d] = ((parameter['minD2Dsinr'][candicate] * parameter['N0']) / gain)
    print(parameter['t_c2d'])
    print(parameter['t_d2c'])
    print(parameter['t_d2d'])