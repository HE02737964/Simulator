import numpy as np
import tools

def initial_parameter(**parameter):
    parameter.update({'powerD2DList' : np.zeros(parameter['numD2D'])})
    parameter.update({'nStartD2D' : np.asarray([])})
    parameter = cal_num_interfered_neighbor(**parameter)
    parameter = cal_priority(**parameter)
    parameter = create_no_cell_interference_graph(**parameter) #建沒有與Cell UE關聯的干擾圖
    parameter.update({'longestPath_type' : "priority"})
    assignmentD2D = np.zeros((parameter['numD2D'], parameter['numRB']))
    parameter.update({'assignmentD2D' : assignmentD2D})
    d2d_use_rb_List = np.zeros((parameter['numD2D'], parameter['numRB']), dtype=int)
    parameter.update({'d2d_use_rb_List' : d2d_use_rb_List})
    return parameter

def phase1(**parameter):
    tool = tools.Tool()
    #找出d2d所有可用的RB以及所需sinr
    for d2d in range(parameter['numD2D']):
        parameter = get_d2d_use_rb(d2d, **parameter)
        numUseRB = np.sum(parameter['d2d_use_rb_List'][d2d])
        parameter['minD2Dsinr'][d2d] = tool.data_sinr_mapping(parameter['data_d2d'][d2d], numUseRB)
        d2dSinr = np.zeros((parameter['numD2DReciver'][d2d], parameter['numRB']))
        #利用Pmax計算d2d rx的snr
        for rx in range(parameter['numD2DReciver'][d2d]):
            for rb in range(parameter['numRB']):
                d2dSinr[rx][rb] = parameter['d2d_use_rb_List'][d2d][rb] * ((parameter['Pmax'] * parameter['g_d2d'][d2d][rx][rb]) / parameter['N0'])
        minSinr = np.min(d2dSinr[np.nonzero(d2dSinr)])
        #將snr不滿足的d2d放入無法啟動的list中
        if minSinr < parameter['minD2Dsinr'][d2d] or parameter['minD2Dsinr'][d2d] == 0:
            parameter['nStartD2D'] = np.append(parameter['nStartD2D'],d2d)

    candicate = np.copy(parameter['priority_sort_index'])
    # while candicate.size > 0:
    root = candicate[0]
    print('root',root)
    #root如果被assign或最大power不能滿足SINR值(在nStartD2D裡面)
    if parameter['powerD2DList'][root] != 0 or root in parameter['nStartD2D']:
        candicate = np.delete(candicate, 0)
        # continue
    else:
        longestPath = find_longest_path(root, **parameter)
    print('longestPath', longestPath)
    index = len(longestPath) - 1
    print('index', index)
    while index >= 0:
        print('index', index)
        node = longestPath[index]
        print('node', node)
        length = len(longestPath) - 1
        print('length', length)
        p3, p2 = cal_need_power(node, **parameter)
        p1 = cal_min_interference_power(node, **parameter)
        p = min(p1, p2)
        print('p3',p3)
        print('p2',p2)
        print('p1',p1)
        print('p ',p )
        
        #node沒有干擾其他d2d
        if p3 < p or p < 0:
            parameter['assignmentD2D'][d2d] = np.copy(parameter['d2d_use_rb_List'][d2d])
            parameter['powerD2DList'][node] = p2
            index = index - 1
            print('index - 1')
        else:
            iterations = (length - index) + 1
            print('iterations', iterations)
            for i in range(iterations):
                print('i', i)
                d2d = longestPath[-1]
                parameter['assignmentD2D'][d2d] = 0
                parameter['powerD2DList'][d2d] = 0
                longestPath.pop()
            index = len(longestPath) - 1
            print('longestpath pop')
            print(longestPath)
        
        # for d2d in range(parameter['numD2D']):
        #     if parameter['powerD2DList'][d2d] != 0:
        #         deleteD2D = np.where(d2d == candicate)[0]
        #         candicate = np.delete(candicate, deleteD2D)

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
    priority = np.asarray([1,5,2,3,4])
    sort_priority = (-priority).argsort()
    parameter.update({'priority' : priority})
    parameter.update({'priority_sort_index' : sort_priority})
    return parameter

#建立沒有與Cell UE有干擾關係的干擾圖
def create_no_cell_interference_graph(**parameter):
    graph = [[] for i in range(parameter['numD2D'])]
    for d2d in range(parameter['numD2D']):
        for i in parameter['i_d2d'][d2d]['d2d']:
            graph[d2d].append(i)
        graph[d2d] = sorted(graph[d2d], key = lambda k : parameter['priority'][k], reverse=True)
    parameter.update({'d2d_no_cell_interference_graph' : graph})
    return parameter

#D2D依據和Cell UE的干擾關係分群
def d2d_interference_cell(**parameter):
    noCell = []     #D2D與Cell UE沒有干擾
    inCell = []     #D2D與Cell UE有干擾
    #CUE沒有干擾D2D且D2D沒有干擾BS
    for d2d in range(parameter['numD2D']):
        flag = True
        if not parameter['i_d2d'][d2d]['cue']:
            for cell in range(parameter['numCellRx']):
                if d2d in parameter['i_d2c'][cell]:
                    flag = False
            if flag:
                noCell.append(d2d)
    inCell = np.setdiff1d(np.arange(parameter['numD2D']), np.asarray(noCell))
    parameter.update({'d2d_noCellInterference' : noCell})
    parameter.update({'d2d_cellInterference' : inCell})
    return parameter

