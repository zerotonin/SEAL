from importlib import reload 
import SEAL_SIM, opticFlowAna
import numpy as np 

reload(opticFlowAna)
simObj = SEAL_SIM.SEAL_SIM()
simObj.simulate_sample()
simObj.simulate_sample()

OFA = opticFlowAna.opticFlowAnalysis(simObj)
x   = OFA.cartTra2cylTra(OFA.particleList[32].trajectory)

currentSys = np.zeros(shape=(8,3))
currentSys[0,:] = [10,0,0]      
currentSys[1,:] = [8,1,2]      
currentSys[2,:] = [8,0,0]      
currentSys[3,:] = [5,5,2]    
currentSys[4,:] = [10,0,0]      
currentSys[5,:] = [8,3,0]      
currentSys[6,:] = [8,0,0]      
currentSys[7,:] = [5,7,0]     

simObj.environment.setCurrents(currentSys)

# run Simulation with user settings

from importlib import reload 
import SEAL_SIM, opticFlowAna
import numpy as np 
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D 
reload(SEAL_SIM)
reload(opticFlowAna)
simObj = SEAL_SIM.SEAL_SIM()
#simObj.userDefParametersCLI()
simObj.runSimulation()

 
fig = plt.figure() 
ax = fig.add_subplot(111, projection='3d') 
for data in [simObj.protoMove.posTrajectory, np.array(simObj.seal.sealTrajectory)]:
    ax.plot(list(data[:,0]),list(data[:,1]),list(data[:,2]))
    ax.scatter3D(data[0,0],data[0,1],data[0,2], color = 'green')
    ax.scatter3D(data[-1,0],data[-1,1],data[-1,2], color = 'red')
plt.show()     

    frames4Quiver = range(P.traLen)
    for i in  frames4Quiver[0::5]:

        X = P.xProfile[i]
        Y = P.yProfile[i]
        Z = P.zProfile[i]
        U = P.sealHeading[i,0] 
        V = P.sealHeading[i,1] 
        W = P.sealHeading[i,2] 
        ax.quiver(X,Y,Z,U*.1,V*.1,W*.1)
plt.show()     

simObj.protoMove.getPositionAndAngelTrajectoryFromVelTrajectory()

sealPos = np.vstack(simObj.seal.sealTrajectory)

#########
# pitch values, depth, yaw
#########
fig2 = plt.figure()
ax =fig2.add_subplot(311)
ax.plot(np.rad2deg(simObj.protoMove.angles[:,0]))
ax.set_ylabel('yaw, deg')
ax =fig2.add_subplot(312)
ax.plot(np.rad2deg(simObj.protoMove.angles[:,1]))
ax.set_ylabel('pitch, deg')
ax =fig2.add_subplot(313)
ax.plot(P.zProfile)

plt.show()

#######
#yaw & pitch values 
#######
fig3 = plt.figure()
fig, ((ax1, ax2, ax3),(ax4, ax5, ax6)) = plt.subplots(2,3)
ax1.plot(np.rad2deg(simObj.protoMove.angles[:,0]))
ax1.set_ylabel('yaw, deg')
ax2.plot(np.rad2deg(simObj.protoMove.posTrajectory[:,3]))
ax2.set_ylabel('yaw from posTrajectory')
ax3.plot(np.rad2deg(sealPos[:,3]))
ax3.set_ylabel('yaw from sealTrajectory')
ax4.plot(np.rad2deg(simObj.protoMove.angles[:,1]))
ax4.set_ylabel('pitch, deg')
ax5.plot(np.rad2deg(simObj.protoMove.posTrajectory[:,4]))
ax5.set_ylabel('pitch rom posTrajectory')
ax6.plot(np.rad2deg(sealPos[:,4]))
ax6.set_ylabel('pitch from sealTrajectory')

plt.show()

#######
#yx,y,z profile values 
#######
fig4 = plt.figure()
fig, ((ax1, ax2, ax3),  (ax4, ax5, ax6), (ax7, ax8, ax9)) = plt.subplots(3, 3)
ax1.plot(np.rad2deg(simObj.protoMove.xProfile))
ax1.set_ylabel('xProfile')
ax2.plot(np.rad2deg(simObj.protoMove.yProfile))
ax2.set_ylabel('yProfile')
ax3.plot(np.rad2deg(simObj.protoMove.zProfile))
ax3.set_ylabel('zProfile')
ax4.plot(np.rad2deg(simObj.protoMove.posTrajectory[:,0]))
ax4.set_ylabel('x from posTrajectory')
ax5.plot(np.rad2deg(simObj.protoMove.posTrajectory[:,1]))
ax5.set_ylabel('y from posTrajectory')
ax6.plot(np.rad2deg(simObj.protoMove.posTrajectory[:,2]))
ax6.set_ylabel('z from posTrajectory')
ax7.plot(np.rad2deg(sealPos[:,0]))
ax7.set_ylabel('x from sealTrajectory')
ax8.plot(np.rad2deg(sealPos[:,1]))
ax8.set_ylabel('y from sealTrajectory')
ax9.plot(np.rad2deg(sealPos[:,2]))
ax9.set_ylabel('z from sealTrajectory')

plt.show()


# analyse OpticFlow ability
reload(opticFlowAna)
O = opticFlowAna.opticFlowAnalysis(simObj) 
O.opticFlowAbility()

O.anaDataList[0:10]
len(O.anaDataList)
O.distRankDiff[0:10]
len(O.distRankDiff)