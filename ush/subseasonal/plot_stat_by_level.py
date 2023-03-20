'''
Name: plot_stat_by_level.py
Contact(s): Shannon Shields
Abstract: Reads average forecast hour files from plot_time_series.py
          to make stat-pressure plots
History Log: Third version
Usage: Called by make_plots_wrapper.py
Parameters: None
Input Files: Text files
Output Files: .png images
Condition codes: 0 for success, 1 for failure
'''

import os
import sys
import numpy as np
import pandas as pd
import itertools
import warnings
import logging
import datetime
import re
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md

import plot_util as plot_util
from plot_util import get_lead_avg_file

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
plt.rcParams['figure.subplot.top'] = 0.925
plt.rcParams['figure.subplot.bottom'] = 0.075
plt.rcParams['legend.handletextpad'] = 0.25
plt.rcParams['legend.handlelength'] = 1.25
plt.rcParams['legend.borderaxespad'] = 0
plt.rcParams['legend.columnspacing'] = 1.0
plt.rcParams['legend.frameon'] = False
x_figsize, y_figsize = 14, 14
legend_bbox_x, legend_bbox_y = 0, 1
legend_fontsize = 17
legend_loc = 'upper left'
legend_ncol = 1
title_loc = 'center'
model_obs_plot_settings_dict = {
    'model1': {'color': '#000000',
               'marker': 'None', 'markersize': 0,
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
    os.path.join(os.environ['USHevs'], 'subseasonal', 'noaa.png')
)
noaa_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.1
noaa_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.9325
noaa_logo_alpha = 0.5
nws_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHevs'], 'subseasonal', 'nws.png')
)
nws_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.9
nws_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.9325
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
fcst_var_level_list = [os.environ['FCST_LEVEL'].split(', ')]
fcst_var_thresh_list = os.environ['FCST_THRESH'].split(', ')
obs_var_name = os.environ['OBS_VAR']
obs_var_units = os.environ['OBS_UNITS']
obs_var_level_list = [os.environ['OBS_LEVEL'].split(', ')]
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
if date_type == 'VALID':
    start_date = valid_beg
    end_date = valid_end
elif date_type == 'INIT':
    start_date = init_beg
    end_date = init_end

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

