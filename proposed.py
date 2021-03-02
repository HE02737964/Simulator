import numpy as np

def find_d2d_root(numCell, numD2D, i_d2d, i_d2c, time, scheduleTimes, data):
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
    for i in root_d2d:
        scheduleTimes[i] += 1

    return root_d2d, scheduleTimes

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
        print(endPoint)
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
    print(i_d2d)
    print(root)
    print(longestPathList)
    return longestPathList

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