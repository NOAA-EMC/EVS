#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_wmo_format_svs_station_monthly.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: Put monthly stats in the WMO required format for stations
Run By: Individual job scripts
'''

import sys
import os
import itertools
import datetime
import pandas as pd
import glob
import global_det_atmos_util as gda_util
import numpy as np

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMIN = os.environ['COMIN']
SENDCOM = os.environ['SENDCOM']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
VDATE = os.environ['VDATE']
MODELNAME = os.environ['MODELNAME']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
tmp_report_file = os.environ['tmp_report_file']
output_report_file = os.environ['output_report_file']

VDATE_dt = datetime.datetime.strptime(VDATE, '%Y%m%d')

# Check only running for GFS
if MODELNAME != 'gfs':
    print(f"ERROR: WMO stats are only run for gfs, exit")
    sys.exit(1)

# Get WMO param as script argument
wmo_param = sys.argv[1]

# Get WMO s and t information
wmo_init_list = ['00', '12']
if len(sys.argv) == 4:
    wmo_t_list = [sys.argv[2]]
    wmo_s_list = [sys.argv[3]]
else:
    wmo_t_list = ['0', '3', '6', '9', '12', '15', '18', '21']
    if wmo_param == 'tp24':
        wmo_s_list = [str(fhr) for fhr in range(24,240+24,24)]
    elif wmo_param == 'tp06':
        wmo_s_list = [str(fhr) for fhr in range(6,240+6,6)]
    else:
        wmo_s_list = [str(fhr) for fhr in \
                      [*range(0,72,3), *range(72,240+6,6)]]

# WMO rec2 key pair values
wmo_centre = 'kwbc'
wmo_model = MODELNAME
wmo_d = f"{VDATE_dt:%Y%m}"

# Set input file paths
tmp_station_info_file = os.path.join(
    DATA, f"{VDATE_dt:%Y%m}_station_info",
    f"evs.stats.gfs.atmos.wmo.station_info.v{VDATE_dt:%Y%m}.stat"
)

# Set output file paths
tmp_VDATE_monthly_svs_file = tmp_report_file
output_VDATE_monthly_svs_file = output_report_file

# Set wmo_verif information
if wmo_param in ['t2m', 'ff10m', 'dd10m', 'tp24',
                 'td2m', 'rh2m', 'tcc', 'tp06']:
    wmo_verif = 'grid2obs_sfc'
    if wmo_param in ['t2m', 'dd10m', 'td2m', 'rh2m']:
        wmo_sc_dict = {
            'summary': ['me', 'mae', 'rmse']
        }
    elif wmo_param in ['ff10m', 'tcc']:
        wmo_sc_dict = {
            'summary': ['me', 'mae', 'rmse'],
            'aggregate': ['ct']
        }
    elif wmo_param in ['tp24', 'tp06']:
        wmo_sc_dict = {
            'aggregate': ['ct']
        }
else:
    print("ERROR: Unknown WMO param")
    sys.exit(1)
if wmo_param == 't2m':
    met_fcst_var = 'TMP_EC'
    met_fcst_lev = 'Z2'
elif wmo_param in ['ff10m', 'dd10m']:
    met_fcst_var = 'UGRD_VGRD'
    met_fcst_lev = 'Z10'
elif wmo_param == 'tp24':
    met_fcst_var = 'APCP'
    met_fcst_lev = 'A24'
elif wmo_param == 'tp06':
    met_fcst_var = 'APCP'
    met_fcst_lev = 'A6'
elif wmo_param == 'td2m':
    met_fcst_var = 'DPT_EC'
    met_fcst_lev = 'Z2'
elif wmo_param == 'rh2m':
    met_fcst_var = 'RH'
    met_fcst_lev = 'Z2'
elif wmo_param == 'tcc':
    met_fcst_var = 'TCDC'
    met_fcst_lev = 'L0'
time_score_iter_list = list(
    itertools.product(wmo_t_list, wmo_s_list, list(wmo_sc_dict.keys()))
)

# Read in station information
print(f"Reading station information from {tmp_station_info_file}")
column_name_list = gda_util.get_met_line_type_cols('hold', MET_ROOT,
                                                   met_ver, 'MPR')
station_info_df = pd.read_csv(
    tmp_station_info_file, sep=" ", skiprows=1, skipinitialspace=True,
    keep_default_na=False, dtype='str', header=None, names=column_name_list,
    usecols=['FCST_LEAD', 'FCST_VALID_BEG', 'FCST_VAR', 'OBS_SID',
             'OBS_LAT', 'OBS_LON', 'OBS_ELV', 'FCST']
)
if len(station_info_df) == 0:
    have_station_info = False
    print('NOTE: Could not read in station information from file '
          +tmp_station_info_file)
else:
    have_station_info = True

# Format for WMO monthly svs
VDATE_monthly_svs_lines = []
for time_score_iter in time_score_iter_list:
    # Set time info and do checks
    wmo_t = str(time_score_iter[0])
    wmo_s = str(time_score_iter[1])
    print(f"Gathering stats for {VDATE_dt:%Y%m} valid {wmo_t}Z "
          +f"forecast lead {wmo_s} for grid2obs_sfc-{wmo_param}")
    t_s_init_hour = (
        (VDATE_dt+datetime.timedelta(hours=int(wmo_t)))
        -datetime.timedelta(hours=int(wmo_s))
    ).strftime('%H')
    if t_s_init_hour not in wmo_init_list:
        continue
    if have_station_info:
        time_station_info_df = station_info_df[
            (station_info_df['FCST_LEAD'] \
                 == f"{wmo_s.zfill(2)}0000")
            & (station_info_df['FCST_VALID_BEG'].str.contains(
               f"{wmo_t.zfill(2)}0000"))
        ]
        if len(time_station_info_df) == 0:
            have_time_station_info = False
            print(f"NOTE: Could not get station information for "
                  +f"FCST_LEAD={wmo_s.zfill(2)}0000, "
                  +f"FCST_VALID_BEG=*_{wmo_t.zfill(2)}0000")
        else:
            have_time_station_info = True
    else:
        have_time_station_info = False
    # Set score info
    wmo_sc_type = str(time_score_iter[2])
    wmo_sc_list = wmo_sc_dict[wmo_sc_type]
    if wmo_sc_type == 'aggregate':
        met_line_type = 'MCTC'
    else:
        if met_fcst_var == 'UGRD_VGRD':
            met_line_type = 'VCNT'
        else:
            met_line_type = 'CNT'
    # Read in stat file and trim
    stat_file = os.path.join(
        DATA, f"{RUN}.{VDATE}", MODELNAME, VERIF_CASE,
        f"{MODELNAME}.{wmo_verif}.{VDATE_dt:%Y%m}_{wmo_t.zfill(2)}Z."
        +f"f{wmo_s}.{wmo_sc_type}.{met_line_type}.stat"
    )
    if os.path.exists(stat_file):
        print(f"Reading stats from {stat_file}")
        if wmo_sc_type == 'summary':
            stat_file_df = pd.read_csv(
                stat_file, sep=" ", skiprows=1, skipinitialspace=True,
                keep_default_na=False, dtype='str', header=0,
                usecols=['FCST_VAR', 'FCST_LEV', 'FCST_LEAD',
                         'VX_MASK', 'COL_NAME:', 'LINE_TYPE', 'COLUMN',
                         'OBS_THRESH', 'TOTAL', 'MEAN']
            )
        elif wmo_sc_type == 'aggregate':
            stat_file_df = pd.read_csv(
                stat_file, sep=" ", skiprows=1, skipinitialspace=True,
                keep_default_na=False, dtype='str', header=0
            )
        time_var_df = stat_file_df[
            (stat_file_df['FCST_VAR'] == met_fcst_var)
            & (stat_file_df['FCST_LEV'] == met_fcst_lev)
            & (stat_file_df['FCST_LEAD'] == f"{wmo_s.zfill(2)}0000")
        ]
        if len(time_var_df) == 0:
            have_time_var = False
            print(f"No matchine stat lines in {stat_file} matching "
                  +f"FCST_VAR={met_fcst_var}, FCST_LEV={met_fcst_lev}, "
                  +f"FCST_LEAD={wmo_s.zfill(2)}0000")
        else:
            have_time_var = True
    else:
        have_time_var = False
    # Get scores for stations
    if have_time_var:
        for met_vx_mask, met_vx_mask_df in time_var_df.groupby(by='VX_MASK'):
            obs_sid = met_vx_mask
            wmo_st = met_vx_mask
            # Get observation station and model grid point information
            if have_time_station_info:
                obs_sid_info_df = time_station_info_df[
                    time_station_info_df['OBS_SID'] == obs_sid
                ]
                for info in ['LAT', 'LON', 'ELV']:
                    info_df = obs_sid_info_df[
                        obs_sid_info_df['FCST_VAR'] == info
                    ]
                    for dtype in ['obs', 'model']:
                        if dtype == 'obs':
                             col_name = f"OBS_{info}"
                        else:
                            col_name = 'FCST'
                        dtype_info_values = info_df[col_name].unique()
                        dtype_info_values = dtype_info_values[dtype_info_values!='NA']
                        if len(dtype_info_values) == 1:
                            dtype_info_value = dtype_info_values[0]
                        elif len(dtype_info_values) == 0:
                            dtype_info_value = 'na'
                        else:
                            print(f"NOTE: {obs_sid} has more than 1 "
                                  +f"{info} line")
                            dtype_info_values_df = info_df[
                                info_df[col_name].isin(dtype_info_values)
                            ]
                            most_recent_date_df = dtype_info_values_df[
                                dtype_info_values_df['FCST_VALID_BEG'] == \
                                    dtype_info_values_df['FCST_VALID_BEG'].max()
                            ]
                            most_recent_date_values = (
                                most_recent_date_df[col_name].unique()
                            )
                            if len(most_recent_date_values) == 1:
                                dtype_info_value = most_recent_date_values[0]
                            else:
                                dtype_info_value = 'na'
                        if dtype_info_value != 'na':
                            dtype_info_value = (
                                '%s' % float('%.4g' % float(dtype_info_value))
                            )
                        if info == 'LAT' and dtype == 'obs':
                            wmo_lat = dtype_info_value
                        elif info == 'LAT' and dtype == 'model':
                            wmo_lam = dtype_info_value
                        elif info == 'LON' and dtype == 'obs':
                            wmo_lon = dtype_info_value
                        elif info == 'LON' and dtype == 'model':
                            wmo_lom = dtype_info_value
                        elif info == 'ELV' and dtype == 'obs':
                            wmo_se = dtype_info_value
                        elif info == 'ELV' and dtype == 'model':
                            wmo_me = dtype_info_value
            else:
                wmo_lat = 'na'
                wmo_lam = 'na'
                wmo_lon = 'na'
                wmo_lom = 'na'
                wmo_se = 'na'
                wmo_me = 'na'
            # Get scores
            for wmo_sc in wmo_sc_list:
                if wmo_sc == 'ct':
                    stat_line = met_vx_mask_df[
                        met_vx_mask_df['COL_NAME:'] == f"{met_line_type}:"
                    ]
                else:
                    if wmo_param == 'ff10m':
                        if wmo_sc == 'me':
                            met_stat = 'SPEED_ERR'
                        elif wmo_sc == 'rmse':
                            met_stat = 'RMSVE'
                        elif wmo_sc == 'mae':
                            met_stat = 'SPEED_ABSERR'
                    elif wmo_param == 'dd10m':
                        met_stat = f"DIR_{wmo_sc.upper()}"
                    else:
                        met_stat = wmo_sc.upper()
                    wmo_th='na'
                    if wmo_param == 'ff10m':
                        stat_line = met_vx_mask_df[
                            (met_vx_mask_df['LINE_TYPE'] == met_line_type)
                            & (met_vx_mask_df['COLUMN'] == met_stat)
                            & (met_vx_mask_df['OBS_THRESH'] == '>0')
                        ]
                    elif wmo_param == 'dd10m':
                        stat_line = met_vx_mask_df[
                            (met_vx_mask_df['LINE_TYPE'] == met_line_type)
                            & (met_vx_mask_df['COLUMN'] == met_stat)
                            & (met_vx_mask_df['OBS_THRESH'] == '>=3')
                        ]
                        stat_line_gt0 = met_vx_mask_df[
                            (met_vx_mask_df['LINE_TYPE'] == met_line_type)
                            & (met_vx_mask_df['COLUMN'] == met_stat)
                            & (met_vx_mask_df['OBS_THRESH'] == '>0')
                        ]
                    else:
                        stat_line = met_vx_mask_df[
                            (met_vx_mask_df['LINE_TYPE'] == met_line_type)
                            & (met_vx_mask_df['COLUMN'] == met_stat)
                        ]
                if len(stat_line) == 1:
                    have_stat_line = True
                else:
                    have_stat_line = False
                    if len(stat_line) == 0:
                        note_msg = 'No matching stat line'
                    elif len(stat_line) > 1:
                        note_msg = 'Multiple matching stats lines'
                    print(f"NOTE: {note_msg} for station {met_vx_mask} " 
                          +f"{wmo_sc}")
                if have_stat_line:
                    if wmo_param == 'dd10m':
                        wmo_n = stat_line_gt0['TOTAL'].values[0]
                    else:
                        wmo_n = stat_line['TOTAL'].values[0]
                    if wmo_sc == 'ct':
                        ct_rank = int(stat_line['N_CAT'].values[0])
                        # Need to rename tcc columns since only 2 thresholds
                        if wmo_param == 'tcc':
                            stat_line.replace('', float("NaN"), inplace=True)
                            stat_line.dropna(how='all', axis=1, inplace=True)
                            new_stat_line_cols = list(
                                stat_line.columns[
                                    :stat_line.columns.get_loc('N_CAT')+1
                                ]
                            )
                            for f in range(1,ct_rank+1,1):
                                for o in range(1,ct_rank+1,1):
                                    new_stat_line_cols.append(f"F{f}_O{o}")
                            new_stat_line_cols.append('EC_VALUE')
                            tcc_mctc_col_dict = {}
                            for col in stat_line.columns:
                                tcc_mctc_col_dict[col] = new_stat_line_cols[
                                    stat_line.columns.get_loc(col)
                                ]
                            stat_line = stat_line.rename(columns=tcc_mctc_col_dict)
                        wmo_th = (
                            stat_line['FCST_THRESH'].values[0]\
                            .replace(',', '/').replace('>=','')
                        )
                        for o in range(1,ct_rank+1,1):
                            for f in range(ct_rank,0,-1):
                                if f"F{f}_O{o}" == f"F{ct_rank}_O1":
                                    wmo_v = stat_line[f"F{f}_O{o}"].values[0]
                                else:
                                    wmo_v = (
                                        wmo_v+'/'
                                        +stat_line[f"F{f}_O{o}"].values[0]
                                    )
                    else:
                        wmo_v = float(stat_line['MEAN'].values[0])
                        wmo_v = '%s' % float('%.4g' % wmo_v)
                    VDATE_monthly_svs_lines.append(
                        f"centre={wmo_centre},model={wmo_model},d={wmo_d},"
                        +f"parm={wmo_param},t={wmo_t},s={wmo_s},st={wmo_st},"
                        +f"lat={wmo_lat},lon={wmo_lon},lam={wmo_lam},"
                        +f"lom={wmo_lom},se={wmo_se},me={wmo_me},sc={wmo_sc},"
                        +f"th={wmo_th},n={wmo_n},v={wmo_v}\n"
                    )

# Write monthly file
print(f"Writing SVS monthly station data to {tmp_VDATE_monthly_svs_file}")
with open(tmp_VDATE_monthly_svs_file, 'w') as f:
    for line in VDATE_monthly_svs_lines:
        f.write(line)

print("END: "+os.path.basename(__file__))
