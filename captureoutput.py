import sys
import subprocess
import os
import shutil
from math import pi
import io
from contextlib import redirect_stdout,redirect_stderr
import numpy as np
import datetime
import matplotlib.pyplot as plt
start_epoch = datetime.datetime(1858, 11, 17, 00, 00, 00, 00)
trigger = datetime.datetime(2024, 2, 5, 22, 15, 8, 00)
iteration = 3
myimage = f"targetimage9GHz"
curimage = myimage+"_round"+str(iteration)
rgn = "targetsource.crtf"
target="GRB"
visname = '9GHz.ms'
splitvis = "target_round"+str(iteration)+".ms"
def degtohms(ra):
    frac, whole = np.modf(24.0*ra/360.0)
    minutes  = np.abs(int(frac*60))
    seconds = (np.abs(frac*60) - np.abs(minutes))*60
    return f"{int(whole)}:{minutes:02}:{seconds:08.5f}"

def degtodms(dec):
    frac, whole = np.modf(dec)
    minutes  = np.abs(int(frac*60))
    seconds = (np.abs(frac*60) - np.abs(minutes))*60
    return f"{int(whole)}.{minutes:02}.{seconds:08.5f}"
res = imfit(curimage+"_subtracted"+".image", region=rgn)
comp = res['results']['component0'] 
fluxguess = comp['peak']['value']
ra = comp['shape']['direction']['m0']['value']*180/pi
dec = comp['shape']['direction']['m1']['value']*180/pi
if ra < 0:
   ra = ra + 360
if ra >360:
    ra = ra - 360
if dec < -90:
    dec = dec +180
if dec > 90:
    dec = dec + 90
 ####### create ra string as hms and dec string as dms
ra = degtohms(ra)
dec = degtodms(dec)
msmd.close()
msmd.open(visname)
fnum = msmd.fieldsforname(target)
times = msmd.timesforfield(fnum[0])
msmd.close()
shiftedphase = splitvis.replace(".ms","phaseshift.ms")
if os.path.exists(shiftedphase):
    shutil.rmtree(shiftedphase)
phaseshift(vis=splitvis,outputvis=shiftedphase,field="GRB", phasecenter=f"J2000 {ra} {dec}")
timerange = np.linspace(times.min(), times.max(), 4+1)
flux = []
fluxerr = []
startlist = []
stoplist = []
obslist = []
for T,(t1,t2) in enumerate(zip(timerange[:-1],timerange[1:])):
    t1dt = (start_epoch + datetime.timedelta(seconds=t1))
    t2dt = (start_epoch + datetime.timedelta(seconds=t2))
    start = t1dt.strftime("%Y/%m/%d/%H:%M:%S")
    stop = t2dt.strftime("%Y/%m/%d/%H:%M:%S")
    modelfitcommand = ["""casa""","""-c""","""'uvmodelfit(vis=shiftedphase, timerange=f"%s~%s", field=%s, niter=10, comptype="P", sourcepar=[%f,0.1,0.1],outfile=f"complistchunk%i.cl")'""" % (start,stop,target,fluxguess,T)]
    print(modelfitcommand)
    out = subprocess.check_output(modelfitcommand)
    print(out)
    for line in out.split(b'\n'):
        if b"I = " in line:
           flux.append(line.split(b" +/-  ")[0])
           fluxerr.append(line.split(b" +/-  ")[0])
           startlist.append(t1dt)
           stoplist.append(t2dt)
           obslength = t2dt - t1dt
           obslist.append( (t1dt - trigger).total_seconds() +  (obslength/2).total_seconds())


    
flux = np.array(flux)
fluxerr = np.array(fluxerr)
fluxerr = np.sqrt(fluxerr**2 + (0.05*flux)**2)
obsdate = np.array(obslist)
fig = plt.figure()
plt.scatter(obsdate,flux,color='black')
plt.errorbar(obsdate,flux,yerr=fluxerr,fmt=' ',color='black')
ax = plt.gca()
ax.set_yscale('log')
ax.set_title(args.region)
ax.set_ylim(2e-5,1e-2)
plt.savefig(f"{args.region}_lc.png")
plt.close()
with open(f"{args.region}_lc.csv","w") as f:
    f.write("t1,t2,flux,fluxerr\n")
    for t1,t2,flux,fluxerr in zip(startlist,stoplist,flux,fluxerr):
       f.write(f"{t1.strftime('%Y-%m-%d %H:%M:%S.%f')},{t2.strftime('%Y-%m-%d %H:%M:%S.%f')},9,{flux*1e6},{fluxerr*1e6},0,X\n")
# # 
# # 
# # 
# # 
# #             
# #         
# 
#     
# 
