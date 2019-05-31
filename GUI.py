import random as rnd
from neuron import h
from neuron import gui
h.load_file('nrngui.hoc')
import copy as cp
import numpy as np

class Panels(object):
    def __init__(self,branch,protocol,plots):
        self.spines = branch.spines
        self.cell = branch.cell
        self.plots = plots
        self.tau_rm = self.spines[0].head.RMECB.tau_RM
        self.alpha_RMru = self.spines[0].head.RMECB.alpha_RMru
        self.blk_RMBLK = protocol.p['Block_RMBLK']
        self.protocol = protocol
        self.dur = protocol.stimulators['IC_dep'][0][0].dur
        self.dep = protocol.stimulators['IC_dep']
        self.hyp = protocol.stimulators['IC_hyp']
        self.stim = protocol.stim
        self.start_base = protocol.p['time_start_induction_stimuli']
        self.delta_t = 5 #-(self.stim.start - self.start_base)
        self.neck_diam = self.spines[0].neck.diam
        self.AMPA_Pmax = self.spines[0].head.AMPA.Pmax
        self.AMPA_Prel = self.spines[0].head.AMPA.U_SE_init
        self.AMPA_NMDA_ratio = self.spines[0].head.NMDA.Pmax/self.spines[0].head.AMPA.Pmax
        self.NMDA_Pmax = self.spines[0].head.NMDA.Pmax
        self.NMDA_mg = self.spines[0].head.NMDA.mg
        self.NMDA_mgbk = self.spines[0].head.NMDA.mgb_k
        self.KMULT = h.KMULT
        self.KMULTP = h.KMULTP
        self.nBPAP = len(protocol.stimulators['IC_dep'][0])
        self.nstim = 25 #len(protocol.stimulators['IC_dep'])
        self.sp_delay_env = protocol.p['sp_delay_env']
        self.old_sp_delay_env = cp.deepcopy(protocol.p['sp_delay_env'])
        self.gbar_cat = protocol.p['gcatbar']
        self.clamp_dur = 120
        self.clamp_V = -20
        self.build()
        self.map()

    def build(self):
        self.box = h.HBox()
        self.box.intercept(1)
        self.box.ref(self)
        h.xpanel("")
        h.xbutton("View = Plot", self.set_view) 
        h.xbutton("Set to run short sim", self.run_short) 
        h.xbutton("Set to run long sim", self.run_long) 
        h.xbutton("LTP11", self.set_LTP11) 
        h.xbutton("LTP12", self.set_LTP12) 
        h.xbutton("LTP14", self.set_LTP14)
        h.xbutton("SEClamp",self.set_seclamp)
        h.xbutton("SEClamp del",self.del_seclamp)
        h.xstatebutton("Block RMBLK",(self,'blk_RMBLK'),self.set_spines)
        h.xvalue("Pulse duration (ms)", (self, "dur"), 1, self.set_pulse)
        h.xvalue("Delta_t = t_post - t_pre (ms)", (self, "delta_t"), 1, self.set_stim_start)
        h.xvalue("Spine neck diam (um)", (self, "neck_diam"), 1, self.set_spines)
        h.xvalue("AMPA permeability (cm/s)", (self, "AMPA_Pmax"), 1, self.set_spines)
        h.xvalue("Glutammate Prel", (self, "AMPA_Prel"), 1, self.set_spines)
        h.xvalue("AMPA NMDA ratio", (self, "AMPA_NMDA_ratio"), 1, self.set_spines)
        h.xvalue("NMDA permeability (cm/s)", (self, "NMDA_Pmax"), 1, self.set_spines)
        h.xvalue("NMDA Mg out (mM)", (self, "NMDA_mg"), 1, self.set_spines)
        h.xvalue("NMDA Mg Block slope (/mV)", (self, "NMDA_mgbk"), 1, self.set_spines)
        h.xvalue("BPAB number", (self, "nBPAP"), 1, self.set_pulse)
        h.xvalue("Number of stimuli", (self, "nstim"), 1, self.set_pulse)        
        h.xvalue("KMULT", (self, "KMULT"), 1, self.set_cell)
        h.xvalue("KMULTP", (self, "KMULTP"), 1, self.set_cell)
        h.xvalue("CaT gbar", (self, "gbar_cat"), 1, self.set_spines)
        h.xvalue("Spike envelop delay", (self, "sp_delay_env"), 1, self.set_pulse)
        h.xvalue("RM decay tau (ms)", (self, "tau_rm"), 1, self.set_spines)
        h.xvalue("alpha_RMru (1)", (self, "alpha_RMru"), 1, self.set_spines)
        h.xvalue("Clamp dur", (self, "clamp_dur"), 1, self.set_seclamp)
        h.xvalue("Clamp V", (self, "clamp_V"), 1, self.set_seclamp)
        
        h.xpanel()
        self.box.intercept(0)
        
    def map(self):
        self.box.map("Stimulus control", 0, 378, 329.28, 642.24)

    def set_seclamp(self):
        self.clamp = h.SEClamp(0.5,sec=self.cell.soma)
        self.clamp.dur1 = self.clamp_dur
        self.clamp.amp1 = self.clamp_V
        self.clamp_graph = h.Graph()
        self.clamp_graph.addvar('I_seclamp',self.clamp._ref_i, 1,1,sec=self.cell.soma)
        h.graphList[0].append(self.clamp_graph)

    def del_seclamp(self):
        del self.clamp
        
    def set_LTP11(self):
        h.stoprun = 1
        self.erase()
        h.init()
        self.nBPAP = 1
        self.nstim = 70
        self.set_pulse()
        
    def set_LTP12(self):
        h.stoprun = 1
        self.erase()
        h.init()
        self.nBPAP = 2
        self.nstim = 50
        self.set_pulse()
        
    def set_LTP14(self):
        h.stoprun = 1
        self.erase()
        h.init()
        self.nBPAP = 4
        self.nstim = 25
        self.set_pulse()
        
    def set_spines(self):
        for spine in self.spines:
            spine.head.RMECB.tau_RM = self.tau_rm
            spine.head.RMECB.alpha_RMru = self.alpha_RMru
            spine.neck.diam = self.neck_diam
            spine.head.AMPA.Pmax = self.AMPA_Pmax
            spine.head.AMPA.U_SE_init = self.AMPA_Prel
            if self.AMPA_NMDA_ratio > 0:
                spine.head.NMDA.Pmax = self.AMPA_Pmax * self.AMPA_NMDA_ratio
                self.NMDA_Pmax = spine.head.NMDA.Pmax
            else:
                spine.head.NMDA.Pmax = self.NMDA_Pmax

            spine.head.gcatbar_cat = self.gbar_cat
            spine.head.NMDA.mg = self.NMDA_mg
            spine.head.NMDA.mgb_k = self.NMDA_mgbk

            if self.blk_RMBLK:
                self.alpha_cai_RMBLK_tmp = spine.head.RMECB.alpha_cai_RMBLK
                spine.head.RMECB.alpha_cai_RMBLK = 0
            else:
                spine.head.RMECB.alpha_cai_RMBLK = self.alpha_cai_RMBLK_tmp
                
    def set_stim_start(self):
        self.stim.start = self.start_base - self.delta_t
        print("Delta t =",self.stim.start)
        
    def set_pulse(self):
        # Set curr inj duration
        for dc,hc in zip(self.dep, self.hyp):
            for dc2 in dc:
                dc2.dur = self.dur
        # Set nunmber of curr injections for each induction stim (nBPAPs)
        for dc,hc in zip(self.dep, self.hyp):
            for dc2 in dc[int(self.nBPAP):len(dc)]:
                dc2.dur = 0
            # for hc2 in hc:
            #     hc2.dur = 0
            #     hc2.delay = dc.delay + dc.dur # ms

        # Set nunmber of trains of curr injections, i.e. n induction stimuli
        for nst,(dc,hc) in enumerate(zip(self.dep, self.hyp)):
            if nst > self.nstim:
                for dc2 in dc:
                    dc2.dur = 0
        self.stim.number = self.nstim
        synaptic_delays = np.linspace(0,self.sp_delay_env,len(self.spines))
        for delay,nc,nc_nmda in zip(synaptic_delays,self.protocol.nc_stim,self.protocol.nc_stim_nmda):
            nc.delay = delay
            nc_nmda.delay = delay
            
        print("new dur =", self.dep[0][0].dur)

    def set_cell(self):
        command = 'forall '
        for sec in self.cell.apical_sl:
            
            for seg in sec:
                xdist = h.distance(seg.x)
                if xdist > 100:
                    prev_gkabar_kad = seg.gkabar_kad
                    seg.gkabar_kad = self.KMULT*(1+xdist/100)
                    # print((seg.gkabar_kad -  prev_gkabar_kad) / prev_gkabar_kad)
                else:
                    prev_gkabar_kap = seg.gkabar_kap
                    seg.gkabar_kap = self.KMULTP*(1+xdist/100)

    def set_view(self):
        for plot in self.plots.values():
            plot.exec_menu("View = plot")

    def erase(self):
        for plot in self.plots.values():
            plot.exec_menu("Erase")


    def run_short(self):
        h.stoprun = 1
        self.erase()
        h.tstop = 250

    def run_long(self):
        h.stoprun = 1
        self.erase()
        h.tstop = 1800e3 # runs for 30 min = 1000 ms x 60 s x 30 min = 1.800.000 ms
