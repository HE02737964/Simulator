import numpy as np
import tools

np.seterr(divide='ignore', invalid='ignore')

def find_d2d_root(**parameter):
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
    parameter.update({'candicateD2D' : root_d2d})
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
                numMinInte = len(parameter['i_d2d'][sameLength[i][-1]]['d2d'])
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
                            if d2d_power_rx[rx][rb] > parameter['Pmax']:
                                d2d_power_rx[rx][rb] = parameter['Pmax']
                                flag = False
                            if d2d_power_rx[rx][rb] < parameter['Pmin']:
                                d2d_power_rx[rx][rb] = parameter['Pmin']
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
                    parameter['candicateD2D'].append(d2d)
                    parameter['candicateD2D'].sort()

    for tx in parameter['phase1_root']:
        d2d_power_rx = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
        for rx in range(parameter['numD2DReciver'][tx]):
            for rb in range(parameter['numRB']):
                interference = 0
                for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
                    interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
                d2d_power_rx[rx][rb] = (parameter['minD2Dsinr'][tx] * (parameter['N0'] + interference)) / parameter['g_d2d'][tx][rx][rb]
        root_power = np.max(d2d_power_rx)
        if root_power > parameter['Pmax']:
            root_power = parameter['Pmax']
        if root_power < parameter['Pmin']:
            root_power = parameter['Pmin']
        parameter['powerD2DList'][tx] = root_power

    return parameter

