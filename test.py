from importlib import reload  
import utilities as util 
import SEAL_SIM 
import opticFlowAna 
import numpy as np  
import matplotlib.pyplot as plt  
from mpl_toolkits.mplot3d import Axes3D  
reload(SEAL_SIM) 
reload(opticFlowAna) 
sps  = 100000 
step = np.array([3.6564,-0.48179, 0.1856,    0.095942,  0.0022598, 0.0]) 
pos  = np.array([0.,0.,-30.0]) 
curr = np.array([0.,0.,0.]) 
simObj = SEAL_SIM.SEAL_SIM('headless',spsInt=sps, maxParticlesInt=1000, durSecFloat=2/sps,  
                            currentStaticVelTuple=(0.0,0.0,0.0),diveTypeStr='uShape')  
simObj.runSimulationSingleStep(step,pos,curr)
  
simObj.opticFlowAna.plotOpticFlow(frame=0) 