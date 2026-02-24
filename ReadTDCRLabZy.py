
import numpy as np
import re
import datetime as dt
import csv

def readLabZyfile(fname,k):
    """This fonction return the coincidence counting values and measurement setup recorded in output files *.tdc.
                
    :param fname: Name of the file 
    :type fname: str
    :param k: Signal processing parameters
        1. for the extended time 1 and resolution time 1, 
        2. for the extended time 1 and resolution time 2, 
        3. for the extended time 2 and resolution time 1, 
        4. for the extended time 2 and resolution time 2.
    :type k: int
    :param rT: Triple coincidence count rates
    :type rT: array of float size n*1
    :param rD: Logic sum of double coincidence count rates
    :type rD: array of float size n*1
    :param rAB: Double coincidence count rates betwwen channels A and B
    :type rAB: array of float size n*1
    :param rBC: Double coincidence count rates betwwen channels B and C
    :type rBC: array of float size n*1
    :param rAC: Double coincidence count rates betwwen channels A and C
    :type rAC: array of float size n*1
    :param lT: Live time /s
    :type lT: array of float size n*1
    :param rtm: Real time /s
    :type rtm: float  
    :param yy: Year of the measurement
    :type yy: int
    :param mm: Month of the measurement 
    :type mm: int
    :param jj: Day of the measurement
    :type jj: int    
    :param t_EXT: Value of the extended time /µs
    :type t_EXT: float      
    :param t_W: Value of the resolution time /ns
    :type t_W: float     
    :param n: Number of recorded measurements
    :type n: int 
    :return: rT, rD, rAB, rBC, rAC, lT, rtm, yy, mm, jj, t_EXT, t_W, n
    :rtype: tuple
        
    
    """
    
    f=open(fname, "r") # open the file
    d=f.read() # read the file 
    f.close() # close the file
    
    t00=d.find("Hardware,")
    t01=d.find("Serial Number,")
    t02=d.find("Firmware Version,")
    t03=d.find("FPGA Version,")
    t031=d.find("Measurement, Settings")
    t04=d.find("Threshold A [mV],")
    t05=d.find("Threshold B [mV],")
    t06=d.find("Threshold C [mV],")
    
    ## extract the configuration parameters
    HardW=d[t00+9:t01]
    SerNum=d[t01+14:t02]
    FirmW=d[t02+17:t03]
    FPGA=d[t03+13:t031]
    
    ## find the flag key words in the file
    t1=d.find("Dead Time Extension 1 [us],")
    if FirmW[:-1]=="50.22":
        t1end=d.find("Extension 1 Dead Time Mode,")
    t2=d.find("Dead Time Extension 2 [us],")
    if FirmW[:-1]=="50.22":
        t2end=d.find("Extension 2 Dead Time Mode,")
    t3=d.find("Coincidence Window N [ns],")
    t4=d.find("Coincidence Window M [ns],")
    t5=d.find("Preset Sequential Runs,")
    t6=d.find("Preset Time per Run [s],")    
    #t7=d.find("Time Gap between Runs,")       # old tdcr firmware version
    t7=d.find("Time Gap between Runs [s],")   # new tdcr firmware version 11/2019
        
    ## extract the signal processing parameters
    ThsA=d[t04+17:t05]
    ThsB=d[t05+17:t06]
    ThsC=d[t06+17:t1]
    if k==1 or k==2: 
        if FirmW[:-1]=="50.22":
            t_EXT=float(d[t1+28:t1end])     # extended time /µs
        else:
            t_EXT=float(d[t1+28:t1+28+3])     # extended time /µs
    if k==3 or k==4:
        if FirmW[:-1]=="50.22":
            t_EXT=float(d[t2+28:t2end])     # extended time /µs
        else:
            # t_EXT=float(d[t2+28:t3])     # extended time /µs
            t_EXT=float(d[t2+28:t2+28+3])     # extended time /µs
    if k==1 or k==3: t_W=int(d[t3+26:t4])     # resolution time /ns
    if k==2 or k==4: t_W=int(d[t4+26:t5])     # resolution time /ns
    n=int(d[t5+23:t6])       # number of measurement run
    rtm=float(d[t6+24:t7])     # real time of each run /s
    
    # define void vector of size n
 #   Date=np.empty(n)   # Timestamp of the run
 #   lT_A=np.empty(n)   # dead time of channel A /s
 #   lT_B=np.empty(n)   # dead time of channel B /s
 #   lT_C=np.empty(n)   # dead time of channel C /s
    lT=np.empty(n)     # common dead time /s
    rA=np.empty(n)     # Count rate of channel A /cps
    rB=np.empty(n)     # Count rate of channel B /cps
    rC=np.empty(n)     # Count rate of channel C /cps
    rAB=np.empty(n)    # Coincidence count rate of channels A and B /cps
    rBC=np.empty(n)    # Coincidence count rate of channels B and C /cps
    rAC=np.empty(n)    # Coincidence count rate of channels A and C /cps
    rD=np.empty(n)     # Logic sum of double coincidence count rates /cps
    rT=np.empty(n)     # Triple coincidence count rates /cps

    offset=0 # to deal with the difference between time reference.
    for x in range(n):
        # if FirmW[:-1]=="50.22": 
        #     t100=d.find("Run"+str(x+1)+": START TIME: SYSTEM [dd/mm/yyyy hh:mm:ss.ms],")
        #     offset=26
        # else:
        #     t100=d.find("Run"+str(x+1)+": START TIME: SYSTEM,")
        # if t100==-1:
        #     t100=d.find("Run"+str(x+1)+": START TIME: LOCAL,")
        #     offset=-1
        #     if t100==-1:
        #         t100=d.find("Run"+str(x+1)+": START TIME: UTC,")
        #         offset=-3
        t100=d.find("Run"+str(x+1)+": START TIME:")
        # print("R",t100,d[t100:t100+50])
        for j in range(100):
            # print(d[t100+j:t100+j+2])
            if d[t100+j]=='.' and d[t100+j+1]!='m':
                t100=t100+j+5
                break
        # print("F",d[t100-25:t100])
        # print("s",d[t100-7:t100-5])
        # print("min",d[t100-10:t100-8])
        # print("h",d[t100-13:t100-11])
        # print("y",d[t100-19:t100-14])
        # print("m",d[t100-22:t100-20])
        # print("j",d[t100-25:t100-23])
        ## find the flag key words in the file
        
        t8=d.find("Run"+str(x+1)+": Live Time PMT A E1 [s],") 
        t9=d.find("Run"+str(x+1)+": Live Time PMT A E2 [s],")
        t10=d.find("Run"+str(x+1)+": Live Time PMT B E1 [s],") 
        t11=d.find("Run"+str(x+1)+": Live Time PMT B E2 [s],")
        t12=d.find("Run"+str(x+1)+": Live Time PMT C E1 [s],") 
        t13=d.find("Run"+str(x+1)+": Live Time PMT C E2 [s],")
        
        t14=d.find("Run"+str(x+1)+": PMT A Ext1 [cps],")
        t15=d.find("Run"+str(x+1)+": PMT B Ext1 [counts],")
        t16=d.find("Run"+str(x+1)+": PMT B Ext1 [cps],")
        t17=d.find("Run"+str(x+1)+": PMT C Ext1 [counts],")
        t18=d.find("Run"+str(x+1)+": PMT C Ext1 [cps],")
        t19=d.find("Run"+str(x+1)+": PMT A Ext2 [counts],")
        t20=d.find("Run"+str(x+1)+": PMT A Ext2 [cps],")
        t21=d.find("Run"+str(x+1)+": PMT B Ext2 [counts],")
        t22=d.find("Run"+str(x+1)+": PMT B Ext2 [cps],")
        t23=d.find("Run"+str(x+1)+": PMT C Ext2 [counts],")
        t24=d.find("Run"+str(x+1)+": PMT C Ext2 [cps],")        
        t25=d.find("\n\nRun"+str(x+1)+": Live Time AB Ext1 [s],")
        
        
        t200=d.find("Run"+str(x+1)+": Live Time T Ext1 [s],")
        t201=d.find("\n\nRun"+str(x+1)+": Coincidence AB_N1 [counts],")
        t26=d.find("Run"+str(x+1)+": Coincidence AB_N1 [cps],")
        t27=d.find("Run"+str(x+1)+": Coincidence BC_N1 [counts],")
        t28=d.find("Run"+str(x+1)+": Coincidence BC_N1 [cps],")
        t29=d.find("Run"+str(x+1)+": Coincidence AC_N1 [counts],")
        t30=d.find("Run"+str(x+1)+": Coincidence AC_N1 [cps],")
        t31=d.find("Run"+str(x+1)+": Coincidence D_N1 [counts],")
        t32=d.find("Run"+str(x+1)+": Coincidence D_N1 [cps],")
        t33=d.find("Run"+str(x+1)+": Coincidence T_N1 [counts],")
        t34=d.find("Run"+str(x+1)+": Coincidence T_N1 [cps],")
        t35=d.find("\nRun"+str(x+1)+": Coincidence AB_M1 [counts],")
        t36=d.find("Run"+str(x+1)+": Coincidence AB_M1 [cps],")
        t37=d.find("Run"+str(x+1)+": Coincidence BC_M1 [counts],")
        t38=d.find("Run"+str(x+1)+": Coincidence BC_M1 [cps],")
        t39=d.find("Run"+str(x+1)+": Coincidence AC_M1 [counts],")
        t40=d.find("Run"+str(x+1)+": Coincidence AC_M1 [cps],")
        t41=d.find("Run"+str(x+1)+": Coincidence D_M1 [counts],")
        t42=d.find("Run"+str(x+1)+": Coincidence D_M1 [cps],")
        t43=d.find("Run"+str(x+1)+": Coincidence T_M1 [counts],")
        t44=d.find("Run"+str(x+1)+": Coincidence T_M1 [cps],")
        t45=d.find("\nRun"+str(x+1)+": Live Time AB Ext2 [s],")
        
        t300=d.find("Run"+str(x+1)+": Live Time T Ext2 [s],")
        t301=d.find("\n\nRun"+str(x+1)+": Coincidence AB_N2 [counts],")
        t46=d.find("Run"+str(x+1)+": Coincidence AB_N2 [cps],")
        t47=d.find("Run"+str(x+1)+": Coincidence BC_N2 [counts],")
        t48=d.find("Run"+str(x+1)+": Coincidence BC_N2 [cps],")
        t49=d.find("Run"+str(x+1)+": Coincidence AC_N2 [counts],")
        t50=d.find("Run"+str(x+1)+": Coincidence AC_N2 [cps],")
        t51=d.find("Run"+str(x+1)+": Coincidence D_N2 [counts],")
        t52=d.find("Run"+str(x+1)+": Coincidence D_N2 [cps],")
        t53=d.find("Run"+str(x+1)+": Coincidence T_N2 [counts],")
        t54=d.find("Run"+str(x+1)+": Coincidence T_N2 [cps],")
        t55=d.find("\nRun"+str(x+1)+": Coincidence AB_M2 [counts],")
        t56=d.find("Run"+str(x+1)+": Coincidence AB_M2 [cps],")
        t57=d.find("Run"+str(x+1)+": Coincidence BC_M2 [counts],")
        t58=d.find("Run"+str(x+1)+": Coincidence BC_M2 [cps],")
        t59=d.find("Run"+str(x+1)+": Coincidence AC_M2 [counts],")
        t60=d.find("Run"+str(x+1)+": Coincidence AC_M2 [cps],")
        t61=d.find("Run"+str(x+1)+": Coincidence D_M2 [counts],")
        t62=d.find("Run"+str(x+1)+": Coincidence D_M2 [cps],")
        t63=d.find("Run"+str(x+1)+": Coincidence T_M2 [counts],")
        t64=d.find("Run"+str(x+1)+": Coincidence T_M2 [cps],")
        t65=d.find("\nRun"+str(x+2)+": START TIME: SYSTEM,")
        #if t65==-1:
        #    t65=d.find("Run"+str(x+2)+": START TIME: LOCAL,")
        #    offset=-1
        
        # Extrate the date
        jj=int(d[t100-25:t100-23])
        mm=int(d[t100-22:t100-20])
        yy=int(d[t100-19:t100-14])
        hh=int(d[t100-13:t100-11]) 
        mi=int(d[t100-10:t100-8])
        ss=int(d[t100-7:t100-5])
        
        
        
        # if x<9:
        #     jj=int(d[t100+25+offset:t100+27+offset])
        #     mm=int(d[t100+28+offset:t100+30+offset])
        #     yy=int(d[t100+31+offset:t100+35+offset])
        #     hh=int(d[t100+37+offset:t100+39+offset]) 
        #     mi=int(d[t100+40+offset:t100+42+offset])
        #     ss=int(d[t100+43+offset:t100+45+offset])
        # else:
        #     jj=int(d[t100+26+offset:t100+28+offset])
        #     mm=int(d[t100+29+offset:t100+31+offset])
        #     yy=int(d[t100+32+offset:t100+36+offset])
        #     hh=int(d[t100+38+offset:t100+40+offset]) 
        #     mi=int(d[t100+41+offset:t100+43+offset])
        #     ss=int(d[t100+44+offset:t100+46+offset])
        
        # convert in timestamp format
        #Dateb=datetime(yy,mm,jj,hh,mi,ss)
        #Date[x]=timegm(Dateb.timetuple())
        
        # extract and convert the counting data
        if k==1 or k==2: 
 #           lT_A[x]=float(d[t8+30:t9])        # live time PMT A /s
 #           lT_B[x]=float(d[t10+30:t11])      # live time PMT B /s
 #           lT_C[x]=float(d[t12+30:t13])      # live time PMT C /s
            lT[x]=float(re.sub(r'[^\d.]', '', d[t200+28:t201]))     # Common live time /s
            rA[x]=float(re.sub(r'[^\d.]', '', d[t14+24:t15]))      # Count rate channel A /cps
            rB[x]=float(re.sub(r'[^\d.]', '', d[t16+24:t17]))      # Count rate channel B /cps
            rC[x]=float(re.sub(r'[^\d.]', '', d[t18+24:t19]))      # Count rate channel C /cps
            if k==1:          
                rAB[x]=float(re.sub(r'[^\d.]', '', d[t26+31:t27]))   # Count rate channel AB /cps
                rBC[x]=float(re.sub(r'[^\d.]', '', d[t28+31:t29]))   # Count rate channel BC /cps
                rAC[x]=float(re.sub(r'[^\d.]', '', d[t30+31:t31]))   # Count rate channel AC /cps
                rD[x]=float(re.sub(r'[^\d.]', '', d[t32+30:t33]))    # Count rate channel D /cps
                rT[x]=float(re.sub(r'[^\d.]', '', d[t34+30:t35]))    # Count rate channel T /cps
            if k==2:
                rAB[x]=float(re.sub(r'[^\d.]', '', d[t36+31:t37]))   # Count rate channel AB /cps
                rBC[x]=float(re.sub(r'[^\d.]', '', d[t38+31:t39]))   # Count rate channel BC /cps
                rAC[x]=float(re.sub(r'[^\d.]', '', d[t40+31:t41]))   # Count rate channel AC /cps
                rD[x]=float(re.sub(r'[^\d.]', '', d[t42+30:t43]))    # Count rate channel D /cps
                rT[x]=float(re.sub(r'[^\d.]', '', d[t44+30:t45]))    # Count rate channel T /cps
        if k==3 or k==4: 
