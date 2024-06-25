import os
import glob
import shutil
origvis = f'{os.getcwd().split("/")[-1]}.ms'
for f in glob.glob('5GHz*.ms*'):
    shutil.rmtree(f)
for f in glob.glob('9GHz*.ms*'):
    shutil.rmtree(f)

# flagdata(vis=origvis, mode='manual',field='focus')

split(origvis, spw='0', outputvis = '5GHz.ms',datacolumn='ALL')
# vis = '5GHz.ms'
# for i,c in enumerate(range(0,2048,256)):
#     split(vis='5GHz.ms', spw=f'0:{c}~{c+255}', datacolumn='ALL',outputvis=f'5GHzspw{i}.ms')
# shutil.rmtree('5GHz.ms')
# vis = glob.glob('5GHzspw*.ms')
# concat(vis,concatvis='5GHz.ms')
# for v in vis:
#     shutil.rmtree(v)

split(origvis, spw='1', outputvis = '9GHz.ms',datacolumn='ALL')
# split(origvis, spw='4,5', outputvis = '19GHz.ms',datacolumn='ALL')
# vis = '9GHz.ms'
# for i,c in enumerate(range(0,2048,256)):
#     split(vis='9GHz.ms', spw=f'0:{c}~{c+255}', datacolumn='ALL',outputvis=f'9GHzspw{i}.ms')
# shutil.rmtree('9GHz.ms')
# vis = glob.glob('9GHzspw*.ms')
# concat(vis,concatvis='9GHz.ms')
# for v in vis:
#     shutil.rmtree(v)
# 
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
for f in glob.glob(f'*pol*D*'):
    shutil.rmtree(f)
for f in glob.glob(f'*flux*fluxscale*'):
    shutil.rmtree(f)
