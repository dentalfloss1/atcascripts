import argparse
import datetime
import subprocess
import glob
import shutil
import os 
import io
from contextlib import redirect_stderr
from casatools import image
from math import pi
import numpy as np
import matplotlib.pyplot as plt

start_epoch = datetime.datetime(1858, 11, 17, 00, 00, 00, 00)
trigger = datetime.datetime(2024, 2, 5, 22, 15, 8, 00)
cell = '4arcsec'
parser = argparse.ArgumentParser()
parser.add_argument("--field",required=True, type=str)
parser.add_argument("--msname",required=True,type=str)
parser.add_argument("--region",required=True,type=str)
parser.add_argument("--niter",type=int,default=3000)
parser.add_argument("--timeslices",type=int,default=1)
parser.add_argument("--imsize",type=int,default=2560, help="imsize used in tclean")
parser.add_argument("--subrounds",type=int, default=1, help="Number of rounds of subtraction")
parser.add_argument("--scan",action="store_true", help="uvfit each scan")

args = parser.parse_args()

target = args.field
if args.msname[-1]=='/':
    visname = args.msname[:-1]
else:
    visname = args.msname
spw = args.msname.replace(".ms","")
myimage = f"targetimage{spw}"
maskedim="maskedimage0"
brightsrc = args.region.replace(".crtf","")+"_image"
uvfitsfile = f"{args.field}.uvfits"
uvfile = f"{args.region}_miriad.uv"
mapfile = uvfile.replace("uv","imap")
beamfile = uvfile.replace("uv","ibeam")
modelfile = uvfile.replace("uv","model")
restorefile = uvfile.replace("uv","image")
pbcorfile = uvfile.replace("uv","pbcor")
for f in glob.glob(f"target*.ms*"):
    shutil.rmtree(f)
for f in glob.glob(f"{uvfile.replace('uv','')}*"):
    shutil.rmtree(f)
for f in glob.glob(f"{myimage}*"):
    shutil.rmtree(f)
for f in glob.glob(f"{brightsrc}*.*"):
    shutil.rmtree(f)
for f in glob.glob(f"{maskedim}*"):
    shutil.rmtree(f)
for f in glob.glob(f"{args.field}.*"):
    try: 
        os.remove(f)
    except:
        try:
            shutil.rmtree(f)
        except:
            pass

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

def maskpix(imagefile,r1):
    myimage = ia.newimagefromfile(imagefile)
    pixels = myimage.getregion(r1)                  # Recover pixels 
    pixelmask = myimage.getregion(r1, getmask=True)    # and mask 
    for i in range(len(pixels)): 
        pixels[i] = list(pixels[i])              # convert tuple to list for mods 
        for j in range(len(pixels[i])): 
            if pixelmask[i][j]: 
                pixels[i][j] = 0  
        pixels[i] = tuple(pixels[i]) 
    myimage.putregion(pixels=pixels, pixelmask=pixelmask, region=r1) 
    myimage.close()
def subtractim(dstim,srcim):
    ia.open(dstim)
    ia.calc(f'{dstim} - {srcim}')
    ia.close()

def addim(dstim,srcim):
    ia.open(dstim)
    ia.calc(f'{dstim} + {srcim}')
    ia.close()

def makebrightcutout(ind, brightrgn, imageroot, brightsrc, masked):
    for f in glob.glob(f'{imageroot}*'):
        src = f
        for dst in [f.replace(imageroot,masked),f.replace(imageroot,brightsrc)]:
            try:
                   shutil.copytree(src, dst)
                   print('copied ',src,' to ',dst)
            except OSError as exc: # python >2.5
                if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                    shutil.copy(src, dst)
                else: raise
    
    suffixes = ['.model','.image','.residual']
    for suffix in suffixes:
        maskpix(masked+suffix, brightrgn)
        print('masked ',masked+suffix,' using ',brightrgn) 
    for dst, src in [(brightsrc+suffix,masked+suffix) for suffix in suffixes]:
        subtractim(dst,src)
        print('subtracted ',src,' from ',dst)
