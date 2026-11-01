import numpy as np 
import SEAL_SIM
from tqdm import tqdm

trajectoryNum    = 100
diveDurationSec  = {'uShape':385.,'vShape':200.}
folderPos = '/media/dataSSD/diveVelTra'

for i in tqdm(range(trajectoryNum),'running trajectories....'):
    for diveShape in ['vShape','uShape']:
        try:
            # dive duration
            diveDur = np.random.normal(diveDurationSec[diveShape],30.)   
            # simulation object
            print(diveDur)
            simObj = SEAL_SIM.SEAL_SIM('headless',spsInt=100, maxParticlesInt=1, durSecFloat=diveDur, currentStaticVelTuple=(0.0,0.0,0.0),diveTypeStr=diveShape)
            # get trajectory
            simObj.runTrajectoryGenerationOnly()
            print(simObj.runTimeData.velTra)
            # make filename
            fileBaseName = folderPos + '/' + diveShape + '_' +str(i).zfill(3)
            # write out trajectory
            simObj.runTimeData.writeOutVelTra(fileBaseName)
            # clean up
            del(simObj)
        except: 
            pass

#import matplotlib.pyplot as plt
#plt.plot(np.rad2deg(simObj.runTimeData.velTra[:,3]))
#plt.show()