#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_grid2obs_create_anomaly.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script is used to create anomaly
          data from MET point_stat MPR output.
Run By: individual statistics job scripts generated through
        ush/global_det/global_det_atmos_plots_grid2obs_create_job_scripts.py
'''

import os
import sys
import numpy as np
import glob
import pandas as pd
import datetime
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
COMOUT = os.environ['COMOUT']
COMIN = os.environ['COMIN']
SENDCOM = os.environ['SENDCOM']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
VERIF_TYPE = os.environ['VERIF_TYPE']
job_name = os.environ['job_name']
MODEL = os.environ['MODEL']
DATE = os.environ['DATE']
var1_fcst_name = os.environ['var1_fcst_name']
var1_fcst_levels = os.environ['var1_fcst_levels']
var1_obs_name = os.environ['var1_obs_name']
var1_obs_levels = os.environ['var1_obs_levels']
valid_hr_start = '06'
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end']
valid_hr_inc = os.environ['valid_hr_inc']
fhr_list = os.environ['fhr_list'].split(', ')
#fhr_start = os.environ['fhr_start']
#fhr_end = os.environ['fhr_end']
#fhr_inc = os.environ['fhr_inc']
job_num_work_dir = os.environ['job_num_work_dir']

# Check variable settings
if ' ' in var1_fcst_levels or ',' in var1_fcst_levels:
    print("ERROR: Cannot accept list of forecast levels")
    sys.exit(1)
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
    'CLIMO_MEAN', 'CLIMO_STDEV', 'CLIMO_CDF'
]

# Create fcst and obs anomaly data
STARTDATE_dt = datetime.datetime.strptime(
    DATE+valid_hr_start, '%Y%m%d%H'
)
ENDDATE_dt = datetime.datetime.strptime(
    DATE+valid_hr_end, '%Y%m%d%H'
)
valid_date_dt = STARTDATE_dt
while valid_date_dt <= ENDDATE_dt:
    # Set full paths for dates
    full_path_job_num_work_dir = os.path.join(
        job_num_work_dir, f"{RUN}.{valid_date_dt:%Y%m%d}", MODEL, VERIF_CASE
    )
    full_path_DATA = os.path.join(
        DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',
        f"{RUN}.{valid_date_dt:%Y%m%d}", MODEL, VERIF_CASE
    )
    full_path_COMIN = os.path.join(
        COMIN, STEP, COMPONENT, f"{RUN}.{valid_date_dt:%Y%m%d}",
        MODEL, VERIF_CASE
    )
    full_path_COMOUT = os.path.join(
        COMOUT, f"{RUN}.{valid_date_dt:%Y%m%d}", MODEL, VERIF_CASE
    )
    for fhr_str in fhr_list:
        fhr = int(fhr_str)
        init_date_dt = valid_date_dt - datetime.timedelta(hours=fhr)
        input_file_name = (
             f"point_stat_{VERIF_TYPE}_{job_name}_{str(fhr).zfill(2)}0000L_"
             +f"{valid_date_dt:%Y%m%d_%H}0000V.stat"
        )
        # Check possible input files
        check_input_file_list = [
            os.path.join(full_path_job_num_work_dir, input_file_name),
            os.path.join(full_path_DATA, input_file_name),
            os.path.join(full_path_COMOUT, input_file_name),
            os.path.join(full_path_COMIN, input_file_name)
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
        output_file_DATA = os.path.join(
            full_path_DATA, output_file.rpartition('/')[2]
        )
        output_file_COMOUT = os.path.join(
            full_path_COMOUT, output_file.rpartition('/')[2]
        )
        # Check input and output files
        if os.path.exists(output_file_COMOUT):
            print(f"COMOUT Output File exists: {output_file_COMOUT}")
            make_anomaly_output_file = False
            gda_util.copy_file(output_file_COMOUT, output_file_DATA)
        else:
            make_anomaly_output_file = True
        if found_input and make_anomaly_output_file:
            print(f"\nInput file: {input_file}")
            print(f"Output File: {output_file}")
            if not os.path.exists(full_path_job_num_work_dir):
                gda_util.make_dir(full_path_job_num_work_dir)
            with open(input_file, 'r') as infile:
                input_file_header = infile.readline()
            gda_util.run_shell_command(['sed', '-i', '"s/   a//g"',
                                        input_file])
            input_file_df = pd.read_csv(input_file, sep=" ", skiprows=1,
                                        skipinitialspace=True, header=None,
                                        names=MET_MPR_column_list,
                                        na_filter=False, dtype=str)
            input_file_var_level_df = input_file_df[
                (input_file_df['FCST_VAR'] == var1_fcst_name) \
                & (input_file_df['FCST_LEV'] == var1_fcst_levels) \
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
                input_file_var_level_df['CLIMO_MEAN'].values, dtype=float
            )
            fcst_anom_var_level = fcst_var_level - climo_mean_var_level
            obs_anom_var_level = obs_var_level - climo_mean_var_level
            output_file_df = pd.DataFrame.copy(input_file_var_level_df,
                                               deep=True)
            output_file_df['CLIMO_MEAN'] = 'NA'
            output_file_df['FCST'] = fcst_anom_var_level
            output_file_df['OBS'] = obs_anom_var_level
            output_file_df['FCST_VAR'] = f"{var1_fcst_name}_ANOM"
            output_file_df['OBS_VAR'] = f"{var1_obs_name}_ANOM"
            output_file_df.to_csv(output_file, header=input_file_header,
                                  index=None, sep=' ', mode='w')
            if gda_util.check_file_exists_size(output_file):
                if SENDCOM == 'YES':
                    gda_util.copy_file(output_file, output_file_COMOUT)
    valid_date_dt = valid_date_dt + datetime.timedelta(hours=int(valid_hr_inc))

print("END: "+os.path.basename(__file__))
