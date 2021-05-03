import numpy as np
import munkres
import tools
import sys

#初始化參數
def initial_parameter(**parameter):
    weight_matrix = np.zeros((parameter['numD2D'], parameter['numCUE']))
    weight_cue = np.zeros((parameter['numD2D'], parameter['numCUE']))
    weight_d2d = np.zeros((parameter['numD2D'], parameter['numCUE']))
    
    sinrCUEList = np.zeros((parameter['numD2D'], parameter['numCUE']))
    sinrD2DList = np.zeros((parameter['numD2D'], parameter['numCUE']))

    powerCUEList = np.zeros((parameter['numD2D'], parameter['numCUE']))
    powerD2DList = np.zeros((parameter['numD2D'], parameter['numCUE']))

    assignmentD2D = np.zeros((parameter['numD2D'], parameter['numRB']))

    matching_pair = [[] for i in range(parameter['numCUE'])]

    data = np.copy(parameter['data_d2d'])
    
    parameter.update({'weight_matrix' : weight_matrix})
    parameter.update({'weight_cue' : weight_cue})
    parameter.update({'weight_d2d' : weight_d2d})
    parameter.update({'powerCUEList' : powerCUEList})
    parameter.update({'powerD2DList' : powerD2DList})
    parameter.update({'sinrCUEList' : sinrCUEList})
    parameter.update({'sinrD2DList' : sinrD2DList})
    parameter.update({'assignmentD2D' : assignmentD2D})
    parameter.update({'matching_pair' : matching_pair})
    parameter.update({'data' : data})
    return parameter

