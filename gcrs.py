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

    rb_use_status = []
    for rb in range(parameter['numRB']):
        rb_use_dict = {'cue' : [], 'd2d' : []}
        rb_use_status.append(rb_use_dict)

    #宣告edge
    edge_cue = np.zeros((parameter['numCellTx'], parameter['numRB'], parameter['numRB']))
    edge_d2d = np.zeros((parameter['numD2D'], parameter['numRB'], parameter['numRB']))

    #宣告 throughput list
    edge_rb = np.zeros((parameter['numRB']))
    throughput_rb = np.zeros((parameter['numRB']))
    throughput_cue = np.zeros((parameter['numRB']))
    throughput_d2d = np.zeros((parameter['numD2D'], parameter['numRB']))
    d2d_total_throughput = np.zeros((parameter['numD2D']))

    #宣告power list
    powerD2DList = np.full((parameter['numD2D'], parameter['numRB']), initial_power)

    #功率分配因子
    delta = np.zeros((parameter['numRB']))

    parameter.update({'initial_power' : initial_power})
    parameter.update({'weight_cue' : weight_cue})
    parameter.update({'weight_d2d' : weight_d2d})
    parameter.update({'assignmentD2D' : color_d2d})
    parameter.update({'rb_use_status' : rb_use_status})
    parameter.update({'edge_cue' : edge_cue})
    parameter.update({'edge_d2d' : edge_d2d})
    parameter.update({'edge_rb' : edge_rb})
    parameter.update({'throughput_rb' : throughput_rb})
    parameter.update({'throughput_cue' : throughput_cue})
    parameter.update({'throughput_d2d' : throughput_d2d})
    parameter.update({'d2d_total_throughput' : d2d_total_throughput})
    parameter.update({'powerD2DList' : powerD2DList})
    parameter.update({'delta' : delta})
    return parameter

def vertex_coloring(**parameter):
    #先更新每個RB裏頭CUE的throughput
    for rb in range(parameter['numRB']):
        cue_throughput = cal_Vt_cue(rb, **parameter)
        parameter['throughput_rb'][rb] = cue_throughput
        parameter['throughput_cue'][rb] = cue_throughput
    
    iterations = 1
    for i in range(iterations):
        for rb in range(parameter['numRB']):
            subscript = []
            for d2d in range(parameter['numD2D']):
                if d2d not in parameter['rb_use_status'][rb]['d2d']:
                    subscript.append(d2d)
            while subscript:
                #選擇一個未著色的頂點
                vertex = subscript[0]
                
                #記錄當前Vt, Vi
                current_Vt = parameter['throughput_rb'][rb]
                current_Vi = parameter['edge_rb'][rb]
                current_vertex_list = parameter['rb_use_status'][rb]['d2d'].copy()

                #將vertex放入Sk裡
                parameter['rb_use_status'][rb]['d2d'].append(vertex)

                #更新Vt
                cue_Vt = cal_Vt_cue(rb, **parameter)
                d2d_Vt = cal_Vt_d2d(rb, **parameter)
                new_Vt = cue_Vt + d2d_Vt
                new_vertex_list = parameter['rb_use_status'][rb]['d2d'].copy()
                
                #將vertex從Sk中移除
                parameter['rb_use_status'][rb]['d2d'].remove(vertex)

                #挑選最大Vt的那組vertex組合
                totalVi = 0
                if current_Vt < new_Vt:
                    parameter['rb_use_status'][rb]['d2d'] = new_vertex_list
                    parameter['throughput_rb'][rb] = new_Vt
                    subscript.remove(vertex)
                else:
                    parameter['rb_use_status'][rb]['d2d'] = current_vertex_list
                    parameter['throughput_rb'][rb] = current_Vt
                    subscript.remove(vertex)
                
                #更新Vi
                for cue in parameter['rb_use_status'][rb]['cue']:
                    for d2d in parameter['rb_use_status'][rb]['d2d']:
                        c2d_weight = cal_cue_edge_weight(cue, d2d, rb, **parameter)
                        totalVi = totalVi + c2d_weight
                for d2d_v in parameter['rb_use_status'][rb]['d2d']:
                    d2d_u = parameter['rb_use_status'][rb]['d2d'][-1]
                    if d2d_u != d2d_v:
                        dij_weight = cal_d2d_edge_weight(d2d_u, d2d_v, rb, **parameter)
                        totalVi = totalVi + dij_weight
                parameter['edge_rb'][rb] = totalVi

        #每個RB的Vi總和
        s = np.sum(parameter['edge_rb'])

        #計算每個RB上的功率分配因子(delta)
        for rb in range(parameter['numRB']):
            parameter['delta'][rb] = (1 / s*parameter['edge_rb'][rb])
            
            #計算每個D2D在每個RB上的傳輸功率
            for d2d in range(parameter['numD2D']):
                if d2d in parameter['rb_use_status'][rb]['d2d']:
                    power = parameter['delta'][rb] * parameter['Pmax']
                    if power > parameter['Pmax']:
                        power = parameter['Pmax']
                    if power < parameter['Pmin']:
                        power = parameter['Pmin']
                    parameter['powerD2DList'][d2d][rb] = power
                else:
                    parameter['powerD2DList'][d2d][rb] = 0
    parameter = check_some_value(**parameter)
    return parameter

