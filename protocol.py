from neuron import h
import random as rnd
import numpy as np

class stim_protocol():
    
    def __init__(self,
                 cell,
                 p,
                 rank = 0):

        # Add parameters to protocol
        self.p = p
        self.seed = 123881
        rnd.seed(self.seed)
        # Start protocol
        self.stimulators = {}

        # Initial time lag
        start_next = 0

        # Stabilization of membrane potential
        start_next += 0

        # pre induction EPSP Test 
        self.test_pre = h.NetStim()
        self.test_pre.start = start_next # start_next # ms
        self.test_pre.interval = 1e3/self.p['test_freq'] # ms -> 20 sec
        self.test_pre.number = int(self.p['time_on_initialization'] / self.test_pre.interval) # 200
        self.test_pre.noise = 0
        if p['check']:
            print('Begin sim',start_next)
        
        self.nc_test_pre = []
        self.nc_test_pre_nmda = []
        for spine in cell.spines:
            self.nc_test_pre.append(h.NetCon(self.test_pre, spine.head.AMPA,0,0,1))
            self.nc_test_pre_nmda.append(h.NetCon(self.test_pre, spine.head.NMDA,0,0,1))
        self.stimulators['test_pre_spike_times'] = h.Vector()
        self.nc_test_pre[-1].record(self.stimulators['test_pre_spike_times'])

        start_next += self.p['time_on_initialization']
        if p['check']:
            print('End PRE',start_next)
        

        # Induction protocol
        self.stim = h.NetStim()
        start_next += self.p['time_to_begin_induction']
        self.stim.start = start_next # ms
        self.p['time_start_induction_stimuli'] = self.stim.start
        self.stim.number = self.p['nstim'] # 200
        self.stim.interval = 1e3/self.p['induction_freq'] # ms  0.5 Hz = 2 s
        self.stim.noise = 0
        if p['check']:
            print('Begin induction',start_next)
        

        self.nc_stim = []
        self.nc_stim_nmda = []
        synaptic_delays = np.linspace(0,p['sp_delay_env'],len(cell.spines))
        for spine,delay in zip(cell.spines,synaptic_delays):
            spine.delay = delay #rnd.uniform(0,p['sp_delay_env'])
            self.nc_stim.append(h.NetCon(self.stim, spine.head.AMPA,0,spine.delay,1))
            self.nc_stim_nmda.append(h.NetCon(self.stim, spine.head.NMDA,0,spine.delay,1))
        self.stimulators['induction_spikes'] = h.Vector()
        self.nc_stim[-1].record(self.stimulators['induction_spikes'])

        # during induction EPSP Test 
        self.test_during = h.NetStim()
        self.test_during.start = start_next + 1e3/self.p['induction_freq']/2 # ms
        if p['check']:
            print("DURING",self.test_during.start, 1e3/self.p['induction_freq']/2)
        self.test_during.interval = 1e3/self.p['test_freq'] # ms -> 20 sec
        self.test_during.number = int(self.stim.number*self.stim.interval / self.test_during.interval)
        self.test_during.noise = 0

        self.nc_test_during = []
        self.nc_test_during_nmda = []
        for spine in cell.spines:
            self.nc_test_during.append(h.NetCon(self.test_during, spine.head.AMPA,0,0,1))
            self.nc_test_during_nmda.append(h.NetCon(self.test_during, spine.head.NMDA,0,0,1))
        self.stimulators['test_during_spike_times'] = h.Vector()
        self.nc_test_during[-1].record(self.stimulators['test_during_spike_times'])

        # BPAP self.stimulation    
        IC_dep = self.stimulators['IC_dep'] = []
        IC_hyp = self.stimulators['IC_hyp'] = []
        IC_delays = self.stimulators['IC_delays'] = []
        for s in range(self.p['nstim']):
            IC_dep.append([])
            IC_hyp.append([])
            IC_delays.append(start_next + self.stim.interval * s - p['IC_delay_to_spike'])
            for ap in range(4):
                IC_dep[-1].append(h.IClamp(0.5, sec = cell.cell.soma))
                IC_hyp[-1].append(h.IClamp(0.5, sec = cell.cell.soma))
                IC_dep[-1][ap].amp = p['BPAP_stimulus_amplitude'] # nA
                IC_dep[-1][ap].delay =  IC_delays[-1] + ap*5# ms
                IC_dep[-1][ap].dur = p['BPAP_dep_stimulus_duration'] # ms

                IC_hyp[-1][ap].amp = -0.02 # nA
                IC_hyp[-1][ap].delay = IC_dep[-1][ap].delay + IC_dep[-1][ap].dur # ms
                IC_hyp[-1][ap].dur = p['BPAP_hyp_stimulus_duration'] # ms
            # self.stimulators['IC_dep'].append(h.IClamp(0.5, sec = cell.cell.branch_base))
            # self.stimulators['IC_hyp'].append(h.IClamp(0.5, sec = cell.cell.branch_base))
            # self.stimulators['IC_dep'][-1].amp = self.p['BPAP_stimulus_ampitude'] # nA
            # self.stimulators['IC_dep'][-1].delay = start_next + self.stim.interval * s - self.p['IC_delay_to_spike'] # ms
            # self.stimulators['IC_delays'].append(self.stimulators['IC_dep'][-1].delay)
            # self.stimulators['IC_dep'][-1].dur = self.p['BPAP_dep_stimulus_duration'] # ms

            # self.stimulators['IC_hyp'][-1].amp = -0.02 # nA
            # self.stimulators['IC_hyp'][-1].delay = self.stimulators['IC_dep'][-1].delay + self.stimulators['IC_dep'][-1].dur # ms
            # self.stimulators['IC_hyp'][-1].dur = self.p['BPAP_hyp_stimulus_duration'] # ms


        self.time_of_induction = self.p['nstim'] * self.stim.interval
        start_next += self.time_of_induction
        self.time_end_induction = start_next
        if p['check']:
            print('End induction',start_next)

        # Post induction EPSP test during expression
        self.test_post = h.NetStim()
        start_next += self.p['time_after_induction']
        self.test_post.start = start_next  # ms
        self.test_post.number = 1e4 
        self.test_post.interval = 1e3/self.p['test_freq'] # ms = 0.05 Hz = 20 sec
        self.test_post.noise = 0

        self.nc_test_post = []
        self.nc_test_post_nmda = []
        for spine in cell.spines:
            self.nc_test_post.append(h.NetCon(self.test_post, spine.head.AMPA,0,0,1))
            self.nc_test_post_nmda.append(h.NetCon(self.test_post, spine.head.NMDA,0,0,1))
        start_next += self.p['time_of_expression'] #ms
        self.stimulators['test_post_spike_times'] = h.Vector()
        self.nc_test_post[-1].record(self.stimulators['test_post_spike_times'])

        # cell.spines[0].head.plot('cai')
        # dend.plot('v')
        # # h('load_file("Tests/Test_ampa.ses")')
        # # h('load_file("Tests/Test_ampa_30min.ses")')

        # Remve the induction self.stimulus
        if self.p['activate_LTP_protocol']:
            self.stim.number = self.p['nstim']
        else:
            self.stim.number = 0

        ##### Initialization ########
        h.v_init = self.p['Vrest'] # mV
        self.p['tstop'] = start_next
        h.init()
        if p['check']:
            print('Setup finished on cpu %g tstop %g'%(rank,h.tstop))


