import numpy as np
import munkres
import tools
import sys

#一個CUE和D2D的計算
def juad_ul(cue, d2d, **parameter):
    tool = tools.Tool()

    #cue和d2d所需的sinr值
    s_cue = parameter['minCUEsinr'][cue]
    s_d2d = parameter['minD2Dsinr'][d2d]
    
    #cue和d2d所使用的RB總數量
    numCUERB = np.sum(parameter['assignmentTxCell'][cue], dtype=int)
    numD2DRB = np.sum(parameter['assignmentTxCell'][cue], dtype=int)
    
    #cue和d2d所需的資料量(Throughput)
    r_cue = parameter['data_cue'][cue]
    # r_d2d = parameter['data_d2d'][d2d] #思考是否需要將其轉換為可使用RB的數量中所需的資料量
    r_d2d = tool.sinr_throughput_mapping(s_d2d, numCUERB)

    #取d2d - d2d所有rx最差的gain
    g_d2d = parameter['g_d2d'][d2d][np.nonzero(parameter['g_d2d'][d2d])]
    g_d2d = np.min(g_d2d)
    
    #取cue - d2d所有rx最差的gain
    g_c2d = parameter['g_c2d'][cue][d2d][np.nonzero(parameter['g_c2d'][cue][d2d])]
    g_c2d = np.min(g_c2d)

    #取tx - rx 最差的gain（因為每個RB的gain都相同，所以不管tx rx有沒有使用該rb都沒差)
    g_d2c = np.min(parameter['g_d2c'][d2d])
    g_c2b = np.min(parameter['g_c2b'][cue])

    #cue沒有干擾時的Throughput
    snr_cue = (parameter['Pmax'] * g_c2b) / (parameter['N0'])
    t_cue = tool.sinr_throughput_mapping(snr_cue, numCUERB)

    #計算 Y0
    Y0_cue = (s_cue * parameter['N0'] * (s_d2d * g_d2c + g_d2d)) / (g_d2d * g_c2b - s_d2d * s_cue * g_c2d * g_d2c)
    Y0_d2d = (s_d2d * parameter['N0'] * (s_cue * g_c2d + g_c2b)) / (g_d2d * g_c2b - s_d2d * s_cue * g_d2c * g_c2d)
    Y0 = [Y0_cue, Y0_d2d]
    print(Y0)

    #計算 Y1
    Y1_cue  = (s_cue * (parameter['Pmax'] * g_d2c + parameter['N0'])) / g_c2b
    Y1_d2d  = parameter['Pmax']
    Y1 = [Y1_cue, Y1_d2d]

    #計算 Y2
    Y2_cue = parameter['Pmax']
    Y2_d2d = parameter['Pmax']
    Y2 = [Y2_cue, Y2_d2d]

    #計算 Y3
    Y3_cue = parameter['Pmax']
    Y3_d2d = (s_d2d * (parameter['Pmax'] * g_c2d + parameter['N0'])) / g_d2d
    Y3 = [Y3_cue, Y3_d2d]

    #計算 Y4
    Y4_cue = parameter['Pmax']
    Y4_d2d = (parameter['Pmax'] * g_c2b - parameter['N0'] * s_cue) / (s_cue * g_d2c)
    Y4 = [Y4_cue, Y4_d2d]

    #計算 Y5
    Y5_cue = (parameter['Pmax'] * g_d2d - parameter['N0'] * s_d2d) / (s_d2d * g_c2d)
    Y5_d2d = parameter['Pmax']
    Y5 = [Y5_cue, Y5_d2d]

    point_cue = [Y1_cue, Y2_cue, Y3_cue, Y4_cue, Y5_cue]
    point_d2d = [Y1_d2d, Y2_d2d, Y3_d2d, Y4_d2d, Y5_d2d]
    # print(point_cue)
    # print(point_d2d)
    # print("??")
    #計算d2d複用cue的rb時的throughput
    R_sum = np.zeros((5,3))
    for point in range(5):
        sinr_cue = (point_cue[point] * g_c2b) / (point_d2d[point] * g_d2c +  parameter['N0'])
        R_cue = tool.sinr_throughput_mapping(sinr_cue, numCUERB)

        sinr_d2d = (point_d2d[point] * g_d2d) / (point_cue[point] * g_c2d + parameter['N0'])
        R_d2d = tool.sinr_throughput_mapping(sinr_d2d, numD2DRB)

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
    #case 1 論文中圖(b)的Y1,Y2
    if Y1_cue < parameter['Pmax'] and Y3_d2d < parameter['Pmax']:
        R_sum[3] = 0
        R_sum[4] = 0

    #case 2 論文中圖(c)的Y2,Y4
    if Y3_d2d < parameter['Pmax'] and  Y4_d2d < parameter['Pmax']:
        R_sum[0] = 0
        R_sum[2] = 0
        R_sum[4] = 0

    #case 3 論文中圖(d)的Y1,Y5
    if Y5_cue < parameter['Pmax'] and Y1_cue < parameter['Pmax']:
        R_sum[1] = 0
        R_sum[2] = 0
        R_sum[3] = 0

    power_cue = power_d2d = 0

    #找出R_sum最大的index
    solution = np.max(R_sum[:,0])
    index = np.where(R_sum == solution)
    index_cue = index[1][0]
    index_d2d = index[0][0]

    #計算最大throughput組合的d2d sinr和cue throughput
    sinr_d2d = (point_d2d[index_d2d] * g_d2d) / (point_cue[index_d2d] * g_c2d + parameter['N0'])
    throughput_d2d = tool.sinr_throughput_mapping(sinr_d2d, numD2DRB)

    #計算最大throughput組合的cue sinr和cue throughput
    sinr_cue = (point_cue[index_cue] * g_c2b) / (point_d2d[index_d2d] * g_d2c + parameter['N0'])
    throughput_cue = tool.sinr_throughput_mapping(sinr_cue, numCUERB)

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
        throughput_d2d = 0 
        solution = 0
        sinr_cue = (parameter['Pmax'] * g_c2b) / (parameter['N0'])
        power_cue = parameter['Pmax']
        power_d2d = 0
        throughput_cue = tool.sinr_throughput_mapping(sinr_cue, numCUERB)
        print('cant matching')
    
    #debug用
    # print('Y0_cue', Y0_cue)
    # print('Y0_d2d', Y0_d2d)
    # print('cue rb : ',numCUERB)
    print(d2d, cue)
    print(point_cue)
    print(point_d2d)
    print('power_cue : ', power_cue)
    print('power_d2d : ', power_d2d)
    print('sinr_cue', sinr_cue)
    print('min_sinr', s_cue)
    print('sinr_d2d', sinr_d2d)
    print('min_sinr', s_d2d)
    # print('need data rate : ',r_cue)
    # print('cue',cue,'throughput',throughput_cue)
    # print('need data rate : ',r_d2d)
    # print('d2d',d2d,'throughput',throughput_d2d)
    print()

    if throughput_cue < r_cue:
        print('exit!!!')
        sys.exit()
    
    if throughput_d2d < r_d2d and throughput_d2d != 0:
        print('exit!!!')
        sys.exit()

    parameter.update({'throughputRasing' : solution})
    parameter.update({'throughputCUE' : throughput_cue})
    parameter.update({'maxThroughputCUE' : t_cue})
    parameter.update({'throughputD2D' : throughput_d2d})
    parameter.update({'power_cue' : power_cue})
    parameter.update({'power_d2d' : power_d2d})
    
    parameter['weight_matrix'][d2d][cue] = solution
    parameter['weight_cue'][d2d][cue] = throughput_cue
    parameter['weight_d2d'][d2d][cue] = throughput_d2d

    return parameter

def bipartite_matching(cue, d2d, **parameter):
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

    assignment = [i[0] for i in indexes]
    d2d_throughput = 0
    for i in range(parameter['numD2D']):
        if assignment[i] != 0:
            d2d_throughput = d2d_throughput + parameter['weight_d2d'][i][assignment[i]]

    numD2DSchedule = 0
    for i in range(parameter['numD2D']):
        if assignment[i] != 0 and parameter['weight_d2d'][i][assignment[i]] != 0:
            numD2DSchedule = numD2DSchedule + 1
    
    parameter.update({'matching_index' : indexes})

    return parameter