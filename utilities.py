import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as numpy


class plotUtils:
    def __init__(self):
        # maybe later on we want to keep our particle object list here
        self.name = 'plotting utilities for turbidity model'

    def particleObjList2CoordList(self,partclObjList):
        xdata = list()
        ydata = list()
        zdata = list()
        sdata = list()


        for particle in partclObjList :
            xdata.append(particle.position[0])
            ydata.append(particle.position[1])
            zdata.append(particle.position[2])
            sdata.append(particle.size[0])
        
        return (xdata,ydata,zdata,sdata)

    def plot3D_positionSizeColorCoded(self,partclObjList):
        
        coordinates = self.particleObjList2CoordList(partclObjList)
        
        fig = plt.figure()
        ax = Axes3D(fig)
        h = ax.scatter3D(coordinates[0], coordinates[1], coordinates[2], c=coordinates[3], cmap='brg')
        fig.colorbar(h)
        fig.show()
