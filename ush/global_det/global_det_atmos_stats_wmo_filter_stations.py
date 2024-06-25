#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_wmo_filter_stations.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: Filter the station information
Run By: scripts/stats/global_det/exevs_global_det_atmos_wmo_stats.sh
'''

import sys
import os
import datetime
import pandas as pd
import glob
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMIN = os.environ['COMIN']
COMOUT = os.environ['COMOUT']
SENDCOM = os.environ['SENDCOM']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
MODELNAME = os.environ['MODELNAME']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
valid_date = os.environ['valid_date']
tmp_stat_unfiltered_file = os.environ['tmp_stat_unfiltered_file']
tmp_stat_file = os.environ['tmp_stat_file']

# Read in station information
column_name_list = gda_util.get_met_line_type_cols('hold', MET_ROOT,
                                                   met_ver, 'MPR')
if gda_util.check_file_exists_size(tmp_stat_unfiltered_file):
    print(f"Reading station information from {tmp_stat_unfiltered_file}")
    station_info_df = pd.read_csv(
        tmp_stat_unfiltered_file, sep=" ", skiprows=1, skipinitialspace=True,
        keep_default_na=False, dtype='str', header=None, names=column_name_list
    )
    station_info_df = station_info_df.drop(
        station_info_df[station_info_df['OBS_ELV'] == 'NA'].index
    )
    if len(station_info_df) == 0:
        have_station_info = False
        print('NOTE: Could not read in station information from file '
              +f"{tmp_stat_unfiltered_file}")
    else:
        have_station_info = True
else:
    have_station_info = False

if have_station_info:
    print(f"Writing filtered station info to {tmp_stat_file}")
    station_info_df.to_csv(
        tmp_stat_file, index=None, sep=' ', mode='w'
    )

print("END: "+os.path.basename(__file__))
