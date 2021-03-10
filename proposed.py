import numpy as np
import tools

np.seterr(divide='ignore', invalid='ignore')

def find_d2d_root(**parameter):
    tool = tools.Tool()
    i_len = np.zeros(parameter['numD2D'])
    for tx in range(parameter['numD2D']):
        i_len[tx] = len(parameter['i_d2d'][tx]['cue']) + len(parameter['i_d2d'][tx]['d2d']) + 1 #干擾鄰居的數量

    priority = (parameter['data_d2d'] / i_len) * (parameter['currentTime'] / parameter['scheduleTimes'])
    sort_priority = (-priority).argsort()

    root_d2d = []
    for d2d in sort_priority:
        flag = True
        if d2d in parameter['nStartD2D']: #D2D用最大power仍不滿足最小SINR,該round無法啟動
            flag = False
        if not parameter['i_d2d'][d2d]['cue']: 
            for cell in range(parameter['numCellRx']):
                if d2d in parameter['i_d2c'][cell]:
                    flag = False
            if not (set(parameter['i_d2d'][d2d]['d2d']) & set(root_d2d)): #the root list any element not interference d2d
                for root in root_d2d:
                    if d2d in parameter['i_d2d'][root]['d2d']: #D2D interference root list element
                        flag = False
                if flag:
                    root_d2d.append(d2d)
    assignmentD2D = np.zeros((parameter['numD2D'], parameter['numRB']))
    powerList = np.zeros(parameter['numD2D'])
    for i in root_d2d:
        parameter['scheduleTimes'][i] += 1
        assignmentD2D[i] = 1
        powerList[i] = parameter['Pmax']

    parameter.update({'phase1_root': root_d2d})
    parameter.update({'assignmentD2D' : assignmentD2D})
    parameter.update({'powerD2DList': powerList})
    return parameter

def create_interference_graph(**parameter):
    graph = [[] for i in range(parameter['numD2D'])]
    parameter = d2d_interference_cell(**parameter)
    
    for d2d in parameter['d2d_noCellInterference']:
        for i in parameter['i_d2d'][d2d]['d2d']:
            if i in parameter['d2d_noCellInterference']:
                graph[d2d].append(i)
    parameter.update({'d2d_interference_graph' : graph})
    return parameter

def find_longest_path(**parameter):
    longestPathList = []
    endPoint = parameter['phase1_root'] + parameter['nStartD2D']
    for node in parameter['phase1_root']:
        longestPath = []
        vis = [False] * len(parameter['d2d_interference_graph'])
        if not vis[node]:
            path = []
            # deleteNode = node
            endPoint.remove(node)
            longestPath = dfs(node, parameter['d2d_interference_graph'], endPoint, parameter['d2d_noCellInterference'], vis, path, longestPath)

        #找出最長path是多長
        pathLength = -1
        for i in range(len(longestPath)):
            if len(longestPath[i]) >= pathLength:
                pathLength = len(longestPath[i])

        #先選出最長的path(可能有多個)
        sameLength = []
        for i in range(len(longestPath)):
            if len(longestPath[i]) == pathLength:
                sameLength.append(longestPath[i])
        
        #path中最後一個node被干擾最少的優先
        numMinInte = 1000
        sol = []
        for i in range(len(sameLength)):
            if len(parameter['i_d2d'][sameLength[i][-1]]['d2d']) < numMinInte:
                minInte = len(parameter['i_d2d'][sameLength[i][-1]]['d2d'])
                sol[-1:] = [sameLength[i]]
        
        for candicate in sol[0]:
            if candicate not in endPoint:
                endPoint.append(candicate)
        endPoint.sort()

        sol_longestPathDict = {}
        for i in sol:
            sol_longestPathDict[i[0]] = i[1:]
        longestPathList.append(sol_longestPathDict)
    parameter.update({'longestPathList' : longestPathList})
    return parameter

