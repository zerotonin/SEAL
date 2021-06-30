import SEAL_SIM
import pandas as pd
import numpy as np
from utilities import mathUtils
"""
Parameter,Runs:

-current Static   8 
-current None     1
-current Interp   1
-particle No      10 
-basic Reps       100


-sps              100 ?
"""

simObj = SEAL_SIM.SEAL_SIM('headless')

def getCurrent(vel):
    rotMat =np.array([[ 0.5       , -0.5       ,  0.70710678],
                      [ 0.70710678,  0.70710678, -0.        ],
                      [-0.5       ,  0.5       ,  0.70710678]])
    frontalCurrent = np.array([vel,0.,0.])
    return np.dot(rotMat,frontalCurrent)

currents = [getCurrent(x) for x in np.logspace(0,3,20)]
cloudRad = np.logspace(0,200,20)
particleNoList    = np.logspace(0,200,20)[0,5,10,50,150,250,500,1000] #
 

currentPC = 'Kathi'
#Kathis PC:
if currentPC == 'Kathi':
    for diveType in diveTypeList:
        for pNo in particleNoList:
            i = 0
            while i < basicReps:
                simObj = SEAL_SIM.SEAL_SIM('headless',diveTypeStr=diveType,maxParticlesInt=pNo , currentStaticVelTuple=(0.0,0.0,0.0)) 
                simObj.runSimulation()
                i+=1

  