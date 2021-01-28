
import numpy as np 
import SEAL_SIM, opticFlowAna
import matplotlib.pyplot as plt 
 
# cluster translational 5D PMs plus 0.0 for roll
TranslaPM = ([[1.8609,0.44391, -0.072173, -0.52564,  -0.0011278, 0.0],
              [1.4749,0.96914,  0.020206, -0.049538, -0.0048028, 0.0],
              [1.0312,-0.33755,-0.10574,  -0.023993, -0.0041735, 0.0],
              [1.6527,0.3865,  -0.052242,  0.0060586,-0.93312,   0.0],
              [1.6259,0.39059, -0.010533,  0.008956,  0.84291,   0.0],
              [1.1163,0.33908, -2.5045,    0.033083,  0.00027863,0.0],
              [3.7257,1.4087,   0.058942,  0.041954, -0.0015622, 0.0],
              [3.6564,-0.48179, 0.1856,    0.095942,  0.0022598, 0.0],
              [1.5748,0.45007,  0.051904,  0.35187,  -0.0064602, 0.0]])

RotationalPM = ([[1.8268,  0.01529,  -0.15939, 2.1617,    0.0054881, 0.0],#yaw right
                 [1.7163,  0.79161,  -0.13845,-2.2299,    0.00061883,0.0],#yaw left
                 [0.27325, 0.10791,   0.26439,-0.0018402,-2.9212,    0.0],#pitch down
                 [-0.10417,0.0054149,-0.019695,0.0048984, 2.2828,    0.0]])#pitch up
# diveType to simulate


# single plot should give hammer projection overview and zoomed in visual field
# for all 9 PMs for a given current 

#1 plot: all translational and rotational data in high turbidty middle of the ocean for u and v shape
# describing flow filed during translation and rotation.
dt = 'uShape'
# translational PMs

fig = plt.figure(figsize=(5.27, 18.69), dpi=100)
fig.suptitle('Translational PMs', fontsize=16)
for pm in range(len(TranslaPM)):
    simObj = SEAL_SIM.SEAL_SIM('headless', spsInt=10000, maxParticlesInt=770, durSecFloat=2/10000,currentStaticVelTuple=(0.0,0.0,0.0), diveTypeStr= dt  )
    simObj.runSimulationSingleStep(np.array(TranslaPM[pm]),np.array([0.,0.,-33.0]),np.array([0.,0.,0.]))
    simObj.opticFlowAna.plotOpticFlow(0,subPlot=fig.add_subplot(9,2,pm*2+1, projection = 'hammer'), figure= fig,showStartEnd = False, plotFigure=False)
    
    simObj.opticFlowAna.plotOpticFlow(0,subPlot=fig.add_subplot(9,2,pm*2+2), figure= fig, showStartEnd = False, projectionType ='', viewField = True, plotFigure=False) 
plt.show()

# rotational PMs

fig = plt.figure(figsize=(8.27, 11.69), dpi=100)

fig.suptitle('Rotational PMs', fontsize=16)
for pm in range(len(RotationalPM)):
    simObj = SEAL_SIM.SEAL_SIM('headless', spsInt=10000, maxParticlesInt=770, durSecFloat=2/10000,currentStaticVelTuple=(0.0,0.0,0.0), diveTypeStr= dt )
    simObj.runSimulationSingleStep(np.array(RotationalPM[pm]),np.array([0.,0.,-33.0]),np.array([0.,0.,0.]))
    simObj.opticFlowAna.plotOpticFlow(0,subPlot=fig.add_subplot(4,2,pm*2+1, projection = 'hammer'), figure= fig,showStartEnd = False, plotFigure=False)
    simObj.opticFlowAna.plotOpticFlow(0,subPlot=fig.add_subplot(4,2,pm*2+2), figure= fig, showStartEnd = False, projectionType ='', viewField = True, plotFigure=False) 
plt.show()

############################################################################################
# choose two tranlational(fast and slow) and one rotational (pitch down) PM for further 
# analysis
ThreePMs = ([[3.6564,-0.48179, 0.1856,    0.095942,  0.0022598, 0.0],
             [1.4749,0.96914,  0.020206, -0.049538, -0.0048028, 0.0],
             [1.7163,  0.79161,  -0.13845,-2.2299,    0.00061883,0.0]])

