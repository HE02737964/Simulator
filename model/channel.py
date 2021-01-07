from tools.convert  import Convert
import  numpy as np
import  random


class Channel:

    def getCellChannelGain(self, numCUE, CUEposition, numRB):
        rayleighFading = np.random.rayleigh(1, [numCUE, numRB])
        gain = np.zeros([numCUE, numRB]) #CUE Channel gain
        distanceCtoB = list() # Distnce CUE to BS

        for x,y in CUEposition:
            distance = np.sqrt((x**2 + y**2) / 1000 )
            distanceCtoB = np.append(np.asarray(distanceCtoB), distance)
        
        pathLoss = 128.1+37.6*np.log10(distanceCtoB) #path loss in dB
        pathLossScale = Convert.dB_to_mW(pathLoss) #convert path loss to linear scale

        for i in range(numCUE):
            gain[i] = (rayleighFading[i] ** 2) / pathLossScale[i]
        
        return gain