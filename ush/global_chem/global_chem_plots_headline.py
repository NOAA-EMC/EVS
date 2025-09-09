#!/usr/bin/env python3
'''
Name: global_chem_plots_headline.py
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This is the driver script for creating headline plots.
Run By: scripts/plots/exevs_global_chem_headline_grid2obs_plots.sh
'''

import os
import sys
import logging
import datetime
import glob
import itertools
import shutil
import dateutil
import global_chem_atmos_util as gda_util
from global_chem_atmos_plots_specs import PlotSpecs

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
fig_name_label = os.environ['fig_name_label']
num_obs_type = os.environ['num_obs_type']
num_obs_src = os.environ['num_obs_src']
num_plot_mdl = os.environ['num_plot_mdl']
num_plot_name = os.environ['num_plot_name']
input_obstype_list= os.environ['plot_obstype_list']
input_obssrc_list= os.environ['plot_obssrc_list']
input_model_list= os.environ['plot_model_list']
input_plotname_list= os.environ['plot_plotname_list']

# Read in obs type names from `input_obstype_list`
input_obs_types = []
if input_obstype_list:
    input_obs_types = input_obstype_list.split(',')
    print(f"Successfully read {len(input_obs_types)} variables.")
    print(f"The input_obs_types are: {input_obs_types}")
else:
    print(f"No environment variable input_obstype_list was found.")

# Read in obs src names from `input_obssrc_list`
input_obs_srcs = []
if input_obssrc_list:
    input_obs_srcs = input_obssrc_list.split(',')
    print(f"Successfully read {len(input_obs_srcs)} variables.")
    print(f"The input_obs_srcs are: {input_obs_srcs}")
else:
    print(f"No environment variable input_obssrc_list was found.")

# Read in model names from `input_model_list`
input_model_names = []
if input_model_list:
    input_model_names = input_model_list.split(',')
    print(f"Successfully read {len(input_model_names)} variables.")
    print(f"The input_model_names are: {input_model_names}")
else:
    print(f"No environment variable input_model_list was found.")

# Read in plot names from `input_plotname_list`
input_plot_names = []
if input_plotname_list:
    input_plot_names = input_plotname_list.split(',')
    print(f"Successfully read {len(input_plot_names)} variables.")
    print(f"The input_plot_names are: {input_plot_names}")
else:
    print(f"No environment variable input_plotname_list was found.")

# Set more specific input directory paths within
#     ~/scripts/plots/global_chem/exevs_global_chem_headline_grid2obs_plots.sh
# Use the staging dir linked_stat_base_dir as source stats base directory. 
linked_stat_base_dir = os.environ['linked_stat_base_dir']

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


icnt=0
for headline_type in input_obs_types:
    # locate obs src array index
    obsidx = input_obs_types.index(headline_type)
    if headline_type == "airnow_pm25":
        icnt += 1
        ### Headline Score Plot : Grid-to-OBS - AIRNOW PM25 hourly concentration CONUS
        ###                                      Last 90 days 00Z CYCLE DAY1 FCST 
        print("\nHeadline Score Plot "+str(icnt)+" : Grid-to-OBS - AIRNOW PM25 hourly concentration CONUS "
              +"Last 90 days 00Z CYCLE DAY1 FCST")
        # Set fixed plot values
        headline1_plot = 'time_series'
        headline1_ndays = 90
        headline1_model_info_dict = {
            'model1': {'name': input_model_names[0],
                       'plot_name': input_plot_names[0],
                       'obs_name': 'AIRNOW_HOURLY_AQOBS'},
        }
        headline1_plot_info_dict = {
            'line_type': 'SL1L2',
            'grid': 'G004',
            'stat': 'FBAR_OBAR',
            'vx_mask': 'CONUS',
            'event_equalization': 'YES',
            'interp_method': 'BILIN',
            'interp_points': '4',
            'fcst_var_name': 'PMTF',
            'fcst_var_level': 'L0',
            'fcst_var_thresh': 'NA',
            'obs_var_name': 'PM25',
            'obs_var_level': 'A1',
            'obs_var_thresh': 'NA',
            'ob_name':'AIRNOW_HOURLY_AQOBS', 
            'obs_src_name': input_obs_srcs[obsidx],
            'fig_name_label': fig_name_label
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
            'forecast_hour': '24',
            'forecast_day': '1',
            'fday_start': '1',
            'fday_end': '1',
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
        #
        ## Creates condensed statistics files for plotting, based on selected criteria.
        #
        for model_num in list(headline1_model_info_dict.keys()):
            model = headline1_model_info_dict[model_num]['name']
            obs_name = headline1_model_info_dict[model_num]['obs_name']
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
        import global_chem_atmos_plots_time_series as gdap_ts
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
        
    elif headline_type == "aeronet_aod":
        icnt += 1
        ### Headline Score Plot : Grid-to-OBS - AERONET AOD observations GLOBAL
        ###                                      Last 90 days 00Z CYCLE DAY1 FCST 
        print("\nHeadline Score Plot "+str(icnt)+" : Grid-to-OBS - AERONET AOD observations GLOBAL "
              +"Last 90 days 00Z CYCLE DAY1 FCST")
        # Set fixed plot values
        headline1_plot = 'time_series'
        headline1_ndays = 90
        headline1_model_info_dict = {
            'model1': {'name': input_model_names[0],
                       'plot_name': input_plot_names[0],
                       'obs_name': 'AERONET_AOD'},
        }
        headline1_plot_info_dict = {
            'line_type': 'SL1L2',
            'grid': 'G004',
            'stat': 'FBAR_OBAR',
            'vx_mask': 'GLOBAL',
            'event_equalization': 'YES',
            'interp_method': 'NEAREST',
            'interp_points': '1',
            'fcst_var_name': 'AOTK',
            'fcst_var_level': 'L0',
            'fcst_var_thresh': 'NA',
            'obs_var_name': 'AOD',
            'obs_var_level': 'Z550',
            'obs_var_thresh': 'NA',
            'ob_name':'AERONET_AOD', 
            'obs_src_name': input_obs_srcs[obsidx],
            'fig_name_label': fig_name_label
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
            'forecast_hour': '24',
            'forecast_day': '1',
            'fday_start': '1',
            'fday_end': '1',
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
        #
        ## Creates condensed statistics files for plotting, based on selected criteria.
        #
        for model_num in list(headline1_model_info_dict.keys()):
            model = headline1_model_info_dict[model_num]['name']
            obs_name = headline1_model_info_dict[model_num]['obs_name']
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
        import global_chem_atmos_plots_time_series as gdap_ts
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
    else:
        print(f"\nDEBUG: ================================================================================")
        print(f"\nDEBUG: Input verification type {headline_type} is currently undefined for headline plot")
        print(f"\nDEBUG: ================================================================================")

print("END: "+os.path.basename(__file__))
