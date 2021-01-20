
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
# diveType to simulate
diveType = ('uShape','vShape')
# optional current ranging from 40 to 0 cm/s in the y plane,
# plus one complex current shifting 40 cm/s in all 3 dimensions 
Currents = ((0.0,0.4,0.0),
            (0.0,0.3,0.0),
            (0.0,0.2,0.0),
            (0.0,0.1,0.0),
            (0.0,0.0,0.4),
            (0.0,0.0,0.0),
            (0.4,0.4,0.4))
# simulate 3 depth, close to surface, middle of the ocean
# and close to the sea floor
depth = (-0.0001,-35, -69.9999)

# simulate differen turbidity 1000 p/cm3, 10000 p/cm3, 35000p/cm3
# https://www.tandfonline.com/doi/abs/10.3402/tellusb.v35i5.14624
particles = (22, 200, 770)


# single plot should give hammer projection overview and zoomed in visual field
# for all 9 PMs for a given current 

for dt in diveType:
    for c in Currents:
        for d in depth:
            
            fig = plt.figure()
            index = 0

            for pm in range(len(TranslaPM)):
                
                simObj = SEAL_SIM.SEAL_SIM('headless', spsInt=10000, maxParticlesInt=770, durSecFloat=2/10000,currentStaticVelTuple=(0.0,0.4,0.0), diveTypeStr='uShape' )
                simObj.runSimulationSingleStep([1.8609,0.44391, -0.072173, -0.52564,  -0.0011278, 0.0],np.array([0.,0.,-33]),np.array([0.,0.,0.]))
                 
                frame =0
                
                ax = fig.add_subplot(9,2,pm*2+1, projection = 'hammer')
                print(index)
                #for specific frame it calcultates the magnitute between the old and new position of each visibile? particle
                for i in range(len(simObj.opticFlowAna.particleList)): # po should be (oldPosition, newPosition, status) of particle per movement
                    direct = simObj.opticFlowAna.anaDataList[frame][3][i]
                    if  simObj.opticFlowAna.anaDataList[frame][2][i] != None: # richtungsvector between frames
                        X = simObj.opticFlowAna.anaDataList[frame][2][i][0][2] # phi
                        Y = simObj.opticFlowAna.anaDataList[frame][2][i][0][1] # theta
                        U = direct[2] # phi direction
                        V = direct[1] # theta direction
                        ax.quiver(X,Y,U,V,angles ='xy',scale_units='xy', scale =1,width=0.001, color='midnightblue', alpha=0.7, zorder=2)
                    else:
                        pass
                    
                x = ([-1.815,-1.815,1.815,1.815,-1.815])
                y = ([-0.209,1.204,1.204,-0.209,-0.209])
                ax.plot(x,y, zorder=1, color= 'forestgreen', linewidth= 2.0)

                ax.set_xlabel('azimuth [deg]')
                ax.set_ylabel('elevation [deg]')
                plt.grid(True)
                            #axPos = pm+1
                            #axs[axPos][0].plot() # simObj.opticFlowAna.plotOpticFlow(0,showStartEnd = False) 
                            #axs[axPos][1].plot() # simObj.opticFlowAna.plotOpticFlow(0,showStartEnd = False, projectionType ='', viewField = True)
                

                viewField = True
                ax = fig.add_subplot(9,2,pm*2+2)
                print(index)
                for i in range(len(simObj.opticFlowAna.particleList)): # po should be (oldPosition, newPosition, status) of particle per movement
                    direct = simObj.opticFlowAna.anaDataList[frame][3][i]
                    if  simObj.opticFlowAna.anaDataList[frame][2][i] != None: # richtungsvector between frames
                        X = simObj.opticFlowAna.anaDataList[frame][2][i][0][2] # phi
                        Y = simObj.opticFlowAna.anaDataList[frame][2][i][0][1] # theta
                        U = direct[2] # phi direction
                        V = direct[1] # theta direction
                        ax.quiver(np.rad2deg(X),np.rad2deg(Y),np.rad2deg(U),np.rad2deg(V),angles ='xy',scale_units='xy', scale =1,width=0.001, color='midnightblue', alpha=0.7, zorder=2)
                    else:
                        pass
                    
                if viewField == True:
                    ax.set_xlim(np.rad2deg(-1.815),np.rad2deg(1.815)) # visual field from -104 to 104° horizontally
                    ax.set_ylim(np.rad2deg(-0.209),np.rad2deg(1.204)) # vidual field from−12°to+69°vertically
                if viewField == False:
                    x = ([np.rad2deg(-1.815),np.rad2deg(-1.815),np.rad2deg(1.815),np.rad2deg(1.815),np.rad2deg(-1.815)])
                    y = ([np.rad2deg(-0.209),np.rad2deg(1.204),np.rad2deg(1.204),np.rad2deg(-0.209),np.rad2deg(-0.209)])
                    ax.plot(x,y, zorder=1, color= 'forestgreen', linewidth= 2.0)    
                
                ax.set_xlabel('azimuth [deg]')
                ax.set_ylabel('elevation [deg]')
                plt.grid(True)
            
            plt.tight_layout()
            plt.show()