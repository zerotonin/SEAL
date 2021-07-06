import pandas as pd 
import seaborn as sns
import numpy as np
from matplotlib import pyplot as plt

data = pd.read_csv('OF_content.csv')

plt.figure()


noCurrent = data[data.current_mPs == 0.0]

sns.set_theme(style="whitegrid")
noCurrPlot = sns.lineplot(data=noCurrent, x="cloudRad_m", y="OFmag_index", hue='protoMov_No',style='protoMov_No',markers=True,palette="tab10")
noCurrPlot.set(xscale='log')
noCurrPlot.set(ylim= [-1.05,1.05])
yTlabels = noCurrPlot.get_yticklabels()
noCurrPlot.set_yticks([-1.0,-0.75,-0.5,-0.25,0.0,0.25,0.5,0.75,1.0])
yTlabels =['pure transl. 1.00','0.75','0.5','0.25','0.0','-0.25','-0.5','-0.75','pure rotation -1.00']
yTlabels.reverse()
noCurrPlot.set_yticklabels(yTlabels)

plt.figure()

cloudRad1 = data[data.cloudRad_m > 9.0]
clRad1 = sns.lineplot(data=cloudRad1, x="current_mPs", y="OFmag_index", hue='protoMov_No',style='protoMov_No',markers=True,palette="tab10")
clRad1.set(xscale='log')
clRad1.set(ylim= [-1.05,1.05])
clRad1.set(xlim= [0,3])
yTlabels = noCurrPlot.get_yticklabels()
clRad1.set_yticks([-1.0,-0.75,-0.5,-0.25,0.0,0.25,0.5,0.75,1.0])
yTlabels =['pure transl. 1.00','0.75','0.5','0.25','0.0','-0.25','-0.5','-0.75','pure rotation -1.00']
yTlabels.reverse()
clRad1.set_yticklabels(yTlabels)

plt.show()

