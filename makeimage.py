#Copyright (C) 2022 Inter-University Institute for Data Intensive Astronomy
#See processMeerKAT.py for license details.

#!/usr/bin/env python3

import os
import glob
import argparse
import traceback
import shutil, errno

import glob
try:
    from casatasks import *
except Exception as e:
    print(e)
    print('Continuing anyway')
try:
    from casatools import table,msmetadata
except Exception as e:
    print(e)
    print('Continuing anyway')
# casalog.setlogfile('logs/{SLURM_JOB_NAME}-{SLURM_JOB_ID}.casa'.format(**os.environ))

import logging
from time import gmtime
logging.Formatter.converter = gmtime
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)-15s %(levelname)s: %(message)s", level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('msin',type=str)
parser.add_argument('target',type=str)
parser.add_argument('--refant',type=str, default='CA04')
args = parser.parse_args()
refant = args.refant
msname = "target.ms"
split(args.msname, outputvis = msname, field=args.target)

def doclean(roundnum,threshold):
    imagename = msname.replace('.ms',f'_round{roundnum}')
    tclean(vis=msname, selectdata=False, datacolumn='corrected', 
            imagename=imagename, imsize=5120,
            cell='0.75arcsec', stokes='I', gridder='standard',
            deconvolver = 'hogbom', restoration=True,
            weighting='natural',
            niter=10000, threshold=threshold,
            savemodel='modelcolumn', pblimit=-1e-12, parallel = False, gain=0.08)

def writegaintable(calnum,mysolint):
    prefix = msname.replace('.ms','_caltable')
    caltable = f'{prefix}{calnum}.G'
    if calnum < 2:
        calmode='p'
    else:
        calmode='ap'
    gaincal(vis=msname, caltable=caltable, selectdata=False, refant = refant, solint=mysolint, solnorm=False, normtype='median', gaintype='G', calmode=calmode, append=False, parang=False)

def apply(calnum):
    prefix = msname.replace('.ms','_caltable')
    caltable = f'{prefix}{calnum}.G'
    applycal(vis=msname, selectdata=False, gaintable=caltable, parang=False, interp='linear,linearflag')

def flagging():
    flagdata(vis=msname, mode='rflag', datacolumn='RESIDUAL', field='', timecutoff=5.0,freqcutoff=5.0, timefit='line', freqfit='line', flagdimension='freqtime', extendflags=False, timedevscale=3.0, freqdevscale=3.0, spectralmax=500, extendpols=False, growaround=False, flagneartime=False, flagnearfreq=False, action='apply', flagbackup=True, overwrite=True, writeflags=True)

if __name__ == "__main__":
  #   def namefolder(foldername, index):
  #       if index >= 1:
  #           foldername = f'{foldername}{index}'
  #       if os.path.exists(foldername):
  #           namefolder(foldername,index + 1)
  #       else:
  #           return foldername
  #   myfolder = namefolder('msname',0)
  #   os.mkdir(myfolder)
  #   try:
  #       shutil.copytree(msname, f'{myfolder}/{msname}')
  #   except OSError as exc: # python >2.5
  #       if exc.errno in (errno.ENOTDIR, errno.EINVAL):
  #           shutil.copy(msname, f'{myfolder}/{msname}')
  #       else: raise
    thresholdlist = [1e-4,7e-5,5e-5,3e-5]
    solint = ['inf','10min','5min']

    for ind,thresh in enumerate(thresholdlist):
        thisround = ind + 1
        if thisround > 1:
            writegaintable(ind-1,solint[ind-1])
            apply(ind-1)
            flagging()
        doclean(thisround,thresh)

        



    
