#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_wmo_format_rec2_domain_daily.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: Put daily stats in the WMO required format for domains
Run By: Individual job scripts
'''

import sys
import os
import itertools
import datetime
import pandas as pd
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
VDATEm1_dt = VDATE_dt - datetime.timedelta(days=1)

# Check only running for GFS
if MODELNAME != 'gfs':
    print(f"ERROR: WMO stats are only run for gfs, exit")
    sys.exit(1)

# WMO rec2 key pair values
wmo_centre = 'kwbc'
wmo_model = MODELNAME
wmo_d = VDATE
wmo_met_par_match_dict = {
    'PRMSL': 'mslp',
    'HGT': 'z',
    'TMP': 't',
    'UGRD_VGRD': 'w',
    'RH': 'r'
}

# Set input file paths
input_VDATEm1_daily_rec2_file = os.path.join(
    COMIN, STEP, COMPONENT, f"{MODELNAME}.{VDATEm1_dt:%Y%m%d}",
    tmp_report_file.rpartition('/')[2].replace(VDATE,f"{VDATEm1_dt:%Y%m%d}")
)
have_VDATEm1_daily_rec2 = os.path.exists(input_VDATEm1_daily_rec2_file)

# Set output file paths
tmp_VDATE_daily_rec2_file = tmp_report_file
output_VDATE_daily_rec2_file = output_report_file

wmo_verif_info_dict = {
    'grid2grid_upperair': {
        'wmo_ref': 'an',
        'met_obtype': f"{MODELNAME}_anl",
        'wmo_t_list': ['0', '12'],
        'wmo_s_list': range(12,240+12,12),
        'met_vx_mask_list': ['NHEM', 'SHEM', 'TROPICS',
                             'EURNAFR', 'NAMER', 'ASIA',
                             'AUSTNZ', 'NPOL', 'SPOL'],

        'stat_file_dict': {
                'GRAD': {'stat_list': ['S1'],
                         'var_list': ['PRMSL/Z0']},
                'CNT': {'stat_list': ['RMSE', 'ME', 'ANOM_CORR', 'MAE',
                                      'RMSFA', 'RMSOA', 'FSTDEV'],
                        'var_list': ['PRMSL/Z0', 'HGT/P850', 'HGT/P500',
                                     'HGT/P250', 'HGT/P100', 'TMP/P850',
                                     'TMP/P500', 'TMP/P250', 'TMP/P100',
                                     'RH/P850', 'RH/P700']},
                'VCNT': {'stat_list': ['RMSVE', 'SPEED_ERR'],
                         'var_list': ['UGRD_VGRD/P925', 'UGRD_VGRD/P850',
                                      'UGRD_VGRD/P700', 'UGRD_VGRD/P500',
                                      'UGRD_VGRD/P250', 'UGRD_VGRD/P100']}
        }
    },
    'grid2obs_upperair': {
        'wmo_ref': 'ob',
        'met_obtype': 'ADPUPA',
        'wmo_t_list': ['0', '12'],
        'wmo_s_list': range(12,240+12,12),
        'met_vx_mask_list': ['NHEM', 'SHEM', 'TROPICS',
                             'EURNAFR', 'NAMER', 'ASIA',
                             'AUSTNZ', 'NPOL', 'SPOL'],
        'stat_file_dict': {
                'CNT': {'stat_list': ['RMSE', 'ME', 'MAE'],
                        'var_list': ['HGT/P850', 'HGT/P500', 'HGT/P250',
                                     'HGT/P100', 'TMP/P850', 'TMP/P500',
                                     'TMP/P250', 'TMP/P100', 'RH/P850',
                                     'RH/P700']},
                'VCNT': {'stat_list': ['RMSVE', 'SPEED_ERR'],
                         'var_list': ['UGRD_VGRD/P925', 'UGRD_VGRD/P850',
                                      'UGRD_VGRD/P700', 'UGRD_VGRD/P500',
                                      'UGRD_VGRD/P250', 'UGRD_VGRD/P100']}
        }
    }
}

# Format for WMO daily rec2
VDATE_daily_rec2_lines = []
for wmo_verif in list(wmo_verif_info_dict.keys()):
    wmo_verif_dict = wmo_verif_info_dict[wmo_verif]
    wmo_ref = wmo_verif_dict['wmo_ref']
    met_obtype = wmo_verif_dict['met_obtype']
    wmo_t_list = wmo_verif_dict['wmo_t_list']
    wmo_s_list = wmo_verif_dict['wmo_s_list']
    met_vx_mask_list = wmo_verif_dict['met_vx_mask_list']
    stat_file_dict = wmo_verif_dict['stat_file_dict']
    stat_file_iter_list = list(
        itertools.product(wmo_t_list, wmo_s_list, list(stat_file_dict.keys()))
    )
    for stat_file_iter in stat_file_iter_list:
        wmo_t = str(stat_file_iter[0])
        wmo_s = str(stat_file_iter[1])
        met_line_type = stat_file_iter[2]
        if wmo_verif == 'grid2grid_upperair':
            met_tool = 'grid_stat'
        elif wmo_verif == 'grid2obs_upperair':
            met_tool = 'point_stat'
        stat_file = os.path.join(
            DATA, f"{RUN}.{VDATE}", MODELNAME, VERIF_CASE,
            f"{met_tool}_{wmo_verif}_{met_line_type}_"
            +f"{wmo_s.zfill(2)}0000L_{VDATE}_{wmo_t.zfill(2)}0000V.stat"
        )
        if os.path.exists(stat_file):
            stat_file_df = pd.read_csv(
                stat_file, sep=" ", skiprows=1, skipinitialspace=True,
                names = gda_util.get_met_line_type_cols('hold', MET_ROOT,
                                                        met_ver,
                                                        met_line_type),
                keep_default_na=False, dtype='str', header=None
            )
            have_stat_file = True
        else:
            print(f"NOTE: {stat_file} does not exist")
            have_stat_file = False
        met_iter_list = list(
            itertools.product(stat_file_dict[met_line_type]['var_list'],
                              met_vx_mask_list)
        )
        for met_var_level in stat_file_dict[met_line_type]['var_list']:
            if met_var_level == 'PRMSL/Z0':
                wmo_par = 'mslp'
            else:
                wmo_par = (
                    wmo_met_par_match_dict[met_var_level.split('/')[0]]
                    +met_var_level.split('/')[1][1:]+'hPa'
                )
            for met_vx_mask in met_vx_mask_list:
                wmo_dom = met_vx_mask.lower()
                if have_stat_file:
                    stat_line = stat_file_df[
                        (stat_file_df['MODEL'] == MODELNAME)
                        & (stat_file_df['FCST_LEAD'] \
                           == f"{wmo_s.zfill(2)}0000")
                        & (stat_file_df['FCST_VAR'] \
                           == met_var_level.split('/')[0])
                        & (stat_file_df['FCST_LEV'] \
                           == met_var_level.split('/')[1])
                        & (stat_file_df['OBS_VAR'] \
                           == met_var_level.split('/')[0])
                        & (stat_file_df['OBS_LEV'] \
                           == met_var_level.split('/')[1])
                        & (stat_file_df['OBTYPE'] == met_obtype)
                        & (stat_file_df['VX_MASK'] == met_vx_mask)
                        & (stat_file_df['LINE_TYPE'] == met_line_type)
                    ]
                    if len(stat_line) == 1:
                        have_stat_line = True
                    else:
                        if len(stat_line) == 0:
                            note_msg = 'No matching stat line'
                        elif len(stat_line) > 1:
                            note_msg = 'Multiple matching stat lines'
                        print(f"NOTE: {note_msg} in {stat_file} "
                              +f"matching MODEL={MODELNAME}, "
                              +f"FCST_LEAD={wmo_s.zfill(2)}0000, "
                              +f"FCST_VAR={met_var_level.split('/')[0]}, "
                              +f"FCST_LEV={met_var_level.split('/')[1]}, "
                              +f"OBS_VAR={met_var_level.split('/')[0]}, "
                              +f"OBS_LEV={met_var_level.split('/')[1]}, "
                              +f"OBTYPE={met_obtype}, VX_MASK={met_vx_mask}, "
                              +f"LINE_TYPE={met_line_type}")
                        have_stat_line = False
                else:
                    have_stat_line = False
                for met_stat in stat_file_dict[met_line_type]['stat_list']:
                    if met_line_type == 'VCNT' and met_stat == 'RMSVE':
                        wmo_sc = 'rmse'
                    elif met_line_type == 'VCNT' and met_stat == 'SPEED_ERR':
                        wmo_sc = 'me'
                    elif met_stat == 'ANOM_CORR':
                        wmo_sc = 'ccaf'
                    elif met_stat == 'RMSFA':
                        wmo_sc = 'rmsaf'
                    elif met_stat == 'RMSOA':
                        wmo_sc = 'rmsav'
                    elif met_stat == 'FSTDEV':
                        wmo_sc = 'sd'
                    else:
                        wmo_sc = met_stat.lower()
                    if have_stat_line:
                        wmo_v = str(
                            round(float(stat_line.iloc[0][met_stat]),3)
                        )
                    else:
                        wmo_v = 'nil'
                    if wmo_sc == 'sd' and str(wmo_s) == '12':
                        if have_stat_line:
                            wmo_v_sd_0 = str(
                                round(float(stat_line.iloc[0]['OSTDEV']),3)
                            )
                        else:
                            wmo_v_sd_0 = 'nil'
                        VDATE_daily_rec2_lines.append(
                            f"centre={wmo_centre},model={wmo_model},d={wmo_d},"
                            +f"ref={wmo_ref},par={wmo_par},sc={wmo_sc},"
                            +f"dom={wmo_dom},t={wmo_t},s=0,v={wmo_v_sd_0}\n"
                        )
                    VDATE_daily_rec2_lines.append(
                        f"centre={wmo_centre},model={wmo_model},d={wmo_d},"
                        +f"ref={wmo_ref},par={wmo_par},sc={wmo_sc},"
                        +f"dom={wmo_dom},t={wmo_t},s={wmo_s},v={wmo_v}\n"
                    )

# Write daily file
print(f"Writing REC2 daily domain data to {tmp_VDATE_daily_rec2_file}")
with open(tmp_VDATE_daily_rec2_file, 'w') as f:
    if have_VDATEm1_daily_rec2:
        VDATEm1_daily_rec2_lines = open(
            input_VDATEm1_daily_rec2_file, 'r'
        ).readlines()
        for line in VDATEm1_daily_rec2_lines:
            f.write(line)
    for line in VDATE_daily_rec2_lines:
        f.write(line)

print("END: "+os.path.basename(__file__))