#找D2D的最長路徑
def find_longest_path(root, **parameter):
    longestPath = []
    power_assign_list = np.where(parameter['powerD2DList'] != 0)[0]
    not_visit_point = np.concatenate((power_assign_list, parameter['nStartD2D']))
    vis = [False] * len(parameter['d2d_no_cell_interference_graph'])
    if not vis[root]:
        path = []
        longestPath = dfs(root, parameter['d2d_no_cell_interference_graph'], not_visit_point, vis, path, longestPath)

    if parameter['longestPath_type'] == "priority":
        return longestPath[0]

#DFS算法
def dfs(node, graph, not_visit_point, vis, path, longestPath):
    vis[node] = True
    if node in not_visit_point:
        return []
    else:
        path.append(node)
        for i in graph[node]:
            if not vis[i]:
                dfs(i, graph, not_visit_point, vis, path, longestPath)
        p = path.copy()
        longestPath.append(p)
        path.pop()
        vis[node] = False

    return longestPath

#得到d2d能使用的rb
def get_d2d_use_rb(d2d, **parameter):
    d2dUseRBList = np.ones(25, dtype=int)
    cueUseRBList = np.zeros(25, dtype=int)
    for cue in range(parameter['numCellRx']):
        if d2d in parameter['i_d2c'][cue]:
            #CUE有使用的RB做or運算，找出所有rx cue會被d2d干擾的RB
            cueUseRBList = np.logical_or(cueUseRBList, parameter['assignmentRxCell'][cue])
    d2dUseRBList = d2dUseRBList - cueUseRBList
    parameter['d2d_use_rb_List'][d2d] = d2dUseRBList
    return parameter

#計算滿足所需sinr需要的傳輸功率(p2和p3)
def cal_need_power(d2d, **parameter):
    p3_need_power = np.zeros((parameter['numD2DReciver'][d2d], parameter['numRB']))
    p2_need_power = np.zeros((parameter['numD2DReciver'][d2d], parameter['numRB']))
    virtual_interference = 0
    #方便計算干擾用，先假設d2d已被分配它能使用的rb
    parameter['assignmentD2D'][d2d] = np.copy(parameter['d2d_use_rb_List'][d2d])
    for rx in range(parameter['numD2DReciver'][d2d]):
        for rb in range(parameter['numRB']):
            interference = cal_d2d_interference(d2d, rx, rb, **parameter)            
            # 虛擬干擾的計算方式virtual_interference = 
            p3_need_power[rx][rb] = (parameter['minD2Dsinr'][d2d] * (parameter['N0'] + interference)) / parameter['g_d2d'][d2d][rx][rb]
            p2_need_power[rx][rb] = (parameter['minD2Dsinr'][d2d] * (parameter['N0'] + interference + virtual_interference)) / parameter['g_d2d'][d2d][rx][rb]
    p3 = np.max(p3_need_power)
    p2 = np.max(p2_need_power)
    parameter['assignmentD2D'][d2d] = 0
    return p3, p2

#計算能對其他裝置造成的最小干擾功率(p1)
def cal_min_interference_power(d2d, **parameter):
    #d2d沒有干擾任何裝置
    if not parameter['t_d2d'][d2d] and not parameter['t_d2c'][d2d]:
        return -1

    #被干擾的裝置分為2種case討論，一種是d2d另一種是cue
    Pmin = parameter['Pmax'] + 1
    #方便計算干擾用，先假設d2d已被分配它能使用的rb
    parameter['assignmentD2D'][d2d] = np.copy(parameter['d2d_use_rb_List'][d2d])
    for tx in parameter['t_d2d'][d2d]:
        if parameter['powerD2DList'][tx] == 0:
            continue
        for rx in range(parameter['numD2DReciver'][tx]):
            if d2d in parameter['i_d2d_rx'][tx][rx]:
                d2d_min_power = np.zeros(parameter['numRB'])
                for rb in range(parameter['numRB']):
                    if parameter['assignmentD2D'][d2d] == 1:
                        interference = cal_d2d_interference(tx, rx, rb, **parameter)
                        d2d_min_power[rb] = ((parameter['powerD2DList'][tx] * parameter['g_d2d'][tx][rx][rb]) / (parameter['minD2Dsinr'][tx] * parameter['g_dij'][d2d][tx][rx][rb])) - ((parameter['N0'] + interference) / parameter['g_dij'][d2d][tx][rx][rb])
                d2d_nonzero_min_power = d2d_min_power[np.nonzero(d2d_min_power)]
                if d2d_nonzero_min_power.size > 0 and np.min(d2d_min_power) < Pmin:
                    Pmin = np.min(d2d_min_power)
    
    for cue in parameter['t_d2c'][d2d]:
        d2d_min_power = np.zeros(parameter['numRB'])
        for rb in range(parameter['numRB']):
            interference = cal_cue_interference(cue, rb, **parameter)
            # uplink
            if parameter['numCellRx'] == 1:
                d2d_min_power[rb] = ((parameter['powerCUEList'][cue] * parameter['g_c2b'][cue][0][rb]) / (parameter['minCUEsinr'][cue] * parameter['g_d2c'][d2d][0][rb])) - ((parameter['N0'] + interference) / parameter['g_c2b'][cue][0][rb])
            # downlink
            else:
                d2d_min_power[rb] = ((parameter['powerCUEList'][cue] * parameter['g_c2b'][0][cue][rb]) / (parameter['minCUEsinr'][cue] * parameter['g_d2c'][d2d][cue][rb])) - ((parameter['N0'] + interference) / parameter['g_c2b'][0][cue][rb])
            d2d_nonzero_min_power = d2d_min_power[np.nonzero(d2d_min_power)]
            if d2d_nonzero_min_power.size > 0 and np.min(d2d_min_power) < Pmin:
                Pmin = np.min(d2d_min_power)
    parameter['assignmentD2D'][d2d] = 0

    if Pmin < parameter['Pmax']:
        return Pmin
    else:
        return -2

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