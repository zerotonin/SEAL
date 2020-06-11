import utilities as util
import turbidity as tb
from importlib import reload 

reload(util)
C= tb.Cloud('test')
C.add_particles()
C.randomInit()

pU = util.plotUtils()
pU.plot3D_positionSizeColorCoded(C.partclObjList)
pU.plot3D_positionRelSize(C.partclObjList)

# test miriam
#test Anna
