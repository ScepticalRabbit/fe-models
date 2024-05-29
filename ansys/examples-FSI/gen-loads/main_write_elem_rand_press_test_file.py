# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 11:24:17 2022

@author: Lloyd Fletcher
"""

#%% IMPORTS
import time
import os
import numpy as np
import matplotlib.pyplot as plt
import sys

#==============================================================================
useWorkPath = 0
#==============================================================================

# Add the parent directory to the path to access functions
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
parent_dir = parent_dir + '\\'

import pytools.misc_tools as util
#print(sys.path)

#%% LOAD DATA
print()
print('------------------------------------------------------------------')
print('WRITE TEST FLUID PRESS TO STRUCT MODEL')
print('------------------------------------------------------------------')
# Gets the directory of the current script file
cwd = os.getcwd()+'\\'
print("Current working directory:")
print(cwd)
print()

#%% INIT PARAMS AND LOAD INITIAL DATA

#==============================================================================
ext_FSI = False
#struct_sub_path = 'models-noextfsi\\data_td_m1_cv\\'
#press_save_path = 'models-noextfsi\\fluidload_m1_cv\\'

struct_sub_path = 'models-withextfsi\\data_td_m1_dwt1\\'
press_save_path = 'models-withextfsi\\fluidload_m1_dwt1\\'
#==============================================================================

# Pressure Varibles
press_add_noise = True
if press_add_noise:
    press_noise_amp = 20
else:
    press_noise_amp = 0
press_sin_amp =  0
press_tot_amp = press_sin_amp+press_noise_amp
press_offset = press_sin_amp+press_noise_amp # Zero minimum pressure

press_num_freqs = 1
press_freq_offset_fact = 1.00
if ext_FSI:
    #press_freqs = press_freq_offset_fact*np.array([28.78,49.52,86.84])  # Hz
    press_freqs = press_freq_offset_fact*np.array([0.0,0.0,0.0])  # Hz
else:
    #press_freqs = press_freq_offset_fact*np.array([41.59,64.65,125.21])  # Hz
    press_freqs = press_freq_offset_fact*np.array([24.46,37.38,93.53])  # Hz
press_pers = 1/press_freqs

# Time Variables
time_step = 0.001   # s
time_end = 2.01     # s
time_num_steps = round(time_end/time_step)
time_vec = np.expand_dims(np.arange(0,time_end,time_step),1)

# Seed random number generator
np.random.seed(1)   # Makes random number sequence reproducible

print("Loading structural element centroid data")
 
struct_path = parent_dir + struct_sub_path
struct_name = 'elem_centroids.csv'
struct_full_path = struct_path+struct_name
# Read Structural Element Centroids
struct_elem_cents = np.genfromtxt(struct_full_path,delimiter=',')
struct_coords = struct_elem_cents[:,:-1]

struct_num_elems = struct_coords.shape[0]

print()

#%% CREATE RANDOM FLUID PRESSURE DATA PER ELEMENT

print("Generating time vs element pressure array")
# Create an array of white noise from a uniform distribution
if press_add_noise:
    press_arr = 2*press_noise_amp*np.random.rand(time_num_steps,struct_num_elems)-press_noise_amp
else:
    press_arr = np.zeros((time_num_steps,struct_num_elems))

# Add the offset so the minimum pressure is the offset value
press_arr = press_arr + press_offset

#------------------------------------------------------------------------------
print("Looping over elements to superimpose sin waves")
tic = time.time()
if press_num_freqs > 0:
    elem_t_offset = np.tile(press_pers,(struct_num_elems,1)) + \
        np.random.rand(struct_num_elems,press_num_freqs)
        
    for ee in range(struct_num_elems):
        for tt in range(time_num_steps):
            for ff in range(press_num_freqs):
                press_arr[tt,ee] = press_arr[tt,ee] + \
                    press_sin_amp/(ff+1)*np.sin(2*np.pi*press_freqs[ff]*(time_vec[tt] + \
                                            elem_t_offset[ee,ff]))
                
toc = time.time()
print('Looping over elements took {:.4f} seconds'.format(toc-tic))
#------------------------------------------------------------------------------

tab_elem = np.arange(0,struct_num_elems+1)
tab_time = np.linspace(0.0,time_end,time_num_steps+1)

press_tab = np.zeros((len(tab_time),len(tab_elem)))

press_tab[:,0] = tab_time
press_tab[0,:] = tab_elem.transpose()
press_tab[1:,1:] = press_arr

print()
#%% RESULT FIGURES
# https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
pp = util.PlotProps()
print("Plotting diagnostic figures")

#------------------------------------------------------------------------------
# FIG: Time Series
fig, ax = plt.subplots(figsize=pp.single_fig_size, layout='constrained')
fig.set_dpi(pp.resolution)

ax.plot(time_vec,press_arr[:,1],
        '-',label='E1',lw=pp.lw,ms=pp.ms)

ax.set_xlabel('Time $t$ [s]', 
              fontsize=pp.font_ax_size, fontname=pp.font_name)
ax.set_ylabel('Pressure $P$ [Pa]', 
              fontsize=pp.font_ax_size, fontname=pp.font_name)
#ax.set_xlim([0, 0.1])
plt.grid(True)

#------------------------------------------------------------------------------
# FIG: FFT

N = time_num_steps
T = time_step
x = np.linspace(0.0, N*T, N)
#y = np.sin(60.0 * 2.0*np.pi*x) + 0.5*np.sin(90.0 * 2.0*np.pi*x)
y = press_arr[:,1]
y_f = np.fft.fft(y)
x_f = np.linspace(0.0, 1.0/(2.0*T), N//2)

fig, ax = plt.subplots(figsize=pp.single_fig_size, layout='constrained')
fig.set_dpi(pp.resolution)

ax.plot(x_f, 2.0/N * np.abs(y_f[:N//2]),
        '-',label='P1',lw=pp.lw,ms=pp.ms)

ax.set_xlabel('Freq. [Hz]', 
              fontsize=pp.font_ax_size, fontname=pp.font_name)
ax.set_ylabel('Amp. [-]', 
              fontsize=pp.font_ax_size, fontname=pp.font_name)
#ax.set_xlim([0, 0.1])
plt.grid(True)

print()
#%% SAVE DATA
print("Saving pressure table to file.")
save_path = parent_dir + press_save_path

test_name = 'pressETab_f{:.2f}_fos{:.0f}_PN{}_PS{}_PO{}_ts{}_tt{}.csv'.format(
    press_freqs[0],press_freq_offset_fact*100,press_noise_amp,
    press_sin_amp,press_offset,time_step*1000,time_end)

save_name = test_name
np.savetxt(save_path+save_name,press_tab,delimiter=',')

#%% COMPLETE
print('')
print('--------------------------------------------------------------------')
print('COMPLETE\n')

#%%
'''
print("Interpolating pressure data onto structural element centroids")
tic = time.time()

toc = time.time()
print('Interpolating pressure data took {:.4f} seconds'.format(toc-tic))
print()

Write ANSYS table with: TIME,ELEM (Press)

Rows = Time
Columns = Elems

0,e1,e2,e3...
t1
t2
t3
...
'''



