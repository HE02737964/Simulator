import numpy as np

a = [(0,1), (1,2), (2,3)]

dis = list()

for x,y in a: 
    distance = np.sqrt(x**2+y**2)
    dis = np.append(np.asarray(dis), distance)

print(dis)


N = -174
N0 = 10**(N / 10)
N0 = N0 * 15e3
print(10*np.log10(N0))



from model import channel

pos = [(1,1), (2,2), (3,3)]
x = channel.Channel()
y = x.getCellChannelGain(len(pos), pos, 6)
print(y)


x = [1,2,3,4,5,6,7,8,9,0]
print(x[5:])