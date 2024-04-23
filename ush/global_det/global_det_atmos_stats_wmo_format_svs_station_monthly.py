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
if wmo_param == 'dd10m':
    print("ERROR: 10m wind direction statistics not supported in MET yet")
    sys.exit(1)

# WMO rec2 key pair values
wmo_centre = 'kwbc'
wmo_model = MODELNAME
wmo_d = f"{VDATE_dt:%Y%m}"

# Set input file paths
tmp_station_info_file_list = glob.glob(
    os.path.join(DATA, f"{VDATE_dt:%Y%m}_station_info", '*')
)

# Set output file paths
tmp_VDATE_monthly_svs_file = tmp_report_file
output_VDATE_monthly_svs_file = output_report_file

# Set wmo_verif information
if wmo_param in ['t2m', 'ff10m', 'dd10m', 'tp24']:
    wmo_verif = 'grid2obs_sfc'
    if wmo_param in ['t2m', 'dd10m']:
        wmo_sc_list = ['me', 'mae', 'rmse']
    elif wmo_param == 'ff10m':
        wmo_sc_list = ['me', 'mae', 'rmse', 'ct']
    elif wmo_param == 'tp24':
        wmo_sc_list = ['ct']
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
wmo_init_list = ['00', '12']
if wmo_verif == 'grid2obs_sfc':
    wmo_t_list = ['0', '6', '12', '18']
    if wmo_param == 'tp24':
        wmo_s_list = [str(fhr) for fhr in range(240,240+24,24)]
    else:
        wmo_s_list = [str(fhr) for fhr in \
                      [*range(0,72,6), *range(72,240+12,12)]]
time_iter_list = list(
    itertools.product(wmo_t_list, wmo_s_list)
)

# Read in station information
station_info = []
column_name_list = gda_util.get_met_line_type_cols('hold', MET_ROOT,
                                                   met_ver, 'MPR')
for station_info_file in tmp_station_info_file_list:
    station_info.append(
        pd.read_csv(station_info_file, sep=" ", skiprows=1,
                    skipinitialspace=True, keep_default_na=False, dtype='str',
                    header=None, names=column_name_list)
    )
station_info_df = pd.concat(station_info, axis=0, ignore_index=True)

