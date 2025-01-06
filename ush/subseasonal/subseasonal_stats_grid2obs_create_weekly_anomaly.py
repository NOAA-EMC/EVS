#!/usr/bin/env python3
'''
Name: subseasonal_stats_grid2obs_create_weekly_anomaly.py
Contact(s): Shannon Shields
Abstract: This script is run by subseasonal_stats_grid2obs_create_weekly_
          assemble_job_scripts.py in ush/subseasonal.
          This script is used to create anomaly
          data from MET point_stat MPR output.
'''

import os
import sys
import numpy as np
import glob
import pandas as pd
import datetime
import subseasonal_util as sub_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
COMOUT = os.environ['COMOUT']
SENDCOM = os.environ['SENDCOM']
RUN = os.environ['RUN']
NET = os.environ['NET']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
VERIF_TYPE = os.environ['VERIF_TYPE']
job_name = os.environ['job_name']
MODEL = os.environ['MODEL']
WEEKLYSTART = os.environ['WEEKLYSTART']
DATE = os.environ['DATE']
var1_obs_name = os.environ['var1_obs_name']
var1_obs_levels = os.environ['var1_obs_levels']
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end']
valid_hr_inc = os.environ['valid_hr_inc']
fhr_list = os.environ['CORRECT_LEAD_SEQ'].split(',')
job_num_work_dir = os.environ['job_num_work_dir']

# Check variable settings
if ' ' in var1_obs_levels or ',' in var1_obs_levels:
    print("ERROR: Cannot accept list of observation levels")
    sys.exit(1)

# Set MET MPR columns
MET_MPR_column_list = [
    'VERSION', 'MODEL', 'DESC', 'FCST_LEAD', 'FCST_VALID_BEG',
    'FCST_VALID_END', 'OBS_LEAD', 'OBS_VALID_BEG', 'OBS_VALID_END', 'FCST_VAR',
    'FCST_UNITS', 'FCST_LEV', 'OBS_VAR', 'OBS_UNITS', 'OBS_LEV', 'OBTYPE',
    'VX_MASK', 'INTERP_MTHD', 'INTERP_PNTS', 'FCST_THRESH', 'OBS_THRESH',
    'COV_THRESH', 'ALPHA', 'LINE_TYPE', 'TOTAL', 'INDEX', 'OBS_SID',
    'OBS_LAT', 'OBS_LON', 'OBS_LVL', 'OBS_ELV', 'FCST', 'OBS', 'OBS_QC',
    'OBS_CLIMO_MEAN', 'OBS_CLIMO_STDEV', 'OBS_CLIMO_CDF',
    'FCST_CLIMO_MEAN', 'FCST_CLIMO_STDEV'
]

