import json as js
from neuron import h

def get_cell_list():
    sl = h.SectionList()
    sl.allroots()
    return sl

def get_section_list(cell):
    print(("Selected section where to start for h.wholetree() %s"%cell.name()))

    # Access parent section
    cell.push()
    # Populate sectionlist
    sl = h.SectionList()
    sl.wholetree()
    h.pop_section()
    return sl

def geom_nseg(sl, check = False):
    if check:
        for sec in sl:
            print((sec.nseg))
    for sec in sl:
        sec.nseg = int((sec.L/(0.1*h.lambda_f(100))+.9)/2)*2 + 1
    if check:
        for sec in sl:
            print((sec.nseg))

def dump_structure_in_dict_for_hoc(sl ,filename,sec_list,mec_list):
    sec_dict = {}
    for sec_n in sec_list:
        sec = sec_dict[sec_n]
        # get geometry
        
    #         sec_mechs = npy.get_variables(h,sec)

    #         # Saving initial vm
    #         fn.write('v_init = '+str(round(sec.v,2))+'\n')
    #         # Saving passive properties
    #         for sm_name,sm in sec_mechs.iteritems():
    #             if 'diam' == sm_name or 'L' == sm_name or 'Ra' == sm_name:
    #                 fn.write(sm_name+' = '+str(round(sm,4))+'\n')
    #         fn.write('\n')
    #         # Saving single channel paramenters
    #         for sm_name in mec_list:
    #             if sm_name in sec_mechs.keys():
    #                 sm = sec_mechs[sm_name]
    #                 if 'GRC' in sm_name:
    #                     mech_params = npy.get_variables_from_mechanism(h,sm,1)
    #                     fn.write(sm_name+'\n')
    #                     for p_n,p in mech_params.iteritems():
    #                         fn.write(p_n+' = '+str(p)+'\n')
    #                     fn.write('\n')
    #         fn.write('\n')
            
    # fn.close()
