
import numpy as np
import pandas as pd
import pickle
import yaml
#import h5py
class runTimeData:
    '''
    This class sets and gets all public data, which are needed to run a specific simulation.
    Here all public data is stored and the other class get and set changes in these public data
    via the runTimeData class.
    '''
    def __init__(self,simObj):
        """
        This function initializes default values for all public data

        @param simObj                          ? default: 
        @param sps                             int default: 100
            simulated samples per second
        @param oceanSurface                    int default: 0
            oceanSurface an 0m
        @param oceanDepth                      float default: -70.0
            depth of ocenan set to -70m
        @param oceanLimit                      tuple default: (-70, 70)
            limits of simulated 2D ocean in x and y plane
        @param waterCurrent                    array default: ([0. , 0.1, 0. ])
            ???
        @param amountOfObstacles               int default: 100
            number of obstcles simulates
        @param durSec                          int default: 240 
            runTime in seconds
        @param traLen                          int default: 100*240
            calculated runtime in samples
        @param velTra                          list default: None
            list to store seal velocitiy trajectory
        @param sealPosition                    array default: ([0. , 0. , 0. ])
            position of seal (x,y,z)
        @param sealOrientation                 array default: ([0. , 0. , 0. ])
            orientation of seal
        @param sealStep                        str default: ([0. , 0. , 0. ,0. , 0. , 0. ])
            change is position and orientation(from veltra)
        @param sealTrajectory                  list default: None 
            calculates sealTrajectory based of veltra
        @param diveType                        str default: 'vShape'
            dive type can be uShape or vShape
        @param currentType                     str default: 'static'
            type of current (static,interpolated)
        @param currentStaticVel                tuple default: (0. , 0.1, 0. )
            needed??
        @param max_particles                   int default: 270
            number of particles within the sphere
        @param particleSizeRange               tuple default: (0.00002,0.00016)
            size range of particles in m 
        @param cloudRadius                     float default: 0.0018
            radius of particle cloud in m 
        """
        self.simObj                 = simObj
        self.sps                    = 100 # number of samples per second
        self.oceanSurface           = 0 # [m] linkable
        self.oceanDepth             = -70 # [m] linkable
        self.oceanLimit             = (-70,70) # [m] linkable
        self.waterCurrent           = np.array([0.0,0.1,0.0]) # just a simple example will be changed later 
        self.amountOfObstacles      = 0
        self.durSec                 = 240 # duration of,
        self.traLen                 = self.durSec*self.sps # number of samples
        self.velTra                 = list() # list of sealTrajectory per sample with (thrust,slip,lift,yaw,pitch,roll)        
        self.sealPosition           = np.zeros(shape = 3) #centre of the coordinate system of the Seal in disctance to (0,0,0) of world
        self.sealOrientation        = np.zeros(shape = 3)  # orientation as yaw pitch roll
        self.sealStep               = np.zeros(shape =6) # change of position and orientation
        self.sealTrajectory         = list() # public??
        self.diveType               = 'vShape' # descri
        self.currentType            = 'static'
        self.max_particles          = 3660
        self.particleSizeRange      = (0.00002,0.00016)
        self.cloudRadius            = 0.00174
        self.gridParticles          = False

    def setParameter(self, parameterName, parameterValue):
        ''' 
        This function sets the parameter in the init function to a 
        userdefined value, or by other classes which are making changes
        to a parameter throughout the simulation (eg. sealPosition)
        '''
        if parameterName == 'sps':
            self.sps = parameterValue
            self.traLen = self.durSec*self.sps
        elif parameterName == 'oceanSurface':
            self.oceanSurface = parameterValue
        elif parameterName == 'oceanDepth':
            self.oceanDepth = parameterValue
        elif parameterName == 'oceanLimit':
            self.oceanLimit = parameterValue
        elif parameterName == 'waterCurrent':
            self.waterCurrent = parameterValue
        elif parameterName == 'amountOfObstacles':
            self.amountOfObstacles = parameterValue
        elif parameterName == 'traLen':
            self.traLen = parameterValue
        elif parameterName == 'velTra':
            self.velTra  = parameterValue
        elif parameterName == 'sealPosition':
            self.sealPosition = parameterValue
        elif parameterName == 'sealOrientation':
            self.sealOrientation  = parameterValue
        elif parameterName == 'sealStep':
            self.sealStep  = parameterValue
        elif parameterName == 'sealTrajectory':
            self.sealTrajectory  = parameterValue
        elif parameterName == 'diveType':
            self.diveType  = parameterValue
        elif parameterName == 'durSec':
            self.durSec  = parameterValue
            self.traLen = self.durSec*self.sps
        elif parameterName == 'currentType':
            self.currentType  = parameterValue
        elif parameterName == 'max_particles':
            self.max_particles  = parameterValue
        elif parameterName == 'particleSizeRange':
            self.particleSizeRange  = parameterValue
        elif parameterName == 'cloudRadius':
            self.cloudRadius  = parameterValue
        elif parameterName == 'gridParticles':
            self.gridParticles = parameterValue
        else:
            print('set unknown parameter'+str(parameterName))

    def getParameter(self,parameterName):
        '''
        This function allows other functions or classes to get the most
        recent value for each parameter from the init function.
        '''
        if parameterName == 'sps':
            return self.sps
        elif parameterName == 'oceanSurface':
            return self.oceanSurface
        elif parameterName == 'oceanDepth':
            return self.oceanDepth 
        elif parameterName == 'oceanLimit':
            return self.oceanLimit 
        elif parameterName == 'waterCurrent':
            return self.waterCurrent
        elif parameterName == 'amountOfObstacles':
            return self.amountOfObstacles 
        elif parameterName == 'traLen':
            return self.traLen 
        elif parameterName == 'velTra':
            return self.velTra  
        elif parameterName == 'sealPosition':
            return self.sealPosition 
        elif parameterName == 'sealOrientation':
            return self.sealOrientation  
        elif parameterName == 'sealStep':
            return self.sealStep  
        elif parameterName == 'sealTrajectory':
            return self.sealTrajectory  
        elif parameterName == 'diveType':
            return self.diveType  
        elif parameterName == 'durSec':
            return self.durSec  
        elif parameterName == 'currentType':
            return self.currentType  
        elif parameterName == 'max_particles':
            return self.max_particles  
        elif parameterName == 'particleSizeRange':
            return self.particleSizeRange  
        elif parameterName == 'cloudRadius':
            return self.cloudRadius  
        elif parameterName == 'gridParticles':
            return self.gridParticles
        else:
            print('get unknown parameter'+str(parameterName))
    
    def packToWriteOut(self):
        self.partclObjList = self.simObj.pCloud.partclObjList
    
    def writeOutPickle(self,filename):
        self.packToWriteOut()
        fileHandler = open(filename,'wb')
        pickle.dump(self,fileHandler)

    def data2pandaShit(self,lightWeight=True):
        # labels for the dataframes
        coordinateLable  = ['x_m','y_m','z_m']
        sphericLable     = ['r_m' ,'theta_rad','phi_rad']
        orientationLable = ['yaw_rad','pitch_rad','roll_rad']
        
        # make a seal data frame we use a second hierarchical level to have the same amount of levels as 
        # for the particles. There might be more elegant ways to program this. Please improve
        sealCoordsDF = pd.DataFrame(self.sealTrajectory[0::,0:3],columns= coordinateLable)
        sealOrientDF = pd.DataFrame(self.sealTrajectory[0::,3::],columns= orientationLable)
        sealDF       = pd.concat(dict(coordinates = sealCoordsDF,orientation=sealOrientDF),axis = 1)
        
        # counter for particles
        c = 0
        
        # data dictionary for the final dataframe
        dataDict = dict(seal = sealDF)
        # run through all particles
        for particle in self.simObj.pCloud.partclObjList:
            # we use a list constructor to get the data out of the list of tuples and 
            # directly write them into individual data frames
            if lightWeight:
            
                pre       = pd.DataFrame([ self.simObj.opticFlowAna.cart2spheric(x[0]) for x in particle.trajectory],columns= sphericLable)
                post      = pd.DataFrame([ self.simObj.opticFlowAna.cart2spheric(x[1])  for x in particle.trajectory],columns= sphericLable)
                flag      = pd.DataFrame([ x[2] for x in particle.trajectory],columns= ['flag'])
                radii     = pd.concat(dict(preR=pre['r_m'],postR=post['r_m']),axis=1).mean(axis=1)
                inSideFoV = pd.concat(dict( prePhiLT = pre['phi_rad'].gt(-1.815), 
                                            prePhiGT = pre['phi_rad'].lt(1.815)),
                                            axis=1)

                # combine pre-step-coordinates and post-step-coordinates with the visibilaity flag into one df
                particleDF = pd.concat(dict(preStep = pre,postStep = post,visible = flag),axis = 1)


            else:

                pre     = pd.DataFrame([x[0] for x in particle.trajectory],columns= coordinateLable)
                post    = pd.DataFrame([x[1]  for x in particle.trajectory],columns= coordinateLable)
                flag    = pd.DataFrame([ x[2] for x in particle.trajectory],columns= ['flag'])
                # combine pre-step-coordinates and post-step-coordinates with the visibility flag into one df
                particleDF = pd.concat(dict(preStep = pre,postStep = post,visible = flag),axis = 1)
            # save the new df in the data dictionary
            dataDict['particle_'+str(c).zfill(4)] = particleDF
            # increase counter
            c+=1
        # dictionary to create final data frame
        return pd.concat(dataDict,axis = 1)

    def metaData2Dict(self):
        # dict that shit   
        outDict = { 'sps'                  : self.sps,
                    'oceanSurface'         : self.oceanSurface,
                    'oceanDepth'           : self.oceanDepth,
                    'oceanLowerLim'        : float(self.oceanLimit[0]), 
                    'oceanUpperLim'        : float(self.oceanLimit[1]),      
                    'waterCurrentX'        : float(self.waterCurrent[0]), 
                    'waterCurrentY'        : float(self.waterCurrent[1]),
                    'waterCurrentZ'        : float(self.waterCurrent[2]),     
                    'amountOfObstacles'    : self.amountOfObstacles, 
                    'durSec'               : self.durSec,            
                    'traLen'               : self.traLen,            
                    #'velTra:self.velTra              
                    'sealPositionX'        : float(self.sealPosition[0]),  
                    'sealPositionY'        : float(self.sealPosition[1]), 
                    'sealPositionZ'        : float(self.sealPosition[2]),     
                    'sealOrientationX'     : float(self.sealOrientation[0]),
                    'sealOrientationY'     : float(self.sealOrientation[1]),
                    'sealOrientationZ'     : float(self.sealOrientation[2]),   
                    'sealStepX'            : float(self.sealStep[0]),
                    'sealStepY'            : float(self.sealStep[1]),
                    'sealStepZ'            : float(self.sealStep[2]),
                    'sealStepYaw'          : float(self.sealStep[3]),
                    'sealStepPitch'        : float(self.sealStep[4]),
                    'sealStepRoll'         : float(self.sealStep[5]),          
                    #'sealTrajectory'  : self.sealTrajectory,    
                    'diveType'             : self.diveType,          
                    'currentType'          : self.currentType,       
                    #'currentStaticVelX'   : self.currentStaticVel[0], same as waterCurrent 
                    'max_particles'        : self.max_particles,     
                    'smallestParticleSize' : float(self.particleSizeRange[0]),
                    'largestParticleSize'  : float(self.particleSizeRange[1]), 
                    'cloudRadius'          : self.cloudRadius,       
                     }

        return outDict

    def standardOut(self,fileBaseName):
        # get data as DataFrame
        resultDF = self.data2pandaShit()
        resultDF.columns = resultDF.columns.map(str)
        # get meta data as yaml conform dictionary
        outDict = self.metaData2Dict()
        # add file location to meta data
        outDict['yamlFile'] = fileBaseName + '.yaml'
        outDict['hdf5File'] = fileBaseName + '.h5' 
        # write out yaml
        with open(outDict['yamlFile'], 'w') as file:
            yaml.dump(outDict, file, sort_keys=False)
        #write out data frame
        resultDF.to_hdf(outDict['hdf5File'],key='df',mode='w',complevel=9)
        #or
        #compression_opts = dict(method='zip',archive_name='out.csv')  
        #resultDF.to_csv(fileBaseName + '.csv.gz',compression= 'gzip')
        #resultDF.to_csv(fileBaseName + '.csv.zip',compression= 'zip')
        #resultDF.to_pickle(fileBaseName + '.pickle')
        #resultDF.to_pickle(fileBaseName + '.pickle.gz', compression='gzip')
        #resultDF.to_pickle(fileBaseName + '.pickle.bz2', compression='bz2')
        #resultDF.to_pickle(fileBaseName + '.pickle.zip', compression='zip')
        #resultDF.to_pickle(fileBaseName + '.pickle.xz', compression='xz')
        #resultDF.to_feather(fileBaseName + '.feather')
        #resultDF.to_parquet(fileBaseName + '.parquet.gz', compression='gzip')
 

    def writeOutVelTra(self,fileBaseName):
        sealVelDF = pd.DataFrame(self.velTra,columns= ['thrust m/s','slip m/s','lift m/s','yaw rad/s','pitch rad/s','roll rad/s'])
        sealVelDF.to_csv(fileBaseName + '.csv')

    def writeOutParticleTra(self, fileBaseName):
        particleVel  = pd.DataFrame(self.simObj.opticFlowAna.partCartList, columns=['startPosition', 'endPosition'])
        particleVel.index.name='particleNo'
        #particleVel2 = pd.DataFrame(self.simObj.opticFlowAna.partSphereList, columns=['startPosition', 'endPosition'])
        particleVel.to_csv(fileBaseName + '.csv')
        #particleVel2.to_csv(f'{fileBaseName}2.csv')