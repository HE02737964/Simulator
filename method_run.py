import threading
import sys
import time
import numpy as np
import initial_info
import method
import juad
import gcrs

parameter = initial_info.get_initial()
UL = initial_info.initial_ul(**parameter)
DL = initial_info.initial_dl(**parameter)


def run_method_ul(**parameter):
    simu_time = 15000
    exe_time = 0
    t_m = 0
    p_assign = 0
    for currentTime in range(simu_time):
        sys.stdout.write("\r")
        # progress = int(100 * ((currentTime / simu_time)))
        # percent = "{:2}".format(progress)
        # sys.stdout.write(" " + percent + " % ")
        # # [sys.stdout.write("#") for x in range(int(currentTime / simu_time))]
        # sys.stdout.flush()

        method_ul = parameter.copy()
        method_ul = initial_info.get_ul_system_info(currentTime, **method_ul)

        meth_start = time.time()
        method_ul = method.initial_parameter(**method_ul)
        method_ul = method.phase1(**method_ul)
        meth_end = time.time()

        for i in range(method_ul['numD2D']):
            if method_ul['powerD2DList'][i] != 0:
                t_m = t_m + method_ul['data_d2d'][i]

        p_assign = p_assign + method_ul['numAssignment']
        exe_time = exe_time + (meth_end - meth_start)

    # sys.stdout = open('file', 'w')
    return exe_time, t_m, (((t_m / simu_time)*1000)/1e6), p_assign
    # sys.stdout.close()

def run_method_dl(**parameter):
    simu_time = 15000
    exe_time = 0
    t_m = 0
    p_assign = 0
    for currentTime in range(simu_time):
        sys.stdout.write("\r")
        # progress = int(100 * ((currentTime / simu_time)))
        # percent = "{:2}".format(progress)
        # sys.stdout.write(" " + percent + " % ")
        # # [sys.stdout.write("#") for x in range(int(currentTime / simu_time))]
        # sys.stdout.flush()

        method_dl = parameter.copy()
        method_dl = initial_info.get_dl_system_info(currentTime, **method_dl)

        meth_start = time.time()
        method_dl = method.initial_parameter(**method_dl)
        method_dl = method.phase1(**method_dl)
        meth_end = time.time()
        
        for i in range(method_dl['numD2D']):
            if method_dl['powerD2DList'][i] != 0:
                t_m = t_m + method_dl['data_d2d'][i]

        p_assign = p_assign + method_dl['numAssignment']
        exe_time = exe_time + (meth_end - meth_start)
        
    # sys.stdout = open('file', 'a')
    return exe_time, t_m, (((t_m / simu_time)*1000)/1e6), p_assign
    # sys.stdout.close()

# ------------------------------------------------------------------------------------

def run_juad_ul(**parameter):
    simu_time = 15000
    exe_time = 0
    juad_throughput = 0
    j_assign = 0
    for currentTime in range(simu_time):
        juad_ul = parameter.copy()
        juad_ul = initial_info.get_ul_system_info(currentTime, **juad_ul)

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
    
    return exe_time, juad_throughput, (((juad_throughput / simu_time)*1000)/1e6), j_assign

def run_juad_dl(**parameter):
    simu_time = 15000
    exe_time = 0
    juad_throughput = 0
    j_assign = 0
    for currentTime in range(simu_time):
        juad_dl = parameter.copy()
        juad_dl = initial_info.get_dl_system_info(currentTime, **juad_dl)

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
    
    return exe_time, juad_throughput, (((juad_throughput / simu_time)*1000)/1e6), j_assign

# ----------------------------------------------------------------------------------

def run_gcrs_ul(**parameter):
    simu_time = 15000
    exe_time = 0
    gcrs_throughput = 0
    g_assign = 0
    for currentTime in range(simu_time):
        gcrs_ul = parameter.copy()
        gcrs_ul = initial_info.get_ul_system_info(currentTime, **gcrs_ul)

        gcrs_start = time.time()
        gcrs_ul = gcrs.initial_parameter(**gcrs_ul)
        gcrs_ul = gcrs.vertex_coloring(**gcrs_ul)
        gcrs_end = time.time()

        gcrs_throughput = gcrs_throughput + np.sum(gcrs_ul['d2d_total_throughput'])
        g_assign = g_assign + gcrs_ul['numAssignment']

        exe_time = exe_time + (gcrs_start - gcrs_end)
    
    return exe_time, gcrs_throughput, (((gcrs_throughput / simu_time)*1000)/1e6), g_assign

