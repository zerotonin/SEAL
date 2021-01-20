
import numpy as np
import matplotlib.patches as mpatches 
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt


class plot2DProtoMov:
    def __init__(self):

        self.PMtype           =  '3D' # string defining which type of prototypical movement is plotted available types will be 3D thrust,slip yaw and 5D thrust slip lift yaw pitch
        self.PMvelocities     =  [0.75, 0.5 ,-1]   # list with either 3 or 5 entires normalised between -1 and 1 for the velocities
        self.plotOrigin       =  (0.0, 0.0)        # tupel of floats with the center of the coordinates for the PM
        self.velColorList     =  []                # list with colors for the different velocities
        self.edgeColor        = self.keiItoPalette(0)

    def keiItoPalette(self,indice,typeStr='hex'):

        if returnFormat == 'rgb':
            returnFormatIndice = 1
        elif returnFormat == 'cmyk':
            returnFormatIndice = 0
        elif returnFormat == 'hex':
            returnFormatIndice = 3
        elif returnFormat == 'name':
            returnFormatIndice = 4
        else:
            raise ValueError('keiItoPlatte: The return returnFormat is unkown: '+ str(returnFormat))


        data = ([[0.0 ,0.0 ,0.0 ,1.0 ],[0.0 ,0.0 ,0.0 ],'#000000','Black'],
                [[0.0 ,0.5 ,1.0 ,0.0 ],[0.9 ,0.6 ,0.0 ],'#e69f00','Orange'],
                [[0.8 ,0.0 ,0.0 ,0.0 ],[0.35,0.7 ,0.9 ],'#56b4e9','SkyBlue'],
                [[0.97,0.0 ,0.75,0.0 ],[0.0 ,0.6 ,0.50],'#009e73','greenBlue'],
                [[0.10,0.05,0.90,0.00],[0.95,0.90,0.25],'#f0e442','yellow'],
                [[1.00,0.50,0.00,0.00],[0.00,0.45,0.70],'#0072b2','darkBlue'],
                [[0.00,0.80,1.00,0.00],[0.80,0.04,0.00],'#d55e00','vermillion'],
                [[0.10,0.70,0.00,0.00],[0.80,0.60,0.70],'#cc79a7','reddishPurple'])
        
        if type(indice)==int:
            indice = mod(indice,8)
            return data[indice][returnFormatIndice]
        elif type(indice)==list:
            colorList = list()
            for i in indice:
                i = mod(i,8)
                colorList.append(data[i][returnFormatIndice])
            return colorList
        else:
            raise ValueError('keiItoPlatte: The indice type is unkown: '+ str(type(indice))+' . Only int and a list of ints are allowed!')



    def drawYawArrows(self,center, radius, facecolor='#2693de', edgecolor='#000000', theta1=90, theta2=180):
        
        # Add the ring
        rwidth = 0.02
        ring = mpatches.Wedge(center, radius, theta1, theta2, width=rwidth)

        # Triangle edges
        xcent  = center[0] +(radius-rwidth/2)*np.cos(np.deg2rad(theta2))
        ycent  = center[1] +(radius-rwidth/2)*np.sin(np.deg2rad(theta2))
        offset = 0.02
        left   = [xcent  + offset*np.cos(np.deg2rad(theta2)), ycent +offset*np.sin(np.deg2rad(theta2))]
        right  = [xcent  + offset*np.cos(np.deg2rad(theta2)+np.pi), ycent +offset*np.sin(np.deg2rad(theta2)+np.pi)]
        bottom = [xcent  + offset*1.5*np.cos(np.deg2rad(theta2)+np.pi/2), ycent +offset*1.5*np.sin(np.deg2rad(theta2)+np.pi/2)]
        arrow  = plt.Polygon([left, right, bottom, left])
        p = PatchCollection(
            [ring, arrow], 
            edgecolor = edgecolor, 
            facecolor = facecolor
        )
        ax.add_collection(p)
#---------------------------------------------
# Drawing time
#---------------------------------------------
fig, ax = plt.subplots(figsize=(6,6))
drawYawArrows(center=(.5, .7), radius=.1,theta2=120)
drawYawArrows(center=(.2, .2), radius=.15, facecolor='#ffb83c', edgecolor='gray')
drawYawArrows(center=(.8, .3), radius=.15, facecolor='#39c1c8', edgecolor=None)
plt.show()