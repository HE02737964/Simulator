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
    parameter.update({'throughput' : 0})
    parameter.update({'powerD2D' : powerD2DList})
    parameter.update({'throughput' : 0})
    parameter.update({'delta' : delta})
    return parameter

def vertex_coloring(**parameter):
    tool = tools.Tool()
    parameter = initial_parameter(**parameter)
    #先更新每個RB裏頭CUE的throughput
    for rb in range(parameter['numRB']):
        cue_throughput = cal_Vt_cue(rb, **parameter)
        parameter['throughput_rb'][rb] = cue_throughput
        parameter['throughput_cue'][rb] = cue_throughput
    
    iterations = 1
    for i in range(iterations):
        for rb in range(parameter['numRB']):
            # print('rb',rb)
            subscript = []
            for d2d in range(parameter['numD2D']):
                if d2d not in parameter['rb_use_status'][rb]['d2d']:
                    # if parameter['rb_use_status'][rb]['cue'] not in parameter['t_d2c'][d2d]:
                    #     print('d2d',d2d,parameter['t_d2c'][d2d],parameter['rb_use_status'][rb]['cue'])
                    subscript.append(d2d)
            # print('subscript',subscript)
            while subscript:
                #選擇一個未著色的頂點
                vertex = subscript[0]
                # print('vertex',vertex)

                #記錄當前Vt, Vi
                current_Vt = parameter['throughput_rb'][rb]
                current_Vc = cue_throughput
                current_Vi = parameter['edge_rb'][rb]
                current_vertex_list = parameter['rb_use_status'][rb]['d2d'].copy()
                # print('current Vt', current_Vt)

                #將vertex放入Sk裡
                parameter['rb_use_status'][rb]['d2d'].append(vertex)

                #更新Vt
                cue_Vt = cal_Vt_cue(rb, **parameter)
                d2d_Vt = cal_Vt_d2d(rb, **parameter)
                new_Vt = cue_Vt + d2d_Vt
                new_vertex_list = parameter['rb_use_status'][rb]['d2d'].copy()
                # print('new Vt',new_Vt)
                
                #將vertex從Sk中移除
                parameter['rb_use_status'][rb]['d2d'].remove(vertex)

                #挑選最大Vt的那組vertex組合
                totalVi = 0
                if current_Vt < new_Vt:
                    parameter['rb_use_status'][rb]['d2d'] = new_vertex_list
                    parameter['throughput_rb'][rb] = new_Vt
                    parameter['throughput_cue'][rb] = cue_Vt
                    subscript.remove(vertex)
                    # print('put vertex in rb')
                else:
                    parameter['rb_use_status'][rb]['d2d'] = current_vertex_list
                    parameter['throughput_rb'][rb] = current_Vt
                    parameter['throughput_cue'][rb] = current_Vc
                    subscript.remove(vertex)
                    # print('vertex can not throughput rasing')
                
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
                # print('update Vi',totalVi)

        #每個RB的Vi總和
        s = np.sum(parameter['edge_rb'])

        #計算每個RB上的功率分配因子(delta)
        for rb in range(parameter['numRB']):
            if s*parameter['edge_rb'][rb] == 0:
                parameter['delta'][rb] = 0
            else:
                parameter['delta'][rb] = (1 / s*parameter['edge_rb'][rb])
            # print('calculate rb',rb,'power factor',parameter['delta'][rb])
            #計算每個D2D在每個RB上的傳輸功率
            for d2d in range(parameter['numD2D']):
                if d2d in parameter['rb_use_status'][rb]['d2d']:
                    power = parameter['delta'][rb] * parameter['Pmax']
                    if power > parameter['Pmax']:
                        power = parameter['Pmax']
                    if power < parameter['Pmin']:
                        power = parameter['Pmin']
                    parameter['powerD2D'][d2d][rb] = power
                else:
                    parameter['powerD2D'][d2d][rb] = 0
                # print('set d2d',d2d,'power',parameter['powerD2D'][d2d][rb],'in rb',rb)
    # print('check some value start',time.ctime(time.time()))
    parameter = check_some_value(**parameter)
    # print('check some value end',time.ctime(time.time()))
    parameter = tool.power_collect(**parameter)
    return parameter