def check_some_value(**parameter):
    tool = tools.Tool()
    convert = tools.Convert()

    for rb in range(parameter['numRB']):
        #扣除掉CUE的throughput
        parameter['throughput_rb'][rb] = parameter['throughput_rb'][rb] - parameter['throughput_cue'][rb]
        
        #紀錄會使CUE的sinr小於所需值的D2D
        deleteD2D = []
        # for cue in parameter['rb_use_status'][rb]['cue']:
        #     sinr = cal_cue_sinr(cue, rb, **parameter)
        #     if convert.mW_to_dB(parameter['minCUEsinr'][cue]) < convert.mW_to_dB(sinr):
        #         for d2d in parameter['i_d2c']:
        #             if d2d in parameter['rb_use_status'][rb]['d2d']:
        #                 sinr = cal_d2d_sinr(d2d, rb, **parameter)
        #                 d_vt = convert_sinr_vt(sinr)
        #                 parameter['throughput_rb'][rb] = parameter['throughput_rb'][rb] - d_vt
        #                 deleteD2D.append(d2d)
        
        #紀錄sinr不滿足所需值的D2D
        for d2d in parameter['rb_use_status'][rb]['d2d']:
            sinr = cal_d2d_sinr(d2d, rb, **parameter)
            d_vt = convert_sinr_vt(sinr)
            if convert.mW_to_dB(parameter['minD2Dsinr'][d2d]) > convert.mW_to_dB(sinr) and d2d not in deleteD2D:
                parameter['throughput_rb'][rb] = parameter['throughput_rb'][rb] - d_vt
                deleteD2D.append(d2d)

        #將先前紀錄起來的D2D從RB使用列表中移除
        for d2d in deleteD2D:
            parameter['rb_use_status'][rb]['d2d'].remove(d2d)
    
    #更新每個D2D使用的RB和Vt
    for rb in range(parameter['numRB']):
        for d2d in parameter['rb_use_status'][rb]['d2d']:
            sinr = cal_d2d_sinr(d2d, rb, **parameter)
            d_vt = convert_sinr_vt(sinr)
            parameter['throughput_d2d'][d2d][rb] = d_vt
            parameter['assignmentD2D'][d2d][rb] == 1

    #紀錄每個D2D的總throughput
    for d2d in range(parameter['numD2D']):
        total = np.sum(parameter['throughput_d2d'][d2d])
        if total > parameter['data_d2d'][d2d]:
            parameter['d2d_total_throughput'][d2d] = parameter['data_d2d'][d2d]
        else:
            parameter['d2d_total_throughput'][d2d] = total

    t = 0
    for d2d in range(parameter['numD2D']):
        s = np.zeros(parameter['numRB'])
        numRB = int(np.sum(parameter['assignmentD2D'][d2d]))
        for rb in range(parameter['numRB']):
            s[rb] = cal_d2d_sinr(d2d, rb, **parameter)
        sinr = np.min(s)
        sinr = convert.mW_to_dB(sinr)
        th = tool.sinr_throughput_mapping(sinr, numRB)
        t = t + th

    assignList = []
    for rb in range(parameter['numRB']):
        for d2d in parameter['rb_use_status'][rb]['d2d']:
            if d2d not in assignList:
                assignList.append(d2d)
    parameter['numAssignment'] = parameter['numAssignment'] + len(assignList)
    # print(parameter['powerD2DList'])

    print(parameter['rb_use_status'])
    # t = np.sum(parameter['throughput_rb'])
    print('total th',t)
    print(parameter['throughput_rb'])
    # print(parameter['i_d2c'])
    # print('rb weight',parameter['edge_rb'])
    # print(parameter['rb_use_status'])
    # print()
    return parameter

def cal_d2d_sinr(tx, rb, **parameter):
    rx_sinr = np.zeros((parameter['numD2DReciver'][tx]))
    for rx in range(parameter['numD2DReciver'][tx]):
        interference = cal_d2d_interference(tx, rx, rb, **parameter)
        rx_sinr[rx] = (parameter['powerD2DList'][tx][rb] * parameter['g_d2d'][tx][rx][rb]) / (parameter['N0'] + interference)
    return np.min(rx_sinr)

