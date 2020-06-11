from utilities import plotUtils as pU
import turbidity as tb

C= tb.Cloud('test')
C.add_particles()
C.randomInit()
pU.plot3D_positionSizeColorCoded(C.partclObjList)