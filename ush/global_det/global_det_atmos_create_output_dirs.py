#!/usr/bin/env python3
'''
Name: global_det_atmos_create_output_dirs.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This creates the base directories and their subdirectories.
Run By: scripts/stats/global_det/exevs_global_det_atmos_grid2grid_stats.sh
        scripts/stats/global_det/exevs_global_det_atmos_grid2obs_stats.sh
        scripts/plots/global_det/exevs_global_det_atmos_grid2grid_plots.sh
        scripts/plots/global_det/exevs_global_det_atmos_grid2obs_plots.sh
'''

import os
import datetime
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
evs_ver = os.environ['evs_ver']
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
model_list = os.environ['model_list'].split(' ')
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
if VERIF_CASE_STEP == 'grid2grid_stats':
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        if VERIF_CASE_STEP_type == 'flux':
            data_dir_list.append(os.path.join(data_base_dir, 'get_d'))
        elif VERIF_CASE_STEP_type in ['precip_accum24hr', 'precip_accum3hr']:
            data_dir_list.append(os.path.join(data_base_dir, 'ccpa'))
        elif VERIF_CASE_STEP_type == 'sea_ice':
            data_dir_list.append(os.path.join(data_base_dir, 'osi_saf'))
        elif VERIF_CASE_STEP_type == 'snow':
            data_dir_list.append(os.path.join(data_base_dir, 'nohrsc'))
        elif VERIF_CASE_STEP_type == 'sst':
            data_dir_list.append(os.path.join(data_base_dir, 'ghrsst_ospo'))
elif VERIF_CASE_STEP == 'grid2obs_stats':
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        if VERIF_CASE_STEP_type == 'pres_levs':
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_gdas'))
        elif VERIF_CASE_STEP_type == 'sfc':
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_gdas'))
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_nam'))
        elif VERIF_CASE_STEP_type == 'ptype':
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_nam'))
elif VERIF_CASE_STEP == 'grid2grid_plots':
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        if VERIF_CASE_STEP_type == 'precip':
            data_dir_list.append(os.path.join(data_base_dir, 'ccpa'))
        elif VERIF_CASE_STEP_type == 'snow':
            data_dir_list.append(os.path.join(data_base_dir, 'nohrsc'))

# Create data directories
for data_dir in data_dir_list:
    gda_util.make_dir(data_dir)

# Create job script base directory
if STEP == 'stats':
    job_scripts_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                   'METplus_job_scripts')
elif STEP == 'plots':
   job_scripts_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                   'plot_job_scripts')
if not os.path.exists(job_scripts_dir):
    gda_util.make_dir(job_scripts_dir)

# Build information of working and COMOUT output directories
working_dir_list = []
COMOUT_dir_list = []
if STEP == 'stats':
    working_output_base_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                           'METplus_output')
    working_dir_list.append(working_output_base_dir)
    working_dir_list.append(os.path.join(working_output_base_dir, 'confs'))
    working_dir_list.append(os.path.join(working_output_base_dir, 'logs'))
    working_dir_list.append(os.path.join(working_output_base_dir, 'tmp'))
    date_dt = start_date_dt
    while date_dt <= end_date_dt:
        for model in model_list:
            COMOUT_dir_list.append(
                os.path.join(COMOUT, RUN+'.'+date_dt.strftime('%Y%m%d'), model,
                             VERIF_CASE)
            )
            COMOUT_dir_list.append(
                os.path.join(COMOUT, model+'.'+date_dt.strftime('%Y%m%d'))
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
        date_dt = date_dt + datetime.timedelta(days=1)
elif STEP == 'plots':
    NDAYS = str(os.environ['NDAYS'])
    working_output_base_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                           'plot_output')
    working_dir_list.append(working_output_base_dir)
    working_dir_list.append(
        os.path.join(working_output_base_dir,
                     RUN+'.'+end_date_dt.strftime('%Y%m%d'))
    )
    working_dir_list.append(
        os.path.join(working_output_base_dir,
                     'logs')
    )
    working_dir_list.append(
        os.path.join(working_output_base_dir,
                     'tar_files')
    )
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        working_dir_list.append(
            os.path.join(working_output_base_dir,
                         RUN+'.'+end_date_dt.strftime('%Y%m%d'),
                         VERIF_CASE+'_'+VERIF_CASE_STEP_type,
                         'last'+NDAYS+'days')
        )
        COMOUT_dir_list.append(
            os.path.join(COMOUT, VERIF_CASE+'_'+VERIF_CASE_STEP_type,
                         'last'+NDAYS+'days')
        )

# Create working output directories
for working_output_dir in working_dir_list:
    gda_util.make_dir(working_output_dir)

# Create COMOUT output directories
for COMOUT_dir in COMOUT_dir_list:
    gda_util.make_dir(COMOUT_dir)

print("END: "+os.path.basename(__file__))
