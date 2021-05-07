import numpy as np
import sys
import initial_info
import method
import draw
import time

def flexible(args):
    simu_time = int(args)
    throughput = 0
    for ms in range(1, simu_time + 1):
        generator_ul = initial_info.Initial(sys.argv)
        ul = generator_ul.initial_ul()
        ul = generator_ul.get_ul_system_info(ms, **ul)
        ul = method.phase1(**ul)

        generator_dl = initial_info.Initial(sys.argv)
        dl = generator_dl.initial_dl()
        dl = generator_dl.get_dl_system_info(ms, **dl)
        print('ddd',dl['candicateCUE'])
        print('uuu',dl['inSectorCUE'])
        time.sleep(3)
        dl = method.phase1(**dl)
        
        throughput =  throughput + (ul['throughput'] + dl['throughput'])
    throughput = (((throughput/ simu_time)* 1000) / 1e6)

    f = open("result_",'a')
    f.write("simulation time {} ".format(simu_time))
    f.write("{} {}\n".format(sys.argv[4], throughput))

def fixed(args):
    simu_time = int(args)
    throughput = 0
    generator = initial_info.Initial(sys.argv)
    ul = generator.initial_ul()
    dl = generator.initial_dl()

    for ms in range(1, simu_time + 1):
        ul = generator.get_ul_system_info(ms, **ul)
        ul = method.phase1(**ul)

        dl = generator.get_dl_system_info(ms, **dl)
        dl = method.phase1(**dl)

    # throughput =  throughput + (ul['total_throughput'] + dl['total_throughput'])
    throughput = (ul['total_throughput'] + dl['total_throughput'])
    throughput = (((throughput/ simu_time)* 1000) / 1e6)

    f = open("result_fixed",'a')
    f.write("simulation time {} ".format(simu_time))
    f.write("{} {}\n".format(sys.argv[4], throughput))

if __name__ == '__main__':
    if sys.argv[1] == 'flexible':
        flexible(sys.argv[2])
    elif sys.argv[1] == "fixed":
        fixed(sys.argv[2])