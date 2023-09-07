import os
import glob
import shutil
spwlist = ['0','1']
origvis = f'{os.getcwd().split("/")[-1]}.ms'
for f in glob.glob('5GHz*.ms*'):
    shutil.rmtree(f)
for f in glob.glob('9GHz*.ms*'):
    shutil.rmtree(f)

# flagdata(vis=origvis, mode='manual',field='focus')

split(origvis, spw='0', outputvis = '5GHz.ms',datacolumn='ALL')
vis = '5GHz.ms'
for i,c in enumerate(range(0,2048,256)):
    split(vis='5GHz.ms', spw=f'0:{c}~{c+255}', datacolumn='ALL',outputvis=f'5GHzspw{i}.ms')
shutil.rmtree('5GHz.ms')
vis = glob.glob('5GHzspw*.ms')
concat(vis,concatvis='5GHz.ms')
for v in vis:
    shutil.rmtree(v)

split(origvis, spw='1', outputvis = '9GHz.ms',datacolumn='ALL')
vis = '9GHz.ms'
for i,c in enumerate(range(0,2048,256)):
    split(vis='9GHz.ms', spw=f'0:{c}~{c+255}', datacolumn='ALL',outputvis=f'9GHzspw{i}.ms')
shutil.rmtree('9GHz.ms')
vis = glob.glob('9GHzspw*.ms')
concat(vis,concatvis='9GHz.ms')
for v in vis:
    shutil.rmtree(v)

 # Remove files from previous runs, glob ensures we only delete it if it exists
for f in glob.glob('gaincalspw*'):
    shutil.rmtree(f)
for f in glob.glob('*target*spw*'):
    shutil.rmtree(f)
for f in glob.glob(f'*jpg'):
    os.remove(f)
for f in glob.glob(f'*delay*K*'):
    shutil.rmtree(f)
for f in glob.glob(f'*bp*B*'):
    shutil.rmtree(f)
for f in glob.glob(f'*gain*G*'):
    shutil.rmtree(f)
for f in glob.glob(f'*flux*fluxscale*'):
    shutil.rmtree(f)
