'''
Name: global_det_atmos_headline_plots.py
Contact(s): Mallory Row
Abstract: This script is main driver for the headline score plots.
'''

import os
import sys
import logging
import datetime
import glob
import subprocess
import itertools
import shutil
import global_det_atmos_util as gda_util
from global_det_atmos_plots_specs import PlotSpecs

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
FIXevs = os.environ['FIXevs']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
evs_run_mode = os.environ['evs_run_mode']
COMINdailystats = os.environ['COMINdailystats']

# Set up directory paths
logo_dir = os.path.join(FIXevs, 'logos')
stat_base_dir = os.path.join(DATA, 'data')
logging_dir = os.path.join(DATA, 'logs')
images_dir = os.path.join(DATA, 'images')
for mkdir in [stat_base_dir, logging_dir, images_dir]:
    if not os.path.exists(mkdir):
        os.makedirs(mkdir)

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

### Headline Score Plot 1: Grid-to-Grid - Geopotential Height 500-hPa ACC Day 5 NH Last 31 days 00Z
print("Headline Score Plot 1: Grid-to-Grid - Geopotential Height 500-hPa "
      "ACC Day 5 NH Last 31 days 00Z")
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
headline1_date_info_dict = {
    'date_type': 'VALID',
    'start_date': (now - datetime.timedelta(days=headline1_ndays))\
                   .strftime('%Y%m%d'),
    'end_date': (now - datetime.timedelta(days=1)).strftime('%Y%m%d'),
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
if not os.path.exists(headline1_output_dir):
    os.makedirs(headline1_output_dir)
# Set up logging
headline1_logging_file = os.path.join(logging_dir, 'evs_'+COMPONENT+'_atmos_'
                                      +RUN+'_'+STEP+'_'+headline1_job_name
                                      +'_runon'
                                      +now.strftime('%Y%m%d%H%M%S')+'.log')
logger1 = logging.getLogger(headline1_logging_file)
logger1.setLevel(log_verbosity)
file_handler1 = logging.FileHandler(headline1_logging_file, mode='a')
file_handler1.setFormatter(log_formatter)
logger1.addHandler(file_handler1)
logger1_info = f"Log file: {headline1_logging_file}"
print(logger1_info)
logger1.info(logger1_info)
# Get model daily stat files and condense
for model_num in list(headline1_model_info_dict.keys()):
    model = headline1_model_info_dict[model_num]['name']
    obs_name = headline1_model_info_dict[model_num]['obs_name']
    stat_model_dir = os.path.join(stat_base_dir, model)
    if not os.path.exists(stat_model_dir):
        os.makedirs(stat_model_dir)
    headline1_start_date_dt = datetime.datetime.strptime(
        headline1_date_info_dict['start_date'], '%Y%m%d'
    )
    headline1_end_date_dt = datetime.datetime.strptime(
        headline1_date_info_dict['end_date'], '%Y%m%d'
    )
    date_dt = headline1_start_date_dt
    while date_dt <= headline1_end_date_dt:
        source_model_date_stat_file = os.path.join(
            COMINdailystats, model+'.'+date_dt.strftime('%Y%m%d'),
            'evs.stats.'+model+'.atmos.grid2grid.'
            +'v'+date_dt.strftime('%Y%m%d')+'.stat'
        )
        dest_model_date_stat_file = os.path.join(
            stat_model_dir,  model+'_grid2grid_v'+date_dt.strftime('%Y%m%d')
            +'.stat'
        )
        if not os.path.exists(dest_model_date_stat_file):
            if os.path.exists(source_model_date_stat_file):
                logger1.debug("Linking "+source_model_date_stat_file+" to "
                              +dest_model_date_stat_file)
                os.symlink(source_model_date_stat_file,
                           dest_model_date_stat_file)
            else:
                logger1.warning(source_model_date_stat_file+" "
                                +"DOES NOT EXIST")
        date_dt = date_dt + datetime.timedelta(days=1)
    logger1.info("Condensing model .stat files for job")
    condensed_model_stat_file = os.path.join(headline1_output_dir,
                                             model_num+'_'+model
                                             +'.stat')
    gda_util.condense_model_stat_files(logger1, stat_base_dir,
                                       condensed_model_stat_file, model,
                                       obs_name,
                                       headline1_plot_info_dict['grid'],
                                       headline1_plot_info_dict['vx_mask'],
                                       headline1_plot_info_dict['fcst_var_name'],
                                       headline1_plot_info_dict['obs_var_name'],
                                       headline1_plot_info_dict['line_type'])
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
headline1_image_name = plot_specs.get_savefig_name(
    os.path.join(headline1_output_dir, 'images'),
    headline1_plot_info_dict, headline1_date_info_dict
)
headline1_copy_image_name = os.path.join(
    images_dir,
    headline1_image_name.rpartition('/')[2].replace('evs.','evs.headline.')
)
print("Copying "+headline1_image_name+" to "+headline1_copy_image_name)
shutil.copy2(headline1_image_name, headline1_copy_image_name)
print("")

### Headline Score Plot 2:
 
print("END: "+os.path.basename(__file__))
