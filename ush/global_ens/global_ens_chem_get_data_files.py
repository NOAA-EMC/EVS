#!/usr/bin/env python3
'''
Name: global_ens_chem_get_data_files.py
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This gets the necessary data files for verification.
Run By: scripts/plots/global_ens/exevs_global_ens_chem_grid2obs_plots.sh
'''

import os
import datetime
import global_ens_chem_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in common environment variables
RUN = os.environ['RUN']
NET = os.environ['NET']
COMPONENT = os.environ['COMPONENT']
MODELNAME = os.environ['MODELNAME']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
DATA = os.environ['DATA']
COMIN = os.environ['COMIN']
model_list = os.environ['model_list'].split(' ')
g2op_type_list = os.environ['g2op_type_list'].split(' ')
g2op_obs_list = os.environ['g2op_obs_list'].split(' ')
model_evs_data_dir_list = os.environ['model_evs_data_dir_list'].split(' ')
model_file_format_list = os.environ['model_file_format_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
USER = os.environ['USER']
evs_run_mode = os.environ['evs_run_mode']

if evs_run_mode != 'production':
    QUEUESERV = os.environ['QUEUESERV']
    ACCOUNT = os.environ['ACCOUNT']
    machine = os.environ['machine']
VERIF_CASE_STEP = VERIF_CASE+'_'+STEP

# Set archive paths
if evs_run_mode != 'production':
    archive_obs_data_dir = os.environ['archive_obs_data_dir']
else:
    archive_obs_data_dir = '/dev/null'

# Make sure in right working directory
cwd = os.getcwd()
if cwd != DATA:
    os.chdir(DATA)

if STEP == 'plots' :
    # Read in VERIF_CASE_STEP related environment variables
    # Get model stat files
    start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
    VERIF_CASE_STEP_data_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
    date_type = 'VALID'
    for model_idx in range(len(model_list)):
        model = model_list[model_idx]
        model_evs_data_dir = model_evs_data_dir_list[model_idx]
        obstype = g2op_type_list[model_idx]
        obsvar  = g2op_obs_list[model_idx]
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            if date_type == 'VALID':
                if evs_run_mode == 'production':
                    source_model_date_stat_file = os.path.join(
                        model_evs_data_dir+'.'+date_dt.strftime('%Y%m%d'),
                        'evs.stats.'+MODELNAME+'.'+RUN+'.'+VERIF_CASE+'_'
                        +obstype+"_"+obsvar+"."+'v'+date_dt.strftime('%Y%m%d')+'.stat'
                    )
                else:
                    source_model_date_stat_file = os.path.join(
                        model_evs_data_dir+'.'+date_dt.strftime('%Y%m%d'),
                        'evs.stats.'+MODELNAME+'.'+RUN+'.'+VERIF_CASE+'_'
                        +obstype+"_"+obsvar+"."+'v'+date_dt.strftime('%Y%m%d')+'.stat'
                    )
                dest_model_date_stat_file = os.path.join(
                    VERIF_CASE_STEP_data_dir, model,
                    model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                )
            if not os.path.exists(dest_model_date_stat_file):
                if gda_util.check_file_exists_size(
                        source_model_date_stat_file
                ):
                    print("Linking "+source_model_date_stat_file+" to "
                          +dest_model_date_stat_file)
                    os.symlink(source_model_date_stat_file,
                               dest_model_date_stat_file)
            date_dt = date_dt + datetime.timedelta(days=1)

print("END: "+os.path.basename(__file__))
