'''
Name: global_det_atmos_plots_long_term.py
Contact(s): Mallory Row
Abstract: This script generates monthly and yearly long term stats plots.
'''

import sys
import os
import logging
import datetime
import dateutil
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
evs_run_mode = os.environ['evs_run_mode']
COMINmonthlystats = os.environ['COMINmonthlystats']
COMINyearlystats = os.environ['COMINyearlystats']
VDATEYYYY = os.environ['VDATEYYYY']
VDATEmm = os.environ['VDATEmm']

# Set up time ranges to do averages for
avg_time_range_list = ['monthly']
if VDATEmm == '12':
    avg_time_range_list.append('yearly')

# Definitions
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

# Set up plotting information
model_group_dict = {'all_models': ['gfs', 'ecmwf', 'cmc', 'fnmoc', 'ukmet'],
                    'gfs_ecmwf': ['ecmwf', 'gfs'],
                    'gfs_4cycles': ['gfs00Z', 'gfs06Z', 'gfs12Z', 'gfs18Z']}
plot_info_dict = {'HGT': {'level_list': ['P1000', 'P500'],
                          'vx_mask_list': ['NHEM', 'SHEM'],
                          'stat_list': ['ACC', 'ME', 'RMSE']},
                  'UGRD_VGRD': {'level_list': ['P850', 'P200'],
                                'vx_mask_list': ['TROPICS'],
                                'stat_list': ['ME', 'RMSE']}}
for avg_time_range in avg_time_range_list:
    # Set forecast days to plot
    forecast_day_list = [str(x) for x in np.arange(0,11,1)]
    # Set run lengths to plot
    run_length_list = ['allyears', 'past10years']
    # Set COMIN directory
    if avg_time_range == 'monthly':
        COMINtime_range_stats = COMINmonthlystats
    elif avg_time_range == 'yearly':
        COMINtime_range_stats = COMINyearlystats
    # Set up time range directory
    avg_time_range_dir = os.path.join(DATA, avg_time_range)
    if not os.path.exists(avg_time_range_dir):
        os.makedirs(avg_time_range_dir)
    ### Do grid-to-grid plots
    print(f"Doing {avg_time_range} grid-to-grid plots")
    avg_time_range_g2g_dir = os.path.join(avg_time_range_dir, 'grid2grid')
    avg_time_range_logs_g2g_dir = os.path.join(avg_time_range_dir,
                                               'grid2grid', 'logs')
    avg_time_range_images_g2g_dir = os.path.join(avg_time_range_dir,
                                                 'grid2grid', 'images')
    if not os.path.exists(avg_time_range_g2g_dir):
        os.makedirs(avg_time_range_g2g_dir)
        os.makedirs(avg_time_range_logs_g2g_dir)
        os.makedirs(avg_time_range_images_g2g_dir)
    print(f"Working in {avg_time_range_g2g_dir}")
    # Make plots for groupings
    for model_group in list(model_group_dict.keys()):
        model_list = model_group_dict[model_group]
        print(f"Working on model group {model_group}: "
              +f"{' '.join(model_list)}")
        now = datetime.datetime.now()
        logging_file = os.path.join(
            avg_time_range_logs_g2g_dir,
            'evs_'+COMPONENT+'_atmos_'+RUN+'_'+STEP+'_'+model_group
            +'_runon'+now.strftime('%Y%m%d%H%M%S')+'.log'
        )
        logger = get_logger(logging_file)
        for var_name in list(plot_info_dict.keys()):
            if model_group == 'gfs_4cycles':
                start_YYYYmm = '200301'
            elif model_group == 'all_models' and var_name == 'UGRD_VGRD':
                start_YYYYmm = '201001'
            else:
                start_YYYYmm = '199601'
            if avg_time_range == 'monthly':
                all_dt_list = list(
                    dateutil.rrule.rrule(
                        dateutil.rrule.MONTHLY,
                        dtstart=dateutil.parser.parse(start_YYYYmm
                                                      +'01T000000'),
                        until=dateutil.parser.parse(VDATEYYYY+VDATEmm
                                                    +'01T000000')
                    )
                )
            elif avg_time_range == 'yearly':
                all_dt_list = list(
                    dateutil.rrule.rrule(
                        dateutil.rrule.YEARLY,
                        dtstart=dateutil.parser.parse(start_YYYYmm[0:4]
                                                      +'0101T000000'),
                        until=dateutil.parser.parse(VDATEYYYY
                                                    +'0101T000000')
                    )
                )
            for plot_loop in list(
                itertools.product(plot_info_dict[var_name]['level_list'],
                                  plot_info_dict[var_name]['vx_mask_list'],
                                  plot_info_dict[var_name]['stat_list'])
            ):
                var_level = plot_loop[0]
                vx_mask = plot_loop[1]
                stat = plot_loop[2]
                logger.info(f"Working on {var_name} {var_level} {vx_mask} "
                            +f"{stat}")
                if avg_time_range == 'monthly':
                    import global_det_atmos_plots_long_term_time_series_diff \
                        as gdap_lttsd
                    plot_lttsd = gdap_lttsd.LongTermTimeSeriesDiff(
                        logger, COMINtime_range_stats, avg_time_range_g2g_dir,
                        os.path.join(FIXevs, 'logos'), avg_time_range,
                        all_dt_list, model_group, model_list, var_name,
                        var_level, vx_mask, stat, forecast_day_list,
                        run_length_list
                    )
                    plot_lttsd.make_long_term_time_series_diff()
                    import global_det_atmos_plots_long_term_lead_by_date \
                        as gdap_ltlbd
                    plot_ltlbd = gdap_ltlbd.LongTermLeadByDate(
                        logger, COMINtime_range_stats, avg_time_range_g2g_dir,
                        os.path.join(FIXevs, 'logos'), avg_time_range,
                        all_dt_list, model_group, model_list, var_name,
                        var_level, vx_mask, stat, forecast_day_list,
                        run_length_list
                    )
                    plot_ltlbd.make_long_term_lead_by_date()
                    if stat == 'ACC' and var_name == 'HGT' \
                            and model_group == 'all_models':
                        import global_det_atmos_plots_long_term_useful_forecast_days \
                            as gdap_ltufd
                        plot_ltufd = gdap_ltufd.LongTermUsefulForecastDays(
                            logger, COMINtime_range_stats,
                            avg_time_range_g2g_dir,
                            os.path.join(FIXevs, 'logos'), avg_time_range,
                            all_dt_list, model_group, model_list, var_name,
                            var_level, vx_mask, stat, forecast_day_list,
                            run_length_list
                        )
                        plot_ltufd.make_long_term_useful_forecast_days_time_series()
                elif avg_time_range == 'yearly':
                    import global_det_atmos_plots_long_term_annual_mean \
                        as gdap_ltam
                    plot_ltam = gdap_ltam.LongTermAnnualMean(
                        logger, COMINtime_range_stats, avg_time_range_g2g_dir,
                        os.path.join(FIXevs, 'logos'), avg_time_range,
                        all_dt_list, model_group, model_list, var_name,
                        var_level, vx_mask, stat, forecast_day_list,
                        run_length_list
                    )
                    plot_ltam.make_long_term_annual_mean()

print("END: "+os.path.basename(__file__))
