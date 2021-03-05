import numpy as np
import tools

def find_d2d_root(numCell, numD2D, numRB, i_d2d, i_d2c, time, scheduleTimes, data):
    tool = tools.Tool()
    i_len = np.zeros(numD2D)
    for tx in range(numD2D):
        i_len[tx] = len(i_d2d[tx]['cue']) + len(i_d2d[tx]['d2d']) + 1 #干擾鄰居的數量

    priority = (data / i_len) * (time / scheduleTimes)
    sort_priority = (-priority).argsort()

    root_d2d = []
    for d2d in sort_priority:
        flag = True
        if not i_d2d[d2d]['cue']: 
            for cell in range(numCell):
                if d2d in i_d2c[cell]:
                    flag = False
            if not (set(i_d2d[d2d]['d2d']) & set(root_d2d)): #the root list any element not interference d2d
                for root in root_d2d:
                    if d2d in i_d2d[root]['d2d']: #D2D interference root list element
                        flag = False
                if flag:
                    root_d2d.append(d2d)
    assignmentD2D = np.zeros((numD2D, numRB))
    powerList = np.zeros(numD2D)
    minSINR = np.zeros(numD2D)
    for i in root_d2d:
        scheduleTimes[i] += 1
        assignmentD2D[i] = 1
        powerList[i] = 199.52623149688787

    for i in range(numD2D):
        minSINR[i] = tool.data_sinr_mapping(data[i], numRB)

    return root_d2d, scheduleTimes, assignmentD2D, minSINR, powerList

def create_interference_graph(numCell, numD2D, i_d2d, i_d2c):
    graph = [[] for i in range(numD2D)]
    candidate, other  = not_interference_cell(numCell, numD2D, i_d2d, i_d2c)
    
    for d2d in candidate:
        for i in i_d2d[d2d]['d2d']:
            if i in candidate:
                graph[d2d].append(i)
    return graph, candidate, other

def find_longest_path(root, chooseList, graph, i_d2d):
    longestPathList = []
    endPoint = root.copy()
    for node in root:
        longestPath = []
        vis = [False] * len(graph)
        if not vis[node]:
            path = []
            deleteNode = node
            endPoint.remove(node)
            longestPath = dfs(node, graph, endPoint, chooseList, vis, path, longestPath)

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
            if len(i_d2d[sameLength[i][-1]]['d2d']) < numMinInte:
                minInte = len(i_d2d[sameLength[i][-1]]['d2d'])
                sol[-1:] = [sameLength[i]]
        
        for candicate in sol[0]:
            if candicate not in endPoint:
                endPoint.append(candicate)
        endPoint.sort()

        sol_longestPathDict = {}
        for i in sol:
            sol_longestPathDict[i[0]] = i[1:]
        longestPathList.append(sol_longestPathDict)
    return longestPathList

def phase2_power_configure(numRB, root, i_d2d_rx, g_d2d, g_dij, N0, longestPath, d2d_min_sinr, powerList, assignmentD2D, numD2DReciver):
    targetList = root.copy()
    longest = longestPath.copy()
    for path in longest:
        for key in path:
            if path[key]:
                point = len(path[key]) - 1
                while  point >= 0:
                    lastNode = path[key][point]
                    d2d_power_rx = np.zeros((numD2DReciver[lastNode], numRB))
                    for rx in range(numD2DReciver[lastNode]):
                        for rb in range(numRB):
                            interference = 0
                            for i in i_d2d_rx[lastNode][rx]['d2d']:
                                interference = interference + (powerList[i] * g_dij[i][lastNode][rx][rb])
                            d2d_power_rx[rx][rb] = (d2d_min_sinr[lastNode] * (N0 + interference)) / g_d2d[lastNode][rx][rb]
                            if d2d_power_rx[rx][rb] < 0.0001:
                                d2d_power_rx[rx][rb] = 0.0001
                            if d2d_power_rx[rx][rb] > 199.52623149688787:
                                d2d_power_rx[rx][rb] = 199.52623149688787
                    # powerList[lastNode] = max(powerList[lastNode], np.max(d2d_power_rx))
                    for d2d in targetList:
                        for rx in range(numD2DReciver[d2d]):
                            for rb in range(numRB):
                                interference = 0
                                for i in i_d2d_rx[d2d][rx]['d2d']:
                                    interference = interference + (powerList[i] * g_dij[i][d2d][rx][rb])
                                sinr = (powerList[d2d] * g_d2d[d2d][rx][rb]) / (N0 + interference)
                                if sinr < d2d_min_sinr[d2d]:
                                    powerList[lastNode] = 0
                                    print(path[key])
                                    print(lastNode)
                                    path[key].remove(lastNode)
                                    point = len(path[key]) - 1
                    point = point - 1
    print(10*np.log10(powerList))
    print(10*np.log10(d2d_min_sinr))
    for tx in range(10):
        sin = 1000
        power = 0
        for rx in range(numD2DReciver[tx]):
            for rb in range(numRB):
                interference = 0
                for i in i_d2d_rx[tx][rx]['d2d']:
                    interference = interference + (powerList[i] * g_dij[i][tx][rx][rb])
                sinr = (powerList[tx] * g_d2d[tx][rx][rb]) / (N0 + interference)
                power1 = (d2d_min_sinr[tx] * N0) / g_d2d[tx][rx][rb]
                if sinr < sin:
                    sin = sinr
                if power1 > power:
                    power = power1
                    
        if power > 199.52623149688787:
            print(10*np.log10(sin))
            print(np.min(g_d2d[tx]))
            print(tx,'power',10*np.log10(power))

def not_interference_cell(numCell, numD2D, i_d2d, i_d2c):
    noCell = []
    inCell = []
    for d2d in range(numD2D):
        flag = True
        if not i_d2d[d2d]['cue']: #CUE not interfernece D2D and D2D not interference BS
            for cell in range(numCell):
                if d2d in i_d2c[cell]:
                    flag = False
            if flag:
                noCell.append(d2d)
    inCell = np.setdiff1d(np.arange(numD2D), np.asarray(noCell))
    return noCell, inCell

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