def remove_d2d_interference(**parameter):
    convert = tools.Convert()
    for rb in range(parameter['numRB']):
        #扣除掉CUE的throughput
        parameter['throughput_rb'][rb] = parameter['throughput_rb'][rb] - parameter['throughput_cue'][rb]
        #移除會使CUE的sinr小於所需值的d2d
        cue_list = parameter['rb_use_status'][rb]['cue'] #有使用rb的cue list
        if cue_list:
            cue = cue_list[0] #一個RB只會有1個CUE使用,所以取第一個
            for d2d in parameter['i_d2c']:
                cue_sinr = cal_cue_sinr(cue, rb, **parameter)
                if convert.mW_to_dB(parameter['minCUEsinr'][cue]) < convert.mW_to_dB(cue_sinr) and d2d in parameter['rb_use_status'][rb]['d2d']:
                    #將d2d從rb_use_status中移除並設置該rb上的power為0
                    parameter['rb_use_status'][rb]['d2d'].remove(d2d)
                    parameter['powerD2D'][d2d][rb] = 0
                    #扣除掉d2d在該rb上的throughput
                    d2d_sinr = cal_d2d_sinr(d2d, rb, **parameter)
                    d_vt = convert_sinr_vt(d2d_sinr)
                    parameter['throughput_rb'][rb] = parameter['throughput_rb'][rb] - d_vt
    return parameter

def remove_d2d_less_than_min_sinr(**parameter):
    convert = tools.Convert()
    #移除rb上不滿足所需sinr的d2d
    if parameter['check_value'] == True:
        for rb in range(parameter['numRB']):
            index = len(parameter['rb_use_status'][rb]['d2d']) - 1
            point = 0
            while point <= index:
                d2d = parameter['rb_use_status'][rb]['d2d'][point]
                d2d_sinr = cal_d2d_sinr(d2d, rb, **parameter)
                d_vt = convert_sinr_vt(d2d_sinr)
                if convert.mW_to_dB(parameter['minD2Dsinr'][d2d]) > convert.mW_to_dB(d2d_sinr):
                    parameter['rb_use_status'][rb]['d2d'].remove(d2d)
                    parameter['powerD2D'][d2d][rb] = 0
                    #扣除掉d2d在該rb上的throughput
                    parameter['throughput_rb'][rb] = parameter['throughput_rb'][rb] - d_vt
                    index = len(parameter['rb_use_status'][rb]['d2d']) - 1
                    point = 0
                else:
                    point = point + 1
    return parameter

