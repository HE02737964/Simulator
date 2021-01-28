import scenario
import channel
import json
import numpy as np

x = scenario.Genrator()
dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver = x.genrator()
# x.draw_model()
c_x, c_y, d_x, d_y, r_x, r_y = x.get_position()

class Allocate():
    def __init__(self, dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver):
        with open("config.json", "r") as f:
            config = json.load(f)
            f.close()
        
        self.numCUE = config["numCUE"]
        self.numD2D = config["numD2D"]
        self.numRB = config["numRB"]
        self.maxReciver = config["maxReciver"]
        self.radius = config["radius"]
        self.totalBeam = config["totalBeam"]
        self.scheduleBeam = config["scheduleBeam"]
        self.dataMax = config["dataMax"]
        self.dataMin = config["dataMin"]
        
        self.schedule = np.zeros((self.totalBeam, 4))
        x = channel.Channel(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver)
        self.g_b, self.g_d = x.cell_downlink()

        self.scheduleUE = np.full(self.numCUE, -1)
    
    def alloc_downlink(self, time, c_x, c_y):
        #Get beam sector position
        for n in range(self.totalBeam):
            theta = 2 * np.pi * n / self.totalBeam
            x = self.radius * np.cos(theta)
            y = self.radius * np.sin(theta)
            if -1 < x < 1:
                x = 0
            if -1 < y < 1:
                y = 0
            self.schedule[n][0] = x
            self.schedule[n][1] = y
            if n != 0:
                self.schedule[n-1][2] = x
                self.schedule[n-1][3] = y
            if n == self.totalBeam-1:
                self.schedule[n][2] = self.schedule[0][0]
                self.schedule[n][3] = self.schedule[0][1]
        
        
        #
        self.selectBeam = np.full(self.totalBeam, -1)
        self.selectBeam[time % self.totalBeam] = 0
        candicate = np.where(self.selectBeam < 0)[0]
        beamCandicate = np.random.choice(candicate, self.scheduleBeam-1, replace=False)
        beamCandicate = np.insert(beamCandicate, 0, time % self.totalBeam)
        
        for cue in range(self.numCUE):
            for beam in beamCandicate:
                sectorStart = (self.schedule[beam][0], self.schedule[beam][1])
                sectorEnd = (self.schedule[beam][2], self.schedule[beam][3])
                if not self.isInsideSector(sectorStart, (c_x[cue], c_y[cue])) and self.isInsideSector(sectorEnd, (c_x[cue], c_y[cue])):
                    if np.where(beamCandicate == beam)[0] > 0:
                        self.scheduleUE[cue] = np.where(beamCandicate == beam)[0]
                    else:
                        self.scheduleUE[cue] = np.where(beamCandicate == beam)[0]
        self.scheduleUE = np.full(self.numCUE, -1)
    
    def isInsideSector(self, u, v):
        return -u[0]*v[1] + u[1]*v[0] > 0

# u = scenario.Genrator()
# dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver = u.genrator()
# x = channel.Channel(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver)
allocate = Allocate(dis_C2BS, dis_D, dis_C2D, dis_D2C, dis_BS2D, dis_DiDj, dis_D2BS, numD2DReciver)
# allocate.alloc_downlink(0, c_x, c_y)
# x.draw_model()
# numbeam = 8
# for i in range(100):
#     print("{} time with {} beam".format(i, i%numbeam+1))
for i in range(10):
    allocate.alloc_downlink(i, c_x, c_y)

# x.draw_model()