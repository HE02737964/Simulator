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
    for cue in range(parameter['numCellRx']):
        if d2d in parameter['i_d2c'][cue]:
            #CUE有使用的RB做or運算，找出所有rx cue會被d2d干擾的RB
            cueUseRBList = np.logical_or(cueUseRBList, parameter['assignmentRxCell'][cue])
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

    d2d_use_rb_list = []

    #找出d2d所需RB數量、SINR、Power
    for d2d in range(parameter['numD2D']):
        gain = np.min(parameter['g_d2d'][d2d])
        tbs, rb = tool.data_tbs_mapping(parameter['data_d2d'][d2d], parameter['numRB'])
        cqi, sinr = get_d2d_sys_info(tbs)
        d2d_use_rb_list.append(rb)
        parameter['minD2Dsinr'][d2d] = sinr
        parameter['powerD2DList'][d2d] = ((sinr * parameter['N0']) / gain)

    # for candicate in parameter['priority_sort_index']:
        