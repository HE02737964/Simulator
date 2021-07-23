import sys
import initial_info
import method
import mGreedy
import juad
import gcrs
import greedy
import numpy as np

def m(totalTime):
    throughput = 0
    loss = 0
    assignment = 0
    distance = 0
    fairness = 0
    non_fairness = 0
    consumption = 0
    for ms in range(1, totalTime+1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        ul = generator_ul.get_ul_system_info(ms, **ul)
        ul = mGreedy.mGreedy(**ul)

        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        dl = generator_dl.get_dl_system_info(ms, **dl)
        dl = mGreedy.mGreedy(**dl)
        
        MaxThroughput = TotalThroughput = 0
        MaxThroughput = np.int64(MaxThroughput)
        TotalThroughput = np.int64(TotalThroughput)
        count = 0
        for d2d in range(ul['numD2D']):
            if ul['powerD2DList'][d2d] != 0:
                MaxThroughput = MaxThroughput + ul['data_d2d'][d2d]
                TotalThroughput = TotalThroughput + (ul['data_d2d'][d2d]**2)
                count += 1
            else:
                TotalThroughput = TotalThroughput + 0
            if dl['powerD2DList'][d2d] != 0:
                MaxThroughput = MaxThroughput + dl['data_d2d'][d2d]
                TotalThroughput = TotalThroughput + (dl['data_d2d'][d2d]**2)
                count += 1
            else:
                TotalThroughput = TotalThroughput + 0

        MaxThroughput = MaxThroughput**2
        NonTotalThroughput = TotalThroughput * count
        TotalThroughput = TotalThroughput * ul['numD2D']
        fair = MaxThroughput / TotalThroughput
        non_fair = MaxThroughput / NonTotalThroughput

        fairness = fairness + fair
        non_fairness = non_fairness + non_fair
        # MaxThroughput = MaxThroughput + (np.sum(ul['data_d2d']) + np.sum(dl['data_d2d']))
        throughput =  throughput + (ul['throughput'] + dl['throughput'])
        loss = loss + (ul['consumption'] + dl['consumption'])
        assignment = assignment + (ul['numAssignment'] + dl['numAssignment'])
        if ul['interferenceDistance'] == 0 and dl['interferenceDistance'] == 0:
            distance = distance + 1
        else:
            distance = distance + (ul['interferenceDistance'] + dl['interferenceDistance'])

        for d2d in range(ul['numD2D']):
            if ul['powerD2DList'][d2d] != 0:
                count = 1
                for tx in range(ul['numD2D']):
                    # print(ul['i_d2d'][d2d]['d2d'])
                    if d2d != tx and tx in ul['i_d2d'][d2d]['d2d'] and ul['powerD2DList'][tx] != 0:
                        count = count + 1
                        # print(count)
                t = (ul['throughput'] / ul['watt_list'][d2d]) / count
                consumption = consumption + t

        for d2d in range(dl['numD2D']):
            if dl['powerD2DList'][d2d] != 0:
                count = 1
                for tx in range(dl['numD2D']):
                    # print(ul['i_d2d'][d2d]['d2d'])
                    if d2d != tx and tx in ul['i_d2d'][d2d]['d2d'] and dl['powerD2DList'][tx] != 0:
                        count = count + 1
                        # print(count)
                t = (dl['throughput'] / dl['watt_list'][d2d]) / count
                consumption = consumption + t

    # MaxThroughput = (((MaxThroughput / totalTime) * 1000) / 1e6) 
    throughput = (((throughput / totalTime)* 1000) / 1e6) 
    assignment = (assignment / totalTime)  / 2
    non_assignment = ul['numD2D'] - assignment
    percent_assignment = assignment / ul['numD2D']
    percent_nonsaaignment = non_assignment / ul['numD2D']
    distance = (distance / totalTime) 
    # consumption = (throughput / (loss / totalTime)) / distance
    consumption = (consumption / 2) / totalTime / 1000
    fairness = fairness / totalTime / 2
    non_fairness = non_fairness / totalTime

    data = ['numD2D', 'numCUE', 'maxReciver']
    if sys.argv[3] in data:
        f = open("./result/method", 'a')
        f.write("simulation time {} {} {} {} throughput {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], throughput))
        f.write("simulation time {} {} {} {} consumption {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], consumption))
        f.write("simulation time {} {} {} {} assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], assignment))
        f.write("simulation time {} {} {} {} percent_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], percent_assignment))
        f.write("simulation time {} {} {} {} non_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], non_assignment))
        f.write("simulation time {} {} {} {} percent_nonsaaignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], percent_nonsaaignment))
        f.write("simulation time {} {} {} {} fairness {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], fairness))
        f.write("simulation time {} {} {} {} non_fairness {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], non_fairness))
        f.write("simulation time {} {} {} {} distance {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], distance))
        f.write("simulation time {} {} {} {} loss {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], loss))

    # f = open("./result/method",'a')
    # f.write("simulation time {} ".format(totalTime))
    # f.write("{} {} {}\n".format(sys.argv[3], sys.argv[4], throughput))

def j(totalTime):
    throughput = 0
    loss = 0
    distance = 0
    assignment = 0
    fairness = 0
    non_fairness = 0
    consumption = 0
    for ms in range(1, totalTime+1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        ul = generator_ul.get_ul_system_info(ms, **ul)
        ul = juad.maximum_matching(**ul)

        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        dl = generator_dl.get_dl_system_info(ms, **dl)
        dl = juad.maximum_matching(**dl)
        
        MaxThroughput = TotalThroughput = 0
        MaxThroughput = np.int64(MaxThroughput)
        TotalThroughput = np.int64(TotalThroughput)
        count = 0
        for d2d in range(ul['numD2D']):
            if ul['powerD2DList'][d2d] != 0:
                MaxThroughput = MaxThroughput + ul['data_d2d'][d2d]
                TotalThroughput = TotalThroughput + (ul['data_d2d'][d2d]**2)
                count += 1
            else:
                TotalThroughput = TotalThroughput + 0
            if dl['powerD2DList'][d2d] != 0:
                MaxThroughput = MaxThroughput + dl['data_d2d'][d2d]
                TotalThroughput = TotalThroughput + (dl['data_d2d'][d2d]**2)
                count += 1
            else:
                TotalThroughput = TotalThroughput + 0

        MaxThroughput = MaxThroughput**2
        NonTotalThroughput = TotalThroughput * count
        TotalThroughput = TotalThroughput * ul['numD2D']
        fair = MaxThroughput / TotalThroughput
        non_fair = MaxThroughput / NonTotalThroughput

        fairness = fairness + fair
        non_fairness = non_fairness + non_fair
        # MaxThroughput = MaxThroughput + (np.sum(ul['data_d2d']) + np.sum(dl['data_d2d']))
        throughput =  throughput + (ul['throughput'] + dl['throughput'])
        loss = loss + (ul['consumption'] + dl['consumption'])
        assignment = assignment + (ul['numAssignment'] + dl['numAssignment'])
        if ul['interferenceDistance'] == 0 and dl['interferenceDistance'] == 0:
            distance = distance + 1
        else:
            distance = distance + (ul['interferenceDistance'] + dl['interferenceDistance'])

        for d2d in range(ul['numD2D']):
            if ul['powerD2DList'][d2d] != 0:
                count = 1
                for tx in range(ul['numD2D']):
                    # print(ul['i_d2d'][d2d]['d2d'])
                    if d2d != tx and tx in ul['i_d2d'][d2d]['d2d'] and ul['powerD2DList'][tx] != 0:
                        count = count + 1
                        # print(count)
                t = (ul['throughput'] / ul['watt_list'][d2d]) / count
                consumption = consumption + t

        for d2d in range(dl['numD2D']):
            if dl['powerD2DList'][d2d] != 0:
                count = 1
                for tx in range(dl['numD2D']):
                    # print(ul['i_d2d'][d2d]['d2d'])
                    if d2d != tx and tx in ul['i_d2d'][d2d]['d2d'] and dl['powerD2DList'][tx] != 0:
                        count = count + 1
                        # print(count)
                t = (dl['throughput'] / dl['watt_list'][d2d]) / count
                consumption = consumption + t

    # MaxThroughput = (((MaxThroughput / totalTime) * 1000) / 1e6) 
    throughput = (((throughput / totalTime)* 1000) / 1e6) 
    assignment = (assignment / totalTime)  / 2
    non_assignment = ul['numD2D'] - assignment
    percent_assignment = assignment / ul['numD2D']
    percent_nonsaaignment = non_assignment / ul['numD2D']
    distance = (distance / totalTime) 
    # consumption = (throughput / (loss / totalTime)) / distance
    consumption = (consumption / 2) / totalTime / 1000
    fairness = fairness / totalTime / 2
    non_fairness = non_fairness / totalTime

    data = ['numD2D', 'numCUE', 'maxReciver']
    if sys.argv[3] in data:
        f = open("./result/juad", 'a')
        f.write("simulation time {} {} {} {} throughput {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], throughput))
        f.write("simulation time {} {} {} {} consumption {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], consumption))
        f.write("simulation time {} {} {} {} assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], assignment))
        f.write("simulation time {} {} {} {} percent_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], percent_assignment))
        f.write("simulation time {} {} {} {} non_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], non_assignment))
        f.write("simulation time {} {} {} {} percent_nonsaaignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], percent_nonsaaignment))
        f.write("simulation time {} {} {} {} fairness {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], fairness))
        f.write("simulation time {} {} {} {} distance {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], distance))
        f.write("simulation time {} {} {} {} loss {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], loss))

    # f = open("./result/juad",'a')
    # f.write("simulation time {} ".format(totalTime))
    # f.write("{} {} {}\n".format(sys.argv[3], sys.argv[4], throughput))


def g(totalTime):
    throughput = 0
    loss = 0
    distance = 0
    assignment = 0
    fairness = 0
    non_fairness = 0
    consumption = 0
    for ms in range(1, totalTime+1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        ul = generator_ul.get_ul_system_info(ms, **ul)
        ul.update({'check_value' : False})
        ul = gcrs.vertex_coloring(**ul)

        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        dl = generator_dl.get_dl_system_info(ms, **dl)
        dl.update({'check_value' : False})
        dl = gcrs.vertex_coloring(**dl)

        MaxThroughput = TotalThroughput = 0
        MaxThroughput = np.int64(MaxThroughput)
        TotalThroughput = np.int64(TotalThroughput)
        count = 0
        for d2d in range(ul['numD2D']):
            if ul['powerD2DList'][d2d] != 0:
                MaxThroughput = MaxThroughput + ul['data_d2d'][d2d]
                TotalThroughput = TotalThroughput + (ul['data_d2d'][d2d]**2)
                count += 1
            else:
                TotalThroughput = TotalThroughput + 0
            if dl['powerD2DList'][d2d] != 0:
                MaxThroughput = MaxThroughput + dl['data_d2d'][d2d]
                TotalThroughput = TotalThroughput + (dl['data_d2d'][d2d]**2)
                count += 1
            else:
                TotalThroughput = TotalThroughput + 0

        MaxThroughput = MaxThroughput**2
        NonTotalThroughput = TotalThroughput * count
        TotalThroughput = TotalThroughput * ul['numD2D']
        fair = MaxThroughput / TotalThroughput
        non_fair = MaxThroughput / NonTotalThroughput

        fairness = fairness + fair
        non_fairness = non_fairness + non_fair
        # MaxThroughput = MaxThroughput + (np.sum(ul['data_d2d']) + np.sum(dl['data_d2d']))
        throughput =  throughput + (ul['throughput'] + dl['throughput'])
        loss = loss + (ul['consumption'] + dl['consumption'])
        assignment = assignment + (ul['numAssignment'] + dl['numAssignment'])
        if ul['interferenceDistance'] == 0 and dl['interferenceDistance'] == 0:
            distance = distance + 1
        else:
            distance = distance + (ul['interferenceDistance'] + dl['interferenceDistance'])

        for d2d in range(ul['numD2D']):
            if ul['powerD2DList'][d2d] != 0:
                count = 1
                for tx in range(ul['numD2D']):
                    # print(ul['i_d2d'][d2d]['d2d'])
                    if d2d != tx and tx in ul['i_d2d'][d2d]['d2d'] and ul['powerD2DList'][tx] != 0:
                        count = count + 1
                        # print(count)
                t = (ul['throughput'] / ul['watt_list'][d2d]) / count
                consumption = consumption + t

        for d2d in range(dl['numD2D']):
            if dl['powerD2DList'][d2d] != 0:
                count = 1
                for tx in range(dl['numD2D']):
                    # print(ul['i_d2d'][d2d]['d2d'])
                    if d2d != tx and tx in ul['i_d2d'][d2d]['d2d'] and dl['powerD2DList'][tx] != 0:
                        count = count + 1
                        # print(count)
                t = (dl['throughput'] / dl['watt_list'][d2d]) / count
                consumption = consumption + t

    # MaxThroughput = (((MaxThroughput / totalTime) * 1000) / 1e6) 
    throughput = (((throughput / totalTime)* 1000) / 1e6) 
    assignment = (assignment / totalTime)  / 2
    non_assignment = ul['numD2D'] - assignment
    percent_assignment = assignment / ul['numD2D']
    percent_nonsaaignment = non_assignment / ul['numD2D']
    distance = (distance / totalTime) 
    # consumption = (throughput / (loss / totalTime)) / distance
    consumption = (consumption / 2) / totalTime / 1000
    fairness = fairness / totalTime / 2
    non_fairness = non_fairness / totalTime

    data = ['numD2D', 'numCUE', 'maxReciver']
    if sys.argv[3] in data:
        f = open("./result/gcrs", 'a')
        f.write("simulation time {} {} {} {} throughput {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], throughput))
        f.write("simulation time {} {} {} {} consumption {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], consumption))
        f.write("simulation time {} {} {} {} assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], assignment))
        f.write("simulation time {} {} {} {} percent_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], percent_assignment))
        f.write("simulation time {} {} {} {} non_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], non_assignment))
        f.write("simulation time {} {} {} {} percent_nonsaaignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], percent_nonsaaignment))
        f.write("simulation time {} {} {} {} fairness {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], fairness))
        f.write("simulation time {} {} {} {} non_fairness {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], non_fairness))
        f.write("simulation time {} {} {} {} distance {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], distance))
        f.write("simulation time {} {} {} {} loss {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], loss))

    # f = open("./result/gcrs",'a')
    # f.write("simulation time {} ".format(totalTime))
    # f.write("{} {} {}\n".format(sys.argv[3], sys.argv[4], throughput))

def y(totalTime):
    throughput = 0
    loss = 0
    distance = 0
    assignment = 0
    fairness = 0
    non_fairness = 0
    consumption = 0
    for ms in range(1, totalTime+1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        ul = generator_ul.get_ul_system_info(ms, **ul)
        ul = greedy.greedy(**ul)

        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        dl = generator_dl.get_dl_system_info(ms, **dl)
        dl = greedy.greedy(**dl)
        
        MaxThroughput = TotalThroughput = 0
        MaxThroughput = np.int64(MaxThroughput)
        TotalThroughput = np.int64(TotalThroughput)
        count = 0
        for d2d in range(ul['numD2D']):
            if ul['powerD2DList'][d2d] != 0:
                MaxThroughput = MaxThroughput + ul['data_d2d'][d2d]
                TotalThroughput = TotalThroughput + (ul['data_d2d'][d2d]**2)
                count += 1
            else:
                TotalThroughput = TotalThroughput + 0
            if dl['powerD2DList'][d2d] != 0:
                MaxThroughput = MaxThroughput + dl['data_d2d'][d2d]
                TotalThroughput = TotalThroughput + (dl['data_d2d'][d2d]**2)
                count += 1
            else:
                TotalThroughput = TotalThroughput + 0

        MaxThroughput = MaxThroughput**2
        NonTotalThroughput = TotalThroughput * count
        TotalThroughput = TotalThroughput * ul['numD2D']
        fair = MaxThroughput / TotalThroughput
        non_fair = MaxThroughput / NonTotalThroughput

        fairness = fairness + fair
        non_fairness = non_fairness + non_fair
        # MaxThroughput = MaxThroughput + (np.sum(ul['data_d2d']) + np.sum(dl['data_d2d']))
        throughput =  throughput + (ul['throughput'] + dl['throughput'])
        loss = loss + (ul['consumption'] + dl['consumption'])
        assignment = assignment + (ul['numAssignment'] + dl['numAssignment'])
        if ul['interferenceDistance'] == 0 and dl['interferenceDistance'] == 0:
            distance = distance + 1
        else:
            distance = distance + (ul['interferenceDistance'] + dl['interferenceDistance'])

        for d2d in range(ul['numD2D']):
            if ul['powerD2DList'][d2d] != 0:
                count = 1
                for tx in range(ul['numD2D']):
                    # print(ul['i_d2d'][d2d]['d2d'])
                    if d2d != tx and tx in ul['i_d2d'][d2d]['d2d'] and ul['powerD2DList'][tx] != 0:
                        count = count + 1
                        # print(count)
                t = (ul['throughput'] / ul['watt_list'][d2d]) / count
                consumption = consumption + t

        for d2d in range(dl['numD2D']):
            if dl['powerD2DList'][d2d] != 0:
                count = 1
                for tx in range(dl['numD2D']):
                    # print(ul['i_d2d'][d2d]['d2d'])
                    if d2d != tx and tx in ul['i_d2d'][d2d]['d2d'] and dl['powerD2DList'][tx] != 0:
                        count = count + 1
                        # print(count)
                t = (dl['throughput'] / dl['watt_list'][d2d]) / count
                consumption = consumption + t

    # MaxThroughput = (((MaxThroughput / totalTime) * 1000) / 1e6) 
    throughput = (((throughput / totalTime)* 1000) / 1e6) 
    assignment = (assignment / totalTime)  / 2
    non_assignment = ul['numD2D'] - assignment
    percent_assignment = assignment / ul['numD2D']
    percent_nonsaaignment = non_assignment / ul['numD2D']
    distance = (distance / totalTime) 
    # consumption = (throughput / (loss / totalTime)) / distance
    consumption = (consumption / 2) / totalTime / 1000
    fairness = fairness / totalTime / 2
    non_fairness = non_fairness / totalTime

    data = ['numD2D', 'numCUE', 'maxReciver']
    if sys.argv[3] in data:
        f = open("./result/greedy", 'a')
        f.write("simulation time {} {} {} {} throughput {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], throughput))
        f.write("simulation time {} {} {} {} consumption {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], consumption))
        f.write("simulation time {} {} {} {} assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], assignment))
        f.write("simulation time {} {} {} {} percent_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], percent_assignment))
        f.write("simulation time {} {} {} {} non_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], non_assignment))
        f.write("simulation time {} {} {} {} percent_nonsaaignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], percent_nonsaaignment))
        f.write("simulation time {} {} {} {} fairness {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], fairness))
        f.write("simulation time {} {} {} {} non_fairness {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], non_fairness))
        f.write("simulation time {} {} {} {} distance {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], distance))
        f.write("simulation time {} {} {} {} loss {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], loss))

    # f = open("./result/greedy",'a')
    # f.write("simulation time {} ".format(totalTime))
    # f.write("{} {} {}\n".format(sys.argv[3], sys.argv[4], throughput))

def test(totalTime):
    t_m = t_j = t_g = t_k = 0
    l_m = l_j = l_g = l_k = 0
    d_m = d_j = d_g = d_k = 0
    a_m = a_j = a_g = a_k = 0
    f_m = f_j = f_g = f_k = 0
    for ms in range(1, totalTime+1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        data_ul = generator_ul.get_data_ul(ms)
        # MaxThroughput = MaxThroughput + np.sum(data_ul['data_d2d'])
        ul = {**ul, **data_ul}
        ul = generator_ul.data_to_alloc_ul(**ul)
        ul.update({'check_value' : False})
        
        m_ul = mGreedy.mGreedy(**ul)
        j_ul = juad.maximum_matching(**ul)
        g_ul = gcrs.vertex_coloring(**ul)
        k_ul = greedy.greedy(**ul)


        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        data_dl = generator_dl.get_data_dl(ms)
        # MaxThroughput = MaxThroughput + np.sum(data_dl['data_d2d'])
        dl = {**dl, **data_dl}
        dl = generator_dl.data_to_alloc_dl(**dl)
        dl.update({'check_value' : False})
        
        m_dl = mGreedy.mGreedy(**dl)
        j_dl = juad.maximum_matching(**dl)
        g_dl = gcrs.vertex_coloring(**dl)
        k_dl = greedy.greedy(**dl)

        M_m = M_j = M_g = M_k = T_m = T_j = T_g = T_k = 0
        T_m = np.int64(T_m)
        T_j = np.int64(T_j)
        T_g = np.int64(T_g)
        T_k = np.int64(T_k)
        for d2d in range(ul['numD2D']):
            if m_ul['powerD2DList'][d2d] != 0:
                M_m = M_m + m_ul['data_d2d'][d2d]
                T_m = T_m + m_ul['data_d2d'][d2d]**2
            if m_dl['powerD2DList'][d2d] != 0:
                M_m = M_m + m_dl['data_d2d'][d2d]
                T_m = T_m + m_dl['data_d2d'][d2d]**2
            
            if j_ul['powerD2DList'][d2d] != 0:
                M_j = M_j + j_ul['data_d2d'][d2d]
                T_j = T_j + j_ul['data_d2d'][d2d]**2
            if j_dl['powerD2DList'][d2d] != 0:
                M_j = M_j + j_dl['data_d2d'][d2d]
                T_j = T_j + j_dl['data_d2d'][d2d]**2

            if g_ul['powerD2DList'][d2d] != 0:
                M_g = M_g + g_ul['data_d2d'][d2d]
                T_g = T_g + g_dl['data_d2d'][d2d]**2
            if g_dl['powerD2DList'][d2d] != 0:
                M_g = M_g + g_dl['data_d2d'][d2d]
                T_g = T_g + g_dl['data_d2d'][d2d]**2
            
            if k_ul['powerD2DList'][d2d] != 0:
                M_k = M_k + k_ul['data_d2d'][d2d]
                T_k = T_k + k_dl['data_d2d'][d2d]**2
            if k_dl['powerD2DList'][d2d] != 0:
                M_k = M_k + k_dl['data_d2d'][d2d]
                T_k = T_k + k_dl['data_d2d'][d2d]**2

        M_m = M_m ** 2
        M_j = M_j ** 2
        M_g = M_g ** 2
        M_k = M_k ** 2

        m = M_m / T_m
        j = M_j / T_j
        g = M_g / T_g
        k = M_k / T_k
        # print(fair)
        f_m = f_m + m
        f_j = f_j + j
        f_g = f_g + g
        f_k = f_k + k

        t_m =  t_m + (m_ul['throughput'] + m_dl['throughput'])
        t_j =  t_j + (j_ul['throughput'] + j_dl['throughput'])
        t_g =  t_g + (g_ul['throughput'] + g_dl['throughput'])
        t_k =  t_k + (k_ul['throughput'] + k_dl['throughput'])

        l_m = l_m + (m_ul['consumption'] + m_ul['consumption'])
        l_j = l_j + (j_dl['consumption'] + j_dl['consumption'])
        l_g = l_g + (g_ul['consumption'] + g_dl['consumption'])
        l_k = l_k + (k_ul['consumption'] + k_ul['consumption'])
        
        a_m = a_m + (m_ul['numAssignment'] + m_dl['numAssignment'])
        a_j = a_j + (j_ul['numAssignment'] + j_dl['numAssignment'])
        a_g = a_g + (g_ul['numAssignment'] + g_dl['numAssignment'])
        a_k = a_k + (k_ul['numAssignment'] + k_dl['numAssignment'])

        d_m = d_m + (m_ul['interferenceDistance'] + m_ul['interferenceDistance'])
        d_j = d_j + (j_ul['interferenceDistance'] + j_ul['interferenceDistance'])
        d_g = d_g + (g_dl['interferenceDistance'] + g_dl['interferenceDistance'])
        d_k = d_k + (k_ul['interferenceDistance'] + k_ul['interferenceDistance'])

    # MaxThroughput = (((MaxThroughput / totalTime) * 1000) / 1e6) / 2
    t_m = (((t_m / totalTime)* 1000) / 1e6) / 2
    t_j = (((t_j / totalTime)* 1000) / 1e6) / 2
    t_g = (((t_g / totalTime)* 1000) / 1e6) / 2
    t_k = (((t_k / totalTime)* 1000) / 1e6) / 2
    
    # f_m = t_m / MaxThroughput
    # f_j = t_j / MaxThroughput
    # f_g = t_g / MaxThroughput
    # f_k = t_k / MaxThroughput

    # print(f_m)
    # print(f_k)
    # print(f_j)
    # print(f_g)
    
    

    l_m = l_m / 2
    l_j = l_j / 2
    l_g = l_g / 2
    l_k = l_k / 2
    
    a_m = (a_m / totalTime) / 2
    a_j = (a_j / totalTime) / 2
    a_g = (a_g / totalTime) / 2
    a_k = (a_k / totalTime) / 2

    n_m = ul['numD2D'] - a_m
    n_j = ul['numD2D'] - a_j
    n_g = ul['numD2D'] - a_g
    n_k = ul['numD2D'] - a_k
    
    p_m = a_m / ul['numD2D']
    p_j = a_j / ul['numD2D']
    p_g = a_g / ul['numD2D']
    p_k = a_k / ul['numD2D']

    pn_m = n_m / ul['numD2D']
    pn_j = n_j / ul['numD2D']
    pn_g = n_g / ul['numD2D']
    pn_k = n_k / ul['numD2D']

    d_m = (d_m / totalTime) / 2
    d_j = (d_j / totalTime) / 2
    d_g = (d_g / totalTime) / 2
    d_k = (d_k / totalTime) / 2
    
    c_m = (t_m / (l_m / totalTime)) / d_m
    c_j = (t_j / (l_j / totalTime)) / d_j
    c_g = (t_g / (l_g / totalTime)) / d_g
    c_k = (t_k / (l_k / totalTime)) / d_k

    f_m = f_m / totalTime
    f_j = f_j / totalTime
    f_g = f_g / totalTime
    f_k = f_k / totalTime

    print(f_m)
    print(f_j)
    print(f_g)
    print(f_k)

    data = ['numD2D', 'numCUE', 'maxReciver']
    if sys.argv[3] in data:
        f = open("./result/raw_data", 'a')
        
        f.write("simulation time {} {} {} {} method throughput {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], t_m))
        f.write("simulation time {} {} {} {} method consumption {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], c_m))
        f.write("simulation time {} {} {} {} method assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], a_m))
        f.write("simulation time {} {} {} {} method percent_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], p_m))
        f.write("simulation time {} {} {} {} method non_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], n_m))
        f.write("simulation time {} {} {} {} method percent_nonsaaignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], pn_m))
        f.write("simulation time {} {} {} {} method distance {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], d_m))
        f.write("simulation time {} {} {} {} method loss {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], l_m))
        
        f.write("simulation time {} {} {} {} greedy throughput {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], t_k))
        f.write("simulation time {} {} {} {} greedy consumption {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], c_k))
        f.write("simulation time {} {} {} {} greedy assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], a_k))
        f.write("simulation time {} {} {} {} greedy percent_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], p_k))
        f.write("simulation time {} {} {} {} greedy non_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], n_k))
        f.write("simulation time {} {} {} {} greedy percent_nonsaaignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], pn_k))
        f.write("simulation time {} {} {} {} greedy distance {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], d_k))
        f.write("simulation time {} {} {} {} greedy loss {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], l_k))

        f.write("simulation time {} {} {} {} juad throughput {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], t_j))
        f.write("simulation time {} {} {} {} juad consumption {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], c_j))
        f.write("simulation time {} {} {} {} juad assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], a_j))
        f.write("simulation time {} {} {} {} juad percent_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], p_j))
        f.write("simulation time {} {} {} {} juad non_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], n_j))
        f.write("simulation time {} {} {} {} juad percent_nonsaaignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], pn_j))
        f.write("simulation time {} {} {} {} juad distance {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], d_j))
        f.write("simulation time {} {} {} {} juad loss {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], l_j))

        f.write("simulation time {} {} {} {} gcrs throughput {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], t_g))
        f.write("simulation time {} {} {} {} gcrs consumption {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], c_g))
        f.write("simulation time {} {} {} {} gcrs assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], a_g))
        f.write("simulation time {} {} {} {} gcrs percent_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], p_g))
        f.write("simulation time {} {} {} {} gcrs non_assignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], n_g))
        f.write("simulation time {} {} {} {} gcrs percent_nonsaaignment {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], pn_g))
        f.write("simulation time {} {} {} {} gcrs distance {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], d_g))
        f.write("simulation time {} {} {} {} gcrs loss {}\n".format(totalTime, sys.argv[1], sys.argv[3], sys.argv[4], l_g))
        
if __name__ == '__main__':
    simulation_time = int(sys.argv[2])

    generator_ul = initial_info.Initial(sys.argv)
    ul = generator_ul.initial_ul()
    data_ul = generator_ul.get_data_ul(simulation_time)
    ul = {**ul, **data_ul}
    ul = generator_ul.data_to_alloc_ul(**ul)
    ul.update({'check_value' : False})

    generator_dl = initial_info.Initial(sys.argv)
    dl = generator_dl.initial_dl()
    data_dl = generator_dl.get_data_dl(simulation_time)
    dl = {**dl, **data_dl}
    dl = generator_dl.data_to_alloc_dl(**dl)
    dl.update({'check_value' : False})

    if sys.argv[1] == "method":
        m(simulation_time)
    elif sys.argv[1] == "juad":
        j(simulation_time)
    elif sys.argv[1] == "gcrs":
        g(simulation_time)
    elif sys.argv[1] == "greedy":
        y(simulation_time)
    elif sys.argv[1] == "test":
        test(simulation_time)