import sys
import initial_info
import method
import mGreedy
import juad
import gcrs
import greedy
import time

def m(totalTime):
    throughput = 0
    for ms in range(1, totalTime+1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        ul = generator_ul.get_ul_system_info(ms, **ul)
        ul = method.proposed(**ul)

        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        dl = generator_dl.get_dl_system_info(ms, **dl)
        dl = method.proposed(**dl)
        
        throughput =  throughput + (ul['throughput'] + dl['throughput'])
    throughput = (((throughput / totalTime)* 1000) / 1e6)

    f = open("./result/method",'a')
    f.write("simulation time {} ".format(totalTime))
    f.write("{} {} {}\n".format(sys.argv[3], sys.argv[4], throughput))

def m_c(totalTime):
    throughput = 0
    for ms in range(1, totalTime+1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        ul = generator_ul.get_ul_system_info(ms, **ul)
        ul = mGreedy.mGreedy(**ul)

        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        dl = generator_dl.get_dl_system_info(ms, **dl)
        dl = mGreedy.mGreedy(**dl)
        
        throughput =  throughput + (ul['throughput'] + dl['throughput'])
    throughput = (((throughput / totalTime)* 1000) / 1e6)

    f = open("./result/method_c",'a')
    f.write("simulation time {} ".format(totalTime))
    f.write("{} {} {}\n".format(sys.argv[3], sys.argv[4], throughput))

def j(totalTime):
    throughput = 0
    for ms in range(1, totalTime+1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        ul = generator_ul.get_ul_system_info(ms, **ul)
        ul = juad.maximum_matching(**ul)

        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        dl = generator_dl.get_dl_system_info(ms, **dl)
        dl = juad.maximum_matching(**dl)
        
        throughput =  throughput + (ul['throughput'] + dl['throughput'])
    throughput = (((throughput / totalTime)* 1000) / 1e6)

    f = open("./result/juad",'a')
    f.write("simulation time {} ".format(totalTime))
    f.write("{} {} {}\n".format(sys.argv[3], sys.argv[4], throughput))

def g(totalTime):
    throughput = 0
    for ms in range(1, totalTime+1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        ul = generator_ul.get_ul_system_info(ms, **ul)
        ul.update({'check_value' : True})
        ul = gcrs.vertex_coloring(**ul)

        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        dl = generator_dl.get_dl_system_info(ms, **dl)
        dl.update({'check_value' : True})
        dl = gcrs.vertex_coloring(**dl)

        throughput =  throughput + (ul['throughput'] + dl['throughput'])
    throughput = (((throughput / totalTime)* 1000) / 1e6)

    f = open("./result/gcrs",'a')
    f.write("simulation time {} ".format(totalTime))
    f.write("{} {} {}\n".format(sys.argv[3], sys.argv[4], throughput))

def g_c(totalTime):
    throughput = 0
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

        throughput =  throughput + (ul['throughput'] + dl['throughput'])
    throughput = (((throughput / totalTime)* 1000) / 1e6)

    f = open("./result/gcrs_noCheck",'a')
    f.write("simulation time {} ".format(totalTime))
    f.write("{} {} {}\n".format(sys.argv[3], sys.argv[4], throughput))

def y(totalTime):
    throughput = 0
    for ms in range(1, totalTime+1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        ul = generator_ul.get_ul_system_info(ms, **ul)
        ul = greedy.greedy(**ul)

        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        dl = generator_dl.get_dl_system_info(ms, **dl)
        dl = greedy.greedy(**dl)
        
        throughput =  throughput + (ul['throughput'] + dl['throughput'])
    throughput = (((throughput / totalTime)* 1000) / 1e6)

    f = open("./result/greedy",'a')
    f.write("simulation time {} ".format(totalTime))
    f.write("{} {} {}\n".format(sys.argv[3], sys.argv[4], throughput))

import copy
def test(totalTime):
    throughput = 0
    for ms in range(1, totalTime+1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        ul = generator_ul.get_ul_system_info(ms, **ul)
        ul.update({'check_value' : False})
        ul = gcrs.test_coloring(**ul)

        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        dl = generator_dl.get_dl_system_info(ms, **dl)
        dl.update({'check_value' : False})
        dl = gcrs.test_coloring(**dl)

        throughput =  throughput + (ul['throughput'] + dl['throughput'])
    throughput = (((throughput / totalTime)* 1000) / 1e6)

    f = open("./result/test",'a')
    f.write("simulation time {} ".format(totalTime))
    f.write("{} {} {}\n".format(sys.argv[3], sys.argv[4], throughput))

if __name__ == '__main__':
    simulation_time = int(sys.argv[2])
    if sys.argv[1] == 'method':
        m(simulation_time)
    elif sys.argv[1] == "method_c":
        m_c(simulation_time)
    elif sys.argv[1] == "juad":
        j(simulation_time)
    elif sys.argv[1] == "gcrs":
        g(simulation_time)
    elif sys.argv[1] == "gcrs_c":
        g_c(simulation_time)
    elif sys.argv[1] == "greedy":
        y(simulation_time)
    elif sys.argv[1] == "test":
        test(simulation_time)