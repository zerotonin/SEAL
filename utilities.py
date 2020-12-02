import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np


class plotUtils:
    '''
    Class 'plotUtilities' contains functions for creating plots for 3D particles' cloud 
    visialization, for plotting vectors distribution, and for optic flow field visualization 
    '''
    def __init__(self):
        # maybe later on we want to keep our particle object list here
        self.name = 'plotting utilities for turbidity model'

    def particleObjList2CoordList(self,frame,prePost,partclObjList):
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
            xdata.append(particle.trajectory[frame][prePost][0])
            ydata.append(particle.trajectory[frame][prePost][1])
            zdata.append(particle.trajectory[frame][prePost][2])
            sdata.append(particle.size[0])
        
        return (xdata,ydata,zdata,sdata)
    
    def makeSquare3DAxis(self):
        '''
        This function equals axes in 3D plot by giving same limits.

        @return a 3D coordinate system with equal axes, ready to plot input data.
        '''
        fig = plt.figure()# open fig space
        ax = Axes3D(fig)#make 3D plot
        #ax.set_aspect('equal')
        ax.set_xlim(-10,10)# x axes goes from -10 to 10 since Cloudsphere is 10
        ax.set_ylim(-10,10)# same here
        ax.set_zlim(-10,10)

        return fig,ax
        
    def plot3D_positionSizeColorCoded(self,frame,prePost,partclObjList):
        '''
        This function finally returns particles plotted in a 3D coordinate system according to 
        their position and size. Where z - is the depth of the ocean where cloud is located.
        '''
        coordinates = self.particleObjList2CoordList(frame, prePost, partclObjList)
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

        @return the list of values of vector magnitude VctMgn for 
                each particle in the cloud.
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
    systems for particles, and math functions to rotation coordinate in 2D and 3D
    in order to covert the position between seal and world coordinate system
    '''
    def __init__(self):
        """
        @param name           str default: none
            ??
        """
        self.name = 'math utilities for coordinate stuff'

    def cart2sphere(self):
        """
        Converts cartasian coordinates (x = pobject.positison[0],y = pobject.positison[1],
        z = pobject.positison[2]) of pobjects in self.partclObjList to sperical coordinates
        and returns radius, theta, phi coordinates as list of floats.

        r = sqrt(x*x + y*y + z*z)
        theta = atan2((x*x +y*y),z)
        phi = atan2(y,x)

        @return list of radius, theta and phi
        """
        XsqPlusYsq    = self.position[0]**2 + self.position[1]**2
        r             = m.sqrt(XsqPlusYsq + self.position[2]**2)               # r
        theta         = m.atan2(m.sqrt(XsqPlusYsq),self.position[2])     # theta 
        phi           = m.atan2(self.position[1],self.position[0])          # phi not correct 
        self.position = [r,theta,phi]

        return [r,theta,phi]

    def Cloudcart2sphere (self,partclObjList):
        """
        The Cloudcart2sphere function converts the postion of each particle from 
        cartasian coordinates (x,y,z) to spheric coordinates (radius,theta,phi)
        """
        for pobject in self.partclObjList:
            pobject.cart2sphere()

    def agentBasedVels2worldBasedCoords(self,transVel,angles,mode='2D'):
        """
        This function takes the translational velocity of the seal trajectory
        and converts it into positional coordinates within the world 
        coordinate system.

        @return worldBased coordinate vector for both 2D or 3D rotated 
                seal coordinated
        """
        # angle expected to be in radians
        angles = angles*-1 # negative angle as we want to get the xyz shift 
                           # from the orientation of the world and not the seal
        transVel = np.array(transVel) # make sure it is a numpy array
        if mode == '2D':  
            R = self.getRotMatrix2D(angles)
            return np.dot(R,transVel)
        elif mode == '3D':
            R = self.getRotMatrix3D(angles[0],angles[1],angles[2])
            return np.dot(R,transVel) 
        else:
            print('Unknown mode for agentBasedVels2worldBasedCoords func:' + str(mode))
            raise ValueError
    
    def getRotMatrix2D(self,theta):
        """
        This function 
        """
        # theta is in radians
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array(((c, -s), (s, c)))
        
    
    def getRotMatrix3D(self,yaw,pitch,roll,mode='active'):
        # theta is in radians
        cosYaw = np.cos(yaw)
        sinYaw = np.sin(yaw)
        cosPitch = np.cos(pitch)
        sinPitch = np.sin(pitch)
        cosRoll = np.cos(roll)
        sinRoll = np.sin(roll)
        if mode == 'active':
            return np.array(((cosYaw*cosPitch                        , -sinYaw*cosPitch                       , sinPitch         ),
                             (cosYaw*sinPitch*sinRoll+sinYaw*cosRoll , -sinYaw*sinPitch*sinRoll+cosYaw*cosRoll, -cosPitch*sinRoll), 
                             (-cosYaw*sinPitch*cosRoll+sinYaw*sinRoll,  sinYaw*sinPitch*cosRoll+cosYaw*sinRoll, cosPitch*cosRoll)))
        elif mode == 'passive':
            return np.array(((cosYaw*cosPitch,  cosYaw*sinPitch*sinRoll-sinYaw*cosRoll,  cosYaw*sinPitch*cosRoll+sinYaw*sinRoll),
                            (sinYaw*cosPitch ,  sinYaw*sinPitch*sinRoll+cosYaw*cosRoll, sinYaw*sinPitch*cosRoll-cosYaw*sinRoll ),
                            (-sinPitch       ,          cosPitch*sinRoll              ,          cosPitch*cosRoll              )))

        else:
            print('Unknown mode for generating Fick Rotational Matrix:' + str(mode))
            raise ValueError