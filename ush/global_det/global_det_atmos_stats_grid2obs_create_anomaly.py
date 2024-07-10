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
SENDCOM = os.environ['SENDCOM']
RUN = os.environ['RUN']
NET = os.environ['NET']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
VERIF_TYPE = os.environ['VERIF_TYPE']
job_name = os.environ['job_name']
MODEL = os.environ['MODEL']
DATE = os.environ['DATE']
valid_hr_start = '06'
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end']
valid_hr_inc = os.environ['valid_hr_inc']
fhr_list = os.environ['fhr_list'].split(', ')
#fhr_start = os.environ['fhr_start']
#fhr_end = os.environ['fhr_end']
#fhr_inc = os.environ['fhr_inc']

# Process run time agruments
if len(sys.argv) != 3:
    print("FATAL ERROR: Not given correct number of run time agruments..."
          +os.path.basename(__file__)+" VARNAME_VARLEVEL FILE_FORMAT")
    sys.exit(1)
else:
    if '_' not in sys.argv[1]:
        print("FATAL ERROR: variable and level runtime agrument formated "
              +"incorrectly, be sure to separate variable and level with "
              +"an underscore (_), example TMP_Z2")
        sys.exit(1)
    else:
        var_level = sys.argv[1]
        print("Using var_level = "+var_level)
    file_format = sys.argv[2]
var = var_level.split('_')[0]
level = var_level.split('_')[1]

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
    for fhr_str in fhr_list:
        fhr = int(fhr_str)
        init_date_dt = valid_date_dt - datetime.timedelta(hours=fhr)
        input_file = gda_util.format_filler(
            file_format, valid_date_dt, init_date_dt, str(fhr), {}
        )
        output_DATA_file = os.path.join(
            DATA, VERIF_CASE+'_'+STEP, 'METplus_output',
            RUN+'.'+valid_date_dt.strftime('%Y%m%d'),
            MODEL, VERIF_CASE, 'anomaly_'+VERIF_TYPE+'_'
            +job_name+'_init'+init_date_dt.strftime('%Y%m%d%H')+'_'
            +'fhr'+str(fhr).zfill(3)+'.stat'
        )
        output_COMOUT_file = os.path.join(
            COMOUT,
            RUN+'.'+valid_date_dt.strftime('%Y%m%d'),
            MODEL, VERIF_CASE, 'anomaly_'+VERIF_TYPE+'_'
            +job_name+'_init'+init_date_dt.strftime('%Y%m%d%H')+'_'
            +'fhr'+str(fhr).zfill(3)+'.stat'
        )
        if gda_util.check_file_exists_size(input_file):
            if os.path.exists(output_COMOUT_file):
                make_anomaly_output_file = False
                gda_util.copy_file(output_COMOUT_file, output_DATA_file)
            else:
                if not os.path.exists(output_DATA_file):
                    make_anomaly_output_file = True
                else:
                    make_anomaly_output_file = False
                    print(f"DATA Output File exists: {output_DATA_file}")
                    if SENDCOM == 'YES' \
                            and gda_util.check_file_size_exists(
                                output_DATA_file
                            ):
                        gda_util.copy_file(output_DATA_file,
                                           output_COMOUT_file)
        else:
            print(f"NOTE: Cannot make anomaly file {output_DATA_file} - "
                  +f"{input_file} does not exist")
            make_anomaly_output_file = False
        if make_anomaly_output_file:
            print(f"\nInput file: {input_file}")
            with open(input_file, 'r') as infile:
                input_file_header = infile.readline()
            gda_util.run_shell_command(['sed', '-i', '"s/   a//g"',
                                        input_file])
            input_file_df = pd.read_csv(input_file, sep=" ", skiprows=1,
                                        skipinitialspace=True, header=None,
                                        names=MET_MPR_column_list,
                                        na_filter=False, dtype=str)
            input_file_var_level_df = input_file_df[
                (input_file_df['FCST_VAR'] == var) & (input_file_df['FCST_LEV'] == level)
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
            output_file_df['FCST_VAR'] = var+'_ANOM'
            output_file_df['OBS_VAR'] = var+'_ANOM'
            print(f"DATA Output File: {output_DATA_file}")
            print(f"COMOUT Output File: {output_COMOUT_file}")
            output_file_df.to_csv(output_DATA_file, header=input_file_header,
                                  index=None, sep=' ', mode='w')
            if SENDCOM == 'YES' \
                    and gda_util.check_file_exists_size(output_DATA_file):
                gda_util.copy_file(output_DATA_file, output_COMOUT_file)
    valid_date_dt = valid_date_dt + datetime.timedelta(hours=int(valid_hr_inc))

print("END: "+os.path.basename(__file__))
