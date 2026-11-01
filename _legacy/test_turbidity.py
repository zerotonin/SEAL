import numpy as np
import time, turbidity 
import matplotlib.pyplot  as plt
from mpl_toolkits.mplot3d import Axes3D
from importlib import reload 

reload(turbidity)   
C = turbidity.Cloud('test')  
C.add_particles()
C.sealStep = np.array([2,0.,-4.,0.0,-45,0.])   
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



'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
unused functinon from particle class
        



    #def cart2cylindric(self,cartPosition):
    #
    #    r   = np.sqrt(cartPosition[0]**2+cartPosition[1]**2)
    #    phi = np.arctan2(cartPosition[1],cartPosition[0]) # https://en.wikipedia.org/wiki/Cylindrical_coordinate_system depending on x value differen function ?
    #    return r, phi, z
    

    #def cart2sphere(self,cartPosition):
    #    
    #    XsqPlusYsq  = cartPosition[0]**2 + cartPosition[1]**2
    #    r           = m.sqrt(XsqPlusYsq + cartPosition[2]**2)              
    #    theta       = m.atan2(m.sqrt(XsqPlusYsq),cartPosition[2])     
    #    phi         = m.atan2(cartPosition[1],cartPosition[0])          
    #    return r,theta,phi

unused function from environment class
    #def contrast2particleSize(self):
    #    """
    #    dependent on the contrast particle can be detected by the seal up to 3,8mm in a distance of 60cm, This is too big for real 
    #    particles in the balticSea (20µm and 160µm)*R1
    #    R1) Bunke, Dennis, et al. "Natural and Anthropogenic Sediment Mixing Processes in the South-Western Baltic Sea." Frontiers in Marine Science (2019).
    #    R2) Miroslaw Jonasz (1983) Particle-size distributions in the Baltic, Tellus B:Chemical and Physical Meteorology, 35:5, 346-358, DOI: 10.3402/tellusb.v35i5.14624
    #    Those objects that are still visible in 60cm distance can be as small a 3.8mm. Taken the contrast related objct sizes detectable by seals
    #    from Frederike Hanke the following function is true.
    #    
    #    f(x) = 3.6195568931541864+10.040262458171055*Exp(-0.055671078908775984*x) 
    #    created via curve fitting in plotly 
    #    """
