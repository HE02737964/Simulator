# -*- coding: utf-8 -*
import numpy as np
import matplotlib.pyplot as plt
import genrator

def drawCell(**parameter):
    numCUE = len(parameter['ue_point'])
    numD2D = len(parameter['tx_point'])

    text_cue = [i for i in range(numCUE)]
    text_d2d = [i for i in range(numD2D)]

    x0 = 0
    y0 = 0
    theta = np.arange(0, 2*np.pi, 0.01)
    x1 = x0 + parameter['radius'] * np.cos(theta)
    y1 = y0 + parameter['radius'] * np.sin(theta)

    fig = plt.figure()
    axes = fig.add_subplot(111)
    axes.plot(x1, y1, color='blue',)
    axes.set_xlabel("distance (m)")
    axes.set_ylabel("distance (m)")
    axes.axis('equal')

    plt.scatter(0, 0, color="#888888", zorder=1000, s=8, label="BS")

    #Draw CUE
    plotted = 0
    for i in range(numCUE):
        if plotted == 0:
            plt.scatter(parameter['ue_point'][i][0], parameter['ue_point'][i][1], color="#FF00FF", zorder=1000, s=6, label="CUE")
            plotted = 1
        else:
            plt.scatter(parameter['ue_point'][i][0], parameter['ue_point'][i][1], color="#FF00FF", zorder=1000, s=6)

    for i, txt in enumerate(text_cue):
        plt.annotate(txt, (parameter['ue_point'][i][0], parameter['ue_point'][i][1]))

    #Draw D2D
    plotted = 0
    for i in range(numD2D):
        for j in range(parameter['numD2DReciver'][i]):
            t,r = (parameter['tx_point'][i][0], parameter['tx_point'][i][1]), (parameter['rx_point'][i][j][0],parameter['rx_point'][i][j][1])

            p1 = np.asarray(t)  
            p2 = np.asarray(r)
            alphas = np.arange(0, 1, 1 / 100)
            diff = p2 - p1
            line = [(p1 + (alpha * diff)) for alpha in alphas]

            if(plotted == 0):
                plt.scatter(t[0], t[1], color="red", zorder=1000, s=8, label="D2D Transmitter")
                plt.scatter(r[0], r[1], color="green", zorder=1000, s=8, label="D2D Receiver")
                xx, yy = zip(*line)
                plt.plot(xx, yy, color="#888888", zorder = 999, linewidth=1)
                plotted = 1
            else:
                plt.scatter(t[0], t[1], color="red", zorder=1000, s=8)
                plt.scatter(r[0], r[1], color="green", zorder=1000, s=8)
                xx, yy = zip(*line)
                plt.plot(xx, yy, color="#888888", zorder = 999, linewidth=1)
    axes.legend(loc="upper right")
    plt.show()

def draw_test():
    fixed_values1 = [525.660522 ,633.172286 ,716.835674 ,790.695622 ,782.893444 ,882.143046 ,992.58404 ,1082.217374 ,1056.872718 ,1192.83241]
    fixed_values2 = [525.045466 ,605.994134 ,679.932226 ,731.823092 ,827.03916 ,937.365108 ,1017.964052 ,1083.6777 ,1081.146828 ,1113.770642]
    fixed_value3 = [545.568432, 609.069646, 699.420256, 742.56326, 792.914766, 896.253694, 1002.271784, 985.07623,  1161.31785, 1137.322656]

    fixed_4 = [1174.05856, 1167.25106, 1157.377035, 1161.852825, 1166.323375, 1159.51205, 1154.39687, 1153.701875, 1156.89623, 1145.16863]
    fixed_5 = [1150.178045, 1160.686715, 1152.999155, 1152.425165, 1153.25057, 1148.319175, 1143.83779, 1141.0801, 1145.778955, 1134.79409]

    flexible_1000ms = [511.548636, 593.84806, 666.399189, 736.14967, 808.61329, 880.705499, 941.881326, 1006.75319, 1066.9373400000002, 1134.325642]
    flexible_500ms = [512.703684, 594.1119, 666.460892, 736.471596, 811.089578, 877.036142, 941.380454, 1011.842402, 1067.477328, 1129.793816]
    flexible_500ms_1 = [502.95154, 586.009308, 655.067642, 725.485298, 795.739872, 866.595186, 925.634746, 990.061358, 1051.194132, 1107.092976]
    flexible_1000ms_1 = [504.513089, 586.066517, 655.885513, 723.987047, 796.604173, 864.121465, 925.244553, 991.587952, 1051.021377, 1109.533657]
    
    x_labels = [30, 35, 40, 45,50, 55,60, 65, 70, 75]
    
    # plt.plot(x_labels, fixed_values1,'s-',color = 'r', label="fixed_1")
    # plt.plot(x_labels, fixed_values2,'o-',color = 'g', label="fixed_2")
    # plt.plot(x_labels, flexible_500ms,'^-', color = 'b', label="flexible_500ms")
    # plt.plot(x_labels, flexible_1000ms, 'd-', color = 'k', label="flexible_1000ms")

    # plt.plot(x_labels, fixed_value3,'s-',color = 'r', label="fixed_1")
    # plt.plot(x_labels, flexible_500ms_1,'^-', color = 'b', label="flexible_500ms")
    # plt.plot(x_labels, flexible_1000ms_1, 'd-', color = 'k', label="flexible_1000ms")

    plt.plot(x_labels, fixed_4,'s-',color = 'r', label="fixed_1")
    plt.plot(x_labels, fixed_5,'o-',color = 'g', label="fixed_2")

    # plt.title("Python 畫折線圖(Line chart)範例", x=0.5, y=1.03)

    # 设置刻度字体大小
    # plt.xticks(fontsize=10)

    # plt.yticks(fontsize=10)

    # 標示x軸(labelpad代表與圖片的距離)

    plt.xlabel("D2D pair", labelpad = 15)
    plt.xticks(x_labels)

    # 標示y軸(labelpad代表與圖片的距離)

    plt.ylabel("Throughput (Mbps)", labelpad = 20)

    # 顯示出線條標記位置

    plt.legend(loc = "best")

    plt.tight_layout()
    # 畫出圖片
    plt.savefig("Test.eps")
    plt.show()

