import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np


class plotUtils:
    '''
    Class 'plotUtilities' contains functions for creating plots for 3D particles' cloud 
    visialization and for plotting vectors distribution
    '''
    def __init__(self):
        # maybe later on we want to keep our particle object list here
        self.name = 'plotting utilities for turbidity model'

        ''' 
        This class creates a list of position values (x,y,z) and size values (s) of each particle of the 
        Cloud to plot each particle in respective size into a squared coordinate system.
         '''

    def particleObjList2CoordList(self,partclObjList):
        '''
        This function returns lists of position values x,y,z and size value s of all particles from
        partclObjList.
        @return four lists with x,y,z positions and particles sizes.
        '''
        xdata = list()#create list of x coordinated
        ydata = list()#create list of y coordinated
        zdata = list()#create list of z coordinated
        sdata = list()#create list of particles' sizes


        for particle in partclObjList :
            xdata.append(particle.position[0])
            ydata.append(particle.position[1])
            zdata.append(particle.position[2])
            sdata.append(particle.size[0])
        
        return (xdata,ydata,zdata,sdata)
    
    def makeSquare3DAxis(self):
        '''
        This function equals axes in 3D plot by giving same limits.
        @ return a 3D coordinate system with equal axes, ready to plot input data.
        '''
        fig = plt.figure()# open fig space
        ax = Axes3D(fig)#make 3D plot
        #ax.set_aspect('equal')
        ax.set_xlim(-10,10)# x axes goes from -10 to 10 since Cloudsphere is 10
        ax.set_ylim(-10,10)# same here
        ax.set_zlim(-10,10)
        return fig,ax
        

    def plot3D_positionSizeColorCoded(self,partclObjList):
        '''
        This function finally returns particles plotted in a 3D coordinate system according to 
        their position and size. Where z - is the depth of the ocean where cloud is located.
        '''
        
        coordinates = self.particleObjList2CoordList(partclObjList)
        fig,ax = self.makeSquare3DAxis()
        h = ax.scatter3D(coordinates[0], coordinates[1], coordinates[2], c=coordinates[3], cmap='brg')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Depth (m)')
        fig.colorbar(h)
        fig.show()
    
    def plot3D_positionRelSize(self,partclObjList):
        '''
        Function that builds 3d graph with zoomed * 10^3 particles sizes for better visualization 
        due to the small size of particles.
        '''

        fig,ax = self.makeSquare3DAxis()

        for particle in partclObjList :
            ax.plot([particle.position[0]],[particle.position[1]],
                    [particle.position[2]], 
                    markerfacecolor='k', markeredgecolor='b', 
                    marker='o', 
                    markersize=particle.size*10000, 
                    alpha=0.85)
        fig.show()

    def VectorMagnitude(self,partclObjList):
        '''
        This function might take coordinates for x,y,z of particle.
        @return the list of values of vector magnitude VctMgn for each particle in the cloud.
        '''

        VctMgn = list()
        for particle in partclObjList:
            VctMgn.append(np.linalg.norm(particle.position))

        return VctMgn 

    def plot_vectorHistogram(self,partclObjList):
        '''
        This function plots the distribution of the particles's vectors magnitude in the 
        visual field of a seal
        '''
        VctMgn = self.VectorMagnitude(partclObjList)

        fig = plt.figure()# open fig space
        n, bins, patches = plt.hist(x=VctMgn, bins='auto', color='#0504aa',
                                    alpha=0.7, rwidth=0.85)
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Vectors magnitude')
        plt.ylabel('# of Vectors')
        plt.title('Distribution of vectors magnitude')
        plt.show()

    

class mathUtils:
    '''
    This class contains tools for switching between cartesian and spheric coordinate
    systems for particles.
    '''
    def __init__(self):
        self.name = 'math utilities for coordinate stuff'

    def cart2sphere(self):
       """
       Converts cartasian coordinates (x = pobject.positison[0],y = pobject.positison[1],
       z = pobject.positison[2]) of pobjects in self.partclObjList to sperical coordinates
       and returns radius, theta, phi coordinates as list of floats.
       r = sqrt(x*x + y*y + z*z)
       theta = atan2((x*x +y*y),z)
       phi = atan2(y,x)
       """
       XsqPlusYsq = self.position[0]**2 + self.position[1]**2
       r = m.sqrt(XsqPlusYsq + self.position[2]**2)               # r
       theta = m.atan2(m.sqrt(XsqPlusYsq),self.position[2])     # theta 
       phi = m.atan2(self.position[1],self.position[0])          # phi not correct 
       self.position = [r,theta,phi]
       return [r,theta,phi]

    def sphere2cart (self): 
        """
        Converts spheric coordinates(r = pobject.positison[0],theta = pobject.positison[1],
        phi = pobject.positison[2]) of pobjects in self.partclObjList to cartasian coordinates
        and returns x,y,z coordinates as a list
        """
        # attempt to convert spheric coordinates of our pobjects in our self.partclObjList to cartasian coordinates 
        #take list
        x = self.position[0] * np.sin( self.position[1] ) * np.cos( self.position[2] )
        y = self.position[0] * np.sin( self.position[1] ) * np.sin( self.position[2] )
        z = self.position[0] * np.cos( self.position[1] )
        self.position = [x,y,z]
        self.particleStateCheck()
        return [x,y,z] # this is just giving me one set of changed Coordinates and is not changing the whole list 

    def multiplyBySphereMax(self,coordinate):
        """
        The multiplyBySphereMax function is creating the mathematic setting for the coordinats in 
        the spheric coordinate system (0=radius,1=theta,2=phi). defining 
            radius by radiusMax
            theta by np.pi describing a range between (0-180°)
            phi by np.pi*2-np.pi describing a range between ((-180°)-180°)
        """
        sphereCoord = np.empty(3)
        sphereCoord[0] = coordinate[0]*self.radiusMax
        sphereCoord[1] = coordinate[1]*np.pi
        sphereCoord[2] = coordinate[2]*np.pi*2-np.pi
        return sphereCoord

################## Unused stuff
    #def Cloudsphere2cart (self):
    #    """
    #    The Cloudsphere2cart function converts the postions of each particle from 
    #    spheric coordinates (radius,theta,phi) to cartasian coordinates (x,y,z)
    #    """
    #    for pobject in self.partclObjList:
    #        pobject.sphere2cart()
#
    #def Cloudcart2sphere (self):
    #    """
    #    The Cloudcart2sphere function converts the postion of each particle from 
    #    cartasian coordinates (x,y,z) to spheric coordinates (radius,theta,phi)
    #    """
    #    for pobject in self.partclObjList:
    #        pobject.cart2sphere()
    #    def CloudDepth2Temperature(self):
    #    """
    #    The CloudDepth2Temperature function calls all particle objects in the Cloud 
    #    which are between surface and seafloor and calculates the temperature for
    #    every particle. This information will be needed for the temperature dependent
    #    brownian motion of the particles.
    #    """
    #    for pobject in self.partclObjList:
    #        if pobject.activeMovement == True:
    #            pobject.depth2Temperature()