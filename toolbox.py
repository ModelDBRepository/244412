from neuron import h
import numpy as np

def get_range(X, window, Y=None):

    # X ia a matrix with 2 cols
    # window is a 2 elements vector
    r =  X.__ge__(window[0]).__and__(X.__le__(window[1]))
    if Y is None:
        # Return a boolean array to be used as index for X rows.
        return r
    else:
        return Y[r]

def X_is_running():
    from subprocess import Popen, PIPE
    p = Popen(["xset", "-q"], stdout=PIPE, stderr=PIPE)
    p.communicate()
    return p.returncode == 0

def dig_dict_save(name,d,hfg):
    type_h_vector = type(h.Vector())
    # Loop on the dict items
    if type(d) == type({}):
        for label,item in d.items():
            # The item is a dict create an hdf5 group and redo the loop
            if label is not '__builtins__':
                dig_dict_save(label,item,hfg.create_group(label))
    elif type(d) == type(10.) or type(d) == type(10) or type(d) == type('') :
        # Save floats and int
        hfg.create_dataset(name,data=d)
    elif type(d) is type([]):
        # The d is a list
        for element_index,element in enumerate(d):
            # For each element create a group with unique label and redo the loop 
            dig_dict_save('%s_%g'%(name,element_index),element,hfg.create_group('%s_%g'%(name,element_index)))
    elif isinstance(d,np.ndarray):
        # The d is a np.array
        hfg.create_dataset(name,data=d)
    elif type(d) == type_h_vector:
        # Save compressed vector
        if name is 'Spikes':
            hfg.create_dataset(name,data=np.array(d))
        else:
            hfg.create_dataset(
                name,
                data=np.
                reshape(np.array(d),(np.array(d).shape[0],1)),
                chunks=(min(np.array(d).shape[0],1000),1),
                compression='gzip',
                compression_opts=9)

def dig_dict_convert_to_savemat(d_source,d_dest):

    # Loop on the dict items
    for name,value in d_source.items():
        if type(value) == type({}):
            # The value is a dict create an hdf5 group and redo the loop
            d_dest[name.encode('utf-8')] = {}
            dig_dict_convert_to_savemat(value,d_dest[name])
        elif type(value) == type(10.) or type(value) == type(10) or type(value) == type('') :
            # Save floats and int
            d_dest[name.encode('utf-8')] = value
        elif type(value) == type(h.Vector()) or type(value) == type([]):
            # Save compressed vector
            d_dest[name.encode('utf-8')] = np.array(value)
        else:
            print(type(value), "is not among the considered data types")

def EPSP_peak(test_spikes,time,PSP, time_window=[0,500], slope = 'instantaneous'):
    # Arguments:
    # test_spikes time of spike for eliciting test EPSPs
    # time array
    # PSP signal to process
    # tw time window to consider around each spike
    import numpy as np
    # time and PSP can be an HDF5 dataset
    time = np.array(time)
    bgs = []
    peaks = []
    amplitudes = []
    slopes = []
    # f,a = plt.subplots(1,1)
    for spike in test_spikes:
        tw = [spike-time_window[0],spike+time_window[1]]
        tw_idx = time.__ge__(tw[0]).__and__(time.__le__(tw[1]))
        EPSP = np.array(PSP[tw_idx])
        bgs.append(EPSP[0])
        peaks.append(np.max(EPSP))
        amplitudes.append(np.max(EPSP) - bgs[-1])

        # Slopes
        # import ipdb; ipdb.set_trace()        
        begin_idx = (time[tw_idx]-tw[0]).__le__(2)
        time_begin = time[tw_idx][begin_idx]-tw[0] # use only 2 ms after EPSP onset
        EPSP_begin = EPSP[begin_idx]
        # import ipdb;ipdb.set_trace()
        # remove nan in time due to 0 time steps
        if slope == 'instantaneous':
            epsp_deriv = np.diff(EPSP_begin)
            time_deriv = np.diff(time_begin)
            # plot(time_begin,EPSP_begin,figure=a)
            sl = epsp_deriv / time_deriv
            slopes_not_nan = sl[~np.isnan(sl)]
            # print slopes_not_nan
            if slopes_not_nan.tolist():
                slopes.append(max(slopes_not_nan))
            if not slopes:
                slopes = np.zero_like(epsp_deriv)
        elif slope == 'differential':
            slopes.append((EPSP_begin[-1]-EPSP_begin[0]) / (time_begin[-1]-time_begin[0]))
        else:
            print('Slope can be either instantaneous or differential!!!!', slope)
            
    # plt.show()
    return bgs,peaks,amplitudes,slopes


def EPSP_trace(test_spike,time,PSP, time_window=[0,100], zero = 0):
    # Arguments:
    # test_spikes time of spike for eliciting test EPSPs
    # time array
    # PSP signal to process
    # tw time window to consider around each spike
    import numpy as np
    # time and PSP can be an HDF5 dataset
    time = np.array(time)
    spike = test_spike

    tw = [spike+time_window[0],spike+time_window[1]]
    tw_idx = time.__ge__(tw[0]).__and__(time.__le__(tw[1]))
    EPSP = np.array(PSP[tw_idx])
    print(time_window, time[tw_idx][0], spike)
    EPSP = np.column_stack((time[tw_idx]-zero,EPSP))
    print(EPSP[0,:])
    return EPSP


