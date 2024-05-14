#!/usr/bin/env python3
'''
Name: subseasonal_stats_grid2obs_create_weekly_avg.py
Contact(s): Shannon Shields
Abstract: This script is run by subseasonal_stats_grid2obs_create_job_scripts.py
          in ush/subseasonal.
          This script is used to create weekly averages
          from MET point_stat MPR output.
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
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end']
valid_hr_inc = os.environ['valid_hr_inc']
fhr_end = os.environ['fhr_list'].split(',')[-1]

# Process run time arguments
if len(sys.argv) != 4:
    print("FATAL ERROR: Not given correct number of run time arguments..."
          +os.path.basename(__file__)+" VARNAME_VARLEVEL DATAROOT_FILE_FORMAT "
          +"COMIN_FILE_FORMAT")
    sys.exit(1)
else:
    if '_' not in sys.argv[1]:
        print("FATAL ERROR: variable and level runtime argument formatted "
              +"incorrectly, be sure to separate variable and level with "
              +"an underscore (_), example HGT_P500")
        sys.exit(1)
    else:
        var_level = sys.argv[1]
        print("Using var_level = "+var_level)
    DATAROOT_file_format = sys.argv[2]
    COMIN_file_format = sys.argv[3]

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

# Set input and output directories
output_dir = os.path.join(DATA, VERIF_CASE+'_'+STEP, 'METplus_output',
                          RUN+'.'+DATE, MODEL, VERIF_CASE)

# Create weekly average files
print("\nCreating weekly average files")
valid_hr = int(valid_hr_start)
while valid_hr <= int(valid_hr_end):
    weekly_avg_valid_end = datetime.datetime.strptime(DATE+str(valid_hr),
                                                      '%Y%m%d%H')
    weekly_avg_valid_start = datetime.datetime.strptime(WEEKLYSTART
                                                        +str(valid_hr),
                                                        '%Y%m%d%H')
    weekly_avg_day_end = int(fhr_end)/24
    weekly_avg_day_start = 7
    weekly_avg_day = weekly_avg_day_start
    while weekly_avg_day <= weekly_avg_day_end:
        weekly_avg_file_list = []
        weekly_avg_day_fhr_end = weekly_avg_day * 24
        weekly_avg_day_fhr_start = weekly_avg_day_fhr_end - 168
        weekly_avg_day_init = (weekly_avg_valid_end
                              - datetime.timedelta(days=weekly_avg_day))
        weekly_avg_day_fhr = weekly_avg_day_fhr_start
        output_DATA_file = os.path.join(output_dir, 'weekly_avg_'
                                        +VERIF_TYPE+'_'+job_name+'_init'
                                        +weekly_avg_day_init.strftime('%Y%m%d%H')
                                        +'_valid'
                                        +weekly_avg_valid_start\
                                        .strftime('%Y%m%d%H')+'to'
                                        +weekly_avg_valid_end\
                                        .strftime('%Y%m%d%H')+'.stat')
        output_COMOUT_file = os.path.join(COMOUT, RUN+'.'+DATE, MODEL,
                                          VERIF_CASE, 'weekly_avg_'
                                          +VERIF_TYPE+'_'+job_name+'_init'
                                          +weekly_avg_day_init.strftime('%Y%m%d%H')
                                          +'_valid'
                                          +weekly_avg_valid_start\
                                          .strftime('%Y%m%d%H')+'to'
                                          +weekly_avg_valid_end\
                                          .strftime('%Y%m%d%H')+'.stat')
        while weekly_avg_day_fhr <= weekly_avg_day_fhr_end:
            weekly_avg_day_fhr_valid = (
                weekly_avg_day_init
                + datetime.timedelta(hours=weekly_avg_day_fhr)
            )
            weekly_avg_day_fhr_DATAROOT_input_file = sub_util.format_filler(
                    DATAROOT_file_format, weekly_avg_day_fhr_valid,
                    weekly_avg_day_init,
                    str(weekly_avg_day_fhr), {}
            )
            weekly_avg_day_fhr_COMIN_input_file = sub_util.format_filler(
                    COMIN_file_format, weekly_avg_day_fhr_valid,
                    weekly_avg_day_init,
                    str(weekly_avg_day_fhr), {}
            )
            if os.path.exists(weekly_avg_day_fhr_COMIN_input_file):
                weekly_avg_day_fhr_input_file = (
                    weekly_avg_day_fhr_COMIN_input_file)
            else:
                weekly_avg_day_fhr_input_file = (
                    weekly_avg_day_fhr_DATAROOT_input_file
                )
            if os.path.exists(weekly_avg_day_fhr_input_file):
                print("Input file for forecast hour "+str(weekly_avg_day_fhr)
                      +', valid '+str(weekly_avg_day_fhr_valid)
                      +', init '+str(weekly_avg_day_init)+": "
                      +weekly_avg_day_fhr_input_file)
                weekly_avg_file_list.append(weekly_avg_day_fhr_input_file)
            else:
                print("No input file for forecast hour "+str(weekly_avg_day_fhr)
                      +', valid '+str(weekly_avg_day_fhr_valid)
                      +', init '+str(weekly_avg_day_init)+" "
                      +weekly_avg_day_fhr_DATAROOT_input_file+" or "
                      +weekly_avg_day_fhr_COMIN_input_file)
            weekly_avg_day_fhr+=12
        weekly_avg_df_list = []
        if os.path.exists(output_COMOUT_file):
            sub_util.copy_file(output_COMOUT_file, output_DATA_file)
            make_weekly_avg_output_file = False
        else:
            if len(weekly_avg_file_list) >= 12:
                if not os.path.exists(output_DATA_file):
                    make_weekly_avg_output_file = True
                else:
                    make_weekly_avg_output_file = False
                    print(f"DATA Output File exist: {output_DATA_file}")
                    if SENDCOM == 'YES' \
                            and sub_util.check_file_exists_size(
                                output_DATA_file
                            ):
                        sub_util.copy_file(output_DATA_file,
                                           output_COMOUT_file)
            else:
                print("WARNING: Need at least 12 files to create weekly average")
                make_weekly_avg_output_file = False
        if make_weekly_avg_output_file:
            print(f"DATA Output File: {output_DATA_file}")
            print(f"COMOUT Output File: {output_COMOUT_file}")
            all_weekly_avg_df = pd.DataFrame(columns=MET_MPR_column_list)
            for weekly_avg_file in weekly_avg_file_list:
                with open(weekly_avg_file, 'r') as infile:
                    input_file_header = infile.readline()
                weekly_avg_file_df = pd.read_csv(weekly_avg_file, sep=" ", skiprows=1,
                                                skipinitialspace=True, header=None,
                                                names=MET_MPR_column_list,
                                                na_filter=False, dtype=str)
                all_weekly_avg_df = pd.concat(
                    [all_weekly_avg_df, weekly_avg_file_df], ignore_index=True
                )
            for obtype in all_weekly_avg_df['OBTYPE'].unique():
                all_weekly_avg_obtype_df = all_weekly_avg_df.loc[
                    all_weekly_avg_df['OBTYPE'] == obtype
                ]
                for sid in all_weekly_avg_obtype_df['OBS_SID'].unique():
                    all_weekly_avg_obtype_sid_df = (
                        all_weekly_avg_obtype_df.loc[
                            all_weekly_avg_obtype_df['OBS_SID'] == sid
                        ]
                    )
                    for vx_mask \
                            in all_weekly_avg_obtype_sid_df['VX_MASK'].unique():
                        all_weekly_avg_obtype_sid_vx_mask_df = (
                            all_weekly_avg_obtype_sid_df.loc[
                                all_weekly_avg_obtype_sid_df['VX_MASK']\
                                == vx_mask
                            ]
                        )
                        if len(all_weekly_avg_obtype_sid_vx_mask_df) < 12:
                            continue
                        all_weekly_avg_obtype_sid_vx_mask_fcst_mean = (
                            np.array(
                                all_weekly_avg_obtype_sid_vx_mask_df['FCST']\
                                .values, dtype=float
                            ).mean()
                        )
                        all_weekly_avg_obtype_sid_vx_mask_obs_mean = (
                            np.array(
                                all_weekly_avg_obtype_sid_vx_mask_df['OBS']\
                                .values, dtype=float
                            ).mean()
                        )
                        weekly_avg_obtype_sid_vx_mask_df = pd.DataFrame.copy(
                            all_weekly_avg_obtype_sid_vx_mask_df.iloc[0,:],
                            deep=True
                        )
                        weekly_avg_obtype_sid_vx_mask_df['FCST_LEAD'] = (
                            str(weekly_avg_day_fhr_end).zfill(2)+'0000'
                        )
                        weekly_avg_obtype_sid_vx_mask_df['FCST_VALID_BEG'] = (
                            weekly_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        weekly_avg_obtype_sid_vx_mask_df['FCST_VALID_END'] = (
                            weekly_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        weekly_avg_obtype_sid_vx_mask_df['OBS_VALID_BEG'] = (
                            weekly_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        weekly_avg_obtype_sid_vx_mask_df['OBS_VALID_END'] = (
                            weekly_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        weekly_avg_obtype_sid_vx_mask_df['FCST_VAR'] = (
                            weekly_avg_obtype_sid_vx_mask_df['FCST_VAR']
                            +'_WEEKLYAVG'
                        )
                        weekly_avg_obtype_sid_vx_mask_df['OBS_VAR'] = (
                            weekly_avg_obtype_sid_vx_mask_df['OBS_VAR']
                            +'_WEEKLYAVG'
                        )
                        weekly_avg_obtype_sid_vx_mask_df['FCST'] = str(
                            all_weekly_avg_obtype_sid_vx_mask_fcst_mean
                        )
                        weekly_avg_obtype_sid_vx_mask_df['OBS'] = str(
                            all_weekly_avg_obtype_sid_vx_mask_obs_mean
                        )
                        weekly_avg_df_list.append(
                            weekly_avg_obtype_sid_vx_mask_df
                        )
            weekly_avg_df = pd.concat(
                weekly_avg_df_list, axis=1, ignore_index=True
            ).T
            weekly_avg_df.to_csv(
                output_DATA_file, header=input_file_header,
                index=None, sep=' ', mode='w'
            )
            if SENDCOM == 'YES' \
                    and sub_util.check_file_exists_size(output_DATA_file):
                sub_util.copy_file(output_DATA_file, output_COMOUT_file)
        print("")
        weekly_avg_day+=7
    valid_hr+=int(valid_hr_inc)

print("END: "+os.path.basename(__file__))
