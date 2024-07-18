#!/usr/bin/env python3
'''
Name: global_det_atmos_headline_plots.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This is the driver script for creating headline plots.
Run By: scripts/plots/global_det/exevs_global_det_atmos_headline_plots.sh
'''

import os
import sys
import logging
import datetime
import glob
import itertools
import shutil
import dateutil
import global_det_atmos_util as gda_util
from global_det_atmos_plots_specs import PlotSpecs

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
COMIN = os.environ['COMIN']
FIXevs = os.environ['FIXevs']
VDATE_END = os.environ['VDATE_END']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
evs_run_mode = os.environ['evs_run_mode']
envir = os.environ['envir']

# Set more specific input directory paths
daily_stats_dir = os.path.join(COMIN, 'stats', COMPONENT)
yearly_stats_dir = os.path.join(COMIN, 'stats', COMPONENT, 'long_term',
                                'yearly_means')

# Set up directory paths
logo_dir = os.path.join(FIXevs, 'logos')
stat_base_dir = os.path.join(DATA, 'data')
logging_dir = os.path.join(DATA, 'logs')
images_dir = os.path.join(DATA, 'images')
for mkdir in [stat_base_dir, logging_dir, images_dir]:
    gda_util.make_dir(mkdir)

# Set up MET information dictionary
met_info_dict = {
    'root': MET_ROOT,
    'version': met_ver
}

# Set up end valid date
VDATE_END_dt = datetime.datetime.strptime(VDATE_END, '%Y%m%d')

### Headline Score Plot 1: Grid-to-Grid - Geopotential Height 500-hPa ACC Day 5 NH Last 31 days 00Z
print("\nHeadline Score Plot 1: Grid-to-Grid - Geopotential Height 500-hPa "
      +"ACC Day 5 NH Last 31 days 00Z")
