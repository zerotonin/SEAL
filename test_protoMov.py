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
set_axes_equal(ax)


fig = plt.figure() 
ax = fig.gca()   
ax.plot(P.yaw)