for visname in ['5GHz.ms','9GHz.ms']:
    gfield = '1420-679'
    calfields = ['1934-638',gfield]
    referenceant = 'CA01'
    target = 'sgrb'
    allfields = ['1934-638',gfield,target]
    pfield = ['1934-638']
    bfield = ['1934-638']
    minbaselines=3
    spw = visname[:-3]
    kfilebase = f'delayspw{spw}.K'
    bfilebase = f'bpspw{spw}.B'
    gfilebase = f'gainspw{spw}.G'
    pregfilebase = f'gainspw{spw}.Gpre'
    fluxfilebase = f'fluxspw{spw}.fluxscale'
    setjy(vis=visname,field="1934-638",scalebychan=True,standard="Stevens-Reynolds 2016")
    # flagdata(vis=visname, mode='manual',scan='0,44')
    # RFI issues in this one
    for f in calfields:
        flagdata(vis=visname, mode='tfcrop', field=f,
                ntime='scan', timecutoff=5.0, freqcutoff=5.0, timefit='line',
                freqfit='line', extendflags=False, timedevscale=5., freqdevscale=5.,
                extendpols=True, growaround=False, action='apply', flagbackup=True,
                overwrite=True, writeflags=True, datacolumn='DATA')
    
    plotms(vis=visname, xaxis='freq', yaxis='amp', showgui=False,
            field='1934-638', plotfile='freqamp1934.jpg')
    plotms(vis=visname, xaxis='freq', yaxis='amp', showgui=False,
            field=gfield, plotfile=f'freqampgfield.jpg')
    plotms(vis=visname, xaxis='time', yaxis='amp', showgui=False,
            field='1934-638', plotfile='timeamp1934.jpg')
    plotms(vis=visname, xaxis='time', yaxis='amp', showgui=False,
            field=gfield, plotfile=f'timeampgfield.jpg')
    flagdata(vis=visname, mode='tfcrop', field=target,
            ntime='scan', timecutoff=6.0, freqcutoff=6.0, timefit='poly',
            freqfit='poly', extendflags=False, timedevscale=5., freqdevscale=5.,
            extendpols=True, growaround=False, action='apply', flagbackup=True,
            overwrite=True, writeflags=True, datacolumn='DATA')
    
    flagdata(vis=visname, mode='extend', field=target,
            datacolumn='data', clipzeros=True, ntime='scan', extendflags=False,
            extendpols=True, growtime=80., growfreq=80., growaround=False,
            flagneartime=False, flagnearfreq=False, action='apply',
            flagbackup=True, overwrite=True, writeflags=True)
    for f in calfields:
        # Conservatively extend flags for all fields in config
        flagdata(vis=visname, mode='extend', field=f,
                datacolumn='data', clipzeros=True, ntime='scan', extendflags=False,
                extendpols=True, growtime=80., growfreq=80., growaround=False,
                flagneartime=False, flagnearfreq=False, action='apply',
                flagbackup=True, overwrite=True, writeflags=True)
    kfile = f'{kfilebase}'
    bfile = f'{bfilebase}'
    pregfile = f'{pregfilebase}'
    gfile = f'{gfilebase}'
    fluxfile = f'{fluxfilebase}'
    for j,bf in enumerate(bfield):
        if j==0:
            append=False
        else:
            append=True
        gaincal(vis=visname, caltable = pregfile, field = bf, refant = referenceant,
                    minblperant = minbaselines, solnorm = False,  gaintype = 'G',
                    solint = 'inf', combine = 'scan', calmode='p',
                    parang = False,append = append)
        plotms(vis=pregfile, xaxis='time', yaxis='phase', coloraxis='corr', 
                    field='1934-638', iteraxis='antenna',plotrange=[-1,-1,-180,180],
                    showgui= False, gridrows=3, gridcols=2, plotfile='initialgain.jpg')
        gaincal(vis=visname, caltable = kfile, field = bf, refant = referenceant,
                    minblperant = minbaselines, solnorm = False,  gaintype = 'K',
                    solint = 'inf', combine = 'scan', parang = False,append = append)
        
        bandpass(vis=visname, caltable = bfile,
                field = bf, refant = referenceant,
                minblperant = minbaselines, solnorm = False,  solint = 'inf',
                combine = 'scan', bandtype = 'B', fillgaps = 4,
                gaintable = kfile, gainfield = bf,
                parang = False, append = append)
    gaincal(vis=visname, caltable = gfile,
            field = '1934-638', refant = referenceant,
            minblperant = minbaselines, solnorm = False,  gaintype = 'G',
            solint = 'inf', combine = '', calmode='ap',
            gaintable=[kfile, bfile],
            parang = False, append = False)
    gaincal(vis=visname, caltable = gfile,
            field = gfield, refant = referenceant,
            minblperant = minbaselines, solnorm = False,  gaintype = 'G',
            solint = 'inf', combine = '', calmode='ap',
            gaintable=[kfile, bfile],
            parang = False, append = True)
    myscale = fluxscale(vis=visname,caltable=gfile,fluxtable=fluxfile, reference='1934-638',transfer=[gfield],incremental=False, fitorder=4)
    applycal(vis=visname, field='1934-638',
            selectdata=False, calwt=False, gaintable=[fluxfile,bfile,kfile],
            gainfield=['1934-638','',''],
            parang=False, interp=['nearest','',''])
    applycal(vis=visname, field=gfield,
            selectdata=False, calwt=False, gaintable=[fluxfile,bfile,kfile],
            gainfield=[gfield,'',''],
            parang=False, interp=['nearest','',''])
    
    applycal(vis=visname, field=target,
            selectdata=False, calwt=False, gaintable=[fluxfile,bfile,kfile],
            gainfield=[gfield,'',''],
            parang=False, interp=['nearest',''])
    
    
    # now flag using 'rflag' option  for flux, phase cal and extra fields tight flagging
    for f in calfields:
        flagdata(vis=visname, mode="tfcrop", datacolumn="corrected",
                field=f, ntime="scan", timecutoff=6.0,
                freqcutoff=5.0, timefit="line", freqfit="line",
                flagdimension="freqtime", extendflags=False, timedevscale=5.0,
                freqdevscale=5.0, extendpols=False, growaround=False,
                action="apply", flagbackup=True, overwrite=True, writeflags=True)
        flagdata(vis=visname, mode="rflag", datacolumn="corrected",
                field=f, timecutoff=5.0, freqcutoff=5.0,
                timefit="poly", freqfit="line", flagdimension="freqtime",
                extendflags=False, timedevscale=4.0, freqdevscale=4.0,
                spectralmax=500.0, extendpols=False, growaround=False,
                flagneartime=False, flagnearfreq=False, action="apply",
                flagbackup=True, overwrite=True, writeflags=True)
    
        ## Now extend the flags (70% more means full flag, change if required)
        flagdata(vis=visname, mode="extend", field=f,
                datacolumn="corrected", clipzeros=True, ntime="scan",
                extendflags=False, extendpols=False, growtime=90.0, growfreq=90.0,
                growaround=False, flagneartime=False, flagnearfreq=False,
                action="apply", flagbackup=True, overwrite=True, writeflags=True)
    
    # Now flag for target - moderate flagging, more flagging in self-cal cycles
    flagdata(vis=visname, mode="tfcrop", datacolumn="corrected",
            field=target, ntime='scan', timecutoff=6.0, freqcutoff=5.0,
            timefit="poly", freqfit="line", flagdimension="freqtime",
            extendflags=False, timedevscale=5.0, freqdevscale=5.0,
            extendpols=False, growaround=False, action="apply", flagbackup=True,
            overwrite=True, writeflags=True)
    for i in range(5): 
    # now flag using 'rflag' option
        flagdata(vis=visname, mode="rflag", datacolumn="corrected",
                field=target, timecutoff=5.0, freqcutoff=5.0, timefit="poly",
                freqfit="poly", flagdimension="freqtime", extendflags=False,
                timedevscale=5.0, freqdevscale=5.0, spectralmax=500.0,
                extendpols=False, growaround=False, flagneartime=False,
                flagnearfreq=False, action="apply", flagbackup=True, overwrite=True,
                writeflags=True, ntime='scan')
    for i in range(5): 
    # now flag using 'rflag' option
        flagdata(vis=visname, mode="rflag", datacolumn="corrected",
                field=target, timecutoff=4.0, freqcutoff=4.0, timefit="poly",
                freqfit="poly", flagdimension="freqtime", extendflags=False,
                timedevscale=4.0, freqdevscale=4.0, spectralmax=500.0,
                extendpols=False, growaround=False, flagneartime=False,
                flagnearfreq=False, action="apply", flagbackup=True, overwrite=True,
                writeflags=True, ntime='scan')
    for i in range(5): 
    # now flag using 'rflag' option
        flagdata(vis=visname, mode="rflag", datacolumn="corrected",
                field=target, timecutoff=3.0, freqcutoff=3.0, timefit="poly",
                freqfit="poly", flagdimension="freqtime", extendflags=False,
                timedevscale=3.0, freqdevscale=3.0, spectralmax=500.0,
                extendpols=False, growaround=False, flagneartime=False,
                flagnearfreq=False, action="apply", flagbackup=True, overwrite=True,
                writeflags=True, ntime='scan')
   
    tclean( vis=visname,field=gfield,datacolumn='corrected',imagename=f'gaincalspw{spw}',imsize=5120,cell='0.75arcsec',gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='natural',niter=1000,gain=0.1)
    tclean( vis=visname,field=target,datacolumn='corrected',imagename=f'targetspw{spw}',imsize=5120,cell='0.75arcsec',gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='natural',niter=3000,gain=0.1)

    msmd.close()
    msmd.open(visname)
    scans = msmd.scansforfield(target)
    msmd.close()
    
    for i in range(0,len(scans),4):
        s = f'{scans[i]}~{scans[min(i+4,len(scans)-1)]}'
        tclean( vis=visname,field=target,datacolumn='corrected',imagename=f'targetspw{spw}scan{s}',scan=s,imsize=5120,cell='0.75arcsec',gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='natural',niter=1000,gain=0.1)