# Set fixed plot values
headline1_plot = 'time_series'
headline1_ndays = 31
headline1_model_info_dict = {
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
headline1_plot_info_dict = {
    'line_type': 'SAL1L2',
    'grid': 'G004',
    'stat': 'ACC',
    'vx_mask': 'NHEM',
    'event_equalization': 'NO',
    'interp_method': 'NEAREST',
    'interp_points': '1',
    'fcst_var_name': 'HGT',
    'fcst_var_level': 'P500',
    'fcst_var_thresh': 'NA',
    'obs_var_name': 'HGT',
    'obs_var_level': 'P500',
    'obs_var_thresh': 'NA',
}
now = datetime.datetime.now()
headline1_date_info_dict = {
    'date_type': 'VALID',
    'start_date': (VDATE_END_dt - datetime.timedelta(days=headline1_ndays-1))\
                   .strftime('%Y%m%d'),
    'end_date': VDATE_END_dt.strftime('%Y%m%d'),
    'valid_hr_start': '00',
    'valid_hr_end': '00',
    'valid_hr_inc': '24',
    'init_hr_start': '00',
    'init_hr_end': '00',
    'init_hr_inc': '24',
    'forecast_hour': '120'
}
headline1_job_name = (
    'grid2grid_'+headline1_plot_info_dict['line_type']+'_'
    +headline1_plot_info_dict['stat']+'_'
    +headline1_plot_info_dict['vx_mask']+'_'
    +headline1_plot_info_dict['fcst_var_name']+'_'
    +headline1_plot_info_dict['fcst_var_level']+'_'
    +'fhr'+headline1_date_info_dict['forecast_hour']+'_'
    +headline1_plot+'_'+str(headline1_ndays)+'days_'
    +headline1_date_info_dict['valid_hr_start']+'Z'
)
# Set output
headline1_output_dir = os.path.join(DATA, headline1_job_name)
gda_util.make_dir(headline1_output_dir)
# Set up logging
now = datetime.datetime.now()
headline1_logging_file = os.path.join(logging_dir, 'evs_'+COMPONENT+'_atmos_'
                                      +RUN+'_'+STEP+'_'+headline1_job_name
                                      +'_runon'
                                      +now.strftime('%Y%m%d%H%M%S')+'.log')
logger1 = gda_util.get_logger(headline1_logging_file)
# Get model daily stat files and condense
headline1_start_date_dt = datetime.datetime.strptime(
    headline1_date_info_dict['start_date'], '%Y%m%d'
)
headline1_end_date_dt = datetime.datetime.strptime(
    headline1_date_info_dict['end_date'], '%Y%m%d'
)
for model_num in list(headline1_model_info_dict.keys()):
    model = headline1_model_info_dict[model_num]['name']
    obs_name = headline1_model_info_dict[model_num]['obs_name']
    stat_model_dir = os.path.join(stat_base_dir, model)
    gda_util.make_dir(stat_model_dir)
    gda_util.get_daily_stat_file(model, daily_stats_dir, stat_model_dir,
                                 'grid2grid', headline1_start_date_dt,
                                 headline1_end_date_dt)
    logger1.info("Condensing model .stat files for job")
    gda_util.condense_model_stat_files(
        logger1, stat_base_dir, headline1_output_dir, model,
        obs_name, headline1_plot_info_dict['vx_mask'],
        headline1_plot_info_dict['fcst_var_name'],
        headline1_plot_info_dict['fcst_var_level'],
        headline1_plot_info_dict['obs_var_name'],
        headline1_plot_info_dict['obs_var_level'],
        headline1_plot_info_dict['line_type']
    )
# Make plot
plot_specs = PlotSpecs(logger1, headline1_plot)
import global_det_atmos_plots_time_series as gdap_ts
plot_ts = gdap_ts.TimeSeries(logger1, headline1_output_dir,
                             headline1_output_dir,
                             headline1_model_info_dict,
                             headline1_date_info_dict,
                             headline1_plot_info_dict,
                             met_info_dict, logo_dir)
plot_ts.make_time_series()
# Rename and copy to main image directory
for headline1_image_name in glob.glob(
    os.path.join(headline1_output_dir, '*.png')
):
    headline1_copy_image_name = os.path.join(
        images_dir,
        headline1_image_name.rpartition('/')[2]
    )
    print("Copying "+headline1_image_name+" to "
          +headline1_copy_image_name)
    shutil.copy2(headline1_image_name, headline1_copy_image_name)

### Headline Score Plot 2: Grid-to-Obs - 2 meter Temperature ME and RMSE Days 1,3,5,10 CONUS Last 90 days 00Z
print("\nHeadline Score Plot 2: Grid-to-Obs - 2 meter Temperature  "
      +"ME and RMSE Days 1,3,5,10 CONUS Last 90 Days 00Z")
# Set fixed plot values
headline2_plot = 'time_series_multifhr'
headline2_ndays = 90
headline2_model_info_dict = {
    'model1': {'name': 'gfs',
               'plot_name': 'gfs',
               'obs_name': 'ADPSFC'}
}
headline2_plot_info_dict = {
    'line_type': 'SL1L2',
    'grid': 'G104',
    'vx_mask': 'CONUS',
    'event_equalization': 'NO',
    'interp_method': 'BILIN',
    'interp_points': '4',
    'fcst_var_name': 'TMP',
    'fcst_var_level': 'Z2',
    'fcst_var_thresh': 'NA',
    'obs_var_name': 'TMP',
    'obs_var_level': 'Z2',
    'obs_var_thresh': 'NA',
}
headline2_date_info_dict = {
    'date_type': 'VALID',
    'start_date': (VDATE_END_dt - datetime.timedelta(days=headline2_ndays-1))\
                   .strftime('%Y%m%d'),
    'end_date': VDATE_END_dt.strftime('%Y%m%d'),
    'valid_hr_start': '00',
    'valid_hr_end': '00',
    'valid_hr_inc': '24',
    'init_hr_start': '00',
    'init_hr_end': '00',
    'init_hr_inc': '24',
    'forecast_hours': ['24', '72', '120', '240']
}
# Get model daily stat files
headline2_start_date_dt = datetime.datetime.strptime(
    headline2_date_info_dict['start_date'], '%Y%m%d'
)
headline2_end_date_dt = datetime.datetime.strptime(
    headline2_date_info_dict['end_date'], '%Y%m%d'
)
for model_num in list(headline2_model_info_dict.keys()):
    model = headline2_model_info_dict[model_num]['name']
    stat_model_dir = os.path.join(stat_base_dir, model)
    gda_util.make_dir(stat_model_dir)
    gda_util.get_daily_stat_file(model, daily_stats_dir, stat_model_dir,
                                 'grid2obs', headline2_start_date_dt,
                                 headline2_end_date_dt)
# Make plot
for stat in ['ME', 'RMSE']:
    headline2_plot_info_dict['stat'] = stat
    headline2_job_name = (
        'grid2obs_'+headline2_plot_info_dict['line_type']+'_'
        +headline2_plot_info_dict['stat']+'_'
        +headline2_plot_info_dict['vx_mask']+'_'
        +headline2_plot_info_dict['fcst_var_name']+'_'
        +headline2_plot_info_dict['fcst_var_level']+'_'
        +''.join(['fhr'+f for f in headline2_date_info_dict['forecast_hours']])
        +'_'+headline2_plot+'_'+str(headline2_ndays)+'days_'
        +headline2_date_info_dict['valid_hr_start']+'Z'
    )
    # Set output
    headline2_output_dir = os.path.join(DATA, headline2_job_name)
    gda_util.make_dir(headline2_output_dir)
    # Set up logging
    now = datetime.datetime.now()
    headline2_logging_file = os.path.join(logging_dir, 'evs_'+COMPONENT+'_atmos_'
                                          +RUN+'_'+STEP+'_'+headline2_job_name
                                          +'_runon'
                                          +now.strftime('%Y%m%d%H%M%S')+'.log')
    logger2 = gda_util.get_logger(headline2_logging_file)
    # Condense model daily stat files
    for model_num in list(headline2_model_info_dict.keys()):
        model = headline2_model_info_dict[model_num]['name']
        obs_name = headline2_model_info_dict[model_num]['obs_name']
        stat_model_dir = os.path.join(stat_base_dir, model)
        logger2.info("Condensing model .stat files for job")
        gda_util.condense_model_stat_files(
            logger2, stat_base_dir, headline2_output_dir, model,
            obs_name, headline2_plot_info_dict['vx_mask'],
            headline2_plot_info_dict['fcst_var_name'],
            headline2_plot_info_dict['fcst_var_level'],
            headline2_plot_info_dict['obs_var_name'],
            headline2_plot_info_dict['obs_var_level'],
            headline2_plot_info_dict['line_type']
        )
    # Make plot
    plot_specs = PlotSpecs(logger2, headline2_plot)
    import global_det_atmos_plots_time_series_multifhr as gdap_tsmf
    plot_tsmf = gdap_tsmf.TimeSeriesMultiFhr(logger2, headline2_output_dir,
                                             headline2_output_dir,
                                             headline2_model_info_dict,
                                             headline2_date_info_dict,
                                             headline2_plot_info_dict,
                                             met_info_dict, logo_dir)
    plot_tsmf.make_time_series_multifhr()
    # Rename and copy to main image directory
    for headline2_image_name in glob.glob(
        os.path.join(headline2_output_dir, '*.png')
    ):
        headline2_copy_image_name = os.path.join(
            images_dir,
            headline2_image_name.rpartition('/')[2]
        )
        print("Copying "+headline2_image_name+" to "
              +headline2_copy_image_name)
        shutil.copy2(headline2_image_name, headline2_copy_image_name)

if evs_run_mode == 'production' and envir != 'dev':
    print("\nAll production global_det atmos headline plots produced")
else:
    print("\nMaking development global_det atmos headline plots")
    ### Headline Score Plot 3: Grid-to-Grid -
    ### Geopotential Height 500-hPa ACC Day 5 NH 00Z Annual Means
    print("\nHeadline Score Plot 3: Grid-to-Grid - Geopotential Height 500-hPa"
          +" ACC Day 5 NH 00Z Annual Means")
    headline3_stat = 'ACC'
    headline3_vx_grid = 'G004'
    headline3_vx_mask = 'NHEM'
    headline3_var_name = 'HGT'
    headline3_var_level = 'P500'
    headline3_var_thresh = 'NA'
    headline3_nbrhd = 'NA'
    headline3_forecast_day_list = ['5']
    headline3_avg_time_range = 'yearly'
    headline3_valid_hr = '00'
    headline3_model_group_dict = {'all_models': ['gfs', 'ecmwf', 'cmc',
                                                 'fnmoc', 'ukmet', 'cfs'],
                                  'gfs_ecmwf': ['gfs', 'ecmwf']}
    headline3_start_YYYY = '1984'
    headline3_end_YYYY = str(int(VDATE_END_dt.strftime('%Y'))-1)
    headline3_all_dt_list = list(
        dateutil.rrule.rrule(
            dateutil.rrule.YEARLY,
            dtstart=dateutil.parser.parse(headline3_start_YYYY+'0101T000000'),
            until=dateutil.parser.parse(headline3_end_YYYY+'0101T000000')
        )
    )
    import global_det_atmos_plots_long_term_time_series as gdap_ltts
    for headline3_model_group in list(headline3_model_group_dict.keys()):
        headline3_model_list = headline3_model_group_dict[headline3_model_group]
        print(f"Working on model group {headline3_model_group}: "
              +f"{' '.join(headline3_model_list)}")
        headline3_job_name = (
            'grid2grid_'+headline3_avg_time_range+'_'+headline3_model_group+'_'
            +headline3_stat+'_'+headline3_vx_mask+'_'+headline3_var_name+'_'
            +headline3_var_level+'_'
            +''.join(['day'+d for d in headline3_forecast_day_list])+'_'
            +headline3_valid_hr+'Z'
        )
        # Set output
        headline3_output_dir = os.path.join(DATA, headline3_job_name)
        gda_util.make_dir(headline3_output_dir)
        # Set up logging
        now = datetime.datetime.now()
        headline3_logging_file = os.path.join(
            logging_dir, 'evs_'+COMPONENT+'_atmos_'
            +RUN+'_'+STEP+'_'+headline3_job_name
            +'_runon'+now.strftime('%Y%m%d%H%M%S')+'.log'
        )
        logger3 = gda_util.get_logger(headline3_logging_file)
        plot_ltts = gdap_ltts.LongTermTimeSeries(
            logger3, yearly_stats_dir, headline3_output_dir,
            os.path.join(FIXevs, 'logos'), headline3_avg_time_range,
            headline3_all_dt_list, headline3_model_group, headline3_model_list,
            headline3_var_name, headline3_var_level, headline3_var_thresh,
            headline3_vx_grid, headline3_vx_mask, headline3_stat, headline3_nbrhd,
            headline3_forecast_day_list, ['allyears']
        )
        plot_ltts.make_long_term_time_series()
        # Rename and copy to main image directory
        for headline3_image_name in glob.glob(
            os.path.join(headline3_output_dir, 'images', '*')
        ):
            headline3_copy_image_name = os.path.join(
                images_dir,
                headline3_image_name.rpartition('/')[2]
            )
            print("Copying "+headline3_image_name+" to "
                  +headline3_copy_image_name)
            shutil.copy2(headline3_image_name, headline3_copy_image_name)
    ### Headline Score Plot 4: Grid-to-Grid
    ### - GFS Useful Forecast Days NH Annual Means
    print("\nHeadline Score Plot 4: Grid-to-Grid - "
          +"GFS Useful Forecast Days NH Annual Means")
    headline4_stat = 'ACC'
    headline4_vx_grid = 'G004'
    headline4_vx_mask = 'NHEM'
    headline4_var_name = 'HGT'
    headline4_var_level = 'P500'
    headline4_var_thresh = 'NA'
    headline4_nbrhd = 'NA'
    headline4_avg_time_range = 'yearly'
    headline4_valid_hr = '00'
    headline4_avg_time_range = 'yearly'
    headline4_valid_hr = '00'
    headline4_start_YYYY = '1989'
    headline4_end_YYYY = str(int(VDATE_END_dt.strftime('%Y'))-1)
    headline4_all_dt_list = list(
        dateutil.rrule.rrule(
            dateutil.rrule.YEARLY,
            dtstart=dateutil.parser.parse(headline4_start_YYYY+'0101T000000'),
            until=dateutil.parser.parse(headline4_end_YYYY+'0101T000000')
        )
    )
    headline4_job_name = (
        'grid2grid_'+headline4_avg_time_range+'_gfs_'
        +headline4_stat+'_'+headline4_vx_mask+'_'+headline4_var_name+'_'
        +headline4_var_level+'_useful_forecast_days_'
        +headline4_valid_hr+'Z'
    )
    # Set output
    headline4_output_dir = os.path.join(DATA, headline4_job_name)
    gda_util.make_dir(headline4_output_dir)
    # Set up logging
    now = datetime.datetime.now()
    headline4_logging_file = os.path.join(
        logging_dir, 'evs_'+COMPONENT+'_atmos_'
        +RUN+'_'+STEP+'_'+headline4_job_name
        +'_runon'+now.strftime('%Y%m%d%H%M%S')+'.log'
    )
    logger4 = gda_util.get_logger(headline4_logging_file)
    import global_det_atmos_plots_long_term_useful_forecast_days as gdap_ltufd
    plot_ltufd = gdap_ltufd.LongTermUsefulForecastDays(
        logger4, yearly_stats_dir, headline4_output_dir,
        os.path.join(FIXevs, 'logos'), headline4_avg_time_range,
        headline4_all_dt_list, 'gfs', ['gfs'], headline4_var_name,
        headline4_var_level, headline4_var_thresh, headline4_vx_grid,
        headline4_vx_mask, headline4_stat, headline4_nbrhd, ['allyears']
    )
    plot_ltufd.make_long_term_useful_forecast_days_histogram()
    # Rename and copy to main image directory
    for headline4_image_name in glob.glob(
        os.path.join(headline4_output_dir, 'images', '*')
    ):
        headline4_copy_image_name = os.path.join(
            images_dir,
            headline4_image_name.rpartition('/')[2]
        )
        print("Copying "+headline4_image_name+" to "
              +headline4_copy_image_name)
        shutil.copy2(headline4_image_name, headline4_copy_image_name)
    ### Headline Score Plot 5: Grid-to-Grid
    ### - 24 hour Precip CONUS Days 1,2,3 FSS 62km Neighborhood
    ### & ETS
    print("\nHeadline Score Plot 5: Grid-to-Grid - "
          +"GFS 24 hour Precip CONUS FSS 62km Neighborhood and ETS")
    headline5_vx_mask = 'CONUS'
    headline5_var_name = 'APCP'
    headline5_var_level = 'A24'
    headline5_forecast_day_list = ['1', '2', '3']
    headline5_avg_time_range = 'yearly'
    headline5_valid_hr = '12'
    headline5_avg_time_range = 'yearly'
    headline5_valid_hr = '12'
    headline5_stat_thresh_dict = {'FSS': ['ge10mm', 'ge25mm'],
                                  'ETS': ['ge0.25in', 'ge1in', 'ge2in', 'ge3in']}
    headline5_start_YYYY = '2002'
    headline5_end_YYYY = str(int(VDATE_END_dt.strftime('%Y'))-1)
    headline5_all_dt_list = list(
        dateutil.rrule.rrule(
            dateutil.rrule.YEARLY,
            dtstart=dateutil.parser.parse(headline5_start_YYYY+'0101T000000'),
            until=dateutil.parser.parse(headline5_end_YYYY+'0101T000000')
        )
    )
    import global_det_atmos_plots_long_term_time_series_multifhr \
        as gdap_lttsmf
    for stat in list(headline5_stat_thresh_dict.keys()):
        headline5_job_name = (
            'grid2grid_'+headline5_avg_time_range+'_gfs_'
            +stat.replace('/', '_')+'_'+headline5_vx_mask+'_'
            +headline5_var_name+'_'+headline5_var_level+'_'
            +''.join(['day'+d for d in headline5_forecast_day_list])+'_'
            +headline5_valid_hr+'Z'
        )
        # Set output
        headline5_output_dir = os.path.join(DATA, headline5_job_name)
        gda_util.make_dir(headline5_output_dir)
        # Set up logging
        now = datetime.datetime.now()
        headline5_logging_file = os.path.join(
            logging_dir, 'evs_'+COMPONENT+'_atmos_'
            +RUN+'_'+STEP+'_'+headline5_job_name
            +'_runon'+now.strftime('%Y%m%d%H%M%S')+'.log'
        )
        logger5 = gda_util.get_logger(headline5_logging_file)
        if stat == 'FSS':
            vx_grid = 'G240'
            nbrhd = 'NBRHD_SQUARE/169'
        else:
            vx_grid = 'G212'
            nbrhd = 'NA'
        for thresh in headline5_stat_thresh_dict[stat]:
            plot_lttsmf = gdap_lttsmf.LongTermTimeSeriesMultiFhr(
                logger5, yearly_stats_dir, headline5_output_dir,
                os.path.join(FIXevs, 'logos'), headline5_avg_time_range,
                headline5_all_dt_list, 'gfs', ['gfs'], headline5_var_name,
                headline5_var_level, thresh, vx_grid, headline5_vx_mask,
                stat, nbrhd, headline5_forecast_day_list, ['allyears']
            )
            plot_lttsmf.make_long_term_time_series_multifhr()
        # Rename and copy to main image directory
        for headline5_image_name in glob.glob(
            os.path.join(headline5_output_dir, 'images', '*')
        ):
            headline5_copy_image_name = os.path.join(
                images_dir,
                headline5_image_name.rpartition('/')[2]
            )
            print("Copying "+headline5_image_name+" to "
                  +headline5_copy_image_name)
            shutil.copy2(headline5_image_name, headline5_copy_image_name)


print("END: "+os.path.basename(__file__))