def check_some_value(**parameter):
    tool = tools.Tool()
    convert = tools.Convert()

    parameter = remove_d2d_interference(**parameter)
    parameter = remove_d2d_less_than_min_sinr(**parameter)

    #更新每個D2D使用的RB和Vt
    parameter['throughput_d2d'] = np.zeros_like(parameter['throughput_d2d'])
    # print('set d2d throughput zero',parameter['throughput_d2d'])
    # print('set assignemnt d2d zero',parameter['assignmentD2D'])
    for rb in range(parameter['numRB']):
        for d2d in parameter['rb_use_status'][rb]['d2d']:
            sinr = cal_d2d_sinr(d2d, rb, **parameter)
            d_vt = convert_sinr_vt(sinr)
            parameter['throughput_d2d'][d2d][rb] = d_vt
            parameter['assignmentD2D'][d2d][rb] = 1
    # print('update Vt rb status', parameter['rb_use_status'])

    #紀錄每個D2D的總throughput
    for d2d in range(parameter['numD2D']):
        total = np.sum(parameter['throughput_d2d'][d2d])
        if total >= parameter['data_d2d'][d2d]:
            parameter['d2d_total_throughput'][d2d] = parameter['data_d2d'][d2d]
        else:
            parameter['d2d_total_throughput'][d2d] = total
    # print('d2d in each rb throughput',parameter['d2d_total_throughput'])

    #修正d2d的throughput
    for d2d in range(parameter['numD2D']):
        sinr_list = np.zeros(parameter['numRB'])
        numRB = int(np.sum(parameter['assignmentD2D'][d2d]))
        # print('d2d',d2d,'total use rb',np.sum(parameter['assignmentD2D'][d2d]))
        if numRB == 0:
            # print('d2d',d2d,'use rb',numRB)
            d2d_throughput = 0
            parameter['powerD2D'][d2d] = 0
            for rb in range(parameter['numRB']):
                if d2d in parameter['rb_use_status'][rb]['d2d']:
                    parameter['rb_use_status'][rb]['d2d'].remove(d2d)
            continue

        for rb in range(parameter['numRB']):
            sinr_list[rb] = cal_d2d_sinr(d2d, rb, **parameter)
        sinr_nonzeroList = sinr_list[np.nonzero(sinr_list)]
        sinr = np.min(sinr_nonzeroList)
        sinr = convert.mW_to_dB(sinr)
        d2d_throughput = tool.sinr_throughput_mapping(sinr, numRB)
        if d2d_throughput >= parameter['data_d2d'][d2d]:
            d2d_throughput = parameter['data_d2d'][d2d]
        else:
            if parameter['check_value'] == True:
                d2d_throughput = 0
                parameter['powerD2D'][d2d] = 0
                for rb in range(parameter['numRB']):
                    if d2d in parameter['rb_use_status'][rb]['d2d']:
                        parameter['rb_use_status'][rb]['d2d'].remove(d2d)
        parameter['d2d_total_throughput'][d2d] = d2d_throughput
    # print('d2d update throughput',parameter['d2d_total_throughput'])
    
    assignList = []
    for rb in range(parameter['numRB']):
        for d2d in parameter['rb_use_status'][rb]['d2d']:
            if d2d not in assignList:
                assignList.append(d2d)
    parameter['numAssignment'] = parameter['numAssignment'] + len(assignList)
    for d2d in range(parameter['numD2D']):
        parameter['data_d2d'][d2d] = parameter['d2d_total_throughput'][d2d]
    parameter['throughput'] = np.sum(parameter['d2d_total_throughput'])
    # print('d2d assign list',assignList)
    # print('rb use status',parameter['rb_use_status'])
    pwr = np.zeros(parameter['numD2D'])
    for d2d in range(parameter['numD2D']):
        pwr[d2d] = np.max(parameter['powerD2D'][d2d])
    parameter.update({'powerD2DList' : pwr})
    # print('gcrs d2d power',pwr)
    return parameter

def cal_d2d_sinr(tx, rb, **parameter):
    rx_sinr = np.zeros((parameter['numD2DReciver'][tx]))
    for rx in range(parameter['numD2DReciver'][tx]):
        interference = cal_d2d_interference(tx, rx, rb, **parameter)
        rx_sinr[rx] = (parameter['powerD2D'][tx][rb] * parameter['g_d2d'][tx][rx][rb]) / (parameter['N0'] + interference)
    return np.min(rx_sinr)

def cal_d2d_interference(tx, rx, rb, **parameter):
    interference = 0
    for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
        if i in parameter['rb_use_status'][rb]['d2d']:
            interference = interference + parameter['powerD2D'][i][rb] * parameter['g_dij'][i][tx][rx][0]
    for i in parameter['i_d2d_rx'][tx][rx]['cue']:
        if i in parameter['rb_use_status'][rb]['cue']:
            interference = interference + parameter['powerCUEList'][i] * parameter['g_c2d'][i][tx][rx][0]
    return interference

def cal_cue_sinr(cue, rb, **parameter):
    sinr = 0
    for rx in range(parameter['numCellRx']):
        if parameter['numCellRx'] == 1:
            tx = cue
            rx = 0
        else:
            tx = 0
            rx = cue

        if parameter['assignmentRxCell'][rx][rb] == 1:
            interference = cal_cue_interference(tx, rx, rb, **parameter)
            sinr = (parameter['powerCUEList'][tx] * parameter['g_c2b'][tx][rx][rb]) / (parameter['N0'] + interference)
    return sinr

