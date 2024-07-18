#!/usr/bin/env python3
'''
Name: subseasonal_stats_grid2obs_create_weeks3_4_avg.py
Contact(s): Shannon Shields
Abstract: This script is run by subseasonal_stats_grid2obs_create_job_scripts.py
          in ush/subseasonal.
          This script is used to create Weeks 3-4 averages
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
W3_4START = os.environ['W3_4START']
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

# Create Weeks 3-4 average files
print("\nCreating Weeks 3-4 average files")
valid_hr = int(valid_hr_start)
while valid_hr <= int(valid_hr_end):
    weeks_avg_valid_end = datetime.datetime.strptime(DATE+str(valid_hr),
                                                     '%Y%m%d%H')
    weeks_avg_valid_start = datetime.datetime.strptime(W3_4START
                                                       +str(valid_hr),
                                                       '%Y%m%d%H')
    weeks_avg_day_end = int(fhr_end)/24
    weeks_avg_day_start = 28
    weeks_avg_day = weeks_avg_day_start
    while weeks_avg_day <= weeks_avg_day_end:
        weeks_avg_file_list = []
        weeks_avg_day_fhr_end = weeks_avg_day * 24
        weeks_avg_day_fhr_start = weeks_avg_day_fhr_end - 336
        weeks_avg_day_init = (weeks_avg_valid_end
                              - datetime.timedelta(days=weeks_avg_day))
        weeks_avg_day_fhr = weeks_avg_day_fhr_start
        output_DATA_file = os.path.join(output_dir, 'weeks3_4_avg_'
                                        +VERIF_TYPE+'_'+job_name+'_init'
                                        +weeks_avg_day_init.strftime('%Y%m%d%H')
                                        +'_valid'
                                        +weeks_avg_valid_start\
                                        .strftime('%Y%m%d%H')+'to'
                                        +weeks_avg_valid_end\
                                        .strftime('%Y%m%d%H')+'.stat')
        output_COMOUT_file = os.path.join(COMOUT, RUN+'.'+DATE, MODEL,
                                          VERIF_CASE, 'weeks3_4_avg_'
                                          +VERIF_TYPE+'_'+job_name+'_init'
                                          +weeks_avg_day_init.strftime('%Y%m%d%H')
                                          +'_valid'
                                          +weeks_avg_valid_start\
                                          .strftime('%Y%m%d%H')+'to'
                                          +weeks_avg_valid_end\
                                          .strftime('%Y%m%d%H')+'.stat')
        while weeks_avg_day_fhr <= weeks_avg_day_fhr_end:
            weeks_avg_day_fhr_valid = (
                weeks_avg_day_init
                + datetime.timedelta(hours=weeks_avg_day_fhr)
            )
            weeks_avg_day_fhr_DATAROOT_input_file = sub_util.format_filler(
                    DATAROOT_file_format, weeks_avg_day_fhr_valid,
                    weeks_avg_day_init,
                    str(weeks_avg_day_fhr), {}
            )
            weeks_avg_day_fhr_COMIN_input_file = sub_util.format_filler(
                    COMIN_file_format, weeks_avg_day_fhr_valid,
                    weeks_avg_day_init,
                    str(weeks_avg_day_fhr), {}
            )
            if os.path.exists(weeks_avg_day_fhr_COMIN_input_file):
                weeks_avg_day_fhr_input_file = (
                    weeks_avg_day_fhr_COMIN_input_file)
            else:
                weeks_avg_day_fhr_input_file = (
                    weeks_avg_day_fhr_DATAROOT_input_file
                )
            if os.path.exists(weeks_avg_day_fhr_input_file):
                print("Input file for forecast hour "+str(weeks_avg_day_fhr)
                      +', valid '+str(weeks_avg_day_fhr_valid)
                      +', init '+str(weeks_avg_day_init)+": "
                      +weeks_avg_day_fhr_input_file)
                weeks_avg_file_list.append(weeks_avg_day_fhr_input_file)
            else:
                print("No input file for forecast hour "+str(weeks_avg_day_fhr)
                      +', valid '+str(weeks_avg_day_fhr_valid)
                      +', init '+str(weeks_avg_day_init)+" "
                      +weeks_avg_day_fhr_DATAROOT_input_file+" or "
                      +weeks_avg_day_fhr_COMIN_input_file)
            weeks_avg_day_fhr+=12
        weeks_avg_df_list = []
        if os.path.exists(output_COMOUT_file):
            sub_util.copy_file(output_COMOUT_file, output_DATA_file)
            make_weeks_avg_output_file = False
        else:
            if len(weeks_avg_file_list) >= 23:
                if not os.path.exists(output_DATA_file):
                    make_weeks_avg_output_file = True
                else:
                    make_weeks_avg_output_file = False
                    print(f"DATA Output File exist: {output_DATA_file}")
                    if SENDCOM == 'YES' \
                            and sub_util.check_file_exists_size(
                                output_DATA_file
                            ):
                        sub_util.copy_file(output_DATA_file,
                                           output_COMOUT_file)
            else:
                print("WARNING: Need at least 23 files to create Weeks 3-4 average")
                make_weeks_avg_output_file = False
        if make_weeks_avg_output_file:
            print(f"DATA Output File: {output_DATA_file}")
            print(f"COMOUT Output File: {output_COMOUT_file}")
            all_weeks_avg_df = pd.DataFrame(columns=MET_MPR_column_list)
            for weeks_avg_file in weeks_avg_file_list:
                with open(weeks_avg_file, 'r') as infile:
                    input_file_header = infile.readline()
                weeks_avg_file_df = pd.read_csv(weeks_avg_file, sep=" ", skiprows=1,
                                                skipinitialspace=True, header=None,
                                                names=MET_MPR_column_list,
                                                na_filter=False, dtype=str)
                all_weeks_avg_df = pd.concat(
                    [all_weeks_avg_df, weeks_avg_file_df], ignore_index=True
                )
            for obtype in all_weeks_avg_df['OBTYPE'].unique():
                all_weeks_avg_obtype_df = all_weeks_avg_df.loc[
                    all_weeks_avg_df['OBTYPE'] == obtype
                ]
                for sid in all_weeks_avg_obtype_df['OBS_SID'].unique():
                    all_weeks_avg_obtype_sid_df = (
                        all_weeks_avg_obtype_df.loc[
                            all_weeks_avg_obtype_df['OBS_SID'] == sid
                        ]
                    )
                    for vx_mask \
                            in all_weeks_avg_obtype_sid_df['VX_MASK'].unique():
                        all_weeks_avg_obtype_sid_vx_mask_df = (
                            all_weeks_avg_obtype_sid_df.loc[
                                all_weeks_avg_obtype_sid_df['VX_MASK']\
                                == vx_mask
                            ]
                        )
                        if len(all_weeks_avg_obtype_sid_vx_mask_df) < 23:
                            continue
                        all_weeks_avg_obtype_sid_vx_mask_fcst_mean = (
                            np.array(
                                all_weeks_avg_obtype_sid_vx_mask_df['FCST']\
                                .values, dtype=float
                            ).mean()
                        )
                        all_weeks_avg_obtype_sid_vx_mask_obs_mean = (
                            np.array(
                                all_weeks_avg_obtype_sid_vx_mask_df['OBS']\
                                .values, dtype=float
                            ).mean()
                        )
                        if job_name == 'Weeks3_4Avg_Temp2m':
                            all_weeks_avg_obtype_sid_vx_mask_climo_mean = (
                                np.array(
                                    all_weeks_avg_obtype_sid_vx_mask_df['CLIMO_MEAN']\
                                    .values, dtype=float
                                ).mean()
                            )
                        weeks_avg_obtype_sid_vx_mask_df = pd.DataFrame.copy(
                            all_weeks_avg_obtype_sid_vx_mask_df.iloc[0,:],
                            deep=True
                        )
                        weeks_avg_obtype_sid_vx_mask_df['FCST_LEAD'] = (
                            str(weeks_avg_day_fhr_end).zfill(2)+'0000'
                        )
                        weeks_avg_obtype_sid_vx_mask_df['FCST_VALID_BEG'] = (
                            weeks_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        weeks_avg_obtype_sid_vx_mask_df['FCST_VALID_END'] = (
                            weeks_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        weeks_avg_obtype_sid_vx_mask_df['OBS_VALID_BEG'] = (
                            weeks_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        weeks_avg_obtype_sid_vx_mask_df['OBS_VALID_END'] = (
                            weeks_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                        )
                        weeks_avg_obtype_sid_vx_mask_df['FCST_VAR'] = (
                            weeks_avg_obtype_sid_vx_mask_df['FCST_VAR']
                            +'_WEEKS3_4AVG'
                        )
                        weeks_avg_obtype_sid_vx_mask_df['OBS_VAR'] = (
                            weeks_avg_obtype_sid_vx_mask_df['OBS_VAR']
                            +'_WEEKS3_4AVG'
                        )
                        weeks_avg_obtype_sid_vx_mask_df['FCST'] = str(
                            all_weeks_avg_obtype_sid_vx_mask_fcst_mean
                        )
                        weeks_avg_obtype_sid_vx_mask_df['OBS'] = str(
                            all_weeks_avg_obtype_sid_vx_mask_obs_mean
                        )
                        if job_name == 'Weeks3_4Avg_Temp2m':
                            weeks_avg_obtype_sid_vx_mask_df['CLIMO_MEAN'] = str(
                                all_weeks_avg_obtype_sid_vx_mask_climo_mean
                            )
                        weeks_avg_df_list.append(
                            weeks_avg_obtype_sid_vx_mask_df
                        )
            weeks_avg_df = pd.concat(
                weeks_avg_df_list, axis=1, ignore_index=True
            ).T
            weeks_avg_df.to_csv(
                output_DATA_file, header=input_file_header,
                index=None, sep=' ', mode='w'
            )
            if SENDCOM == 'YES' \
                    and sub_util.check_file_exists_size(output_DATA_file):
                sub_util.copy_file(output_DATA_file, output_COMOUT_file)
        print("")
        weeks_avg_day+=1
    valid_hr+=int(valid_hr_inc)

print("END: "+os.path.basename(__file__))
