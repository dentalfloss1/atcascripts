import argparse
import subprocess
import glob
import shutil
import os 
parser = argparse.ArgumentParser()
parser.add_argument("ms",type=str, help="calibrated ms to split from")
parser.add_argument("--target",required=True, type=str, help="name of target field")
parser.add_argument("--niter",type=int,default=3000)
args = parser.parse_args()

uvfitsfile = f"{args.target}.uvfits"
uvfile = f"{args.target}.uv"
mapfile = uvfile.replace("uv","imap")
beamfile = uvfile.replace("uv","ibeam")
modelfile = uvfile.replace("uv","model")
restorefile = uvfile.replace("uv","image")
pbcorfile = uvfile.replace("uv","pbcor")
for f in glob.glob(f"{args.target}.*"):
    try: 
        os.remove(f)
    except:
        try:
            shutil.rmtree(f)
        except:
            pass

if __name__=="__main__":
    exportuvfits(vis=args.ms, field=args.target, fitsfile=uvfitsfile)
    mirfits = ["fits",f"vis={uvfitsfits}","op=uvin",f"out={uvfile}"]
    out = subprocess.run(mirfits)
    mirinvert = ["invert",f"vis={uvfile}",f"map={mapfile}",f"beam={beamfile}","stokes=i","options=mfs,sdb","robust=0","imsize=4,4,beam","cell=5,5,res"]
    out = subprocess.run(mirinvert)
    mirmfclean = ["mfclean",f"map={mapfile}",f"beam={beamfile}",f"out={modelfile}","options=negstop,positive",f"niters={args.niter}","cutoff=0.00005",'region="percentage(33)"']
    out = subprocess.run(mirmfclean)
    mirrestor = ["restor",f"model={modelfile}",f"beam={beamfile}",f"map={mapfile}",f"out={restorefile}"]
    out = subprocess.run(mirrestor)
    mirlinmos = ["linmos",f"in={restorefile}",f"out={restorefile}"]
