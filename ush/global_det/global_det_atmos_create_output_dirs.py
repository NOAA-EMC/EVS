'''
Program Name: global_det_atmos_create_output_dirs.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This creates the base directories and their subdirectories
          for the verification use cases.
'''

import os
import datetime

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
evs_ver = os.environ['evs_ver']
COMROOT = os.environ['COMROOT']
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
        elif VERIF_CASE_STEP_type == 'precip':
            data_dir_list.append(os.path.join(data_base_dir, 'ccpa'))
        elif VERIF_CASE_STEP_type == 'sea_ice':
            data_dir_list.append(os.path.join(data_base_dir, 'osi_saf'))
        elif VERIF_CASE_STEP_type == 'snow':
            data_dir_list.append(os.path.join(data_base_dir, 'nohrsc'))
        elif VERIF_CASE_STEP_type == 'sst':
            data_dir_list.append(os.path.join(data_base_dir, 'ghrsst_median'))
elif VERIF_CASE_STEP == 'grid2obs_stats':
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        if VERIF_CASE_STEP_type == 'pres_levs':
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_gdas'))
        elif VERIF_CASE_STEP_type == 'sfc':
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_gdas'))
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_nam'))
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_rap'))
elif VERIF_CASE_STEP == 'grid2grid_plots':
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        if VERIF_CASE_STEP_type == 'precip':
            data_dir_list.append(os.path.join(data_base_dir, 'ccpa'))

# Create data directories
for data_dir in data_dir_list:
    if not os.path.exists(data_dir):
        print("Creating data directory: "+data_dir)
        os.makedirs(data_dir, mode=0o755)

# Create job script base directory
if STEP == 'stats':
    job_scripts_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                   'METplus_job_scripts')
elif STEP == 'plots':
   job_scripts_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                   'plot_job_scripts')
if not os.path.exists(job_scripts_dir):
    print("Creating job script directory: "+job_scripts_dir)
    os.makedirs(job_scripts_dir, mode=0o755)

# Build information of working and COMROOT output directories
working_dir_list = []
COMROOT_dir_list = []
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
            COMROOT_dir_list.append(
                os.path.join(COMROOT, NET, evs_ver, STEP, COMPONENT,
                             RUN+'.'+date_dt.strftime('%Y%m%d'), model,
                             VERIF_CASE)
            )
            COMROOT_dir_list.append(
                os.path.join(COMROOT, NET, evs_ver, STEP, COMPONENT,
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
        if VERIF_CASE_STEP == 'grid2grid_stats':
            for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
                if VERIF_CASE_STEP_type == 'precip':
                    COMROOT_dir_list.append(
                        os.path.join(COMROOT, NET, evs_ver, STEP, COMPONENT,
                                     RUN+'.'+date_dt.strftime('%Y%m%d'), 'ccpa',
                                     VERIF_CASE)
                    )
                    working_dir_list.append(
                        os.path.join(working_output_base_dir,
                                     RUN+'.'+date_dt.strftime('%Y%m%d'), 'ccpa',
                                     VERIF_CASE)
                    )
        elif VERIF_CASE_STEP == 'grid2obs_stats':
            for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
                if VERIF_CASE_STEP_type == 'pres_levs':
                    COMROOT_dir_list.append(
                        os.path.join(COMROOT, NET, evs_ver, STEP, COMPONENT,
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
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        working_dir_list.append(
            os.path.join(working_output_base_dir,
                         RUN+'.'+end_date_dt.strftime('%Y%m%d'),
                         'images', VERIF_CASE_STEP_type)
        )
        working_dir_list.append(
            os.path.join(working_output_base_dir,
                         RUN+'.'+end_date_dt.strftime('%Y%m%d'),
                         VERIF_CASE_STEP_type)
        )
    COMROOT_dir_list.append(
        os.path.join(COMROOT, NET, evs_ver, STEP, COMPONENT,
                     RUN+'.'+end_date_dt.strftime('%Y%m%d'))
    )

# Create working output directories
for working_output_dir in working_dir_list:
    if not os.path.exists(working_output_dir):
        print("Creating working output directory: "+working_output_dir)
        os.makedirs(working_output_dir, mode=0o755, exist_ok=True)

# Create COMROOT output directories
for COMROOT_dir in COMROOT_dir_list:
    if not os.path.exists(COMROOT_dir):
        print("Creating COMROOT output directory: "+COMROOT_dir)
        os.makedirs(COMROOT_dir, mode=0o755, exist_ok=True)

print("END: "+os.path.basename(__file__))
