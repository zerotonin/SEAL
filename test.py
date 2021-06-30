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
  
stepThrust = np.array([3.0, 0.0, 0.0, 0.0, 0.0, 0.0]) # translation 3m/s thrust  
stepSlip   = np.array([0.0, 3.0, 0.0, 0.0, 0.0, 0.0]) # translation 3m/s Slip  
stepLift   = np.array([0.0, 0.0, 3.0, 0.0, 0.0, 0.0]) # translation 3m/s lift  
  
pos  = np.array([0.,0.,-30.0])   
curr = np.array([0.,0.,0.])   
simObj = SEAL_SIM.SEAL_SIM('headless',spsInt=sps,cloudRadiusFloat=0.18, maxParticlesInt=1000, durSecFloat=2/sps,  
                            currentStaticVelTuple=(0.0,0.0,0.0),diveTypeStr='uShape')    
  
simObj.runSimulationSingleStep(stepThrust,pos,curr)   
simObj.opticFlowAna.plotOpticFlow(frame=0)  
simObj.opticFlowAna.plotOpticFlow(frame=0,projectionType = 'nonPolar', viewField = True)   
simObj.opticFlowAna.plotOpticFlow(frame=0,projectionType = 'nonPolar')   
simObj.runTimeData.writeOutParticleTra('TranslationalMovementThust')  
  
simObj.runSimulationSingleStep(stepSlip,pos,curr)   
simObj.opticFlowAna.plotOpticFlow(frame=0)  
simObj.opticFlowAna.plotOpticFlow(frame=0,projectionType = 'nonPolar', viewField = True)   
simObj.opticFlowAna.plotOpticFlow(frame=0,projectionType = 'nonPolar')   
simObj.runTimeData.writeOutParticleTra('TranslationalMovementSlip')  
  
simObj.runSimulationSingleStep(stepLift,pos,curr)   
simObj.opticFlowAna.plotOpticFlow(frame=0)  
simObj.opticFlowAna.plotOpticFlow(frame=0,projectionType = 'nonPolar', viewField = True)   
simObj.opticFlowAna.plotOpticFlow(frame=0,projectionType = 'nonPolar')   
simObj.runTimeData.writeOutParticleTra('TranslationalMovementLift')    