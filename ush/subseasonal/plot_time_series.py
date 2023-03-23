'''
Name: plot_time_series.py
Contact(s): Shannon Shields
Abstract: Reads filtered files from stat_analysis_wrapper
          run_all_times to make time series plots
History Log: Third version
Usage: Called by make_plots_wrapper.py
Parameters: None
Input Files: MET .stat files
Output Files: .png images
Condition codes: 0 for success, 1 for failure
'''

import os
import numpy as np
import pandas as pd
pd.plotting.deregister_matplotlib_converters()
#pd.plotting.register_matplotlib_converters()
import itertools
import warnings
import logging
import datetime
import math
import re
import sys
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md

import plot_util as plot_util
from plot_util import get_ci_file, get_lead_avg_file

# add metplus directory to path so the wrappers and utilities can be found
sys.path.insert(0, os.path.abspath(os.environ['HOMEMETplus']))
from metplus.util import do_string_sub

#### EMC-evs title creation script
import plot_title as plot_title

#### EMC-evs plot settings
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.titlepad'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['axes.labelpad'] = 10
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['xtick.major.pad'] = 10
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['ytick.major.pad'] = 10
plt.rcParams['figure.subplot.left'] = 0.1
plt.rcParams['figure.subplot.right'] = 0.95
plt.rcParams['figure.subplot.top'] = 0.85
plt.rcParams['figure.subplot.bottom'] = 0.15
plt.rcParams['legend.handletextpad'] = 0.25
plt.rcParams['legend.handlelength'] = 1.25
plt.rcParams['legend.borderaxespad'] = 0
plt.rcParams['legend.columnspacing'] = 1.0
plt.rcParams['legend.frameon'] = False
x_figsize, y_figsize = 14, 7
nticks = 4
legend_bbox_x, legend_bbox_y = 0.5, 0.05
legend_fontsize = 13
legend_loc = 'center'
legend_ncol = 5
title_loc = 'center'
model_obs_plot_settings_dict = {
    'model1': {'color': '#000000',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 3},
    'model2': {'color': '#FB2020',
               'marker': '^', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model3': {'color': '#00DC00',
               'marker': 'x', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model4': {'color': '#1E3CFF',
               'marker': '+', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model5': {'color': '#E69F00',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model6': {'color': '#56B4E9',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model7': {'color': '#696969',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model8': {'color': '#8400C8',
               'marker': 'D', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model9': {'color': '#D269C1',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model10': {'color': '#F0E492',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'obs': {'color': '#AAAAAA',
            'marker': 'None', 'markersize': 0,
            'linestyle': 'solid', 'linewidth': 2}
}
noaa_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'noaa.png')
)
noaa_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.1
noaa_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.865
noaa_logo_alpha = 0.5
nws_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'nws.png')
)
nws_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.9
nws_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.865
nws_logo_alpha = 0.5

# Read environment variables set in make_plots_wrapper.py
verif_case = os.environ['VERIF_CASE']
verif_type = os.environ['VERIF_TYPE']
date_type = os.environ['DATE_TYPE']
valid_beg = os.environ['VALID_BEG']
valid_end = os.environ['VALID_END']
init_beg = os.environ['INIT_BEG']
init_end = os.environ['INIT_END']
fcst_valid_hour = os.environ['FCST_VALID_HOUR']
fcst_init_hour = os.environ['FCST_INIT_HOUR']
obs_valid_hour = os.environ['OBS_VALID_HOUR']
obs_init_hour = os.environ['OBS_INIT_HOUR']
fcst_lead_list = os.environ['FCST_LEAD'].split(', ')
fcst_var_name = os.environ['FCST_VAR']
fcst_var_units = os.environ['FCST_UNITS']
fcst_var_level_list = os.environ['FCST_LEVEL'].split(', ')
fcst_var_thresh_list = os.environ['FCST_THRESH'].split(', ')
obs_var_name = os.environ['OBS_VAR']
obs_var_units = os.environ['OBS_UNITS']
obs_var_level_list = os.environ['OBS_LEVEL'].split(', ')
obs_var_thresh_list = os.environ['OBS_THRESH'].split(', ')
interp_pnts = os.environ['INTERP_PNTS']
vx_mask = os.environ['VX_MASK']
alpha = os.environ['ALPHA']
desc = os.environ['DESC']
obs_lead = os.environ['OBS_LEAD']
cov_thresh = os.environ['COV_THRESH']
stats_list = os.environ['STATS'].split(', ')
model_list = os.environ['MODEL'].split(', ')
model_obtype_list = os.environ['MODEL_OBTYPE'].split(', ')
model_reference_name_list = os.environ['MODEL_REFERENCE_NAME'].split(', ')
dump_row_filename_template = os.environ['DUMP_ROW_FILENAME']
average_method = os.environ['AVERAGE_METHOD']
ci_method = os.environ['CI_METHOD']
verif_grid = os.environ['VERIF_GRID']
event_equalization = os.environ['EVENT_EQUALIZATION']
met_version = os.environ['MET_VERSION']
input_base_dir = os.environ['INPUT_BASE_DIR']
output_base_dir = os.environ['OUTPUT_BASE_DIR']
log_metplus = os.environ['LOG_METPLUS']
log_level = os.environ['LOG_LEVEL']
#### EMC-evs environment variables
var_name = os.environ['var_name']
fcst_var_extra = (os.environ['fcst_var_options'].replace(' ', '') \
                  .replace('=','').replace(';','').replace('"','') \
                  .replace("'",'').replace(',','-').replace('_',''))
