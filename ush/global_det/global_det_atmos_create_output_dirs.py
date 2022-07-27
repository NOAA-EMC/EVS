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

# Build information of data directories
data_base_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
data_dir_list = [data_base_dir]
for model in model_list:
    data_dir_list.append(os.path.join(data_base_dir, model))
if VERIF_CASE_STEP == 'grid2grid_stats':
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        if VERIF_CASE_STEP_type == 'flux':
            data_dir_list.append(os.path.join(data_base_dir, 'alexi'))
        elif VERIF_CASE_STEP_type == 'ozone':
            data_dir_list.append(os.path.join(data_base_dir, 'omi'))
            data_dir_list.append(os.path.join(data_base_dir, 'tropomi'))
            data_dir_list.append(os.path.join(data_base_dir, 'omps'))
        elif VERIF_CASE_STEP_type == 'precip':
            data_dir_list.append(os.path.join(data_base_dir, 'ccpa'))
        elif VERIF_CASE_STEP_type == 'sea_ice':
            data_dir_list.append(os.path.join(data_base_dir, 'osi_saf'))
            data_dir_list.append(os.path.join(data_base_dir, 'smos'))
            data_dir_list.append(os.path.join(data_base_dir, 'ostia'))
            data_dir_list.append(os.path.join(data_base_dir, 'giomas'))
        elif VERIF_CASE_STEP_type == 'snow':
            data_dir_list.append(os.path.join(data_base_dir, 'nohrsc'))
        elif VERIF_CASE_STEP_type == 'sst':
            data_dir_list.append(os.path.join(data_base_dir, 'ghrsst'))
elif VERIF_CASE_STEP == 'grid2obs_stats':
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        if VERIF_CASE_STEP_type == 'pres_levs':
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_gdas'))
        elif VERIF_CASE_STEP_type == 'sea_ice':
            data_dir_list.append(os.path.join(data_base_dir, 'iabp'))
        elif VERIF_CASE_STEP_type == 'sfc':
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_gdas'))
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_nam'))
            data_dir_list.append(os.path.join(data_base_dir, 'prepbufr_rap'))

# Create data directories
for data_dir in data_dir_list:
    if not os.path.exists(data_dir):
        print("Creating data directory: "+data_dir)
        os.makedirs(data_dir, mode=0o755)

# Create METplus jobs base directory
METplus_job_scripts_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                       'METplus_job_scripts')
if not os.path.exists(METplus_job_scripts_dir):
    print("Creating METplus job directory: "+METplus_job_scripts_dir)
    os.makedirs(METplus_job_scripts_dir, mode=0o755)

# Build information of METplus and COMROOT output directories
METplus_output_base_dir = os.path.join(DATA, VERIF_CASE_STEP, 'METplus_output')
METplus_output_dir_list = [ METplus_output_base_dir ]
METplus_output_dir_list.append(os.path.join(METplus_output_base_dir, 'confs'))
METplus_output_dir_list.append(os.path.join(METplus_output_base_dir, 'logs'))
METplus_output_dir_list.append(os.path.join(METplus_output_base_dir, 'tmp'))
COMROOT_dir_list = []
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
date_dt = start_date_dt
while date_dt <= end_date_dt:
    if STEP == 'stats':
        for model in model_list:
            COMROOT_dir_list.append(
                os.path.join(COMROOT, NET, evs_ver, STEP, COMPONENT,
                             RUN+'.'+date_dt.strftime('%Y%m%d'), model,
                             VERIF_CASE)
            )
            COMROOT_dir_list.append(
                os.path.join(COMROOT, NET, evs_ver, STEP, COMPONENT,
                             RUN+'.'+(date_dt-datetime.timedelta(days=1))\
                             .strftime('%Y%m%d'), model,
                             VERIF_CASE)
            )
            COMROOT_dir_list.append(
                os.path.join(COMROOT, NET, evs_ver, STEP, COMPONENT,
                             model+'.'+date_dt.strftime('%Y%m%d'))
            )
            METplus_output_dir_list.append(
                os.path.join(METplus_output_base_dir,
                             RUN+'.'+date_dt.strftime('%Y%m%d'), model,
                             VERIF_CASE)
            )
            METplus_output_dir_list.append(
                os.path.join(METplus_output_base_dir,
                             RUN+'.'+(date_dt-datetime.timedelta(days=1))\
                             .strftime('%Y%m%d'), model,
                             VERIF_CASE)
            )
            METplus_output_dir_list.append(
                os.path.join(METplus_output_base_dir,
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
                METplus_output_dir_list.append(
                    os.path.join(METplus_output_base_dir,
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
                METplus_output_dir_list.append(
                    os.path.join(METplus_output_base_dir,
                                 RUN+'.'+date_dt.strftime('%Y%m%d'), 'prepbufr',
                                 VERIF_CASE)
                )
    date_dt = date_dt + datetime.timedelta(days=1)

# Create COMROOT output directories
for COMROOT_dir in COMROOT_dir_list:
    if not os.path.exists(COMROOT_dir):
        print("Creating COMROOT output directory: "+COMROOT_dir)
        os.makedirs(COMROOT_dir, mode=0o755)

# Create METplus output directories
for METplus_output_dir in METplus_output_dir_list:
    if not os.path.exists(METplus_output_dir):
        print("Creating METplus output directory: "+METplus_output_dir)
        os.makedirs(METplus_output_dir, mode=0o755)

print("END: "+os.path.basename(__file__))
