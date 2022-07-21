'''
Program Name: global_det_atmos_copy_to_archive.py
Contact(s): Mallory Row
Abstract: This script copies files to the archive
'''

import os
import datetime
import shutil

print("BEGIN: "+os.path.basename(__file__))

# Read in common environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
NET = os.environ['NET']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
model_list = os.environ['model_list'].split(' ')
model_evs_data_dir_list = os.environ['model_evs_data_dir_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']

# Set up date information
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')

# Copy files to archive dir
for model_idx in range(len(model_list)):
    model = model_list[model_idx]
    model_evs_data_base_dir = model_evs_data_dir_list[model_idx]
    model_evs_data_dir = os.path.join(
        model_evs_data_base_dir, 'evs_data',
        COMPONENT, RUN, VERIF_CASE, model
    )
    if not os.path.exists(model_evs_data_dir):
        os.makedirs(model_evs_data_dir)
    date_dt = start_date_dt
    while date_dt <= end_date_dt:
        tmp_stat_file = os.path.join(
            DATA, VERIF_CASE+'_'+STEP, 'METplus_output',
            model+'.'+date_dt.strftime('%Y%m%d'),
            model+'_'+RUN+'_'+VERIF_CASE+'_v'
            +date_dt.strftime('%Y%m%d')+'.stat'
        )
        arch_stat_file = os.path.join(
            model_evs_data_dir, model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
        )
        if os.path.exists(tmp_stat_file):
            print("Copying "+tmp_stat_file+" to "+arch_stat_file)
            shutil.copy2(tmp_stat_file, arch_stat_file)
        else:
            print("WARNING: "+tmp_stat_file+" DOES NOT EXIST")
        date_dt = date_dt + datetime.timedelta(days=1)

print("END: "+os.path.basename(__file__))
