import  numpy as np

class Convert:
    def mW_to_dB(mW):
        dB = 10*np.log10(mW)
        return np.round(dB, decimals=0)
    
    def dB_to_mW(dB):
        mW = 10**(dB/10)
        return np.round(mW, decimals=0)