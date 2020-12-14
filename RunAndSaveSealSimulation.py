import SEAL_SIM

simObj = SEAL_SIM.SEAL_SIM('headless')

diveTypeList = ['vSahpe','uShape']
particleNoList = [0,5,10,50,150,250,500]
basicReps = 100
simObj = SEAL_SIM.SEAL_SIM() # why again ?

for diveType in diveTypeList:
    simObj.runTimeData.setParameter('diveType',diveType)
    for pNo in particleNoList:
        simObj.runTimeData.setParameter('maxParticles',pNo)
        i = 0
        while i < basicReps:
            simObj.runSimulation()
            i+=1
            