def phase3_power_configure(**parameter):
    tool = tools.Tool()
    candicate = (-parameter['data_d2d']).argsort()  #根據資料量大小做排序
    candicate_d2d = []
    candicate_cell = []
    for d2d in candicate:
        #挑出candicate中沒有被分配RB且與CUE沒有干擾的D2D
        if not all(parameter['assignmentD2D'][d2d]) and d2d in parameter['d2d_noCellInterference']:
            candicate_d2d.append(d2d)
        #挑出candicate中沒有被分配RB且與CUE有干擾的D2D
        elif not all(parameter['assignmentD2D'][d2d]) and d2d in parameter['d2d_cellInterference']:
            candicate_cell.append(d2d)
    print(candicate_d2d)
    #每個Rx計算目前現有的干擾強度以及計算所需SINR之Tx傳輸功率
    for tx in candicate_d2d:
        tx_power =  parameter['Pmax']
        flag = True
        tx_power_rx = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
        for rx in range(parameter['numD2DReciver'][tx]):
            for rb in range(parameter['numRB']):
                interference = 0
                for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
                    interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
                tx_power_rx[rx][rb] = (parameter['minD2Dsinr'][tx] * (parameter['N0'] + interference)) / parameter['g_d2d'][tx][rx][rb]
        tx_min_power = np.max(tx_power_rx)
        print(tx_min_power)
        if tx_min_power > parameter['Pmax']:
            # tx_min_power = parameter['Pmax']
            tx_min_power = 0
        elif tx_min_power < parameter['Pmin']:
            tx_min_power = parameter['Pmin']
        print(tx_min_power)
        print()
        # print(10*np.log10(tx_min_power))

        #已設置傳輸功率過的D2D的干擾鄰居有tx的D2D計算滿足最小所需的SINR能接受的干擾，可推算出tx能用的傳輸功率
        for d2d in parameter['candicateD2D']:
            for rx in range(parameter['numD2DReciver'][d2d]):
                if tx in parameter['i_d2d_rx'][d2d][rx]['d2d']:
                    flag = False
                    tx_power_d2dRx = np.zeros(parameter['numRB'])
                    for rb in range(parameter['numRB']):
                        interference = 0
                        for i in parameter['i_d2d_rx'][d2d][rx]['d2d']:
                            if tx != i:
                                interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][d2d][rx][rb])
                        tx_power_d2dRx[rb] = ((parameter['powerD2DList'][d2d] * parameter['g_d2d'][d2d][rx][rb]) / (parameter['minD2Dsinr'][d2d] * parameter['g_dij'][tx][d2d][rx][rb])) - ((parameter['N0'] + interference) / parameter['g_dij'][tx][d2d][rx][rb])
             
                    if np.min(tx_power_d2dRx) <= tx_power:
                        tx_power = np.min(tx_power_d2dRx)
        #已設置傳輸功率過的D2D的干擾鄰居都沒有tx
        if flag:
            tx_power = tx_min_power
        else:
            if tx_power >= parameter['Pmax']:
                # power = parameter['Pmax']
                tx_power = 0
            if tx_power < parameter['Pmin']:
                # power = parameter['Pmin']
                tx_power = 0
        if tx_power >= tx_min_power:
            parameter['powerD2DList'][tx] = tx_power
        else:
            parameter['powerD2DList'][tx] = 0

    #D2D在每個RB上的傳輸功率
    # powerD2DList_rb = np.zeros((parameter['numD2D'], parameter['numRB']))
    # for d2d in range(parameter['numD2D']):
    #     if parameter['powerD2DList'][d2d] != 0:
    #         powerD2DList_rb[d2d] = parameter['powerD2DList'][d2d]
    
    s = np.zeros(parameter['numD2D'])
    for tx in range(parameter['numD2D']):
        s_rx = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
        for rx in range(parameter['numD2DReciver'][tx]):
            for rb in range(parameter['numRB']):
                interference = 0
                for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
                    interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
                s_rx[rx][rb] = (parameter['powerD2DList'][tx] * parameter['g_d2d'][tx][rx][rb]) / ( parameter['N0'] + interference)
        s[tx] = np.min(s_rx)
        if np.round(10*np.log10(s[tx]), 1) < np.round(10*np.log10(parameter['minD2Dsinr'][tx]), 1) and parameter['powerD2DList'][tx] != 0:
            print('tx',tx)
            print(np.round(10*np.log10(parameter['minD2Dsinr'][tx]), 1))
            print(np.round(10*np.log10(s[tx]), 1))
            print(np.round(10*np.log10(parameter['powerD2DList'][tx]), 1))


    print('candicate_cell',candicate_cell)
    #每個會干擾CUE(或BS)的tx首先找出可用的RB，得到可用的SINR，接下來則與前面步驟相同
    for tx in candicate_cell:
        d2d_rb = np.ones(parameter['numRB'], dtype=int)
        numRB = parameter['numRB']
        #找出tx可用的RB(即不干擾CUE的RB)
        for cue in parameter['candicateCUE']:
            #所有CUE使用RB送給BS，只要該RB有使用，那一回合所有D2D都無法使用該RB，因為接收端只有一個是BS
            for cue_rx in range(parameter['numCellRx']):
                if tx in parameter['i_d2c'][cue_rx]: #D2D tx 會干擾 CUE rx
                    print("?????????")
                    for rb in range(parameter['numRB']):
                        if parameter['assignmentCUE'][cue][rb] == 1:
                            d2d_rb[rb] = 0
                            numRB = numRB - 1
    #     # print(d2d_rb)
    #     # print(numRB)
    #     #將可用RB換成所需SINR
    #     if numRB == 0:
    #         break
    #     parameter['minD2Dsinr'][tx] = tool.data_sinr_mapping(parameter['data_d2d'][tx], sum(d2d_rb)) #會有資料傳不完的問題
    #     # print(tool.data_sinr_mapping(parameter['data_d2d'][tx], sum(d2d_rb)))
    #     tx_power_rx = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
    #     #每個Rx計算目前現有的干擾強度以及計算所需SINR之Tx傳輸功率
    #     for rx in range(parameter['numD2DReciver'][tx]):
    #         for rb in range(parameter['numRB']):
    #             interference = 0
    #             #干擾只需計算tx能用的RB
    #             if d2d_rb[rb] == 1:
    #                 for cell in parameter['i_d2d_rx'][tx][rx]['cue']:
    #                     interference = interference + (parameter['powerCUEList'][cell] * parameter['g_c2d'][cell][tx][rx][rb])
    #                 for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
    #                     interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
    #                 tx_power_rx[rx][rb] = (parameter['minD2Dsinr'][tx] * (parameter['N0'] + interference)) / parameter['g_d2d'][tx][rx][rb]
    #     tx_min_power = np.max(tx_power_rx)
    #     if tx_min_power > parameter['Pmax']:
    #         tx_min_power = parameter['Pmax']
    #         # tx_min_power = 0
    #     if tx_min_power < parameter['Pmin']:
    #         tx_min_power = parameter['Pmin']

    #     #干擾鄰居有tx的UE計算滿足最小所需的SINR能接受的干擾，可推算出tx能用的傳輸功率
    #     for d2d in range(parameter['numD2D']):
    #         tx_power_d2dRx = np.zeros((parameter['numD2DReciver'][d2d], parameter['numRB']))
    #         for rx in range(parameter['numD2DReciver'][d2d]):
    #             # print('tx',tx,'i',d2d,parameter['i_d2d_rx'][d2d][rx])
    #             if tx in parameter['i_d2d_rx'][d2d][rx]['d2d']:
    #                 for rb in range(parameter['numRB']):
    #                     interference = 0
    #                     if parameter['assignmentD2D'][d2d][rb] == 1 and d2d_rb[rb] == 1:
    #                         for i in parameter['i_d2d_rx'][d2d][rx]['d2d']:
    #                             if tx != i:
    #                                 interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
    #                         tx_power_d2dRx[rx][rb] = ((parameter['powerD2DList'][d2d] * parameter['g_d2d'][d2d][rx][rb]) / (parameter['minD2Dsinr'][d2d] * parameter['g_dij'][tx][d2d][rx][rb])) - ((parameter['N0'] + interference) / parameter['g_dij'][tx][d2d][rx][rb])
    #         tx_power = np.min(tx_power_d2dRx)
    #         if tx_power > parameter['Pmax']:
    #             # power = parameter['Pmax']
    #             tx_power = 0
    #         if tx_power < parameter['Pmin']:
    #             # power = parameter['Pmin']
    #             tx_power = 0
    #         if tx_power >= tx_min_power:
    #             powerD2DList_rb[tx][rb] = tx_power
    #         else:
    #             powerD2DList_rb[tx][rb] = 0
        
    #     for cue in range(parameter['numCellTx']):
    #         tx_power_CellRx = np.zeros((parameter['numCellRx'], parameter['numRB']))
    #         for rx in range(parameter['numCellRx']):
    #             if tx in parameter['i_d2c'][rx]:
    #                 for rb in range(parameter['numRB']):
    #                     if parameter['assignmentCUE'][cue][rb] == 1 and d2d_rb[rb] == 1:
    #                         interference = 0
    #                         for i in parameter['i_d2c'][rx]:
    #                             if tx != i:
    #                                 interference = interference + (parameter['powerD2DList'][i] * parameter['g_d2c'][i][rx][rb])
    #                         # print(cue)
    #                         # print(parameter['powerCUEList']) #ul and dl reciver
    #                         tx_power_CellRx[rx][rb] = ((parameter['powerCUEList'][rx] * parameter['g_c2b'][cue][rx][rb]) / (parameter['minCUEsinr'][rx] * parameter['g_d2c'][tx][rx][rb])) - ((parameter['N0'] + interference) / parameter['g_c2b'][cue][rx][rb])
    #         tx_power = np.min(tx_power_CellRx)
    #         if tx_power > parameter['Pmax']:
    #             # power = parameter['Pmax']
    #             tx_power = 0
    #         if tx_power < parameter['Pmin']:
    #             # power = parameter['Pmin']
    #             tx_power = 0
    #         if tx_power >= np.max(powerD2DList_rb[tx][rb]):
    #             powerD2DList_rb[tx][rb] = tx_power
    #         else:
    #             powerD2DList_rb[tx][rb] = 0
    #     parameter['powerD2DList'][tx] = np.max(powerD2DList_rb[tx])
    # # print( parameter['powerD2DList'])
    # # print("=================================")
    # s = np.zeros(parameter['numD2D'])
    # for tx in range(parameter['numD2D']):
    #     s_rx = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
    #     for rx in range(parameter['numD2DReciver'][tx]):
    #         for rb in range(parameter['numRB']):
    #             interference = 0
    #             for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
    #                 interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
    #             s_rx[rx][rb] = (parameter['powerD2DList'][tx] * parameter['g_d2d'][tx][rx][rb]) / ( parameter['N0'] + interference)
    #     s[tx] = np.min(s_rx)

    # # print(np.round(10*np.log10(parameter['minD2Dsinr']), 1))
    # # print(np.round(10*np.log10(s), 1))
    # # print(np.round(10*np.log10(parameter['powerD2DList']), 1))
    # # print(len(parameter['phase1_root']))
    # # c = 0
    # # print(parameter['longestPathList'])
    # # for i in parameter['longestPathList']:
    # #     for j in i:
    # #         c = c + len(i[j])
    # # print(c)
    # # x = 0
    # # for i in range(parameter['numD2D']):
    # #     if parameter['powerD2DList'][i] != 0:
    # #         x = x + 1
    # # print(x)
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