def run_gcrs_dl(**parameter):
    simu_time = 15000
    exe_time = 0
    gcrs_throughput = 0
    g_assign = 0
    for currentTime in range(simu_time):
        gcrs_dl = parameter.copy()
        gcrs_dl = initial_info.get_dl_system_info(currentTime, **gcrs_dl)

        gcrs_start = time.time()
        gcrs_dl = gcrs.initial_parameter(**gcrs_dl)
        gcrs_dl = gcrs.vertex_coloring(**gcrs_dl)
        gcrs_end = time.time()

        gcrs_throughput = gcrs_throughput + np.sum(gcrs_dl['d2d_total_throughput'])
        g_assign = g_assign + gcrs_dl['numAssignment']

        exe_time = exe_time + (gcrs_start - gcrs_end)
    
    return exe_time, gcrs_throughput, (((gcrs_throughput / simu_time)*1000)/1e6), g_assign

# ===============================================================================

def m():
    m_exe_time = 0
    m_total_t = 0
    m_t = 0
    m_assign = 0

    m_exe_time_ul, m_total_t_ul, m_t_ul, m_assign_ul =  run_method_ul(**UL)
    m_exe_time_dl, m_total_t_dl, m_t_dl, m_assign_dl = run_method_dl(**DL)

    m_exe_time = m_exe_time_ul + m_exe_time_dl
    m_total_t = m_total_t_ul + m_total_t_dl
    m_t = m_t_ul + m_t_dl
    m_assign = m_assign_ul + m_assign_dl

    f = open("file",'a')
    f.write("Method 執行時間 {} 秒\n".format(m_exe_time))
    f.write("Method 總吞吐量 {} bits\n".format(m_total_t))
    f.write("Method 平均吞吐 {} Mbps\n".format(m_t))
    f.write("Method 平均排程 {} 個/輪\n".format(m_assign))
    
def j():
    m_exe_time = 0
    m_total_t = 0
    m_t = 0
    m_assign = 0

    m_exe_time_ul, m_total_t_ul, m_t_ul, m_assign_ul =  run_juad_ul(**UL)
    m_exe_time_dl, m_total_t_dl, m_t_dl, m_assign_dl = run_juad_dl(**DL)

    m_exe_time = m_exe_time_ul + m_exe_time_dl
    m_total_t = m_total_t_ul + m_total_t_dl
    m_t = m_t_ul + m_t_dl
    m_assign = m_assign_ul + m_assign_dl

    f = open("file",'a')
    f.write("juad   執行時間 {} 秒\n".format(m_exe_time))
    f.write("juad   總吞吐量 {} bits\n".format(m_total_t))
    f.write("juad   平均吞吐 {} Mbps\n".format(m_t))
    f.write("juad   平均排程 {} 個/輪\n".format(m_assign))

def g():
    m_exe_time = 0
    m_total_t = 0
    m_t = 0
    m_assign = 0

    m_exe_time_ul, m_total_t_ul, m_t_ul, m_assign_ul =  run_gcrs_ul(**UL)
    m_exe_time_dl, m_total_t_dl, m_t_dl, m_assign_dl = run_gcrs_dl(**DL)

    m_exe_time = m_exe_time_ul + m_exe_time_dl
    m_total_t = m_total_t_ul + m_total_t_dl
    m_t = m_t_ul + m_t_dl
    m_assign = m_assign_ul + m_assign_dl

    f = open("file",'a')
    f.write("gcrs   執行時間 {} 秒\n".format(m_exe_time))
    f.write("gcrs   總吞吐量 {} bits\n".format(m_total_t))
    f.write("gcrs   平均吞吐 {} Mbps\n".format(m_t))
    f.write("gcrs   平均排程 {} 個/輪\n".format(m_assign))

mm = threading.Thread(target = m)
jj = threading.Thread(target = j)
gg = threading.Thread(target = g)

mm.start()
jj.start()
gg.start()

mm.join()
jj.join()
gg.join()

print('Done')