# Format for WMO monthly svs
VDATE_monthly_svs_lines = []
for time_iter in time_iter_list:
    wmo_t = str(time_iter[0])
    wmo_s = str(time_iter[1])
    t_s_init_hour = (
        (VDATE_dt+datetime.timedelta(hours=int(wmo_t)))
        -datetime.timedelta(hours=int(wmo_s))
    ).strftime('%H')
    if t_s_init_hour not in wmo_init_list:
        continue
    summary_stat_file = os.path.join(
        DATA, f"{RUN}.{VDATE}", MODELNAME, VERIF_CASE,
        f"{MODELNAME}.{wmo_verif}.{VDATE_dt:%Y%m}_{wmo_t.zfill(2)}Z."
        +f"f{wmo_s}.summary.stat"
    )
    if os.path.exists(summary_stat_file):
        have_summary_stat_file = True
        summary_stat_file_df = pd.read_csv(
            summary_stat_file, sep=" ", skiprows=1, skipinitialspace=True,
            keep_default_na=False, dtype='str', header=0
       )
    else:
        print(f"NOTE: {summary_stat_file} does not exist")
        have_summary_stat_file = False
    aggregate_stat_file = os.path.join(
        DATA, f"{RUN}.{VDATE}", MODELNAME, VERIF_CASE,
        f"{MODELNAME}.{wmo_verif}.{VDATE_dt:%Y%m}_{wmo_t.zfill(2)}Z."
        +f"f{wmo_s}.aggregate.stat"
    )
    if os.path.exists(aggregate_stat_file):
        have_aggregate_stat_file = True
        aggregate_stat_file_df = pd.read_csv(
            aggregate_stat_file, sep=" ", skiprows=1, skipinitialspace=True,
            keep_default_na=False, dtype='str', header=0
       )
    else:
        print(f"NOTE: {aggregate_stat_file} does not exist")
        have_agreagate_stat_file = False
    time_station_info_df = station_info_df[
        (station_info_df['FCST_LEAD'] \
             == f"{wmo_s.zfill(2)}0000")
        & (station_info_df['FCST_VALID_BEG'].str.contains(
           f"{wmo_t.zfill(2)}0000"))
    ]
    for obs_sid in list(sorted(time_station_info_df['OBS_SID'].unique())):
        met_vx_mask = obs_sid
        wmo_st = obs_sid
        # Get observation station and model grid point information
        obs_sid_info_df = time_station_info_df[
            (time_station_info_df['OBS_SID'] == obs_sid)
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
        # Get scores for station 
        for wmo_sc in wmo_sc_list:
            if wmo_sc == 'ct':
                met_line_type = 'MCTC'
                if have_aggregate_stat_file:
                    stat_line = aggregate_stat_file_df[
                        (aggregate_stat_file_df['COL_NAME:'] == met_line_type+':')
                        & (aggregate_stat_file_df['FCST_VAR'] == met_fcst_var)
                        & (aggregate_stat_file_df['FCST_LEV'] == met_fcst_lev)
                        & (aggregate_stat_file_df['FCST_LEAD'] \
                               == f"{wmo_s.zfill(2)}0000")
                        & (aggregate_stat_file_df['VX_MASK'] == met_vx_mask)
                    ]
                    if len(stat_line) == 1:
                        have_stat_line = True
                    else:
                        have_stat_line = False
                        if len(stat_line) == 0:
                            note_msg = 'No matching stat line'
                        elif len(stat_line) > 1:
                            note_msg = 'Multiple matching stats lines'
                        print(f"NOTE: {note_msg} in "
                              +f"{aggregate_stat_file} matching "
                              +f"COL_NAME:={met_line_type}:, "
                              +f"FCST_VAR={met_fcst_var}, "
                              +f"FCST_LEV={met_fcst_lev}, "
                              +f"FCST_LEAD={wmo_s.zfill(2)}0000, "
                              +f"VX_MASK={met_vx_mask}")
                else:
                    have_stat_line = False
            else:
                if met_fcst_var == 'UGRD_VGRD':
                    met_line_type = 'VCNT'
                    if wmo_sc == 'me':
                        met_stat = 'SPEED_ERR'
                    elif wmo_sc == 'rmse':
                        met_stat = 'RMSVE'
                    elif wmo_sc == 'mae':
                        met_stat = 'SPEED_ABSERR'
                else:
                    met_stat = wmo_sc.upper()
                    met_line_type = 'CNT'
                wmo_th='na'
                if have_summary_stat_file:
                    stat_line = summary_stat_file_df[
                        (summary_stat_file_df['LINE_TYPE'] == met_line_type)
                        & (summary_stat_file_df['COLUMN'] == met_stat)
                        & (summary_stat_file_df['FCST_VAR'] == met_fcst_var)
                        & (summary_stat_file_df['FCST_LEV'] == met_fcst_lev)
                        & (summary_stat_file_df['FCST_LEAD'] \
                               == f"{wmo_s.zfill(2)}0000")
                        & (summary_stat_file_df['VX_MASK'] == met_vx_mask)
                    ]
                    if len(stat_line) == 1:
                        have_stat_line = True
                    elif len(stat_line) == 2 and met_fcst_var == 'UGRD_VGRD':
                        have_stat_line = True
                    else:
                        have_stat_line = False
                        if len(stat_line) == 0:
                            note_msg = 'No matching stat line'
                        elif len(stat_line) > 1:
                            note_msg = 'Multiple matching stats lines'
                        print(f"NOTE: {note_msg} in "
                              +f"{summary_stat_file} matching "
                              +f"LINE_TYPE={met_line_type}, "
                              +f"COLUMN={met_stat}, "
                              +f"FCST_VAR={met_fcst_var}, "
                              +f"FCST_LEV={met_fcst_lev}, "
                              +f"FCST_LEAD={wmo_s.zfill(2)}0000, "
                              +f"VX_MASK={met_vx_mask}")
                else:
                    have_stat_line = False
            if have_stat_line:
                if wmo_param == 'ff10m' and wmo_sc in ['me', 'rmse', 'mae']:
                    stat_line = stat_line[stat_line['OBS_THRESH'] == '>0']
                wmo_n = stat_line['TOTAL'].values[0]
                if wmo_sc == 'ct':
                    wmo_th = (
                        stat_line['FCST_THRESH'].values[0].replace(',', '/')\
                        .replace('>=','')
                    )
                    ct_rank = int(stat_line['N_CAT'].values[0])
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
                    +f"th={wmo_th},n={wmo_n},v={wmo_v}"
                )

# Write monthly file
with open(tmp_VDATE_monthly_svs_file) as f:
    for line in VDATE_monthly_svs_lines:
        f.write(line)

print("END: "+os.path.basename(__file__))
