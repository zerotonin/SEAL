import SEAL_SIM,os
import pandas as pd
import numpy as np
from utilities import mathUtils
from pathlib import Path
"""
"""


def float2str(num):
    return str(np.around(num,3)).replace('.','-')


def getCurrent(vel):
    rotMat =np.array([[ 0.5       , -0.5       ,  0.70710678],
                      [ 0.70710678,  0.70710678, -0.        ],
                      [-0.5       ,  0.5       ,  0.70710678]])
    frontalCurrent = np.array([vel,0.,0.])
    return np.insert(np.dot(rotMat,frontalCurrent),0,vel,axis=0)

simObj = SEAL_SIM.SEAL_SIM('headless')
sps = 100 #100 samples per second
pos  = np.array([0.,0.,-30.0]) # in the water column
step = np.array([3.0, 0.0, 0.0, 0.0, 0.0, 0.0]) # changed to all PMs

# cluster translational 5D PMs plus 0.0 for roll
TranslaSlowPM = ([[1.8609,0.44391, -0.072173, -0.52564,  -0.0011278, 0.0],
                  [1.4749,0.96914,  0.020206, -0.049538, -0.0048028, 0.0],
                  [1.0312,-0.33755,-0.10574,  -0.023993, -0.0041735, 0.0],
                  [1.6527,0.3865,  -0.052242,  0.0060586,-0.93312,   0.0],
                  [1.6259,0.39059, -0.010533,  0.008956,  0.84291,   0.0],
                  [1.5748,0.45007,  0.051904,  0.35187,  -0.0064602, 0.0]])

TranslaFastPM = ([[1.1163,0.33908, -2.5045,    0.033083,  0.00027863,0.0],
                  [3.7257,1.4087,   0.058942,  0.041954, -0.0015622, 0.0],
                  [3.6564,-0.48179, 0.1856,    0.095942,  0.0022598, 0.0],])


RotationalPM = ([[1.8268,  0.01529,  -0.15939, 2.1617,    0.0054881, 0.0],#yaw right
                 [1.7163,  0.79161,  -0.13845,-2.2299,    0.00061883,0.0],#yaw left
                 [0.27325, 0.10791,   0.26439,-0.0018402,-2.9212,    0.0],#pitch down
                 [-0.10417,0.0054149,-0.019695,0.0048984, 2.2828,    0.0]])#pitch up

currents = [getCurrent(x) for x in np.insert(np.geomspace(0.01,3,9,endpoint=True),0,0.0,axis=0)] # currenty between 0-3m/s waterspeed
#cloudRad = np.geomspace(0.1,0.1,1,endpoint=True)  # loud Radius from 1mm to 1m (this is not working yet, giving to high values above 1)
# simulate differen turbidity 1000 p/cm3, 10000 p/cm3, 35000p/cm3
# https://www.tandfonline.com/doi/abs/10.3402/tellusb.v35i5.14624
#turbidty = (22,220,770) --> gilt für eine sphere von 0.0018m
cloudRad = np.array([0.1]) # run for distance of 10c,
particleNoList    = np.geomspace(2.0,770.0,10,endpoint=True) # muss an weiter Hohlsphere angepasst werden ?
rotVelList        = np.geomspace(0.001,np.pi,10, endpoint = True)
cloudRadList      = np.geomspace(0.001,10,10,endpoint=True)  


basePath = '/media/dataSSD/sealPartTra'
metaDataList = list()
#%%  PrototypicalMovements
Movement = 'all'

if Movement == 'TranslaFast':
    ProtoMoveList = TranslaFastPM
elif Movement == 'TranslaSlow':
    ProtoMoveList = TranslaSlowPM
elif Movement == 'all':
    ProtoMoveList = TranslaFastPM+TranslaSlowPM+RotationalPM
else:
    ProtoMoveList = RotationalPM

