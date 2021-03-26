import numpy as np
import tools

def UplinkCUE(**parameter):
    tool = tools.Tool()
    i_d2d_rx = []   #Dict,每個D2D Rx包含被哪些CUE和D2D Tx干擾
    #CUE對D2D的干擾
    for d2d in range(parameter['numD2D']):
        t = []      #d2d的干擾情況
        for rx in range(parameter['numD2DReciver'][d2d]):
            r = {}  #干擾接收端的集合
            r_cue = {'cue':[]}      #每個rx被哪些CUE干擾
            for cue in parameter['candicateCUE']:
                #以CUE為圓心，BS為半徑，判斷D2D Rx是否在圓形範圍裡
                if cue in parameter['omnidirectCUE'] and parameter['d_c2b'][cue][0] >= parameter['d_c2d'][cue][d2d][rx]:
                    r_cue['cue'].append(cue)
                #以CUE和BS兩點,判斷D2D Rx是否在矩形範圍裡
                elif cue in parameter['directCUE']:
                    #先求出CUE與BS的方位角
                    bs = [0, 0]
                    p1,p2,p3,p4 = tool.GetRectanglePoint(parameter['ue_point'][cue], bs, parameter['beamWide'])
                    p = (parameter['rx_point'][d2d][rx][0], parameter['rx_point'][d2d][rx][1])                    
                    #判斷D2D Rx(p點)是否在矩形的4個頂點(p1,p2,p3,p4)內
                    if tool.IsPointInMatrix(p1, p2, p3, p4, p):
                        r_cue['cue'].append(cue)
            r.update(r_cue)
            t.append(r)
        i_d2d_rx.append(t)
    parameter.update({'i_d2d_rx' : i_d2d_rx})
    return parameter
    
def DownlinkBS(**parameter):
    tool = tools.Tool()
    i_d2d_rx = []   #Dict,每個D2D Rx包含被哪些BS和D2D Tx干擾

    #BS對D2D的干擾
    for d2d in range(parameter['numD2D']):
        t = []
        for rx in range(parameter['numD2DReciver'][d2d]):
            r = {}
            r_bs = {'cue':[]}
            for beam in parameter['beamPoint']:
                if tool.IsPointInSector(beam, parameter['rx_point'][d2d][rx]):
                    r_bs['cue'].append(0) #rx有在beam波束裡
            r.update(r_bs)
            t.append(r)
        i_d2d_rx.append(t)
    parameter.update({'i_d2d_rx' : i_d2d_rx})
    return parameter

def Cell_in_OmniD2D(**parameter):
    i_d2c = []   #List,BS被哪些D2D Tx干擾
    #判斷cell環境的UE是否在全向型D2D Tx的傳輸範圍內
    for cell in range(parameter['numCellRx']):
        r_c = []
        for d2d in range(parameter['numD2D']):
            if parameter['numCellRx'] > 1:
                if d2d in parameter['omnidirectD2D'] and max(parameter['d_d2d'][d2d]) >= parameter['d_d2c'][d2d][cell] and d2d not in r_c and cell in parameter['candicateCUE']:
                    r_c.append(d2d)
            else:
                if d2d in parameter['omnidirectD2D'] and max(parameter['d_d2d'][d2d]) >= parameter['d_d2c'][d2d][cell] and d2d not in r_c:
                    r_c.append(d2d)
        i_d2c.append(r_c)
    parameter.update({'i_d2c' : i_d2c})
    return parameter
    
