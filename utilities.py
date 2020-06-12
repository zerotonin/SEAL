import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np


class plotUtils:
    def __init__(self):
        # maybe later on we want to keep our particle object list here
        self.name = 'plotting utilities for turbidity model'

        ''' 
        This class creates a list of position values (x,y,z) and size values (s) of each particle of the Cloud to plot
        each particle in respective size into a squared coordinate system.


         '''

    def particleObjList2CoordList(self,partclObjList):
        '''
        This function returns lists of position values x,y,z and size value s of all particles .
        '''
        xdata = list()#create list 
        ydata = list()
        zdata = list()
        sdata = list()


        for particle in partclObjList :# for each particle take certain value and make...
            xdata.append(particle.position[0])# list containing x position 
            ydata.append(particle.position[1])
            zdata.append(particle.position[2])
            sdata.append(particle.size[0])
        
        return (xdata,ydata,zdata,sdata)
    
    def makeSquare3DAxis(self):
        '''
        This function equals axes by giving same limits.
        '''
        fig = plt.figure()# open fig space
        ax = Axes3D(fig)#make 3D plot
        #ax.set_aspect('equal')
        ax.set_xlim(-10,10)# x axes goes from -10 to 10 since Cloudsphere is 10
        ax.set_ylim(-10,10)# same here
        ax.set_zlim(-10,10)
        return fig,ax # returns a 3D coordinate system with equal axes, ready to plot data
        

    def plot3D_positionSizeColorCoded(self,partclObjList):
        '''
        This function finally returns particles plotted in a 3D coordinate system according to their position and size
        '''
        
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

    def VectorMagnitude (VctMgn):
        for particle in partclObjList:
            VctMgn = list()
            VctMgn.append(np.linalg.norm(xdata, ydata, zdata))

            return VctMgn 

    def VectorHistogram ():
        n, bins, patches = plt.hist(x=VctMgn, bins='auto', color='#0504aa',
                                    alpha=0.7, rwidth=0.85)
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Vectors magnitude')
        plt.ylabel('# of Vectors')
        plt.title('Distribution of vectors magnitude')
        plt.show()

        
