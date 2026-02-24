import tdcrpy as td
import datetime as dt
import numpy as np
import ReadTDCRLabZy as rtd
import importlib.metadata
import csv
import os
import ast
from fractions import Fraction
import configparser

kBvec = [0.5e-5, 0.6e-5, 0.7e-5, 0.8e-5, 0.9e-5]  # Birks constant (cm/keV)

version = "2.17.1" # version of TDCRPy
kbstr = "10"

modelA = True # Model analytic (used in the framwork of the ESIR - works on for pure beta emitters)
modelS = True # Model stochastic (more general, more accurate, works for all emitters)
N = 5000 # Number of MC trials

# list the intput files to be processed
config_Filename_list = [
"inputs\\S-35\\measurement_config.ini",
]

for kB in kBvec:
    for config_Filename in config_Filename_list:
        # --- Load config file ---
        print("\nLoading config file:", config_Filename)
        config = configparser.ConfigParser()
        config.read(config_Filename)   # Replace with your filename

        # --- Helper function to safely evaluate numbers or expressions ---
        def parse_value(v):
            try:
                # first try integer or float
                return float(v) if "." in v or "e" in v.lower() else int(v)
            except ValueError:
                try:
                    # try to evaluate Python expressions: dt.datetime(...), fractions, etc.
                    return ast.literal_eval(v)
                except Exception:
                    return v  # return raw string if nothing else works

        # --- Parse all values from [Inputs] ---
        inputs = {}
        for key, value in config["Inputs"].items():
            inputs[key] = parse_value(value)

        # --- Example: Accessing parsed values ---
        print("Radionuclide:", inputs["rad"])
        print("Half-life (s):", inputs["t05"])
        print("Half-life uncertainty (s):", inputs["ut05"])
        print("Laboratory:", inputs["laboratory"])
        print("Year:", inputs["year"])
        inputs["kb"] = kB
        print("Birsks constant (cm/keV):", inputs["kb"])
        print("Birks constant min (cm/keV):", inputs["kbmin"])
        print("Birks constant max (cm/keV):", inputs["kbmax"])
        print("Quantum efficiency PMT A:", inputs["quantum_efficiency_pmta"])
        print("Quantum efficiency PMT B:", inputs["quantum_efficiency_pmtb"])
        print("Quantum efficiency PMT C:", inputs["quantum_efficiency_pmtc"])
        print("DAQ type:", inputs["daq"])
        print("DSP parameters:", inputs["dsp_params"])
        inputs["ref_date"] = dt.datetime.strptime(inputs["ref_date"], "%Y-%m-%d %H:%M:%S")
        print("Reference date:", inputs["ref_date"])
        print("Source name:", inputs["source_name"])
        print("Grey filter ND:", inputs["grey_filter_nd"])
        print("Diffusive vial:", inputs.get("diffusive_vial", False))
        print("Mass (g):", inputs["mass_g"])
        print("Mass uncertainty (g):", inputs["u_mass_g"])
        print("Total source volume (ml):",inputs["total_source_vol_ml"])
        print("LS cocktail:", inputs["ls_cocktail"])
        if "/" in str(inputs["frac_aq"]):
            # inputs["frac_aq"] = eval(inputs["frac_aq"]) # Only use if inputs are trusted
            # # OR safer:
            inputs["frac_aq"] = sum(float(x) for i, x in enumerate(inputs["frac_aq"].split('/')) if i == 0) / float(inputs["frac_aq"].split('/')[1])
        print("Fraction of aqueous phase:", inputs["frac_aq"])
        print("Solvent:", inputs["solvant"])
        print("Solvent concentration:", inputs["solvant_conc"])
        print("Path to background data:", inputs["path_ntd_bck"])
        print("Path to source data:", inputs["path_ntd_src"])





        inputs["daq"] == "nanoTDCR"
        if inputs["dsp_params"] == 1:
            t_EXT = 50 # extended dead time (µs)
            t_W = 50 # resolution time (ns)
        elif inputs["dsp_params"] == 2:
            t_EXT = 50 # extended dead time (µs)
            t_W = 100 # resolution time (ns)
        elif inputs["dsp_params"] == 3:
            t_EXT = 10 # extended dead time (µs)
            t_W = 50 # resolution time (ns)
        elif inputs["dsp_params"] == 4:
            t_EXT = 10 # extended dead time (µs)
            t_W = 100 # resolution time (ns)

        # DAQ = "DT5751"
        # measTime = 7200 # measurement time (s)
        # t_W = 100 # coincidence window (ns)
        # t_EXT = 100 # extended dead time (µs)
        # t_Wmin = 40 # minimum coincidence window for uncertainty estimation (ns)
        # t_Wmax = 160 # maximum coincidence window for uncertainty estimation (ns)
        # t_EXTmin = 50 # minimum extended dead time for uncertainty estimation (ns)
        # t_EXTmax = 150 # maximum extended dead time for uncertainty estimation (ns)
        # thres = 0 # energy threshold
        # baseTime = 1e-12 # base time unit (s)
        # n_run = 10 # number of runs to be averaged
        # sumWindow = 3 # sum window for pulse integration - 3 for long gate, 4 for short gate
        # recordLen = 100 # event record length for distribution plotting


        if inputs["daq"] == "nanoTDCR":
            # Extract TDCR background measurements
            rT,rD,rAB,rBC,rAC,lT,rtm,yy,mm,jj,t_EXT,t_W,n,rA,rB,rC,hh,mi,ss,HardW,SerNum,FirmW,FPGA,ThsA,ThsB,ThsC = rtd.readLabZyfile(inputs["path_ntd_bck"],inputs["dsp_params"])
            # Correct for accidental coincidences
            _ , _, _, D0i, T0i =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,rD,rT,t_W)
            D0 = np.mean(D0i) # background count rate (s-1)
            uD0 = np.std(D0i)/np.sqrt(len(rD)) # standard uncertainty on the background count rate (s-1)
            T0 = np.mean(T0i) # background triple count rate (s-1)
            uT0 = np.std(T0i)/np.sqrt(len(rD)) # standard uncertainty on the background triple count rate (s-1)

            # Uncertainty on dsp parameters
            rT,longDeadTime,rAB,rBC,rAC,lT,rtm,yy,mm,jj,t_EXT,t_W,n,rA,rB,rC,hh,mi,ss,HardW,SerNum,FirmW,FPGA,ThsA,ThsB,ThsC = rtd.readLabZyfile(inputs["path_ntd_src"],2)
            _, _, _, longDeadTime, _ =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,longDeadTime,rT,t_W)
            rT,shortDeadTime,rAB,rBC,rAC,lT,rtm,yy,mm,jj,t_EXT,t_W,n,rA,rB,rC,hh,mi,ss,HardW,SerNum,FirmW,FPGA,ThsA,ThsB,ThsC = rtd.readLabZyfile(inputs["path_ntd_src"],4)
            _, _, _, shortDeadTime, _ =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,shortDeadTime,rT,t_W)
            rT,longCoincWindow,rAB,rBC,rAC,lT,rtm,yy,mm,jj,t_EXT,t_W,n,rA,rB,rC,hh,mi,ss,HardW,SerNum,FirmW,FPGA,ThsA,ThsB,ThsC  = rtd.readLabZyfile(inputs["path_ntd_src"],2)
            _, _, _, longCoincWindow, _ =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,longCoincWindow,rT,t_W)
            rT,shortCoincWindow,rAB,rBC,rAC,lT,rtm,yy,mm,jj,t_EXT,t_W,n,rA,rB,rC,hh,mi,ss,HardW,SerNum,FirmW,FPGA,ThsA,ThsB,ThsC = rtd.readLabZyfile(inputs["path_ntd_src"],1)
            _, _, _, shortCoincWindow, _ =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,shortCoincWindow,rT,t_W)

            rT,rD,rAB,rBC,rAC,lT,rtm,yy,mm,jj,t_EXT,t_W,n,rA,rB,rC,hh,mi,ss,HardW,SerNum,FirmW,FPGA,ThsA,ThsB,ThsC = rtd.readLabZyfile(inputs["path_ntd_src"],inputs["dsp_params"])
            # Correct for accidental coincidences
            _, _, _, Di, Ti =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,rD,rT,t_W)
            measdate = dt.datetime(int(yy),int(mm),int(jj),int(hh),int(mi)) # measurement date (Y,M,D,h,m,s)
            accCorr=np.mean(Di/rD-1)*100 # accidental coincidences correction in percent
            measTime = rtm*len(rD)

            u_relative_deadtime = np.abs(np.mean(longDeadTime) - np.mean(shortDeadTime))/(np.mean(rD)*np.sqrt(12)) # relative uncertainty on dead time parameter
            u_relative_coincwindow = np.abs(np.mean(longCoincWindow) - np.mean(shortCoincWindow))/(np.mean(rD)*np.sqrt(12)) # relative uncertainty on coincidence window parameter


        if inputs["daq"] == "DT5751":
            print("Can takes time to read large DT5751 files...")
            # Extract TDCR background measurements
            #pathCSV = "U:\Radionuclides\ESIR\DT5751\DAQ\???\RAW\???.csv"
            #rA,rB,rC,rAB,rBC,rAC,_,rD,rT,lT,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = rtd.readDT5751(pathCSV, thres, baseTime, sumWindow, t_mes, t_W, t_EXT, recordLen)
            # Correct for accidental coincidences
            #_ , _, _, D0i, _ =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,rD,rT,t_W)    
            #D0 = np.mean(D0i) # background count rate (s-1)
            #uD0 = np.std(D0i)/np.sqrt(len(rD)) # standard uncertainty on the background count rate (s-1)
            D0 = 0.0 # set background to zero for DT5751 measurements
            uD0 = 0.0 # set background uncertainty to zero for DT5751 measurements
            T0 = 0.0 # set background to zero for DT5751 measurements
            uT0 = 0.0 # set background uncertainty to zero for DT5751 measurements
            
            # Extract TDCR source measurements
            pathCSV = "U:\Radionuclides\ESIR\DT5751\DAQ\Ho166m_DT5751_UG0_D00\RAW\SDataR_Ho166m_DT5751_UG0_D00.csv"
            measdate = dt.datetime(2025,9,25,15,40,25)  # copy by hand from info file

            # uncertainty on dsp parameters
            rA,rB,rC,rAB,rBC,rAC,_,shortDeadTime,rT,lT,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = rtd.readDT5751(pathCSV, thres, baseTime, sumWindow, measTime/n_run, t_W, t_EXTmin, 0)
            _, _, _, shortDeadTime, _ =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,shortDeadTime,rT,t_W)
            rA,rB,rC,rAB,rBC,rAC,_,longDeadTime,rT,lT,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = rtd.readDT5751(pathCSV, thres, baseTime, sumWindow, measTime/n_run, t_W, t_EXTmax, 0)
            _, _, _, longDeadTime, _ =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,longDeadTime,rT,t_W)
            rA,rB,rC,rAB,rBC,rAC,_,longCoincWindow,rT,lT,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = rtd.readDT5751(pathCSV, thres, baseTime, sumWindow, measTime/n_run, t_Wmax, t_EXT, 0)
            _, _, _, longCoincWindow, _ =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,longCoincWindow,rT,t_Wmax)
            rA,rB,rC,rAB,rBC,rAC,_,shortCoincWindow,rT,lT,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = rtd.readDT5751(pathCSV, thres, baseTime, sumWindow, measTime/n_run, t_Wmin, t_EXT, 0)
            _, _, _, shortCoincWindow, _ =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,shortCoincWindow,rT,t_Wmin)

            rA,rB,rC,rAB,rBC,rAC,_,rD,rT,lT,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = rtd.readDT5751(pathCSV, thres, baseTime, sumWindow, measTime/n_run, t_W, t_EXT, recordLen)
            # Correct for accidental coincidences
            _, _, _, Di, Ti =rtd.accidentalCoincCorr(rA,rB,rC,rAB,rBC,rAC,rD,rT,t_W)
            accCorr=np.mean(Di/rD-1)*100 # accidental coincidences correction in percent

            u_relative_deadtime = np.abs(np.mean(longDeadTime) - np.mean(shortDeadTime))/(np.mean(rD)*np.sqrt(12)) # relative uncertainty on dead time parameter
            u_relative_coincwindow = np.abs(np.mean(longCoincWindow) - np.mean(shortCoincWindow))/(np.mean(rD)*np.sqrt(12)) # relative uncertainty on coincidence window parameter



        A = np.mean(rA)
        uA = np.std(rA)/len(rA)
        B = np.mean(rB)
        uB = np.std(rB)/len(rB)
        C = np.mean(rC)
        uC = np.std(rC)/len(rC)
        AB = np.mean(rAB)
        uAB = np.std(rAB)/len(rAB)
        BC = np.mean(rBC)
        uBC = np.std(rBC)/len(rBC)
        AC = np.mean(rAC)
        uAC = np.std(rAC)/len(rAC)
        T = np.mean(Ti) # average triple coincidence rate (s-1)
        uT = np.std(Ti)/len(Ti) # standard deviation of triple coincidence rate (Type A)
        D = np.mean(Di) # average double coincidence rate (s-1)
        uD = np.std(Di)/len(Di) # standard deviation of double coincidence rate (Type A)
        covTD = np.mean((Ti-T)*(Di-D)) # covariance between T and D
        TD = np.mean(np.asarray(Ti)/np.asarray(Di)) # mean TDCR
        # uTD = np.sqrt( uT**2/D**2 + T**2*uD*2/D**4 -2*T*uT*covTD/D**3 ) # standard deviation of TDCR with covariance term
        uTD = np.sqrt( uT**2/D**2 + T**2*uD*2/D**4) # standard deviation of TDCR without covariance term

        Dnet = D - D0 # background correction on double coincidence rate
        Tnet = T - T0 # background correction on triple coincidence rate

        uDnet = np.sqrt(uD**2 + uD0**2) # combined standard uncertainty on background corrected double coincidence rate
        uTnet = np.sqrt(uT**2 + uT0**2) # combined standard uncertainty on background corrected triple coincidence rate

        measDeadTime = 100*(1-np.mean(lT)/rtm) # measurement dead time in percent

        print("Acc corr = ", accCorr)
        print("T = ", T, " +/- ", uT)
        print("D = ", D, " +/-", uD)
        print("D - D0 = ", Dnet, " +/-", uDnet)
        print("T - T0 = ", Tnet, " +/-", uTnet)
        print("u(T,D) = ", covTD)
        print("TD = ", TD, " +/- ", uTD)
        print("measurement dead time = ",measDeadTime, " %")



        print(inputs["ref_date"], type(inputs["ref_date"]))

        Delta_t = measdate-inputs["ref_date"]             # cooling time
        Delta_t = Delta_t.total_seconds()      # convert to timedelta
        Q = np.exp(np.log(2)*Delta_t/(inputs["t05"]))   # decay correction from the reference date to the measurement date
        uQ = Q*np.log(2)*inputs["ut05"]*Delta_t/(inputs["t05"]**2) # uncertainty on decay correction
        k = -measTime*np.log(2)/(inputs["t05"]*(np.exp(-measTime*np.log(2)/inputs["t05"])-1)) # decay during measurement correction
        uk = np.abs((inputs["ut05"]/inputs["t05"])*(k**2*np.exp(-measTime*np.log(2)/inputs["t05"])-k)) # uncertainty on decay during measurement correction

        print("REF DATE = ", inputs["ref_date"])
        print("MEAS DATE = ", measdate)
        print("T05 = ", inputs["t05"], "+/-", inputs["ut05"], " days")
        print("meas time = ", measTime, " s")
        print("Dt = ", Delta_t, " s")
        print("Q = ", Q, "+/-", uQ)
        print("k = ", k, "+/-", uk)


        #print("TDCRPy version = ", importlib.metadata.version("TDCRPy"))
        print("kB = ", inputs["kb"], " cm/keV")
        if inputs["ls_cocktail"] == "Water":
            modelS = False # model stochastic not working for pure water
            modelA = True # model analytic working for pure beta emitters in pure water
            cerenkov = True

        if modelS:
            print("\nModel stochastic\n")
            td.TDCR_model_lib.modifyTau(int(t_W))
            td.TDCR_model_lib.modifyDeadTime(int(t_EXT))
            td.TDCR_model_lib.modifyMeasTime(int(rtm*60))
            td.TDCR_model_lib.modifyEffQ(str(inputs["quantum_efficiency_pmta"])+","+str(inputs["quantum_efficiency_pmtb"])+","+str(inputs["quantum_efficiency_pmtc"]))
            td.TDCR_model_lib.modifySolvantType(inputs["solvant"])
            td.TDCR_model_lib.modifySolvantConc(inputs["solvant_conc"])
            td.TDCR_model_lib.modifyLScocktail(inputs["ls_cocktail"], inputs["frac_aq"], solvantType=inputs["solvant"], solvantConc=inputs["solvant_conc"])
            print(" ")
            result = td.TDCRPy.eff(TD, inputs["rad"], "1", inputs["kb"], inputs["total_source_vol_ml"], N, Lbounds=(0.01, 20))
            freeP_S = result[0]
            eff_S = result[4]
            u_eff_S = result[5]
            print("efficiency D = ", eff_S, "+/-", u_eff_S, " (statisitical component only)")
            reskBmin = td.TDCRPy.eff(TD, inputs["rad"], "1", inputs["kbmin"], inputs["total_source_vol_ml"], N, Lbounds=(0.01, 20))
            reskBmax = td.TDCRPy.eff(TD, inputs["rad"], "1", inputs["kbmax"], inputs["total_source_vol_ml"], N, Lbounds=(0.01, 20))
            u_eff_kB_S = np.abs(reskBmax[4]-reskBmin[4])/(np.sqrt(12)) # uncertainty on efficiency due to kB
            print("uncertainty on efficiency D due to kB = ", u_eff_kB_S)
        if modelA:
            print("\nModel deterministic")
            if inputs["ls_cocktail"] == "Water":
                result = td.TDCRPy.effA(TD, inputs["rad"], "1", inputs["kb"], inputs["total_source_vol_ml"],cerenkov=True, Lbounds=[0.01, 10])
            else:
                result = td.TDCRPy.effA(TD, inputs["rad"], "1", inputs["kb"], inputs["total_source_vol_ml"], Lbounds=[0.01, 10])
            freeP_A = result[0]
            eff_A = result[3]
            u_eff_A = 0
            print("efficiency D = ", eff_A, "+/-", u_eff_A, " (statisitical component only)")
            if inputs["ls_cocktail"] == "Water":
                reskBmin = td.TDCRPy.effA(TD, inputs["rad"], "1", inputs["kbmin"], inputs["total_source_vol_ml"],cerenkov=True, Lbounds=[0.01, 10])
                reskBmax = td.TDCRPy.effA(TD, inputs["rad"], "1", inputs["kbmax"], inputs["total_source_vol_ml"],cerenkov=True, Lbounds=[0.01, 10])
            else:
                reskBmin = td.TDCRPy.effA(TD, inputs["rad"], "1", inputs["kbmin"], inputs["total_source_vol_ml"], Lbounds=[0.01, 10])
                reskBmax = td.TDCRPy.effA(TD, inputs["rad"], "1", inputs["kbmax"], inputs["total_source_vol_ml"], Lbounds=[0.01, 10])
            u_eff_kB_A = np.abs(reskBmax[3]-reskBmin[3])/(np.sqrt(12)) # uncertainty on efficiency due to kB
            print("uncertainty on efficiency D due to kB = ", u_eff_kB_A)


        modelParams = td.TDCR_model_lib.readParameters(disp=True)
        nE_electron = modelParams[0]
        nE_alpha = modelParams[1]
        rho = modelParams[2]
        effective_charge_number = modelParams[3]
        effective_mass_number = modelParams[4]
        diam_micelle = modelParams[8]
        print(modelParams[9]==inputs["frac_aq"])
        print(modelParams[10]==t_W)
        print(modelParams[11]==t_EXT)
        print(modelParams[12]==int(rtm*60))
        micCorr = modelParams[13]
        effQuantic = modelParams[14]
        frac_H_atom = modelParams[18]
        frac_C_atom = modelParams[19]
        frac_N_atom = modelParams[20]
        frac_O_atom = modelParams[21]
        frac_P_atom = modelParams[22]
        frac_S_atom = modelParams[23]
        frac_Na_atom = modelParams[24]
        frac_Cl_atom = modelParams[25]
        print(modelParams[26]==inputs["solvant"])
        print(modelParams[27]==inputs["solvant_conc"])


        u_relative_countingStat = uDnet/Dnet
        u_relative_decay_correction = np.sqrt( (uQ/Q)**2 + (uk/k)**2 )
        if modelS:
            u_relative_efficiency_stat = np.mean(np.asarray(u_eff_S)/np.asarray(eff_S))
            u_relative_efficiency_kB_S = u_eff_kB_S/(np.mean(np.asarray(eff_S)))
        if modelA:
            u_relative_efficiency_kB_A = u_eff_kB_A/(np.mean(np.asarray(eff_A)))
        u_relative_mass = inputs["u_mass_g"]/inputs["mass_g"]

        print("\nRelative counting statistics uncertainty = \t", round(u_relative_countingStat*100,5), " %")
        print("Relative decay correction uncertainty = \t", round(u_relative_decay_correction*100,5), " %")
        if modelS:
            print("Relative efficiency statistical uncertainty = \t", round(u_relative_efficiency_stat*100,5), " %")
            print("Relative efficiency kB uncertainty = \t\t", round(u_relative_efficiency_kB_S*100,5), " %", "(model stochastic)")
        if modelA:
            print("Relative efficiency kB uncertainty = \t\t", round(u_relative_efficiency_kB_A*100,5), " %", "(model analytic)")
        print("Relative mass uncertainty = \t\t\t", round(u_relative_mass*100,5), " %")
        print("Relative dead time uncertainty = \t\t", round(u_relative_deadtime*100,5), " %")
        print("Relative coincidence window uncertainty = \t", round(u_relative_coincwindow*100,5), " %")

        if modelS:
            u_relative_combined_S = np.sqrt( 
            u_relative_countingStat**2
            + u_relative_decay_correction**2
            + u_relative_efficiency_stat**2 
            + u_relative_efficiency_kB_S**2
            + u_relative_deadtime**2
            + u_relative_coincwindow**2)
            print("\nCombined relative uncertainty for activity(model stochastic) = \t", round(u_relative_combined_S*100,5), " %")
            u_relative_combined_massA_S = np.sqrt( 
            u_relative_countingStat**2
            + u_relative_decay_correction**2
            + u_relative_efficiency_stat**2 
            + u_relative_efficiency_kB_S**2 
            + u_relative_mass**2
            + u_relative_deadtime**2
            + u_relative_coincwindow**2)
            print("\nCombined relative uncertainty for mass activity (model stochastic) = \t", round(u_relative_combined_massA_S*100,5), " %")

        if modelA:
            u_relative_combined_A = np.sqrt( 
            u_relative_countingStat**2
            + u_relative_decay_correction**2
            + u_relative_efficiency_kB_A**2 
            + u_relative_deadtime**2
            + u_relative_coincwindow**2)
            print("\nCombined relative uncertainty for activity (model analytic) = \t", round(u_relative_combined_A*100,5), " %")
            u_relative_combined_massA_A = np.sqrt( 
            u_relative_countingStat**2
            + u_relative_decay_correction**2
            + u_relative_efficiency_kB_A**2 
            + u_relative_mass**2
            + u_relative_deadtime**2
            + u_relative_coincwindow**2)
            print("\nCombined relative uncertainty for mass activity (model analytic) = \t", round(u_relative_combined_massA_A*100,5), " %")

        print("ext DTC = ", t_EXT, " µs")
        print("resolution time = ", t_W, " ns")
        print("Birks constant kB = ", inputs["kb"], " cm/keV")
        print("m = ", inputs["mass_g"], "+/-", inputs["u_mass_g"], " g")

        if modelS:
            mass_activity_S = 1e-3*(Dnet)*Q*k/(eff_S*inputs["mass_g"])
            u_mass_activity_S = mass_activity_S * u_relative_combined_massA_S
            activity_S = 1e-3*(Dnet)*Q*k/(eff_S)
            u_activity_S = activity_S * u_relative_combined_S
            print("\nModel stochastic")
            print("mass activity = ", round(mass_activity_S,2), "+/-", round(u_mass_activity_S,2), "kBq/g")
            print("activity = ", round(activity_S,2), "+/-", round(u_activity_S,2), "kBq")
        if modelA:
            mass_activity_A = 1e-3*(Dnet)*Q*k/(eff_A*inputs["mass_g"])
            u_mass_activity_A = mass_activity_A * u_relative_combined_massA_A
            activity_A = 1e-3*(Dnet)*Q*k/(eff_A)
            u_activity_A = activity_A * u_relative_combined_A
            print("\nModel analytic")
            print("mass activity = ", round(mass_activity_A,2), "+/-", round(u_mass_activity_A,2), "kBq/g")
            print("activity = ", round(activity_A,2), "+/-", round(u_activity_A,2), "kBq")



        # Define the output filename based on Nuclide and Measurement Date
        # Uses 'measdate' if available, otherwise defaults to current time
        try:
            date_str = measdate.strftime('%Y%m%d_%H%M%S')
        except NameError:
            date_str = dt.datetime.now().strftime('%Y%m%d_%H%M%S')

        if inputs["daq"]=="nanoTDCR": output_filename = f"results\{inputs["rad"]}\TDCR_Results_{inputs["rad"]}_{inputs["laboratory"]}_{inputs["year"]}_{inputs["source_name"]}_{inputs["grey_filter_nd"]}_{inputs["daq"]}_{int(t_EXT)}_{int(t_W)}_{int(inputs['kb']*1e6)}.csv"
        #if DAQ=="DT5751": output_filename = f"results\{Rad}\TDCR_Results_{path.replace("\\","-").replace(":","-").replace(".","")}_{t_EXT}_{t_W}.csv"

        # Initialize the data list
        # Structure: [Section, Parameter, Value, Uncertainty, Unit, Description]
        data_rows = []

        def add_entry(section, param, value, unc, unit, desc):
            """Helper to format and add rows safely."""
            try:
                # Format values to string, handling None
                val_str = str(value) if value is not None else ""
                unc_str = str(unc) if unc is not None else ""
                data_rows.append([section, param, val_str, unc_str, unit, desc])
            except Exception as e:
                print(f"Skipping {param}: {e}")

        # --- 1. General & Source Parameters ---
        add_entry("General", "Nuclide", inputs["rad"], None, "-", "Radionuclide name")
        add_entry("General", "Reference Date", inputs["ref_date"], None, "-", "Reference date")
        add_entry("General", "Measurement Date", measdate, None, "-", "Date of measurement")
        add_entry("General", "Half-life (T1/2)", inputs["t05"], inputs["ut05"], "days", "Half-life")
        add_entry("Source", "Laboratory", inputs["laboratory"], None, "-", "Provider of the standard solution")
        add_entry("Source", "Source Name", inputs["source_name"], None, "-", "Name of the source")
        add_entry("Source", "LS Cocktail", inputs["ls_cocktail"], None, "-", "Liquid scintillation cocktail")
        add_entry("Source", "Aqueous Fraction", inputs["frac_aq"], None, "rel", "Aqueous fraction in scintillator")
        add_entry("Source", "Grey Filter ND", inputs["grey_filter_nd"], None, "-", "Neutral density grey filter")
        add_entry("Source", "Diffusive Vial", inputs.get("diffusive_vial", False), None, "-", "Diffusive vial used")
        add_entry("Source", "Solvent", inputs["solvant"], None, "-", "Solvent type")
        add_entry("Source", "Solvent Concentration", inputs["solvant_conc"], None, "mol/L", "Solvent concentration in scintillator")
        add_entry("Source", "Mass", inputs["mass_g"], inputs["u_mass_g"], "g", "Source mass")
        add_entry("Source", "Volume", inputs["total_source_vol_ml"], None, "mL", "Scintillator volume")

        # --- 2. DAQ & Measurement Settings ---
        add_entry("DAQ", "Device", inputs["daq"], None, "-", "DAQ Device Name")
        add_entry("DAQ", "Measurement Time", measTime, None, "s", "Duration")
        add_entry("DAQ", "Dead Time (Extended)", t_EXT, None, "us", "Extended dead time")
        add_entry("DAQ", "Coincidence Window", t_W, None, "ns", "Coincidence window")

        # --- 3. Intermediate Results (Count Rates) ---
        add_entry("Rates", "Singles Raw (A)", A, uA, "s-1", "Raw singles count rate (A)")
        add_entry("Rates", "Singles Raw (B)", B, uB, "s-1", "Raw singles count rate (B)")
        add_entry("Rates", "Singles Raw (C)", C, uC, "s-1", "Raw singles count rate (C)")
        add_entry("Rates", "Doubles Raw (AB)", AB, uAB, "s-1", "Raw doubles count rate (AB)")
        add_entry("Rates", "Doubles Raw (BC)", BC, uBC, "s-1", "Raw doubles count rate (BC)")
        add_entry("Rates", "Doubles Raw (AC)", AC, uAC, "s-1", "Raw doubles count rate (AC)")
        add_entry("Rates", "Doubles Raw (D)", D, uD, "s-1", "Raw doubles count rate")
        add_entry("Rates", "Triples Raw (T)", T, uT, "s-1", "Raw triples count rate")
        add_entry("Rates", "Doubles Net (D-D0)", Dnet, uDnet, "s-1", "Background corrected doubles")
        add_entry("Rates", "Triples Net (T-T0)", Tnet, uTnet, "s-1", "Background corrected triples")
        add_entry("Rates", "TDCR", TD, uTD, "-", "Triple to Double Coincidence Ratio")
        add_entry("Rates", "Accidental Corr.", accCorr, None, "%", "Accidental coincidence correction")
        add_entry("Rates", "Measurement Dead Time", measDeadTime, None, "%", "Measurement dead time")

        # --- 4. Corrections ---
        add_entry("Corrections", "Decay Factor (Q)", Q, uQ, "-", "Decay correction to ref date")
        add_entry("Corrections", "Decay During Meas (k)", k, uk, "-", "Decay during measurement correction")

        # --- 5. Uncertainty Budget (Relative) ---
        # We convert these to percentages for readability in the description or keep as fraction
        add_entry("Uncertainty Budget", "u_rel Counting Stat", u_relative_countingStat, None, "rel", "Relative counting statistics unc.")
        add_entry("Uncertainty Budget", "u_rel Decay Corr", u_relative_decay_correction, None, "rel", "Relative decay correction unc.")
        add_entry("Uncertainty Budget", "u_rel Mass", u_relative_mass, None, "rel", "Relative mass unc.")
        add_entry("Uncertainty Budget", "u_rel Dead Time", u_relative_deadtime, None, "rel", "Relative dead time unc.")
        add_entry("Uncertainty Budget", "u_rel Coinc Window", u_relative_coincwindow, None, "rel", "Relative coincidence window unc.")

        # --- 6. Stochastic Model Results ---
        if 'modelS' in locals() and modelS:
            add_entry("Model Stochastic", "version", version, None, "-", "Version of TDCRPy")
            add_entry("Model Stochastic", "rho", rho, None, "g/mL", "Scintillator density")
            add_entry("Model Stochastic", "Effective Z", effective_charge_number, None, "-", "Effective charge number")
            add_entry("Model Stochastic", "Effective A", effective_mass_number, None, "-", "Effective mass number")
            add_entry("Model Stochastic", "Micelle correction", micCorr, None, "-", "Micelle correction factor")
            add_entry("Model Stochastic", "Micelle diameter", diam_micelle, None, "nm", "Micelle diameter")
            add_entry("Model Stochastic", "Aqueous fraction", inputs["frac_aq"], None, "-", "Aqueous fraction")
            add_entry("Model Stochastic", "Fraction H atom", frac_H_atom, None, "rel", "Fraction of H atoms in scintillator")
            add_entry("Model Stochastic", "Fraction C atom", frac_C_atom, None, "rel", "Fraction of C atoms in scintillator")
            add_entry("Model Stochastic", "Fraction N atom", frac_N_atom, None, "rel", "Fraction of N atoms in scintillator")
            add_entry("Model Stochastic", "Fraction O atom", frac_O_atom, None, "rel", "Fraction of O atoms in scintillator")
            add_entry("Model Stochastic", "Fraction P atom", frac_P_atom, None, "rel", "Fraction of P atoms in scintillator")
            add_entry("Model Stochastic", "Fraction S atom", frac_S_atom, None, "rel", "Fraction of S atoms in scintillator")
            add_entry("Model Stochastic", "Fraction Na atom", frac_Na_atom, None, "rel", "Fraction of Na atoms in scintillator")
            add_entry("Model Stochastic", "Fraction Cl atom", frac_Cl_atom, None, "rel", "Fraction of Cl atoms in scintillator")
            add_entry("Model Stochastic", "Quantum efficiency pmt A", inputs["quantum_efficiency_pmta"], None, "-", "Photomultiplier A quantum efficiency")
            add_entry("Model Stochastic", "Quantum efficiency pmt B", inputs["quantum_efficiency_pmtb"], None, "-", "Photomultiplier B quantum efficiency")
            add_entry("Model Stochastic", "Quantum efficiency pmt C", inputs["quantum_efficiency_pmtc"], None, "-", "Photomultiplier C quantum efficiency")
            add_entry("Model Stochastic", "Birks Constant (kB)", inputs["kb"], None, "cm/keV", "Birks constant")
            add_entry("Model Stochastic", "MC trials", N, None, "-", "Number of Monte Carlo trails")
            add_entry("Model Stochastic", "Free parameter", freeP_S, None, "keV-1", "Free parameter (the light yield)")
            add_entry("Model Stochastic", "Efficiency", eff_S, u_eff_S, "-", "Detection efficiency (Stochastic)")
            add_entry("Model Stochastic", "u_rel Efficiency kB", u_relative_efficiency_kB_S, None, "rel", "Relative eff. unc. due to kB")
            add_entry("Model Stochastic", "Activity Conc.", mass_activity_S, u_mass_activity_S, "kBq/g", "Activity concentration")
            add_entry("Model Stochastic", "Combined Rel. Unc. Activity Conc.", u_relative_combined_massA_S, None, "rel", "Combined relative uncertainty for activity concentration")
            add_entry("Model Stochastic", "Activity", activity_S, u_activity_S, "kBq", "Activity")
            add_entry("Model Stochastic", "Combined Rel. Unc. Activity", u_relative_combined_S, None, "rel", "Combined relative uncertainty for activity")

        # --- 7. Analytic Model Results ---
        if 'modelA' in locals() and modelA:
            add_entry("Model Analytic", "version", version, None, "-", "Version of TDCRPy")
            add_entry("Model Analytic", "rho", rho, None, "g/mL", "Scintillator density")
            add_entry("Model Analytic", "Effective Z", effective_charge_number, None, "-", "Effective charge number")
            add_entry("Model Analytic", "Effective A", effective_mass_number, None, "-", "Effective mass number")
            add_entry("Model Analytic", "Energy binning electron", nE_electron, None, "-", "energy binning the quenching function of electrons")
            add_entry("Model Analytic", "Energy binning alpha", nE_alpha, None, "-", "energy binning the quenching function of alphas")
            add_entry("Model Analytic", "Birks Constant (kB)", inputs["kb"], None, "cm/keV", "Birks constant")
            add_entry("Model Analytic", "Free parameter", freeP_A, None, "keV-1", "Free parameter (the photoelectron yield)")
            add_entry("Model Analytic", "Efficiency", eff_A, u_eff_A, "-", "Detection efficiency (Analytic)")
            add_entry("Model Analytic", "u_rel Efficiency kB", u_relative_efficiency_kB_A, None, "rel", "Relative eff. unc. due to kB")
            add_entry("Model Analytic", "Activity Conc.", mass_activity_A, u_mass_activity_A, "kBq/g", "Activity concentration")
            add_entry("Model Analytic", "Combined Rel. Unc. Activity Conc.", u_relative_combined_massA_A, None, "rel", "Combined relative uncertainty for activity concentration")
            add_entry("Model Analytic", "Activity", activity_A, u_activity_A, "kBq", "Activity")
            add_entry("Model Analytic", "Combined Rel. Unc. Activity", u_relative_combined_A, None, "rel", "Combined relative uncertainty for activity")


        # --- Write to CSV ---
        header = ["Section", "Parameter", "Value", "Uncertainty", "Unit", "Description"]

        try:
            with open(output_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(header)
                writer.writerows(data_rows)
            print(f"File successfully created: {os.path.abspath(output_filename)}")
            
            # Optional: Display top of file to user
            print("\nPreview of CSV content:")
            for row in data_rows[:5]:
                print(row)
                
        except IOError as e:
            print(f"Error writing file: {e}")

        # back to the default value
        td.TDCR_model_lib.resetConfFile()