def Cell_in_DirectD2D(**parameter):
    tool = tools.Tool()
    for d2d in range(parameter['numD2D']):       #對別人造成干擾的D2D
        #以d2d Tx和他所有的D2D Rx兩點,判斷其他D2D Rx是否在矩形範圍裡
        if d2d in parameter['directD2D']:
            #d2d Tx(干擾端)的每一個Rx
            for d2d_rx in range(parameter['numD2DReciver'][d2d]):
                p1,p2,p3,p4 = tool.GetRectanglePoint(parameter['tx_point'][d2d], parameter['rx_point'][d2d][d2d_rx], parameter['beamWide'])
                #判斷cell UE有無被D2D干擾
                for cell in range(parameter['numCellRx']):
                    if parameter['numCellRx'] == 1:
                        p = (0, 0)
                        if tool.IsPointInMatrix(p1, p2, p3, p4, p) and d2d not in parameter['i_d2c'][cell]:
                            parameter['i_d2c'][cell].append(d2d)
                            parameter['i_d2c'][cell].sort()
                    else:
                        p = (parameter['ue_point'][cell][0], parameter['ue_point'][cell][1])
                        if tool.IsPointInMatrix(p1, p2, p3, p4, p) and d2d not in parameter['i_d2c'][cell] and cell in parameter['candicateCUE']:
                            parameter['i_d2c'][cell].append(d2d)
                            parameter['i_d2c'][cell].sort()
    return parameter

def BetweenD2D(**parameter):
    tool = tools.Tool()
    minSINR = np.zeros(parameter['numD2D'])
    nStartD2D = []
    for tx in range(parameter['numD2D']):
        minSINR[tx] = tool.data_sinr_mapping(parameter['data_d2d'][tx], parameter['numRB'])
        D2Dsinr = np.zeros((parameter['numD2DReciver'][tx], parameter['numRB']))
        for rx in range(parameter['numD2DReciver'][tx]):
            r_dij = {'d2d':[]}
            for d2d in range(parameter['numD2D']):       #對別人造成干擾的D2D
                #以d2d Tx為圓心，其最遠的Rx為半徑，判斷其他D2D Rx是否在圓形範圍裡
                if d2d in parameter['omnidirectD2D'] and max(parameter['d_d2d'][d2d]) >= parameter['d_dij'][d2d][tx][rx] and d2d != tx:
                    r_dij['d2d'].append(d2d)
                    r_dij['d2d'].sort()
                #以d2d Tx和他所有的D2D Rx兩點,判斷其他D2D Rx是否在矩形範圍裡
                elif d2d in parameter['directD2D'] and d2d != tx:
                    #d2d Tx(干擾端)的每一個Rx
                    for d2d_rx in range(parameter['numD2DReciver'][d2d]):
                        p = (parameter['rx_point'][tx][rx][0], parameter['rx_point'][tx][rx][1])
                        p1,p2,p3,p4 = tool.GetRectanglePoint(parameter['tx_point'][d2d], parameter['rx_point'][d2d][d2d_rx], parameter['beamWide'])
                        #判斷D2D Rx(p點)是否在矩形的4個頂點(p1,p2,p3,p4)內
                        if tool.IsPointInMatrix(p1, p2, p3, p4, p) and d2d not in r_dij['d2d']:
                            r_dij['d2d'].append(d2d)
                            r_dij['d2d'].sort()
            parameter['i_d2d_rx'][tx][rx].update(r_dij)

            for rb in range(parameter['numRB']):
                D2Dsinr[rx][rb] = (parameter['Pmax'] * parameter['g_d2d'][tx][rx][rb]) / parameter['N0']
        if np.min(D2Dsinr) < minSINR[tx]:
            nStartD2D.append(tx)
    parameter.update({'nStartD2D' : np.asarray(nStartD2D)})
    parameter.update({'minD2Dsinr' : minSINR})
    return parameter

def InterferenceD2D(**parameter):
    i_d2d = []
    for tx in parameter['i_d2d_rx']:
        i = {'cue':[], 'd2d':[]}
        for rx in tx:
            for inte in rx['cue']:
                if inte not in i['cue']:
                    i['cue'].append(inte)
                    i['cue'].sort()
            for inte in rx['d2d']:
                if inte not in i['d2d']:
                    i['d2d'].append(inte)
                    i['d2d'].sort()
        i_d2d.append(i)
    parameter.update({'i_d2d' : i_d2d})
    return parameter