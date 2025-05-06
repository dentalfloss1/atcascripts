import glob
import os
cwd = os.getcwd().split('/')[-1]
vis      = f'{cwd}.ms'
# CHANGE GLOB TO CORRECT PROJECT CODE
files    = glob.glob('*.C3204')
print(files)
importatca(files=files,vis=vis,edge=2,options='noac')
