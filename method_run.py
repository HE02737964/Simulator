# import multiprocessing as mp
import sys
import time
import argparse
import numpy as np
import initial_info
import method
import juad
import gcrs

# parameter = initial_info.get_initial(sys.argv)
# UL = initial_info.initial_ul(**parameter)
# DL = initial_info.initial_dl(**parameter)

def run_method_ul(simu_time):
    exe_time = 0
    t_m = 0
    p_assign = 0
    total = 0
    method_ul = generator.initial_ul()
    # method_ul = UL.copy()
    for cTime in range(simu_time):
        sys.stdout.write("\r")
        progress = int(100 * ((cTime / simu_time)))
        percent = "{:2}".format(progress)
        sys.stdout.write(" " + percent + " % ")
        [sys.stdout.write("#") for x in range(int(cTime / simu_time))]
        sys.stdout.flush()

        # method_ul = initial_info.get_ul_system_info(cTime, **method_ul)
        method_ul = generator.get_ul_system_info(cTime, **method_ul)

        meth_start = time.time()
        method_ul = method.initial_parameter(**method_ul)
        method_ul = method.phase1(**method_ul)
        meth_end = time.time()

        for i in range(method_ul['numD2D']):
            if method_ul['powerD2DList'][i] != 0:
                t_m = t_m + method_ul['data_d2d'][i]
        total = total + np.sum(method_ul['data_d2d'])
        exe_time = exe_time + (meth_end - meth_start)
    p_assign = (method_ul['numAssignment'] / simu_time)
    return exe_time, t_m, (((t_m / simu_time)*1000)/1e6), p_assign, total

def run_method_dl(simu_time):
    exe_time = 0
    t_m = 0
    p_assign = 0
    total = 0
    method_dl = generator.initial_dl()
    for cTime in range(simu_time):
        sys.stdout.write("\r")
        progress = int(100 * ((cTime / simu_time)))
        percent = "{:2}".format(progress)
        sys.stdout.write(" " + percent + " % ")
        [sys.stdout.write("#") for x in range(int(cTime / simu_time))]
        sys.stdout.flush()

        method_dl = generator.get_dl_system_info(cTime, **method_dl)

        meth_start = time.time()
        method_dl = method.initial_parameter(**method_dl)
        method_dl = method.phase1(**method_dl)
        meth_end = time.time()
        
        for i in range(method_dl['numD2D']):
            if method_dl['powerD2DList'][i] != 0:
                t_m = t_m + method_dl['data_d2d'][i]
        total = total + np.sum(method_dl['data_d2d'])
        # p_assign = p_assign + method_dl['numAssignment']
        exe_time = exe_time + (meth_end - meth_start)
    p_assign = (method_dl['numAssignment'] / simu_time)
    return exe_time, t_m, (((t_m / simu_time)*1000)/1e6), p_assign, total

# ------------------------------------------------------------------------------------

def run_juad_ul(simu_time):
    exe_time = 0
    juad_throughput = 0
    j_assign = 0
    juad_ul = generator.initial_ul()
    for cTime in range(simu_time):
        sys.stdout.write("\r")
        progress = int(100 * ((cTime / simu_time)))
        percent = "{:2}".format(progress)
        sys.stdout.write(" " + percent + " % ")
        [sys.stdout.write("#") for x in range(int(cTime / simu_time))]
        sys.stdout.flush()
        
        juad_ul = generator.get_ul_system_info(cTime, **juad_ul)

        juad_start = time.time()
        juad_ul = juad.initial_parameter(**juad_ul)
        juad_ul = juad.maximum_matching(**juad_ul)
        juad_end = time.time()

        assignmentD2D = [i[0] for i in juad_ul['matching_index']]
        assignmentCUE = [i[1] for i in juad_ul['matching_index']]

        for i in range(len(assignmentCUE)):
            if juad_ul['powerCUEList'][i][assignmentCUE[i]] != 0 and juad_ul['powerD2DList'][i][assignmentCUE[i]] != 0:
                j_assign = j_assign + 1
                juad_throughput = juad_throughput + juad_ul['weight_d2d'][i][assignmentCUE[i]]
    
        exe_time = exe_time + (juad_end - juad_start)
    j_assign = j_assign / simu_time
    return exe_time, juad_throughput, (((juad_throughput / simu_time)*1000)/1e6), j_assign

