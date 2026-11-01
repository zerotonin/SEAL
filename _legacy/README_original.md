# SEAL SEnsory Aquatic odometry simuLator

This is a python project designed to simulate hydrodynamic and optic sensation of the harbour seal, in order to evaluate their ability to use optic flow as an odometer for home tracking.


# SEAL Model Structure

                        SEAL SIM OBJECT
                        /     |       \ 
                sealAgent turbidity environment
                    |
                protoMov


# ToDo

- turbidity
    - sizes to 0.5 to 20 mm  
- environment
    - done
- seal Agent
    - movement classes
        - orientation
    - combine steps of seal movement to sim Obj
- SIM Obj
    - implementation:
        1) decide for dive type, length etc.
        2) decide for environment (currents,depth,objects)
        3) compose trajectory
        4) run turbidty cloud through trajectory

- analyse
    - completion of OpticFlowAna
        - implementation of r_querr vs R ranking 
        - plot routine for optic flow





# Windows: batch to start from GitBash 

Filenname: startCodeSeal.bat
Contents: 
cd /c/Users/you/yourProjectPath/project
eval `ssh-agent -s`
ssh-add ~/.ssh/id_rsa

code

Than run from gitbash: bash startCodeSeal.bat