#一個CUE和D2D的計算
def gp_method(cue, d2d, **parameter):
    tool = tools.Tool()
    convert = tools.Convert()

    #判斷cue是bs還是cell ue
    c_tx = 0
    c_rx = 0
    if parameter['numCellRx'] == 1:
        c_tx = cue
        c_rx = 0
    else:
        c_tx = 0
        c_rx = cue

    #先判斷cue和d2d是否有干擾
    flag_cue = False
    flag_d2d = False

    #cue干擾d2d
    if cue in parameter['i_d2d'][d2d]['cue']:
        flag_cue = True

    #d2d干擾cue
    if d2d in parameter['i_d2c'][c_rx]:
        flag_d2d = True
    
    #cue和d2d所使用的RB總數量
    if parameter['numCellRx'] == 1:
        numCUERB = np.sum(parameter['assignmentTxCell'][cue], dtype=int)
        numD2DRB = np.sum(parameter['assignmentTxCell'][cue], dtype=int)
    else:
        numCUERB = np.sum(parameter['assignmentRxCell'][cue], dtype=int)
        numD2DRB = np.sum(parameter['assignmentRxCell'][cue], dtype=int)

    #cue和d2d所需的sinr值
    s_cue = parameter['minCUEsinr'][cue]
    # s_d2d = parameter['minD2Dsinr'][d2d]
    s_d2d = tool.data_sinr_mapping(parameter['data'][d2d], numD2DRB)
    parameter['minD2Dsinr'][d2d] = s_d2d

    #cue和d2d所需的資料量(Throughput)
    r_cue = parameter['data_cue'][cue]
    r_d2d = parameter['data'][d2d]
    if r_d2d == 0:
        parameter['powerCUEList'][d2d][cue] = 0
        parameter['powerD2DList'][d2d][cue] = 0
        
        parameter['weight_matrix'][d2d][cue] = 0
        parameter['weight_cue'][d2d][cue] = 0
        parameter['weight_d2d'][d2d][cue] = 0
        return parameter
    # r_d2d = tool.sinr_throughput_mapping(convert.mW_to_dB(s_d2d), numD2DRB)

    #取d2d - cue有干擾的d2drx中最差的gain
    g_d2d = 100
    if cue not in parameter['i_d2d'][d2d]['cue']:
        g_d2d = parameter['g_d2d'][d2d][np.nonzero(parameter['g_d2d'][d2d])]
        g_d2d = np.min(g_d2d)
    else:
        for rx in range(parameter['numD2DReciver'][d2d]):
            if cue in parameter['i_d2d_rx'][d2d][rx]['cue']:
                g_min = np.min(parameter['g_d2d'][d2d][rx])
                if g_min < g_d2d:
                    g_d2d = g_min

    #取cue - d2d所有rx最差的gain
    g_c2d = parameter['g_c2d'][c_tx][d2d][np.nonzero(parameter['g_c2d'][c_tx][d2d])]
    g_c2d = np.min(g_c2d)

    g_c2d = 100
    if cue not in parameter['i_d2d'][d2d]['cue']:
        g_c2d = parameter['g_c2d'][c_tx][d2d][np.nonzero(parameter['g_c2d'][c_tx][d2d])]
        g_c2d = np.min(g_c2d)
    else:
        for rx in range(parameter['numD2DReciver'][d2d]):
            if cue in parameter['i_d2d_rx'][d2d][rx]['cue']:
                g_min = np.min(parameter['g_c2d'][c_tx][d2d][rx])
                if g_min < g_c2d:
                    g_c2d = g_min

    #取tx - rx 最差的gain（因為每個RB的gain都相同，所以不管tx rx有沒有使用該rb都沒差)
    g_d2c = np.min(parameter['g_d2c'][d2d][c_rx])
    g_c2b = np.min(parameter['g_c2b'][c_tx][c_rx])

    #cue沒有干擾時的Throughput
    snr_cue = (parameter['Pmax'] * g_c2b) / (parameter['N0'])
    t_cue = tool.sinr_throughput_mapping(convert.mW_to_dB(snr_cue), numCUERB)

    #計算 Y0
    Y0_cue = (s_cue * parameter['N0'] * (s_d2d * g_d2c + g_d2d)) / (g_d2d * g_c2b - s_d2d * s_cue * g_c2d * g_d2c)
    Y0_d2d = (s_d2d * parameter['N0'] * (s_cue * g_c2d + g_c2b)) / (g_d2d * g_c2b - s_d2d * s_cue * g_d2c * g_c2d)
    Y0 = [Y0_cue, Y0_d2d]

    #計算 Y1
    Y1_cue  = (s_cue * (flag_d2d * parameter['Pmax'] * g_d2c + parameter['N0'])) / g_c2b
    Y1_d2d  = parameter['Pmax']
    Y1 = [Y1_cue, Y1_d2d]

    #計算 Y2
    Y2_cue = parameter['Pmax']
    Y2_d2d = parameter['Pmax']
    Y2 = [Y2_cue, Y2_d2d]

    #計算 Y3
    Y3_cue = parameter['Pmax']
    Y3_d2d = (s_d2d * (flag_cue * parameter['Pmax'] * g_c2d + parameter['N0'])) / g_d2d
    Y3 = [Y3_cue, Y3_d2d]

    #計算 Y4
    Y4_cue = parameter['Pmax']
    if not flag_d2d:
        Y4_d2d = (s_d2d * parameter['N0']) / g_d2d
    else:
        Y4_d2d = (parameter['Pmax'] * g_c2b - parameter['N0'] * s_cue) / (s_cue * g_d2c)
    Y4 = [Y4_cue, Y4_d2d]

    #計算 Y5
    if not flag_cue:
        Y5_cue = (s_cue * parameter['N0']) / g_c2b
    else:
        Y5_cue = (parameter['Pmax'] * g_d2d - parameter['N0'] * s_d2d) / (s_d2d * g_c2d)
    Y5_d2d = parameter['Pmax']
    Y5 = [Y5_cue, Y5_d2d]

    point_cue = [Y1_cue, Y2_cue, Y3_cue, Y4_cue, Y5_cue]
    point_d2d = [Y1_d2d, Y2_d2d, Y3_d2d, Y4_d2d, Y5_d2d]

    #計算d2d複用cue的rb時的throughput
    R_sum = np.zeros((5,3))
    for point in range(5):
        sinr_cue = (point_cue[point] * g_c2b) / (flag_d2d * point_d2d[point] * g_d2c +  parameter['N0'])
        R_cue = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr_cue), numCUERB)

        sinr_d2d = (point_d2d[point] * g_d2d) / (flag_cue * point_cue[point] * g_c2d + parameter['N0'])
        R_d2d = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr_d2d), numD2DRB)

        sum = R_cue + R_d2d
        R_sum[point][0] = sum
        R_sum[point][1] = R_cue
        R_sum[point][2] = R_d2d

    for point in range(5):
        if R_sum[point][1] < r_cue:
            R_sum[point] = 0

        if R_sum[point][2] < r_d2d:
            R_sum[point] = 0

    #分為3種case，將不合理的功率值設為0
    #這裡需要確認判斷功率的條件
    # #case 1 論文中圖(b)的Y1,Y2
    # if Y1_cue < parameter['Pmax'] and Y3_d2d < parameter['Pmax']:
    #     R_sum[3] = 0
    #     R_sum[4] = 0

    # #case 2 論文中圖(c)的Y2,Y4
    # if Y3_d2d < parameter['Pmax'] and  Y4_d2d < parameter['Pmax']:
    #     R_sum[0] = 0
    #     R_sum[2] = 0
    #     R_sum[4] = 0

    # #case 3 論文中圖(d)的Y1,Y5
    # if Y5_cue < parameter['Pmax'] and Y1_cue < parameter['Pmax']:
    #     R_sum[1] = 0
    #     R_sum[2] = 0
    #     R_sum[3] = 0

    power_cue = power_d2d = 0

    #找出R_sum最大的index
    solution = np.max(R_sum[:,0])
    index = np.where(R_sum == solution)
    index_cue = index[1][0]
    index_d2d = index[0][0]

    #計算最大throughput組合的d2d sinr和cue throughput
    sinr_d2d = (point_d2d[index_d2d] * g_d2d) / (flag_cue * point_cue[index_d2d] * g_c2d + parameter['N0'])
    throughput_d2d = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr_d2d), numD2DRB)

    #計算最大throughput組合的cue sinr和cue throughput
    sinr_cue = (point_cue[index_cue] * g_c2b) / (flag_d2d * point_d2d[index_d2d] * g_d2c + parameter['N0'])
    throughput_cue = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr_cue), numCUERB)

    #設置cue和d2d的傳輸功率 
    power_cue = point_cue[index_d2d]
    power_d2d = point_d2d[index_d2d]

    #與d2d匹配後對整體throughput的提升
    solution = solution -  t_cue

    #表示cue和d2d不能形成匹配
    if Y0_cue > parameter['Pmax'] or Y0_d2d > parameter['Pmax']:
        solution = 0

    if Y0_cue < parameter['Pmin'] or Y0_d2d < parameter['Pmin']:
        solution = 0

    if solution <= 0:
        solution = 0
        
        power_cue = parameter['Pmax']
        sinr_cue = (power_cue * g_c2b) / (parameter['N0'])
        
        power_d2d = 0
        sinr_d2d = 0

        throughput_cue = tool.sinr_throughput_mapping(convert.mW_to_dB(sinr_cue), numCUERB)
        throughput_d2d = 0

    if throughput_cue > r_cue:
        throughput_cue = r_cue
    
    if throughput_d2d > r_d2d:
        throughput_d2d = r_d2d

    parameter['powerCUEList'][d2d][cue] = power_cue
    parameter['powerD2DList'][d2d][cue] = power_d2d

    parameter['sinrCUEList'][d2d][cue] = sinr_cue
    parameter['sinrD2DList'][d2d][cue] = sinr_d2d


    # parameter.update({'throughputRasing' : solution})
    # parameter.update({'throughputCUE' : throughput_cue})
    # parameter.update({'maxThroughputCUE' : t_cue})
    
    parameter['weight_matrix'][d2d][cue] = solution
    parameter['weight_cue'][d2d][cue] = throughput_cue
    parameter['weight_d2d'][d2d][cue] = throughput_d2d
    return parameter

