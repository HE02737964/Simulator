import numpy as np
import tools

def initial_parameter(**parameter):
    parameter.update({'powerD2DList' : np.zeros(parameter['numD2D'])})
    parameter = cal_num_interfered_neighbor(**parameter)
    parameter = cal_priority(**parameter)
    parameter = create_no_cell_interference_graph(**parameter) #建沒有與Cell UE關聯的干擾圖
    parameter.update({'longestPath_type' : "priority"})
    return parameter

def phase1(**parameter):
    for root in parameter['priority_sort_index']:
        print(root)
        #root不能被assign而且最大power能滿足SINR值(不在nStartD2D裡面)
        if parameter['powerD2DList'][root] == 0 and root not in parameter['nStartD2D']:
            longestPath = find_longest_path(root, **parameter)
            
            if longestPath:
                parameter['powerD2DList'][longestPath[-1]] = 1
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
    print(not_visit_point)
    vis = [False] * len(parameter['d2d_no_cell_interference_graph'])
    if not vis[root]:
        path = []
        longestPath = dfs(root, parameter['d2d_no_cell_interference_graph'], not_visit_point, vis, path, longestPath)
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