def run_juad_dl(simu_time):
    exe_time = 0
    juad_throughput = 0
    j_assign = 0
    juad_dl = generator.initial_dl()
    for cTime in range(simu_time):
        sys.stdout.write("\r")
        progress = int(100 * ((cTime / simu_time)))
        percent = "{:2}".format(progress)
        sys.stdout.write(" " + percent + " % ")
        [sys.stdout.write("#") for x in range(int(cTime / simu_time))]
        sys.stdout.flush()
        
        juad_dl = generator.get_dl_system_info(cTime, **juad_dl)

        juad_start = time.time()
        juad_dl = juad.initial_parameter(**juad_dl)
        juad_dl = juad.maximum_matching(**juad_dl)
        juad_end = time.time()

        assignmentD2D = [i[0] for i in juad_dl['matching_index']]
        assignmentCUE = [i[1] for i in juad_dl['matching_index']]

        for i in range(len(assignmentCUE)):
            if juad_dl['powerCUEList'][i][assignmentCUE[i]] != 0 and juad_dl['powerD2DList'][i][assignmentCUE[i]] != 0:
                j_assign = j_assign + 1
                juad_throughput = juad_throughput + juad_dl['weight_d2d'][i][assignmentCUE[i]]
    
        exe_time = exe_time + (juad_end - juad_start)
    j_assign = j_assign / simu_time
    return exe_time, juad_throughput, (((juad_throughput / simu_time)*1000)/1e6), j_assign

# ----------------------------------------------------------------------------------

def run_gcrs_ul(simu_time):
    exe_time = 0
    gcrs_throughput = 0
    g_assign = 0
    gcrs_ul = generator.initial_ul()
    for cTime in range(simu_time):
        sys.stdout.write("\r")
        progress = int(100 * ((cTime / simu_time)))
        percent = "{:2}".format(progress)
        sys.stdout.write(" " + percent + " % ")
        [sys.stdout.write("#") for x in range(int(cTime / simu_time))]
        sys.stdout.flush()

        gcrs_ul = generator.get_ul_system_info(cTime, **gcrs_ul)

        gcrs_start = time.time()
        gcrs_ul = gcrs.initial_parameter(**gcrs_ul)
        gcrs_ul = gcrs.vertex_coloring(**gcrs_ul)
        gcrs_end = time.time()

        gcrs_throughput = gcrs_throughput + np.sum(gcrs_ul['d2d_total_throughput'])
        # g_assign = g_assign + gcrs_ul['numAssignment']

        exe_time = exe_time + (gcrs_end - gcrs_start)
    g_assign = gcrs_ul['numAssignment'] / simu_time
    return exe_time, gcrs_throughput, (((gcrs_throughput / simu_time)*1000)/1e6), g_assign

def run_gcrs_dl(simu_time):
    exe_time = 0
    gcrs_throughput = 0
    g_assign = 0
    gcrs_dl = generator.initial_dl()
    for cTime in range(simu_time):
        sys.stdout.write("\r")
        progress = int(100 * ((cTime / simu_time)))
        percent = "{:2}".format(progress)
        sys.stdout.write(" " + percent + " % ")
        [sys.stdout.write("#") for x in range(int(cTime / simu_time))]
        sys.stdout.flush()

        gcrs_dl = generator.get_dl_system_info(cTime, **gcrs_dl)

        gcrs_start = time.time()
        gcrs_dl = gcrs.initial_parameter(**gcrs_dl)
        gcrs_dl = gcrs.vertex_coloring(**gcrs_dl)
        gcrs_end = time.time()

        gcrs_throughput = gcrs_throughput + np.sum(gcrs_dl['d2d_total_throughput'])
        # g_assign = g_assign + gcrs_dl['numAssignment']

        exe_time = exe_time + (gcrs_end - gcrs_start)
    g_assign = gcrs_dl['numAssignment'] / simu_time
    return exe_time, gcrs_throughput, (((gcrs_throughput / simu_time)*1000)/1e6), g_assign

# ===============================================================================