def cal_cue_interference(tx, rx, rb, **parameter):
    interference = 0
    for i in parameter['i_d2c'][rx]:
        if i in parameter['rb_use_status'][rb]['d2d']:
            interference = interference + (parameter['powerD2D'][i][rb] * parameter['g_d2c'][i][rx][0])
    return interference

def cal_d2d_edge_weight(u, v, rb, **parameter):
    uv_weight_list = np.zeros((parameter['numD2DReciver'][v]))
    vu_weight_list = np.zeros((parameter['numD2DReciver'][u]))

    #表示 u 會干擾 v
    if u in parameter['i_d2d'][v]['d2d']:
        for v_rx in range(parameter['numD2DReciver'][v]):
            if u in parameter['i_d2d_rx'][v][v_rx]['d2d']:
                uv_weight_list[v_rx] = parameter['powerD2D'][u][rb] * parameter['g_dij'][u][v][v_rx][rb]
    
    #表示 v 會干擾 u
    if v in parameter['i_d2d'][u]['d2d']:
        for u_rx in range(parameter['numD2DReciver'][u]):
            if v in parameter['i_d2d_rx'][u][u_rx]['d2d']:
                vu_weight_list[u_rx] = parameter['powerD2D'][v][rb] * parameter['g_dij'][v][u][u_rx][rb]
    weight = np.max(uv_weight_list) + np.max(vu_weight_list)
    return weight

def cal_cue_edge_weight(u, v, rb, **parameter):
    #u是cue
    if parameter['numCellRx'] == 1:
        tx = u
        rx = 0
    else:
        tx = 0
        rx = u

    uv_weight_list = np.zeros((parameter['numD2DReciver'][v]))
    vu_weight_list = np.zeros((1))

    #表示 u 會干擾 v
    if tx in parameter['i_d2d'][v]['cue']:
        for v_rx in range(parameter['numD2DReciver'][v]):
            if tx in parameter['i_d2d_rx'][v][v_rx]['cue']:
                uv_weight_list[v_rx] = parameter['powerCUEList'][tx] * parameter['g_c2d'][tx][v][v_rx][rb]
    
    #表示 v 會干擾 u
    if v in parameter['i_d2c'][rx]:
        vu_weight_list[0] = parameter['powerD2D'][v][rb] * parameter['g_d2c'][v][rx][rb]
    weight = np.max(uv_weight_list) + np.max(vu_weight_list)
    return weight

def cal_Vt_d2d(rb, **parameter):
    tool = tools.Tool()
    convert = tools.Convert()
    throughput = 0
    for i in parameter['rb_use_status'][rb]['d2d']:
        sinr = cal_d2d_sinr(i, rb, **parameter)
        # print('d2d sinr',sinr)
        t = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr), 1)
        throughput = throughput + t
    return throughput

def cal_Vt_cue(rb, **parameter):
    tool = tools.Tool()
    convert = tools.Convert()
    throughput = 0
    for cue in range(parameter['numCellTx']):
        for rx in range(parameter['numCellRx']):
            if parameter['numCellRx'] == 1:
                if parameter['assignmentTxCell'][cue][rb] == 1:
                    if cue not in parameter['rb_use_status'][rb]['cue']:
                        parameter['rb_use_status'][rb]['cue'].append(cue)
                    sinr = cal_cue_sinr(cue, rb, **parameter)
                    # print('cue',cue, 'sinr',sinr)
                    # print('cue min sinr',parameter['minCUEsinr'][cue])
                    # throughput = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr), 1)
                    throughput = parameter['data_cue'][cue]
            else:
                if parameter['assignmentTxCell'][cue][rb] == 1:
                    if cue not in parameter['rb_use_status'][rb]['cue']:
                        parameter['rb_use_status'][cue]['cue'].append(cue)
                    sinr = cal_cue_sinr(cue, rb, **parameter)
                    # print('cue',rx, 'sinr',sinr)
                    # print('cue min sinr',parameter['minCUEsinr'][rx])
                    # throughput = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr), 1)
                    throughput = parameter['data_cue'][rx]
    return throughput

def convert_sinr_vt(sinr):
    tool = tools.Tool()
    convert = tools.Convert()
    throughput = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr), 1)
    return throughput
