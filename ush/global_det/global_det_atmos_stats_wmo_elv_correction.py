#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_wmo_elv_correction.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script is used to do the elevation correction
          for 2 meter temperature and dewpoint forecasts,
          as required by the WMO.
Run By: individual statistics job scripts generated through
        ush/global_det/global_det_atmos_stats_wmo_create_job_scripts.py
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
RUN = os.environ['RUN']
NET = os.environ['NET']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
MODELNAME = os.environ['MODELNAME']
wmo_verif = os.environ['wmo_verif']
valid_date = os.environ['valid_date']
fhr = os.environ['fhr']
tmp_fhr_stat_file = os.environ['tmp_fhr_stat_file']
tmp_fhr_elv_correction_stat_file = (
    os.environ['tmp_fhr_elv_correction_stat_file']
)

valid_date_dt = datetime.datetime.strptime(valid_date, '%Y%m%d%H')

# Set lapse rates set by WMO (K/m)
elv_correction_var_list = ['TMP/Z2', 'DPT/Z2']
tmp2m_lapse_rate = 0.0065
dpt2m_lapse_rate = 0.0012

# Set MET MPR columns
MET_MPR_column_list = gda_util.get_met_line_type_cols(
    'null', MET_ROOT, met_ver, 'MPR'
)

# Initialize data dictionary
stat_elv_correction_dict = {}
for col in MET_MPR_column_list:
    stat_elv_correction_dict[col] = []

# Do elevation correction by station
if gda_util.check_file_exists_size(tmp_fhr_stat_file):
    print(f"Reading data from {tmp_fhr_stat_file}")
    with open(tmp_fhr_stat_file, 'r') as infile:
        headers = infile.readline()
    file_df = pd.read_csv(tmp_fhr_stat_file, sep=" ", skiprows=1,
                          skipinitialspace=True, header= None,
                          names=MET_MPR_column_list,
                          na_filter=False, dtype=str)
    for sid in file_df['OBS_SID'].unique():
        sid_df = file_df[file_df['OBS_SID'] == sid]
        # Grab model elevation
        sid_model_elv_df = sid_df[sid_df['FCST_VAR'] == 'ELV']
        if len(sid_model_elv_df) == 0:
            print(f"NOTE: Cannot grab model elevation for {sid} from "
                  +f"{tmp_fhr_stat_file}, not doing elevation corrections "
                  +"for station")
        else:
            sid_model_elv = float(sid_model_elv_df.iloc[0]['FCST'])
            for var_level in elv_correction_var_list:
                var = var_level.split('/')[0]
                level = var_level.split('/')[1]
                if var_level == 'TMP/Z2':
                    var_level_lapse_rate = tmp2m_lapse_rate
                elif var_level == 'DPT/Z2':
                    var_level_lapse_rate = dpt2m_lapse_rate
                sid_var_level_df = sid_df[
                    (sid_df['FCST_VAR'] == var)
                    & (sid_df['FCST_LEV'] == level)
                    & (sid_df['FCST'] != 'NA')
                    & (sid_df['OBS_ELV'] != 'NA')
                ]
                if len(sid_var_level_df) > 0:
                    sid_var_level_fcst = float(sid_var_level_df.iloc[0]['FCST'])
                    sid_obs_elv = float(sid_var_level_df.iloc[0]['OBS_ELV'])
                    sid_var_level_fcst_elv_correction = str(
                        sid_var_level_fcst
                        +((sid_model_elv - sid_obs_elv)*var_level_lapse_rate)
                    )
                    for col in MET_MPR_column_list:
                        if col == 'FCST':
                            stat_elv_correction_dict[col].append(
                                sid_var_level_fcst_elv_correction
                            )
                        elif col == 'FCST_VAR':
                            stat_elv_correction_dict[col].append(
                                f"{sid_var_level_df.iloc[0][col]}_EC"
                            )
                        else:
                            stat_elv_correction_dict[col].append(
                                sid_var_level_df.iloc[0][col]
                            )
                            append_value = sid_var_level_df.iloc[0][col]
                else:
                    print(f"NOTE: No data found for {var_level} "
                          +f"for station {sid}")

# Make dataframe
stat_elv_correction_df = pd.DataFrame(stat_elv_correction_dict)

# Write out dataframe
print("Writing forecast value elevations to "
      +f"{tmp_fhr_elv_correction_stat_file}")
stat_elv_correction_df.to_csv(
    tmp_fhr_elv_correction_stat_file, header=headers, index=None, sep=' ',
    mode='w'
)

print("END: "+os.path.basename(__file__))