def EPSP_features(run_data,section,location, time = None):
    # Test EPSPs
    if time is None:
        tests = {'pre':{},'dur':{},'post':{}}
        (tests['pre']['bgs'],tests['pre']['peaks'],tests['pre']['amplitudes'],tests['pre']['slopes']) = EPSP_peak(
            run_data['test_pre_spike_times'],
            run_data['%s/time/Data'%section],
            run_data['%s/v_%g/Data'%(section,location)],
            slope = 'instantaneous')

        (tests['dur']['bgs'],tests['dur']['peaks'],tests['dur']['amplitudes'],tests['dur']['slopes']) = EPSP_peak(
            run_data['test_during_spike_times'],
            run_data['%s/time/Data'%section],
            run_data['%s/v_%g/Data'%(section,location)],
            slope = 'instantaneous')

        (tests['post']['bgs'],tests['post']['peaks'],tests['post']['amplitudes'],tests['post']['slopes']) = EPSP_peak(
            run_data['test_post_spike_times'],
            run_data['%s/time/Data'%section],
            run_data['%s/v_%g/Data'%(section,location)],
            slope = 'instantaneous')
    else:
        tests = {'pre':{},'dur':{},'post':{}}
        print(list(run_data.keys()),'%s/v_%g/Data'%(section,location))
        (tests['pre']['bgs'],tests['pre']['peaks'],tests['pre']['amplitudes'],tests['pre']['slopes']) = EPSP_peak(
            run_data['test_pre_spike_times'],
            time,
            run_data['%s_v_%g/Data'%(section,location)],
            slope = 'instantaneous')

        (tests['dur']['bgs'],tests['dur']['peaks'],tests['dur']['amplitudes'],tests['dur']['slopes']) = EPSP_peak(
            run_data['test_during_spike_times'],
            time,
            run_data['%s_v_%g/Data'%(section,location)],
            slope = 'instantaneous')

        (tests['post']['bgs'],tests['post']['peaks'],tests['post']['amplitudes'],tests['post']['slopes']) = EPSP_peak(
            run_data['test_post_spike_times'],
            time,
            run_data['%s_v_%g/Data'%(section,location)],
            slope = 'instantaneous')

    EPSP_LTP_pre = np.column_stack((np.array(run_data['test_pre_spike_times'])[1:],
                                    np.array(tests['pre']['amplitudes'])[1:]/np.median(tests['pre']['amplitudes'])*100))
    EPSP_LTP_dur = np.column_stack((np.array(run_data['test_during_spike_times']),
                                    np.array(tests['dur']['amplitudes'])/np.median(tests['dur']['amplitudes'])*100))
    EPSP_LTP_post = np.column_stack((np.array(run_data['test_post_spike_times'])[1:],
                                     np.array(tests['post']['amplitudes'])[1:]/np.median(tests['pre']['amplitudes'])*100))
    EPSP_LTP = np.concatenate((EPSP_LTP_pre,EPSP_LTP_dur,EPSP_LTP_post), axis=0)

    EPSP_LTP_sl_pre = np.column_stack((np.array(run_data['test_pre_spike_times'])[1:],
                                       np.array(tests['pre']['slopes'])[1:]/np.median(tests['pre']['slopes'])*100))
    EPSP_LTP_sl_dur = np.column_stack((np.array(run_data['test_during_spike_times']),
                                       np.array(tests['dur']['slopes'])/np.median(tests['dur']['slopes'])*100))
    print(np.array(run_data['test_post_spike_times'])[1:].shape, np.array(tests['post']['slopes'])[1:].shape)
    EPSP_LTP_sl_post = np.column_stack((np.array(run_data['test_post_spike_times'])[1:-1],
                                        np.array(tests['post']['slopes'])[1:]/np.median(tests['pre']['slopes'])*100))
    EPSP_LTP_sl = np.concatenate((EPSP_LTP_pre,EPSP_LTP_dur,EPSP_LTP_post), axis=0)

    return EPSP_LTP, EPSP_LTP_sl

def balance_currents(Vrest,sl, check = False):
    # Arguments: $1 Vrest
    h.init()
    print("Balancing all currents to ", Vrest)
    h.finitialize(Vrest)
    for sec in sl:
        for seg in sec:
            if check:
                e_pas = seg.e_pas
                seg.e_pas = seg.v
            if h.ismembrane("na_ion"):
                seg.e_pas = seg.e_pas + (seg.ina + seg.ik) / seg.g_pas
            if h.ismembrane("hd"):
                seg.e_pas = seg.e_pas + seg.i_hd/seg.g_pas
            if h.ismembrane("ca_ion"):
                seg.e_pas = seg.e_pas + seg.ica/seg.g_pas
            if check:
                print(e_pas, seg.e_pas)

def PPR(time,V,t1,t2,t3):
    # Cal 100 * max(V([t1,t2])-Vrest) / max(V([t2,t3])-Vrest)
    # time = np.array(branch.cell.records['time']['val'])
    trest = t1 -10 # ms
    trest_i = time.__ge__(trest).nonzero()[0][0]
    Vrest = V[trest_i]
    t1_i = time.__ge__(t1).nonzero()[0][0]
    t2_i = time.__ge__(t2).nonzero()[0][0]
    t3_i = time.__ge__(t3).nonzero()[0][0]
    V1 = np.max(V[t1_i:t2_i]) - Vrest
    V2 = np.max(V[t2_i:t3_i]) - Vrest
    return V2/V1 * 100
