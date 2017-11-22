# Reduction of SABOCA data
#
import time
#import mpfit


sab = os.getenv('BOA_HOME_SABOCA') + '/'
execfile(sab + 'saboca-cabling.py')
execfile(sab + 'boaSaboca.py')
execfile(sab + 'saboca-secondary-fluxes.py')
execfile(sab + 'skydip.py')
execfile(r'/homes/ylin/saboca_reduce_script_update/saboca-planet-flux.py')
execfile(os.getenv('BOA_LOCAL_SABOCA')+'/saboca.boa')
execfile(os.getenv('BOA_LOCAL_SABOCA')+ '/boaSaboca.py')
BoaConfig.rcpPath = '/homes/schuller/boa/SVN/boa/rcp'
#oaConfig.rcpPath = '/aux/pc20179a/saboca_raw_data_three/rcp_crush/'
#outdir = r'/aux/pc20179a/saboca_raw_data_three/'

# List of scans in Atlas/2011/scans.txt

# 2011-04-13
#scans = [16395,16397,16398,16399]  # W43-A, W43-B
#taus  = [1.40,1.40,1.40,1.35]
#scans=(range(57993,58005))            #E 08.25
#scans=(range(57993,58041))            #E 08.25
#scans.extend(range(58379,58403))      #E 08.26
#scans.extend(range(58409,58433))      #E 08.26


# Limits of the map to cover everything - except G29.9
#x1,x2 = 98.95,98.8
#y1,y2 = 3.88,4.05

def basic(scan,taufile=''):
    global data
    data.read(scan)
    mjdref = data.ScanParam.MJD[0]
    if taufile:
	    tau = getTau(mjdref,'linear',taufile)
    else:
	    tau = scanTau()
	    
    #Opacity correction	    
    data.correctOpacity(tau)
    data.zeroStart()
    
    #Convert from Volts to Jy/beam
    data.Data *= array(VtoJy,'f')
    
    # Get RCPs
    nr=len(data.ScanParam.MJD)
    nr = nr -1
    mjdref = (data.ScanParam.MJD[nr]-data.ScanParam.MJD[0])/2.+data.ScanParam.MJD[0]
    # >> axels version 
    rcp=getSabocaRCP(mjdref)
    #rcp=getSabocaRCP(mjdref)    
    updateRCP(rcp)
    print rcp
    #old rcp action:
    #rcp = 'saboca-2010-05.rcp'
    #data.MessHand.info("RCP file : %s " % rcp)
    #data.BolometerArray.updateRCP(rcp)
    
    #Normalize signals by bolometer gains
    #  Note: flat()       >> point source
    #        flatfield()  >> extended emission
    data.flatfield()
    # ------
    # >> from redsweak
    bad=getSabocaCross(mjdref)
    data.MessHand.info("Bad channels : %s " % bad)
    data.flagChannels(bad)
    #
    inverted=getSabocaInvert(mjdref)
    data.MessHand.info("Inverted channels : %s " % inverted)
    data.flagChannels(bad)
    #
    inverted=getSabocaInvert(mjdref)
    data.MessHand.info("Inverted channels : %s " % inverted)
    invertSomeChannels(inverted)
    # >> -----

def redssky(scan):
    global data
    tst = data.read(scan)
    if tst:
        print "Problem reading scan %s"%(str(scan))
        return

    execfile(sab+'sskydip.boa')
   
