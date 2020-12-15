import SEAL_SIM
"""
Parameter,Runs:

-dive type,2
-current Static,8 
-current None,1
-current Interp,1
-particle No,10 
-basic Reps,100
--> 200 different conditions 

--> totalNo of Runs,20000
-sps,100
-traDurSec,240
-simulatedFrames,480000000

-sim Rate,0.05
-Total sim Duration in h ,6666.66666666667

CPUs available = 52

--> real time in days,5.55555555555556

runs per CPU ,400 (4 conditions)

Kathis PC: 4CPU, Annes PC: 8CPU, 
Miris PC: 4CPU, Laurins PC: 8CPU, 
EckPC: 8CPU, LabPC: 4CPU,
Bart1 PC:8CPU, Bart2 PC:8CPU
"""

simObj = SEAL_SIM.SEAL_SIM('headless')

diveTypeList      = ['vShape','uShape']
currentNone       = (0.0,0.0,0.0)
# taken from https://www.frontiersin.org/articles/10.3389/fmars.2018.00287/full
# water velocities ranging from -15 +15 cm/s ( -0.15 to 0.15m/s)
currentStaticList = [(0.15,0.0,0.0),(0.0,0.15,0.0),(0.0,0.0,0.15),(-0.05,0.0,0.0),
                     (0.0,-0.05,0.0),(0.0,0.0,-0.05),(0.05,0.15,0.01),(-0.05,-0.15,-0.01)]
currentInterp     = None
particleNoList    = [0,5,10,50,150,250,500,1000] #8 + 2 ([300,750])
basicReps         = 100 


#Kathis PC:
#how to do it with reloading the SealSim?
#for diveType in diveTypeList:
#    simObj.runTimeData.setParameter('diveType',diveType)
#    for pNo in particleNoList:
#        simObj.runTimeData.setParameter('maxParticles',pNo)
#        i = 0
#        while i < basicReps:
#            simObj.runSimulation()
#            i+=1
#
# or :
for diveType in diveTypeList:
    for pNo in particleNoList:
        i = 0
        while i < basicReps:
            simObj = SEAL_SIM.SEAL_SIM('headless',diveTypeStr=diveType,maxParticlesInt=pNo , currentStaticVelTuple=(0.0,0.0,0.0)) 
            simObj.runSimulation()
            i+=1

#Annes PC:

currentStaticList= [(0.15,0.0,0.0),(0.0,0.15,0.0)]
for diveType in diveTypeList:
    for currentStatic in currentStaticList:
        for pNo in particleNoList:
            i = 0
            while i < basicReps:
                simObj = SEAL_SIM.SEAL_SIM('headless',diveTypeStr=diveType,maxParticlesInt=pNo , currentStaticVelTuple=currentStatic) 
                simObj.runSimulation()
                i+=1

#Miris PC:

for diveType in diveTypeList:
    for pNo in particleNoList:
        i = 0
        while i < basicReps:
            simObj = SEAL_SIM.SEAL_SIM('headless',diveTypeStr=diveType,maxParticlesInt=pNo , currentStaticVelTuple=(0.0,0.0,0.15)) 
            simObj.runSimulation()
            i+=1

#Laurins PC:

currentStaticList= [(-0.05,0.0,0.0), (0.0,-0.05,0.0)]
for diveType in diveTypeList:
    for currentStatic in currentStaticList:
        for pNo in particleNoList:
            i = 0
            while i < basicReps:
                simObj = SEAL_SIM.SEAL_SIM('headless',diveTypeStr=diveType,maxParticlesInt=pNo , currentStaticVelTuple=currentStatic) 
                simObj.runSimulation()
                i+=1

#EckPC:

currentStaticList= [(0.0,0.0,-0.05),(0.05,0.15,0.01)]
for diveType in diveTypeList:
    for currentStatic in currentStaticList:
        for pNo in particleNoList:
            i = 0
            while i < basicReps:
                simObj = SEAL_SIM.SEAL_SIM('headless',diveTypeStr=diveType,maxParticlesInt=pNo , currentStaticVelTuple=currentStatic) 
                simObj.runSimulation()
                i+=1

#LabPC:

for diveType in diveTypeList:
    for pNo in particleNoList:
        i = 0
        while i < basicReps:
            simObj = SEAL_SIM.SEAL_SIM('headless',diveTypeStr=diveType,maxParticlesInt=pNo , currentTypeStr='interp') 
            simObj.runSimulation()
            i+=1

#Bart1 PC:

for diveType in diveTypeList:
    for pNo in particleNoList:
        i = 0
        while i < basicReps:
            simObj = SEAL_SIM.SEAL_SIM('headless',diveTypeStr=diveType,maxParticlesInt=pNo , currentStaticVelTuple=(-0.05,-0.15,-0.01)) 
            simObj.runSimulation()
            i+=1

particleNoList = [300,750]
for diveType in diveTypeList:
    for pNo in particleNoList:
        i = 0
        while i < basicReps:
            simObj = SEAL_SIM.SEAL_SIM('headless',diveTypeStr=diveType,maxParticlesInt=pNo , currentTypeStr='interp') 
            simObj.runSimulation()
            i+=1

particleNoList = [300,750]
for diveType in diveTypeList:
    for pNo in particleNoList:
        i = 0
        while i < basicReps:
            simObj = SEAL_SIM.SEAL_SIM('headless',diveTypeStr=diveType,maxParticlesInt=pNo , currentStaticVelTuple=(0.0,0.0,0.0)) 
            simObj.runSimulation()
            i+=1

#Bart2 PC:

particleNoList = [300,750]
for diveType in diveTypeList:
    for currentStatic in currentStaticList:
        for pNo in particleNoList:
            i = 0
            while i < basicReps:
                simObj = SEAL_SIM.SEAL_SIM('headless',diveTypeStr=diveType,maxParticlesInt=pNo , currentStaticVelTuple=currentStatic) 
                simObj.runSimulation()
                i+=1

