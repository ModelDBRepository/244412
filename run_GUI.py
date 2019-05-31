# import ipdb
from neuron import h, gui
import numpy as np
from glob import glob as listdir
import os
from branch_setup import *
from protocol import *
import h5py as h5
from GUI import Panels


CVOde = h.cvode
CVOde.active(1)

p = {}
exec(compile(open('parameters.py').read(), 'parameters.py', 'exec'),p)

# Change initialization time
p['time_on_initialization'] = 100
p['time_to_begin_induction'] = 20 # ms

branch = Spiny_branch(p)

protocol = stim_protocol(branch,p)

h.tstop = 2e4


# Load gui
h.nrncontrolmenu() # Run menu
# Color management
# 0 white
# 1 black
# 2 red
# 3 blue
# 4 green
# 5 orange
# 6 brown
# 7 violet
# 8 yellow
# 9 gray
colors = list(range(1,9))
restricted_colors = list(range(2,9))
# Brushes
brush = list(range(1,20)) # 0 thinnest, 1-4 other thicknesses,
                    # higher values cycle through these line thicknesses with different brush patterns.


plots = {}
plots['v'] = branch.plot_soma('v', label='soma',show = 0, color=restricted_colors[0],line=2, position=[0.8, 0.9])
plots['v'].size(110,200,-80,30) 
plots['v'].view(110, -80, 90, 120, 411, 52, 634.56, 407.68)
for s_i,s in enumerate(branch.spines[1:12]):
    plots['v'].addvar('%s[%i]'%('spine_head',s_i),'v(0.5)',
                      restricted_colors[(s_i)%7],1,
                      sec=s.head)
for s_i,s in enumerate(branch.spines[12:]):
    plots['v'].addvar('%s[%i]'%('spine_head',s_i),'v(0.5)',
                      9,1,
                      sec=s.head)
# plot soma Vm
plots['v'].addvar('branch[38](0.1)',
                  'v(0.1)',4,1,
                  sec=branch.cell.branch_base)
plots['v'].flush()

plots['cai'] = branch.spines[9].head.plot('cai', show=0, color=restricted_colors[0])
# Plot thresholds
time_stamps = h.Vector([110,200])
# Plot theta1
theta1 = h.Vector([p['spine_point_processes'][0]['parameters']['theta_cai_RM'], p['spine_point_processes'][0]['parameters']['theta_cai_RM']])
theta1.plot(plots['cai'], time_stamps, 1, 2)
# Plot theta2
theta2 = h.Vector([p['spine_point_processes'][2]['parameters']['theta_cai_BDNF'], p['spine_point_processes'][2]['parameters']['theta_cai_BDNF']])
theta2.plot(plots['cai'], time_stamps, 1, 7)
# Plot theta3
theta3 = h.Vector([p['spine_point_processes'][0]['parameters']['theta_cai_RMBLK'], p['spine_point_processes'][0]['parameters']['theta_cai_RMBLK']])
theta3.plot(plots['cai'], time_stamps, 2, 7)

plots['cai'].size(110,200,-0.01,0.19)
plots['cai'].view(110, -0.01, 90, 0.2, 1085, 52, 559.68, 407.68)
for s_i,s in enumerate(branch.spines[1:12]):
    plots['cai'].addvar('cai '+s.name,'cai(0.5)',restricted_colors[s_i%7],1,sec = s.head)
for s_i,s in enumerate(branch.spines[12:]):
    plots['cai'].addvar('cai '+s.name,'cai(0.5)',9,1,sec = s.head)

plots['cai'].flush()

########### Plot mBDNF of all spines in one graph #######
# plots['BDNF'] = branch.spines[0].head.plot(['BDNF','mBDNF'],
#                             type_mec='pp',
#                             label = 'mBDNF_'+s.name,
#                             color=restricted_colors[0],
#                             line=2,
#                             show=0)
# for s_i,s in enumerate(branch.spines[1:]):
#     s.head.plot(['BDNF','mBDNF'],
#                 type_mec='pp',
#                 label = 'mBDNF',
#                 color=restricted_colors[s_i%7],
#                 line=2,
#                 show=0,
#                 graph=plots['BDNF'])
# plots['BDNF'].size(0,110,0,1)
# plots['BDNF'].view(0, 0, 110, 1, 350, 486, 345.6, 563.2)

