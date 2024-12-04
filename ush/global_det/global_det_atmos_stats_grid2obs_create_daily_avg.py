#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_grid2obs_create_daily_average.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script is used to create daily average
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
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end']
valid_hr_inc = os.environ['valid_hr_inc']
fhr_end = os.environ['fhr_list'].split(', ')[-1]
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

# Set input file formats
if job_name == 'DailyAvg_TempAnom2m':
    input_file_format_COMIN = os.path.join(
        COMIN, STEP, COMPONENT, RUN+'.{valid?fmt=%Y%m%d}',
        MODEL, VERIF_CASE,
        f"anomaly_{VERIF_TYPE}_TempAnom2m_init"
        +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.stat'
    )
else:
    print(f"ERROR: job_name={job_name} not known to get file format")
    sys.exit(1)
input_file_format_DATA = os.path.join(
    DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',  RUN+'.{valid?fmt=%Y%m%d}',
    MODEL, VERIF_CASE, input_file_format_COMIN.rpartition('/')[2]
)
input_file_format_COMOUT = os.path.join(
    COMOUT, RUN+'.{valid?fmt=%Y%m%d}', MODEL, VERIF_CASE,
    input_file_format_COMIN.rpartition('/')[2]
)

# Create daily average files
print("\nCreating daily average files")
valid_hr = int(valid_hr_start)
while valid_hr <= int(valid_hr_end):
    daily_avg_valid_end = datetime.datetime.strptime(DATE+str(valid_hr),
                                                     '%Y%m%d%H')
    daily_avg_valid_start = daily_avg_valid_end - datetime.timedelta(hours=18)
    daily_avg_day_end = int(fhr_end)/24
    daily_avg_day_start = 1
    daily_avg_day = daily_avg_day_start
    while daily_avg_day <= daily_avg_day_end:
        full_path_job_num_work_dir = os.path.join(
            job_num_work_dir, f"{RUN}.{DATE}",
            MODEL, VERIF_CASE
        )
        full_path_DATA = os.path.join(
            DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',
            f"{RUN}.{DATE}", MODEL, VERIF_CASE
        )
        full_path_COMIN = os.path.join(
            COMIN, STEP, COMPONENT, f"{RUN}.{DATE}",
            MODEL, VERIF_CASE
        )
        full_path_COMOUT = os.path.join(
            COMOUT, f"{RUN}.{DATE}", MODEL, VERIF_CASE
        )
        daily_avg_file_list = []
        daily_avg_day_fhr_end = daily_avg_day * 24
        daily_avg_day_fhr_start = daily_avg_day_fhr_end - 12
        daily_avg_day_init = (daily_avg_valid_end
                              - datetime.timedelta(days=daily_avg_day))
        daily_avg_day_fhr = daily_avg_day_fhr_start
        # Set output file
        output_file = os.path.join(
            full_path_job_num_work_dir,
            f"daily_avg_{VERIF_TYPE}_{job_name}_init"
            +f"{daily_avg_day_init:%Y%m%d%H}_valid"
            +f"{daily_avg_valid_start:%Y%m%d%H}to"
            +f"{daily_avg_valid_end:%Y%m%d%H}.stat"
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
            gda_util.copy_file(output_file_COMOUT, output_file_DATA)
            make_daily_avg_output_file = False
        else:
            make_daily_avg_output_file = True
        while daily_avg_day_fhr <= daily_avg_day_fhr_end:
            daily_avg_day_fhr_valid = (
                daily_avg_day_init
                + datetime.timedelta(hours=daily_avg_day_fhr)
            )
            # Check possible input files
            daily_avg_day_fhr_DATA_input_file = gda_util.format_filler(
                input_file_format_DATA, daily_avg_day_fhr_valid,
                daily_avg_day_init,
                str(daily_avg_day_fhr), {}
            )
            daily_avg_day_fhr_COMOUT_input_file = gda_util.format_filler(
                input_file_format_COMOUT, daily_avg_day_fhr_valid,
                daily_avg_day_init,
                str(daily_avg_day_fhr), {}
            )
            daily_avg_day_fhr_COMIN_input_file = gda_util.format_filler(
                    input_file_format_COMIN, daily_avg_day_fhr_valid,
                    daily_avg_day_init,
                    str(daily_avg_day_fhr), {}
            )
            check_input_file_list = [
                daily_avg_day_fhr_DATA_input_file,
                daily_avg_day_fhr_COMOUT_input_file,
                daily_avg_day_fhr_COMIN_input_file
            ]
            daily_avg_day_fhr_job_input_file_glob = glob.glob(
                os.path.join(
                    DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',
                    'job_work_dir', 'assemble_data', 'job*',
                    daily_avg_day_fhr_COMOUT_input_file.rpartition(
                        f"{COMPONENT}/"
                    )[2]
                )
            )
            if len(daily_avg_day_fhr_job_input_file_glob) == 1:
                check_input_file_list.insert(
                    0,daily_avg_day_fhr_job_input_file_glob[0]
                )
            found_input = False
            for check_input_file in check_input_file_list:
                daily_avg_day_fhr_input_file = check_input_file
                if os.path.exists(daily_avg_day_fhr_input_file):
                    daily_avg_day_fhr_input_file = check_input_file
                    found_input = True
                    break
            if found_input and make_daily_avg_output_file:
                print("Input file for forecast hour "+str(daily_avg_day_fhr)
                      +', valid '+str(daily_avg_day_fhr_valid)
                      +', init '+str(daily_avg_day_init)+": "
                      +daily_avg_day_fhr_input_file)
                daily_avg_file_list.append(daily_avg_day_fhr_input_file)
            else:
                if not found_input:
                    print("No input file for forecast hour "
                          +str(daily_avg_day_fhr)
                          +', valid '+str(daily_avg_day_fhr_valid)
                          +', init '+str(daily_avg_day_init)+": "
                          +', '.join(check_input_file_list)+" do not exist")
            daily_avg_day_fhr+=12
        daily_avg_df_list = []
        if make_daily_avg_output_file:
            if len(daily_avg_file_list) == 2:
                make_daily_avg_output_file = True
            else:
                make_daily_avg_output_file = False
                print("NOTE: Cannot creat daily average file "
                      +output_file+"; need 2 input files")
        if make_daily_avg_output_file:
            print(f"Output File: {output_file}")
            if not os.path.exists(full_path_job_num_work_dir):
                gda_util.make_dir(full_path_job_num_work_dir)
            all_daily_avg_df = pd.DataFrame(columns=MET_MPR_column_list)
            for daily_avg_file in daily_avg_file_list:
                with open(daily_avg_file, 'r') as infile:
                    input_file_header = infile.readline()
                daily_avg_file_df = pd.read_csv(daily_avg_file, sep=" ",
                                                skiprows=1,
                                                skipinitialspace=True, header=None,
                                                names=MET_MPR_column_list,
                                                na_filter=False, dtype=str)
                all_daily_avg_df = pd.concat(
                    [all_daily_avg_df, daily_avg_file_df], ignore_index=True
                )
            for obtype in all_daily_avg_df['OBTYPE'].unique():
                all_daily_avg_obtype_df = all_daily_avg_df.loc[
                    all_daily_avg_df['OBTYPE'] == obtype
                ]
                for sid in all_daily_avg_obtype_df['OBS_SID'].unique():
                    all_daily_avg_obtype_sid_df = (
                        all_daily_avg_obtype_df.loc[
                            all_daily_avg_obtype_df['OBS_SID'] == sid
                        ]
                    )
                    for vx_mask \
                            in all_daily_avg_obtype_sid_df['VX_MASK'].unique():
                        all_daily_avg_obtype_sid_vx_mask_df = (
                            all_daily_avg_obtype_sid_df.loc[
                                all_daily_avg_obtype_sid_df['VX_MASK']\
                                == vx_mask
                            ]
                        )
                        if len(all_daily_avg_obtype_sid_vx_mask_df) != 2:
                            continue
                        all_daily_avg_obtype_sid_vx_mask_fcst_mean = (
                            np.array(
                                all_daily_avg_obtype_sid_vx_mask_df['FCST']\
                                .values, dtype=float
                            ).mean()
                        )
                        all_daily_avg_obtype_sid_vx_mask_obs_mean = (
                            np.array(
                                all_daily_avg_obtype_sid_vx_mask_df['OBS']\
                                .values, dtype=float
                            ).mean()
                        )
                        daily_avg_obtype_sid_vx_mask_df = pd.DataFrame.copy(
                            all_daily_avg_obtype_sid_vx_mask_df.iloc[0,:],
                            deep=True
                        )
                        daily_avg_obtype_sid_vx_mask_df['FCST_LEAD'] = (
                            str(daily_avg_day_fhr_end).zfill(2)+'0000'
                        )
                        daily_avg_obtype_sid_vx_mask_df['FCST_VALID_BEG'] = (
                            daily_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        daily_avg_obtype_sid_vx_mask_df['FCST_VALID_END'] = (
                            daily_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        daily_avg_obtype_sid_vx_mask_df['OBS_VALID_BEG'] = (
                            daily_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        daily_avg_obtype_sid_vx_mask_df['OBS_VALID_END'] = (
                            daily_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        daily_avg_obtype_sid_vx_mask_df['FCST_VAR'] = (
                            daily_avg_obtype_sid_vx_mask_df['FCST_VAR']
                            +'_DAILYAVG'
                        )
                        daily_avg_obtype_sid_vx_mask_df['OBS_VAR'] = (
                            daily_avg_obtype_sid_vx_mask_df['OBS_VAR']
                            +'_DAILYAVG'
                        )
                        daily_avg_obtype_sid_vx_mask_df['FCST'] = str(
                            all_daily_avg_obtype_sid_vx_mask_fcst_mean
                        )
                        daily_avg_obtype_sid_vx_mask_df['OBS'] = str(
                            all_daily_avg_obtype_sid_vx_mask_obs_mean
                        )
                        daily_avg_df_list.append(
                            daily_avg_obtype_sid_vx_mask_df
                        )
            daily_avg_df = pd.concat(
                daily_avg_df_list, axis=1, ignore_index=True
            ).T
            daily_avg_df.to_csv(
                output_file, header=input_file_header,
                index=None, sep=' ', mode='w'
            )
            if gda_util.check_file_exists_size(output_file):
                if SENDCOM == 'YES':
                    gda_util.copy_file(output_file, output_file_COMOUT)
        print("")
        daily_avg_day+=1
    valid_hr+=int(valid_hr_inc)

print("END: "+os.path.basename(__file__))
