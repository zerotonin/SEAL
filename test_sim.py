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
reload(SEAL_SIM)
reload(opticFlowAna)
simObj = SEAL_SIM.SEAL_SIM()
simObj.userDefParametersCLI()
simObj.runSimulation()

# analyse OpticFlow ability

O = opticFlowAna.opticFlowAnalysis(simObj) 
O.opticFlowAbility()

O.anaDataList[0:10]
len(O.anaDataList)
O.distRankDiff[0:10]
len(O.distRankDiff)