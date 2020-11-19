import utilities as util
import SEAL_SIM
import opticFlowAna
from importlib import reload 

reload(util)
reload(SEAL_SIM)
pU = util.plotUtils()
simObj = SEAL_SIM.SEAL_SIM()

pU.plot_vectorHistogram(SO.pCloud.partclObjList )
simObj.runSimulation()
  

pU.plot3D_positionSizeColorCoded(0,1,simObj.pCloud.partclObjList )
pU.plot3D_positionRelSize(simObj.pCloud.partclObjList,)


reload(util) 
reload(SEAL_SIM) 
reload(opticFlowAna)
pU = util.plotUtils() 
simObj = SEAL_SIM.SEAL_SIM() 
simObj.userDefParametersCLI() 
simObj.runSimulation()   

pU.plot3D_positionSizeColorCoded(100,1,simObj.pCloud.partclObjList )
pU.plot3D_positionSizeColorCoded(100,1,simObj.pCloud.partclObjList )

O = opticFlowAna.opticFlowAnalysis(simObj)
O.opticFlowAbility()
O.plot2DparticleDist(100)