def redcal(scan,tau):
    global data
    basic(scan,taufile=tau)
    
    data.flagFractionRms(ratio=3)
    data.flagSpeed(below=10.)
    data.flagSpeed(above=150.)
    data.flagAccel(above=800.)

    data.polynomialBaseline(order=1)
    data.flagPosition(radius=25,flag=8)
    data.medianNoiseRemoval(chanRef=-1,factor=0.8,nbloop=5)#set to -1 to compute the relative gains with respect to mean signal
    data.medianBaseline()
    data.flagFractionRms(ratio=5,below=0)
    medianNoiseRemoval(chanRef=-1,factor=0.8,nbloop=5)
    data.medianBaseline()
    data.computeWeight()
    data.unflag(flag=8)
    data.doMap(sizeX=[-50,50],sizeY=[-50,50],oversamp=5,noPlot=1)
    data.solvePointingOnMap(plot=1,radius=20)
    obsflux = data.PointingResult['gauss_peak']['value']

    source_name = data.ScanParam.Object
    nr=len(data.ScanParam.MJD)
    nr = nr -1
    mjdref = (data.ScanParam.MJD[nr]-data.ScanParam.MJD[0])/2.+data.ScanParam.MJD[0]
    if calibFluxes.has_key(string.upper(source_name)):
        expect_flux = calibFluxes[string.upper(source_name)]        
        percent = 100.0*obsflux/expect_flux
        print "-----------------------------------------------------------"
        print "Scan %s - %s:  %7.2f [expected: %7.2f, %6.2f %%]"%(str(scan),
                                                                  source_name,
                                                                  obsflux,
                                                                  expect_flux,
                                                                  percent)
        print "-----------------------------------------------------------"
    elif source_name in ['Uranus','Neptune','Mars','Saturn','Jupiter','Venus']:
        astrotime,astrodate=getAstroDate(data)
        beam = 8.0
        freq = 852.0

        # NOTE: the following call uses the function PlanetFlux
        # defined in $BOA_HOME_SABOCA/saboca-planet-flux.py

        print "NOTICE!!!!!!",source_name,astrotime,astrodate,(beam),(freq)
        expect_flux = PlanetFlux(source_name,astrotime,astrodate,(beam),(freq))
        percent = 100.0*obsflux/expect_flux
        print "-----------------------------------------------------------"
        print "Scan %s - %s:  %7.2f [expected: %7.2f, %6.2f %%]"%(str(scan),
                                                                  source_name,
                                                                  obsflux,
                                                                  expect_flux,
                                                                  percent)
        print "-----------------------------------------------------------"

    #########write the calibration data results to calibration.dat##########
    #format: scannumber MJD percentage
    scannr = data.ScanParam.ScanNum
    date = data.ScanParam.DateObs
    calcorr = percent/100.0

    print scannr, date, mjdref, calcorr
    scanel  = fStat.f_mean(data.ScanParam.El)
    print scanel

    

    
    #f = open(outdir+'calibration-long-test.dat','a')
    #print "SEE IF RIGHT test"
    #print "%10s  %i  %s %18.12f %5.3f %5.3f %7.3f %7.3f %5.3f %5.3f"%(source_name,scannr,scandate,mjdref,calcorr,taucorr,obsflux,expect_flux,scanel,tau)
 
    #f.write('%10s  %i  %s %18.12f %5.3f %5.3f %7.3f %7.3f %5.3f %5.3f\n' %(source_name,scannr,scandate,mjdref,calcorr,taucorr,obsflux,expect_flux,scanel,tau))
    #f.close()
    if tau is not '':
	    taui = getTau(mjdref,'linear',tau)
    else:
	    taui = scanTau()
    taucorr = exp(taui/sin(scanel * pi / 180.))
    #print 'TEST'
    print taucorr
    print "----------------------------------------------------------------"
    print "Writing calibration results to \n"
    print "Format:scanNumber obsDate mjdref calcorr tau taucorr"
    print "----------------------------------------------------------------"
    f = open('./calibration-modi46_1206.dat','a')
    f.write('%i  %s %18.12f %5.3f %5.3f\n' %(scannr,date,mjdref,calcorr,taucorr))
    f.close()

#########################################################
# Simple processing of individual scan
#
def proc0(scan,tau):
    global data
    basic(scan,tau)
            
    # standard reduction
    data.flagSpeed(below=10.)
    data.flagSpeed(above=150.)
    data.flagAccel(above=800.)
    data.medianNoiseRemoval(chanRef=-1,factor=0.96,nbloop=3)
    data.flagFractionRms(ratio=5)
    data.medianNoiseRemoval(chanRef=-1,factor=0.98,nbloop=2)
    data.computeWeight()
    data.flagFractionRms(ratio=3,below=0)
    return data


# Full standard processing of individual scan
def process(scan,taufile,calfile,model=None,subtract=0,threshold=5):
    global data
    basic(scan,taufile)

    # mask or subtract model, if present
    if model:
        if subtract:
            data.addSource(model=model,factor=-1.)
        else:
            data.flagSource(model=model,threshold=threshold,flag=8)
            
    # standard reduction
    # >flagging bad channels:
    data.flagSpeed(below=10.)
    data.flagSpeed(above=150.)
    data.flagAccel(above=800.)
    
    #flag rcp? flagC(cross?)
    #flag dead/noisy channels? >> data.flagFractionsRms(ratio=5)
    # First 2 correlated noise removal on all channels and despiking
    data.medianNoiseRemoval(chanRef=-1,factor=0.96,nbloop=3)
    data.flagFractionRms(ratio=5)
    data.medianNoiseRemoval(chanRef=-1,factor=0.98,nbloop=2)
    data.flagFractionRms(ratio=3,below=0)

    data.polynomialBaseline(order=1)

    data.despike()
