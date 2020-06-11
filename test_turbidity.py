import numpy as np
import time, turbidity 
import matplotlib.pyplot  as plt
from mpl_toolkits.mplot3d import Axes3D
from importlib import reload 

reload(turbidity)   
C = turbidity.Cloud('test')  
C.add_particles()   
C.moveParticles() 

start = time.time() 
C.moveParticles() 
end = time.time()
print(end-start)   



reload(turbidity)   
C = turbidity.Cloud('test')  
C.add_particles()   

# openening a figure object
fig = plt.figure()
# adding a axis object with 3D axis
ax = fig.add_subplot(111, projection='3d')
# create test data
xdata = np.array([ 1 , 2   ,3.69,-1.4 ,-3  ])
ydata = np.array([-.5, 6.6 ,-3.6,-9.2,0])
zdata = np.random.rand(5)*10 -5
#plot
ax.scatter3D(xdata, ydata, zdata, c=xdata, cmap='brg')
# update and plot
fig.show()

# thingi

for po in C.partclObjList: 
   print(po.position,po.visible,po.activeMovement,po.temperature) 
   po.position[2] = po.position[2] -np.random.rand()*50
   po.depth2Temperature()
   print(po.position,po.visible,po.activeMovement,po.temperature) 
   print("=====================================================")

p = C.partclObjList[23]
start = time.time() 
p.combinedMovement(np.array([0,-2.1,0]),np.array([3.4,0,0]))
end = time.time()
print(end-start) 

reload(turbidity)   
C = turbidity.Cloud('test')  
C.add_particles()  
for i in range(1000):

    C.moveParticles() 
print(len(C.partclObjList))

for po in C.partclObjList: 
   ...:     print(po.position) 


# for testing sphere2cart function 

import numpy as np
import time, turbidity
from importlib import reload 
from sympy import *

reload(turbidity)
C = turbidity.Cloud('test')  
C.add_particles() 
C.sphere2cart()


print(C.partclObjList[0].position)                                                                                                 
C.Cloudsphere2cart()                                                                                                               
print(C.partclObjList[0].position)                                                                                                 
C.Cloudcart2sphere()                                                                                                               
print(C.partclObjList[0].position) 