def cal_d2d_interference(tx, rx, rb, **parameter):
    interference = 0
    for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
        if i in parameter['rb_use_status'][rb]['d2d']:
            interference = interference + parameter['powerD2DList'][i][rb] * parameter['g_dij'][i][tx][rx][0]
    for i in parameter['i_d2d_rx'][tx][rx]['cue']:
        if i in parameter['rb_use_status'][rb]['cue']:
            interference = interference + parameter['powerCUEList'][i] * parameter['g_c2d'][i][tx][rx][0]
    return interference

def cal_cue_sinr(tx, rb, **parameter):
    sinr = 0
    for rx in range(parameter['numCellRx']):
        if parameter['assignmentRxCell'][rx][rb] == 1:
            interference = cal_cue_interference(tx, rx, rb, **parameter)
            sinr = (parameter['powerCUEList'][tx] * parameter['g_c2b'][tx][rx][rb]) / (parameter['N0'] + interference)
    return sinr

def cal_cue_interference(tx, rx, rb, **parameter):
    interference = 0
    for i in parameter['i_d2c'][rx]:
        if i in parameter['rb_use_status'][rb]['d2d']:
            interference = interference + (parameter['powerD2DList'][i][rb] * parameter['g_d2c'][i][rx][0])
    return interference

def cal_d2d_edge_weight(u, v, rb, **parameter):
    uv_weight_list = np.zeros((parameter['numD2DReciver'][v]))
    vu_weight_list = np.zeros((parameter['numD2DReciver'][u]))

    #表示 u 會干擾 v
    if u in parameter['i_d2d'][v]['d2d']:
        for v_rx in range(parameter['numD2DReciver'][v]):
            if u in parameter['i_d2d_rx'][v][v_rx]['d2d']:
                uv_weight_list[v_rx] = parameter['powerD2DList'][u][rb] * parameter['g_dij'][u][v][v_rx][rb]
    
    #表示 v 會干擾 u
    if v in parameter['i_d2d'][u]['d2d']:
        for u_rx in range(parameter['numD2DReciver'][u]):
            if v in parameter['i_d2d_rx'][u][u_rx]['d2d']:
                vu_weight_list[u_rx] = parameter['powerD2DList'][v][rb] * parameter['g_dij'][v][u][u_rx][rb]
    weight = np.max(uv_weight_list) + np.max(vu_weight_list)
    return weight

def cal_cue_edge_weight(u, v, rb, **parameter):
    #u是cue
    if parameter['numCellRx'] == 1:
        rx = 0
    else:
        rx = u

    uv_weight_list = np.zeros((parameter['numD2DReciver'][v]))
    vu_weight_list = np.zeros((1))

    #表示 u 會干擾 v
    if u in parameter['i_d2d'][v]['cue']:
        for v_rx in range(parameter['numD2DReciver'][v]):
            if u in parameter['i_d2d_rx'][v][v_rx]['cue']:
                uv_weight_list[v_rx] = parameter['powerCUEList'][u] * parameter['g_c2d'][u][v][v_rx][rb]
    
    #表示 v 會干擾 u
    if v in parameter['i_d2c'][rx]:
        vu_weight_list[rx] = parameter['powerD2DList'][v][rb] * parameter['g_d2c'][v][rx][rb]
    weight = np.max(uv_weight_list) + np.max(vu_weight_list)
    return weight

def cal_Vt_d2d(rb, **parameter):
    tool = tools.Tool()
    convert = tools.Convert()
    throughput = 0
    for i in parameter['rb_use_status'][rb]['d2d']:
        sinr = cal_d2d_sinr(i, rb, **parameter)
        print('d2d sinr',sinr)
        t = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr), 1)
        throughput = throughput + t
    return throughput

def cal_Vt_cue(rb, **parameter):
    tool = tools.Tool()
    convert = tools.Convert()
    throughput = 0
    for cue in range(parameter['numCellTx']):
        for rx in range(parameter['numCellRx']):
            c_tx = 0
            c_rx = 0
            if parameter['numCellRx'] == 1:
                c_tx = cue
            else:
                c_rx = cue
            if parameter['assignmentTxCell'][cue][rb] == 1:
                if cue not in parameter['rb_use_status'][rb]['cue']:
                    parameter['rb_use_status'][rb]['cue'].append(cue)
                sinr = cal_cue_sinr(cue, rb, **parameter)
                print('cue',rx, 'sinr',sinr)
                print('cue min sinr',parameter['minCUEsinr'][c_rx])
                throughput = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr), 1)
    return throughput

def convert_sinr_vt(sinr):
    tool = tools.Tool()
    convert = tools.Convert()
    throughput = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr), 1)
    return throughput