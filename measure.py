import numpy as np
import tools

def UplinkCUE(**parameter):
    tool = tools.Tool()
    i_d2d_rx = []   #Dict,每個D2D Rx包含被哪些CUE和D2D Tx干擾
    t_c2d = [[] for i in range(parameter['numCellTx'])] #cue干擾哪些d2d
    #CUE對D2D的干擾
    for d2d in range(parameter['numD2D']):
        i_d2d_list = []      #d2d的干擾情況
        for rx in range(parameter['numD2DReciver'][d2d]):
            i_rx_list = {}  #干擾接收端的集合
            i_rx = {'cue':[]}      #每個rx被哪些CUE干擾
            for cue in parameter['candicateCUE']:
                #以CUE為圓心，BS為半徑，判斷D2D Rx是否在圓形範圍裡，表示rx會被cue干擾
                if cue in parameter['omnidirectCUE'] and parameter['d_c2b'][cue][0] >= parameter['d_c2d'][cue][d2d][rx] and d2d not in t_c2d[cue]:
                    i_rx['cue'].append(cue)
                    t_c2d[cue].append(d2d)
                #以CUE和BS兩點,判斷D2D Rx是否在矩形範圍裡
                elif cue in parameter['directCUE']:
                    #先求出CUE與BS的方位角
                    bs = [0, 0]
                    p1,p2,p3,p4 = tool.GetRectanglePoint(parameter['ue_point'][cue], bs, parameter['beamWide'])
                    p = (parameter['rx_point'][d2d][rx][0], parameter['rx_point'][d2d][rx][1])                    
                    #判斷D2D Rx(p點)是否在矩形的4個頂點(p1,p2,p3,p4)內
                    if tool.IsPointInMatrix(p1, p2, p3, p4, p):
                        i_rx['cue'].append(cue)
                        t_c2d[cue].append(d2d)
            i_rx_list.update(i_rx)
            i_d2d_list.append(i_rx_list)
        i_d2d_rx.append(i_d2d_list)
    parameter.update({'i_d2d_rx' : i_d2d_rx})
    parameter.update({'t_c2d' : t_c2d})
    return parameter
    
def DownlinkBS(**parameter):
    tool = tools.Tool()
    i_d2d_rx = []   #Dict,每個D2D Rx包含被哪些BS和D2D Tx干擾
    t_c2d = [[] for i in range(parameter['numCellTx'])]
    #BS對D2D的干擾
    for d2d in range(parameter['numD2D']):
        i_d2d_list = []
        for rx in range(parameter['numD2DReciver'][d2d]):
            i_rx_list = {}
            i_rx = {'cue':[]}
            for beam in parameter['beamPoint']:
                if tool.IsPointInSector(beam, parameter['rx_point'][d2d][rx]) and d2d not in t_c2d[0]:
                    i_rx['cue'].append(0) #rx有在beam波束裡
                    t_c2d[0].append(d2d)
            i_rx_list.update(i_rx)
            i_d2d_list.append(i_rx_list)
        i_d2d_rx.append(i_d2d_list)
    parameter.update({'i_d2d_rx' : i_d2d_rx})
    parameter.update({'t_c2d' : t_c2d})
    return parameter

def Cell_in_OmniD2D(**parameter):
    i_d2c = []   #List,BS被哪些D2D Tx干擾
    t_d2c = [[] for i in range(parameter['numD2D'])] #d2d干擾哪些cue
    #判斷cell環境的UE是否在全向型D2D Tx的傳輸範圍內
    for cell in range(parameter['numCellRx']):
        i_c = []
        for d2d in range(parameter['numD2D']):
            if parameter['numCellRx'] > 1:
                #cue會被d2d tx干擾
                if d2d in parameter['omnidirectD2D'] and max(parameter['d_d2d'][d2d]) >= parameter['d_d2c'][d2d][cell] and d2d not in i_c and cell in parameter['candicateCUE'] and cell not in t_d2c[d2d]:
                    i_c.append(d2d)
                    t_d2c.append(cell)

            else:
                if d2d in parameter['omnidirectD2D'] and max(parameter['d_d2d'][d2d]) >= parameter['d_d2c'][d2d][cell] and d2d not in i_c and cell not in t_d2c[d2d]:
                    i_c.append(d2d)
                    t_d2c.append(cell)
        i_d2c.append(i_c)
    parameter.update({'i_d2c' : i_d2c})
    parameter.update({'t_d2c' : t_d2c})
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
                        if tool.IsPointInMatrix(p1, p2, p3, p4, p) and d2d not in parameter['i_d2c'][cell] and cell not in parameter['t_d2c'][d2d]:
                            parameter['i_d2c'][cell].append(d2d)
                            parameter['i_d2c'][cell].sort()
                            parameter['t_d2c'][d2d].append(cell)
                            parameter['t_d2c'][d2d].sort()
                    else:
                        p = (parameter['ue_point'][cell][0], parameter['ue_point'][cell][1])
                        if tool.IsPointInMatrix(p1, p2, p3, p4, p) and d2d not in parameter['i_d2c'][cell] and cell in parameter['candicateCUE'] and cell not in parameter['t_d2c'][d2d]:
                            parameter['i_d2c'][cell].append(d2d)
                            parameter['i_d2c'][cell].sort()
                            parameter['t_d2c'][d2d].append(cell)
                            parameter['t_d2c'][d2d].sort()
    return parameter

def BetweenD2D(**parameter):
    tool = tools.Tool()
    minSINR = np.zeros(parameter['numD2D'])
    t_d2d = [[] for i in range(parameter['numD2D'])]
    for tx in range(parameter['numD2D']):
        minSINR[tx] = tool.data_sinr_mapping(parameter['data_d2d'][tx], parameter['numRB'])
        for rx in range(parameter['numD2DReciver'][tx]):
            i_dij = {'d2d':[]}
            for d2d in range(parameter['numD2D']):       #對別人造成干擾的D2D
                #以tx為圓心，其最遠的rx為半徑，判斷d2d rx是否在圓形範圍裡
                if d2d in parameter['omnidirectD2D'] and max(parameter['d_d2d'][d2d]) >= parameter['d_dij'][d2d][tx][rx] and d2d != tx and tx not in t_d2d[d2d]:
                    i_dij['d2d'].append(d2d)
                    i_dij['d2d'].sort()
                    t_d2d[d2d].append(tx)
                    t_d2d[d2d].sort()
                    
                #以d2d Tx和他所有的D2D Rx兩點,判斷其他D2D Rx是否在矩形範圍裡
                elif d2d in parameter['directD2D'] and d2d != tx:
                    #d2d Tx(干擾端)的每一個Rx
                    for d2d_rx in range(parameter['numD2DReciver'][d2d]):
                        p = (parameter['rx_point'][tx][rx][0], parameter['rx_point'][tx][rx][1])
                        p1,p2,p3,p4 = tool.GetRectanglePoint(parameter['tx_point'][d2d], parameter['rx_point'][d2d][d2d_rx], parameter['beamWide'])
                        #判斷D2D Rx(p點)是否在矩形的4個頂點(p1,p2,p3,p4)內
                        if tool.IsPointInMatrix(p1, p2, p3, p4, p) and d2d not in i_dij['d2d'] and tx not in t_d2d[d2d]:
                            i_dij['d2d'].append(d2d)
                            i_dij['d2d'].sort()
                            t_d2d[d2d].append(tx)
                            t_d2d[d2d].sort()
            parameter['i_d2d_rx'][tx][rx].update(i_dij)

    parameter.update({'minD2Dsinr' : minSINR})
    parameter.update({'t_d2d' : t_d2d})
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