# simulate differen turbidity 1000 p/cm3, 10000 p/cm3, 35000p/cm3
# https://www.tandfonline.com/doi/abs/10.3402/tellusb.v35i5.14624
turbidty = (22,220,770)

# Test turbidty


for pm in range(len(ThreePMs)):
    fig = plt.figure()
    fig.subplots_adjust(left=0.125, right=0.9, bottom=0.1, top=0.9,wspace=0.25, hspace=0.5)
    fig.suptitle('Turbidty: PM'+str(pm+1), fontsize=16)
    positionValue = 0
    for t in range(len(turbidty)):
        simObj = SEAL_SIM.SEAL_SIM('headless', spsInt=10000, maxParticlesInt=turbidty[t], durSecFloat=2/10000,currentStaticVelTuple=(0.0,0.0,0.0), diveTypeStr= dt )
        simObj.runSimulationSingleStep(np.array(ThreePMs[pm]),np.array([0.,0.,-33.0]),np.array([0.,0.,0.]))
        simObj.opticFlowAna.plotOpticFlow(0,subPlot=fig.add_subplot(3,2,t*2+1+positionValue, projection = 'hammer'), figure= fig,showStartEnd = False, plotFigure=False)
        simObj.opticFlowAna.plotOpticFlow(0,subPlot=fig.add_subplot(3,2,t*2+2+positionValue), figure= fig, showStartEnd = False, projectionType ='', viewField = True, plotFigure=False) 
        
        print(positionValue)
    
plt.show()

############################################################################################
# for high turbidity 770 particles we want to test different currents 

# optional current ranging from 40 to 0 cm/s in the y plane,
# plus one complex current shifting 40 cm/s in all 3 dimensions 
Currents = ([[0.0,0.0,0.0],
             [0.0,0.2,0.0],
             [0.0,0.4,0.0],
             [0.4,0.4,0.4]])

fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
fig.suptitle('Currents', fontsize=16)

for pm in range(len(ThreePMs)):
    for c in range(len(Currents)):
        colorChoice = ('#000000','#e69f00','#56b4e9','#009e73')
        simObj = SEAL_SIM.SEAL_SIM('headless', spsInt=10000, maxParticlesInt=770, durSecFloat=2/10000,currentStaticVelTuple=Currents[c], diveTypeStr= dt )
        simObj.runSimulationSingleStep(np.array(ThreePMs[pm]),np.array([0.,0.,-33.0]),np.array([0.,0.,0.]))
        simObj.opticFlowAna.plotOpticFlow(0,subPlot=fig.add_subplot(3,2,pm*2+1, projection = 'hammer'), figure= fig,showStartEnd = False, plotFigure=False, color=colorChoice[c])
        simObj.opticFlowAna.plotOpticFlow(0,subPlot=fig.add_subplot(3,2,pm*2+2), figure= fig, showStartEnd = False, projectionType ='', viewField = True, plotFigure=False, color=colorChoice[c]) 
plt.show()

##################################################################################################
# run simulation without currents in different depth 

# simulate 3 depth, close to surface, middle of the ocean
# and close to the sea floor
depth = ([[0.0,0.0,-0.01],
          [0.0,0.0,-35.0],
          [0.0,0.0,-69.9999]])


fig = plt.figure(figsize=(5.27, 11.69), dpi=100)

fig.suptitle('Depth', fontsize=16)
positionValue = 0
for pm in range(len(ThreePMs)):
    for c in range(len(depth)):
        simObj = SEAL_SIM.SEAL_SIM('headless', spsInt=10000, maxParticlesInt=770, durSecFloat=2/10000,currentStaticVelTuple=(0.0,0.0,0.0), diveTypeStr= dt )
        simObj.runSimulationSingleStep(np.array(ThreePMs[pm]),np.array(depth[c]),np.array([0.,0.,0.]))
        simObj.opticFlowAna.plotOpticFlow(0,subPlot=fig.add_subplot(9,2,c*2+1+positionValue, projection = 'hammer'), figure= fig,showStartEnd = False, plotFigure=False)
        simObj.opticFlowAna.plotOpticFlow(0,subPlot=fig.add_subplot(9,2,c*2+2+positionValue), figure= fig, showStartEnd = False, projectionType ='', viewField = True, plotFigure=False) 
        
        print(positionValue)
    positionValue = positionValue+6
plt.show()