#################################################
    data.flagFractionRms(ratio=3,below=0)
    data.despike()
#################################################
    # no correlated noise removal?
    
    # Filtering on low frequencies
    data.flattenFreq(below=0.2,hiref=0.35)
####The values for the parameters below and hiref should be chosen depending on the expected brightness
#and spatial scale of the sources. Since choice of these parameters will affect the final map care should
#be taken to choose values which are most appropriate to the particular type of source. See Section 3.8.4
#for further details.
#################################################
    data.despike()
    
    # Remove first order baseline again
    data.polynomialBaseline(order=1)
    sensi = calcsensitivity()
    
    # Compute weifths based on rms of each channel
    data.computeWeight()
    data.unflag(flag=8)
    data.despike(below=-10,above=50)

    print '########################################'
    print "Sensitivity: %6.1f mJy sqrt(s)"%(sensi)
    print '#######################################'

    # put back model, if subtracted
    if model and subtract:
        data.addSource(model=model,factor=1.)


# ------------- to write out parameters ---------------
    source=data.ScanParam.Object
    scandate=data.ScanParam.DateObs
    scannr=data.ScanParam.ScanNum
    scanel  = fStat.f_mean(data.ScanParam.El)
    mjdref = data.ScanParam.MJD[0]    
    if calfile:
       calcorr = getCalCorr(mjdref,'linear',calfile)
       data.Data /= array((calcorr),'f')
    else:
       calcorr = 1.0
    if taufile:
	    tau = getTau(mjdref,'linear',taufile)
    else:
	    tau = scanTau()
    #tau = scanTau()    
    taucorr = exp(tau/sin(scanel * pi / 180.))    
    output=file(outdir+source+'.log','a')
    output.write('%i  %s %s %18.12f %5.1f %5.3f %5.3f %5.1f %5.3f\n' %(scannr,source,scandate,mjdref,sensi,taucorr,calcorr,scanel,tau))
    output.close()
# ------------- to write out parameters ---------------

    # Compute and return a map
    #data.doMap(system='eq',sizeX=[c1[0],c2[0]],sizeY=[c1[1],c2[1]],
    #           oversamp=4,noPlot=1) #orig one
###########change to galactic system###########################maybe should be replaced by 'data.scanParam.Coord',which is in RA-DEC coordinates
    import numpy as np
    import re
    #try:
    #  global c1
    #  global c2
    #  c1 = [-80,-80]
    #  c2 = [80,80]
    #  data.doMap(sizeX=[c1[0],c2[0]],sizeY=[c1[1],c2[1]],oversamp=4,noPlot=1)
      #centerx = np.asarray(re.split('[+-]+', data.ScanParam.Object[2:]),dtype=np.float32)[0]
     # if '+' in data.ScanParam.Object:
     #	 centery = np.asarray(re.split('[+-]+', data.ScanParam.Object[2:]),dtype=np.float32)[1]
     # else:
     #  	 centery= -1*np.asarray(re.split('[+-]+', data.ScanParam.Object[2:]),dtype=np.float32)[1]
     # global c1
    #  global c2
      #c1 = [centerx-0.03,centery-0.03]
      #c2 = [centerx+0.03,centery+0.03]
      #data.doMap(system='gal',sizeX=[c1[0],c2[0]],sizeY=[c1[1],c2[1]],oversamp=4,noPlot=1)
    #except:
    global c1
    global c2
    c1 = [data.ScanParam.Coord[0]-0.06,data.ScanParam.Coord[1]-0.06]
    c2 = [data.ScanParam.Coord[0]+0.06,data.ScanParam.Coord[1]+0.06]
    data.doMap(system='EQ',sizeX=[c2[0],c1[0]],sizeY=[c1[1],c2[1]],oversamp=4,noPlot=1)
     
################################################################
    #  data.doMap(system='gal',sizeX=[x1,x2],sizeY=[y1,y2],
    #             oversamp=3,noPlot=1)
    #ms = copy.deepcopy(data.Map)
    #return ms
    #return data
    return copy.deepcopy(data.Map)
    


 
#########################################################
# First level of loop: call "process" on all scans
def loop(taufile='',calfile='',ms=0,inmodel=None):
    Plot.panels(2,1)
    
    for i in range(len(scans)):
        oneMap = process(scans[i],taufile,calfile,
                         model=inmodel,threshold=8)
        Plot.nextpage()
        oneMap.display(noerase=1)
        if ms:
            ms = mapsumfast([ms,oneMap])
        else:
            ms = copy.deepcopy(oneMap)
        Plot.nextpage()
        ms.display(noerase=1)
 #   return ms
    return copy.deepcopy(ms)

