'''
Program Name: get_subseasonal_stat_files.py
Contact(s): Shannon Shields
Abstract: This script retrieves stat files for subseasonal plotting step.
'''

import os
import datetime
import subseasonal_util as sub_util

print("BEGIN: "+os.path.basename(__file__))

# Read in common environment variables
RUN = os.environ['RUN']
NET = os.environ['NET']
COMPONENT = os.environ['COMPONENT']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
DATA = os.environ['DATA']
COMIN = os.environ['COMIN']
model_list = os.environ['model_list'].split(' ')
model_dir_list = os.environ['model_dir_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
plot_by = os.environ['plot_by']
VERIF_CASE_STEP = os.environ['VERIF_CASE_STEP']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))

# Confirm working directory
cwd = os.getcwd()
if cwd != DATA:
    os.chdir(DATA)

if STEP == 'plots':
    # Read in VERIF_CASE_STEP related environment variables
    # Get model stat files
    start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
    VERIF_CASE_STEP_data_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
    for model_idx in range(len(model_list)):
        model = model_list[model_idx]
        model_dir = model_dir_list[model_idx]
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            if plot_by == 'VALID':
                source_model_date_stat_file = os.path.join(
                    model_dir+'.'+date_dt.strftime('%Y%m%d'),
                    'evs.stats.'+model+'.'+RUN+'.'+VERIF_CASE+'.'
                    +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                )
                dest_model_date_stat_file = os.path.join(
                    VERIF_CASE_STEP_data_dir, model,
                    model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                )
            if not os.path.exists(dest_model_date_stat_file):
                if os.path.exists(source_model_date_stat_file):
                    print("Linking "+source_model_date_stat_file+" to "
                          +dest_model_date_stat_file)
                    os.symlink(source_model_date_stat_file,
                               dest_model_date_stat_file)
                else:
                    print("WARNING: "+source_model_date_stat_file+" "
                          +"DOES NOT EXIST")
            date_dt = date_dt + datetime.timedelta(days=1)

print("END: "+os.path.basename(__file__))