obs_var_extra = (os.environ['obs_var_options'].replace(' ', '') \
                 .replace('=','').replace(';','').replace('"','') \
                 .replace("'",'').replace(',','-').replace('_',''))
interp_mthd = os.environ['interp']

# General set up and settings
# Logging
logger = logging.getLogger(log_metplus)
logger.setLevel(log_level)
formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
    +'%(message)s',
    '%m/%d %H:%M:%S'
    )
file_handler = logging.FileHandler(log_metplus, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
output_data_dir = os.path.join(output_base_dir, 'data')
#### EMC-evs image directory
output_imgs_dir = os.path.join(output_base_dir, 'subseasonal',
                               'subseasonal.{valid?fmt=%Y%m%d%H}')
# Model info
model_info_list = list(
    zip(model_list,
        model_reference_name_list,
        model_obtype_list,
    )
)
nmodels = len(model_info_list)
# Plot info
plot_info_list = list(
    itertools.product(*[fcst_lead_list,
                        fcst_var_level_list,
                        fcst_var_thresh_list])
    )
# Date and time information and build title for plot
date_beg = os.environ[date_type+'_BEG']
date_end = os.environ[date_type+'_END']
valid_init_dict = {
    'fcst_valid_hour_beg': fcst_valid_hour.split(', ')[0],
    'fcst_valid_hour_end': fcst_valid_hour.split(', ')[-1],
    'fcst_init_hour_beg': fcst_init_hour.split(', ')[0],
    'fcst_init_hour_end': fcst_init_hour.split(', ')[-1],
    'obs_valid_hour_beg': obs_valid_hour.split(', ')[0],
    'obs_valid_hour_end': obs_valid_hour.split(', ')[-1],
    'obs_init_hour_beg': obs_init_hour.split(', ')[0],
    'obs_init_hour_end': obs_init_hour.split(', ')[-1],
    'valid_hour_beg': '',
    'valid_hour_end': '',
    'init_hour_beg': '',
    'init_hour_end': ''
}
valid_init_type_list = [
    'valid_hour_beg', 'valid_hour_end', 'init_hour_beg', 'init_hour_end'
]
for vitype in valid_init_type_list:
    if (valid_init_dict['fcst_'+vitype] != ''
            and valid_init_dict['obs_'+vitype] == ''):
        valid_init_dict[vitype] = valid_init_dict['fcst_'+vitype]
    elif (valid_init_dict['obs_'+vitype] != ''
            and valid_init_dict['fcst_'+vitype] == ''):
        valid_init_dict[vitype] = valid_init_dict['obs_'+vitype]
    if valid_init_dict['fcst_'+vitype] == '':
        if 'beg' in vitype:
            valid_init_dict['fcst_'+vitype] = '000000'
        elif 'end' in vitype:
            valid_init_dict['fcst_'+vitype] = '235959'
    if valid_init_dict['obs_'+vitype] == '':
        if 'beg' in vitype:
            valid_init_dict['obs_'+vitype] = '000000'
        elif 'end' in vitype:
            valid_init_dict['obs_'+vitype] = '235959'
    if valid_init_dict['fcst_'+vitype] == valid_init_dict['obs_'+vitype]:
        valid_init_dict[vitype] = valid_init_dict['fcst_'+vitype]

# MET .stat file formatting
stat_file_base_columns = plot_util.get_stat_file_base_columns(met_version)
nbase_columns = len(stat_file_base_columns)
# Significance testing info
# need to set up random number array [nmodels, ntests, ndays]
# for EMC Monte Carlo testing. Each model has its own
# "series" of random numbers used at all forecast hours
# and thresholds.
mc_dates, mc_expected_stat_file_dates = plot_util.get_date_arrays(
    date_type, date_beg, date_end,
    fcst_valid_hour, fcst_init_hour,
    obs_valid_hour, obs_init_hour,
    '000000'
)
ndays = len(mc_expected_stat_file_dates)
ntests = 10000
randx = np.random.rand(nmodels,ntests,ndays)

# Start looping to make plots
for plot_info in plot_info_list:
    fcst_lead = plot_info[0]
    fcst_var_level = plot_info[1]
    obs_var_level = obs_var_level_list[
        fcst_var_level_list.index(fcst_var_level)
    ]
    fcst_var_thresh = plot_info[2]
    obs_var_thresh = obs_var_thresh_list[
        fcst_var_thresh_list.index(fcst_var_thresh)
    ]
    fcst_var_thresh_symbol, fcst_var_thresh_letter = plot_util.format_thresh(
        fcst_var_thresh
    )
    obs_var_thresh_symbol, obs_var_thresh_letter = plot_util.format_thresh(
        obs_var_thresh
    )
    logger.info("Working on forecast lead "+fcst_lead+" "
                +"and forecast variable "+fcst_var_name+" "+fcst_var_level+" "
                +fcst_var_thresh)
    # Set up base name for file naming convention for MET .stat files,
    # and output data and images
    base_name = date_type.lower()+date_beg+'to'+date_end
    if (valid_init_dict['valid_hour_beg'] != ''
            and valid_init_dict['valid_hour_end'] != ''):
        base_name+=(
            '_valid'+valid_init_dict['valid_hour_beg'][0:4]
            +'to'+valid_init_dict['valid_hour_end'][0:4]+'Z'
        )
    else:
        base_name+=(
            '_fcst_valid'+valid_init_dict['fcst_valid_hour_beg'][0:4]
            +'to'+valid_init_dict['fcst_valid_hour_end'][0:4]+'Z'
            +'_obs_valid'+valid_init_dict['obs_valid_hour_beg'][0:4]
            +'to'+valid_init_dict['obs_valid_hour_end'][0:4]+'Z'
        )
    if (valid_init_dict['init_hour_beg'] != ''
            and valid_init_dict['init_hour_end'] != ''):
        base_name+=(
            '_init'+valid_init_dict['init_hour_beg'][0:4]
            +'to'+valid_init_dict['init_hour_end'][0:4]+'Z'
        )
    else:
        base_name+=(
            '_fcst_init'+valid_init_dict['fcst_init_hour_beg'][0:4]
            +'to'+valid_init_dict['fcst_init_hour_end'][0:4]+'Z'
            +'_obs_init'+valid_init_dict['obs_init_hour_beg'][0:4]
            +'to'+valid_init_dict['obs_init_hour_end']+'Z'
        )
    base_name+=(
        '_fcst_lead'+fcst_lead
        +'_fcst'+fcst_var_name+fcst_var_level
        +fcst_var_thresh_letter.replace(',', '_')+interp_mthd
        +'_obs'+obs_var_name+obs_var_level
        +obs_var_thresh_letter.replace(',', '_')+interp_mthd
        +'_vxmask'+vx_mask
    )
    if desc != '':
        base_name+='_desc'+desc
    if obs_lead != '':
        base_name+='_obs_lead'+obs_lead
    if interp_pnts != '':
        base_name+='_interp_pnts'+interp_pnts
    if cov_thresh != '':
        cov_thresh_symbol, cov_thresh_letter = plot_util.format_thresh(
            cov_thresh
        )
        base_name+='_cov_thresh'+cov_thresh_letter.replace(',', '_')
    if alpha != '':
        base_name+='_alpha'+alpha
    # Set up expected date in MET .stat file and date plot information
    plot_time_dates, expected_stat_file_dates = plot_util.get_date_arrays(
        date_type, date_beg, date_end,
        fcst_valid_hour, fcst_init_hour,
        obs_valid_hour, obs_init_hour,
        fcst_lead
    )
    total_dates = len(plot_time_dates)
    if len(plot_time_dates) == 0:
        logger.error("Date array constructed information from METplus "
                     +"conf file has length of 0. Not enough information "
                     +"was provided to build date information. Please check "
                     +"provided VALID/INIT_BEG/END and "
                     +"OBS/FCST_INIT/VALID_HOUR_LIST")
        exit(1)
    #### EMC-evs date tick interval
    if len(plot_time_dates) < nticks:
        date_tick_intvl = 1
    else:
        date_tick_intvl = int(len(plot_time_dates)/nticks)
    # Reading in model .stat files from stat_analysis
    logger.info("Reading in model data")
    for model_info in model_info_list:
        model_num = model_info_list.index(model_info) + 1
        model_name = model_info[0]
        model_plot_name = model_info[1]
        model_obtype = model_info[2]
        model_data_now_index = pd.MultiIndex.from_product(
            [[model_plot_name], expected_stat_file_dates],
            names=['model_plot_name', 'dates']
        )
        model_stat_template = dump_row_filename_template
        string_sub_dict = {
            'model': model_name,
            'model_reference': model_plot_name,
            'obtype': model_obtype,
            'fcst_lead': fcst_lead,
            'fcst_level': fcst_var_level,
            'obs_level': obs_var_level,
            'fcst_thresh': fcst_var_thresh,
            'obs_thresh': obs_var_thresh,
        }
        model_stat_file = do_string_sub(model_stat_template,
                                        **string_sub_dict)
        if os.path.exists(model_stat_file):
            nrow = sum(1 for line in open(model_stat_file))
            if nrow == 0:
                logger.warning("Model "+str(model_num)+" "+model_name+" "
                               +"with plot name "+model_plot_name+" "
                               +"file: "+model_stat_file+" empty")
                model_now_data = pd.DataFrame(np.nan,
                                              index=model_data_now_index,
                                              columns=[ 'TOTAL' ])
            else:
                logger.debug("Model "+str(model_num)+" "+model_name+" "
                             +"with plot name "+model_plot_name+" "
                             +"file: "+model_stat_file+" exists")
                model_now_stat_file_data = pd.read_csv(
                    model_stat_file, sep=" ", skiprows=1,
                    skipinitialspace=True, header=None
                )
                model_now_stat_file_data.rename(
                    columns=dict(zip(
                        model_now_stat_file_data.columns[:nbase_columns],
                        stat_file_base_columns
                    )), inplace=True
                )
                line_type = model_now_stat_file_data['LINE_TYPE'][0]
                stat_file_line_type_columns = (
                    plot_util.get_stat_file_line_type_columns(logger,
                                                              met_version,
                                                              line_type)
                )
                model_now_stat_file_data.rename(
                    columns=dict(zip(
                        model_now_stat_file_data.columns[nbase_columns:],
                        stat_file_line_type_columns
                    )), inplace=True
                )
                model_now_stat_file_data_fcst_valid_dates = (
                    model_now_stat_file_data.loc[:]['FCST_VALID_BEG'].values
                )
                model_now_data = (
                    pd.DataFrame(np.nan, index=model_data_now_index,
                                 columns=stat_file_line_type_columns)
                )
                #model_now_stat_file_data.fillna(
                #    {'FCST_UNITS':'NA', 'OBS_UNITS':'NA', 'VX_MASK':'NA'},
                #    inplace=True
                #)
                for expected_date in expected_stat_file_dates:
                    if expected_date in \
                            model_now_stat_file_data_fcst_valid_dates:
                        matching_date_idx = (
                            model_now_stat_file_data_fcst_valid_dates \
                            .tolist().index(expected_date)
                        )
                        model_now_stat_file_data_indexed = (
                            model_now_stat_file_data.loc[matching_date_idx][:]
                        )
                        for col in stat_file_line_type_columns:
                            #### EMC-evs changes for PRMSL, PRES/Z0
                            #### O3MR
                            if fcst_var_name == 'PRMSL' \
                                    or \
                                    (fcst_var_name == 'PRES' \
                                     and fcst_var_level == 'Z0'):
                                if col in ['FBAR', 'OBAR']:
                                    scale = 1/100.
                                elif col in ['FFBAR', 'FOBAR', 'OOBAR']:
                                    scale = 1/(100.*100.)
                                else:
                                    scale = 1
                            elif fcst_var_name == 'O3MR':
                                if col in ['FBAR', 'OBAR']:
                                    scale = 1e6
                                elif col in ['FFBAR', 'FOBAR', 'OOBAR']:
                                    scale = 1e6*1e6
                                else:
                                    scale = 1
                            else:
                                scale = 1
                            model_now_data.loc[
                                (model_plot_name, expected_date)
                            ][col] = (
                                model_now_stat_file_data_indexed \
                                .loc[:][col] * scale
                            )
        else:
            logger.warning("Model "+str(model_num)+" "+model_name+" "
                           +"with plot name "+model_plot_name+" "
                           +"file: "+model_stat_file+" does not exist")
            model_now_data = pd.DataFrame(np.nan,
                                          index=model_data_now_index,
                                          columns=[ 'TOTAL' ])
        if model_num > 1:
            model_data = pd.concat([model_data, model_now_data], sort=True)
        else:
            model_data = model_now_data
    # Calculate statistics and plots
    logger.info("Calculating and plotting statistics")
    for stat in stats_list:
        logger.debug("Working on "+stat)
        stat_values, stat_values_array, stat_plot_name = (
            plot_util.calculate_stat(logger, model_data, stat)
        )
        if event_equalization == 'True':
            logger.debug("Doing event equalization")
            for l in range(len(stat_values_array[:,0,0])):
                stat_values_array[l,:,:] = (
                    np.ma.mask_cols(stat_values_array[l,:,:])
                )
        np.ma.set_fill_value(stat_values_array, np.nan)
        stat_min = np.ma.masked_invalid(np.nan)
        stat_max = np.ma.masked_invalid(np.nan)
        for model_info in model_info_list:
            model_num = model_info_list.index(model_info) + 1
            model_idx = model_info_list.index(model_info)
            model_name = model_info[0]
            model_plot_name = model_info[1]
            model_obtype = model_info[2]
            #### EMC-evs model plot settings
            model_plot_settings_dict = (
                model_obs_plot_settings_dict['model'+str(model_num)]
            )
            model_stat_values_array = stat_values_array[:,model_idx,:]
            # Write model forecast lead average to file
            model_stat_template = dump_row_filename_template
            string_sub_dict = {
                'model': model_name,
                'model_reference': model_plot_name,
                'obtype': model_obtype,
                'fcst_lead': fcst_lead,
                'fcst_level': fcst_var_level,
                'obs_level': obs_var_level,
                'fcst_thresh': fcst_var_thresh,
                'obs_thresh': obs_var_thresh,
            }
            model_stat_file = do_string_sub(model_stat_template,
                                            **string_sub_dict)
            lead_avg_file = get_lead_avg_file(stat,
                                              model_stat_file,
                                              fcst_lead,
                                              output_base_dir)
            logger.debug("Writing model "+str(model_num)+" "+model_name+" "
                         +"with name on plot "+model_plot_name+" lead "
                         +fcst_lead+" average to file: "+lead_avg_file)
            model_stat_average_array = plot_util.calculate_average(
                logger, average_method, stat,
                model_data.loc[[model_plot_name]],
                model_stat_values_array
            )
            with open(lead_avg_file, 'a') as file2write:
                file2write.write(fcst_lead)
                for l in range(len(model_stat_average_array)):
                    file2write.write(
                        ' '+str(model_stat_average_array[l])
                    )
                file2write.write('\n')
            # Write confidence intervals to file, if requested,
            # using similar naming to model forecast lead average
            if ci_method != 'NONE':
                CI_file = get_ci_file(stat,
                                      model_stat_file,
                                      fcst_lead,
                                      output_base_dir,
                                      ci_method)
                if (stat == 'fbar_obar' or stat == 'orate_frate'
                        or stat == 'baser_frate'):
                    logger.debug("Writing "+ci_method+" confidence intervals "
                                 +"for difference between model "
                                 +str(model_num)+" "+model_name+" with name "
                                 +"on plot "+model_plot_name+" and the "
                                 +"observations at lead "+fcst_lead+" to "
                                 +"file: "+CI_file)
                    if ci_method == 'EMC_MONTE_CARLO':
                        logger.warning("Monte Carlo resampling not "
                                       +"done for fbar_obar, orate_frate, "
                                       +"or baser_frate.")
                        stat_CI = '--'
                    else:
                        stat_CI = plot_util.calculate_ci(
                            logger, ci_method, model_stat_values_array[0,:],
                            model_stat_values_array[1,:],total_dates,
                            stat, average_method, randx[model_idx,:,:]
                        )
                    with open(CI_file, 'a') as file2write:
                        file2write.write(fcst_lead+' '+str(stat_CI)+'\n')
                else:
                    if model_num == 1:
                        model1_stat_values_array = (
                            model_stat_values_array[0,:]
                        )
                        model1_plot_name = model_plot_name
                        model1_name = model_name
                    else:
                        logger.debug("Writing "+ci_method+" confidence "
                                     +"intervals for difference between "
                                     +"model "+str(model_num)+" "
                                     +model_name+" with name on plot "
                                     +model_plot_name+" and model 1 "
                                     +model1_name+" with name on plot "
                                     +model1_plot_name+" at lead "
                                     +fcst_lead+" to file: "+CI_file)
                        if ci_method == 'EMC_MONTE_CARLO':
                            stat_CI = plot_util.calculate_ci(
                                logger, ci_method,
                                model_data.loc[[model_plot_name]],
                                model_data.loc[[model1_plot_name]],
                                total_dates,
                                stat, average_method, randx[model_idx,:,:]
                            )
                        else:
                            stat_CI = plot_util.calculate_ci(
                                logger, ci_method, model_stat_values_array,
                                model1_stat_values_array, total_dates,
                                stat, average_method, randx[model_idx,:,:]
                            )
                        with open(CI_file, 'a') as file2write:
                            file2write.write(fcst_lead+' '+str(stat_CI)+'\n')
            if model_num == 1:
                fig, ax = plt.subplots(1,1,figsize=(x_figsize, y_figsize))
                ax.grid(True)
                ax.set_xlabel(date_type.title()+' Date')
                ax.set_xlim([plot_time_dates[0],plot_time_dates[-1]])
                ax.set_xticks(plot_time_dates[::date_tick_intvl])
                ax.xaxis.set_major_formatter(md.DateFormatter('%d%b%Y'))
                if len(plot_time_dates) > 60:
                    ax.xaxis.set_minor_locator(md.MonthLocator())
                else:
                    ax.xaxis.set_minor_locator(md.DayLocator())
                ax.set_ylabel(stat_plot_name)
                obs_plotted = False
            if (stat == 'fbar_obar' or stat == 'orate_frate'
                    or stat == 'baser_frate'):
                obs_stat_values_array = model_stat_values_array[1,:]
                obs_count = (
                    len(obs_stat_values_array)
                    - np.ma.count_masked(obs_stat_values_array)
                )
                obs_stat_values_mc = np.ma.compressed(
                    obs_stat_values_array
                )
                plot_time_dates_m = np.ma.masked_where(
                    np.ma.getmask(obs_stat_values_array), plot_time_dates
                )
                plot_time_dates_mc = np.ma.compressed(plot_time_dates_m)
                obs_plot_settings_dict = (
                    model_obs_plot_settings_dict['obs']
                )
                #### EMC-evs plot observations
                if not obs_plotted:
                    if obs_count != 0:
                        logger.debug("Plotting obs from "+model_name)
                        if np.abs(obs_stat_values_array.mean()) >= 10:
                            obs_mean_for_label = round(
                                obs_stat_values_array.mean(), 2
                            )
                            obs_mean_for_label = format(
                                obs_mean_for_label, '.2f'
                            )
                        else:
                            obs_mean_for_label = round(
                                obs_stat_values_array.mean(), 3
                            )
                            obs_mean_for_label = format(
                                obs_mean_for_label, '.3f'
                            )
                        ax.plot_date(plot_time_dates_mc,
                                     obs_stat_values_mc,
                                     color = obs_plot_settings_dict['color'],
                                     linestyle = obs_plot_settings_dict \
                                         ['linestyle'],
                                     linewidth = obs_plot_settings_dict \
                                         ['linewidth'],
                                     marker = obs_plot_settings_dict \
                                         ['marker'],
                                     markersize = obs_plot_settings_dict \
                                         ['markersize'],
                                     label=('obs '
                                            +str(obs_mean_for_label)
                                            +' '+str(obs_count)+' days'),
                                     zorder=4)
                        if obs_stat_values_array.min() < stat_min \
                                or np.ma.is_masked(stat_min):
                            stat_min = obs_stat_values_array.min()
                        if obs_stat_values_array.max() > stat_max \
                                or np.ma.is_masked(stat_max):
                            stat_max = obs_stat_values_array.max()
                        obs_plotted = True
            count = (
                len(model_stat_values_array[0,:])
                - np.ma.count_masked(model_stat_values_array[0,:])
            )
            plot_time_dates_m = np.ma.masked_where(
                np.ma.getmask(model_stat_values_array[0,:]), plot_time_dates
            )
            plot_time_dates_mc = np.ma.compressed(plot_time_dates_m)
            model_stat_values_mc = np.ma.compressed(
                model_stat_values_array[0,:]
            )
            #### EMC-evs plot model
            if count != 0:
                logger.debug("Plotting model "+str(model_num)+" "
                             +model_name+" with name on plot "
                             +model_plot_name)
                if np.abs(model_stat_values_array.mean()) >= 10:
                    mean_for_label = round(model_stat_values_array.mean(), 2)
                    mean_for_label = format(mean_for_label, '.2f')
                else:
                    mean_for_label = round(model_stat_values_array.mean(), 3)
                    mean_for_label = format(mean_for_label, '.3f')
                ax.plot_date(plot_time_dates_mc, model_stat_values_mc,
                             color = model_plot_settings_dict['color'],
                             linestyle = model_plot_settings_dict \
                                 ['linestyle'],
                             linewidth = model_plot_settings_dict \
                                 ['linewidth'],
                             marker = model_plot_settings_dict['marker'],
                             markersize = model_plot_settings_dict \
                                 ['markersize'],
                             label=(model_plot_name
                                    +' '+str(mean_for_label)
                                    +' '+str(count)+' days'),
                             zorder=(nmodels-model_idx)+4)
                if model_stat_values_array.min() < stat_min \
                        or np.ma.is_masked(stat_min):
                    stat_min = model_stat_values_array.min()
                if model_stat_values_array.max() > stat_max \
                        or np.ma.is_masked(stat_max):
                    stat_max = model_stat_values_array.max()
        #### EMC-evs adjust y axis limits and ticks
        preset_y_axis_tick_min = ax.get_yticks()[0]
        preset_y_axis_tick_max = ax.get_yticks()[-1]
        preset_y_axis_tick_inc = ax.get_yticks()[1] - ax.get_yticks()[0]
        if stat in ['acc', 'msess', 'ets', 'rsd']:
            y_axis_tick_inc = 0.1
        else:
            y_axis_tick_inc = preset_y_axis_tick_inc
        if np.ma.is_masked(stat_min):
            y_axis_min = preset_y_axis_tick_min
        else:
            if stat in ['acc', 'msess', 'ets', 'rsd']:
                y_axis_min = round(stat_min,1) - y_axis_tick_inc
            else:
                y_axis_min = preset_y_axis_tick_min
                while y_axis_min > stat_min:
                    y_axis_min = y_axis_min - y_axis_tick_inc
        if np.ma.is_masked(stat_max):
            y_axis_max = preset_y_axis_tick_max
        else:
            if stat in ['acc', 'msess', 'ets']:
                y_axis_max = 1
            elif stat in ['rsd']:
                y_axis_max = round(stat_max,1) + y_axis_tick_inc
            else:
                y_axis_max = preset_y_axis_tick_max + y_axis_tick_inc
                while y_axis_max < stat_max:
                    y_axis_max = y_axis_max + y_axis_tick_inc
        ax.set_yticks(
            np.arange(y_axis_min, y_axis_max+y_axis_tick_inc, y_axis_tick_inc)
        )
        ax.set_ylim([y_axis_min, y_axis_max])
        #### EMC-evs check y axis limits
        if stat_max >= ax.get_ylim()[1]:
            while stat_max >= ax.get_ylim()[1]:
                y_axis_max = y_axis_max + y_axis_tick_inc
                ax.set_yticks(
                    np.arange(y_axis_min,
                              y_axis_max +  y_axis_tick_inc,
                              y_axis_tick_inc)
                )
                ax.set_ylim([y_axis_min, y_axis_max])
        if stat_min <= ax.get_ylim()[0]:
            while stat_min <= ax.get_ylim()[0]:
                y_axis_min = y_axis_min - y_axis_tick_inc
                ax.set_yticks(
                    np.arange(y_axis_min,
                              y_axis_max +  y_axis_tick_inc,
                              y_axis_tick_inc)
                )
                ax.set_ylim([y_axis_min, y_axis_max])
        #### EMC-evs add legend, adjust if points in legend
        if len(ax.lines) != 0:
            legend = ax.legend(bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                               loc=legend_loc, ncol=legend_ncol,
                               fontsize=legend_fontsize)
            plt.draw()
            legend_box = legend.get_window_extent() \
                .inverse_transformed(ax.transData)
            if stat_min < legend_box.y1:
                while stat_min < legend_box.y1:
                    y_axis_min = y_axis_min - y_axis_tick_inc
                    ax.set_yticks(
                        np.arange(y_axis_min,
                                  y_axis_max + y_axis_tick_inc,
                                  y_axis_tick_inc)
                    )
                    ax.set_ylim([y_axis_min, y_axis_max])
                    legend = ax.legend(
                        bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                        loc=legend_loc, ncol=legend_ncol,
                        fontsize=legend_fontsize
                    )
                    plt.draw()
                    legend_box = (
                        legend.get_window_extent() \
                        .inverse_transformed(ax.transData)
                    )
        #### EMC-evs build formal plot title
        if verif_grid == vx_mask:
            grid_vx_mask = verif_grid
        else:
            grid_vx_mask = verif_grid+vx_mask
        var_info_title = plot_title.get_var_info_title(
            fcst_var_name, fcst_var_level, fcst_var_extra, fcst_var_thresh
        )
        vx_mask_title = plot_title.get_vx_mask_title(vx_mask)
        date_info_title = plot_title.get_date_info_title(
            date_type, fcst_valid_hour.split(', '),
            fcst_init_hour.split(', '),
            str(datetime.date.fromordinal(int(
                plot_time_dates[0])
            ).strftime('%d%b%Y')),
            str(datetime.date.fromordinal(int(
                plot_time_dates[-1])
            ).strftime('%d%b%Y')),
            verif_case
        )
        forecast_lead_title = plot_title.get_lead_title(fcst_lead[:-4])
        full_title = (
            stat_plot_name+'\n'
            +var_info_title+', '+vx_mask_title+'\n'
            +date_info_title+', '+forecast_lead_title
        )
        ax.set_title(full_title, loc=title_loc)
        fig.figimage(noaa_logo_img_array,
                     noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
                     zorder=1, alpha=noaa_logo_alpha)
        fig.figimage(nws_logo_img_array,
                     nws_logo_xpixel_loc, nws_logo_ypixel_loc,
                     zorder=1, alpha=nws_logo_alpha)
        #### EMC-evs build savefig name
        savefig_name = os.path.join(output_imgs_dir, stat)
        if date_type == 'VALID':
            if verif_case == 'grid2obs':
                savefig_name = (
                    savefig_name+'_init'
                    +fcst_init_hour.split(', ')[0][0:2]+'Z'
                )
            else:
                savefig_name = (
                    savefig_name+'_valid'
                    +fcst_valid_hour.split(', ')[0][0:2]+'Z'
                )
        elif date_type == 'INIT':
            if verif_case == 'grid2obs':
                savefig_name = (
                    savefig_name+'_valid'
                    +fcst_valid_hour.split(', ')[0][0:2]+'Z'
                )
            else:
                savefig_name = (
                    savefig_name+'_init'+fcst_init_hour.split(', ')[0][0:2]+'Z'
                )
        if verif_case == 'grid2grid' and verif_type == 'anom':
            savefig_name = savefig_name+'_'+var_name+'_'+fcst_var_level
        else:
            savefig_name = savefig_name+'_'+fcst_var_name+'_'+fcst_var_level
        if verif_case == 'precip':
            savefig_name = savefig_name+'_'+fcst_var_thresh
        savefig_name = (savefig_name+'_fhr'+fcst_lead[:-4]
                        +'_'+grid_vx_mask+'.png')
        logger.info("Saving image as "+savefig_name)
        plt.savefig(savefig_name)
        plt.clf()
        plt.close('all')
