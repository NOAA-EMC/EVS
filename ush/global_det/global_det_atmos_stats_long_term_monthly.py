'''
Name: global_det_atmos_stats_long_term_monthly.py
Contact(s): Mallory Row
Abstract: This script generates monthly long term stats.
'''

import sys
import os
import logging
import datetime
import calendar
import glob
import subprocess
import pandas as pd
pd.plotting.deregister_matplotlib_converters()
#pd.plotting.register_matplotlib_converters()
import numpy as np
import itertools
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
FIXevs = os.environ['FIXevs']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
evs_run_mode = os.environ['evs_run_mode']
COMINdailystats = os.environ['COMINdailystats']
COMINmonthlystats = os.environ['COMINmonthlystats']
VDATEYYYY = os.environ['VDATEYYYY']
VDATEmm = os.environ['VDATEmm']

# Set up monthly directory
monthly_dir = os.path.join(DATA, 'monthly')
if not os.path.exists(monthly_dir):
    os.makedirs(monthly_dir)

# Get dates
VDATEYYYYmm_start_date_dt = datetime.datetime.strptime(
    VDATEYYYY+VDATEmm+'01', '%Y%m%d'
)
VDATEYYYYmm_end_date_dt = datetime.datetime.strptime(
    VDATEYYYY+VDATEmm
    +str(calendar.monthrange(int(VDATEYYYY), int(VDATEmm))[1]),
    '%Y%m%d'
)

# Set up MET information dictionary
met_info_dict = {
    'root': MET_ROOT,
    'version': met_ver
}

# Set logging
log_formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
    + '%(message)s',
    '%m/%d %H:%M:%S'
)
log_verbosity = 'DEBUG'
now = datetime.datetime.now()

# File header
file_header_list = [
    'SYS', 'YEAR', 'MONTH', 'DAY0', 'DAY1', 'DAY2', 'DAY3', 'DAY4',
    'DAY5', 'DAY6', 'DAY7', 'DAY8', 'DAY9', 'DAY10', 'DAY11', 'DAY12',
    'DAY13', 'DAY14', 'DAY15', 'DAY16'
]

### Do grid-to-grid stats
print(f"Doing monthly grid-to-grid stats for {VDATEYYYY} {VDATEmm}")
monthly_g2g_dir = os.path.join(monthly_dir, 'grid2grid')
monthly_logs_g2g_dir = os.path.join(monthly_dir, 'grid2grid', 'logs')
if not os.path.exists(monthly_g2g_dir):
    os.makedirs(monthly_g2g_dir)
    os.makedirs(monthly_logs_g2g_dir)
print(f"Working in {monthly_g2g_dir}")
# Set statistics information
g2g_stats_var_dict = {
    'SAL1L2/ACC': {'HGT': ['P1000', 'P700', 'P500', 'P250'],
                   'TMP': ['P850', 'P500', 'P250'],
                   'UGRD': ['P850', 'P500', 'P250'],
                   'VGRD': ['P850', 'P500', 'P250']},
    'SL1L2/ME': {'HGT': ['P1000', 'P850', 'P500', 'P200', 'P100', 'P20'],
                 'TMP': ['P1000', 'P850', 'P500', 'P200', 'P100', 'P20'],
                 'UGRD': ['P1000', 'P850', 'P500', 'P200', 'P100', 'P20'],
                 'VGRD': ['P1000', 'P850', 'P500', 'P200', 'P100', 'P20']},
    'SL1L2/RMSE': {'HGT': ['P1000', 'P850', 'P500', 'P200', 'P100', 'P20'],
                   'TMP': ['P1000', 'P850', 'P500', 'P200', 'P100', 'P20'],
                   'UGRD': ['P1000', 'P850', 'P500', 'P200', 'P100', 'P20'],
                   'VGRD': ['P1000', 'P850', 'P500', 'P200', 'P100', 'P20']},
    'VAL1L2/ACC': {'UGRD_VGRD': ['P850', 'P500', 'P250']},
    'VL1L2/ME': {'UGRD_VGRD': ['P1000', 'P850', 'P500', 'P200', 'P100', 'P20']},
    'VL1L2/RMSE': {'UGRD_VGRD': ['P1000', 'P850', 'P500', 'P200', 'P100', 'P20']}
}
# Set model information
g2g_model_info_dict = {
    'model1': {'name': 'gfs',
               'plot_name': 'gfs',
               'obs_name': 'gfs_anl'},
    'model2': {'name': 'ecmwf',
               'plot_name': 'ecmwf',
               'obs_name': 'ecmwf_anl'},
    'model3': {'name': 'ukmet',
               'plot_name': 'ukmet',
               'obs_name': 'ukmet_anl'},
    'model4': {'name': 'cmc',
               'plot_name': 'cmc',
               'obs_name': 'cmc_anl'},
    'model5': {'name': 'fnmoc',
               'plot_name': 'fnmoc',
               'obs_name': 'fnmoc_anl'},
}
# Other information
g2g_grid = 'G004'
g2g_valid_hour_list = ['00', '06', '12', '18']
g2g_vx_mask_list = ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS']
# Get daily stat files
print(f"Getting model daily stat files for {VDATEYYYY} {VDATEmm}")
YYYYmm_daily_g2g_stats_dir = os.path.join(monthly_g2g_dir,
                                          VDATEYYYY+'_'+VDATEmm+'_daily_stats')