for visname in ['5GHz.ms','9GHz.ms','19GHz.ms']:
    

    fluxfield = '1934-638'
    target = 'GRB'
    gfield = '2333-528'
    if visname == '19GHz.ms':
        bfield = "0727-115"
        calfields = [fluxfield,bfield,gfield]
    else:
        bfield = fluxfield
        calfields = [fluxfield,gfield]
    msmd.close()
    msmd.open(visname)
    bfieldno = msmd.fieldsforname(bfield)[0]
    msmd.done()
    print(bfieldno)
    referenceant = 'CA01'
    allfields = [fluxfield,gfield,target]
    minbaselines=3
    spw = visname[:-3]
    kfilebase = f'delayspw{spw}.K'
    bfilebase = f'bpspw{spw}.B'
    gfilebase = f'gainspw{spw}.G'
    pregfilebase = f'gainspw{spw}.Gpre'
    fluxfilebase = f'fluxspw{spw}.fluxscale'
    polfilebase = f'polspw{spw}.D'
    setjy(vis=visname,field=fluxfield,scalebychan=True,standard="Stevens-Reynolds 2016")
    # flagdata(vis=visname, mode='manual',scan='0,44')
    # RFI issues in this one
    for f in calfields:
        flagdata(vis=visname, mode='tfcrop', field=f,
                ntime='scan', timecutoff=5.0, freqcutoff=5.0, timefit='line',
                freqfit='line', extendflags=False, timedevscale=5., freqdevscale=5.,
                extendpols=True, growaround=False, action='apply', flagbackup=True,
                overwrite=True, writeflags=True, datacolumn='DATA')
    plotms(vis=visname, xaxis='freq', yaxis='amp', showgui=False,
            field=fluxfield, plotfile=f'{spw}freqamp1934.jpg')
    plotms(vis=visname, xaxis='freq', yaxis='amp', showgui=False,
            field=gfield, plotfile=f'{spw}freqampgfield.jpg')
    plotms(vis=visname, xaxis='time', yaxis='amp', showgui=False,
            field=fluxfield, plotfile=f'{spw}timeamp1934.jpg')
    plotms(vis=visname, xaxis='time', yaxis='amp', showgui=False,
            field=gfield, plotfile=f'{spw}timeampgfield.jpg') 
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
    kxfile = f'{kfilebase}x'
    bfile = f'{bfilebase}'
    pregfile = f'{pregfilebase}'
    gfile = f'{gfilebase}'
    fluxfile = f'{fluxfilebase}'
    polfile = f'{polfilebase}'

    append=False
    gaincal(vis=visname, caltable = pregfile, field = bfield, refant = referenceant,
                minblperant = minbaselines, solnorm = False,  gaintype = 'G',
                solint = 'int', combine = '', calmode='p',
                parang = False,append = append)
    plotms(vis=pregfile, xaxis='time', yaxis='phase', coloraxis='corr', 
                field=fluxfield, iteraxis='antenna',plotrange=[-1,-1,-180,180],
                showgui= False, gridrows=3, gridcols=2, plotfile='initialgain.jpg')
    gaincal(vis=visname, caltable = kfile, field = bfield, refant = referenceant,
                minblperant = minbaselines, solnorm = False,  gaintype = 'K',
                solint = 'int', combine = '', parang = False,append = False)
    bandpass(vis=visname, caltable = bfile,
            field = bfield, refant = referenceant,
            minblperant = minbaselines, solnorm = False,  solint = 'int',
            combine = '', bandtype = 'B', fillgaps = 4,
            gaintable = [kfile], gainfield = bfield,
            parang = False, append = append)
    gaincal(vis=visname, caltable = kxfile, field=gfield, refant=referenceant,
            gaintype='KCROSS', smodel=[1.,0.,1.,0.], solint='inf', combine='scan',
            minblperant=minbaselines, minsnr=0, gaintable=[kfile,bfile],gainfield=[bfield,bfield])
    gaincal(vis=visname, caltable = gfile,
            field = fluxfield, refant = referenceant,
            minblperant = minbaselines, solnorm = False,  gaintype = 'G',
            solint = 'int', combine = '', calmode='ap',
            gaintable=[kfile,bfile,kxfile],gainfield=[bfield,bfield,gfield],
            parang = False, append = False)
    if fluxfield!=bfield:
        gaincal(vis=visname, caltable = gfile,
                field = bfield, refant = referenceant,
                minblperant = minbaselines, solnorm = False,  gaintype = 'G',
                solint = 'int', combine = '', calmode='ap',
                gaintable=[kfile,bfile,kxfile],gainfield=[bfield,bfield,gfield],
                parang = False, append = True)
    gaincal(vis=visname, caltable = gfile,
            field = gfield, refant = referenceant,
            minblperant = minbaselines, solnorm = False,  gaintype = 'G',
            solint = 'int', combine = '', calmode='ap',
            gaintable=[kfile,bfile,kxfile],gainfield=[bfield,bfield,gfield],
            parang = False, append = True)
    from casarecipes.atcapolhelpers import qufromgain
    qu = qufromgain(gfile)
    print(qu)
    smodel = [1,qu[bfieldno][0],qu[bfieldno][1],0]
    polcal(vis=visname,caltable=polfile,field=bfield,refant=referenceant,gaintable=[bfile,kxfile,gfile],poltype='D',solint='inf')
    plotms(vis=gfile,xaxis='time',yaxis='amp',coloraxis='corr',iteraxis='antenna',gridrows=3,gridcols=2,showgui=False,
            plotfile=f'relpolgaintable{spw}.jpg')
    kfile2 = f'{kfilebase}1'
    kxfile2 = f'{kfilebase}x1'
    bfile2 = f'{bfilebase}1'
    pregfile2 = f'{pregfilebase}1'
    gfile2 = f'{gfilebase}1'
    fluxfile2 = f'{fluxfilebase}1'
    polfile2 = f'{polfilebase}1'
    gaincal(vis=visname, caltable = pregfile2, field = bfield, refant = referenceant,
                minblperant = minbaselines, solnorm = False,  gaintype = 'G',
                solint = 'int', combine = '', calmode='p',
                parang = False,append = append, gaintable=[bfile,kxfile,gfile,polfile])
    plotms(vis=pregfile, xaxis='time', yaxis='phase', coloraxis='corr', 
                field=fluxfield, iteraxis='antenna',plotrange=[-1,-1,-180,180],
                showgui= False, gridrows=3, gridcols=2, plotfile='initialgain2.jpg')
    bandpass(vis=visname, caltable = bfile2,
            field = bfield, refant = referenceant,
            minblperant = minbaselines, solnorm = False,  solint = 'int',
            combine = '', bandtype = 'B', fillgaps = 4,
            gaintable = [gfile,polfile], gainfield = [bfield,bfield],
            parang = False, append = append)
    gaincal(vis=visname, caltable = gfile2,
            field = fluxfield, refant = referenceant,
            minblperant = minbaselines, solnorm = False,  gaintype = 'G',
            solint = 'int', combine = '', calmode='ap',
            gaintable=bfile2,
            parang = False, append = False)
    if fluxfield!=bfield:
        gaincal(vis=visname, caltable = gfile2,
                field = bfield, refant = referenceant,
                minblperant = minbaselines, solnorm = False,  gaintype = 'G',
                solint = 'int', combine = '', calmode='ap',
                gaintable=bfile2,
                parang = False, append = True)
    gaincal(vis=visname, caltable = gfile2,
            field = gfield, refant = referenceant,
            minblperant = minbaselines, solnorm = False,  gaintype = 'G',
            solint = 'int', combine = '', calmode='ap',
            gaintable=bfile2,smodel=smodel,
            parang = False, append = True)
    polcal(vis=visname,caltable=polfile2,field=bfield,refant=referenceant,gaintable=[bfile2,gfile2],poltype='D',solint='inf')
    if fluxfield!=bfield:
        myscale = fluxscale(vis=visname,caltable=gfile2,fluxtable=fluxfile2, reference=fluxfield,transfer=[gfield,bfield],incremental=False, fitorder=4)
    else:
        myscale = fluxscale(vis=visname,caltable=gfile2,fluxtable=fluxfile2, reference=fluxfield,transfer=[gfield],incremental=False, fitorder=4)
    applycal(vis=visname, field=fluxfield,
            selectdata=False, calwt=False, gaintable=[fluxfile2,bfile2,polfile2],
            gainfield=[fluxfield,'',''],
            parang=True, interp=['nearest','',''])
    applycal(vis=visname, field=gfield,
            selectdata=False, calwt=False, gaintable=[fluxfile2,bfile2,polfile2],
            gainfield=[gfield,'',''],
            parang=True, interp=['nearest','',''])
    if fluxfield!=bfield:
        applycal(vis=visname, field=bfield,
                selectdata=False, calwt=False, gaintable=[fluxfile2,bfile2,polfile2],
                gainfield=[gfield,'',''],
                parang=True, interp=['nearest','',''])
    
    applycal(vis=visname, field=target,
            selectdata=False, calwt=False, gaintable=[fluxfile2,bfile2,polfile2],
            gainfield=[gfield,'',''],
            parang=True, interp=['nearest',''])
    
    
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
    if spw=="5GHz":
        cell = '4arcsec'
    if spw=='9GHz':
        cell = '4arcsec'
    if spw=='19GHz':
        cell = '0.9arcsec'

    tclean( vis=visname,field=gfield,datacolumn='corrected',imagename=f'gaincalspw{spw}',imsize=5120,cell=cell,gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='briggs',robust=0,niter=1000,gain=0.1)
    tclean( vis=visname,field=target,datacolumn='corrected',imagename=f'targetspw{spw}',imsize=5120,cell=cell,gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='briggs',robust=0,stokes="IQUV",niter=3000,gain=0.1)

  #   msmd.close()
  #   msmd.open(visname)
  #   scans = msmd.scansforfield(target)
  #   msmd.close()
    
  #   for i in range(0,len(scans),4):
  #       s = f'{scans[i]}~{scans[min(i+4,len(scans)-1)]}'
  #       tclean( vis=visname,field=target,datacolumn='corrected',imagename=f'targetspw{spw}scan{s}',scan=s,imsize=5120,cell='4arcsec',gridder='standard',pblimit=-1e-12,deconvolver='hogbom',weighting='natural',niter=1000,gain=0.1)