#            lT_A[x]=float(d[t9+30:t10])       # life time PMT A /s
#            lT_B[x]=float(d[t11+30:t12])      # life time PMT B /s
#            lT_C[x]=float(d[t13+30:t13+40])   # life time PMT C /s
            lT[x]=float(re.sub(r'[^\d.]', '', d[t300+28:t301]))    # Common live time /s
            rA[x]=float(re.sub(r'[^\d.]', '', d[t20+24:t21]))   # Count rate channel A /cps
            rB[x]=float(re.sub(r'[^\d.]', '', d[t22+24:t23]))   # Count rate channel B /cps
            rC[x]=float(re.sub(r'[^\d.]', '', d[t24+24:t25]))   # Count rate channel C /cps
            if k==3:
                rAB[x]=float(re.sub(r'[^\d.]', '', d[t46+31:t47]))   # Count rate channel AB /cps
                rBC[x]=float(re.sub(r'[^\d.]', '', d[t48+31:t49]))   # Count rate channel BC /cps
                rAC[x]=float(re.sub(r'[^\d.]', '', d[t50+31:t51]))   # Count rate channel AC /cps
                rD[x]=float(re.sub(r'[^\d.]', '', d[t52+30:t53]))    # Count rate channel D /cps
                rT[x]=float(re.sub(r'[^\d.]', '', d[t54+30:t55]))    # Count rate channel T /cps
            if k==4:
                rAB[x]=float(re.sub(r'[^\d.]', '', d[t56+31:t57]))   # Count rate channel AB /cps
                rBC[x]=float(re.sub(r'[^\d.]', '', d[t58+31:t59]))   # Count rate channel BC /cps
                rAC[x]=float(re.sub(r'[^\d.]', '', d[t60+31:t61]))    # Count rate channel AC /cps
                rD[x]=float(re.sub(r'[^\d.]', '', d[t62+30:t63]))   # Count rate channel D /cps
                if t65==-1:
                    t65=d.find("run"+str(x+2)+": STArT TIME: LOCAL,")
                    if t65==-1:
                        t65=d.find("run"+str(x+2)+": STArT TIME: UTC,")
                        rT[x]=float(re.sub(r'[^\d.]', '', d[t64+30:t64+40]))
                    else:
                        rT[x]=float(re.sub(r'[^\d.]', '', d[t64+30:t65]))
                else:
                    rT[x]=float(re.sub(r'[^\d.]', '', d[t64+30:t65]))
                                
    return rT,rD,rAB,rBC,rAC,lT,rtm,yy,mm,jj,t_EXT,t_W,n,rA,rB,rC,hh,mi,ss,HardW,SerNum,FirmW,FPGA,ThsA,ThsB,ThsC


def accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,rD,rT,t_W):
    """This fonction correction the counting data from accidental coincidence counting rates.
    
    Reference:
    C.Dutsov,P.Cassette,B.Sabotetal. Nuclear Inst. and Methods in Physics Research,A 977 (2020) 164292
    https://doi.org/10.1016/j.nima.2020.164292    
            
    :param rA: count rate on channel A. 
    :type rA: float
    :param rB: count rate on channel B. 
    :type rB: float
    :param rC: count rate on channel C. 
    :type rC: float
    :param rAB: count rate on channel AB. 
    :type rAB: float
    :param rBC: count rate on channel BC. 
    :type rBC: float
    :param rAC: count rate on channel AC. 
    :type rAC: float
    :param rD: count rate on double coincidence D. 
    :type rD: float
    :param rT: count rate on double coincidence T. 
    :type rT: float
    :param t_W: resolving time. 
    :type t_W: float

    :param rAB2: corrected count rate on channel AB. 
    :type rAB2: float
    :param rBC2: corrected count rate on channel BC. 
    :type rBC2: float
    :param rAC2: corrected count rate on channel AC. 
    :type rAC2: float
    :param rD2: corrected count rate on double coincidence D. 
    :type rD2: float
    :param rT2: corrected count rate on double coincidence T. 
    :type rT2: float


    :return: rAB2, rBC2, rAC2, rD2, rT
    :rtype: tuple of floats     
    """
    
    # Calculation of uncorrelated count rates
    pA=rA-rAC-rAB+rT # uncorrelated count rate on channel A
    pB=rB-rAB-rBC+rT # uncorrelated count rate on channel B
    pC=rC-rAC-rBC+rT # uncorrelated count rate on channel C
    pAB=rAB-rT # uncorrelated count rate on channel AB
    pBC=rBC-rT # uncorrelated count rate on channel BC
    pAC=rAC-rT # uncorrelated count rate on channel AC
    pS=pA+pB+pC # uncorrelated count rate on single channels
    pD=pAB+pBC+pAC # uncorrelated count rate on double coincidence channels
    pT=rT # uncorrelated count rate on triple coincidence channels

    # Calculation of accidental coincidence counting rates
    aAB=(2*(pA*pB+pA*pBC+pB*pAC+pAC*pBC)+(pS+pD-pAB)*(pAB+pT))*t_W*1e-9 # accidental count rate on AB cointing rate
    aBC=(2*(pB*pC+pB*pAC+pC*pAB+pAB*pAC)+(pS+pD-pBC)*(pBC+pT))*t_W*1e-9 # accidental count rate on BC cointing rate
    aAC=(2*(pA*pC+pA*pBC+pC*pAB+pAB*pBC)+(pS+pD-pAC)*(pAC+pT))*t_W*1e-9 # accidental count rate on AC cointing rate
    aD=(2*(pA*pB+pB*pC+pC*pA)+pS*(pD+pT))*t_W*1e-9 # accidental count rate on D cointing rate
    aT=(2*(pA*pBC+pB*pAC+pC*pAB)+(pS+pD)*pT+2*(pBC*pAB+pAC*pBC+pAC*pAB))*t_W*1e-9 # accidental count rate on T cointing rate

    # Corrected count rates
    rAB2=rAB-aAB
    rBC2=rBC-aBC
    rAC2=rAC-aAC
    rD2=rD-aD
    rT2=rT-aT
    
    return rAB2, rBC2, rAC2, rD2, rT2