def merge(args):
    simu_time = int(args)
    total = 0
    m_throughput = j_throughput = g_throughput = 0
    m_assign = j_assign = g_assign = 0
    m_time = j_time = g_time = 0

    m_ul = generator.initial_ul()
    j_ul = generator.initial_ul()
    g_ul = generator.initial_ul()

    m_dl = generator.initial_dl()
    j_dl = generator.initial_dl()
    g_dl = generator.initial_dl()

    for cTime in range(simu_time):
        sys.stdout.write("\r")
        progress = int(100 * ((cTime / simu_time)))
        percent = "{:2}".format(progress)
        sys.stdout.write(" " + percent + " % ")
        [sys.stdout.write("#") for x in range(int(cTime / simu_time))]
        sys.stdout.flush()
        
        data_ul = generator.get_data_ul(cTime)
        data_dl = generator.get_data_dl(cTime)

        m_ul = {**m_ul, **data_ul}
        j_ul = {**j_ul, **data_ul}
        g_ul = {**g_ul, **data_ul}

        m_dl = {**m_dl, **data_dl}
        j_dl = {**j_dl, **data_dl}
        g_dl = {**g_dl, **data_dl}

        m_ul = generator.data_to_alloc_ul(**m_ul)
        j_ul = generator.data_to_alloc_ul(**j_ul)
        g_ul = generator.data_to_alloc_ul(**g_ul)

        m_dl = generator.data_to_alloc_dl(**m_dl)
        j_dl = generator.data_to_alloc_dl(**j_dl)
        g_dl = generator.data_to_alloc_dl(**g_dl)



        #method ul
        meth_start = time.time()
        m_ul = method.initial_parameter(**m_ul)
        m_ul = method.phase1(**m_ul)
        meth_end = time.time()

        for i in range(m_ul['numD2D']):
            if m_ul['powerD2DList'][i] != 0:
                m_throughput = m_throughput + m_ul['data_d2d'][i]
        total = total + np.sum(m_ul['data_d2d'])
        m_time = m_time + (meth_end - meth_start)

        #juad ul
        juad_start = time.time()
        j_ul = juad.initial_parameter(**j_ul)
        j_ul = juad.maximum_matching(**j_ul)
        juad_end = time.time()
        assignmentD2D = [i[0] for i in j_ul['matching_index']]
        assignmentCUE = [i[1] for i in j_ul['matching_index']]
        for i in range(len(assignmentCUE)):
            if j_ul['powerCUEList'][i][assignmentCUE[i]] != 0 and j_ul['powerD2DList'][i][assignmentCUE[i]] != 0:
                j_assign = j_assign + 1
                j_throughput = j_throughput + j_ul['weight_d2d'][i][assignmentCUE[i]]
        j_time = j_time + (juad_end - juad_start)

        #gcrs ul
        gcrs_start = time.time()
        g_ul = gcrs.initial_parameter(**g_ul)
        g_ul = gcrs.vertex_coloring(**g_ul)
        gcrs_end = time.time()
        g_throughput = g_throughput + np.sum(g_ul['d2d_total_throughput'])
        g_time = g_time + (gcrs_end - gcrs_start)

        #meth dl
        meth_start = time.time()
        m_dl = method.initial_parameter(**m_dl)
        m_dl = method.phase1(**m_dl)
        meth_end = time.time()
        for i in range(m_dl['numD2D']):
            if m_dl['powerD2DList'][i] != 0:
                m_throughput = m_throughput + m_dl['data_d2d'][i]
        total = total + np.sum(m_dl['data_d2d'])
        m_time = m_time + (meth_end - meth_start)

        #juad dl
        juad_start = time.time()
        j_dl = juad.initial_parameter(**j_dl)
        j_dl = juad.maximum_matching(**j_dl)
        juad_end = time.time()
        assignmentD2D = [i[0] for i in j_dl['matching_index']]
        assignmentCUE = [i[1] for i in j_dl['matching_index']]
        for i in range(len(assignmentCUE)):
            if j_dl['powerCUEList'][i][assignmentCUE[i]] != 0 and j_dl['powerD2DList'][i][assignmentCUE[i]] != 0:
                j_assign = j_assign + 1
                j_throughput = j_throughput + j_dl['weight_d2d'][i][assignmentCUE[i]]
        j_time = j_time + (juad_end - juad_start)

        #gcrs dl
        gcrs_start = time.time()
        g_dl = gcrs.initial_parameter(**g_dl)
        g_dl = gcrs.vertex_coloring(**g_dl)
        gcrs_end = time.time()
        g_throughput = g_throughput + np.sum(g_dl['d2d_total_throughput'])
        g_time = g_time + (gcrs_end - gcrs_start)


    m_assign = ((m_ul['numAssignment'] + m_dl['numAssignment']) / simu_time)
    j_assign = j_assign / simu_time
    g_assign = ((g_ul['numAssignment'] + g_dl['numAssignment']) / simu_time)

    m = (((m_throughput / simu_time) * 1000) / 1e6)
    j = (((j_throughput / simu_time) * 1000) / 1e6)
    g = (((g_throughput / simu_time) * 1000) / 1e6)

    Total = (((total/simu_time)*1000)/1e6)
    f = open("file_merge",'a')
    f.write("\n")
    f.write("模擬時間        {} 秒\n".format(simu_time*2/1000))
    f.write("D2D總吞吐量     {} Mbps\n".format(Total))
    
    f.write("\n")
    f.write("Method 執行時間 {} 秒\n".format(m_time))
    f.write("Method 總吞吐量 {} bits\n".format(m_throughput))
    f.write("Method 平均吞吐 {} Mbps\n".format(m))
    f.write("Method 平均排程 {} 個/輪\n".format(m_assign))

    f.write("\n")
    f.write("juad   執行時間 {} 秒\n".format(j_time))
    f.write("juad   總吞吐量 {} bits\n".format(j_throughput))
    f.write("juad   平均吞吐 {} Mbps\n".format(j))
    f.write("juad   平均排程 {} 個/輪\n".format(j_assign))

    f.write("\n")
    f.write("gcrs   執行時間 {} 秒\n".format(g_time))
    f.write("gcrs   總吞吐量 {} bits\n".format(g_throughput))
    f.write("gcrs   平均吞吐 {} Mbps\n".format(g))
    f.write("gcrs   平均排程 {} 個/輪\n".format(g_assign))

    sys.stdout.close()

