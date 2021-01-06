
import numpy as np
import pandas as pd
import pickle
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
        self.amountOfObstacles      = 100
        self.durSec                 = 240 # duration of,
        self.traLen                 = self.durSec*self.sps # number of samples
        self.velTra                 = list() # list of sealTrajectory per sample with (thrust,slip,lift,yaw,pitch,roll)        
        self.sealPosition           = np.zeros(shape = 3) #centre of the coordinate system of the Seal in disctance to (0,0,0) of world
        self.sealOrientation        = np.zeros(shape = 3)  # orientation as yaw pitch roll
        self.sealStep               = np.zeros(shape =6) # change of position and orientation
        self.sealTrajectory         = list() # public??
        self.diveType               = 'vShape' # descri
        self.currentType            = 'static'
        self.currentStaticVel       = (0.0,0.1,0.0)
        self.max_particles          = 270
        self.particleSizeRange      = (0.00002,0.00016)
        self.cloudRadius            = 0.0018

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
        elif parameterName == 'currentStaticVel':
            self.currentStaticVel  = parameterValue
        elif parameterName == 'max_particles':
            self.max_particles  = parameterValue
        elif parameterName == 'particleSizeRange':
            self.particleSizeRange  = parameterValue
        elif parameterName == 'cloudRadius':
            self.cloudRadius  = parameterValue
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
        elif parameterName == 'currentStaticVel':
            return self.currentStaticVel  
        elif parameterName == 'max_particles':
            return self.max_particles  
        elif parameterName == 'particleSizeRange':
            return self.particleSizeRange  
        elif parameterName == 'cloudRadius':
            return self.cloudRadius  
        else:
            print('get unknown parameter'+str(parameterName))
    
    def packToWriteOut(self):
        self.partclObjList = self.simObj.pCloud.partclObjList
    
    def writeOutPickle(self,filename):
        self.packToWriteOut()
        fileHandler = open(filename,'wb')
        pickle.dump(self,fileHandler)

    def data2pandaShit(self):
        # labels for the dataframes
        coordinateLable  = ['x_m','y_m','z_m']
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
            pre     = pd.DataFrame([ x[0] for x in particle.trajectory],columns= coordinateLable)
            post    = pd.DataFrame([ x[1] for x in particle.trajectory],columns= coordinateLable)
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
        outDict = { 'diveType'       : self.diveType,
                    'oceanLowerLim'  : float(self.oceanLimit[0]),
                     }

        return outDict

    def standardOut(self,fileBaseName)
        # get data as DataFrame
        resultDF = self.data2pandaShit()
        # get meta data as yaml conform dictionary
        outDict = self.metaData2Dict()
        # add file location to meta data
        outDict['yamlFile'] = fileBaseName + '.yaml'
        outDict['hdf5File'] = fileBaseName + '.h5' 

        with open(outDict['yamlFile'], 'w') as file:
            documents = yaml.dump(outDict, file)
        
        resultDF.to_hdf(outDict['hdf5File'],key='df',mode='w',complevel=9)




        '''
        This function saves the simulated sealTrajectories and particle Trajectories
        as well as all public data for this simulation in a hdf5 file format.
        
        # sealTra, particleTra(for each particle list of duration ( including list of prePosition, postPosition and state)), Paramater aus init
        hf = h5py.File('data.h5', 'w')

        g1 = hf.create_group('publicData')

        g1.create_dataset('sps',data=self.sps)
        g1.create_dataset('oceanSurface',data=self.oceanSurface)
        g1.create_dataset('oceanDepth',data=self.oceanDepth)
        g1.create_dataset('oceanLimit',data=self.oceanLimit)
        g1.create_dataset('waterCurrent',data=self.waterCurrent)
        g1.create_dataset('amountOfObstacles',data=self.amountOfObstacles)
        g1.create_dataset('durSec',data=self.durSec)
        g1.create_dataset('traLen',data=self.traLen)
        g1.create_dataset('velTra',data=self.velTra)
        g1.create_dataset('sealPosition',data=self.sealPosition)
        g1.create_dataset('sealOrientation',data=self.sealOrientation)
        g1.create_dataset('sealStep',data=self.sealStep)
        g1.create_dataset('diveType',data=self.diveType)
        g1.create_dataset('currentType',data=self.currentType)
        g1.create_dataset('currentStaticVel',data=self.currentStaticVel)
        g1.create_dataset('max_particles',data=self.max_particles)
        g1.create_dataset('particleSizeRange',data=self.particleSizeRange)
        g1.create_dataset('cloudRadius',data=self.cloudRadius)
#
        hf.create_dataset('sealTrajectory',data=self.sealTrajectory)

        g3 = hf.create_group('particleList')
        for pObject in self.simObj.pCloud.partclObjList:
            g3.create_dataset('particleTra_'+str(pObject),data=self.simObj.pCloud.partclObjList[pObject].trajectory)
#       # data=self.simObj.pCloud.partclObjList[pObject].trajectory[i] --> prePosition ARRAY, postPosition ARRAY StateCheck BOOL
        '''