def resetTriplet():
    """
    This function aims to reset the triplet buffer recording events within the 3 channels.
    """
    return [False,False,False]


def readDT5751(path, thres, baseTime, SumW, t_mes, t_W, t_EXT, recordLen):
    print("\nConvert time parameters...") 
    ResolTime=t_W*1e-9/baseTime # Coincidence resolution time in basetime unit
    ExtDT=t_EXT*1e-6/baseTime # Extented dead time in basetime unit

    print("\nInitialization...") 
    # counter initialization
    triplet=[False,False,False]
    Acount=0;Bcount=0;Ccount=0;ABcount=0;BCcount=0;ACcount=0;Scount=0;Dcount=0;Tcount=0

    # intilization of time parameters
    trigger_time=0 # time of the previous trig
    t=0 # triggering time of the currren event
    comdtW=0 # projected dead time
    realTime=0 # real time
    liveTime=0 # live time
    count_pulse=0 # global event counter
    w=1 # increment of intermediate results 

    # energy list of single events (live time filtered)
    E_list_A=[];E_list_B=[];E_list_C=[]

    # energy list of single events (unfiltered)
    E_list_A_raw=[];E_list_B_raw=[];E_list_C_raw=[]

    # energy list of coincident events (double)
    E_list_A_D=[];E_list_B_D=[];E_list_C_D=[]

    # energy list of coincident events (triple)
    E_list_A_T=[];E_list_B_T=[];E_list_C_T=[]

    # list of intermediate count rates
    Arate=[];Brate=[];Crate=[];ABrate=[];BCrate=[];ACrate=[];Srate=[];Drate=[]
    Trate=[]
    lt=[] # list of intermediate live times

    # list of timestamps of unfiltered single events
    tlistA_r=[];tlistB_r=[];tlistC_r=[]

    # list of timestamps of live-time filtered single events
    tlistA=[];tlistB=[];tlistC=[]

    # list of timestamps of coincidences
    tlistAB=[];tlistBC=[];tlistAC=[];tlistD=[];tlistT=[]

    print("\n Process the TDCR signal processing...") 
    with open(path) as csv_file:
        csvdata = csv.reader(csv_file, delimiter=';')
        for row in csvdata:
            if row[0] != "BOARD": # skip the header
                t=int(row[2])            # arrival time of the pulse event
                realTime=t*baseTime      # arrival time of the pulse event in second
                charge=float(row[SumW])  # charge of the pulse event

                # if Bkg_mode: # record every event to build energy spectra
                if int(row[1])==0:
                    E_list_A_raw.append(charge) # record charge to build channel A spectrum 
                    if len(tlistA_r)<recordLen: tlistA_r.append(realTime)
                if int(row[1])==1:
                    E_list_B_raw.append(charge) # record charge to build channel B spectrum 
                    if len(tlistB_r)<recordLen:tlistB_r.append(realTime)
                if int(row[1])==2:
                    E_list_C_raw.append(charge) # record charge to build channel C spectrum
                    if len(tlistC_r)<recordLen: tlistC_r.append(realTime)
                
                # (1) DETECT EVENT WHEN IDLE
                # ie. when the charge is above the energy threshold and when the
                # is set available after the appropriate extended time period (comdtW)
                # since the previous triggering.
                if charge>=thres and t>trigger_time+comdtW:
                    # (1.1) RECORD THE PREVIOUS EVENT IN COUNTERS AND UPDATE THE LIVETIME
                    # Read the triplet buffer
                    if sum(triplet)>=1: # at least one event recorded among the channels 
                        Scount+=1 # record the single events in the counter S
                        if triplet==[True, False, False]:
                            Acount+=1 # record event in channel A only
                            if len(E_list_A)<recordLen:
                                E_list_A.append(charge) # record charge to build channel A spectrum 
                                tlistA.append(realTime)
                        if triplet==[False, True, False]:
                            Bcount+=1 # record event in channel B only
                            if len(E_list_B)<recordLen:
                                E_list_B.append(charge) # record charge to build channel B spectrum 
                                tlistB.append(realTime)
                        if triplet==[False, False, True]:
                            Ccount+=1 # record event in channel C only
                            E_list_C.append(charge) # record charge to build channel C spectrum
                            tlistC.append(realTime)
                        if sum(triplet)>=2: # at least two events recorded among the channels
                            if int(row[1])==0 and len(E_list_A_D)<recordLen:
                                E_list_A_D.append(charge) # record charge to build channel A spectrum 
                            if int(row[1])==1 and len(E_list_B_D)<recordLen:
                                E_list_B_D.append(charge) # record charge to build channel B spectrum 
                            if int(row[1])==2 and len(E_list_C_D)<recordLen:
                                E_list_C_D.append(charge) # record charge to build channel C spectrum
                            Dcount+=1 # record the double coincidence event in the counter D
                            if len(tlistD)<recordLen: tlistD.append(realTime)
                            if triplet==[True, True, False]:
                                ABcount+=1 # record coincident event in channel A and B
                                if len(tlistAB)<recordLen: tlistAB.append(realTime)
                            if triplet==[False, True, True]:
                                BCcount+=1 # record coincident event in channel B and C
                                if len(tlistBC)<recordLen: tlistBC.append(realTime)
                            if triplet==[True, False, True]:
                                ACcount+=1 # record coincident event in channel A and C
                                if len(tlistAC)<recordLen: tlistAC.append(realTime)
                            if sum(triplet)==3: # at least three events recorded in each od the channels
                                if len(tlistT)<recordLen: tlistT.append(t*baseTime)    
                                if int(row[1])==0 and len(E_list_A_T)<recordLen: E_list_A_T.append(charge) # record charge to build channel A spectrum 
                                if int(row[1])==1 and len(E_list_B_T)<recordLen: E_list_B_T.append(charge) # record charge to build channel B spectrum 
                                if int(row[1])==2 and len(E_list_C_T)<recordLen: E_list_C_T.append(charge) # record charge to build channel C spectrum
                                Tcount+=1; ABcount+=1; BCcount+=1; ACcount+=1 # record the triple coincidence event in the counter T
                    else:
                        print("Warning: no count recorded when triggering in idle")
                    
                    # (1.1.(opt))PRODUCE AN INTERMEDIATE MEASUREMENT RESULT                                            
                    if realTime>t_mes*w: # end of a run
                        print("run #", w, int(realTime*w/60)," min processed.")
                        
                        # CALCULATE COUNT RATE
                        Arate.append(Acount/liveTime)
                        Brate.append(Bcount/liveTime)
                        Crate.append(Ccount/liveTime)
                        ABrate.append(ABcount/liveTime)
                        BCrate.append(BCcount/liveTime)
                        ACrate.append(ACcount/liveTime)
                        Srate.append(Scount/liveTime)
                        Drate.append(Dcount/liveTime)
                        Trate.append(Tcount/liveTime)
                        lt.append(liveTime)

                        # REINITIALIZE THE COUNTERS
                        Acount=0; Bcount=0; Ccount=0; ABcount=0; BCcount=0; ACcount=0; Scount=0; Dcount=0; Tcount=0
                        liveTime=0
                        w+=1 # new measurement
                    
                    # (1.2) UPDATE THE LIVETIME CALCULATION
                    # add the real time interval (t-trigger_time)
                    # and substract the extended dead time (comdtW)
                    # and substract the intrinsic dead time (count_pulse*busy)
                    liveTime+=(t-(trigger_time+comdtW))*baseTime # livetime in s
                                    
                    # (1.3) REINITIALIZE BUFFERS FOR A NEW EVENT ANALYSIS
                    triplet=resetTriplet()      # reset the coincidence event buffer
                    trigger_time=t              # set the new triggering time
                    triplet[int(row[1])]=True   # record of the event in the corresponding channel in the triplet buffer
                    comdtW=ExtDT                # impose the extended dead time
                    #count_pulse=1               # initialize the pulse counter used to evaluate the intrinsic dead time
                
                # (2) DETECT EVENT WHEN BUSY
                # Events arriving during the coincidence resolving time are recorded in the triplet event buffer
                # Cumulate the parralytime time by adding an extended dead time period starting from the pulse arrival
                elif charge>=thres: # only pulse event with charge above the defined threshold
                    count_pulse+=1 # increment the pulse counter
                    # (2-1) DETECT EVENT IN THE COINCIDENCE WINDOW
                    if t<trigger_time+ResolTime: # until the arrival is within the resolving time since the primary trigger
                        triplet[int(row[1])]=True # record of the event in the corresponding channel in the triplet buffer
                        comdtW+=t-trigger_time # reconduct the parallyzing time by the period from the primary trigger
                    # (2-1) DETECT EVENT OUT OF THE COINCIDENCE WINDOW
                    else:
                        # print((t-trigger_time)*baseTime*1e6)
                        comdtW=t-trigger_time+ExtDT # reconduct the parrallyzing time by adding an extended dead time period from the hidden event arrival time  
            else:
                continue
                print("\tHeader: ",row) # print the header of the list mode file
    Arate=np.asarray(Arate); Brate=np.asarray(Brate); Crate=np.asarray(Crate); Drate=np.asarray(Drate); Trate=np.asarray(Trate)
    ABrate=np.asarray(ABrate); BCrate=np.asarray(BCrate); ACrate=np.asarray(ACrate)
    return Arate,Brate,Crate,ABrate,BCrate,ACrate,Srate,Drate,Trate,lt,E_list_A,E_list_B,E_list_C,E_list_A_raw,E_list_B_raw,E_list_C_raw,E_list_A_D,E_list_B_D,E_list_C_D,E_list_A_T,E_list_B_T,E_list_C_T,tlistA_r,tlistB_r,tlistC_r,tlistA,tlistB,tlistC,tlistAB,tlistBC,tlistAC,tlistD,tlistT