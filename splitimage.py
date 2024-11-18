import datetime
import numpy as np 
import argparse
start_epoch = datetime.datetime(1858, 11, 17, 00, 00, 00, 00)
parser = argparse.ArgumentParser()
parser.add_argument("visname",type=str)
parser.add_argument("--targetname",type=str,required=True)
parser.add_argument("--numparts",type=int,required=True)
parser.add_argument("--cell",type=str,required=True)
parser.add_argument("--imsize",type=int,required=True)
args = parser.parse_args()
visname = args.visname
target = args.targetname

msmd.close()
msmd.open(visname)
fieldnum = msmd.fieldsforname(target)[0]
targetscans = msmd.scansforfield(fieldnum)
timeonsource = 0
for ts in targetscans:
    scantimes = msmd.timesforscan(ts)
    timeonsource += scantimes.max() - scantimes.min()
alltimes = msmd.timesforfield(fieldnum)
msmd.close()

tdelt = (alltimes.max() - alltimes.min()) / args.numparts
for i in range(args.numparts):
    t1 = start_epoch + datetime.timedelta(seconds=alltimes.min())
    start_subobs = (t1 + datetime.timedelta(seconds=i*tdelt)).strftime("%Y/%m/%d/%H:%M:%S")
    stop_subobs = (t1 + datetime.timedelta(seconds=(i+1)*tdelt)).strftime("%Y/%m/%d/%H:%M:%S")
    timestring = start_subobs+"~"+stop_subobs

    tclean( vis=visname,timerange =timestring, field=target,datacolumn='corrected',imagename=f'targetspw{visname.replace(".ms","")}_part{i+1}of{args.numparts}',imsize=args.imsize,cell=args.cell,gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='briggs',robust=0,niter=5000,gain=0.1,pbcor=True)

print("Hours on source:", timeonsource/60/60)

    