# Start looping to make plots
for plot_info in plot_info_list:
    fcst_lead = plot_info[0]
    fcst_var_levels = plot_info[1]
    obs_var_levels = obs_var_level_list[
        fcst_var_level_list.index(fcst_var_levels)
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
        +'_fcst'+fcst_var_name+'FCSTLEVELHOLDER'
        +fcst_var_thresh_letter.replace(',', '_')+interp_mthd
        +'_obs'+obs_var_name+'OBSLEVELHOLDER'
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
    for stat in stats_list:
        logger.debug("Working on "+stat)
        stat_min = np.ma.masked_invalid(np.nan)
        stat_max = np.ma.masked_invalid(np.nan)
        stat_plot_name = plot_util.get_stat_plot_name(logger, stat)
        if (stat == 'fbar_obar' or stat == 'orate_frate'
                or stat == 'baser_frate'):
            avg_file_cols = ['LEADS', 'VALS', 'OBS_VALS']
        else:
            avg_file_cols = ['LEADS', 'VALS']
        avg_cols_to_array = avg_file_cols[1:]
        # Build forecast levels for plotting
        fcst_var_levels_int = np.empty(len(fcst_var_levels), dtype=int)
        for vl in range(len(fcst_var_levels)):
            fcst_var_levels_int[vl] = fcst_var_levels[vl][1:]
        # Reading in model lead averages files produced
        # from plot_time_series.py
        logger.info("Reading in model data")
        for model_info in model_info_list:
            model_num = model_info_list.index(model_info) + 1
            model_idx = model_info_list.index(model_info)
            model_name = model_info[0]
            model_plot_name = model_info[1]
            model_obtype = model_info[2]
            model_plot_settings_dict = (
                model_obs_plot_settings_dict['model'+str(model_num)]
            )
            model_avg_data = np.empty(
                [len(avg_cols_to_array), len(fcst_var_levels)]
            )
            model_avg_data.fill(np.nan)
            for vl in range(len(fcst_var_levels)):
                fcst_var_level = fcst_var_levels[vl]
                obs_var_level = obs_var_levels[vl]
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
                if os.path.exists(lead_avg_file):
                    nrow = sum(1 for line in open(lead_avg_file))
                    if nrow == 0:
                        logger.warning("Model "+str(model_num)+" "
                                       +model_name+" with plot name "
                                       +model_plot_name+" file: "
                                       +lead_avg_file+" empty")
                    else:
                        logger.debug("Model "+str(model_num)+" "
                                     +model_name+" with plot name "
                                     +model_plot_name+" file: "
                                     +lead_avg_file+" exists")
                    model_avg_file_data = pd.read_csv(
                        lead_avg_file, sep=' ', header=None,
                        names=avg_file_cols, dtype=str
                    )
                    model_avg_file_data_leads = (
                        model_avg_file_data.loc[:]['LEADS'].tolist()
                    )
                    if fcst_lead in model_avg_file_data_leads:
                        model_fcst_lead_idx = (
                            model_avg_file_data_leads.index(fcst_lead)
                        )
                        for col in avg_cols_to_array:
                            col_idx = avg_cols_to_array.index(col)
                            model_avg_file_data_col = (
                                model_avg_file_data.loc[:][col].tolist()
                            )
                            if (model_avg_file_data_col[model_fcst_lead_idx]
                                    != '--'):
                                model_avg_data[col_idx, vl] = (
                                    float(model_avg_file_data_col \
                                          [model_fcst_lead_idx])
                                )
                else:
                    logger.warning("Model "+str(model_num)+" "+model_name+" "
                                   +"with plot name "+model_plot_name+" "
                                   +"file: "+lead_avg_file+" does not exist")
            model_avg_data = np.ma.masked_invalid(model_avg_data)
            if model_num == 1:
                fig, ax = plt.subplots(1, 1, figsize=(x_figsize, y_figsize))
                ax.grid(True)
                ax.set_xlabel(stat_plot_name)
                ax.set_ylabel('Pressure Level (hPa)')
                ax.set_yscale('log')
                ax.invert_yaxis()
                ax.minorticks_off()
                ax.set_yticks(fcst_var_levels_int)
                ax.set_yticklabels(fcst_var_levels_int)
                ax.set_ylim([fcst_var_levels_int[0],fcst_var_levels_int[-1]])
                obs_plotted = False
            if (stat == 'fbar_obar' or stat == 'orate_frate'
                    or stat == 'baser_frate'):
                count_obs = (
                    len(model_avg_data[1,:])
                    - np.ma.count_masked(model_avg_data[1,:])
                )
                obs_plot_settings_dict = (
                    model_obs_plot_settings_dict['obs']
                )
                mfcst_var_levels = np.ma.array(
                   fcst_var_levels_int,
                   mask=np.ma.getmaskarray(model_avg_data[1,:])
                )
                if not obs_plotted:
                    if count_obs != 0:
                        ax.plot(model_avg_data[1,:].compressed(),
                                mfcst_var_levels.compressed(),
                                color=obs_plot_settings_dict['color'],
                                linestyle=obs_plot_settings_dict['linestyle'],
                                linewidth=obs_plot_settings_dict['linewidth'],
                                marker=obs_plot_settings_dict['marker'],
                                markersize=obs_plot_settings_dict[
                                    'markersize'
                                ],
                                label='obs',
                                zorder=4)
                        if model_avg_data[1,:].min() < stat_min \
                                or np.ma.is_masked(stat_min):
                            stat_min = model_avg_data[1,:].min()
                        if model_avg_data[1,:].max() > stat_max \
                                or np.ma.is_masked(stat_max):
                            stat_max = model_avg_data[1,:].max()
                        obs_plotted = True
            count = (len(model_avg_data[0,:])
                     - np.ma.count_masked(model_avg_data[0,:]))
            mfcst_var_levels = np.ma.array(
                fcst_var_levels_int,
                mask=np.ma.getmaskarray(model_avg_data[0,:])
            )
            if count != 0:
                ax.plot(model_avg_data[0,:].compressed(),
                        mfcst_var_levels.compressed(),
                        color=model_plot_settings_dict['color'],
                        linestyle=model_plot_settings_dict['linestyle'],
                        linewidth=model_plot_settings_dict['linewidth'],
                        marker=model_plot_settings_dict['marker'],
                        markersize=model_plot_settings_dict['markersize'],
                        label=model_plot_name,
                       zorder=(nmodels-model_idx)+4)
                if model_avg_data[0,:].min() < stat_min \
                        or np.ma.is_masked(stat_min):
                    stat_min = model_avg_data[0,:].min()
                if model_avg_data[0,:].max() > stat_max \
                        or np.ma.is_masked(stat_max):
                    stat_max = model_avg_data[0,:].max()
        #### EMC-evs adjust x axis limits and ticks
        preset_x_axis_tick_min = ax.get_xticks()[0]
        preset_x_axis_tick_max = ax.get_xticks()[-1]
        preset_x_axis_tick_inc = ax.get_xticks()[1] - ax.get_xticks()[0]
        if stat in ['acc', 'msess', 'ets', 'rsd']:
            x_axis_tick_inc = 0.1
        else:
            x_axis_tick_inc = preset_x_axis_tick_inc
        if np.ma.is_masked(stat_min):
            x_axis_min = preset_x_axis_tick_min
        else:
            if stat in ['acc', 'msess', 'ets', 'rsd']:
                x_axis_min = round(stat_min,1) - x_axis_tick_inc
            else:
                x_axis_min = preset_x_axis_tick_min
                while x_axis_min > stat_min:
                    x_axis_min = x_axis_min - x_axis_tick_inc
        if np.ma.is_masked(stat_max):
            x_axis_max = preset_x_axis_tick_max
        else:
            if stat in ['acc', 'msess', 'ets']:
                x_axis_max = 1
            elif stat in ['rsd']:
                x_axis_max = round(stat_max,1) + x_axis_tick_inc
            else:
                x_axis_max = preset_x_axis_tick_max + x_axis_tick_inc
                while x_axis_max < stat_max:
                    x_axis_max = x_axis_max + x_axis_tick_inc
        ax.set_xticks(
            np.arange(x_axis_min, x_axis_max+x_axis_tick_inc, x_axis_tick_inc)
        )
        ax.set_xlim([x_axis_min, x_axis_max])
        # Check x axis limits
        if stat_max >= ax.get_xlim()[1]:
            while stat_max >= ax.get_xlim()[1]:
                x_axis_max = x_axis_max + x_axis_tick_inc
                ax.set_xticks(
                    np.arange(x_axis_min,
                              x_axis_max +  x_axis_tick_inc,
                              x_axis_tick_inc)
                )
                ax.set_xlim([x_axis_min, x_axis_max])
        if stat_min <= ax.get_xlim()[0]:
            while stat_min <= ax.get_xlim()[0]:
                x_axis_min = x_axis_min - x_axis_tick_inc
                ax.set_xticks(
                    np.arange(x_axis_min,
                              x_axis_max +  x_axis_tick_inc,
                              x_axis_tick_inc)
                )
                ax.set_xlim([x_axis_min, x_axis_max])
        # Add legend, adjust if points in legend
        if len(ax.lines) != 0:
            legend = ax.legend(bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                               loc=legend_loc, ncol=legend_ncol,
                               fontsize=legend_fontsize)
            plt.draw()
            legend_box = legend.get_window_extent() \
                .inverse_transformed(ax.transData)
            if stat_min < legend_box.x0:
                while stat_min < legend_box.x0:
                    x_axis_min = x_axis_min - x_axis_tick_inc
                    ax.set_xticks(
                        np.arange(x_axis_min,
                                  x_axis_max + x_axis_tick_inc,
                                  x_axis_tick_inc)
                    )
                    ax.set_xlim([x_axis_min, x_axis_max])
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
            fcst_var_name, 'all', fcst_var_extra, fcst_var_thresh
        )
        vx_mask_title = plot_title.get_vx_mask_title(vx_mask)
        date_info_title = plot_title.get_date_info_title(
            date_type, fcst_valid_hour.split(', '),
            fcst_init_hour.split(', '),
            datetime.datetime.strptime(
                start_date, '%Y%m%d'
            ).strftime('%d%b%Y'),
            datetime.datetime.strptime(
                end_date, '%Y%m%d'
            ).strftime('%d%b%Y'),
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
            savefig_name = savefig_name+'_'+var_name+'_all'
        else:
            savefig_name = savefig_name+'_'+fcst_var_name+'_all'
        if verif_case == 'precip':
            savefig_name = savefig_name+'_'+fcst_var_thresh
        savefig_name = (savefig_name+'_fhr'+fcst_lead[:-4]
                        +'_'+grid_vx_mask+'.png')
        logger.info("Saving image as "+savefig_name)
        plt.savefig(savefig_name)
        plt.clf()
        plt.close('all')
