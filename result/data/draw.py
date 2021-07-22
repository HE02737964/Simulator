import numpy as np
import matplotlib.pyplot as plt

def draw_simulation():
    simulation_file_dict = ['method', 'greedy', 'juad', 'gcrs']
    style_list = ['s-', 'o-', '^-', 'd-']
    label_list = ['DS'+r'$^2$', 'KNAP', 'JUAD', 'GCRS']

    input_file_name_dict = {
        0: 'numD2D', 1: 'maxReciver', 2: 'numCUE'
    }

    label_dict = {
        0: 'throughput', 1: 'consumption', 2: 'assignment', 3: 'percent_assignment', 
        4: 'non_assignment', 5: 'percent_nonsaaignment', 6: 'fairness' 
    }

    output_file_name_dict = { 
        0: "sim_d2d_throughput", 1: "sim_d2d_energy", 2: "sim_d2d_assignment", 3: 'sim_d2d_percent_assignment',
        4: 'sim_d2d_non_assignment', 5: 'sim_d2d_percent_nonsaaignment', 6: 'sim_d2d_fairness',
        7: "sim_rx_throughput", 8: "sim_rx_energy", 9: "sim_rx_assignment", 10: 'sim_rx_percent_assignment',
        11: 'sim_rx_non_assignment', 12: 'sim_rx_percent_nonsaaignment', 13: 'sim_rx_fairness',
        14: "sim_cue_throughp1ut", 15: "sim_cue_energy", 16: "sim_cue_assignment", 17: 'sim_cue_percent_assignment',
        18: 'sim_cue_non_assignment', 19: 'sim_cue_percent_nonsaaignment', 20: 'sim_cue_fairness',
    }

    x_label_name_dict = {
        0: 'Number of D2D groups', 1: 'Number of receivers in a D2D group', 2: 'Number of CUEs',
    }

    y_label_name_dict = {
        0: 'D2D group throughput (Mbps)', 1: '(Throughput / Watt) / d', 2: 'Number of supported link',
        3: 'Percentage of supported link', 4: 'Number of non-supported link', 5: 'Percentage of non-supported link',
        6: 'Fairness index'
    }
    
    
    input_key_list = list(input_file_name_dict.keys())
    input_value_list = list(input_file_name_dict.values())

    label_key_list = list(label_dict.keys())
    label_value_list = list(label_dict.values())
    width = [-0.15, -0.05, 0.05, 0.15]
    numRBbar = 4
    numRBarange = np.arange(numRBbar)

    x_temp = [[[] for i in range(len(input_file_name_dict))] for i in range(len(simulation_file_dict)) ]
    x_label = [[[] for i in range(len(input_file_name_dict))] for i in range(len(simulation_file_dict)) ]

    y_temp = [[[[] for i in range(len(label_dict))] for j in range(len(input_file_name_dict))] for k in range(len(simulation_file_dict))]
    y_label = [[[[] for i in range(len(label_dict))] for j in range(len(input_file_name_dict))] for k in range(len(simulation_file_dict))]
    
    for i in range(len(simulation_file_dict)):
        file = open('%s'%simulation_file_dict[i], 'r')

        for data in file:
            result = data.split()
            name = result[3]
            if name in input_value_list:
                pos = input_value_list.index(name)
                index = int(input_key_list[pos])
                if int(result[4]) not in x_temp[i][index]:
                    x_temp[i][index].append(int(result[4]))

                if result[5] in label_value_list:
                    pos = label_value_list.index(result[5])
                    k = int(label_key_list[pos])
                    y_temp[i][index][k].append(float(result[6]))

        for j in range(len(input_file_name_dict)):
            x_label[i][j] = sorted(x_temp[i][j])
            for k in range(len(label_dict)):
                y_label[i][j][k] = [y for x,y in sorted(zip(x_temp[i][j], y_temp[i][j][k]))]

    labelpad = 5
    font_size = 12
    count = 0
    for i in input_file_name_dict:
        x_name = x_label_name_dict[i]
        
        for k in range(len(label_dict)):
            plt.figure()
            for j in range(len(simulation_file_dict)):
                plt.plot(x_label[j][i], y_label[j][i][k], style_list[j], label = label_list[j])
                
            plt.xlabel(x_name, labelpad = labelpad)
            plt.xticks(x_label[0][i])
            plt.ylabel(y_label_name_dict[k], labelpad = 20)
            plt.legend(loc = "best")
            plt.tight_layout()
            plt.savefig('%s.png'%(output_file_name_dict[count]))
            count = count + 1
            # plt.show()
    
draw_simulation()