# Create fcst and obs anomaly data
STARTDATE_dt = datetime.datetime.strptime(
    WEEKLYSTART+valid_hr_start, '%Y%m%d%H'
)
ENDDATE_dt = datetime.datetime.strptime(
    DATE+valid_hr_end, '%Y%m%d%H'
)
fhr_start = int(fhr_list[0])
fhr_end = int(fhr_list[-1])
valid_date_dt = STARTDATE_dt
fhr = fhr_start
while valid_date_dt <= ENDDATE_dt and fhr <= fhr_end:
    # Set full paths for dates
    full_path_job_num_work_dir = os.path.join(
        job_num_work_dir, RUN+'.'
        +ENDDATE_dt.strftime('%Y%m%d'),
        MODEL, VERIF_CASE
    )
    full_path_DATA = os.path.join(
        DATA, VERIF_CASE+'_'+STEP, 'METplus_output',
        RUN+'.'+ENDDATE_dt.strftime('%Y%m%d'),
        MODEL, VERIF_CASE
    )
    full_path_COMOUT = os.path.join(
        COMOUT, RUN+'.'+ENDDATE_dt.strftime('%Y%m%d'),
        MODEL, VERIF_CASE
    )
    init_date_dt = valid_date_dt - datetime.timedelta(hours=fhr)
    input_file_name = (
        f"point_stat_{VERIF_TYPE}_{job_name}_{str(fhr).zfill(2)}0000L_"
        +f"{valid_date_dt:%Y%m%d_%H}0000V.stat"
    )
    # Check possible input files
    check_input_file_list = [
        os.path.join(full_path_job_num_work_dir, input_file_name),
        os.path.join(full_path_DATA, input_file_name),
        os.path.join(full_path_COMOUT, input_file_name)
    ]
    found_input = False
    for check_input_file in check_input_file_list:
        if os.path.exists(check_input_file):
            input_file = check_input_file
            found_input = True
            break
    # Set output file
    output_file = os.path.join(
        full_path_job_num_work_dir, f"anomaly_{VERIF_TYPE}_{job_name}_"
        +f"init{init_date_dt:%Y%m%d%H}_fhr{str(fhr).zfill(3)}.stat"
    )
    output_DATA_file = os.path.join(
        full_path_DATA, output_file.rpartition('/')[2]
    )
    output_COMOUT_file = os.path.join(
        full_path_COMOUT, output_file.rpartition('/')[2]
    )
    # Check input and output files
    if os.path.exists(output_COMOUT_file):
        print(f"COMOUT Output File exists: {output_COMOUT_file}")
        make_anomaly_output_file = False
        sub_util.copy_file(output_COMOUT_file, output_DATA_file)
    else:
        make_anomaly_output_file = True
    if found_input and make_anomaly_output_file:
        print("\nInput file: "+input_file)
        print(f"Output File: {output_file}")
        if not os.path.exists(full_path_job_num_work_dir):
            os.makedirs(full_path_job_num_work_dir)
        with open(input_file, 'r') as infile:
            input_file_header = infile.readline()
        sub_util.run_shell_command(['sed', '-i', '"s/   a//g"',
                                    input_file])
        input_file_df = pd.read_csv(input_file, sep=" ", skiprows=1,
                                    skipinitialspace=True, header=None,
                                    names=MET_MPR_column_list, 
                                    na_filter=False, dtype=str)
        input_file_var_level_df = input_file_df[
            (input_file_df['FCST_VAR'] == var1_obs_name) \
            & (input_file_df['FCST_LEV'] == var1_obs_levels) \
            & (input_file_df['OBS_VAR'] == var1_obs_name) \
            & (input_file_df['OBS_LEV'] == var1_obs_levels)
        ]
        fcst_var_level = np.array(
            input_file_var_level_df['FCST'].values, dtype=float
        )
        obs_var_level = np.array(
            input_file_var_level_df['OBS'].values, dtype=float
        )
        climo_mean_var_level = np.array(
            input_file_var_level_df['OBS_CLIMO_MEAN'].values, dtype=float
        )
        fcst_anom_var_level = fcst_var_level - climo_mean_var_level
        obs_anom_var_level = obs_var_level - climo_mean_var_level
        output_file_df = pd.DataFrame.copy(input_file_var_level_df,
                                           deep=True)
        output_file_df['OBS_CLIMO_MEAN'] = 'NA'
        output_file_df['FCST_CLIMO_MEAN'] = 'NA'
        output_file_df['FCST'] = fcst_anom_var_level
        output_file_df['OBS'] = obs_anom_var_level
        output_file_df['FCST_VAR'] = f"{var1_obs_name}_ANOM"
        output_file_df['OBS_VAR'] = f"{var1_obs_name}_ANOM"
        output_file_df.to_csv(output_file, header=input_file_header,
                              index=None, sep=' ', mode='w')
        if SENDCOM == 'YES' \
                and sub_util.check_file_exists_size(output_file):
            sub_util.copy_file(output_file, output_COMOUT_file)
    valid_date_dt = valid_date_dt + datetime.timedelta(hours=int(valid_hr_inc))
    fhr+=int(valid_hr_inc)

print("END: "+os.path.basename(__file__))
