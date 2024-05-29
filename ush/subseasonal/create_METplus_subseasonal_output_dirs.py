#!/usr/bin/env python3
'''
Program Name: create_METplus_subseasonal_output_dirs.py
Contact(s): Shannon Shields
Abstract: This script is run by all stats and plots scripts in scripts/.
          This creates the base directories and their subdirectories
          for the METplus verification use cases and their types.
'''

import os
import datetime

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMOUT = os.environ['COMOUT']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']
VERIF_CASE = os.environ['VERIF_CASE']
VERIF_CASE_STEP = os.environ['VERIF_CASE_STEP']
VCS = os.environ['VERIF_CASE_STEP']
model_list = os.environ['model_list'].split(' ')
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VCS_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VCS_type_list = os.environ[VERIF_CASE_STEP_abbrev+'_type_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']

start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')

# Create data directories
data_base_dir = os.path.join(DATA, VCS, 'data')
data_dir_list = [data_base_dir]
for model in model_list:
    data_dir_list.append(os.path.join(data_base_dir, model))
if VERIF_CASE_STEP == 'grid2grid_stats':
    for VCS_type in VCS_type_list:
        if VCS_type == 'temp':
            data_dir_list.append(os.path.join(data_base_dir, 'ecmwf'))
        elif VCS_type == 'pres_lvls':
            data_dir_list.append(os.path.join(data_base_dir, 'gfs'))
        elif VCS_type == 'sst':
            data_dir_list.append(os.path.join(data_base_dir, 'ghrsst_ospo'))
        elif VCS_type == 'seaice':
            data_dir_list.append(os.path.join(data_base_dir, 'osi_saf'))
elif VERIF_CASE_STEP == 'grid2obs_stats':
    for VCS_type in VCS_type_list:
        if VCS_type == 'prepbufr':
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_nam'))

# Create data directories
for data_dir in data_dir_list:
    if not os.path.exists(data_dir):
        print("Creating data directory: "+data_dir)
        os.makedirs(data_dir, mode=0o755)

# Create METplus job script base directory
if STEP == 'stats':
    job_scripts_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                   'METplus_job_scripts')
elif STEP == 'plots':
    job_scripts_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                   'plot_job_scripts')
if not os.path.exists(job_scripts_dir):
    print("Creating job script directory: "+job_scripts_dir)
    os.makedirs(job_scripts_dir, mode=0o755)

# Create working and COMOUT output directories
working_dir_list = []
COMOUT_dir_list = []
if STEP == 'stats':
    working_output_base_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                           'METplus_output')
    working_dir_list.append(working_output_base_dir)
    working_dir_list.append(os.path.join(working_output_base_dir, 'confs'))
    working_dir_list.append(os.path.join(working_output_base_dir, 'logs'))
    working_dir_list.append(os.path.join(working_output_base_dir, 'tmp'))
    working_dir_list.append(os.path.join(working_output_base_dir, 'stage'))
    date_dt = start_date_dt
    while date_dt <= end_date_dt:
        for model in model_list:
            if VERIF_CASE_STEP == 'grid2obs_stats':
                COMOUT_dir_list.append(
                    os.path.join(COMOUT,
                                 RUN+'.'+date_dt.strftime('%Y%m%d'), model,
                                 VERIF_CASE)
                )
            COMOUT_dir_list.append(
                os.path.join(COMOUT,
                             model+'.'+date_dt.strftime('%Y%m%d'))
            )
            working_dir_list.append(
                os.path.join(working_output_base_dir,
                             RUN+'.'+date_dt.strftime('%Y%m%d'), model,
                             VERIF_CASE)
            )
            working_dir_list.append(
                os.path.join(working_output_base_dir,
                             model+'.'+date_dt.strftime('%Y%m%d'))
            )
        if VERIF_CASE_STEP == 'grid2obs_stats':
            for VCS_type in VCS_type_list:
                if VCS_type in ['prepbufr']:
                    COMOUT_dir_list.append(
                        os.path.join(COMOUT,
                                     RUN+'.'+date_dt.strftime('%Y%m%d'), 'prepbufr',
                                     VERIF_CASE)
                    )
                    working_dir_list.append(
                        os.path.join(working_output_base_dir,
                                     RUN+'.'+date_dt.strftime('%Y%m%d'), 'prepbufr',
                                     VERIF_CASE)
                    )
        date_dt = date_dt + datetime.timedelta(days=1)
elif STEP == 'plots':
    working_output_base_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                           'plot_output')
    working_dir_list.append(working_output_base_dir)
    working_dir_list.append(
        os.path.join(working_output_base_dir,
                     RUN+'.'+end_date_dt.strftime('%Y%m%d'))
    )
    working_dir_list.append(
        os.path.join(working_output_base_dir,
                     RUN+'.'+end_date_dt.strftime('%Y%m%d'),
                     'logs')
    )
    for VCS_type in VCS_type_list:
        working_dir_list.append(
            os.path.join(working_output_base_dir,
                         RUN+'.'+end_date_dt.strftime('%Y%m%d'),
                         'images', VCS_type)
        )
        working_dir_list.append(
            os.path.join(working_output_base_dir,
                         RUN+'.'+end_date_dt.strftime('%Y%m%d'),
                         VCS_type)
        )
    COMOUT_dir_list.append(COMOUT)

# Create working output directories
for working_output_dir in working_dir_list:
    if not os.path.exists(working_output_dir):
        print("Creating working output directory: "+working_output_dir)
        os.makedirs(working_output_dir, mode=0o755, exist_ok=True)

# Create COMOUT output directories
for COMOUT_dir in COMOUT_dir_list:
    if not os.path.exists(COMOUT_dir):
        print("Creating COMOUT output directory: "+COMOUT_dir)
        os.makedirs(COMOUT_dir, mode=0o755, exist_ok=True)

print("END: "+os.path.basename(__file__))