if __name__=="__main__":
    lastvis = visname
    for iteration in range(1,args.subrounds+1):
        splitvis = "target_round"+str(iteration)+".ms"
        split(vis=lastvis, outputvis=splitvis, field=target,antenna="!CA06")
        curimage = myimage+"_round"+str(iteration)
        curmasked = maskedim+"_round"+str(iteration)
        curbright = brightsrc+"_round"+str(iteration)
        tclean( vis=splitvis,imagename=curimage,imsize=args.imsize,cell=cell,gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='briggs',robust=0,niter=args.niter,gain=0.1,pbcor=True)
        ia = image()
        makebrightcutout(0, args.region, curimage, curbright, curmasked)
        tclean( vis=splitvis,imagename=curmasked,imsize=args.imsize,cell=cell,gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='briggs',robust=0,niter=args.niter,gain=0.1,pbcor=True,calcres=False,calcpsf=False,savemodel='modelcolumn')
        uvsub(splitvis)
        tclean( vis=splitvis,imagename=curimage+"_subtracted",imsize=args.imsize,cell=cell,gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='briggs',robust=0,niter=args.niter,gain=0.1,pbcor=True)
        lastvis = splitvis
    
    res = imfit(curimage+"_subtracted"+".image", region=args.region) 
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
    starttimes = []
    stoptimes = []
    msmd.close()
    msmd.open(visname)
    fnum = msmd.fieldsforname(target)
    if args.scan:
        scans = msmd.scansforfield(fnum[0])
        for s in scans:
            timearray = msmd.timesforscan(s)
            starttimes.append(timearray.min())
            stoptimes.append(timearray.max())
        starttimes = np.array(starttimes)
        stoptimes = np.array(stoptimes)
    else:
        alltimes = msmd.timesforfield(fnum[0])
        alltimes = np.linspace(alltimes.min(), alltimes.max(), args.timeslices+1)
        starttimes = alltimes[:-1]
        stoptimes = alltimes[1:]
    msmd.close()
    shiftedphase = splitvis.replace(".ms","phaseshift.ms")
    phaseshift(vis=splitvis,outputvis=shiftedphase,field=args.field, phasecenter=f"J2000 {ra} {dec}")
    flux = []
    fluxerr = []
    startlist = []
    stoplist = []
    obslist = []
    for T,(t1,t2) in enumerate(zip(starttimes,stoptimes)):
        t1dt = (start_epoch + datetime.timedelta(seconds=t1))
        t2dt = (start_epoch + datetime.timedelta(seconds=t2))
        start = t1dt.strftime("%Y/%m/%d/%H:%M:%S")
        stop = t2dt.strftime("%Y/%m/%d/%H:%M:%S")
        flux.append(-1)
        fluxerr.append(-1)
        startlist.append(t1dt)
        stoplist.append(t2dt)
        obslength = t2dt - t1dt
        obslist.append( (t1dt - trigger).total_seconds() +  (obslength/2).total_seconds())
#         with redirect_stderr(io.StringIO()) as f:
        print(f'---{T}----')
        uvmodelfit(vis=shiftedphase, timerange=f"{start}~{stop}", field=args.field, niter=10, comptype='P', sourcepar=[fluxguess,0.1,0.1],outfile=f'complistchunk{T}.cl')
        tclean( vis=shiftedphase,timerange=f"{start}~{stop}",imagename=curimage+"_subtracted_chunk"+str(T),imsize=args.imsize,cell=cell,gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='briggs',robust=0,niter=args.niter,gain=0.1,pbcor=True)
        print('--------')
#         print('----')
#         print(f.getvalue())
#         print('----')
#         input("presskey")
#         for line in f.getvalue().split('\n'):
#             if "I = " in line:
#                flux.append(line.split(" +/-  ")[0])
#                fluxerr.append(line.split(" +/-  ")[0])
#                startlist.append(t1dt)
#                stoplist.append(t2dt)
#                obslength = t2dt - t1dt
#                obslist.append( (t1dt - trigger).total_seconds() +  (obslength/2).total_seconds())
# 
# 
#         
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




            
        

    