def m(args):
    simu_time = int(args)
    m_exe_time = 0
    m_total_t = 0
    m_t = 0
    m_assign = 0
    total = 0
    sys.stdout = open('raw_data', 'w')

    m_exe_time_ul, m_total_t_ul, m_t_ul, m_assign_ul, total_ul =  run_method_ul(simu_time)
    m_exe_time_dl, m_total_t_dl, m_t_dl, m_assign_dl, total_dl = run_method_dl(simu_time)

    m_exe_time = m_exe_time_ul + m_exe_time_dl
    m_total_t = m_total_t_ul + m_total_t_dl
    m_t = m_t_ul + m_t_dl
    m_assign = m_assign_ul + m_assign_dl
    total = total_ul + total_dl

    Total = (((total/simu_time)*1000)/1e6)
    f = open("file",'a')
    f.write("模擬時間        {} 毫秒\n".format(simu_time))
    f.write("D2D總吞吐量     {} Mbps\n".format(Total))
    f.write("Method 執行時間 {} 秒\n".format(m_exe_time))
    f.write("Method 總吞吐量 {} bits\n".format(m_total_t))
    f.write("Method 平均吞吐 {} Mbps\n".format(m_t))
    f.write("Method 平均排程 {} 個/輪\n".format(m_assign))
    sys.stdout.close()

def j(args):
    simu_time = int(args)

    m_exe_time = 0
    m_total_t = 0
    m_t = 0
    m_assign = 0

    m_exe_time_ul, m_total_t_ul, m_t_ul, m_assign_ul =  run_juad_ul(simu_time)
    m_exe_time_dl, m_total_t_dl, m_t_dl, m_assign_dl = run_juad_dl(simu_time)

    m_exe_time = m_exe_time_ul + m_exe_time_dl
    m_total_t = m_total_t_ul + m_total_t_dl
    m_t = m_t_ul + m_t_dl
    m_assign = m_assign_ul + m_assign_dl

    f = open("file",'a')
    f.write("juad   執行時間 {} 秒\n".format(m_exe_time))
    f.write("juad   總吞吐量 {} bits\n".format(m_total_t))
    f.write("juad   平均吞吐 {} Mbps\n".format(m_t))
    f.write("juad   平均排程 {} 個/輪\n".format(m_assign))

def g(args):
    simu_time = int(args)

    m_exe_time = 0
    m_total_t = 0
    m_t = 0
    m_assign = 0

    m_exe_time_ul, m_total_t_ul, m_t_ul, m_assign_ul =  run_gcrs_ul(simu_time)
    m_exe_time_dl, m_total_t_dl, m_t_dl, m_assign_dl = run_gcrs_dl(simu_time)

    m_exe_time = m_exe_time_ul + m_exe_time_dl
    m_total_t = m_total_t_ul + m_total_t_dl
    m_t = m_t_ul + m_t_dl
    m_assign = m_assign_ul + m_assign_dl

    f = open("file",'a')
    f.write("gcrs   執行時間 {} 秒\n".format(m_exe_time))
    f.write("gcrs   總吞吐量 {} bits\n".format(m_total_t))
    f.write("gcrs   平均吞吐 {} Mbps\n".format(m_t))
    f.write("gcrs   平均排程 {} 個/輪\n".format(m_assign))

# mm = threading.Thread(target = m)
# jj = threading.Thread(target = j)
# gg = threading.Thread(target = g)

# jj.start()
# gg.start()
# mm.start()


# jj.join()
# gg.join()
# mm.join()

# p = argparse.ArgumentParser()
# subparsers = p.add_subparsers()

# option1_parser = subparsers.add_parser('m')
# # Add specific options for option1 here
# option1_parser.add_argument('param1')
# option1_parser.set_defaults(func=m)

# option2_parser = subparsers.add_parser('j')
# # Add specific options for option1 here
# option2_parser.add_argument('param1')
# option2_parser.set_defaults(func=j)

# option3_parser = subparsers.add_parser('g')
# # Add specific options for option3 here
# option3_parser.add_argument('param1')
# option3_parser.set_defaults(func=g)

# args = p.parse_args()
# args.func(args)

if __name__ == '__main__':
    generator = initial_info.Initial(sys.argv)
    if sys.argv[1] == 'm':
        m(sys.argv[2])
    elif sys.argv[1] == 'j':
        j(sys.argv[2])
    elif sys.argv[1] == 'g':
        g(sys.argv[2])
    elif sys.argv[1] == 't':
        merge(sys.argv[2])