def bipartite_matching(**parameter):
    cost_matrix = parameter['weight_matrix'].copy()
    max_value = np.max(cost_matrix)
    cost_matrix = max_value - cost_matrix
    cost_matrix = cost_matrix.tolist()

    m = munkres.Munkres()
    indexes = m.compute(cost_matrix)
    # munkres.print_matrix(cost_matrix, msg='Lowest cost through this matrix:')
    
    cost = 0
    for row, column in indexes:
        value = cost_matrix[row][column]
        cost = cost + value
    parameter.update({'matching_index' : indexes})
    print('matching index',indexes)
    return parameter

def throughput_rasing(**parameter):
    # parameter.pop('throughputRasing')
    # parameter.pop('throughputCUE')
    # parameter.pop('maxThroughputCUE')
    
    parameter['weight_matrix'].fill(0)

    #每個cue找出可配對的d2d list(可配對的規則是不能干擾已經與cue配對之d2d)
    assignmentD2D = [i[0] for i in parameter['matching_index']]
    assignmentCUE = [i[1] for i in parameter['matching_index']]

    for index in range(len(assignmentCUE)):
        cue = assignmentCUE[index]
        subscript = []
        if parameter['powerCUEList'][assignmentD2D[index]][cue] != 0:
            for d2d in range(parameter['numD2D']):
                flag = False
                #d2d不在配對列表裡
                if d2d not in parameter['matching_pair'][cue] :
                    flag = True
                    for i in parameter['matching_pair'][cue]:
                        #d2d與配對列表裡的裝置都不能互相干擾
                        if d2d in parameter['i_d2d'][i]['d2d'] or i in parameter['i_d2d'][i]['d2d']:
                            flag = False
                if flag:
                    subscript.append(d2d)

        for d2d in subscript:
            parameter = gp_method(cue, d2d, **parameter)
    
    parameter.pop('matching_index')
    parameter = bipartite_matching(**parameter)
    return parameter