def phase2_power_configure(**parameter):
    targetList = parameter['phase1_root'].copy()    #不能讓SINR低於所需最小值的D2D List
    longest = parameter['longestPathList'].copy()
    for path in longest:
        for key in path:
            if path[key]:
                point = len(path[key]) - 1
                while  point >= 0:
                    flag = True
                    lastNode = path[key][point]
                    d2d_power_rx = np.zeros((parameter['numD2DReciver'][lastNode], parameter['numRB']))
                    for rx in range(parameter['numD2DReciver'][lastNode]):
                        for rb in range(parameter['numRB']):
                            interference = 0
                            for i in parameter['i_d2d_rx'][lastNode][rx]['d2d']:
                                interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][lastNode][rx][rb])
                            d2d_power_rx[rx][rb] = (parameter['minD2Dsinr'][lastNode] * (parameter['N0'] + interference)) / parameter['g_d2d'][lastNode][rx][rb]
                            if d2d_power_rx[rx][rb] < 0.0001:
                                d2d_power_rx[rx][rb] = 0.0001
                            if d2d_power_rx[rx][rb] > 199.52623149688787:
                                d2d_power_rx[rx][rb] = 199.52623149688787
                                flag = False
                    parameter['powerD2DList'][lastNode] = max(parameter['powerD2DList'][lastNode], np.max(d2d_power_rx))
                    for d2d in targetList:
                        for rx in range(parameter['numD2DReciver'][d2d]):
                            for rb in range(parameter['numRB']):
                                interference = 0
                                for i in parameter['i_d2d_rx'][d2d][rx]['d2d']:
                                    interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][d2d][rx][rb])
                                sinr = (parameter['powerD2DList'][d2d] * parameter['g_d2d'][d2d][rx][rb]) / (parameter['N0'] + interference)
                                if sinr < parameter['minD2Dsinr'][d2d]:
                                    flag = False
                    if flag:
                        targetList.append(lastNode)
                        point = point - 1
                    else:
                        removeNode = path[key][len(path[key])-1]
                        parameter['powerD2DList'][lastNode] = 0
                        parameter['powerD2DList'][removeNode] = 0
                        path[key].remove(removeNode)
                        if removeNode in targetList:
                            targetList.remove(removeNode)
                        point = len(path[key]) - 1

                for d2d in path[key]:
                    parameter['assignmentD2D'][d2d] = 1

    for tx in parameter['phase1_root']:
        d2d_power_rx = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
        for rx in range(parameter['numD2DReciver'][tx]):
            for rb in range(parameter['numRB']):
                interference = 0
                for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
                    interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
                d2d_power_rx[rx][rb] = (parameter['minD2Dsinr'][tx] * (parameter['N0'] + interference)) / parameter['g_d2d'][tx][rx][rb]
        parameter['powerD2DList'][tx] = np.max(d2d_power_rx)
    return parameter

def phase3_power_configure(**parameter):
    candicate = (-parameter['data_d2d']).argsort()  #根據資料量大小做排序
    #刪除已經分配RB的D2D以及與Cell環境有干擾的D2D
    index = []
    for d2d in range(parameter['numD2D']):
        if all(parameter['assignmentD2D'][d2d]) or d2d in parameter['d2d_cellInterference']:
            index.append(np.argwhere(d2d == candicate)[0][0])        
    candicate = np.delete(candicate, index)

    #每個Rx計算目前現有的干擾強度以及計算所需SINR之傳輸功率
    for tx in candicate:
        d2d_power_rx = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
        for rx in range(parameter['numD2DReciver'][tx]):
            for rb in range(parameter['numRB']):
                interference = 0
                for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
                    interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
                d2d_power_rx[rx][rb] = (parameter['minD2Dsinr'][tx] * (parameter['N0'] + interference)) / parameter['g_d2d'][tx][rx][rb]
        parameter['powerD2DList'][tx] = np.max(d2d_power_rx)
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

def dfs(node, graph, endPoint, chooseList, vis, path, longestPath):
    vis[node] = True
    if node in endPoint or node not in chooseList:
        p = path.copy()
        longestPath.append(p)
    else:
        path.append(node)
        for i in graph[node]:
            if not vis[i]:
                dfs(i, graph, endPoint, chooseList, vis, path, longestPath)
        p = path.copy()
        longestPath.append(p)
        path.pop()
        vis[node] = False

    return longestPath


