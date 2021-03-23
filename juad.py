import numpy as np

#一個CUE和D2D的計算
def juad(cue, d2d, **parameter):
    #cue和d2d所需的sinr值
    s_cue = parameter['minCUEsinr'][cue]
    s_d2d = parameter['minD2Dsinr'][d2d]
    
    #cue和d2d所需的資料量(Throughput)
    r_cue = parameter['data_cue'][cue]
    r_d2d = parameter['data_d2d'][d2d]
    
    #計算 Y0
    Y0_cue = ( s_cue * parameter['N0'] * ( s_d2d * parameter['g_d2c'] + parameter['g_d2d']) / (  parameter['g_d2d'] * parameter['g_c2b']  - ( s_d2d * s_cue * parameter['g_c2d'] * parameter['g_d2c'])) )
    
    #計算 Y1
    

    #計算 Y2
    

    #計算 Y3
    

    #計算 Y4
    

    #計算 Y5

