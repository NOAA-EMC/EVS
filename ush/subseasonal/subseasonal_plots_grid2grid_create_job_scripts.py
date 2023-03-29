'''                           
Program Name: subseasonal_plots_grid2grid_create_job_scripts.py
Contact(s): Shannon Shields
Abstract: This creates multiple independent job scripts. These
          jobs contain all the necessary environment variables
          and commands needed to run the specific
          use case.
'''

import sys
import os
import glob
import datetime
import numpy as np              
import subprocess               
import subseasonal_util as sub_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \                             .split(' '))
PBS_NODEFILE = os.environ['PBS_NODEFILE']
VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
################################################
#### Plotting jobs
################################################
plot_jobs_dict = {
    'anom': {},
    'pres': {},
    'ENSO': {},
    'OLR': {},
    'precip': {},
    'sea_ice': {
        'WeeklyAvg_Concentration': {'line_type_stat_list': ['SL1L2/RMSE',
                                                            'SL1L2/ME'],
                                    'vx_mask_list': ['ARCTIC', 'ANTARCTIC'],
                                    'fcst_var_dict': {'name': 'ICEC_WEEKLYAVG',
                                                      'levels': 'Z0',
                                                      'threshs': 'NA'},
                                    'obs_var_dict': {'name': 'ice_conc',
                                                     'levels': "'*,*'",
                                                     'threshs': 'NA'},
                                    'interp_dict': {'method': 'NEAREST',
                                                    'points': '1'},
                                    'grid': 'G003',
                                    'obs_name': 'osi_saf',
                                    'plots_list': 'time_series, lead_average'},

        'WeeklyAvg_Concentration_Thresh': {'line_type_stat_list': ['CTC/CSI'],
                                           'vx_mask_list': ['ARCTIC',
                                                            'ANTARCTIC'],
                                           'fcst_var_dict': {'name': (
                                                                 'ICEC_WEEKLYAVG'
                                                             ),
                                                             'levels': 'Z0',
                                                             'threshs': ('ge15, '
                                                                         +'ge40, '
                                                                         +'ge80')},
                                           'obs_var_dict': {'name': 'ice_conc',
                                                            'levels': "'*,*'",
                                                            'threshs': ('ge15, '
                                                                        +'ge40, '
                                                                        +'ge80')},
                                           'interp_dict': {'method': 'NEAREST',
                                                           'points': '1'},
                                           'grid': 'G003',
                                           'obs_name': 'osi_saf',
                                           'plots_list': ('time_series, '
                                                          +'lead_average')},
        'WeeklyAvg_Concentration_PerfDia': {'line_type_stat_list': \
                                                ['CTC/PERF_DIA'],
                                            'vx_mask_list': \
                                                ['ARCTIC', 'ANTARCTIC'],
