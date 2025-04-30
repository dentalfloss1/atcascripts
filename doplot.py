import numpy as np 
import matplotlib.pyplot as plt
import datetime
from scipy.stats import chi2
import glob
flux = []
fluxerr = []
with open("uvfitting.txt","r") as f:
   for line in f:
       if "I = " in line:
           strflux,strerr = line.replace("I = ","").replace(" ","").split("+/-")
           curerr = float(strerr)
           curflux = float(strflux)
           flux.append(curflux)
           fluxerr.append(np.sqrt(curerr**2 + (0.05*curflux)**2))
           print(curflux,curerr)

csvglob= glob.glob('*crtf*.csv')
if len(csvglob) > 1:
    raise Exception("Too many csv files in glob",csvglob)
plotdata = np.loadtxt(csvglob[0], delimiter=',', skiprows=1,usecols=(0,1,2),dtype=[('t1','<U128'),('t2','<U128'),('freq','f8')]) 
trigger = datetime.datetime(2024, 2, 5, 22, 15, 8, 00)
fig = plt.figure()
startdate = [(datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f") - trigger).total_seconds()/3600/24 for d in plotdata['t1']]
stopdate = [(datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f") - trigger).total_seconds()/3600/24 for d in plotdata['t2']]
obsdur = [(t2-t1) for t1,t2 in zip(startdate,stopdate)]
obsdate = [t1+(dur/2) for t1,dur in zip(startdate,obsdur)]

xdata = obsdate
ydata = np.array(flux)
yerr = np.array(fluxerr)
plt.errorbar(xdata,ydata,yerr=yerr, ls='none',marker='o', label="uv fit")
ax = plt.gca()
ax.set_xlabel("Days post-burst")
ax.set_ylabel("Flux (Jy)")
ax.set_ylim(2e-5,3e-3)
ax.set_xscale('log')
ax.set_yscale('log')
plt.legend()
plt.savefig("uvfit.png")
plt.close()

avgflux = np.average(ydata)
chisq = 0
dof = len(ydata)
for t1,t2,freq,f,fe in zip(plotdata['t1'],plotdata['t2'],plotdata['freq'],ydata,yerr):
    chisq += ((f-avgflux)/fe)**2
    print(1,t1,t2,freq,f*1e6,fe*1e6,0,"X",sep=',')
P = chi2.cdf(chisq, dof)

print("$\chi^2$ = ",chisq,"P = ",P)


