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

    #宣告RB use list 以及RB throughput list
    rb_use_status= np.full((parameter['numRB'], 1), {'cue' : [], 'd2d' : []})
    throughput_rb = np.zeros((parameter['numRB']))

    for cue in range(parameter['numCellTx']):
        for rb in range(parameter['numRB']):
            if parameter['assignmentTxCell'][cue][rb] == 1:
                rb_use_status[rb][0]['cue'] = np.append(rb_use_status[rb][0]['cue'], cue)
    
    rb_use_status[24][0]['d2d'] = np.append(rb_use_status[24][0]['d2d'], 87)

    parameter.update({'initial_power' : initial_power})
    parameter.update({'weight_cue' : weight_cue})
    parameter.update({'weight_d2d' : weight_d2d})
    parameter.update({'assignmentD2D' : color_d2d})
    parameter.update({'edge_cue' : edge_cue})
    parameter.update({'edge_d2d' : edge_d2d})
    parameter.update({'rb_use_status' : rb_use_status})
    parameter.update({'throughput_rb' : throughput_rb})
    return parameter

def vertex_coloring(**parameter):
    while  True:
        while True:
            subscript = parameter['rb_use_status'][0][parameter['rb_use_status'][0] == 0]
            vertex = 0