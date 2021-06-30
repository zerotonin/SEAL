import SEAL_SIM
import pandas as pd
import numpy as np
from utilities import mathUtils
"""
Parameter,Runs:

-dive type        2
-current Static   8 
-current None     1
-current Interp   1
-particle No      10 
-basic Reps       100

--> 200 different conditions 
--> totalNo of Runs,20000

-sps              100
-traDurSec        240
-simulatedFrames  480000000

-sim Rate         0.05
-Total sim Duration in h ,6666.66666666667

CPUs available    52

--> real time in days ,5.55555555555556

runs per CPU ,400 (4 conditions)

Kathis PC: 4CPU, Annes PC: 8CPU, 
Miris PC: 4CPU, Laurins PC: 8CPU, 
EckPC: 8CPU, LabPC: 4CPU,
Bart1 PC:8CPU, Bart2 PC:8CPU
"""

simObj = SEAL_SIM.SEAL_SIM('headless')

def getCurrent(vel):
    rotMat =np.array([[ 0.5       , -0.5       ,  0.70710678],
                      [ 0.70710678,  0.70710678, -0.        ],
                      [-0.5       ,  0.5       ,  0.70710678]])
    frontalCurrent = np.array([vel,0.,0.])
    return np.dot(rotMat,frontalCurrent)

currents = [getCurrent(x) for x in np.logspace(0,3,20)]
cloudRad = np.logspace(0,200,20                      )


particleNoList    = [0,5,10,50,150,250,500,1000] #8 + 2 ([300,750])
basicReps         = 100 

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

  