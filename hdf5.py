import numpy as np 
import h5py

matrix1 = np.random.random(size = (1000,1000))
matrix2 = np.random.random(size = (10000,1000))

with h5py.File('/home/anne/Documents/hdf5_data.h5', 'w') as hdf:
    hdf.create_dataset('dataset1', data = matrix1 )
    hdf.create_dataset('dataset2', data = matrix2 )

with h5py.File('/home/anne/Documents/hdf5_data.h5', 'r') as hdf:
    ls = list(hdf.keys())
    print(ls)
    data = hdf.get('dataset1')
    print(data)