#!/usr/bin/env python3
'''
Name: aqm_get_data_files.py
Original Author: Mallory Row (mallory.row@noaa.gov)
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This gets the necessary data files for verification.
Run By: scripts/plots/aqm/exevs_aqm_grid2obs_plots.sh
'''

import os
import datetime
import aqm_util as gda_util

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
        #
        ## the time stamp of aqm daily variable is valided at 11Z (ozmax8)
        ## and 04z (pamve) of next days.  To get the valid-time at 04Z
        ## and 11Z of date=VDATE_START for day1, day2, and day3 forecast,
        ## the stat of previous days from VDATE_START also need to
        ## be linked
        #
        for obs_idx in range(len(VERIF_CASE_STEP_type_list)):
            obstype = VERIF_CASE_STEP_type_list[obs_idx]
            if obstype == 'ozmax8' or obstype == 'pmave':
                date_dt = start_date_dt - datetime.timedelta(days=1)
            else:
                date_dt = start_date_dt
            print(f"CHECK CHECK :: {obstype} var = {obstype} start={date_dt}")
            while date_dt <= end_date_dt:
                if date_type == 'VALID':
                    if evs_run_mode == 'production':
                        source_model_date_stat_file = os.path.join(
                            model_evs_data_dir, model+'_'+obstype+'.'
                            +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                        )
                    else:
                        source_model_date_stat_file = os.path.join(
                            model_evs_data_dir,
                            'evs.stats.'+model+'_'+obstype+"."+RUN+'.'+VERIF_CASE+'.'
                            +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                        )
                    dest_model_date_stat_file = os.path.join(
                        VERIF_CASE_STEP_data_dir, model,
                        model+'_'+obstype+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
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

else:
    print(f"DEBUG :: current script is for plots step only")
print("END: "+os.path.basename(__file__))
