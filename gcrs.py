import numpy as np

def gcrs(**parameter):
    #初始階段

    #初始化傳輸功率
    initial_power = parameter['Pmax'] / parameter['numRB']

    #初始化vertex屬性
    ##宣告權重
    weight_cue = np.zeros((parameter['numTxCell'], parameter['numRB']))
    weight_d2d = np.zeros((parameter['numD2D'], np.max(parameter['numD2DReciver']), parameter['numRB']))

    ###計算權重
    for cue in range(parameter['numTxCell']):
        for rx in range(parameter['numCellRx']):
            weight_cue[cue] = initial_power * parameter['g_c2b'][cue][rx][0]

    for tx in range(parameter['numD2D']):
        # gain_nonzero_list = parameter['g_d2d'][tx][np.nonzero(parameter['g_d2d'][tx])]
        # g_d2d = np.min(gain_nonzero_list)
        for rx in range(parameter['numD2DReciver'][tx]):
            weight_d2d[tx][rx] = initial_power * parameter['g_d2d'][tx][rx][0]

    ##宣告使用的顏色list
    color_cue = np.zeros((parameter['numTxCell'], parameter['numRB']))
    color_d2d = np.zeros((parameter['numD2D'], parameter['numRB']))

    #宣告edge
    edge_cue = np.zeros((parameter['numTxCell'], parameter['numRB'], parameter['numRB']))
    edge_d2d = np.zeros((parameter['numD2D'], parameter['numRB'], parameter['numRB']))

    #宣告RB use list 以及RB throughput list
    rb_use_status= np.full((parameter['numRB']), {'cue' : [], 'd2d' : []})
    throughput_rb = np.zeros((parameter['numRB']))