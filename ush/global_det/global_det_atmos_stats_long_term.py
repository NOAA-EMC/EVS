#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_long_term.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This is the driver script for creating long-term stats.
Run By: scripts/stats/global_det/exevs_global_det_atmos_long_term_stats.sh
'''

import sys
import os
import logging
import datetime
import calendar
import glob
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
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
evs_run_mode = os.environ['evs_run_mode']
COMIN = os.environ['COMIN']
VDATEYYYY = os.environ['VDATEYYYY']
VDATEmm = os.environ['VDATEmm']

# Set up time ranges to do averages for
avg_time_range_list = ['monthly']
if VDATEmm == '12':
    avg_time_range_list.append('yearly')

# Set up MET information dictionary
met_info_dict = {
    'root': MET_ROOT,
    'version': met_ver
}

# Definitions
def get_daily_stat_file(model_name, source_stats_base_dir,
                        dest_model_name_stats_dir,
                        verif_case, start_date_dt, end_date_dt):
    """! Link model daily stat files
         Args:
             model_name                - name of model (string)
             source_stats_base_dir     - full path to stats/global_det
                                         source directory (string)
             dest_model_name_stats_dir - full path to model
                                         destintion directory (string)
             verif_case                - grid2grid or grid2obs (string)
             start_date_dt             - month start date (datetime obj)
             end_date_dt               - month end date (datetime obj)
         Returns:
    """
    date_dt = start_date_dt
    while date_dt <= end_date_dt:
        source_model_date_stat_file = os.path.join(
            source_stats_base_dir,
            model_name+'.'+date_dt.strftime('%Y%m%d'),
            'evs.stats.'+model_name+'.atmos.'+verif_case+'.'
            +'v'+date_dt.strftime('%Y%m%d')+'.stat'
        )
        dest_model_date_stat_file = os.path.join(
            dest_model_name_stats_dir,
            model_name+'_v'+date_dt.strftime('%Y%m%d')
            +'.stat'
        )
        if not os.path.exists(dest_model_date_stat_file):
            if gda_util.check_file_exists_size(source_model_date_stat_file):
                print(f"Linking {source_model_date_stat_file} to "
                      +f"{dest_model_date_stat_file}")
                os.symlink(source_model_date_stat_file,
                           dest_model_date_stat_file)
        date_dt = date_dt + datetime.timedelta(days=1)

def get_logger(log_file):
    """! Get logger
         Args:
             log_file - full path to log file (string)
         Returns:
             logger - logger object
    """
    log_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
        + '%(message)s',
        '%m/%d %H:%M:%S'
    )
    logger = logging.getLogger(log_file)
    logger.setLevel('DEBUG')
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    logger_info = f"Log file: {log_file}"
    print(logger_info)
    logger.info(logger_info)
    return logger

def create_avg_time_range_stat_df(logger, time_range, model_info_dict,
                                  met_info_dict, file_header_list,
                                  input_dir, output_dir,
                                  var_name, var_level, var_thresh,
                                  line_type, stat, grid, vx_mask,
                                  interp_method, interp_points,
                                  start_date_dt, end_date_dt,
                                  vhr):
    """! Create dataframe with each forecast day's average
         for all models
         Args:
             logger              - logger object
             time_range          - either monthly or yearly (string)
             model_info_dict     - dictionary of model information
                                   (strings)
             model_list          - list of model information (strings)
             met_info_dict       - dicitionary of MET information
                                   (strings)
             file_header_list    - list of output file header
                                   (strings)
             input_dir           - full path to input directory
                                   (string)
             output_dir          - full path to output directory
                                   (string)
             var_name            - value in MET column FCST/OBS_VAR
                                   (string)
             var_level           - value in MET column FCST/OBS_LEVS
                                   (string)
             var_thresh          - value in MET column FCST/OBS_THRESH
                                   (string)
             line_type           - value in MET column LINE_TYPE
                                   (string)
             stat                - statistic name (string)
             grid                - value in MET column DESC
                                   (string)
             vx_mask             - value in MET column VX_MASK
                                   (string)
             interp_method       - value in MET column INTERP_MTHD
                                   (string)
             interp_points       - value in MET column INTERP_PNTS
                                   (string)
             start_date_dt       - time range's start date (datetime)
             end_date_dt         - time range's end date (datetime)
             vhr                 - valid hour (string)
         Returns:
             time_range_stat_df  - dataframe with each
                                   forecast day's time range average
                                   for all models (strings)
    """
    model_list = []
    for model_num in list(model_info_dict.keys()):
        model_list.append(
            model_num+'/'
            +model_info_dict[model_num]['name']+'/'
            +model_info_dict[model_num]['plot_name']
        )
    time_range_stat_df = pd.DataFrame(
        index=model_list, columns=file_header_list, dtype=str
    )
    time_range_stat_df['SYS'] = 'EVS'
    time_range_stat_df['YEAR'] = start_date_dt.strftime('%Y')
    if time_range == 'monthly':
        time_range_stat_df['MONTH'] = start_date_dt.strftime('%m')
        forecast_day_header_list = file_header_list[3:]
    elif time_range == 'yearly':
        forecast_day_header_list = file_header_list[2:]
        nvalues_time_range_min = 25
    for forecast_day_header in forecast_day_header_list:
        forecast_day = int(forecast_day_header.replace('DAY', ''))
        forecast_hour = forecast_day * 24
        valid_dates, init_dates = gda_util.get_plot_dates(
            logger, 'VALID',
            start_date_dt.strftime('%Y%m%d'),
            end_date_dt.strftime('%Y%m%d'),
            str(vhr), str(vhr), 24,
            str(vhr), str(vhr), 24,
            str(forecast_hour)
        )
        format_valid_dates = [valid_dates[d].strftime('%Y%m%d_%H%M%S') \
                              for d in range(len(valid_dates))]
        format_init_dates = [init_dates[d].strftime('%Y%m%d_%H%M%S') \
                             for d in range(len(init_dates))]
        nvalues_time_range_min = round(0.75 * len(valid_dates))
        all_model_df = gda_util.build_df(
            'make_plots', logger, input_dir, output_dir,
            model_info_dict, met_info_dict,
            var_name, var_level, var_thresh,
            var_name, var_level, var_thresh,
            line_type, grid, vx_mask,
            interp_method, interp_points,
            'VALID', valid_dates, format_valid_dates,
            str(forecast_hour)
        )
        stat_df, stat_array = gda_util.calculate_stat(
            logger, all_model_df, line_type, stat
        )
        logger.info(f"Calculating average statstic {stat} "
                    +f"from line type {line_type} for "
                    +f"forecast day {str(forecast_day)}/"
                    +f"forecast hour {str(forecast_hour)}")
        for model in model_list:
            model_time_range_stat_values = np.ma.masked_invalid(
                stat_df.loc[model].values
            )
            model_time_range_stat_nvalues = (
                len(model_time_range_stat_values)
                -np.ma.count_masked(model_time_range_stat_values)
            )
            if line_type in ['CNT', 'GRAD', 'CTS', 'NBRCTS',
                             'NBRCNT', 'VCNT']:
                avg_method = 'mean'
                calc_avg_df = stat_df.loc[model]
            else:
                avg_method = 'aggregation'
                calc_avg_df = all_model_df.loc[model]
            model_forecst_day_avg = gda_util.calculate_average(
                logger, avg_method, line_type, stat, calc_avg_df
            )
            if np.isnan(model_forecst_day_avg) \
                    or np.ma.is_masked(model_forecst_day_avg) \
                    or model_time_range_stat_nvalues < nvalues_time_range_min:
                model_forecst_day_avg = 'NA'
            else:
                model_forecst_day_avg = str(round(model_forecst_day_avg,3))
            time_range_stat_df.loc[model][forecast_day_header] = (
                model_forecst_day_avg
            )
    return time_range_stat_df

def make_model_time_range_file(time_range, model_COMIN_file,
                               model_time_range_stat_df, model_DATA_file):
    """! Write model's time range average file
         Args:
             time_range                 - either monthly or yearly (string)
             model_COMIN_file           - full path to the model's
                                          time range average file in COMIN
                                          (string)
             model_time_range_stat_df   - dataframe with model's
                                          forecast day's time range
                                          average (strings)
             model_DATA_file            - full path to write the
                                          model's time range average file to
                                          (string)
         Returns:
    """
    print('Model DATA file: '+model_DATA_file)
    print('Model COMIN file: '+model_COMIN_file)
    if os.path.exists(model_COMIN_file):
        model_COMIN_df = pd.read_table(
            model_COMIN_file, delimiter=' ', dtype='str',
            skipinitialspace=True, keep_default_na=False
        )
        model_DATA_df = pd.concat([model_COMIN_df, model_time_range_stat_df])
        if time_range == 'monthly':
            subset_col_list = ['YEAR', 'MONTH']
        elif time_range == 'yearly':
            subset_col_list = ['YEAR']
        model_DATA_df = model_DATA_df.drop_duplicates(
            subset=subset_col_list, keep='last'
        )
        model_DATA_df = model_DATA_df.sort_values(
            by=subset_col_list, ascending = [True for x in subset_col_list]
        )
        model_DATA_df.to_csv(model_DATA_file, index=None, sep=' ', mode='w')
    else:
        model_time_range_stat_df.to_csv(
            model_DATA_file, index=None, sep=' ', mode='w'
        )

for avg_time_range in avg_time_range_list:
    # Set input directory
    time_range_stats_dir = os.path.join(COMIN, 'stats', COMPONENT, 'long_term',
                                        f"{avg_time_range}_means")
    # Set up time range directory
    avg_time_range_dir = os.path.join(DATA, avg_time_range)
    gda_util.make_dir(avg_time_range_dir)
    # Get time range start and end date
    if avg_time_range == 'monthly':
        avg_time_range_start_date_dt = datetime.datetime.strptime(
            VDATEYYYY+VDATEmm+'01', '%Y%m%d'
        )
        avg_time_range_end_date_dt = datetime.datetime.strptime(
            VDATEYYYY+VDATEmm
            +str(calendar.monthrange(int(VDATEYYYY), int(VDATEmm))[1]),
            '%Y%m%d'
        )
        avg_time_range_info = VDATEYYYY+' '+VDATEmm
    else:
        avg_time_range_start_date_dt = datetime.datetime.strptime(
            VDATEYYYY+'0101', '%Y%m%d'
        )
        avg_time_range_end_date_dt = datetime.datetime.strptime(
            VDATEYYYY+'1231', '%Y%m%d'
        )
        avg_time_range_info = VDATEYYYY
    ### Do grid-to-grid stats
    print(f"Doing {avg_time_range} grid-to-grid stats for "
          +f"{avg_time_range_info}")
    avg_time_range_g2g_dir = os.path.join(
        avg_time_range_dir, 'grid2grid'
    )
    avg_time_range_logs_g2g_dir = os.path.join(
        avg_time_range_dir, 'grid2grid', 'logs'
    )
    gda_util.make_dir(avg_time_range_g2g_dir)
    gda_util.make_dir(avg_time_range_logs_g2g_dir)
    print(f"Working in {avg_time_range_g2g_dir}")
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
        'model6': {'name': 'cfs',
                   'plot_name': 'cfs',
                   'obs_name': 'gfs_anl'},
    }
    # Set statistics information
    if avg_time_range == 'monthly':
        g2g_stats_var_dict = {
            'SAL1L2/ACC': {'HGT': ['P1000', 'P700', 'P500', 'P250'],
                           'TMP': ['P850', 'P500', 'P250'],
                           'UGRD': ['P850', 'P500', 'P250'],
                           'VGRD': ['P850', 'P500', 'P250']},
            'SL1L2/ME': {'HGT': ['P1000', 'P850', 'P500', 'P200', 'P100',
                                 'P20'],
                         'TMP': ['P1000', 'P850', 'P500', 'P200', 'P100',
                                 'P20'],
                         'UGRD': ['P1000', 'P850', 'P500', 'P200', 'P100',
                                  'P20'],
                         'VGRD': ['P1000', 'P850', 'P500', 'P200', 'P100',
                                  'P20']},
            'SL1L2/RMSE': {'HGT': ['P1000', 'P850', 'P500', 'P200', 'P100',
                                   'P20'],
                           'TMP': ['P1000', 'P850', 'P500', 'P200', 'P100',
                                   'P20'],
                           'UGRD': ['P1000', 'P850', 'P500', 'P200', 'P100',
                                    'P20'],
                           'VGRD': ['P1000', 'P850', 'P500', 'P200', 'P100',
                                    'P20']},
            'VAL1L2/ACC': {'UGRD_VGRD': ['P850', 'P500', 'P250']},
            'VL1L2/ME': {'UGRD_VGRD': ['P1000', 'P850', 'P500', 'P200',
                                       'P100', 'P20']},
            'VL1L2/RMSE': {'UGRD_VGRD': ['P1000', 'P850', 'P500', 'P200',
                                         'P100', 'P20']}
        }
    elif avg_time_range == 'yearly':
        g2g_stats_var_dict = {
            'SAL1L2/ACC': {'HGT': ['P1000', 'P500']},
            'SL1L2/ME': {'HGT': ['P1000', 'P500']},
            'SL1L2/RMSE': {'HGT': ['P1000','P500']},
            'VL1L2/ME': {'UGRD_VGRD': ['P850', 'P200']},
            'VL1L2/RMSE': {'UGRD_VGRD': ['P850', 'P200']}
        }
    # Other information
    g2g_grid = 'G004'
    if avg_time_range == 'monthly':
        g2g_valid_hour_list = ['00', '06', '12', '18']
        g2g_file_header_list = ['SYS', 'YEAR', 'MONTH', 'DAY0', 'DAY1',
                                'DAY2', 'DAY3', 'DAY4', 'DAY5', 'DAY6',
                                'DAY7', 'DAY8', 'DAY9', 'DAY10', 'DAY11',
                                'DAY12', 'DAY13', 'DAY14', 'DAY15', 'DAY16']
    elif avg_time_range == 'yearly':
        g2g_valid_hour_list = ['00']
        g2g_file_header_list = ['SYS', 'YEAR', 'DAY0', 'DAY1', 'DAY2',
                                'DAY3', 'DAY4', 'DAY5', 'DAY6', 'DAY7',
                                'DAY8', 'DAY9', 'DAY10', 'DAY11', 'DAY12',
                                'DAY13', 'DAY14', 'DAY15', 'DAY16']
    g2g_vx_mask_list = ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS']
    # Get daily stat files
    print(f"Getting model daily stat files for {avg_time_range_info}")
    avg_time_range_daily_g2g_stats_dir = os.path.join(
        avg_time_range_g2g_dir,
        avg_time_range_info.replace(' ','_')+'_daily_stats'
    )
    gda_util.make_dir(avg_time_range_daily_g2g_stats_dir)
    for model_num in list(g2g_model_info_dict.keys()):
        model = g2g_model_info_dict[model_num]['name']
        stat_model_dir = os.path.join(
            avg_time_range_daily_g2g_stats_dir, model
        )
        gda_util.make_dir(stat_model_dir)
        avg_time_range_model_dir = os.path.join(
            avg_time_range_g2g_dir, avg_time_range+'_means', model
        )
        gda_util.make_dir(avg_time_range_model_dir)
        get_daily_stat_file(model, os.path.join(COMIN, 'stats', COMPONENT),
                            stat_model_dir, 'grid2grid',
                            avg_time_range_start_date_dt,
                            avg_time_range_end_date_dt)
    # Calculate time range averages
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
            now = datetime.datetime.now()
            logging_file = os.path.join(
                avg_time_range_logs_g2g_dir,
                'evs_'+COMPONENT+'_atmos_'+RUN+'_'+STEP+'_'+line_type+'_'+stat
                +'_'+var_name+'_'+vx_mask+'_runon'+now.strftime('%Y%m%d%H%M%S')
                +'.log'
            )
            logger = get_logger(logging_file)
            stat_var_dir = os.path.join(
                avg_time_range_g2g_dir,
                line_type+'_'+stat+'_'+var_name+'_'+vx_mask
            )
            gda_util.make_dir(stat_var_dir)
            for model_num in list(g2g_model_info_dict.keys()):
                model = g2g_model_info_dict[model_num]['name']
                obs_name = g2g_model_info_dict[model_num]['obs_name']
                plot_name = g2g_model_info_dict[model_num]['plot_name']
                logger.debug("Condensing model .stat files for job")
                for var_level in g2g_stats_var_dict[line_type_stat][var_name]:
                    gda_util.condense_model_stat_files(
                        logger, avg_time_range_daily_g2g_stats_dir,
                        stat_var_dir, model, obs_name, vx_mask,
                        var_name, var_level, var_name, var_level, line_type
                    )
            for loop2_info in list(
                    itertools.product(g2g_valid_hour_list,
                                      g2g_stats_var_dict[line_type_stat]\
                                      [var_name])
            ):
                valid_hour = loop2_info[0]
                var_level = loop2_info[1]
                logger.info(f"Working on valid hour {valid_hour} "
                            +f"level {var_level}")
                avg_time_range_stat_df = create_avg_time_range_stat_df(
                    logger, avg_time_range, g2g_model_info_dict,
                    met_info_dict, g2g_file_header_list, stat_var_dir,
                    stat_var_dir, var_name, var_level, 'NA', line_type, stat,
                    g2g_grid, vx_mask, 'NEAREST', '1',
                    avg_time_range_start_date_dt,
                    avg_time_range_end_date_dt, valid_hour
                )
                for model_num in list(g2g_model_info_dict.keys()):
                    model = g2g_model_info_dict[model_num]['name']
                    plot_name = g2g_model_info_dict[model_num]['plot_name']
                    model_file_name = (
                        'evs_'+stat+'_'+var_name+'_'+var_level+'_'+vx_mask
                        +'_valid'+valid_hour+'Z.txt'
                    )
                    time_range_stats_file = os.path.join(
                        time_range_stats_dir, model, model_file_name
                    )
                    DATA_file = os.path.join(
                        avg_time_range_g2g_dir, avg_time_range+'_means',
                        model, model_file_name
                    )
                    make_model_time_range_file(
                        avg_time_range,
                        time_range_stats_file,
                        avg_time_range_stat_df.loc[[
                            model_num+'/'+model+'/'+plot_name
                        ]],
                        DATA_file
                    )
                # Calculate yearly GFS NHEM useful forecast day
                if avg_time_range == 'yearly' \
                        and var_name == 'HGT' \
                        and var_level == 'P500' \
                        and stat == 'ACC' \
                        and vx_mask == 'NHEM' \
                        and valid_hour == '00':
                    for model_num in list(g2g_model_info_dict.keys()):
                        model = g2g_model_info_dict[model_num]['name']
                        plot_name = g2g_model_info_dict[model_num]['plot_name']
                        if model == 'gfs':
                            gfs_avg_time_range_stat_df = (
                                avg_time_range_stat_df.loc[[
                                    model_num+'/'+model+'/'+plot_name
                                ]]
                            ).drop(columns=['SYS', 'YEAR'])
                            break
                    gfs_avg_time_range_stat_values = np.ma.masked_equal(
                         gfs_avg_time_range_stat_df.to_numpy()[0], 'NA'
                    )
                    gfs_avg_time_range_stat_values.set_fill_value(np.nan)
                    gfs_avg_time_range_stat_values = np.ma.masked_invalid(
                        gfs_avg_time_range_stat_values.filled().astype('float')
                    )
                    forecast_days = np.ma.array(
                        [float(day.replace('DAY', '')) for day in \
                         gfs_avg_time_range_stat_df.columns.tolist()],
                         mask=np.ma.getmaskarray(gfs_avg_time_range_stat_values)
                    )
                    if len(gfs_avg_time_range_stat_values.compressed()) != 0:
                        acc06_day = np.interp(
                            0.6,
                            gfs_avg_time_range_stat_values.compressed()[::-1],
                            forecast_days.compressed()[::-1],
                            left=np.nan, right=np.nan
                        )
                        acc06_day_str = str(round(acc06_day,2))
                    else:
                        acc06_day_str = 'NA'
                    acc06_day_df = pd.DataFrame(
                        {'YEAR': [VDATEYYYY], 'DAY': [acc06_day_str]}
                    )
                    model_file_name = (
                        'usefulfcstdays_'+stat+'06_'+var_name+'_'+var_level
                        +'_'+vx_mask+'_valid'+valid_hour+'Z.txt'
                    )
                    time_range_stats_file = os.path.join(
                        time_range_stats_dir, model, model_file_name
                    )
                    DATA_file = os.path.join(
                        avg_time_range_g2g_dir, avg_time_range+'_means',
                        model, model_file_name
                    )
                    make_model_time_range_file(
                        avg_time_range,
                        time_range_stats_file,
                        acc06_day_df,
                        DATA_file
                    )
    ### Do precip stats
    print(f"Doing {avg_time_range} GFS precip stats for "
          +f"{avg_time_range_info}")
    avg_time_range_precip_dir = os.path.join(
        avg_time_range_dir, 'grid2grid'
    )
    avg_time_range_logs_precip_dir = os.path.join(
        avg_time_range_dir, 'grid2grid', 'logs'
    )
    gda_util.make_dir(avg_time_range_precip_dir)
    gda_util.make_dir(avg_time_range_logs_precip_dir)
    print(f"Working in {avg_time_range_precip_dir}")
    # Set model information
    precip_model_info_dict = {
        'model1': {'name': 'gfs',
                   'plot_name': 'gfs',
                   'obs_name': '24hrCCPA'},
    }
    # Set statistics information
    precip_stats_var_dict = {
        'CTC/ETS/G212/1':  {'APCP/A24': ['0.25in', '1in', '2in', '3in']},
        'NBRCNT/FSS/G240/169':  {'APCP/A24': ['10mm', '25mm']},
    }
    # Other information
    precip_valid_hour_list = ['12']
    precip_vx_mask_list = ['CONUS']
    if avg_time_range == 'monthly':
        precip_file_header_list = ['SYS', 'YEAR', 'MONTH', 'DAY1', 'DAY2',
                                   'DAY3', 'DAY4', 'DAY5', 'DAY6', 'DAY7',
                                   'DAY8', 'DAY9', 'DAY10']
    elif avg_time_range == 'yearly':
        precip_file_header_list = ['SYS', 'YEAR', 'DAY1', 'DAY2', 'DAY3',
                                   'DAY4', 'DAY5', 'DAY6', 'DAY7', 'DAY8',
                                   'DAY9', 'DAY10']
    # Get daily stat files
    print(f"Getting model daily stat files for {avg_time_range_info}")
    avg_time_range_daily_precip_stats_dir = os.path.join(
        avg_time_range_precip_dir,
        avg_time_range_info.replace(' ','_')+'_daily_stats'
    )
    gda_util.make_dir(avg_time_range_daily_precip_stats_dir)
    for model_num in list(precip_model_info_dict.keys()):
        model = precip_model_info_dict[model_num]['name']
        obs_name = precip_model_info_dict[model_num]['obs_name']
        plot_name = precip_model_info_dict[model_num]['plot_name']
        stat_model_dir = os.path.join(
            avg_time_range_daily_precip_stats_dir, model
        )
        gda_util.make_dir(stat_model_dir)
        avg_time_range_model_dir = os.path.join(
            avg_time_range_precip_dir, avg_time_range+'_means', model
        )
        gda_util.make_dir(avg_time_range_model_dir)
        get_daily_stat_file(model, os.path.join(COMIN, 'stats', COMPONENT),
                            stat_model_dir, 'grid2grid',
                            avg_time_range_start_date_dt,
                            avg_time_range_end_date_dt)
    # Calculate time range averages
    for line_type_stat_grid_nbrhd in list(precip_stats_var_dict.keys()):
        line_type = line_type_stat_grid_nbrhd.split('/')[0]
        stat = line_type_stat_grid_nbrhd.split('/')[1]
        grid = line_type_stat_grid_nbrhd.split('/')[2]
        nbrhd = line_type_stat_grid_nbrhd.split('/')[3]
        for loop1_info in list(
            itertools.product(
                list(precip_stats_var_dict[line_type_stat_grid_nbrhd].keys()),
                     precip_vx_mask_list)
        ):
            var_name = loop1_info[0].split('/')[0]
            accum = loop1_info[0].split('/')[1]
            vx_mask = loop1_info[1]
            print(f"Working on {line_type} {stat} {var_name} {vx_mask}")
            now = datetime.datetime.now()
            logging_file = os.path.join(
                avg_time_range_logs_precip_dir,
                'evs_'+COMPONENT+'_atmos_'+RUN+'_'+STEP+'_'+line_type+'_'+stat
                +'_'+var_name+'_'+accum+'_'+grid+'_'+vx_mask+'_runon'
                +now.strftime('%Y%m%d%H%M%S')+'.log'
            )
            logger = get_logger(logging_file)
            stat_var_dir = os.path.join(
                avg_time_range_precip_dir, line_type+'_'+stat+'_'+var_name+'_'
                +accum+'_'+vx_mask
            )
            gda_util.make_dir(stat_var_dir)
            for model_num in list(precip_model_info_dict.keys()):
                model = precip_model_info_dict[model_num]['name']
                logger.debug("Condensing model .stat files for job")
                gda_util.condense_model_stat_files(
                    logger, avg_time_range_daily_precip_stats_dir,
                    stat_var_dir, model, obs_name, vx_mask,
                    var_name, 'A24', var_name, 'A24', line_type
                )
            for loop2_info in list(
                itertools.product(precip_valid_hour_list,
                                  precip_stats_var_dict\
                                  [line_type_stat_grid_nbrhd][loop1_info[0]])
            ):
                valid_hour = loop2_info[0]
                var_thresh = loop2_info[1]
                if 'in' in var_thresh:
                    var_thresh_mm = str(
                        float(var_thresh.replace('in', ''))*25.4
                    )+'mm'
                else:
                    var_thresh_mm = var_thresh
                logger.info(f"Working on valid hour {valid_hour} "
                            +f"threshold {var_thresh}")
                if stat == 'FSS':
                    interp_method = 'NBRHD_SQUARE'
                else:
                    interp_method = 'NEAREST'
                avg_time_range_stat_df = create_avg_time_range_stat_df(
                    logger, avg_time_range, precip_model_info_dict,
                    met_info_dict, precip_file_header_list,
                    stat_var_dir, stat_var_dir, var_name, accum,
                    'ge'+var_thresh_mm.replace('mm', ''), line_type, stat,
                    grid, vx_mask, interp_method, nbrhd,
                    avg_time_range_start_date_dt, avg_time_range_end_date_dt,
                    valid_hour
                )
                for model_num in list(precip_model_info_dict.keys()):
                    model = precip_model_info_dict[model_num]['name']
                    plot_name = precip_model_info_dict[model_num]['plot_name']
                    if stat == 'FSS':
                        model_file_name = (
                            'evs_'+stat+'_'+var_thresh.replace('.','p')+'_'
                            +interp_method+nbrhd+'_'+var_name+'_'+accum+'_'
                            +grid+'_'+vx_mask+'_valid'+valid_hour+'Z.txt'
                        )
                    else:
                        model_file_name = (
                            'evs_'+stat+'_'+var_thresh.replace('.','p')+'_'
                            +var_name+'_'+accum+'_'+grid+'_'+vx_mask+'_valid'
                            +valid_hour+'Z.txt'
                        )
                    time_range_stats_file = os.path.join(
                        time_range_stats_dir, model, model_file_name
                    )
                    DATA_file = os.path.join(
                        avg_time_range_precip_dir, avg_time_range+'_means',
                        model, model_file_name
                    )
                    make_model_time_range_file(
                        avg_time_range,
                        time_range_stats_file,
                        avg_time_range_stat_df.loc[[
                            model_num+'/'+model+'/'+plot_name
                        ]],
                        DATA_file
                    )

print("END: "+os.path.basename(__file__))
