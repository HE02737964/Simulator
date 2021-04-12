import numpy as np
import tools

def initial_parameter(**parameter):
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

    #宣告power list
    powerD2DList = np.full((parameter['numD2D']), initial_power)

    parameter.update({'initial_power' : initial_power})
    parameter.update({'weight_cue' : weight_cue})
    parameter.update({'weight_d2d' : weight_d2d})
    parameter.update({'assignmentD2D' : color_d2d})
    parameter.update({'edge_cue' : edge_cue})
    parameter.update({'edge_d2d' : edge_d2d})
    parameter.update({'interference_rb' : interference_rb})
    parameter.update({'throughput_rb' : throughput_rb})
    parameter.update({'powerD2DList' : powerD2DList})
    return parameter

def vertex_coloring(**parameter):
    tool = tools.Tool()
    convert = tools.Convert()
    rb_status = []
    iterations = 5
    for rb in range(parameter['numRB']):
        rb_use_list = {'cue' : [], 'd2d' : []}
        rb_status.append(rb_use_list)
        
    for i in range(iterations):
        for rb in range(parameter['numRB']):
            for cue in range(parameter['numCellTx']):
                if parameter['assignmentTxCell'][cue][rb] == 1 and cue not in rb_status[rb]['cue']:
                    rb_status[rb]['cue'].append(cue)
            
            subscript = []
            for d2d in range(parameter['numD2D']):
                if d2d not in rb_status[rb]['d2d']:
                    subscript.append(d2d)
            while subscript:
                #選擇一個未著色的頂點
                vertex = subscript[0]
                
                #記錄當前Vt, Vi
                current_Vt = parameter['throughput_rb'][rb]
                current_Vi = parameter['interference_rb'][rb]

                #將vertex放入Sk裡
                rb_status[rb]['d2d'].append(vertex)

                #更新Vt
                throughput = 0
                flag = False
                for i in rb_status[rb]['d2d']:
                    sinr = cal_d2d_sinr(i, rb_status[rb], **parameter)
                    #要滿足所需之sinr
                    if sinr < parameter['minD2Dsinr'][i]:
                        flag = True
                        rb_status[rb]['d2d'].remove(vertex)
                        parameter['throughput_rb'][rb] = current_Vt
                        subscript.remove(vertex)

                for i in rb_status[rb]['cue']:
                    sinr = cal_cue_sinr(i, rb_status[rb], **parameter)
                    #要滿足所需之sinr
                    print(sinr)
                    print(parameter['minCUEsinr'][i])
                    if sinr < parameter['minCUEsinr'][i]:
                        if vertex in rb_status[rb]['d2d']:
                            flag = True
                            rb_status[rb]['d2d'].remove(vertex)
                            parameter['throughput_rb'][rb] = current_Vt
                            subscript.remove(vertex)
                if flag:
                    t = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr), 1)
                    throughput = throughput + t

                parameter['throughput_rb'][rb] = throughput

                if vertex in rb_status[rb]['d2d']:
                    #vertex不能讓throughput增長
                    if parameter['throughput_rb'][rb] < current_Vt:
                        #將vertex移除Sk
                        rb_status[rb]['d2d'].remove(vertex)
                        parameter['throughput_rb'][rb] = current_Vt
                        subscript.remove(vertex)
                    else:
                        subscript.remove(vertex)
        for rb in range(parameter['numRB']):
            pass
    print(rb_status)
    return parameter


def cal_d2d_sinr(tx, rb_use_list, **parameter):
    rx_sinr = np.zeros((parameter['numD2DReciver'][tx]))
    for rx in range(parameter['numD2DReciver'][tx]):
        interference = cal_d2d_interference(tx, rx, rb_use_list, **parameter)
        rx_sinr[rx] = (parameter['powerD2DList'][tx] * parameter['g_d2d'][tx][rx][0]) / (parameter['N0'] + interference)
    return np.min(rx_sinr)

def cal_d2d_interference(tx, rx, rb_use_list, **parameter):
    interference = 0
    for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
        if i in rb_use_list['d2d']:
            interference = interference + parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][0]
    for i in parameter['i_d2d_rx'][tx][rx]['cue']:
        if i in rb_use_list['cue']:
            interference = interference + parameter['powerCUEList'][i] * parameter['g_c2d'][i][tx][rx][0]
    return interference

def cal_cue_sinr(tx, rb_use_list, **parameter):
    sinr = 0
    for rx in range(parameter['numCellRx']):
        interference = cal_cue_interference(tx, rx, rb_use_list, **parameter)
        sinr = (parameter['powerCUEList'][tx] * parameter['g_c2b'][tx][rx][0]) / (parameter['N0'] + interference)
    return sinr

def cal_cue_interference(tx, rx, rb_use_list, **parameter):
    interference = 0
    for i in parameter['i_d2c'][rx]:
        if i in rb_use_list['d2d']:
            interference = interference + parameter['powerCUEList'][tx] * parameter['g_d2c'][i][tx][rx][0]
    return interference

def cal_d2d_edge_weight(u, v, rb, **parameter):
    uv_weight_list = np.zeros((parameter['numD2DReciver'][v]))
    vu_weight_list = np.zeros((parameter['numD2DReciver'][u]))

    #表示 u 會干擾 v
    if u in parameter['i_d2d'][v]['d2d']:
        for v_rx in range(parameter['numD2DReciver'][v]):
            if u in parameter['i_d2d_rx'][v][v_rx]['d2d']:
                uv_weight_list[v_rx] = parameter['powerD2DList'][u] * parameter['g_dij'][u][v][v_rx][rb]
    
    #表示 v 會干擾 u
    if v in parameter['i_d2d'][u]['d2d']:
        for u_rx in range(parameter['numD2DReciver'][u]):
            if v in parameter['i_d2d_rx'][u][u_rx]['d2d']:
                vu_weight_list[u_rx] = parameter['powerD2DList'][v] * parameter['g_dij'][v][u][u_rx][rb]
    weight = np.max(uv_weight_list) + np.max(vu_weight_list)
    return weight