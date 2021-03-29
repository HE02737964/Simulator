import numpy as np
import tools

def initial_parameter(**parameter):
    parameter.update({'powerD2DList' : np.zeros(parameter['numD2D'])})
    parameter.update({'nStartD2D' : np.asarray([])})
    parameter = cal_num_interfered_neighbor(**parameter)
    parameter = cal_priority(**parameter)
    parameter = create_no_cell_interference_graph(**parameter) #建沒有與Cell UE關聯的干擾圖
    parameter.update({'longestPath_type' : "priority"})
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
        print(parameter['d2d_use_rb_List'][d2d])
        #將sinr不滿足的d2d放入無法啟動的list中
        for rx in range(parameter['numD2DReciver'][d2d]):
            for rb in range(parameter['numRB']):
                d2dSinr[rx][rb] = parameter['d2d_use_rb_List'][d2d][rb] * ((parameter['Pmax'] * parameter['g_d2d'][d2d][rx][rb]) / parameter['N0'])
                print(d2dSinr[rx][rb])
        minSinr = np.min(d2dSinr[np.nonzero(d2dSinr)])
        if minSinr < parameter['minD2Dsinr'][d2d] or parameter['minD2Dsinr'][d2d] == 0 or d2d not in parameter['nStartD2D']:
            parameter['nStartD2D'] = np.append(parameter['nStartD2D'],d2d)

    for root in parameter['priority_sort_index']:
        # print(root)
        #root不能被assign而且最大power能滿足SINR值(不在nStartD2D裡面)
        if parameter['powerD2DList'][root] == 0 and root not in parameter['nStartD2D']:
            longestPath = find_longest_path(root, **parameter)
            
            # if parameter['powerD2DList'][3] == 0:
            #     parameter['powerD2DList'][3] = 1
        # print(parameter['powerD2DList'])
        # print(longestPath)
        # print()
    
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
    #所有的path做排序
    # longestPath = sorted(longestPath, key = len, reverse=True)
    print(longestPath)
    if parameter['longestPath_type'] == "priority":
        return longestPath[0]

#DFS算法
def dfs(node, graph, not_visit_point, vis, path, longestPath):
    vis[node] = True
    if node in not_visit_point:
        p = path.copy()
        longestPath.append(p)
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

# def cal_p3(d2d, **parameter):
#     tx_power_rx = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
#     for rx in range(parameter['numD2DReciver'][tx]):
#         for rb in range(parameter['numRB']):
#             interference = 0
#             for i in parameter['i_d2d_rx'][tx][rx]['cue']:
#                 #tx的cue干擾鄰居有使用該RB的話才有干擾
#                 if parameter['assignmentTxCell'][i][rb] == 1:
#                     interference = interference + (parameter['powerCUEList'][i] * parameter['g_c2d'][i][tx][rx][rb])
#             for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
#                 #tx的d2d干擾鄰居有使用該RB的話才有干擾
#                 if parameter['assignmentD2D'][i][rb] == 1:
#                     interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
#             tx_power_rx[rx][rb] = (parameter['minD2Dsinr'][tx] * (parameter['N0'] + interference)) / parameter['g_d2d'][tx][rx][rb]
#     tx_min_power = np.max(tx_power_rx)
#     return tx_min_power

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