#主程式
def maximum_matching(**parameter):
    parameter = initial_parameter(**parameter)
    for j in range(parameter['numD2D']):
        for i in parameter['candicateCUE']:
            parameter = gp_method(i, j, **parameter)

    parameter = bipartite_matching(**parameter)
    
    #Assignment D2D RB
    juad_throughput = 0
    print(parameter['data_d2d'])
    assignmentD2D = [i[0] for i in parameter['matching_index']]
    assignmentCUE = [i[1] for i in parameter['matching_index']]
    for index in range(len(assignmentCUE)):
        d2d = assignmentD2D[index]
        cue = assignmentCUE[index]
        if parameter['numCellRx'] == 1:
            assignRB = parameter['assignmentTxCell'][cue].copy()
        else:
            assignRB = parameter['assignmentRxCell'][cue].copy()
        if parameter['powerCUEList'][d2d][cue] != 0 and parameter['powerD2DList'][d2d][cue] != 0:
            parameter['assignmentD2D'][d2d] = assignRB
            parameter['matching_pair'][cue].append(d2d)
            juad_throughput = juad_throughput + parameter['weight_d2d'][d2d][cue]
            parameter['data'][d2d] = parameter['data'][d2d] - parameter['weight_d2d'][d2d][cue]
    print('juad_throughput',juad_throughput)
    
    if len(parameter['candicateCUE']):
        iteration = int(parameter['numD2D'] / len(parameter['candicateCUE']))
    else:
        iteration = 0
    print('iteration',iteration)
    for i in range(iteration):
        parameter = throughput_rasing(**parameter)
        
        assignment1D2D = [i[0] for i in parameter['matching_index']]
        assignment1CUE = [i[1] for i in parameter['matching_index']]
        for i in range(len(assignmentCUE)):
            d2d = assignment1D2D[i]
            cue = assignment1CUE[i]
            if parameter['numCellRx'] == 1:
                assignRB = parameter['assignmentTxCell'][cue].copy()
            else:
                assignRB = parameter['assignmentRxCell'][cue].copy()

            if parameter['powerCUEList'][d2d][cue] != 0 and parameter['powerD2DList'][d2d][cue] != 0:
                parameter['assignmentD2D'][d2d] = assignRB
                parameter['matching_pair'][cue].append(d2d)
                print('mathcing pair',cue,parameter['matching_pair'][cue])
                # for d2d in parameter['matching_pair'][cue]:
                print('d2d th',parameter['weight_d2d'][d2d][cue])
                print('d2d po',parameter['powerD2DList'][d2d][cue])
                juad_throughput = juad_throughput + parameter['weight_d2d'][d2d][cue]
                parameter['data'][d2d] = parameter['data'][d2d] - parameter['weight_d2d'][d2d][cue]

    print('juad:throughput',juad_throughput)
    print('par',parameter['matching_pair'])
    parameter.update({'throughput' : juad_throughput})
    print(parameter['data'])
    print(parameter['data_d2d'])

    for cue in range(len(parameter['matching_pair'])):
        print(parameter['matching_pair'][cue])
    
    for d2d in range(parameter['numD2D']):
        if parameter['assignmentD2D'][d2d].any():
            print('d2d',d2d,parameter['assignmentD2D'][d2d])
            parameter['numAssignment'] = parameter['numAssignment'] + 1
    print(parameter['numAssignment'])

    return parameter