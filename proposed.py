import numpy as np
import tools
import sys

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

        if tx_min_power > parameter['Pmax']:
            # tx_min_power = parameter['Pmax']
            tx_min_power = 0
        elif tx_min_power < parameter['Pmin']:
            tx_min_power = parameter['Pmin']

        # print(10*np.log10(tx_min_power))

        #已設置過傳輸功率且干擾鄰居有tx的D2D的干擾鄰居有tx的D2D計算滿足最小所需的SINR能接受的干擾，可推算出tx能用的傳輸功率
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
            parameter['assignmentD2D'][tx] = 1
            parameter['candicateD2D'].append(tx)
            parameter['candicateD2D'].sort()
        else:
            parameter['powerD2DList'][tx] = 0

    #D2D在每個RB上的傳輸功率
    # powerD2DList_rb = np.zeros((parameter['numD2D'], parameter['numRB']))
    # for d2d in range(parameter['numD2D']):
    #     if parameter['powerD2DList'][d2d] != 0:
    #         powerD2DList_rb[d2d] = parameter['powerD2DList'][d2d]
    
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
    #     if np.round(10*np.log10(s[tx]), 1) < np.round(10*np.log10(parameter['minD2Dsinr'][tx]), 1) and parameter['powerD2DList'][tx] != 0:
    #         print('tx',tx)
    #         print(np.round(10*np.log10(parameter['minD2Dsinr'][tx]), 1))
    #         print(np.round(10*np.log10(s[tx]), 1))
    #         print(np.round(10*np.log10(parameter['powerD2DList'][tx]), 1))


    
    #每個會干擾CUE(或BS)的tx首先找出可用的RB，得到可用的SINR，接下來則與前面步驟相同
    for tx in candicate_cell:
        d2d_rb = np.ones(parameter['numRB'], dtype=int)
        numRB = parameter['numRB']
        #找出tx可用的RB(即不干擾CUE的RB)
        for cell_rx in range(parameter['numCellRx']):
            #檢查Cell rx的干擾鄰居是否有tx
            if tx in parameter['i_d2c'][cell_rx]: 
                for rb in range(parameter['numRB']):
                    if parameter['assignmentRxCell'][cell_rx][rb] == 1:
                            d2d_rb[rb] = 0
                            numRB = numRB - 1
                            
        #將可用RB換成所需SINR，並檢查SINR或可用RB的數量是否能滿足
        parameter['minD2Dsinr'][tx] = tool.data_sinr_mapping(parameter['data_d2d'][tx], numRB)
        if parameter['minD2Dsinr'][tx] == 0:
            break
        
        #每個Rx計算目前現有的干擾強度以及計算所需SINR之Tx傳輸功率
        tx_power =  parameter['Pmax']
        flag = True
        tx_power_rx = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
        for rx in range(parameter['numD2DReciver'][tx]):
            for rb in range(parameter['numRB']):
                interference = 0
                #只計算tx能使用的RB
                if d2d_rb[rb] == 1:
                    for i in parameter['i_d2d_rx'][tx][rx]['cue']:
                        #tx的cue干擾鄰居有使用該RB的話才有干擾
                        if parameter['assignmentTxCell'][i][rb] == 1:
                            interference = interference + (parameter['powerCUEList'][i] * parameter['g_c2d'][i][tx][rx][rb])
                    for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
                        #tx的d2d干擾鄰居有使用該RB的話才有干擾
                        if parameter['assignmentD2D'][i][rb] == 1:
                            interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
                tx_power_rx[rx][rb] = (parameter['minD2Dsinr'][tx] * (parameter['N0'] + interference)) / parameter['g_d2d'][tx][rx][rb]
        tx_min_power = np.max(tx_power_rx)

        if tx_min_power > parameter['Pmax']:
            # tx_min_power = parameter['Pmax']
            tx_min_power = 0
            break
        elif tx_min_power < parameter['Pmin']:
            tx_min_power = parameter['Pmin']
        print('tx need min power',tx,tx_min_power)

        #已設置過傳輸功率且干擾鄰居有tx的D2D計算滿足最小所需的SINR能接受的干擾，可推算出tx能用的傳輸功率
        for d2d in parameter['candicateD2D']:
            for rx in range(parameter['numD2DReciver'][d2d]):
                if tx in parameter['i_d2d_rx'][d2d][rx]['d2d']:
                    flag = False
                    tx_power_d2dRx = np.zeros(parameter['numRB'])
                    for rb in range(parameter['numRB']):
                        interference = 0
                        #只計算tx能使用的RB
                        if d2d_rb[rb] == 1:
                            for i in parameter['i_d2d_rx'][d2d][rx]['cue']:
                                #tx的cue干擾鄰居有使用該RB的話才有干擾
                                if parameter['assignmentTxCell'][i][rb] == 1:
                                    interference = interference + (parameter['powerCUEList'][i] * parameter['g_c2d'][i][d2d][rx][rb])
                            for i in parameter['i_d2d_rx'][d2d][rx]['d2d']:
                                #tx的d2d干擾鄰居有使用該RB的話才有干擾，並計算出除了tx以外的干擾
                                if parameter['assignmentD2D'][i][rb] == 1 and tx != i:
                                    interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][d2d][rx][rb])
                            tx_power_d2dRx[rb] = ((parameter['powerD2DList'][d2d] * parameter['g_d2d'][d2d][rx][rb]) / (parameter['minD2Dsinr'][d2d] * parameter['g_dij'][tx][d2d][rx][rb])) - ((parameter['N0'] + interference) / parameter['g_dij'][tx][d2d][rx][rb])
                    min_tx_power_d2dRx = tx_power_d2dRx[np.nonzero(tx_power_d2dRx)]
                    if min_tx_power_d2dRx.size > 0 and np.min(min_tx_power_d2dRx) <= tx_power:
                        tx_power = np.min(min_tx_power_d2dRx)

        #已設置過傳輸功率且干擾鄰居有tx的CUE計算滿足最小所需的SINR能接受的干擾，可推算出tx能用的傳輸功率
        for cue_tx in range(parameter['numCellTx']):
            for cue_rx in range(parameter['numCellRx']):
                if tx in parameter['i_d2c'][rx]:
                    flag = False
                    tx_power_CellRx = np.zeros((parameter['numCellRx'], parameter['numRB']))
                    for rb in range(parameter['numRB']):
                        if parameter['assignmentRxCell'][cue_rx][rb] == 1 and d2d_rb[rb] == 1:
                            interference = 0
                            for i in parameter['i_d2c'][cue_rx]:
                                if parameter['assignmentD2D'][i][rb] == 1 and tx != i:
                                    interference = interference + (parameter['powerD2DList'][i] * parameter['g_d2c'][i][rx][rb])
                            if parameter['numCellRx'] >= 2:
                                tx_power_CellRx[cue_rx][rb] = ((parameter['powerCUEList'][cue_tx] * parameter['g_c2b'][cue_tx][cue_rx][rb]) / (parameter['minCUEsinr'][cue_rx] * parameter['g_d2c'][cue_tx][cue_rx][rb])) - ((parameter['N0'] + interference) / parameter['g_c2b'][cue_tx][cue_rx][rb])
                            else:
                                tx_power_CellRx[cue_rx][rb] = ((parameter['powerCUEList'][cue_tx] * parameter['g_c2b'][cue_tx][cue_rx][rb]) / (parameter['minCUEsinr'][cue_tx] * parameter['g_d2c'][cue_tx][cue_rx][rb])) - ((parameter['N0'] + interference) / parameter['g_c2b'][cue_tx][cue_rx][rb])
                    min_tx_power_CellRx = tx_power_CellRx[np.nonzero(tx_power_CellRx)]
                    if min_tx_power_CellRx.size > 0 and np.min(min_tx_power_CellRx) <= tx_power:
                        tx_power = np.min(min_tx_power_CellRx)
        print(flag)
        print('use rb',d2d_rb)
        print('with interference power',tx_power)
        #已設置傳輸功率過的D2D的干擾鄰居都沒有tx
        if flag:
            tx_power = tx_min_power
        else:
            if tx_power >= parameter['Pmax'] or tx_power < parameter['Pmin']:
                tx_power = 0
                break
        if tx_power >= tx_min_power:
            print(tx,'assign')
            parameter['powerD2DList'][tx] = tx_power
            for rb in range(parameter['numRB']):
                if d2d_rb[rb] == 1:
                    parameter['assignmentD2D'][tx][rb] = 1
            parameter['candicateD2D'].append(tx)
            parameter['candicateD2D'].sort()
        else:
            print(tx,'dont assign')
            parameter['powerD2DList'][tx] = 0

        print()
    print(candicate_d2d)
    print(candicate_cell)
    sinr_cue = np.zeros(parameter['numCUE'])
    sinr_d2d = np.zeros(parameter['numD2D'])
    for tx in range(parameter['numD2D']):
        s_rx = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
        for rx in range(parameter['numD2DReciver'][tx]):
            for rb in range(parameter['numRB']):
                interference = 0
                for i in parameter['i_d2d_rx'][tx][rx]['d2d']:
                    if parameter['assignmentD2D'][tx][rb] == 1 and parameter['assignmentD2D'][i][rb] == 1:
                        interference = interference + (parameter['powerD2DList'][i] * parameter['g_dij'][i][tx][rx][rb])
                i = interference
                for i in parameter['i_d2d_rx'][tx][rx]['cue']:
                    if parameter['assignmentD2D'][tx][rb] == 1 and parameter['assignmentTxCell'][i][rb] == 1:
                        interference = interference + (parameter['powerCUEList'][i] * parameter['g_c2d'][i][tx][rx][rb])
                s_rx[rx][rb] = (parameter['powerD2DList'][tx] * parameter['g_d2d'][tx][rx][rb]) / ( parameter['N0'] + interference)
                x = (parameter['powerD2DList'][tx] * parameter['g_d2d'][tx][rx][rb]) / ( parameter['N0'] + i)
        sinr_d2d[tx] = np.min(s_rx)
        if np.round(10*np.log10(sinr_d2d[tx]), 1) < np.round(10*np.log10(parameter['minD2Dsinr'][tx]), 1) and parameter['powerD2DList'][tx] != 0:
            print("------------------------------------------------")
            print('D2D tx : ',tx)
            print(parameter['minD2Dsinr'][tx])
            print(sinr_d2d[tx])
            print(x)
            print(parameter['powerD2DList'][tx])
            print(parameter['i_d2d'][tx])
            # print(np.round(10*np.log10(parameter['minD2Dsinr'][tx]), 1))
            # print(np.round(10*np.log10(sinr_d2d[tx]), 1))
            print("------------------------------------------------")
            sys.exit()

    for tx in range(parameter['numCellTx']):
        s_rx = np.zeros((parameter['numCellRx'], parameter['numRB']))
        for rx in range(parameter['numCellRx']):
            for rb in range(parameter['numRB']):
                interference = 0
                for i in parameter['i_d2c'][rx]:
                    if parameter['assignmentRxCell'][rx][rb] == 1 and parameter['assignmentD2D'][i][rb] == 1:
                        interference = interference + (parameter['powerD2DList'][i] * parameter['g_d2c'][i][rx][rb])
                if parameter['numCellRx'] >= 2:
                    s_rx[rx][rb] = (parameter['powerCUEList'][tx] * parameter['g_c2b'][tx][rx][rb]) / ( parameter['N0'] + interference)
                else:
                    s_rx[rx][rb] = (parameter['powerCUEList'][tx] * parameter['g_c2b'][tx][rx][rb]) / ( parameter['N0'] + interference)

            if parameter['numCellRx'] >= 2:
                sinr_cue[rx] = np.min(s_rx[rx])
                # if np.round(10*np.log10(sinr_cue[rx]), 1) < np.round(10*np.log10(parameter['minCUEsinr'][tx]), 1) and parameter['powerCUEList'][tx] != 0:
                #     print("------------------------------------------------")
                #     print('CUE rx : ',rx)
                #     print(parameter['minCUEsinr'][tx])
                #     print(sinr_cue[rx])
                #     print(parameter['i_d2c'][rx])
                #     print("------------------------------------------------")
            else:
                sinr_cue[tx] = np.min(s_rx[rx])
                # if np.round(10*np.log10(sinr_cue[tx]), 1) < np.round(10*np.log10(parameter['minCUEsinr'][tx]), 1) and parameter['powerCUEList'][tx] != 0:
                #     print("------------------------------------------------")
                #     print('CUE rx : ',rx)
                #     print(parameter['minCUEsinr'][tx])
                #     print(sinr_cue[tx])
                #     print(parameter['i_d2c'][rx])
                #     print("------------------------------------------------")

    print(parameter['candicateCUE'])
    print(np.round(10*np.log10(parameter['powerCUEList']),1))
    print(np.round(10*np.log10(parameter['minCUEsinr']), 1))
    print(np.round(10*np.log10(sinr_cue), 1))
    print(parameter['i_d2c'])
    for i in range(parameter['numCellRx']):
        for j in parameter['i_d2c'][i]:
            if parameter['i_d2c'][i]:
                print(parameter['powerD2DList'][j])

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


