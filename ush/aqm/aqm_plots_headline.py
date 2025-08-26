#!/usr/bin/env python3
'''
Name: aqm_headline_plots.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This is the driver script for creating headline plots.
Run By: scripts/plots/aqm/exevs_aqm_headline_plots.sh
'''

import os
import sys
import logging
import datetime
import glob
import itertools
import shutil
import dateutil
import aqm_util as gda_util
from aqm_plots_specs import PlotSpecs

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
obs_src_name=os.environ['obs_src_name']
fig_name_label = os.environ['fig_name_label']
linked_stat_base_dir= os.environ['linked_stat_base_dir']

# Set more specific input directory paths
daily_stats_dir = os.path.join(COMIN, 'stats', COMPONENT)
daily_stats_dir = os.path.join(DATA, 'data', RUN)

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

### Headline Score Plot 1: Grid-to-OBS - Daily MAX 8-HR AVG OZONE concentration CONUS
###                                      Last 90 days 12Z CYCLE DAY2 FCST 
print("\nHeadline Score Plot 1: Grid-to-OBS - Daily MAX 8-HR AVG OZONE concentration CONUS "
      +"Last 90 days 12Z CYCLE DAY2 FCST")
# Set fixed plot values
headline1_plot = 'time_series'
headline1_ndays = 90
headline1_model_info_dict = {
    'model1': {'name': 'aqmv70_raw',
               'plot_name': 'raw',
               'obs_name': 'AIRNOW_DAILY_V2'},
    'model2': {'name': 'aqmv70_bc',
               'plot_name': 'bc',
               'obs_name': 'AIRNOW_DAILY_V2'},
}
headline1_plot_info_dict = {
    'line_type': 'SL1L2',
    'grid': 'NA',
    'stat': 'FBAR_OBAR',
    'vx_mask': 'CONUS',
    'event_equalization': 'YES',
    'interp_method': 'BILIN',
    'interp_points': '4',
    'fcst_var_name': 'OZMAX8',
    'fcst_var_level': 'L1',
    'fcst_var_thresh': 'NA',
    'obs_var_name': 'OZONE-8HR',
    'obs_var_level': 'A8',
    'obs_var_thresh': 'NA',
    'ob_name':'AIRNOW_DAILY_V2', 
    'obs_src_name': obs_src_name,
    'fig_name_label': fig_name_label
}
now = datetime.datetime.now()
headline1_date_info_dict = {
    'date_type': 'VALID',
    'start_date': (VDATE_END_dt - datetime.timedelta(days=headline1_ndays-1))\
                   .strftime('%Y%m%d'),
    'end_date': VDATE_END_dt.strftime('%Y%m%d'),
    'valid_hr_start': '11',
    'valid_hr_end': '11',
    'valid_hr_inc': '24',
    'init_hr_start': '12',
    'init_hr_end': '12',
    'init_hr_inc': '24',
    'forecast_hour': '47',
    'forecast_day': '2',
    'fday_start': '2',
    'fday_end': '2',
    'fday_inc': '1'
}
headline1_job_name = (
    RUN+'_'+headline1_plot_info_dict['line_type']+'_'
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
headline1_logging_file = os.path.join(logging_dir, 'evs_'+COMPONENT+'_'
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
##
## rearrange aqm grid2obs aqm_raw and aqm_bc
## update aqm to aqm_raw or aqm_bc and add to staging dir
## use staging dir as source_stats_base_dir, i.e., daily_stats_dir
##
for model_num in list(headline1_model_info_dict.keys()):
    model = headline1_model_info_dict[model_num]['name']
    obs_name = headline1_model_info_dict[model_num]['obs_name']
    ## Create condense stats file for plotting based on
    ## selected criteria from linked stats files in
    ## "linked_stat_base_dir" defined in exevs_aqm_headline_plots.sh
    logger1.info("Condensing model .stat files for job")
    gda_util.condense_model_stat_files(
        logger1, linked_stat_base_dir, headline1_output_dir, model,
        obs_name, headline1_plot_info_dict['vx_mask'],
        headline1_plot_info_dict['fcst_var_name'],
        headline1_plot_info_dict['fcst_var_level'],
        headline1_plot_info_dict['obs_var_name'],
        headline1_plot_info_dict['obs_var_level'],
        headline1_plot_info_dict['line_type']
    )
# Make plot
plot_specs = PlotSpecs(logger1, headline1_plot)
import aqm_plots_time_series as gdap_ts
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

### Headline Score Plot 2: Grid-to-OBS - Daily 24-HR AVG PM2.5 concentration CONUS
###                                      Last 90 days 12Z CYCLE DAY2 FCST 
print("\nHeadline Score Plot 2: Grid-to-OBS - Daily 24-HR AVG PM2.5 concentration CONUS "
      +"Last 90 days 12Z CYCLE DAY2 FCST")
# Set fixed plot values
headline1_plot = 'time_series'
headline1_ndays = 90
headline1_model_info_dict = {
    'model1': {'name': 'aqmv70_raw',
               'plot_name': 'raw',
               'obs_name': 'AIRNOW_DAILY_V2'},
    'model2': {'name': 'aqmv70_bc',
               'plot_name': 'bc',
               'obs_name': 'AIRNOW_DAILY_V2'},
}
headline1_plot_info_dict = {
    'line_type': 'SL1L2',
    'grid': 'NA',
    'stat': 'FBAR_OBAR',
    'vx_mask': 'CONUS',
    'event_equalization': 'YES',
    'interp_method': 'BILIN',
    'interp_points': '4',
    'fcst_var_name': 'PMAVE',
    'fcst_var_level': 'A23',
    'fcst_var_thresh': 'NA',
    'obs_var_name': 'PM2.5-24hr',
    'obs_var_level': 'A24',
    'obs_var_thresh': 'NA',
    'ob_name':'AIRNOW_DAILY_V2', 
    'obs_src_name': obs_src_name,
    'fig_name_label': fig_name_label
}
now = datetime.datetime.now()
headline1_date_info_dict = {
    'date_type': 'VALID',
    'start_date': (VDATE_END_dt - datetime.timedelta(days=headline1_ndays-1))\
                   .strftime('%Y%m%d'),
    'end_date': VDATE_END_dt.strftime('%Y%m%d'),
    'valid_hr_start': '04',
    'valid_hr_end': '04',
    'valid_hr_inc': '24',
    'init_hr_start': '12',
    'init_hr_end': '12',
    'init_hr_inc': '24',
    'forecast_hour': '40',
    'forecast_day': '2',
    'fday_start': '2',
    'fday_end': '2',
    'fday_inc': '1'
}
headline1_job_name = (
    RUN+'_'+headline1_plot_info_dict['line_type']+'_'
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
headline1_logging_file = os.path.join(logging_dir, 'evs_'+COMPONENT+'_'
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
##
## rearrange aqm grid2obs aqm_raw and aqm_bc
## update aqm to aqm_raw or aqm_bc and add to staging dir
## use staging dir as source_stats_base_dir, i.e., daily_stats_dir
##
for model_num in list(headline1_model_info_dict.keys()):
    model = headline1_model_info_dict[model_num]['name']
    obs_name = headline1_model_info_dict[model_num]['obs_name']
    ## Create condense stats file for plotting based on
    ## selected criteria from linked stats files in
    ## "linked_stat_base_dir" defined in exevs_aqm_headline_plots.sh
    logger1.info("Condensing model .stat files for job")
    gda_util.condense_model_stat_files(
        logger1, linked_stat_base_dir, headline1_output_dir, model,
        obs_name, headline1_plot_info_dict['vx_mask'],
        headline1_plot_info_dict['fcst_var_name'],
        headline1_plot_info_dict['fcst_var_level'],
        headline1_plot_info_dict['obs_var_name'],
        headline1_plot_info_dict['obs_var_level'],
        headline1_plot_info_dict['line_type']
    )
# Make plot
plot_specs = PlotSpecs(logger1, headline1_plot)
import aqm_plots_time_series as gdap_ts
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


print("END: "+os.path.basename(__file__))
