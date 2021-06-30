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
# simulate differen turbidity 1000 p/cm3, 10000 p/cm3, 35000p/cm3
# https://www.tandfonline.com/doi/abs/10.3402/tellusb.v35i5.14624
#turbidty = (22,220,770) --> gilt für eine sphere von 0.0018m
particleNoList    = np.logspace(0,770,20) # muss an weiter Hohlsphere angepasst werden ?


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

  