# very first iteration result dumped to: W43-complex-step1.data

# second level of loop: call "loop" iteratively
def looploop(iter=5,taufile='',calfile=''):
    ms0 = restoreFile(outdir+'iter0.data')
    snr = copy.deepcopy(ms0)
    snr.Data *= sqrt(ms0.Weight)
    snr.smoothBy(5./3600.)

    for i in range(iter):
        print "-----------%i LOOP---------"%(i+1)
        mapNext = loop(ms=0,inmodel=snr,taufile=taufile)
        mapNext.dumpMap('iter%i.data'%(i+1))
        snr = copy.deepcopy(mapNext)
        snr.Data *= sqrt(mapNext.Weight)
        snr.smoothBy(5./3600.)

    return mapNext

#########################################################
# first level of loop (i.e. on all scans) but *subtracting* the model
def loopsub(taufile='',calfile='',model=None):
    ms = 0
    for i in range(len(scans)):
        oneMap = process(scans[i],taufile,calfile,
                         model=model,subtract=1)
        Plot.nextpage()
        oneMap.display(noerase=1,aspect=1)
        if ms:
            ms = mapsumfast([ms,oneMap])
        else:
            ms = oneMap
        Plot.nextpage()
        ms.display(noerase=1,aspect=1)

    return ms
    
# second level of loop: call "loopsub" iteratively
def loopsubloop(iter=8,start=2,taufile='',calfile=''):
    init = restoreFile(outdir+'iter%i.data'%(start))
    snr = copy.deepcopy(init)
    snr.Data *= sqrt(init.Weight)
    snr.smoothBy(5./3600.)

    model = copy.deepcopy(init)
    test = snr.Data < 3.5 or model.Data == float('nan')
    model.Data = where(test,0.,model.Data)

    Plot.panels(2,1)
    for i in range(iter):
        next = loopsub(model=model,taufile=taufile,calfile=calfile)
        next.dumpMap('iter%i.data'%(start+i+1))

        snr = copy.deepcopy(next)
        snr.Data *= sqrt(next.Weight)
        snr.smoothBy(5./3600.)

        model = copy.deepcopy(next)
        test = snr.Data < 3.5 or model.Data == float('nan')
        model.Data = where(test,0.,model.Data)

    return next

#########################################################
# Some utilities to look at the reduced maps...
def maplist(last=10):
    mlist = []
    for i in range(1,last+1):
        m = restoreFile(outdir+'iter%i.data'%(i))
        mlist.append(copy.deepcopy(m))
    return mlist

def movie(mlist,pause=0.1,limZ=[]):
    #x1,x2 = c1[0],c2[0]
    #y1,y2 = c1[1],c2[1]
    for m in mlist:
        m.display(limitsZ=limZ,aspect=1)#imitsX=[x1,x2],limitsY=[y1,y2],limitsZ=limZ,aspect=1)
        time.sleep(pause)

def converge(mlist):
    # function to check how the iterative reduction converges
    # computes and plot peak flux and integrated flux in a
    # given region of the map, as a function of iter. number
    oneMap = mlist[0]
    #x1,y1 = 50,50
    #x2,y2 = 70,70
    #x1,y1 = int(x1+0.5),int(y1+0.5)
    #x2,y2 = int(x2+0.5),int(y2+0.5)
    x1,y1 = int(shape(oneMap.Data)[0]/2.-10),int(shape(oneMap.Data)[1]/2.-10)
    x2,y2 = int(shape(oneMap.Data)[0]/2.+10),int(shape(oneMap.Data)[1]/2.+10)
    print "____________",x1,x2,y1,y2
    print "____________"
    peak,sums,relat = [],[],[]
    for i in range(len(mlist)):
        m = mlist[i]
        piece = m.Data[x1-1:x2+1,y1-1:y2+1]
        mini,maxi = fStat.minmax(piece)
        mean = fStat.f_mean(ravel(piece))
        disp = fStat.f_rms(ravel(piece),mean)
        total = sum(ravel(piece))
        result = " mini = %5.2f  maxi = %5.2f "%(mini,maxi)
        result += "mean = %5.3f  rms = %5.3f  sum = %8.2f"%(mean,disp,total)
        if i > 0:
            # compute relative change
            rel = 100.*(total - sums[-1])/sums[-1]
            result += "  ds/s = %6.2f %%"%(rel)
            relat.append(rel)
        sums.append(total)
        peak.append(maxi)
        print result
    close()
    openDev(outdir+source+'converge.ps/PS')
    Plot.panels(3,1)
    xx = range(1,len(mlist)+1)
    Plot.nextpage()
    plot(xx,peak,noerase=1,labelX='Step',labelY='Peak flux')   
    #plt.plot(xx,peak,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5) 
    Plot.nextpage()
    plot(xx,sums,noerase=1,labelX='Step',labelY='Integ. flux') 
    #plt.plot(xx,sums,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5)    
    Plot.nextpage()
    plot(xx[1:],relat,noerase=1,labelX='Step',labelY='Relative change [%]')    
    #plt.plot(xx[1:],relat,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5)    
    close()
    

    import matplotlib.pyplot as plt
    plt.clf()
    fig = plt.figure(figsize=(20.5,5))

    plt.subplot(152)
    plt.title('Peak flux of each iter')
    plt.plot(xx,peak,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5) 

    plt.subplot(153)
    plt.title('Integrated flux of each iter')
    plt.plot(xx,sums,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5) 

    plt.subplot(154)
    plt.title('Relative flux change of each iter')
    plt.plot(xx[1:],relat,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5)

    fig.savefig(outdir+str(source)+r'converge_mpl.ps')    
