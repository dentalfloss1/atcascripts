import glob
import os
cwd = os.getcwd().split('/')[-1]
vis      = f'{cwd}.ms'
files    = glob.glob('*.C3542')
print(files)
importatca(files=files,vis=vis,edge=2,options='noac')
setjy(vis,field="1934-638",scalebychan=True,standard="Stevens-Reynolds 2016")
