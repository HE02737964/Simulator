import numpy as np
import tools
import method

def mGreedy(**parameter):
    tool = tools.Tool()
    parameter = method.initial_parameter(**parameter)
    parameter = method.phase1(**parameter)
    # parameter = greedy(**parameter)
    parameter = method.cal_d2d_min_sinr_power(**parameter)
    parameter = method.throughput_collect(**parameter)
    parameter = tool.power_collect(**parameter)
    
    return parameter

def greedy(**parameter):
    tool = tools.Tool()
    convert = tools.Convert()

    rasing_data = []
    sortD2D = np.copy(parameter['priority_sort_index'])
    nStartD2D = parameter['nStartD2D'].copy()
    candicate = sortD2D[np.in1d(sortD2D, nStartD2D)]
    
    for d2d in candicate:
        power = cal_min_interference_power(d2d, **parameter)
        numRB = np.sum(parameter['d2d_use_rb_List'][d2d])

        if power < parameter['Pmax'] and power >= parameter['Pmin'] and numRB != 0:
            #為了要計算d2d的sinr,假設已分配RB和power
            parameter['assignmentD2D'][d2d] = np.copy(parameter['d2d_use_rb_List'][d2d])
            parameter['powerD2DList'][d2d] = power

            sinr = method.cal_d2d_sinr(d2d, **parameter)
            sinrDB = convert.mW_to_dB(sinr)

            if sinrDB >= -6.7:
                throughput = tool.sinr_throughput_mapping(sinrDB, numRB)
                rasing_data.append(throughput)

                parameter['minD2Dsinr'][d2d] = sinr
                parameter['data_d2d'][d2d] = throughput

            else:
                #d2d不滿足條件,不能啟動,RB收回以及power歸0
                parameter['assignmentD2D'][d2d].fill(0)
                parameter['powerD2DList'][d2d] = 0

    return parameter

#計算能對其他裝置造成的最小干擾功率(p1)
def cal_min_interference_power(d2d, **parameter):
    #d2d沒有干擾任何裝置
    if (not parameter['t_d2d'][d2d]) and (not parameter['t_d2c'][d2d]):
        return -1

    #被干擾的裝置分為2種case討論，一種是d2d另一種是cue
    Pmin = parameter['Pmax'] + 1
    #flag表示d2d會干擾已配置power的tx
    flag = False
    #方便計算干擾用，先假設d2d已被分配它能使用的rb
    parameter['assignmentD2D'][d2d] = np.copy(parameter['d2d_use_rb_List'][d2d])
    for tx in parameter['t_d2d'][d2d]:
        #被d2d干擾的tx尚未被assign或他在不能啟動的列表裡略過計算
        if parameter['powerD2DList'][tx] == 0 or tx in parameter['nStartD2D']:
            continue
        for rx in range(parameter['numD2DReciver'][tx]):
            #d2d會干擾tx的rx
            if d2d in parameter['i_d2d_rx'][tx][rx]['d2d']:
                flag = True
                d2d_min_power = np.zeros(parameter['numRB'])
                for rb in range(parameter['numRB']):
                    if parameter['assignmentD2D'][d2d][rb] == 1 and parameter['assignmentD2D'][tx][rb] == 1:
                        interference = method.cal_d2d_interference(tx, rx, rb, **parameter)
                        d2d_min_power[rb] = ((parameter['powerD2DList'][tx] * parameter['g_d2d'][tx][rx][rb]) / (parameter['minD2Dsinr'][tx] * parameter['g_dij'][d2d][tx][rx][rb])) - ((parameter['N0'] + interference) / parameter['g_dij'][d2d][tx][rx][rb])
                d2d_nonzero_min_power = d2d_min_power[np.nonzero(d2d_min_power)]
                if d2d_nonzero_min_power.size > 0 and np.min(d2d_min_power) < Pmin:
                    Pmin = np.min(d2d_min_power)

    parameter['assignmentD2D'][d2d].fill(0)

    if not flag:
        return -1
    else:
        return Pmin