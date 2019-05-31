from neuron import h
import nrnutils_ss as nu

class Spine():

    def __init__(self,
                 name,
                 p,
                 neck_mechanisms = [],
                 head_mechanisms = [],
                 parent = None,
                 connection_point = 0,
                 noiseRandObj = None,
                 balance_currents=False,
                 highindex=None):

        self.name = name
        self.parent_sec = parent[0]        
        self.parent_seg = parent[1]
        self.parent_x = parent[1].x
        # Spine morphology from Kater & Harris 1994
        # neck: 0.2 < L < 2 um, 0.04 < diam < 0.5 um, 2.512e-4 < volume < 0.3925 um3, 0.00112 < surface < 3.14 um2
        # total: 0.004 < volume < 0.6 um3, 0.1 < surface < 4 um2
        # spine: 3.7488e-3 < volume <  0.2075 um3, 0.09888 < surface < 0.86 um2
        # spine: diam = 1 um -> L = v/((diam/2)^2*3.14) = 0.2075/0.785 = 0.264 um -> surface = 0.82896 um2
        # we use here:
        # neck: L = 1 um, diam = 0.1 um
        # head: L = 0.264 um, diam = 1 um, v = 0.2075 um3
        # the head volume could be reduced
        self.neck = nu.Section(
            'neck',
            L=2,
            diam=0.5,
            cm = p['CmDend'],
            Ra = p['RaAll'],
            mechanisms=neck_mechanisms,
            parent = self.parent_sec,
            connection_point = self.parent_x)

        self.head = nu.Section(
            'head',
            L=0.264,
            diam=1,
            cm = p['CmDend'],
            Ra = p['RaAll'],
            mechanisms=head_mechanisms,
            parent = self.neck,
            point_processes=p['spine_point_processes'],
            records=p['spine_records'])

        # self.parent_sec.push()
        # for m,attr in [['na3','gbar_na3'],
        #                ['kdr','gkdrbar_kdr'],
        #                ['kad','gkabar_kad']]:
        #     if h.ismembrane(m):
        #         setattr(self.head,attr, getattr(self.parent_sec,attr))
        #         print getattr(self.head,attr)
        # h.pop_section()
        # Access head section
        self.head.push()
        # print self.head.BDNF.alpha_gAMPA, self.head.BDNF.theta_gAMPA, self.head.BDNF.sigma_gAMPA
        
        if hasattr(self.head, 'BDNF'):
            self.head.BDNF.setRandObjRef(noiseRandObj)
            self.highindex = noiseRandObj.MCellRan4(highindex)
            if h.ismembrane('ca_ion'):
                setattr(self.head,'internal_nc',h.NetCon(self.head(0.5)._ref_cai, self.head.BDNF, sec = self.head))
                self.head.internal_nc.threshold = self.head.BDNF.theta_cai_BDNF
                # print 'theta_cai_BDNF', self.head.internal_nc.threshold
                self.head.internal_nc.delay = 0.1e-3
            else:
                raise Exception("BDNF mechanism requires also cad for Ca dynamics")
            if hasattr(self.head, 'AMPA'):
                if p['check']:
                    print("Setting pointer AMPA.g_factor->BDNF.gAMPA")
                h.setpointer(self.head.AMPA._ref_g_factor, 'gAMPA', self.head.BDNF)
            else:
                raise Exception("BDNF mechanism require also AMPA")

        if hasattr(self.head, 'RMECB'):
            if hasattr(self.head, 'AMPA'):
                if p['check']:
                    print("Setting pointer AMPA.U_SE_factor->RMECB.delta_U")
                h.setpointer(self.head.AMPA._ref_U_SE_factor, 'delta_U', self.head.RMECB)
            else:
                raise Exception("RM_eCB mechanism require also AMPA")

        if h.ismembrane('na_ion'):
            self.head.ena = 55

        if h.ismembrane('k_ion'):
            self.head.ek = -90

        # Access neck section
        self.neck.push()        
            
        if h.ismembrane('na_ion'):
            self.neck.ena = 55

        if h.ismembrane('k_ion'):
            self.neck.ek = -90

        # Return to the origina section
        h.pop_section()
        h.pop_section()
        
        if balance_currents:
            self.head.balance_currents(p['Vrest'])
            self.neck.balance_currents(p['Vrest'])
