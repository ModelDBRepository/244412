# import ipdb
from neuron import h,gui
import struct_tools as st
import numpy as np

class cell(object):

    def __init__(self, Vrest, Rm, Ra, Cm, records=[], check = False, use_channels = True):
        self.Name = 'pyr2005'
        # Load the neuron structure from .swc converted to .hoc geometry
        if use_channels:
            h.load_file('bdnf.hoc')
        else:
            h.load_file('bdnf_passive.hoc')

        models = st.get_cell_list()

        # select the brach apic[93] and insert it in a new sectionlist
        self.soma_sl = h.SectionList()
        self.branch_sl = h.SectionList()
        self.branch37_sl = h.SectionList()
        self.branch8_sl = h.SectionList()
        self.branch16_sl = h.SectionList()
        self.apical_sl = h.SectionList()
        self.basal_sl = h.SectionList()
        self.user5_sl = h.SectionList()
        self.axon_sl = h.SectionList()
        for m in models:
            cell = st.get_section_list(m)
            for sec in cell:
                sec.push()
                if 'apical_dendrite[38]' in sec.name():
                    self.branch_sl.subtree()
                    self.branch_base = sec
                if 'apical_dendrite[37]' in sec.name():
                    self.branch37_sl.subtree()
                    self.branch37_base = sec
                if 'apical_dendrite[8]' in sec.name():
                    self.branch8_sl.subtree()
                    self.branch8_base = sec
                if 'apical_dendrite[16]' in sec.name():
                    self.branch16_sl.subtree()
                    self.branch16_base = sec
                if 'soma' in sec.name():
                    self.soma = sec
                    self.soma_sl.append()
                if 'apical_dendrite' in sec.name():
                    self.apical_sl.append()
                if 'dendrite' in sec.name():
                    self.basal_sl.append()
                if 'user5' in sec.name():
                    self.user5_sl.append()
                h.pop_section()


            if check:
                print('List of kept sections:')
                print(cell.printnames())
                print('Apical',apical_sl.printnames())
                print('Basal',basal_sl.printnames())
                print('Axon',axon_sl.printnames())
                print('User',user5_sl.printnames())

        special_sections = {
            'soma':self.soma,
            'branch_base':self.branch_base}
            
        if check:
            print(self.branch_sl.printnames())

        # Put sections into a dictionary
        self.branch38 = {}
        for sec in self.branch_sl:
            self.branch38[sec.name()] = sec

        self.branch37 = {}
        for sec in self.branch37_sl:
            self.branch37[sec.name()] = sec
        self.branch8 = {}
        for sec in self.branch8_sl:
            self.branch8[sec.name()] = sec
        self.branch16 = {}
        for sec in self.branch16_sl:
            self.branch16[sec.name()] = sec

        # # print self.branch93['apic[95]'].diam

        # # access main branch
        # self.soma.push()
        # self.branch_base = self.branch93['apic[93]']
        # # set origin for distance
        # h.distance(0,0.5)

        # # Adjust the nseg
        # st.geom_nseg(self.branch_sl, check = check)

        # Increase the number of segments to at least 10 per section
        # in the branch to have enough segments for the spines
        for br in [self.branch_sl,self.branch37_sl,self.branch8_sl,self.branch16_sl]:
            for sec in br:
                sec.nseg = max(30,sec.nseg)
            
        # # Set biophysical properties
        # Rm = 26000    # Ohm/cm2
        # print "Imput resistance Rm = ", Rm," Ohm/cm2"
        # Cm = 1.41
        # Ra = 150
        # RaAx = 50

        # self.segments = [['%s_%g'%(sec.name(),seg.x),seg] for sec in self.branch_sl for seg in sec]

        # # The "apic" rad Sectionlists
        # # should insert the following channels
        # apic_channels = ['pas','hd','na3','kdr','kad','kap','cacum','cal','can','cat','cagk']
        # basal_channels = ['hd','na3','kdr','kap','cacum','cal','can','cat','cagk']
        # soma_channels = ['hd','na3','kdr','kap','km','kd','cacum','cal','can','cat','cagk']
        # axon_channels = ['na3','kdr','kap','km']

        # gna = 0.07
        # gkdr = 0.06
        # gkap = 0.0015
        # gkad  =  0.001
        # ghd=5.5e-7

        # gkm=0.0001
        # gkd = 0.0001

        # sh = 5
        # nash = 8
        # kash = 12
        # kdrsh = sh
        # kmsh = 12
        # kdsh = 0
        # hdsh = 0

        # gc = 1.e-5
        # gcal=gc
        # gcan=gc
        # gcat=gc
        # gKc = 3e-05

        # for sec in self.apical_sl:
        #     for ch in channels:
        #         sec.insert(ch)
        #     # sec.tau_cacum = 200
        #     # sec.depth_cacum = sec.diam/2
        #     sec.e_pas = Vrest
        #     sec.g_pas = 1.0/Rm
        #     sec.Ra = Ra
        #     sec.cm = Cm

        #     sec.ghdbar_hd = ghd
        #     sec.vhalfl_hd = -73
        #     sec.sh_hd = hdsh
        #     sec.ehd_hd=-30

        #     sec.gbar_na3=gna
        #     sec.sh_na3=nash
        #     sec.gkdrbar_kdr=gkdr
        #     sec.sh_kdr=kdrsh
        #     sec.gkabar_kap=0

        #     sec.sh_kap=kash	
        #     sec.gkabar_kad=0
        #     sec.sh_kad=kash
        #     sec.gcalbar_cal=gc
        #     sec.gcanbar_can=gc
        #     sec.gcatbar_cat=gc
    	#     sec.gbar_cagk= gKc 


        # Store data
        self.records = {}
        # Time
        self.records['time'] = {'val':h.Vector(),'unit':'ms'}
        self.records['time']['val'].record(h._ref_t, sec = self.branch_base)
        # Spikes
        self.record_spikes()
        # Records set from paramenters.py
        for r in records:
            section = special_sections[r['section']]
            self.records['%s'%r['section']] = {
                '%s_%g'%(r['variable'],r['location']):{
                    'unit':r['unit']}}
            print(self.records)
            local_rec = self.records['%s'%r['section']]['%s_%g'%(r['variable'],r['location'])]
             # self.records['%s_%g'%(r['variable'],r['location'])]
            if 'point_process' in list(r.keys()):
                local_rec['val'] = self.record_variable(section,
                                                        r['variable'],
                                                           location=r['location'],
                                                           point_process = r['point_process'])
            else:
                local_rec['val'] = self.record_variable(section,
                                                        r['variable'],
                                                           location=r['location'])

            
    def balance_currents(self, Vrest, check = False):
        # Arguments: $1 Vrest
        h.v_init = Vrest
        h.init()
        if check:
            print("Balancing all currents to %g mV "%Vrest)
        h.finitialize(Vrest)
        for sec in self.branch_sl:
            for seg in sec:
                if check:
                    e_pas = seg.e_pas
                seg.e_pas = Vrest
                if h.ismembrane("na_ion"):
                    seg.e_pas = seg.e_pas + (seg.ina + seg.ik) / seg.g_pas
                if h.ismembrane("hd"):
                    seg.e_pas = seg.e_pas + seg.i_hd/seg.g_pas
                if h.ismembrane("ca_ion"):
                    seg.e_pas = seg.e_pas + seg.ica/seg.g_pas
                if check:
                    print(e_pas, seg.e_pas)
                    # print (seg.ina+seg.ik+seg.ica+seg.i_hd)/seg.g_pas + Vrest
                    
    def record(self, to_record):
        self.records = {}
        if 'vm' in to_record:
            self.records['vms'] = {}
            for sec in self.branch_sl:
                secs = self.records['vms'][sec.name] = {}
                for seg in sec:
                    secs[seg.x] = h.Vector()
                    secs[seg.x].record(seg._ref_v)
        if 'spikes' in to_record:
            self.records['spikes'] = h.Vector()
            self.nc_spike = h.NetCon(self.branch93['apic[93]'](0.5)._ref_v, None,-20,0,1, sec = self.branch93['apic[93]'])
            self.nc_spike.record(self.records['spikes'])

    def record_spikes(self, threshold=-30):
        self.spiketimes = h.Vector()
        self.spikecount = h.APCount(0.5, sec=self.branch_base)
        self.spikecount.thresh = threshold
        self.spikecount.record(self.spiketimes)

    def record_variable(self, section, variable, location=0.5, point_process=None):
        v = h.Vector()
        if point_process is not None:
            eval('v.record(getattr(section,"%s")._ref_%s, sec = section)'%(point_process,variable))
        else:
            eval('v.record(section(%g)._ref_%s, sec = section)'%(location,variable))
        return v

    def save_records(self, store, index = None, write_datasets = True):
        if index is not None:
            g = store.create_group('%s_%g'%(self.Name, index))
        else:
            g = store.create_group(self.Name)

        # Loop over sections
        for r_n,r in self.records.items():
            print(r_n,list(r.keys()))
            r_g = g.create_group(r_n)
            # Write section time
            if r_n is 'time':
                r_u = r_g.create_dataset('Unit', data = np.string_(r['unit']))
                if write_datasets:
                    data = np.array(r['val'])
                    data_length = data.shape[0]
                    r_v = r_g.create_dataset('Data',
                                             data = data,
                                             compression="gzip",
                                             compression_opts=9,
                                             chunks=(min(100,data_length),)
                                             )
                else:
                    r_v = r_g.create_dataset('Data',
                                             (1e5,),
                                             dtype = 'float',
                                             compression="gzip")#,
                                             #compression_opts=9)
                                             #chunks=(100,))
            else:
               # Loop over variables in sections
                for v_n,v in r.items():
                    v_g = r_g.create_group(v_n)
                    v_u = v_g.create_dataset('Unit', data = np.string_(v['unit']))
                    if write_datasets:
                        data = np.array(v['val'])
                        data_length = data.shape[0]
                        v_v = v_g.create_dataset('Data',
                                                 data = data,
                                                 compression="gzip",
                                                 compression_opts=9,
                                                 chunks=(min(100,data_length),)
                                                 )
                    else:
                        v_v = v_g.create_dataset('Data',
                                                 (1e5,),
                                                 dtype = 'float',
                                                 compression="gzip")#,
                                                 #compression_opts=9)
                                                 #chunks=(100,))

    # def store_records(self, section_group, index = None):
    #     # dset = section_group['%s_%g'%(self.Name, index)]['Data']
    #     if index is not None:
    #         dgroup = section_group['%s_%g'%(self.Name, index)]
    #     else:
    #         dgroup = section_group[self.Name]

    #     print dgroup.keys()
    #     for r_n,r in self.records.iteritems():
    #         print dgroup[r_n]['Data']
    #         data = np.array(r['val'])
    #         print data.shape
    #         # dgroup[r_n]['Data'][:] = 
    #         # dgroup[r_n]['Data'].resize((500,))
    #         # print dgroup[r_n]['Data']
            
if __name__ == '__main__':
    Vrest = -70 # mV
    Rm = 26000
    RmDend = Rm
    RaAll= 150
    CmDend = 1.4
    b = cell(Vrest, RmDend, RaAll, CmDend)
