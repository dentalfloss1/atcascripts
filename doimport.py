import glob
import os
cwd = os.getcwd().split('/')[-1]
vis      = f'{cwd}.ms'
files    = glob.glob('*.C3542')
print(files)
importatca(files=files,vis=vis,edge=2,options='noac')
