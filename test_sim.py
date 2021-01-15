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
##########################################################################################
# run Simulation with user settings

from importlib import reload 
import utilities as util
import SEAL_SIM
import opticFlowAna
import numpy as np 
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D 
reload(SEAL_SIM)
reload(opticFlowAna)
simObj = SEAL_SIM.SEAL_SIM('headless',spsInt=100, maxParticlesInt=25, durSecFloat=90, currentStaticVelTuple=(0.0,0.0,0.0),diveTypeStr='uShape') 
#simObj.userDefParametersCLI()
simObj.runSimulation()

#########################################################################################
# plot particleCloud
############################################################################################
pU = util.plotUtils(simObj)
pU.plot3D_OF(100,simObj.pCloud.partclObjList,simObj.runTimeData.sealTrajectory)                                                                                                                                                         
pU.plot3D_positionSizeColorCoded(100,0,simObj.pCloud.partclObjList )
pU.plot3D_positionSizeColorCoded(100,1,simObj.pCloud.partclObjList )

###########################################################################################
# plot OpticFlowAna in 2D
###########################################################################################

O = opticFlowAna.opticFlowAnalysis(simObj)
O.opticFlowAbility()
O.plot2DparticleDist(0)
O.createOpticFlow(0)
O.createOpticFlowViewField(0)

#########################################################################################
#plotSealTrajectory
#########################################################################################

simObj.protoMove.getSealHeading()

fig = plt.figure() 
ax = fig.add_subplot(111, projection='3d') 
for data in [simObj.protoMove.posTrajectory, np.array(simObj.runTimeData.sealTrajectory)]:
    ax.plot(list(data[:,0]),list(data[:,1]),list(data[:,2]))
    ax.scatter3D(data[0,0],data[0,1],data[0,2], color = 'green')
    ax.scatter3D(data[-1,0],data[-1,1],data[-1,2], color = 'red')
#plt.show()     

frames4Quiver = range(simObj.runTimeData.traLen)
for i in  frames4Quiver[0::5]:
    X = simObj.protoMove.xProfile[i]
    Y = simObj.protoMove.yProfile[i]
    Z = simObj.protoMove.zProfile[i]
    U = simObj.protoMove.sealHeading[i,0] 
    V = simObj.protoMove.sealHeading[i,1] 
    W = simObj.protoMove.sealHeading[i,2] 
    ax.quiver(X,Y,Z,U*.1,V*.1,W*.1)
plt.show()     

##############################################################################################
# check all velocities
##############################################################################################

sealPos = np.vstack(simObj.runTimeData.sealTrajectory)

#########
# pitch values, depth, yaw
#########
fig2 = plt.figure()
labelList=['thrust','slip','lift','yaw','pitch','roll']
dimLabelList = ['m/s','m/s','m/s','deg/s','deg/s','deg/s']
for i in range(6):
    ax =fig2.add_subplot(6,1,i+1)
    if i > 2:
        ax.plot(np.rad2deg(simObj.runTimeData.velTra[:,i]))
    else:
        ax.plot(simObj.runTimeData.velTra[:,i])
    ax.set_ylabel(labelList[i]+', '+dimLabelList[i])

fig3 = plt.figure()
labelList=['x-coord','y-coord','z-coord','yaw','pitch','roll']
dimLabelList = ['m','m','m','deg','deg','deg']
for i in range(6):
    ax =fig3.add_subplot(6,1,i+1)
    if i > 2:
        ax.plot(np.rad2deg(simObj.protoMove.posTrajectory[:,i]))
    else:
        ax.plot(simObj.protoMove.posTrajectory[:,i])
    ax.set_ylabel(labelList[i]+', '+dimLabelList[i])

plt.show()

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
ax1.plot(np.rad2deg(simObj.protoMove.posTrajectory[:,3]))
ax1.set_ylabel('yaw from posTrajectory')
ax2.plot(np.rad2deg(simObj.protoMove.angles[:,0]))
ax2.set_ylabel('yaw, cumSum fromVeltra')
ax3.plot(np.rad2deg(sealPos[:,3]))
ax3.set_ylabel('yaw from sealTrajectory')
ax4.plot(np.rad2deg(simObj.protoMove.posTrajectory[:,4]))
ax4.set_ylabel('pitch rom posTrajectory')
ax5.plot(np.rad2deg(simObj.protoMove.angles[:,1]))
ax5.set_ylabel('pitch, cumSum fromVeltra')
ax6.plot(np.rad2deg(sealPos[:,4]))
ax6.set_ylabel('pitch from sealTrajectory')

plt.show()

