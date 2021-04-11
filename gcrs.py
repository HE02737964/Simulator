import numpy as np

def initial_parameter(**parameter):
    #初始階段

    #初始化傳輸功率
    initial_power = parameter['Pmax'] / parameter['numRB']

    #初始化vertex屬性
    ##宣告權重
    weight_cue = np.zeros((parameter['numCUE'], parameter['numRB']))
    weight_d2d = np.zeros((parameter['numD2D'], np.max(parameter['numD2DReciver']), parameter['numRB']))

    ###計算權重
    for c_tx in range(parameter['numCellTx']):
        for c_rx in range(parameter['numCellRx']):
            for rb in range(parameter['numRB']):
                if parameter['assignmentTxCell'][c_tx][rb] == 1:
                    weight_cue[c_tx][rb] = parameter['powerCUEList'][c_tx] * parameter['g_c2b'][c_tx][c_rx][rb]

    for tx in range(parameter['numD2D']):
        # gain_nonzero_list = parameter['g_d2d'][tx][np.nonzero(parameter['g_d2d'][tx])]
        # g_d2d = np.min(gain_nonzero_list)
        for rx in range(parameter['numD2DReciver'][tx]):
            weight_d2d[tx][rx] = initial_power * parameter['g_d2d'][tx][rx][0]

    ##宣告使用的顏色list
    #color_cue = assignmentTxCell
    color_d2d = np.zeros((parameter['numD2D'], parameter['numRB']))

    #宣告edge
    edge_cue = np.zeros((parameter['numCellTx'], parameter['numRB'], parameter['numRB']))
    edge_d2d = np.zeros((parameter['numD2D'], parameter['numRB'], parameter['numRB']))

    #宣告 throughput list
    interference_rb = np.zeros((parameter['numRB']))
    throughput_rb = np.zeros((parameter['numRB']))

    parameter.update({'initial_power' : initial_power})
    parameter.update({'weight_cue' : weight_cue})
    parameter.update({'weight_d2d' : weight_d2d})
    parameter.update({'assignmentD2D' : color_d2d})
    parameter.update({'edge_cue' : edge_cue})
    parameter.update({'edge_d2d' : edge_d2d})
    parameter.update({'interference_rb' : interference_rb})
    parameter.update({'throughput_rb' : throughput_rb})
    return parameter

def vertex_coloring(**parameter):
    rb = 0
    iterations = 5
    rb_use_list = {'cue' : [], 'd2d' : []}
    for cue in range(parameter['numCellTx']):
        if parameter['assignmentTxCell'][cue][rb] == 1:
            rb_use_list['cue'].append(cue)
    
    subscript = []
    for d2d in range(parameter['numD2D']):
        if d2d not in rb_use_list['d2d']:
            subscript.append(d2d)
    for i in range(len(subscript)):
        vertex = subscript[i]
        current_Vt = parameter['throughput_rb'][rb]
        current_Vi = parameter['interference_rb'][rb]
        rb_use_list['d2d'].append(vertex)


def cal_d2d_sinr(tx, rb_use_list, **parameter):
    rx_sinr = np.zeros((parameter['numD2DReciver'][tx]))
    for rx in range(parameter['numD2DReciver'][tx]):
        interference = cal_d2d_interference(tx, rx, rb_use_list)
        rx_sinr[rx] = (parameter['powerD2DList'] * parameter['g_d2d'][tx][rx][0]) / parameter['N0'] + interference
    return np.min(rx_sinr)

def cal_d2d_interference(tx, rx, rb_use_list, **parameter):
    interference = 0
    for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
        if i in rb_use_list['d2d']:
            interference = interference + parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][0]
    for i in parameter['i_d2d_rx'][tx][rx]['cue']:
        interference = interference + parameter['powerCUEList'][i] * parameter['g_c2d'][i][tx][rx][0]
    return interference