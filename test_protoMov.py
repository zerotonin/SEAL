from importlib import reload 
import SEAL_SIM,protoMov
import numpy as np 
import matplotlib.pyplot as plt

reload(protoMov)
simObj = SEAL_SIM.SEAL_SIM()
P = protoMov.ProtMov(simObj)
P.generator2('uShape',600)
P.getPositionAndAngelsFromVel()

tra = np.cumsum(P.velTra[:,0:3]/P.sps,axis=0) 


fig = plt.figure() 
ax = fig.gca(projection='3d')   
ax.plot(list(P.positions[:,0]),list(P.positions[:,1]),list(P.positions[:,2]))    
#ax.set_xlim(-70,70)# x axes goes from -10 to 10 since Cloudsphere is 10
#ax.set_ylim(-70,70)# same here
#ax.set_zlim(-70,70)
ax.set_xlabel('X')
ax.set_ylabel('Y')

ax.set_zlabel('Depth (m)')

fig = plt.figure() 
ax = fig.gca()   
ax.plot(P.zProfile[:,1])
fig = plt.figure() 
ax = fig.gca()   
ax.plot(P.pitchAngle)