
import numpy as np
import matplotlib.patches as mpatches 
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D


class plotProtoMov:
    def __init__(self):

        self.PMtype              =  '3D' # string defining which type of prototypical movement is plotted available types will be 3D thrust,slip yaw and 5D thrust slip lift yaw pitch
        self.PMvelocities        =  [[0.75,-0.15 ,-1],[.3 ,.2,0.01],[-1,.0,.0]]   # list with either 3 or 5 entires normalised between -1 and 1 for the velocities
        self.plotOrigin          =  (0.0, 0.0)        # tupel of floats with the center of the coordinates for the PM
        self.velColorList        =  []                # list with colors for the different velocities
        self.arrowWidth          =  0.1
        self.offset              =  0.15
        self.radius              =  1.25
        self.interPlotStepSize2D = 3.0

    def keiItoPalette(self,indice,returnFormat='hex'):

        if returnFormat == 'rgb':
            returnFormatIndice = 1
        elif returnFormat == 'cmyk':
            returnFormatIndice = 0
        elif returnFormat == 'hex':
            returnFormatIndice = 2
        elif returnFormat == 'name':
            returnFormatIndice = 3
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
            indice = np.mod(indice,8)
            return data[indice][returnFormatIndice]
        elif type(indice)==list:
            colorList = list()
            for i in indice:
                i = np.mod(i,8)
                colorList.append(data[i][returnFormatIndice])
            return colorList
        else:
            raise ValueError('keiItoPlatte: The indice type is unkown: '+ str(type(indice))+' . Only int and a list of ints are allowed!')



    def arrowStrength2ThetaAngle(self,theta1,theta2):
        # Add the ring
        if theta2 < theta1:
            arrowHeadTheta = theta2
            theta2,theta1 = theta1,theta2
            arrowTippOffset = np.pi/-2.0
        else:
            arrowHeadTheta = theta2
            arrowTippOffset = np.pi/2
        
        return theta1,theta2,arrowHeadTheta,arrowTippOffset

    def drawCircleArrows(self,center, facecolor='#c8c8c8', edgecolor='#c8c8c8', theta1=90, theta2=180):
        
        theta1,theta2,arrowHeadTheta,arrowTippOffset = self.arrowStrength2ThetaAngle(self,theta1,theta2)

        ring = mpatches.Wedge(center, self.radius, theta1, theta2, width=self.arrowWidth)

        # Triangle edges
        
        xcent  = center[0] +(self.radius-self.arrowWidth/2)*np.cos(np.deg2rad(arrowHeadTheta))
        ycent  = center[1] +(self.radius-self.arrowWidth/2)*np.sin(np.deg2rad(arrowHeadTheta))
        
        left   = [xcent  + self.offset*np.cos(np.deg2rad(arrowHeadTheta))            , ycent +self.offset*np.sin(np.deg2rad(arrowHeadTheta))]
        right  = [xcent  + self.offset*np.cos(np.deg2rad(arrowHeadTheta)+np.pi)      , ycent +self.offset*np.sin(np.deg2rad(arrowHeadTheta)+np.pi)]
        bottom = [xcent  + self.offset*1.5*np.cos(np.deg2rad(arrowHeadTheta)+arrowTippOffset), ycent +self.offset*1.5*np.sin(np.deg2rad(arrowHeadTheta)+arrowTippOffset)]
        arrow  = plt.Polygon([left, right, bottom, left])
        if theta2-theta1 < 10:
            p = PatchCollection(
                [ring], 
                edgecolor = edgecolor, 
                facecolor = facecolor
            )
        else:
            p = PatchCollection(
                [ring, arrow], 
                edgecolor = edgecolor, 
                facecolor = facecolor
            )
        ax.add_collection(p)
    
    def constructStraightArrow(self,center,orientation,strength):

        
        if orientation == 'vertical':
            xtip = center[0] + 0
            ytip = center[1] + strength
        elif  orientation == 'horizontal':
            xtip = center[0] + strength
            ytip = center[1] + 0
        else:
            raise ValueError('constructStraightArrow: The orientation  is unkown: '+ str(orientation)+' . Only vertical and horizontal are allowed!')
        
        # arrow angle
        if strength < 0:
            a_angle = np.arctan2(center[1]-ytip,center[0]-xtip)
            headOffset = strength+self.offset*1.5
        else:
            a_angle = np.arctan2(center[1]-ytip,center[0]-xtip) - np.pi
            headOffset= strength-self.offset*1.5

        a_angleOrthogonal = a_angle -np.pi/2
        wingOffset = self.offset-self.arrowWidth/2

        #arrow base left
        abl = [center[0]  + self.arrowWidth/2*np.cos(a_angleOrthogonal)      , center[1] +self.arrowWidth/2*np.sin(a_angleOrthogonal)]
        #arrow base right
        abr = [center[0]  + self.arrowWidth/2*np.cos(a_angleOrthogonal+np.pi), center[1] +self.arrowWidth/2*np.sin(a_angleOrthogonal+np.pi)]
        #arrowTipp
        atp = [xtip,ytip]
        if np.abs(strength) < self.offset*1.5:
            #arrow head left
            ahl = [atp[0]  + self.arrowWidth/2*np.cos(a_angleOrthogonal)      , atp[1] +self.arrowWidth/2*np.sin(a_angleOrthogonal)]
            #arrow head right
            ahr = [atp[0]  + self.arrowWidth/2*np.cos(a_angleOrthogonal+np.pi), atp[1] +self.arrowWidth/2*np.sin(a_angleOrthogonal+np.pi)]
            #compose patch
            nodeList  = [abl, abr, ahr,ahl, abl]
        else:
            #arrow neck left    
            anl = [abl[0]  + headOffset*np.cos(a_angle)                          , abl[1] +headOffset*np.sin(a_angle)]
            #arrow wing left
            awl = [anl[0]  + wingOffset*np.cos(a_angleOrthogonal)                , anl[1] +wingOffset*np.sin(a_angleOrthogonal)]
            #arrow neck right
            anr = [abr[0]  + headOffset*np.cos(a_angle)                          , abr[1] +headOffset*np.sin(a_angle)]
            #arrow wing right
            awr = [anr[0]  + wingOffset*np.cos(a_angleOrthogonal+np.pi)          , anr[1] +wingOffset*np.sin(a_angleOrthogonal+np.pi)]
            #compose patch
            nodeList = [abl, abr, anr,awr, atp, awl, anl, abl]
        return nodeList
     
    def drawStraightArrow2D(self, center,facecolor='#c8c8c8',edgecolor='#c8c8c8',orientation='vertical',strength = -1.0):
        nodeList = self.constructStraightArrow(center,orientation,strength)
        arrow  = plt.Polygon(nodeList,edgecolor = edgecolor, facecolor = facecolor)
        ax.add_patch(arrow)
    
    def drawStraightArrow3D(self, center,facecolor='#c8c8c8',edgecolor='#c8c8c8',orientation='vertical',strength = 1.0):
        if orientation == 'orthogonal':
            nodeList = self.constructStraightArrow(center,'vertical',strength)
            #add a zero to all entries, but because the first and last pointer point to the same node, we ignore the first.
            [a.insert(0,0.) for a in nodeList[1::]]
        else:
            nodeList = self.constructStraightArrow(center,orientation,strength)
            #add a zero to all entries, but because the first and last pointer point to the same node, we ignore the first.
            [a.append(0.) for a in nodeList[1::]]

        tri = Poly3DCollection(np.array([nodeList]))
        tri.set_color(facecolor)
        tri.set_edgecolor(edgecolor)
        ax.add_collection3d(tri)

    def drawAxisBackGround3F(self,center):
        self.drawStraightArrow2D(center,orientation='vertical',strength=1.0)
        self.drawStraightArrow2D(center,orientation='vertical',strength=-1.0)
        self.drawStraightArrow2D(center,orientation='horizontal',strength=1.0)
        self.drawStraightArrow2D(center,orientation='horizontal',strength=-1.0)
        self.drawCircleArrows(center, theta2=180)
        self.drawCircleArrows(center, theta2=0)

    def drawAxisBackGround6F(self,center):
        self.drawStraightArrow3D(center,orientation='vertical',strength=1.0)
        self.drawStraightArrow3D(center,orientation='vertical',strength=-1.0)
        self.drawStraightArrow3D(center,orientation='horizontal',strength=1.0)
        self.drawStraightArrow3D(center,orientation='horizontal',strength=-1.0)
        self.drawStraightArrow3D(center,orientation='orthogonal',strength=1.0)
        self.drawStraightArrow3D(center,orientation='orthogonal',strength=-1.0)

    def draw2DPrototype(self,center,PMVel,PMID=''):
        self.drawAxisBackGround3F(center)
        self.drawStraightArrow2D(center,orientation='vertical'  ,strength=PMVel[0],facecolor=pPM.keiItoPalette(0))
        self.drawStraightArrow2D(center,orientation='horizontal',strength=PMVel[1],facecolor=pPM.keiItoPalette(1))
        thetaAngle = np.pi/2 - (np.pi/2*PMVel[2])
        self.drawCircleArrows(center, theta2=np.rad2deg(thetaAngle),facecolor=pPM.keiItoPalette(2))
        ax.annotate(PMID,(center[0]-self.interPlotStepSize2D/2.+0.2,center[1]+self.interPlotStepSize2D/2.-0.2))

    def squareSubplotArrangement(self,PMnum):
        rows = int(np.ceil(np.sqrt(PMnum)))
        cols = int(np.ceil(PMnum/rows))
        return rows,cols
    
    def getCentersforPMs(self,PMnum,firstCenter = (0,0)):

        xOffset    = 0.0
        yOffset    = 0.0
        self.interPlotStepSize2D   = 3.0
        centerList = list()
        rows,cols  = self.squareSubplotArrangement(PMnum)
        
        for j in range(rows):
            for i in range(cols):
                centerList.append([firstCenter[0]+xOffset,firstCenter[0]+yOffset])
                xOffset += self.interPlotStepSize2D
            xOffset    = 0.0
            yOffset += -1*self.interPlotStepSize2D
        return np.array(centerList)
    
    def plot2DPMset(self):
        self.PMvelocities     = np.array(self.PMvelocities)
        PMnum = self.PMvelocities.shape[0]
        centerList = self.getCentersforPMs(PMnum)
        for pmI in range(PMnum):
            self.draw2DPrototype(centerList[pmI],self.PMvelocities[pmI,0:3],PMID=str(pmI+1))
        
        plt.xlim([centerList[0,0]-self.interPlotStepSize2D/2.,centerList[-1,0]+self.interPlotStepSize2D/2.])
        plt.ylim([centerList[-1,1]-self.interPlotStepSize2D/2.,centerList[0,1]+self.interPlotStepSize2D/2.])
        ax.set_aspect('equal','box')
        plt.axis('off')
        
#---------------------------------------------
# Drawing time
#---------------------------------------------

pPM = plotProtoMov()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
pPM.drawAxisBackGround6F((0,0))
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])
ax.set_xlabel('x')
ax.view_init(elev=30, azim=0)
plt.show()

# PMs  = np.genfromtxt('/home/bgeurten/ownCloud/personalSwaps/SealSim/clustering/data/protoMov.csv',delimiter=',')
# norm = np.max(np.abs(PMs),0)
# PMs[:,0:2] =PMs[:,0:2]/np.max(norm[0:2])
# PMs[:,2] =PMs[:,2]/norm[2]
# pPM = plotProtoMov()
# fig, ax = plt.subplots(figsize=(6,6))
# pPM.PMvelocities = PMs
# pPM.plot2DPMset()
# plt.show()