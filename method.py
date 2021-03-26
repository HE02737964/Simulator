import numpy as np
import tools

def initial_parameter(**parameter):
    parameter.update({'powerD2DList' : np.zeros(parameter['numD2D'])})
    return parameter

def phase1(**parameter):
    parameter = find_num_interfered_neighbor(**parameter)
    parameter = sort_d2d(**parameter)
    parameter = create_no_cell_interference_graph(**parameter) #建沒有與Cell UE關聯的干擾圖
    find_longest_path(**parameter)
    
    return parameter

def find_num_interfered_neighbor(**parameter):
    i_len = np.zeros(parameter['numD2D'])
    #干擾鄰居的數量
    for tx in range(parameter['numD2D']):
        i_len[tx] = len(parameter['i_d2d'][tx]['cue']) + len(parameter['i_d2d'][tx]['d2d']) + 1

    parameter.update({'num_interference' : i_len})
    return parameter

def sort_d2d(**parameter):
    priority = (parameter['data_d2d'] / parameter['num_interference']) * (1 / parameter['scheduleTimes'])
    sort_priority = (-priority).argsort() #priority由大至小排序(排序結果為index)
    sort_priority = np.array([0,4,3,1,2])
    parameter.update({'priority' : sort_priority})
    return parameter

def create_no_cell_interference_graph(**parameter):
    graph = [[] for i in range(parameter['numD2D'])]
    print('priority',parameter['priority'])
    for d2d in range(parameter['numD2D']):
        for i in parameter['i_d2d'][d2d]['d2d']:
            graph[d2d].append(i)
        print(graph[d2d])
        np.array(graph[d2d])[parameter['priority']]
    parameter.update({'d2d_no_cell_interference_graph' : graph})
    print('graph',graph)
    return parameter

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

def find_longest_path(**parameter):
    longestPathList = []
    power_assign_list = np.where(parameter['powerD2DList'] != 0)[0]
    not_visit_point = power_assign_list + parameter['nStartD2D']
    for root in parameter['priority']:
        longestPath = []
        vis = [False] * len(parameter['d2d_no_cell_interference_graph'])
        if not vis[root]:
            path = []
            longestPath = dfs(root, parameter['d2d_no_cell_interference_graph'], not_visit_point, vis, path, longestPath)

def dfs(node, graph, not_visit_point, vis, path, longestPath):
    vis[node] = True
    # if node in not_visit_point or node not in chooseList:
    #     p = path.copy()
    #     longestPath.append(p)
    # else:
    #     path.append(node)
    #     for i in graph[node]:
    #         if not vis[i]:
    #             dfs(i, graph, not_visit_point, vis, path, longestPath)
    #     p = path.copy()
    #     longestPath.append(p)
    #     path.pop()
    #     vis[node] = False

    return longestPath