def converge(mlist,edge=False):
    # function to check how the iterative reduction converges
    # computes and plot peak flux and integrated flux in a
    # given region of the map, as a function of iter. number


    #edge: for sources that the brightest clump is not located at the center
    #additionally detect the maximum and cut slices around it.
    oneMap = mlist[-1]
    #x1,y1 = 50,50
    #x2,y2 = 70,70
    #x1,y1 = int(x1+0.5),int(y1+0.5)
    #x2,y2 = int(x2+0.5),int(y2+0.5)
    import numpy as np
    if edge == False:
    	x1,y1 = int(shape(oneMap.Data)[0]/2.-10),int(shape(oneMap.Data)[1]/2.-10)
    	x2,y2 = int(shape(oneMap.Data)[0]/2.+10),int(shape(oneMap.Data)[1]/2.+10)
    	print "____________",x1,x2,y1,y2
    	print "____________"
    if edge == True:
        xc, yc = np.argwhere(oneMap.Data == np.nanmax(oneMap.Data)).flatten()[0],np.argwhere(oneMap.Data == np.nanmax(oneMap.Data)).flatten()[1]
        x1, y1 = xc-10,yc-10
        x2, y2 = xc+10,yc+10
        print "____________",x1,x2,y1,y2
    	print "____________"
        print "Maximum:%.5f"%np.nanmax(oneMap.Data)
    peak,sums,relat = [],[],[]
    for i in range(len(mlist)):
        m = mlist[i]
        piece = m.Data[x1-1:x2+1,y1-1:y2+1]
        mini,maxi = fStat.minmax(piece)
        mean = fStat.f_mean(ravel(piece))
        disp = fStat.f_rms(ravel(piece),mean)
        total = sum(ravel(piece))
        result = " mini = %5.2f  maxi = %5.2f "%(mini,maxi)
        result += "mean = %5.3f  rms = %5.3f  sum = %8.2f"%(mean,disp,total)
        if i > 0:
            # compute relative change
            rel = 100.*(total - sums[-1])/sums[-1]
            result += "  ds/s = %6.2f %%"%(rel)
            relat.append(rel)
        sums.append(total)
        peak.append(maxi)
        print result
    close()
    openDev(outdir+source+'converge.ps/PS')
    Plot.panels(3,1)
    xx = range(1,len(mlist)+1)
    Plot.nextpage()
    plot(xx,peak,noerase=1,labelX='Step',labelY='Peak flux')   
    #plt.plot(xx,peak,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5) 
    Plot.nextpage()
    plot(xx,sums,noerase=1,labelX='Step',labelY='Integ. flux') 
    #plt.plot(xx,sums,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5)    
    Plot.nextpage()
    plot(xx[1:],relat,noerase=1,labelX='Step',labelY='Relative change [%]')    
    #plt.plot(xx[1:],relat,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5)    
    close()
    

    import matplotlib.pyplot as plt
    plt.clf()
    fig = plt.figure(figsize=(20.5,5))

    plt.subplot(152)
    plt.title('Peak flux of each iter')
    plt.plot(xx,peak,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5) 

    plt.subplot(153)
    plt.title('Integrated flux of each iter')
    plt.plot(xx,sums,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5) 

    plt.subplot(154)
    plt.title('Relative flux change of each iter')
    plt.plot(xx[1:],relat,marker='o',markersize=7.5,markeredgecolor='none',color='r',alpha=0.5)

    fig.savefig(outdir+str(source)+r'converge_mpl.ps')    


#def diagnosis(mlist)

#def diagnosis(mlist)

    