if not os.path.exists(YYYYmm_daily_g2g_stats_dir):
    os.makedirs(YYYYmm_daily_g2g_stats_dir)
for model_num in list(g2g_model_info_dict.keys()):
    model = g2g_model_info_dict[model_num]['name']
    stat_model_dir = os.path.join(YYYYmm_daily_g2g_stats_dir, model)
    if not os.path.exists(stat_model_dir):
        os.makedirs(stat_model_dir)
    monthly_model_dir = os.path.join(monthly_g2g_dir, 'monthly_means', model)
    if not os.path.exists(monthly_model_dir):
        os.makedirs(monthly_model_dir)
    date_dt = VDATEYYYYmm_start_date_dt
    while date_dt <= VDATEYYYYmm_end_date_dt:
        source_model_date_stat_file = os.path.join(
            COMINdailystats, model+'.'+date_dt.strftime('%Y%m%d'),
            'evs.stats.'+model+'.atmos.grid2grid.'
            +'v'+date_dt.strftime('%Y%m%d')+'.stat'
        )
        dest_model_date_stat_file = os.path.join(
            stat_model_dir,  model+'_v'+date_dt.strftime('%Y%m%d')
            +'.stat'
        )
        if not os.path.exists(dest_model_date_stat_file):
            if os.path.exists(source_model_date_stat_file):
                print(f"Linking {source_model_date_stat_file} to "
                      +f"{dest_model_date_stat_file}")
                os.symlink(source_model_date_stat_file,
                           dest_model_date_stat_file)
            else:
                print(f"WARNING: {source_model_date_stat_file} DOES NOT EXIST")
        date_dt = date_dt + datetime.timedelta(days=1)
