import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as numpy


class plotUtils:
    def __init__(self):
        # maybe later on we want to keep our particle object list here
        self.name = 'plotting utilities for turbidity model'

        ''' 
        This class creates a list of position values (x,y,z) and size values (s) of each particle of the Cloud to plot
        each particle in respective size into a squared coordinate system.
         '''
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
    
    def makeSquare3DAxis(self):
        fig = plt.figure()
        ax = Axes3D(fig)
        #ax.set_aspect('equal')
        ax.set_xlim(-10,10)
        ax.set_ylim(-10,10)
        ax.set_zlim(-10,10)
        return fig,ax
        

    def plot3D_positionSizeColorCoded(self,partclObjList):
        
        coordinates = self.particleObjList2CoordList(partclObjList)
        fig,ax = self.makeSquare3DAxis()
        h = ax.scatter3D(coordinates[0], coordinates[1], coordinates[2], c=coordinates[3], cmap='brg')
        fig.colorbar(h)
        fig.show()
    
    def plot3D_positionRelSize(self,partclObjList):

        fig,ax = self.makeSquare3DAxis()

        for particle in partclObjList :
            ax.plot([particle.position[0]],[particle.position[1]],
                    [particle.position[2]], 
                    markerfacecolor='k', markeredgecolor='b', 
                    marker='o', 
                    markersize=particle.size*10000, 
                    alpha=0.85)
        fig.show()