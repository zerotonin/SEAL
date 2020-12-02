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




# analyse OpticFlow ability
reload(opticFlowAna)
O = opticFlowAna.opticFlowAnalysis(simObj) 
O.opticFlowAbility()

O.anaDataList[0:10]
len(O.anaDataList)
O.distRankDiff[0:10]
len(O.distRankDiff)