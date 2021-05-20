import numpy as np
import tools
import method

def mGreedy(**parameter):
    tool = tools.Tool()
    parameter = method.initial_parameter(**parameter)
    parameter = method.phase1(**parameter)
    greedy(**parameter)


def greedy(**parameter):
    sortD2D = np.copy(parameter['priority_sort_index'])
    nStartD2D = parameter['nStartD2D'].copy()
    candicate = sortD2D[np.in1d(sortD2D, nStartD2D)]
    
    while candicate.size > 0:
        root = candicate[0]
        

import initial_info
import sys
generator_ul = initial_info.Initial(sys.argv)
ul = generator_ul.initial_ul()
ul = generator_ul.get_ul_system_info(1, **ul)
ul = mGreedy(**ul)