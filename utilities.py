import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import math as m


class plotUtils:
    '''
    Class 'plotUtilities' contains functions for creating plots for 3D particles' cloud 
    visialization, for plotting vectors distribution, and for optic flow field visualization 
    '''

    def __init__(self, simObj):
        # maybe later on we want to keep our particle object list here
        self.name = 'plotting utilities for turbidity model'
        self.simObj = simObj

    def particleObjList2CoordList(self, frame, prePost, partclObjList):
        '''
        This function returns lists of position values x,y,z and size value s of all particles from
        partclObjList.
        @return four lists with x,y,z positions and particles sizes.
        '''
        xdata = list()  # create list of x coordinated
        ydata = list()  # create list of y coordinated
        zdata = list()  # create list of z coordinated
        sdata = list()  # create list of particles' sizes

        for particle in partclObjList:
            xdata.append(particle.trajectory[frame][prePost][0])
            ydata.append(particle.trajectory[frame][prePost][1])
            zdata.append(particle.trajectory[frame][prePost][2])
            sdata.append(particle.size[0])

        return (xdata, ydata, zdata, sdata)

    def makeSquare3DAxis(self):
        '''
        This function equals axes in 3D plot by giving same limits.

        @return a 3D coordinate system with equal axes, ready to plot input data.
        '''
        fig = plt.figure()  # open fig space
        ax = Axes3D(fig)  # make 3D plot
        # ax.set_aspect('equal')
        # x axes goes from -10 to 10 since Cloudsphere is 10
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)  # same here
        ax.set_zlim(-10, 10)

        return fig, ax

    def plot3D_positionSizeColorCoded(self, frame, prePost, partclObjList):
        '''
        This function finally returns particles plotted in a 3D coordinate system according to 
        their position and size. Where z - is the depth of the ocean where cloud is located.
        '''
        coordinates = self.particleObjList2CoordList(
            frame, prePost, partclObjList)
        fig, ax = self.makeSquare3DAxis()
        h = ax.scatter3D(coordinates[0], coordinates[1],
                         coordinates[2], c=coordinates[3], cmap='brg')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Depth (m)')
        fig.colorbar(h)
        fig.show()

    def plot3D_positionsMovement(self, frame, partclObjList):
        '''
        This function plots the prePositions of all particle for a specifc frame in red
        and all postPositions in green.
        '''

        preCoordinates = self.particleObjList2CoordList(
            frame, 0, partclObjList)
        postCoordinates = self.particleObjList2CoordList(
            frame, 1, partclObjList)
        fig, ax = self.makeSquare3DAxis()
        h = ax.scatter3D(
            preCoordinates[0], preCoordinates[1], preCoordinates[2], color='red')
        h = ax.scatter3D(
            postCoordinates[0], postCoordinates[1], postCoordinates[2], color='green')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Depth (m)')
        fig.show()

    def plot3D_OF(self, frame, partclObjList, sealTrajectory):
        '''
        This function plot both, the particle movement (red to green)for a specific frame
        as well as the sealStep(magenta) and heading(green). 
        '''
        # plot pre and post position of particle with direction vector
        preCoordinates = self.particleObjList2CoordList(
            frame, 0, partclObjList)
        postCoordinates = self.particleObjList2CoordList(
            frame, 1, partclObjList)
        direct = np.subtract(postCoordinates, preCoordinates)
        fig, ax = self.makeSquare3DAxis()
        ax.scatter3D(preCoordinates[0], preCoordinates[1],
                     preCoordinates[2], color='red')
        ax.scatter3D(
            postCoordinates[0], postCoordinates[1], postCoordinates[2], color='green')
        X = preCoordinates[0]
        Y = preCoordinates[1]
        Z = preCoordinates[2]
        U = direct[0]
        V = direct[1]
        W = direct[2]
        ax.quiver(X, Y, Z, U, V, W, arrow_length_ratio=0.03, color='black')
        # plot sealStep direction from simObj.runTimeData.sealTrajectory(x,y,z)
        # sealStep = np.subtract(sealTrajectory[frame+1],sealTrajectory[frame]) # sealTrajectory --> simObj.runTimeData.sealTrajectory[0:3]
        # ax.scatter3D(sealStep[0],sealStep[1],sealStep[2])
        #ax.quiver(0,0,0,sealStep[0],sealStep[1],sealStep[2], color ='red')
        # or:
        R = self.simObj.math.getRotMatrix3D(
            sealTrajectory[frame][3:][0], sealTrajectory[frame][3:][1], sealTrajectory[frame][3:][2], 'passive')
        sealStep3 = np.dot(
            R, (np.subtract(sealTrajectory[frame+1][0:3], sealTrajectory[frame][0:3])))
        ax.scatter3D(sealStep3[0], sealStep3[1], sealStep3[2])
        ax.quiver(0, 0, 0, sealStep3[0],
                  sealStep3[1], sealStep3[2], color='red')
        # or:
        # sealStep1 = self.simObj.runTimeData.velTra[frame][0:3]/self.simObj.runTimeData.sps # sealTrajectors --> simObj.runTimeData.velTra
        # ax.scatter3D(sealStep1[0],sealStep1[1],sealStep1[2])
        #ax.quiver(0,0,0,sealStep1[0],sealStep1[1],sealStep1[2], color ='magenta')

        # plot the heading vector during the sealStep taken from the sealTrajectory from the plotted seal
        # yawAngle, pitchAngle, rollAngle
        # headingVector=np.array([0.01,0,0])
        self.sealHeading = self.simObj.protoMove.sealHeading[frame]
        self.sealHeading1 = sealTrajectory[frame][3:]
        #ax.quiver(0,0,0,self.sealHeading[0]*0.01,self.sealHeading[1]*0.01,self.sealHeading[2]*0.01, color ='green')
        ax.quiver(0, 0, 0, self.sealHeading1[0]*0.01, self.sealHeading1[1]*0.01, self.sealHeading1[2]*0.01, color='magenta')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Depth (m)')
        fig.show()
    def plot3D_positionRelSize(self, partclObjList):
        '''
        Function that builds 3d graph with zoomed * 10^3 particles sizes for better visualization 
        due to the small size of particles.
        '''
        fig, ax = self.makeSquare3DAxis()

        for particle in partclObjList:
            ax.plot([particle.position[0]], [particle.position[1]],
                    [particle.position[2]],
                    markerfacecolor='k', markeredgecolor='b',
                    marker='o',
                    markersize=particle.size*10000,
                    alpha=0.85)
        fig.show()

    def VectorMagnitude(self, partclObjList):
        '''
        This function might take coordinates for x,y,z of particle.

        @return the list of values of vector magnitude VctMgn for 
                each particle in the cloud.
        '''
        VctMgn = list()
        for particle in partclObjList:
            VctMgn.append(np.linalg.norm(particle.position))

        return VctMgn

    def plot_vectorHistogram(self, partclObjList):
        '''
        This function plots the distribution of the particles's vectors magnitude in the 
        visual field of a seal
        '''
        VctMgn = self.VectorMagnitude(partclObjList)

        fig = plt.figure()  # open fig space
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
        """
        self.name = 'math utilities for coordinate stuff'

    def cart2sphere(self, position):
        """
        Converts cartasian coordinates (x = pobject.positison[0],y = pobject.positison[1],
        z = pobject.positison[2]) of pobjects in self.partclObjList to sperical coordinates
        and returns radius, theta, phi coordinates as list of floats.

        r = sqrt(x*x + y*y + z*z)
        theta = atan2((x*x +y*y),z)
        phi = atan2(y,x)

        @return list of radius, theta and phi
        """
        XsqPlusYsq = position[0]**2 + position[1]**2
        r = m.sqrt(XsqPlusYsq + position[2]**2)               # r
        theta = m.atan2(m.sqrt(XsqPlusYsq), position[2])     # theta
        phi = m.atan2(position[1], position[0])         # phi not correct
        self.position = [r, theta, phi]

        return [r, theta, phi]

    def Cloudcart2sphere(self, partclObjList):
        """
        The Cloudcart2sphere function converts the postion of each particle from 
        cartasian coordinates (x,y,z) to spheric coordinates (radius,theta,phi)
        """
        for pobject in partclObjList:
            pobject.cart2sphere()

    def agentBasedVels2worldBasedCoords(self, transVel, angles, mode='2D'):
        """
        This function takes the translational velocity of the seal trajectory
        and converts it into positional coordinates within the world 
        coordinate system.

        @return worldBased coordinate vector for both 2D or 3D rotated 
                seal coordinated
        """
        # angle expected to be in radians
        angles = angles*-1  # negative angle as we want to get the xyz shift
        # from the orientation of the world and not the seal
        transVel = np.array(transVel)  # make sure it is a numpy array
        if mode == '2D':
            R = self.getRotMatrix2D(angles)
            return np.dot(R, transVel)
        elif mode == '3D':
            R = self.getRotMatrix3D(angles[0], angles[1], angles[2])
            return np.dot(R, transVel)
        else:
            print('Unknown mode for agentBasedVels2worldBasedCoords func:' + str(mode))
            raise ValueError

    def getRotMatrix2D(self, theta):
        """
        This function creates a rotation matrix in order to rotate
        a 2D vector arround a angle (theta)

        @return 2x2 rotation matrix 
                [c,-s]
                [s, c]
        """
        # theta is in radians
        c = np.cos(theta)
        s = np.sin(theta)

        return np.array(((c, -s), (s, c)))

    def getRotMatrix3D(self, yaw, pitch, roll, mode='active'):
        """
        This function creates a 3D rotation matrix in order
        to rotate activly or passivly around the three given 
        angles (yaw, pitch, roll)

        @return 3x3 rotation matrix based on sinus and cosinus from yaw pitch and roll
        """
        # theta is in radians
        cosYaw = np.cos(yaw)
        sinYaw = np.sin(yaw)
        cosPitch = np.cos(pitch)
        sinPitch = np.sin(pitch)
        cosRoll = np.cos(roll)
        sinRoll = np.sin(roll)
        if mode == 'active':
            return np.array(((cosYaw*cosPitch, -sinYaw*cosPitch, sinPitch),
                             (cosYaw*sinPitch*sinRoll+sinYaw*cosRoll, -sinYaw *
                              sinPitch*sinRoll+cosYaw*cosRoll, -cosPitch*sinRoll),
                             (-cosYaw*sinPitch*cosRoll+sinYaw*sinRoll,  sinYaw*sinPitch*cosRoll+cosYaw*sinRoll, cosPitch*cosRoll)))
        elif mode == 'passive':
            return np.array(((cosYaw*cosPitch,  cosYaw*sinPitch*sinRoll-sinYaw*cosRoll,  cosYaw*sinPitch*cosRoll+sinYaw*sinRoll),
                             (sinYaw*cosPitch,  sinYaw*sinPitch*sinRoll+cosYaw *
                              cosRoll, sinYaw*sinPitch*cosRoll-cosYaw*sinRoll),
                             (-sinPitch,          cosPitch*sinRoll,          cosPitch*cosRoll)))

        else:
            print('Unknown mode for generating Fick Rotational Matrix:' + str(mode))
            raise ValueError
