'''
Name: subseasonal_stats_grid2obs_create_daily_average.py
Contact(s): Shannon Shields
Abstract: This script is used to create daily average
          data from MET point_stat MPR output
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
RUN = os.environ['RUN']
NET = os.environ['NET']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
VERIF_TYPE = os.environ['VERIF_TYPE']
job_name = os.environ['job_name']
MODEL = os.environ['MODEL']
DATE = os.environ['DATE']
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end']
valid_hr_inc = os.environ['valid_hr_inc']
fhr_end = os.environ['fhr_list'].split(',')[-1]

# Process run time agruments
if len(sys.argv) != 4:
    print("ERROR: Not given correct number of run time agruments..."
          +os.path.basename(__file__)+" VARNAME_VARLEVEL DATAROOT_FILE_FORMAT "
          +"COMIN_FILE_FORMART")
    sys.exit(1)
else:
    if '_' not in sys.argv[1]:
        print("ERROR: variable and level runtime agrument formated "
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
        daily_avg_file_list = []
        daily_avg_day_fhr_end = daily_avg_day * 24
        daily_avg_day_fhr_start = daily_avg_day_fhr_end - 12
        daily_avg_day_init = (daily_avg_valid_end
                              - datetime.timedelta(days=daily_avg_day))
        daily_avg_day_fhr = daily_avg_day_fhr_start
        output_file = os.path.join(output_dir, 'daily_avg_'
                                   +VERIF_TYPE+'_'+job_name+'_init'
                                   +daily_avg_day_init.strftime('%Y%m%d%H')
                                   +'_valid'
                                   +daily_avg_valid_start\
                                   .strftime('%Y%m%d%H')+'to'
                                   +daily_avg_valid_end\
                                   .strftime('%Y%m%d%H')+'.stat')
        if os.path.exists(output_file):
            os.remove(output_file)
        while daily_avg_day_fhr <= daily_avg_day_fhr_end:
            daily_avg_day_fhr_valid = (
                daily_avg_day_init
                + datetime.timedelta(hours=daily_avg_day_fhr)
            )
            daily_avg_day_fhr_DATAROOT_input_file = gda_util.format_filler(
                    DATAROOT_file_format, daily_avg_day_fhr_valid,
                    daily_avg_day_init,
                    str(daily_avg_day_fhr), {}
            )
            daily_avg_day_fhr_COMIN_input_file = gda_util.format_filler(
                    COMIN_file_format, daily_avg_day_fhr_valid,
                    daily_avg_day_init,
                    str(daily_avg_day_fhr), {}
            )
            if os.path.exists(daily_avg_day_fhr_COMIN_input_file):
                daily_avg_day_fhr_input_file = (
                    daily_avg_day_fhr_COMIN_input_file)
            else:
                daily_avg_day_fhr_input_file = (
                    daily_avg_day_fhr_DATAROOT_input_file
                )
            if os.path.exists(daily_avg_day_fhr_input_file):
                print("Input file for forecast hour "+str(daily_avg_day_fhr)
                      +', valid '+str(daily_avg_day_fhr_valid)
                      +', init '+str(daily_avg_day_init)+": "
                      +daily_avg_day_fhr_input_file)
                daily_avg_file_list.append(daily_avg_day_fhr_input_file)
            else:
                print("No input file for forecast hour "+str(daily_avg_day_fhr)
                      +', valid '+str(daily_avg_day_fhr_valid)
                      +', init '+str(daily_avg_day_init)+" "
                      +daily_avg_day_fhr_DATAROOT_input_file+" or "
                      +daily_avg_day_fhr_COMIN_input_file)
            daily_avg_day_fhr+=12
        daily_avg_df = pd.DataFrame(columns=MET_MPR_column_list)
        if len(daily_avg_file_list) == 2:
            print("Output File: "+output_file)
            all_daily_avg_df = pd.DataFrame(columns=MET_MPR_column_list)
            for daily_avg_file in daily_avg_file_list:
                with open(daily_avg_file, 'r') as infile:
                    input_file_header = infile.readline()
                daily_avg_file_df = pd.read_csv(daily_avg_file, sep=" ", skiprows=1,
                                                skipinitialspace=True, header=None,
                                                names=MET_MPR_column_list,
                                                na_filter=False, dtype=str)
                all_daily_avg_df = all_daily_avg_df.append(daily_avg_file_df,
                                                           ignore_index=True)
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
                        daily_avg_df = daily_avg_df.append(
                            daily_avg_obtype_sid_vx_mask_df,
                            ignore_index=True
                        )
            daily_avg_df.to_csv(
                output_file, header=input_file_header,
                index=None, sep=' ', mode='w'
            )
        else:
            print("WARNING: Need 2 files to create daily average")
        print("")
        daily_avg_day+=1
    valid_hr+=int(valid_hr_inc)

print("END: "+os.path.basename(__file__))
