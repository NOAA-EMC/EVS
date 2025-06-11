#!/usr/bin/env python3
'''
Name: aqm_create_output_dirs.py
Original Author: Mallory Row (mallory.row@noaa.gov)
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This creates the base directories and their subdirectories.
Run By: scripts/plots/aqm/exevs_aqm_grid2obs_plots.sh
'''

import os
import datetime
import aqm_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
evs_ver = os.environ['evs_ver']
SENDCOM = os.environ['SENDCOM']
COMOUT = os.environ['COMOUT']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
VERIF_CASE_STEP_src_list = (os.environ[VERIF_CASE_STEP_abbrev+'_src_list'] \
                             .split(' '))
model_list = os.environ['model_list'].split(' ')
model_evs_data_dir_list = os.environ['model_evs_data_dir_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')

# Build information of data directories
data_base_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
data_dir_list = [data_base_dir]
for model in model_list:
    data_dir_list.append(os.path.join(data_base_dir, model))

'''
if VERIF_CASE_STEP == 'grid2obs_plots':
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        if VERIF_CASE_STEP_type == 'aeronetaod':
            data_dir_list.append(os.path.join(data_base_dir, 'aeronetaod'))

if VERIF_CASE_STEP == 'grid2grid_plots':
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        if VERIF_CASE_STEP_type == 'abiaod':
            data_dir_list.append(os.path.join(data_base_dir, 'abiaod'))
        elif VERIF_CASE_STEP_type == 'viirsaod':
            data_dir_list.append(os.path.join(data_base_dir, 'viirsaod'))
'''

# Create data directories
for data_dir in data_dir_list:
    gda_util.make_dir(data_dir)

# Create job script base directory
if STEP == 'plots':
    job_scripts_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                   'plot_job_scripts')
else:
    job_scripts_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                   'unknown_job_scripts')

if not os.path.exists(job_scripts_dir):
    gda_util.make_dir(job_scripts_dir)

# Build information of working and COMOUT output directories
working_dir_list = []
output_dir_list = []
if STEP == 'plots':
    fig_name_label = os.environ['fig_name_label']
    dir_name_label = fig_name_label
    working_output_base_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                           'plot_output')
    working_dir_list.append(working_output_base_dir)
    working_dir_list.append(
        os.path.join(working_output_base_dir, 'job_work_dir')
    )
    working_dir_list.append(
        os.path.join(working_output_base_dir, 'tar_files')
    )

    if SENDCOM == 'NO':
        working_dir_list.append(
            os.path.join(working_output_base_dir,
            f"{RUN}.{end_date_dt:%Y%m%d}")
        )
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        src_idx=VERIF_CASE_STEP_type_list.index(VERIF_CASE_STEP_type)
        VERIF_CASE_STEP_src=VERIF_CASE_STEP_src_list[src_idx]
        if SENDCOM == 'NO':
            working_dir_list.append(
                os.path.join(working_output_base_dir,
                             f"{RUN}.{end_date_dt:%Y%m%d}",
                             f"{VERIF_CASE}_{VERIF_CASE_STEP_src}_{VERIF_CASE_STEP_type}",
                             dir_name_label)
            )
        if SENDCOM == 'YES':
            output_dir_list.append(
                os.path.join(COMOUT, f"{VERIF_CASE}_{VERIF_CASE_STEP_src}_{VERIF_CASE_STEP_type}",
                             dir_name_label)
            )

# Create working directories
for working_dir in working_dir_list:
    gda_util.make_dir(working_dir)

# Create output directories
for output_dir in output_dir_list:
    gda_util.make_dir(output_dir)

print("END: "+os.path.basename(__file__))
