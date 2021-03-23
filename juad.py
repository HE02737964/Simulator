import numpy as np

#一個CUE和D2D的計算
def juad_ul(cue, d2d, **parameter):
    #cue和d2d所需的sinr值
    s_cue = parameter['minCUEsinr'][cue]
    s_d2d = parameter['minD2Dsinr'][d2d]
    
    #cue和d2d所需的資料量(Throughput)
    r_cue = parameter['data_cue'][cue]
    r_d2d = parameter['data_d2d'][d2d]
    
    # #找到cue使用RB的編號，因為gain都一樣，所以不須找最使用的RB中最差的gain
    # for i in range(parameter['numRB']):
    #     if parameter['assignmentTxCell'][i] == 1:
    #         rb = i
    rb = cue

    #cue沒有干擾時的SINR
    init_cue = (parameter['Pmax'] * parameter['g_c2b'][cue][0][rb])/(parameter['N0'])

    g_d2d = parameter['g_d2d'][d2d][np.nonzero(parameter['g_d2d'][d2d])]
    g_d2d = np.min(g_d2d)
    
    g_c2d = parameter['g_c2d'][cue][d2d][np.nonzero(parameter['g_c2d'][cue][d2d])]
    g_c2d = np.min(g_c2d)

    #計算 Y0
    Y0_cue = (s_cue * parameter['N0'] * (s_d2d * parameter['g_d2c'][d2d][0][rb] + g_d2d)) / (g_d2d * parameter['g_c2b'][cue][0][rb] - ( s_d2d * s_cue * g_c2d * parameter['g_d2c'][d2d][0][rb]))
    Y0_d2d = (s_d2d * parameter['N0'] * (s_cue * g_c2d + parameter['g_c2b'][cue][0][rb])) / (g_d2d * parameter['g_c2b'][cue][0][rb] - ( s_d2d * s_cue * parameter['g_d2c'][d2d][0][rb] * g_c2d))
    Y0 = [Y0_cue, Y0_d2d]

    #計算 Y1
    Y1_cue  = (s_cue * (parameter['Pmax'] * parameter['g_d2c'][d2d][0][rb] + parameter['N0'])) / parameter['g_c2b'][cue][0][rb]
    Y1_d2d  = parameter['Pmax']
    Y1 = [Y1_cue, Y1_d2d]

    #計算 Y2
    Y2_cue = parameter['Pmax']
    Y2_d2d = (s_d2d * (parameter['Pmax'] * g_c2d + parameter['N0'])) / g_d2d
    Y2 = [Y2_cue, Y2_d2d]

    #計算 Y3
    Y3_cue = parameter['Pmax']
    Y3_d2d = parameter['Pmax']
    Y3 = [Y3_cue, Y3_d2d]

    #計算 Y4
    Y4_cue = parameter['Pmax']
    Y4_d2d = (parameter['Pmax'] * parameter['g_c2b'][cue][0][rb] - parameter['N0'] * s_cue) / (s_cue * parameter['g_d2c'][d2d][0][rb])
    Y4 = [Y4_cue, Y4_d2d]

    #計算 Y5
    Y5_cue = (parameter['Pmax'] * g_d2d - parameter['N0'] * s_d2d) / (s_d2d * g_c2d)
    Y5_d2d = parameter['Pmax']
    Y5 = [Y5_cue, Y5_d2d]

    point_cue = [Y1_cue, Y2_cue, Y3_cue, Y4_cue, Y5_cue]
    point_d2d = [Y1_d2d, Y2_d2d, Y3_d2d, Y4_d2d, Y5_d2d]

    #計算d2d複用cue的rb時的sinr
    R_sum = np.zeros((5,3))
    for point in range(5):
        R_CUE = (point_cue[point] * parameter['g_c2b'][cue][0][rb]) / (point_d2d[point] * parameter['g_d2c'][d2d][0][rb] +  parameter['N0'] )
        R_D2D = (point_d2d[point] * g_d2d) / (point_cue[point] * g_c2d + parameter['N0'])
        sum1 = R_CUE + R_D2D
        R_sum[point][0] = sum1
        R_sum[point][1] = R_CUE
        R_sum[point][2] = R_D2D

    for point in range(5):
        if R_sum[point][1] < s_cue:
            R_sum[point] = 0

        if R_sum[point][2] < s_d2d:
            R_sum[point] = 0

    #分為3種case，將不合理的功率值設為0
    #case 1 論文中圖(b)的Y1,Y2
    if Y1_cue < parameter['Pmax'] and Y2_d2d < parameter['Pmax']:
        R_sum[3] = 0
        R_sum[4] = 0

    #case 2 論文中圖(c)的Y2,Y4
    if Y2_d2d < parameter['Pmax'] and  Y4_d2d < parameter['Pmax']:
        R_sum[0] = 0
        R_sum[2] = 0
        R_sum[4] = 0

    #case 3 論文中圖(d)的Y1,Y5
    if Y5_cue < parameter['Pmax'] and Y1_cue < parameter['Pmax']:
        R_sum[1] = 0
        R_sum[2] = 0
        R_sum[3] = 0

    #找出R_CUE最大的Y
    solution = np.max(R_sum[:,0])
    print(R_sum)
    print(solution)
    index = np.where(R_sum == solution)[0]
    point = index[0]

    d = (point_d2d[point] * g_d2d) / (point_cue[point] * g_c2d + parameter['N0'])
    c = (point_cue[point] * parameter['g_c2b'][cue][0][rb]) / (parameter['N0'])

    solution = solution -  init_cue

    if Y0_cue > parameter['Pmax'] or Y0_d2d > parameter['Pmax']:
        solution = 0

    if solution <= 0:
        d = 0 
        solution  =0
        c = (parameter['Pmax'] * parameter['g_c2b'][cue][0][rb]) / ((parameter['N0']))

    print('d,sinr',d)
    print('c,sinr',c)