# Calculate monthly means
for line_type_stat in list(g2g_stats_var_dict.keys()):
    line_type = line_type_stat.split('/')[0]
    stat = line_type_stat.split('/')[1]
    for loop1_info in list(
        itertools.product(list(g2g_stats_var_dict[line_type_stat].keys()),
                          g2g_vx_mask_list)
    ):
        var_name = loop1_info[0]
        vx_mask = loop1_info[1]
        print(f"Working on {line_type} {stat} {var_name} {vx_mask}")
        logging_file = os.path.join(monthly_logs_g2g_dir,
                                    'evs_'+COMPONENT+'_atmos_'
                                    +RUN+'_'+STEP+'_'+line_type+'_'+stat
                                    +'_'+var_name+'_'+vx_mask+'_runon'
                                    +now.strftime('%Y%m%d%H%M%S')+'.log')
        logger = logging.getLogger(logging_file)
        logger.setLevel(log_verbosity)
        file_handler = logging.FileHandler(logging_file, mode='a')
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
        logger_info = f"Log file: {logging_file}"
        print(logger_info)
        logger.info(logger_info)
        stat_var_dir = os.path.join(monthly_g2g_dir, line_type+'_'+stat
                                    +'_'+var_name+'_'+vx_mask)
        if not os.path.exists(stat_var_dir):
            os.makedirs(stat_var_dir)
        model_num_name_list = []
        for model_num in list(g2g_model_info_dict.keys()):
            model = g2g_model_info_dict[model_num]['name']
            obs_name = g2g_model_info_dict[model_num]['obs_name']
            model_num_name_list.append(model_num+'/'+model)
            logger.debug("Condensing model .stat files for job")
            condensed_model_stat_file = os.path.join(
                 stat_var_dir, model_num+'_'+model+'.stat'
            )
            gda_util.condense_model_stat_files(
                logger, YYYYmm_daily_g2g_stats_dir,
                condensed_model_stat_file, model,
                obs_name, g2g_grid, vx_mask,
                var_name, var_name, line_type
            )
        for loop2_info in list(
                itertools.product(g2g_valid_hour_list,
                                  g2g_stats_var_dict[line_type_stat][var_name])
        ):
            valid_hour = loop2_info[0]
            var_level = loop2_info[1]
            logger.info(f"Working on valid hour {valid_hour} "
                        +f"level {var_level}")
            model_mean_stat_forecast_day_df = pd.DataFrame(
                index=model_num_name_list,
                columns=file_header_list,
                dtype=str
            )
            model_mean_stat_forecast_day_df['SYS'] = 'EVS'
            model_mean_stat_forecast_day_df['YEAR'] = VDATEYYYY
            model_mean_stat_forecast_day_df['MONTH'] = VDATEmm
            for forecast_day_header in file_header_list[3:]:
                forecast_day = int(
                    forecast_day_header.replace('DAY', '')
                )
                forecast_hour = forecast_day * 24
                valid_dates, init_dates = gda_util.get_plot_dates(
                    logger, 'VALID',
                    VDATEYYYYmm_start_date_dt.strftime('%Y%m%d'),
                    VDATEYYYYmm_end_date_dt.strftime('%Y%m%d'),
                    str(valid_hour), str(valid_hour), 24,
                    str(valid_hour), str(valid_hour), 24,
                    str(forecast_hour)
                )
                format_valid_dates = [
                    valid_dates[d].strftime('%Y%m%d_%H%M%S') \
                    for d in range(len(valid_dates))
                ]
                format_init_dates = [
                    init_dates[d].strftime('%Y%m%d_%H%M%S') \
                    for d in range(len(init_dates))
                ]
                all_model_df = gda_util.build_df(
                    logger, stat_var_dir, stat_var_dir,
                    g2g_model_info_dict, met_info_dict,
                    var_name, var_level, 'NA',
                    var_name, var_level, 'NA',
                    line_type, g2g_grid, vx_mask,
                    'NEAREST', '1',
                    'VALID', valid_dates, format_valid_dates,
                    str(forecast_hour)
                )
                logger.info(f"Calculating statstic {stat} "
                            +f"from line type {line_type} for "
                            +f"forecast day {str(forecast_day)}/"
                            +f"forecast hour {str(forecast_hour)}")
                stat_df, stat_array = gda_util.calculate_stat(
                    logger, all_model_df, line_type, stat
                )
                for model_num in list(g2g_model_info_dict.keys()):
                    model = g2g_model_info_dict[model_num]['name']
                    model_plot_name = (
                        g2g_model_info_dict[model_num]['plot_name']
                    )
                    model_month_stat_values = np.ma.masked_invalid(
                        stat_df.loc[model_num+'/'+model+'/'+model_plot_name]\
                        .values
                    )
                    model_month_stat_nvalues = (
                        len(model_month_stat_values)
                        -np.ma.count_masked(model_month_stat_values)
                    )
                    model_month_stat_mean = model_month_stat_values.mean()
                    if np.isnan(model_month_stat_mean) \
                            or np.ma.is_masked(model_month_stat_mean) \
                            or model_month_stat_nvalues < 25:
                        model_month_stat_mean = 'NA'
                    else:
                        model_month_stat_mean = str(
                            round(model_month_stat_mean,3)
                        )
                    model_mean_stat_forecast_day_df.loc[model_num+'/'+model]\
                        [forecast_day_header] = model_month_stat_mean
            for model_num in list(g2g_model_info_dict.keys()):
                model = g2g_model_info_dict[model_num]['name']
                model_file_name = ('evs_'+stat+'_'+var_name+'_'
                                   +var_level+'_'+vx_mask+'_valid'
                                   +valid_hour+'Z.txt')
                COMINmonthlystats_file = os.path.join(
                    COMINmonthlystats, model, model_file_name
                )
                DATA_file = os.path.join(
                    monthly_g2g_dir, 'monthly_means', model, model_file_name
                )
                if os.path.exists(COMINmonthlystats_file):
                    COMINmonthlystats_df = pd.read_table(
                        COMINmonthlystats_file,
                        delimiter=' ', dtype='str',
                        skipinitialspace=True,
                        keep_default_na=False
                    )
                    DATA_df = pd.concat(
                        [COMINmonthlystats_df,
                         model_mean_stat_forecast_day_df.loc[[model_num+'/'+model]]]
                    )
                    DATA_df = DATA_df.drop_duplicates(
                        subset=['YEAR', 'MONTH'], keep='last'
                    )
                    DATA_df = DATA_df.sort_values(
                        by=['YEAR', 'MONTH'], ascending = [True, True]
                    )
                    DATA_df.to_csv(
                        DATA_file, index=None, sep=' ', mode='w'
                    )
                else:
                    model_mean_stat_forecast_day_df.loc[[model_num+'/'+model]]\
                    .to_csv(
                        DATA_file, index=None, sep=' ', mode='w'
                    )

### Do grid-to-obs long term stats

print("END: "+os.path.basename(__file__))