def draw_simulation():
    simulation_file_dict = ['method_c', 'greedy', 'juad', 'gcrs_c']
    style_list = ['s-', 'o-', '^-', 'd-']
    label_list = ['DS'+r'$^2$', 'KNAP', 'JUAD', 'GCRS']

    input_file_name_dict = {
        0: 'totalBeam', 1: 'numScheduleBeam', 2: 'numCUE', 3: 'dataD2DMax', 4: 'numD2D',
        5: 'd2dDistance', 6: 'maxReciver', 7: 'numDensity', 8: 'numRB', 9: 'numD2DCluster', 
        10: 'numD2DCluster', 11: 'fiarness'
    }

    output_file_name_dict = { 
        0: "sim_lobes", 1: "sim_schedule_lobes", 2: "sim_cues", 3: "sim_max_data",
        4: "sim_d2d_groups", 5: "sim_d2d_radius", 6: "sim_num_receivers", 
        7: "sim_energy", 8: "sim_total_rb", 9: "sim_num_clusters", 10: "sim_percentage_clusters",
        11: "sim_fairness"
    }

    x_label_name_dict = {
        0: 'Number of analog radio lobes', 1: 'Number of scheduled radio lobes per TTI', 
        2: 'Number of CUEs', 3: 'DUE' + "'s " + 'maximum data amount per TTI (kbits)',
        4: 'Number of D2D groups', 5: 'Maximum radius of a D2D groups (m)', 
        6: 'Number of receivers in a D2D group', 7: 'Number of D2D group',
        8: 'Total RBs', 9: 'Number of clusters', 10: 'Persentage of D2D groups in clusters (%)', 
        11: 'Number of D2D groups'
    }

    y_label_name_dict = {
        0: 'D2D group throughput (Mbps)', 7: '(Throughput / Watt) / d', 11: 'Fairness index'
    }
    
    
    key_list = list(input_file_name_dict.keys())
    value_list = list(input_file_name_dict.values())
    width = [-0.15, -0.05, 0.05, 0.15]
    numRBbar = 4
    numRBarange = np.arange(numRBbar)

    x_temp = [[[] for i in range(len(input_file_name_dict))] for i in range(len(simulation_file_dict)) ]
    x_label = [[[] for i in range(len(input_file_name_dict))] for i in range(len(simulation_file_dict)) ]

    y_temp = [[[] for i in range(len(input_file_name_dict))] for i in range(len(simulation_file_dict)) ]
    y_label = [[[] for i in range(len(input_file_name_dict))] for i in range(len(simulation_file_dict)) ]
    
    for i in range(len(simulation_file_dict)):
        file = open('./result/%s'%simulation_file_dict[i], 'r')
        
        for data in file:
            result = data.split()
            name = result[3]
            if name in value_list:
                pos = value_list.index(name)
                index = int(key_list[pos])
                
                x_temp[i][index].append(int(result[4]))
                y_temp[i][index].append(float(result[5]))
        for j in range(len(input_file_name_dict)):
            y_label[i][j] = [y for x,y in sorted(zip(x_temp[i][j], y_temp[i][j]))]
            x_label[i][j] = sorted(x_temp[i][j])
    
    for i in input_file_name_dict:
        x_name = x_label_name_dict[i]
        
        if i == 3:
            for j in range(len(simulation_file_dict)):
                for data in range(10):
                    x_label[j][i][data] = (float(x_label[j][i][data]) / 1000)

        plt.figure()
        for j in range(len(simulation_file_dict)):
            if i == 8:
                plt.bar(numRBarange + width[j],  y_label[j][i], 0.1, label = label_list[j])
            else:
                plt.plot(x_label[j][i], y_label[j][i], style_list[j], label = label_list[j])
                
        
        labelpad = 5
        font_size = 12

        plt.xlabel(x_name, labelpad = labelpad)
        
        if i == 8:
            plt.xticks(numRBarange, x_label[0][i], fontsize=font_size-2)
        else:
            plt.xticks(x_label[0][i])
        
        if i != 7 and i != 11:
            plt.ylabel(y_label_name_dict[0], labelpad = 20)
        elif i == 7:
            plt.ylabel(y_label_name_dict[i], labelpad=20)
        else:
            plt.ylabel(y_label_name_dict[i], labelpad = 20)

        if i == 0 or i == 1 or i == 11:
            plt.legend(bbox_to_anchor=(0.7,0.9), loc = "upper left")
        elif i == 2:
            plt.legend(bbox_to_anchor=(0.7,0.85), loc = "upper left")
        elif i == 8:
            plt.legend(bbox_to_anchor=(0.675,1), loc = "upper left", prop={'size': 9})
        else:
            plt.legend(loc = "best")
        plt.tight_layout()
        plt.savefig('./result/%s.eps'%(output_file_name_dict[i]))
        plt.show()
    
draw_simulation()