########### Plot mintracell_signaling of all spines in one graph ########
# plots['intracell_signaling'] = branch.spines[0].head.plot(['BDNF','intracell_signaling'],
#                             type_mec='pp',
#                             label = 'intracell_signaling_'+s.name,
#                             color=restricted_colors[0],
#                             line=2,
#                             show=0)
# for s_i,s in enumerate(branch.spines[1:]):
#     s.head.plot(['BDNF','intracell_signaling'],
#                 type_mec='pp',
#                 label = 'intracell_signaling',
#                 color=restricted_colors[s_i%7],
#                 line=2,
#                 show=0,
#                 graph=plots['intracell_signaling'])
# plots['intracell_signaling'].size(0,110,0,1)
# plots['intracell_signaling'].view(0, 0, 110, 1, 350, 486, 345.6, 563.2)
# # Plot thresholds
# long_time_stamps = h.Vector([110,h.tstop])
# # Plot theta1
# theta_gAMPA = h.Vector([p['spine_point_processes'][2]['parameters']['theta_gAMPA'], p['spine_point_processes'][2]['parameters']['theta_gAMPA']])
# theta_gAMPA.plot(plots['intracell_signaling'], long_time_stamps, 2, 2)

########### Plot g_factor of all spines in one graph ######
plots['g_factor'] = branch.spines[0].head.plot(['AMPA','g_factor'],
                                               type_mec='pp',
                                               label = 'gAMPA_' + branch.spines[0].name,
                                               color=restricted_colors[0],
                                               line=2,
                                               show=0)
for s_i,s in enumerate(branch.spines[1:12]):
    s.head.plot(['AMPA','g_factor'],
                 type_mec='pp',
                 label = 'gAMPA_'+s.name,
                 color=restricted_colors[(s_i+1)%7],
                 line=2,
                 show=0,
                 graph=plots['g_factor'])
for s_i,s in enumerate(branch.spines[12:18]):
    s.head.plot(['AMPA','g_factor'],
                 type_mec='pp',
                 label = 'gAMPA_'+s.name,
                 color=9,
                 line=2,
                 show=0,
                 graph=plots['g_factor'])
plots['g_factor'].size(110,200,-80,30)
plots['g_factor'].view(110, -80, 90, 120, 1085, 530, 559.68, 407.68)
plots['g_factor'].flush()

########### Plot post_intra of all spines in one graph #########
# plots['post_intra'] = branch.spines[0].head.plot(['RMECB','post_intra'],
#                                                  type_mec='pp',
#                                                  label = 'post_intra_'+s.name,
#                                                  color=restricted_colors[0],
#                                                  line=2,
#                                                  show=0)
# for s_i,s in enumerate(branch.spines[1:]):
#     s.head.plot(['RMECB','post_intra'],
#                 type_mec='pp',
#                 label = 'post_intra',
#                 color=restricted_colors[s_i%7],
#                 line=2,
#                 show=0,
#                 graph=plots['post_intra'])
# plots['post_intra'].size(0,110,0,1)
# plots['post_intra'].view(0, 0, 110, 1, 350, 486, 345.6, 563.2)
# # Plot thresholds
# long_time_stamps = h.Vector([110,h.tstop])
# # Plot theta1
# theta_RMru = h.Vector([p['spine_point_processes'][0]['parameters']['theta_RMru'], p['spine_point_processes'][0]['parameters']['theta_RMru']])
# theta_RMru.plot(plots['post_intra'], long_time_stamps, 2, 2)

########### Plot U_SE_factor of all spines in one graph ##################
plots['U_SE_factor'] = branch.spines[0].head.plot(['AMPA','U_SE_factor'],
                                                  type_mec='pp',
                                                  label = 'AMPA_prel_' + branch.spines[0].name,
                                                  color=restricted_colors[0],
                                                  line=2,
                                                  show=0)
for s_i,s in enumerate(branch.spines[1:12]):
    s.head.plot(['AMPA','U_SE_factor'],
                type_mec='pp',
                label = 'AMPA_prel_'+s.name,
                color=restricted_colors[(s_i+1)%7],
                line=2,
                show=0,
                graph=plots['U_SE_factor'])
for s_i,s in enumerate(branch.spines[12:18]):
    s.head.plot(['AMPA','U_SE_factor'],
                type_mec='pp',
                label = 'AMPA_prel_'+s.name,
                color=9,
                line=2,
                show=0,
                graph=plots['U_SE_factor'])
plots['U_SE_factor'].size(110,200,-0.01,0.19)
plots['U_SE_factor'].view(110, -0.01, 90, 0.2, 409, 531, 634.56, 407.68)
plots['U_SE_factor'].flush()

########### Run GUI ############
# if p['override_tstop'] is not None:
#     h.tstop = p['override_tstop']
# else:
#     h.tstop = protocol.p['tstop']#p['time_on_initialization']+p['time_to_begin_induction'] + 1000

panel = Panels(branch,protocol,plots)
panel.set_stim_start()
panel.set_pulse()


