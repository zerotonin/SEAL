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
sps  = 100
step = np.array([0,1.,0.,0.,0.,0.])
pos  = np.array([0.,0.,-30.0])
curr = np.array([0.,0.,0.])
simObj = SEAL_SIM.SEAL_SIM('headless',spsInt=sps, maxParticlesInt=3660, durSecFloat=2/sps, 
                            currentStaticVelTuple=(0.0,0.0,0.0),diveTypeStr='uShape') 
simObj.runSimulationSingleStep(step,pos,curr)
simObj.opticFlowAna.calculateDivergence(0)
plt.figure() 
plt.imshow(simObj.opticFlowAna.divergence) 
plt.colorbar()
simObj.opticFlowAna.plotOpticFlow(0,showStartEnd = False,projectionType='p1olar')