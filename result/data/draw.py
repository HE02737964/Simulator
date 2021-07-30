import numpy as np
import matplotlib.pyplot as plt

def draw_simulation():
    simulation_file_dict = ['method', 'greedy', 'juad', 'gcrs']
    style_list = ['s-', 'o-', '^-', 'd-']
    label_list = ['DS'+r'$^2$', 'KNAP', 'JUAD', 'GCRS']

    input_file_name_dict = {
        0: 'numD2D', 1: 'maxReciver', 2: 'radius', 3: 'd2dDistance', 4: 'numRB', 5: 'numD2DCluster',
        6: 'numDensity', 
    }

    label_dict = {
        0: 'throughput', 1: 'consumption_c', 2: 'consumption', 3: 'assignment', 4: 'percent_assignment', 
        5: 'non_assignment', 6: 'percent_nonsaaignment', 7: 'fairness', 8: 'non_fairness',
    }

    output_file_category = {
        0: 'd2d', 1: 'rx', 2: 'radius', 3: 'distance', 4: 'bandwidth', 5: 'cluster',
        6: 'density',
    }
    output_file_name_dict = { 
        0: "throughput", 1: "energy_assignment", 2: 'energy_total',
        3: "assignment", 4: 'percent_assignment', 5: 'non_assignment', 
        6: 'percent_nonsaaignment', 7: 'fairness_total', 8: 'fairness_assignment'
    }

    x_label_name_dict = {
        0: 'Number of D2D groups', 1: 'Number of receivers in a D2D group', 2: 'Maximum of cell radius',
        3: 'Radius of a D2D groups (m)', 4: 'Total RBs', 5: 'Number of clusters', 6: 'Persentage of D2D groups in clusters (%)'
    }

    y_label_name_dict = {
        0: 'D2D group throughput (Mbps)', 1: '(Throughput / Watt) / c', 2: 'Throughput / Watt',
        3: 'Number of supported link', 4: 'Percentage of supported link', 5: 'Number of non-supported link', 
        6: 'Percentage of non-supported link', 7: 'Fairness index', 8: 'Fairness index'
    }
    
    
    input_key_list = list(input_file_name_dict.keys())
    input_value_list = list(input_file_name_dict.values())

    label_key_list = list(label_dict.keys())
    label_value_list = list(label_dict.values())

    x_temp = [[[] for i in range(len(input_file_name_dict))] for i in range(len(simulation_file_dict)) ]
    x_label = [[[] for i in range(len(input_file_name_dict))] for i in range(len(simulation_file_dict)) ]

    y_temp = [[[[] for i in range(len(label_dict))] for j in range(len(input_file_name_dict))] for k in range(len(simulation_file_dict))]
    y_label = [[[[] for i in range(len(label_dict))] for j in range(len(input_file_name_dict))] for k in range(len(simulation_file_dict))]
    
    for i in range(len(simulation_file_dict)):
        file = open('%s'%simulation_file_dict[i], 'r')

        for data in file:
            result = data.split()
            name = result[4]
            if name in input_value_list:
                pos = input_value_list.index(name)
                index = int(input_key_list[pos])
                if int(result[5]) not in x_temp[i][index]:
                    x_temp[i][index].append(int(result[5]))

                if result[6] in label_value_list:
                    pos = label_value_list.index(result[6])
                    k = int(label_key_list[pos])
                    y_temp[i][index][k].append(float(result[7]))

        for j in range(len(input_file_name_dict)):
            x_label[i][j] = sorted(x_temp[i][j])
            for k in range(len(label_dict)):
                y_label[i][j][k] = [y for x,y in sorted(zip(x_temp[i][j], y_temp[i][j][k]))]

    width = [-0.15, -0.05, 0.05, 0.15]
    numRBbar = 4
    numRBarange = np.arange(numRBbar)
    labelpad = 5
    font_size = 12
    for i in input_file_name_dict:
        x_name = x_label_name_dict[i]
        for k in range(len(label_dict)):
            output_file = 'sim_' + output_file_category[i] + '_' + output_file_name_dict[k]
            plt.figure()
            for j in range(len(simulation_file_dict)):
                if i == 4:
                    plt.bar(numRBarange + width[j],  y_label[j][i][k], 0.1, label = label_list[j])
                else:
                    plt.plot(x_label[j][i], y_label[j][i][k], style_list[j], label = label_list[j])
                
            plt.xlabel(x_name, labelpad = labelpad)
            
            if i == 4:
                plt.xticks(numRBarange, x_label[0][i], fontsize=font_size-2)
            else:
                plt.xticks(x_label[0][i], fontsize=font_size-2)
            
            plt.ylabel(y_label_name_dict[k], labelpad = 20)
            plt.legend(loc = "best")
            plt.tight_layout()
            plt.savefig('%s.eps'%(output_file))
            plt.close('all')
            # plt.show()
    
draw_simulation()