traPath = os.path.join(basePath,'PM_comparison')
Path(traPath).mkdir(parents=True, exist_ok=True)
pmC = 0
for pm in ProtoMoveList:
    pmC +=1    
    for pNo in particleNoList:
        for cRad in cloudRad:
            for rep in range(20):

                #for curr in currents:
                curr = np.array([0.0,0.0,0.0,0.0])
                simObj = SEAL_SIM.SEAL_SIM('headless', spsInt=sps, cloudRadiusFloat=cRad, maxParticlesInt=pNo,                                    
                                            durSecFloat=2/sps, diveTypeStr='uShape')    
                simObj.runSimulationSingleStep(pm,pos,curr[1::])    
                fileName = 'PM_'+str(pmC)+'_Current_'+ float2str(curr[0])+'_CloudRad_'+float2str(cRad)+'_maxParticles_'+str(int(pNo))+'_replicate_'+str(rep).zfill(2)
                simObj.runTimeData.writeOutParticleMat( os.path.join(traPath,fileName))
                metaDataList.append([fileName,pm,curr,cRad,pNo])  
#%% rotation vs distance                   
pmC = 0 
sps = 100   

traPath = os.path.join(basePath,'trigonometry_eva')
Path(traPath).mkdir(parents=True, exist_ok=True)
curr = np.array([0.0,0.0,0.0,0.0])
for rotVel in rotVelList:
    for cloudRad in cloudRadList:
        pm = np.array([1.0,0.0,0.0,rotVel,0.,0.])
        simObj = SEAL_SIM.SEAL_SIM('headless', spsInt=sps, cloudRadiusFloat=cloudRad, maxParticlesInt=360,                                    
                                    durSecFloat=2/sps, diveTypeStr='uShape')    
        simObj.runTimeData.gridParticles = True
        simObj.runSimulationSingleStep(pm,pos,curr[1::])    
        fileName = 'Trigonometry_CloudRad_'+float2str(cloudRad)+'_maxParticles_'+str(int(360))+'_rotVelocity_'+str(round(rotVel,4))
        simObj.runTimeData.writeOutParticleMat( os.path.join(traPath,fileName))  
        metaDataList.append([fileName,pm,curr,rotVel,sps])
#%% degree of freedom test
traPath = os.path.join(basePath,'degreeOfFreedom')
Path(traPath).mkdir(parents=True, exist_ok=True)
sps = 100
dof = np.array([[ 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
               [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
               [ 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
               [ 0.0,-1.0, 0.0, 0.0, 0.0, 0.0],
               [ 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
               [ 0.0, 0.0,-1.0, 0.0, 0.0, 0.0],
               [ 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
               [ 0.0, 0.0, 0.0,-1.0, 0.0, 0.0],
               [ 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
               [ 0.0, 0.0, 0.0, 0.0,-1.0, 0.0],
               [ 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
               [ 0.0, 0.0, 0.0, 0.0, 0.0,-1.0]])
curr = np.array([0.0,0.0,0.0,0.0])
dof_name = ['thrust','neg_thrust','slip','neg_slip','lift','neg_lift','yaw','neg_yaw','pitch','neg_pitch','roll','neg_roll']
c = 0
for pm in dof:
    simObj = SEAL_SIM.SEAL_SIM('headless', spsInt=sps, cloudRadiusFloat=10, maxParticlesInt=360,                                    
                                durSecFloat=2/sps, diveTypeStr='uShape')   
    simObj.runTimeData.gridParticles = True   
    simObj.runSimulationSingleStep(pm,pos,curr[1::])    
    fileName = dof_name[c] +'_CloudRad_'+float2str(1)+'_maxParticles_'+str(int(360))

    simObj.runTimeData.writeOutParticleMat( os.path.join(traPath,fileName))  
    metaDataList.append([fileName,pm,curr,np.sum(pm[3::]),sps])
    c+=1




metaData = pd.DataFrame(metaDataList,columns=['fileName','protoMov_mPs','current_mPs','cloudRad_m','numOfParticles'])
metaData.index.name='fileNo'
metaData.to_csv(os.path.join(basePath,'metaData') + '.csv')
protoMov = pd.DataFrame(ProtoMoveList, columns=['thrust_mPs','slip_mPs','lift_mPs','yaw_radPs','pitch_radPs','roll_radPs'])
protoMov.index.name='pmNo'
protoMov.to_csv(os.path.join(basePath,'protoMov') + '.csv')