import argparse
import datetime
import subprocess
import glob
import shutil
import os 
from casatools import image
from math import pi
import numpy as np
import matplotlib.pyplot as plt

trigger = datetime.datetime(2024, 2, 5, 22, 15, 8, 00)
cell = '4arcsec'
parser = argparse.ArgumentParser()
parser.add_argument("--field",required=True, type=str)
parser.add_argument("--msname",required=True,type=str)
parser.add_argument("--region",required=True,type=str)
parser.add_argument("--niter",type=int,default=3000)
parser.add_argument("--fbin",type=float, default=0)
parser.add_argument("--tbin",type=float,default=1)
parser.add_argument("--imsize",type=int,default=2560, help="imsize used in tclean")
args = parser.parse_args()

fbin = args.fbin
tbin = args.tbin
target = args.field
if args.msname[-1]=='/':
    visname = args.msname[:-1]
else:
    visname = args.msname
spw = args.msname.replace(".ms","")
myimage = f"targetimage{spw}"
splitvis = "target.ms"
maskedim="maskedimage0"
brightsrc = args.region.replace(".crtf","")+"_image"
uvfitsfile = f"{args.field}.uvfits"
uvfile = f"{args.region}_miriad.uv"
mapfile = uvfile.replace("uv","imap")
beamfile = uvfile.replace("uv","ibeam")
modelfile = uvfile.replace("uv","model")
restorefile = uvfile.replace("uv","image")
pbcorfile = uvfile.replace("uv","pbcor")
for f in glob.glob(f"target.ms*"):
    shutil.rmtree(f)
for f in glob.glob(f"{uvfile.replace('uv','')}*"):
    shutil.rmtree(f)
for f in glob.glob(f"{myimage}*"):
    shutil.rmtree(f)
for f in glob.glob(f"{brightsrc}.*"):
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
    return f"{int(whole)}:{minutes:02}:{seconds:08.5f}"

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

def makebrightcutout(ind, brightrgn, imageroot, brightsrc):
    masked = f'maskedimage{ind}'
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
    split(vis=visname, outputvis="target.ms", field=target)
    tclean( vis=splitvis,imagename=myimage,imsize=args.imsize,cell=cell,gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='briggs',robust=0,niter=args.niter,gain=0.1,pbcor=True)
    ia = image()
    imagefile=myimage
    makebrightcutout(0, args.region, myimage, brightsrc)
    tclean( vis=splitvis,imagename=maskedim,imsize=args.imsize,cell=cell,gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='briggs',robust=0,niter=args.niter,gain=0.1,pbcor=True,calcres=False,calcpsf=False,savemodel='modelcolumn')
    uvsub(splitvis)
    res = imfit(brightsrc+".image", region=args.region)
    comp = res['results']['component0']
    fluxguess = comp['flux']['value'][0]
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
    exportuvfits(vis=splitvis, field=args.field, fitsfile=uvfitsfile)
    mirfits = ["fits",f"in={uvfitsfile}","op=uvin",f"out={uvfile}"]
    print(mirfits)
    out = subprocess.run(mirfits)
    mirinvert = ["invert",f"vis={uvfile}",f"map={mapfile}",f"beam={beamfile}","stokes=i","options=mfs,sdb","robust=0","imsize=6,6,beam","cell=5,5,res"]
    print(mirinvert)
    out = subprocess.run(mirinvert)
    mirmfclean = ["mfclean",f"map={mapfile}",f"beam={beamfile}",f"out={modelfile}","options=negstop,positive",f"niters={args.niter}","cutoff=0.00005",'region="percentage(40)"']
    print(mirmfclean)
    out = subprocess.run(mirmfclean)
    mirrestor = ["restor",f"model={modelfile}",f"beam={beamfile}",f"map={mapfile}",f"out={restorefile}"]
    print(mirrestor)
    out = subprocess.run(mirrestor)
    mirlinmos = ["linmos",f"in={restorefile}",f"out={pbcorfile}"]
    print(mirlinmos)
    out = subprocess.run(mirlinmos)
    mirimpos = ["impos",f"in={uvfile}",f"coord={ra},{dec}",f"type=hms,dms"]
    out = subprocess.check_output(mirimpos)
    print(out)
    imposoutput = out.split(b'\n')
    for line in imposoutput:
        if (b'RA---NCP' in line) and (b'arcsec' in line):
            xoff = float(line.split(b" ")[-2])
        if b'DEC--NCP' in line and (b'arcsec' in line):
            yoff = float(line.split(b" ")[-2])
    miruvfit = ["uvfit",f"vis={uvfile}","object=point",f"spar={fluxguess},{xoff},{yoff}",f"bin={fbin},{tbin}"]
    out = subprocess.check_output(miruvfit)
    print(out)
    uvfitoutput = out.split(b'\n')
    flux = []
    fluxerr = []
    obsdate = []
    startdate = []
    stopdate = []
    for line in uvfitoutput:
        if b"Flux:" in line:
            print(line)
            stripline = line.replace(b" ",b"").replace(b"Flux:",b"").split(b"+/-")
            flux.append(float(stripline[0]))
            fluxerr.append(float(stripline[1]))
        if b"Doing time range" in line:
            print(line)
            stripline = line.replace(b"Doing time range ",b"").replace(b" ",b"").split(b"-")
            start = datetime.datetime.strptime(stripline[0].decode(),"%y%b%d:%H:%M:%S.%f")
            stop = datetime.datetime.strptime(stripline[1].decode(),"%y%b%d:%H:%M:%S.%f")
            tdelt = stop-start
            obsdate.append(((start+tdelt/2)-trigger).total_seconds()/3600/24)
            startdate.append(start)
            stopdate.append(stop)
    flux = flux[1:]
    fluxerr = fluxerr[1:]
    fig = plt.figure()
    plt.scatter(obsdate,flux,color='black')
    plt.errorbar(obsdate,flux,yerr=fluxerr,fmt=' ',color='black')
    ax = plt.gca()
    ax.set_yscale('log')
    ax.set_title(args.region)
    ax.set_ylim(2e-5,1e-3)
    plt.savefig(f"{args.region}_lc.png")
    plt.close()
    with open(f"{args.region}_lc.csv","w") as f:
        f.write("date,flux,fluxerr\n")
        for t1,t2,flux,fluxerr in zip(startdate,stopdate,flux,fluxerr):
           f.write(f"{t1.strftime('%Y-%m-%d %H:%M:%S.%f')},{t2.strftime('%Y-%m-%d %H:%M:%S.%f')},9,{flux*1e6},{fluxerr*1e6},0,X\n")




            
        

    