#######
#yx,y,z profile values 
#######
fig4 = plt.figure()
fig, ((ax1, ax2, ax3),  (ax4, ax5, ax6)) = plt.subplots(2, 3)
ax1.plot(simObj.protoMove.xProfile))
ax1.set_ylabel('xProfile')
ax2.plot(simObj.protoMove.yProfile))
ax2.set_ylabel('yProfile')
ax3.plot(simObj.protoMove.zProfile))
# ax3.set_ylabel('zProfile')
ax4.plot(simObj.protoMove.posTrajectory[:,0]))
ax4.set_ylabel('x from posTrajectory')
ax5.plot(simObj.protoMove.posTrajectory[:,1]))
ax5.set_ylabel('y from posTrajectory')
ax6.plot(simObj.protoMove.posTrajectory[:,2]))
ax6.set_ylabel('z from posTrajectory')


plt.show()

#########################################
fig, ((ax1, ax2, ax3),  (ax4, ax5, ax6),(ax7, ax8, ax9), (ax10, ax11, ax12)) = plt.subplots(4, 3) 
ax1.plot(np.rad2deg(simObj.protoMove.posTrajectory[:,3])) 
ax1.set_ylabel('yaw angle') 
ax2.plot(np.rad2deg(simObj.protoMove.posTrajectory[:,4])) 
ax2.set_ylabel('pitch angle') 
ax3.plot(np.rad2deg(simObj.protoMove.posTrajectory[:,5])) 
ax3.set_ylabel('roll angle') 

ax4.plot(simObj.protoMove.posTrajectory[:,0])
ax4.set_ylabel('x from posTrajectory') 
ax5.plot(simObj.protoMove.posTrajectory[:,1]) 
ax5.set_ylabel('y from posTrajectory') 
ax6.plot(simObj.protoMove.posTrajectory[:,2]) 
ax6.set_ylabel('z from posTrajectory') 

ax7.plot(np.rad2deg(simObj.runTimeData.velTra[:,3])) 
ax7.set_ylabel('yaw') 
ax8.plot(np.rad2deg(simObj.runTimeData.velTra[:,4])) 
ax8.set_ylabel('pitch') 
ax9.plot(np.rad2deg(simObj.runTimeData.velTra[:,5])) 
ax9.set_ylabel('roll') 

ax10.plot((simObj.runTimeData.velTra[:,0])) 
ax10.set_ylabel('x from posTrajectory') 
ax11.plot(simObj.runTimeData.velTra[:,1]) 
ax11.set_ylabel('y from posTrajectory') 
ax12.plot(simObj.runTimeData.velTra[:,2]) 
ax12.set_ylabel('z from posTrajectory') 
#plt.savefig('vShape.svg', format = 'svg') 
plt.show()   


###########################################
#test data translation between posTrajectory and velTra YAW & PITCHs   
###########################################

# YAW

print('yawAngle in rad',simObj.protoMove.posTrajectory[:,3][0:10]) 
print('yawAngle from angles', simObj.protoMove.angles[:,0][0:10])
print('yawAngle from veltra', np.cumsum(simObj.protoMove.velTra[:,3][0:10]/simObj.sps))

#PITCH 

print('picthAngle in rad',simObj.protoMove.posTrajectory[:,4][0:10]) 
print('picthAngle from angles', simObj.protoMove.angles[:,1][0:10])
print('picthAngle from veltra', np.cumsum(simObj.protoMove.velTra[:,4][0:10]/simObj.sps))


# analyse OpticFlow ability
reload(opticFlowAna)
O = opticFlowAna.opticFlowAnalysis(simObj) 
O.opticFlowAbility()

O.anaDataList[0:10]
len(O.anaDataList)
O.distRankDiff[0:10]
len(O.distRankDiff)


simObj.environment.setCurrents(currentSys)
##########################################################################################
# run Simulation with user settings

from importlib import reload 
import utilities as util
import SEAL_SIM
import opticFlowAna
import numpy as np 
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D 
reload(SEAL_SIM)
reload(opticFlowAna)
simObj = SEAL_SIM.SEAL_SIM('headless',spsInt=1000, maxParticlesInt=3660, durSecFloat=1/1000., 
                            currentStaticVelTuple=(0.0,0.0,0.0),diveTypeStr='uShape') 
 simObj.runSimulationSingleStep(np.array([0.50831,0.16146,-0.40015,-0.0069808,-1.9845,0.0]),np.array([0.,0.,-35.]),np.array([0.,0.,0.]))

0.50831,0.16146,-0.40015,-0.0069808,-1.9845
0.54088,-0.0058351,-0.41512,-2.4519e-05,-0.76015
0.14588,-0.0143,0.046056,-0.023478,-2.5786e-05
0.10182,-0.5523,0.0024168,-0.16104,0.00047178
0.45197,0.72346,0.021853,0.081617,0.00084235
0.58643,-0.29914,0.012678,0.11914,0.0008728
1.4685,0.15058,0.038578,-0.066709,0.0014909
0.43296,0.098639,-1.0179,0.0060124,0.003138
0.48369,0.01351,-0.0080336,-0.013273,0.5358
