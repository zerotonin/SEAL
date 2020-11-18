import utilities as util
import SEAL_SIM
from importlib import reload 

reload(util)
pU = util.plotUtils()
SO = SEAL_SIM.SEAL_SIM()

pU.plot_vectorHistogram(SO.pCloud.partclObjList )
SO.runSimulation()
  

pU.plot3D_positionSizeColorCoded(0,1,SO.pCloud.partclObjList )
pU.plot3D_positionRelSize(SO.pCloud.partclObjList,)



