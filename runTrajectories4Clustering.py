import numpy as np 
import SEAL_SIM
from tqdm import tqdm

trajectoryNum    = 100
diveDurationSec  = {'uShape':385.,'vShape':200.}
folderPos = '/media/dataSSD/diveVelTra'

for i in tqdm(range(trajectoryNum),'running trajectories....'):
    for diveShape in ['uShape','vShape']:
        try:
            # dive duration
            diveDur = np.random.normal(diveDurationSec[diveShape],30.)   
            # simulation object
            simObj = SEAL_SIM.SEAL_SIM('headless',spsInt=1000, maxParticlesInt=1, durSecFloat=diveDur, currentStaticVelTuple=(0.0,0.0,0.0),diveTypeStr=diveShape)
            # get trajectory
            simObj.runTrajectoryGenerationOnly()
            # make filename
            fileBaseName = folderPos + '/' + diveShape + '_' +str(i).zfill(3)
            # write out trajectory
            simObj.runTimeData.writeOutVelTra(fileBaseName)
            # clean up
            del(simObj)
        except: 
            pass