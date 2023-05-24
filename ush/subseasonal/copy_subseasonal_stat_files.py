#!/usr/bin/env python3
'''
Program Name: copy_subseasonal_stat_files.py
Contact(s): Shannon Shields
Abstract: This script is run by all stat scripts in scripts/subseasonal/stats/
          It copies the stat files to the online archive or
          to COMROOT.
'''

import os
import datetime

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
VERIF_CASE = os.environ['VERIF_CASE']
VERIF_CASE_STEP = os.environ['VERIF_CASE_STEP']
VCS = os.environ['VERIF_CASE_STEP']
model_list = os.environ['model_list'].split(' ')
MODELNAME = os.environ['MODELNAME']
model_stats_dir_list = os.environ['model_stats_dir_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
make_met_data_by = os.environ['make_met_data_by']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VCS_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VCS_type_list = os.environ[VCS_abbrev+'_type_list'].split(' ')

# Set up date information
sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]),
                          int(start_date[6:]))
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]),
                          int(end_date[6:]))

for VCS_type in VCS_type_list:
    VCS_abbrev_type = VCS_abbrev+'_'+VCS_type
    VCS_abbrev_type_gather_by = os.environ[
        VCS_abbrev_type+'_gather_by'
    ]
    #sdate = sdate - datetime.timedelta(days=28) 
    date = sdate
    while date <= edate:
        DATE = date.strftime('%Y%m%d')
        for model in model_list:
            model_idx = model_list.index(model)
            model_stats_dir = model_stats_dir_list[model_idx]
            tmp_stat_file = os.path.join(
                DATA, VCS, 'METplus_output',
                model+'.'+DATE, 'evs.stats.'
                +model+'.'+RUN+'.'+VERIF_CASE
                +'.v'+DATE+'.stat'
            )
            arch_stat_file = os.path.join(
                model_stats_dir, 'evs.stats.'
                +model+'.'+RUN+'.'+VERIF_CASE
                +'.v'+DATE+'.stat'
            )
            if os.path.exists(tmp_stat_file) \
                    and os.path.getsize(tmp_stat_file):
                arch_stat_file_dir = arch_stat_file.rpartition('/')[0]
                if not os.path.exists(arch_stat_file_dir):
                    os.makedirs(arch_stat_file_dir)
                print("Copying "+tmp_stat_file+" to "+arch_stat_file)
                os.system('cpfs '+tmp_stat_file+' '+arch_stat_file)
            else:
                print("**************************************************")
                print("** WARNING: "+tmp_stat_file+" "
                      +"was not generated or zero size")
                print("**************************************************\n")
        date = date + datetime.timedelta(days=1)

print("END: "+os.path.basename(__file__))
