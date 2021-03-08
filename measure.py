import numpy as np
import tools

def UplinkCUE(numCUE, numD2D, beamWide, dis_c2b, dis_c2d, ue_point, rx_point, numD2DReciver, candicate, directCUE, omnidirectCUE):
    tool = tools.Tool()
    i_d2d_rx = []   #Dict,每個D2D Rx包含被哪些CUE和D2D Tx干擾
    # i_d2d = []   #Dict,每個D2D被哪些CUE和D2D Tx干擾

    #CUE對D2D的干擾
    for d2d in range(numD2D):
        t = []      #d2d的干擾情況
        for rx in range(numD2DReciver[d2d]):
            r = {}  #干擾接收端的集合
            r_cue = {'cue':[]}      #每個rx被哪些CUE干擾
            for cue in candicate:
                #以CUE為圓心，BS為半徑，判斷D2D Rx是否在圓形範圍裡
                if cue in omnidirectCUE and dis_c2b[cue][0] >= dis_c2d[cue][d2d][rx]:
                    r_cue['cue'].append(cue)
                #以CUE和BS兩點,判斷D2D Rx是否在矩形範圍裡
                elif cue in directCUE:
                    #先求出CUE與BS的方位角
                    bs = [0, 0]
                    p1,p2,p3,p4 = tool.GetRectanglePoint(ue_point[cue], bs, beamWide)
                    p = (rx_point[d2d][rx][0], rx_point[d2d][rx][1])                    
                    #判斷D2D Rx(p點)是否在矩形的4個頂點(p1,p2,p3,p4)內
                    if tool.IsPointInMatrix(p1, p2, p3, p4, p):
                        r_cue['cue'].append(cue)
            r.update(r_cue)
            t.append(r)
        i_d2d_rx.append(t)
    return i_d2d_rx
    
def DownlinkBS(numD2D, rx_point, numD2DReciver, beamPoint):
    tool = tools.Tool()
    i_d2d_rx = []   #Dict,每個D2D Rx包含被哪些BS和D2D Tx干擾

    #BS對D2D的干擾
    for d2d in range(numD2D):
        t = []
        for rx in range(numD2DReciver[d2d]):
            r = {}
            r_bs = {'cue':[]}
            for beam in beamPoint:
                if tool.IsPointInSector(beam, rx_point[d2d][rx]):
                    r_bs['cue'].append(0) #rx有在beam波束裡
            r.update(r_bs)
            t.append(r)
        i_d2d_rx.append(t)
    return i_d2d_rx

def Cell_in_OmniD2D(numCell, numD2D, dis_d2d, dis_d2c, candicate, omnidirectD2D):
    i_d2c = []   #List,BS被哪些D2D Tx干擾
    #判斷cell環境的UE是否在全向型D2D Tx的傳輸範圍內
    for cell in range(numCell):
        r_c = []
        for d2d in range(numD2D):
            #genrator的dis_d2b型態沒設置好,導致型態不同
            if numCell > 1:
                if d2d in omnidirectD2D and max(dis_d2d[d2d]) >= dis_d2c[d2d][cell] and d2d not in r_c and cell in candicate:
                    r_c.append(d2d)
            else:
                if d2d in omnidirectD2D and max(dis_d2d[d2d]) >= dis_d2c[d2d][cell] and d2d not in r_c:
                    r_c.append(d2d)
        i_d2c.append(r_c)
    return i_d2c

def Cell_in_DirectD2D(numCell, numD2D, ue_point, tx_point, rx_point, numD2DReciver, candicate, i_d2c, directD2D, beamWide):
    tool = tools.Tool()
    for d2d in range(numD2D):       #對別人造成干擾的D2D
        #以d2d Tx和他所有的D2D Rx兩點,判斷其他D2D Rx是否在矩形範圍裡
        if d2d in directD2D:
            #d2d Tx(干擾端)的每一個Rx
            for d2d_rx in range(numD2DReciver[d2d]):
                p1,p2,p3,p4 = tool.GetRectanglePoint(tx_point[d2d], rx_point[d2d][d2d_rx], beamWide)
                #判斷cell UE有無被D2D干擾
                for cell in range(numCell):
                    if numCell == 1:
                        p = (0, 0)
                        if tool.IsPointInMatrix(p1, p2, p3, p4, p) and d2d not in i_d2c[cell]:
                            i_d2c[cell].append(d2d)
                            i_d2c[cell].sort()
                    else:
                        p = (ue_point[cell][0], ue_point[cell][1])
                        if tool.IsPointInMatrix(p1, p2, p3, p4, p) and d2d not in i_d2c[cell] and cell in candicate:
                            i_d2c[cell].append(d2d)
                            i_d2c[cell].sort()
    return i_d2c

def BetweenD2D(numD2D, numRB, data, N0, beamWide, dis_d2d, dis_dij, g_d2d, numD2DReciver, i_d2d_rx, tx_point, rx_point, directD2D, omnidirectD2D):
    tool = tools.Tool()
    Pmax = 199.52623149688787
    minSINR = np.zeros(numD2D)
    nStartD2D = []
    for tx in range(numD2D):
        r_d2d = []
        minSINR[tx] = tool.data_sinr_mapping(data[tx], numRB)
        D2Dsinr = np.zeros((numD2DReciver[tx], numRB))
        for rx in range(numD2DReciver[tx]):
            r = {}
            r_dij = {'d2d':[]}
            for d2d in range(numD2D):       #對別人造成干擾的D2D
                #以d2d Tx為圓心，其最遠的Rx為半徑，判斷其他D2D Rx是否在圓形範圍裡
                if d2d in omnidirectD2D and max(dis_d2d[d2d]) >= dis_dij[d2d][tx][rx] and d2d != tx:
                    r_dij['d2d'].append(d2d)
                    r_dij['d2d'].sort()
                #以d2d Tx和他所有的D2D Rx兩點,判斷其他D2D Rx是否在矩形範圍裡
                elif d2d in directD2D and d2d != tx:
                    #d2d Tx(干擾端)的每一個Rx
                    for d2d_rx in range(numD2DReciver[d2d]):
                        p = (rx_point[tx][rx][0], rx_point[tx][rx][1])
                        p1,p2,p3,p4 = tool.GetRectanglePoint(tx_point[d2d], rx_point[d2d][d2d_rx], beamWide)
                        #判斷D2D Rx(p點)是否在矩形的4個頂點(p1,p2,p3,p4)內
                        if tool.IsPointInMatrix(p1, p2, p3, p4, p) and d2d not in r_dij['d2d']:
                            r_dij['d2d'].append(d2d)
                            r_dij['d2d'].sort()
            i_d2d_rx[tx][rx].update(r_dij)

            for rb in range(numRB):
                D2Dsinr[rx][rb] = (Pmax * g_d2d[tx][rx][rb]) / N0
        if np.min(D2Dsinr) < minSINR[tx]:
            nStartD2D.append(tx)
    return i_d2d_rx, nStartD2D

def InterferenceD2D(i_d2d_rx):
    i_d2d = []
    for tx in i_d2d_rx:
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
    return i_d2d