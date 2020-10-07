from importlib import reload 
import SEAL_SIM,protoMov
import numpy as np 
import matplotlib.pyplot as plt

reload(protoMov)
simObj = SEAL_SIM.SEAL_SIM()
P = protoMov.ProtMov(simObj)
P.generator2('vShape',600)
P.getPositionAndAngels

fig = plt.figure() 
ax = fig.gca()   
ax.plot(P.thrust)

fig = plt.figure() 
ax = fig.gca(projection='3d')   
#ax.axis('equal')
ax.plot(list(P.xProfile),list(P.yProfile),list(P.zProfile))    
#ax.set_xlim(-70,70)# x axes goes from -10 to 10 since Cloudsphere is 10
#ax.set_ylim(-70,70)# same here
#ax.set_zlim(-70,70)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Depth (m)')
#set_axes_equal(ax)
plt.show()

fig = plt.figure() 
ax = fig.gca()   
ax.plot(P.yaw)

fig = plt.figure() 
ax = fig.gca(projection='3d')   
ax.plot(list(P.sealHeading[:,0],list(P.sealHeading[:,1]),list(P.sealHeading[:,2]))    
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Depth (m)')
plt.show()

######################################################################################

from importlib import reload  
import SEAL_SIM,protoMov 
import numpy as np  
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D 

reload(protoMov) 
simObj = SEAL_SIM.SEAL_SIM() 
P = protoMov.ProtMov(simObj) 
P.generator2('vShape',600)  

P.getPositionAndAngelsFromVel()

P.getSealHeading()


fig = plt.figure() 
ax = fig.add_subplot(111, projection='3d') 
#ax.set_xlim(-70,70)# x axes goes from -10 to 10 since Cloudsphere is 10 
#ax.set_ylim(-70,70)# same here 
#ax.set_zlim(-70,10)
ax.plot(list(P.xProfile),list(P.yProfile),list(P.zProfile),color='red')
for i in range(P.traLen):

    X = P.xProfile[i]
    Y = P.yProfile[i]
    Z = P.zProfile[i]
    U = P.sealHeading[i,0] 
    V = P.sealHeading[i,1] 
    W = P.sealHeading[i,2] 
    ax.quiver(X,Y,Z,U,V,W,arrow_length_ratio=0.01)
plt.show()     
