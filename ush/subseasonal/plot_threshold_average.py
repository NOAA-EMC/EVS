'''
Name: plot_threshold_average.py
Contact(s): Shannon Shields
Abstract: Reads average and CI files from plot_time_series.py
          to make dieoff plots
History Log: First version
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
from plot_util import get_ci_file, get_lead_avg_file

# add metplus directory to path so the wrappers and utilities can be found
sys.path.insert(0, os.path.abspath(os.environ['HOMEMETplus']))
from metplus.util import do_string_sub

#### EMC-evs title creation script
import plot_title as plot_title

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
legend_bbox_x, legend_bbox_y = 0.5, 0.05
legend_fontsize = 15
legend_loc = 'center'
legend_ncol = 5
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
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'noaa.png')
)
noaa_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.1
noaa_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.9325
noaa_logo_alpha = 0.5
nws_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHverif_global'], 'plotting_scripts', 'nws.png')
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
fcst_var_level_list = os.environ['FCST_LEVEL'].split(', ')
fcst_var_thresh_list = [os.environ['FCST_THRESH'].split(', ')]
obs_var_name = os.environ['OBS_VAR']
obs_var_units = os.environ['OBS_UNITS']
obs_var_level_list = os.environ['OBS_LEVEL'].split(', ')
obs_var_thresh_list = [os.environ['OBS_THRESH'].split(', ')]
interp_mthd = os.environ['INTERP_MTHD']
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

# Start looping to make plots
for plot_info in plot_info_list:
    fcst_lead = plot_info[0]
    fcst_var_level = plot_info[1]
    obs_var_level = obs_var_level_list[
        fcst_var_level_list.index(fcst_var_level)
    ]
    fcst_var_threshs = plot_info[2]
    obs_var_threshs = obs_var_thresh_list[
        fcst_var_thresh_list.index(fcst_var_threshs)
    ]
    fcst_var_threshs_format = np.full_like(
        fcst_var_threshs, np.nan, dtype=object
    )
    fcst_var_threshs_val = np.full_like(
        fcst_var_threshs, '--', dtype="<U10"
    )
    fcst_var_thresh_counts = np.arange(0, len(fcst_var_threshs),
                                       dtype=int)
    for fcst_var_thresh in fcst_var_threshs:
        fcst_var_thresh_idx = fcst_var_threshs.index(fcst_var_thresh)
        fcst_var_thresh_symbol, fcst_var_thresh_letter = (
            plot_util.format_thresh(fcst_var_thresh)
        )
        fcst_var_threshs_format[fcst_var_thresh_idx] = fcst_var_thresh_letter
        fcst_var_threshs_val[fcst_var_thresh_idx] = (
            fcst_var_thresh_letter[2:]
        )
    obs_var_threshs_format = np.full_like(
        obs_var_threshs, np.nan, dtype=object
    )
    for obs_var_thresh in obs_var_threshs:
        obs_var_thresh_idx = obs_var_threshs.index(obs_var_thresh)
        obs_var_thresh_symbol, obs_var_thresh_letter = (
            plot_util.format_thresh(obs_var_thresh)
        )
        obs_var_threshs_format[obs_var_thresh_idx] = obs_var_thresh_letter
    logger.info("Working on forecast threshold averages "
                +"for forecast lead "+fcst_lead+" "
                +"for forecast variable "+fcst_var_name+" "+fcst_var_level)
    # Set up base name for file naming convention for lead averages files,
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
        '_fcst_lead_avgs'
        +'_fcst'+fcst_var_name+fcst_var_level
        +'FCSTTHRESHHOLDER'+interp_mthd
        +'_obs'+obs_var_name+obs_var_level
        +'OBSTHRESHHOLDER'+interp_mthd
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
        stat_plot_name = plot_util.get_stat_plot_name(logger, stat)
        if (stat == 'fbar_obar' or stat == 'orate_frate'
                or stat == 'baser_frate'):
            avg_file_cols = ['LEADS', 'VALS', 'OBS_VALS']
        else:
            avg_file_cols = ['LEADS', 'VALS']
        avg_cols_to_array = avg_file_cols[1:]
        CI_file_cols = ['LEADS', 'CI_VALS']
        CI_bar_max_widths = np.append(
            np.diff(fcst_var_thresh_counts),
            fcst_var_thresh_counts[-1]-fcst_var_thresh_counts[-2]
        )/1.5
        CI_bar_min_widths = np.append(
            np.diff(fcst_var_thresh_counts),
            fcst_var_thresh_counts[-1]-fcst_var_thresh_counts[-2]
        )/nmodels
        CI_bar_intvl_widths = (
            (CI_bar_max_widths-CI_bar_min_widths)/nmodels
        )
        stat_min_max_dict = {
            'ax1_stat_min': np.ma.masked_invalid(np.nan),
            'ax1_stat_max': np.ma.masked_invalid(np.nan),
            'ax2_stat_min': np.ma.masked_invalid(np.nan),
            'ax2_stat_max': np.ma.masked_invalid(np.nan)
        }
        # Reading in model lead average files produced from plot_time_series.py
        logger.info("Reading in model data")
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
            model_avg_data = np.empty(
                [len(avg_cols_to_array), len(fcst_var_threshs_format)]
            )
            model_avg_data.fill(np.nan)
            model_CI_data = np.empty(len(fcst_var_threshs_format))
            model_CI_data.fill(np.nan)
            for vt in range(len(fcst_var_threshs_format)):
                fcst_var_thresh = fcst_var_threshs[vt]
                obs_var_thresh = obs_var_threshs[vt]
                fcst_var_thresh_format = fcst_var_threshs_format[vt]
                obs_var_thresh_format = obs_var_threshs_format[vt]
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
                                model_avg_data[col_idx, vt] = (
                                    float(model_avg_file_data_col \
                                          [model_fcst_lead_idx])
                                )
                else:
                    logger.warning("Model "+str(model_num)+" "+model_name+" "
                                   +"with plot name "+model_plot_name+" "
                                   +"file: "+lead_avg_file+" does not exist")
                CI_file = get_ci_file(stat,
                                      model_stat_file,
                                      fcst_lead,
                                      output_base_dir,
                                      ci_method)
                if ci_method != 'NONE':
                    if (stat == 'fbar_obar' or stat == 'orate_frate'
                            or stat == 'baser_frate'):
                        if os.path.exists(CI_file):
                            nrow = sum(1 for line in open(CI_file))
                            if nrow == 0:
                                logger.warning("Model "+str(model_num)+" "
                                               +model_name+" with plot name "
                                               +model_plot_name+" file: "
                                               +CI_file+" empty")
                            else:
                                logger.debug("Model "+str(model_num)+" "
                                             +model_name+" with plot name "
                                             +model_plot_name+" file: "
                                             +CI_file+" exists")
                                model_CI_file_data = pd.read_csv(
                                    CI_file, sep=' ', header=None,
                                    names=CI_file_cols, dtype=str
                                 )
                                model_CI_file_data_leads = (
                                    model_CI_file_data.loc[:]['LEADS'] \
                                    .tolist()
                                )
                                model_CI_file_data_vals = (
                                    model_CI_file_data.loc[:]['CI_VALS'] \
                                    .tolist()
                                )
                                model_fcst_lead_idx = (
                                    model_CI_file_data_leads.index(fcst_lead)
                                )
                                if (model_CI_file_data_vals \
                                    [model_fcst_lead_idx]
                                        != '--'):
                                    model_CI_data[vt] = (
                                        float(model_CI_file_data_vals \
                                              [model_fcst_lead_idx])
                                    )
                        else:
                            logger.warning("Model "+str(model_num)+" "
                                           +model_name+" with plot name "
                                           +model_plot_name+" file: "
                                           +CI_file+" does not exist")
                    else:
                        if model_num != 1:
                            if os.path.exists(CI_file):
                                nrow = sum(1 for line in open(CI_file))
                                if nrow == 0:
                                    logger.warning("Model "+str(model_num)+" "
                                                   +model_name+" with plot "
                                                   +"name "
                                                   +model_plot_name+" file: "
                                                   +CI_file+" empty")
                                else:
                                    logger.debug("Model "+str(model_num)+" "
                                                 +model_name+" with plot "
                                                 +"name "
                                                 +model_plot_name+" file: "
                                                 +CI_file+" exists")
                                    model_CI_file_data = pd.read_csv(
                                        CI_file, sep=' ', header=None,
                                        names=CI_file_cols, dtype=str
                                    )
                                    model_CI_file_data_leads = (
                                        model_CI_file_data.loc[:]['LEADS'] \
                                        .tolist()
                                    )
                                    model_CI_file_data_vals = (
                                        model_CI_file_data.loc[:]['CI_VALS'] \
                                        .tolist()
                                    )
                                    model_fcst_lead_idx = (
                                        model_CI_file_data_leads.index(
                                            fcst_lead
                                        )
                                    )
                                    if (model_CI_file_data_vals \
                                        [model_fcst_lead_idx]
                                            != '--'):
                                        model_CI_data[vt] = (
                                            float(model_CI_file_data_vals \
                                                  [model_fcst_lead_idx])
                                        )
                            else:
                                logger.warning("Model "+str(model_num)+" "
                                               +model_name+" with plot name "
                                               +model_plot_name+" file: "
                                               +CI_file+" does not exist")
            model_avg_data = np.ma.masked_invalid(model_avg_data)
            model_CI_data = np.ma.masked_invalid(model_CI_data)
            if (stat == 'fbar_obar' or stat == 'orate_frate'
                    or stat == 'baser_frate'):
                diff_from_avg_data = model_avg_data[1,:]
            else:
                if model_num == 1:
                    diff_from_avg_data = model_avg_data[0,:]
            if model_num == 1:
                fig, (ax1, ax2) = plt.subplots(2, 1,
                                               figsize=(x_figsize, y_figsize),
                                               sharex=True)
                ax1.grid(True)
                if len(fcst_var_thresh_counts) >= 15:
                    ax1.set_xticks(fcst_var_thresh_counts[::2])
                    ax1.set_xticklabels(fcst_var_threshs_val[::2])
                else:
                    ax1.set_xticks(fcst_var_thresh_counts)
                    ax1.set_xticklabels(fcst_var_threshs_val)
                ax1.set_xlim([fcst_var_thresh_counts[0],
                              fcst_var_thresh_counts[-1]])
                ax1.set_ylabel(average_method.title())
                ax2.grid(True)
                ax2.set_xlabel('Forecast Threshold')
                ax2.set_ylabel('Difference')
                props = {
                    'boxstyle': 'square',
                    'pad': 0.35,
                    'facecolor': 'white',
                    'linestyle': 'solid',
                    'linewidth': 1,
                    'edgecolor': 'black'
                }
                ax2.text(0.995, 1.05,
                         "Note: differences outside the outline bars "
                         +"are significant at the 95% confidence level",
                         ha='right',
                         va='center',
                         fontsize=13,
                         bbox=props,
                         transform=ax2.transAxes)
                ax2.plot(fcst_var_thresh_counts,
                         np.zeros_like(fcst_var_thresh_counts),
                         color='black',
                         linestyle='solid',
                         linewidth=2.0,
                         zorder=4)
                obs_plotted = False
            # plot ax1
            count1 = (
                len(model_avg_data[0,:])
                - np.ma.count_masked(model_avg_data[0,:])
            )
            mfcst_var_thresh_counts = np.ma.array(
                fcst_var_thresh_counts,
                mask=np.ma.getmaskarray(model_avg_data[0,:])
            )
            if count1 != 0:
                ax1.plot(mfcst_var_thresh_counts.compressed(),
                         model_avg_data[0,:].compressed(),
                         color = model_plot_settings_dict['color'],
                         linestyle = model_plot_settings_dict['linestyle'],
                         linewidth = model_plot_settings_dict['linewidth'],
                         marker = model_plot_settings_dict['marker'],
                         markersize = model_plot_settings_dict['markersize'],
                         label = model_plot_name,
                         zorder = (nmodels-model_idx)+4)
                if model_avg_data[0,:].min() \
                        < stat_min_max_dict['ax1_stat_min'] \
                        or np.ma.is_masked(stat_min_max_dict['ax1_stat_min']):
                    stat_min_max_dict['ax1_stat_min'] = (
                        model_avg_data[0,:]
                    ).min()
                if model_avg_data[0,:].max() \
                        > stat_min_max_dict['ax1_stat_max'] \
                        or np.ma.is_masked(stat_min_max_dict['ax1_stat_max']):
                    stat_min_max_dict['ax1_stat_max'] = (
                        model_avg_data[0,:]
                    ).max()
            if (stat == 'fbar_obar' or stat == 'orate_frate'
                    or stat == 'baser_frate'):
                count1_obs = (
                    len(model_avg_data[1,:])
                    - np.ma.count_masked(model_avg_data[1,:])
                )
                mfcst_var_thresh_counts = np.ma.array(
                    fcst_var_thresh_counts,
                    mask=np.ma.getmaskarray(model_avg_data[1,:])
                )
                obs_plot_settings_dict = (
                    model_obs_plot_settings_dict['obs']
                )
                if not obs_plotted:
                    if count1_obs != 0:
                        ax1.plot(mfcst_var_thresh_counts.compressed(),
                                 model_avg_data[1,:].compressed(),
                                 color = obs_plot_settings_dict['color'],
                                 linestyle = obs_plot_settings_dict \
                                     ['linestyle'],
                                 linewidth = obs_plot_settings_dict \
                                     ['linewidth'],
                                 marker = obs_plot_settings_dict \
                                     ['marker'],
                                 markersize = obs_plot_settings_dict \
                                     ['markersize'],
                                 label = 'obs',
                                 zorder = 4)
                        if model_avg_data[1,:].min() \
                                < stat_min_max_dict['ax1_stat_min'] \
                                or np.ma.is_masked(
                                    stat_min_max_dict['ax1_stat_min']
                                ):
                            stat_min_max_dict['ax1_stat_min'] = (
                                model_avg_data[1,:]
                            ).min()
                        if model_avg_data[1,:].max() \
                                > stat_min_max_dict['ax1_stat_max'] \
                                or np.ma.is_masked(
                                    stat_min_max_dict['ax1_stat_max']
                                ):
                            stat_min_max_dict['ax1_stat_max'] = (
                                model_avg_data[1,:]
                            ).max()
                        obs_plotted = True
            # plot ax2
            if (stat == 'fbar_obar' or stat == 'orate_frate'
                    or stat == 'baser_frate'):
                ax2.set_title('Difference from obs', loc='left')
            else:
                ax2.set_title('Difference from '+model_info_list[0][1],
                              loc='left')
            count2 = (
                len(model_avg_data[0,:] - diff_from_avg_data)
                - np.ma.count_masked(model_avg_data[0,:] - diff_from_avg_data)
            )
            mfcst_var_thresh_counts = np.ma.array(
                fcst_var_thresh_counts,
                mask=np.ma.getmaskarray(
                    model_avg_data[0,:] - diff_from_avg_data
                )
            )
            if count2 != 0:
                if model_num == 1 and stat \
                        not in ['fbar_obar', 'orate_frate', 'baser_frate']:
                    plot_linewidth = 2
                else:
                    plot_linewidth = model_plot_settings_dict['linewidth']
                ax2.plot(mfcst_var_thresh_counts.compressed(),
                         (model_avg_data[0,:] - diff_from_avg_data) \
                         .compressed(),
                         color = model_plot_settings_dict['color'],
                         linestyle = model_plot_settings_dict['linestyle'],
                         linewidth = plot_linewidth,
                         marker = model_plot_settings_dict['marker'],
                         markersize = model_plot_settings_dict['markersize'],
                         label = model_plot_name,
                         zorder = (nmodels-model_idx)+4)
                if (model_avg_data[0,:] - diff_from_avg_data).min() \
                        < stat_min_max_dict['ax2_stat_min'] \
                        or np.ma.is_masked(stat_min_max_dict['ax2_stat_min']):
                    stat_min_max_dict['ax2_stat_min'] = (
                        model_avg_data[0,:] - diff_from_avg_data
                    ).min()
                if (model_avg_data[0,:] - diff_from_avg_data).max() \
                        > stat_min_max_dict['ax2_stat_max'] \
                        or np.ma.is_masked(stat_min_max_dict['ax2_stat_max']):
                    stat_min_max_dict['ax2_stat_max'] = (
                        model_avg_data[0,:] - diff_from_avg_data
                    ).max()
            count2_bars = (
                len(model_CI_data)
                - np.ma.count_masked(model_CI_data)
            )
            mfcst_var_thresh_counts = np.ma.array(
                fcst_var_thresh_counts,
                mask=np.ma.getmaskarray(model_CI_data)
            )
            if count2_bars != 0:
                top_bar_data_max = model_CI_data.max()
                bottom_bar_data_min = model_CI_data.max() * -1
                if bottom_bar_data_min < stat_min_max_dict['ax2_stat_min'] \
                        or np.ma.is_masked(stat_min_max_dict['ax2_stat_min']):
                    if not np.ma.is_masked(bottom_bar_data_min):
                        stat_min_max_dict['ax2_stat_min'] = (
                            bottom_bar_data_min
                        )
                if top_bar_data_max > stat_min_max_dict['ax2_stat_max'] \
                        or np.ma.is_masked(stat_min_max_dict['ax2_stat_max']):
                    if not np.ma.is_masked(top_bar_data_max):
                        stat_min_max_dict['ax2_stat_max'] = (
                            top_bar_data_max
                        )
                for fcst_var_thresh_count in fcst_var_thresh_counts:
                    idx = np.where(
                        fcst_var_thresh_counts == fcst_var_thresh_count
                    )[0][0]
                    ax2.bar(fcst_var_thresh_counts[idx],
                            2*np.absolute(model_CI_data[idx]),
                            bottom = -1*np.absolute(model_CI_data[idx]),
                            color = 'None',
                            width = CI_bar_max_widths[idx]-(
                                CI_bar_intvl_widths[idx]*model_idx
                            ),
                            edgecolor = model_plot_settings_dict['color'],
                            linewidth=1)
        #### EMC_evs adjust y axis
        subplot_num = 1
        for ax in fig.get_axes():
           # Adjust y axis limits and ticks
           stat_min = stat_min_max_dict['ax'+str(subplot_num)+'_stat_min']
           stat_max = stat_min_max_dict['ax'+str(subplot_num)+'_stat_max']
           preset_y_axis_tick_min = ax.get_yticks()[0]
           preset_y_axis_tick_max = ax.get_yticks()[-1]
           preset_y_axis_tick_inc = ax.get_yticks()[1] - ax.get_yticks()[0]
           if stat in ['acc', 'msess', 'ets', 'rsd'] and subplot_num == 1:
               y_axis_tick_inc = 0.1
           else:
               y_axis_tick_inc = preset_y_axis_tick_inc
           if np.ma.is_masked(stat_min):
               y_axis_min = preset_y_axis_tick_min
           else:
               if stat in ['acc', 'msess', 'ets', 'rsd'] and subplot_num == 1:
                   y_axis_min = round(stat_min,1) - y_axis_tick_inc
               else:
                   y_axis_min = preset_y_axis_tick_min
                   while y_axis_min > stat_min:
                       y_axis_min = y_axis_min - y_axis_tick_inc
           if np.ma.is_masked(stat_max):
               y_axis_max = preset_y_axis_tick_max
           else:
               if stat in ['acc', 'msess', 'ets'] and subplot_num == 1:
                   y_axis_max = 1
               elif stat in ['rsd'] and subplot_num == 1:
                   y_axis_max = round(stat_max,1) + y_axis_tick_inc
               else:
                   y_axis_max = preset_y_axis_tick_max
                   while y_axis_max < stat_max:
                       y_axis_max = y_axis_max + y_axis_tick_inc
           ax.set_yticks(
               np.arange(y_axis_min,
                         y_axis_max+y_axis_tick_inc,
                         y_axis_tick_inc)
           )
           ax.set_ylim([y_axis_min, y_axis_max])
           # Check y axis limits
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
           subplot_num+=1
        #### EMC-evs add legend, adjust if points in legend
        if len(ax1.lines) != 0:
            y_axis_tick_min = ax1.get_yticks()[0]
            y_axis_tick_max = ax1.get_yticks()[-1]
            y_axis_tick_inc = ax1.get_yticks()[1] - ax1.get_yticks()[0]
            stat_min = stat_min_max_dict['ax1_stat_min']
            stat_max = stat_min_max_dict['ax1_stat_max']
            legend = ax1.legend(bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                                loc=legend_loc, ncol=legend_ncol,
                                fontsize=legend_fontsize)
            plt.draw()
            legend_box = legend.get_window_extent() \
                .inverse_transformed(ax1.transData)
            y_axis_min = y_axis_tick_min
            y_axis_max = y_axis_tick_max
            if stat_min < legend_box.y1:
                while stat_min < legend_box.y1:
                    y_axis_min = y_axis_min - y_axis_tick_inc
                    ax1.set_yticks(
                        np.arange(y_axis_min,
                                  y_axis_max + y_axis_tick_inc,
                                  y_axis_tick_inc)
                    )
                    ax1.set_ylim([y_axis_min, y_axis_max])
                    legend = ax1.legend(
                        bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                        loc=legend_loc, ncol=legend_ncol,
                        fontsize=legend_fontsize
                    )
                    plt.draw()
                    legend_box = (
                        legend.get_window_extent() \
                        .inverse_transformed(ax1.transData)
                    )
        #### EMC-evs build formal plot title
        if verif_grid == vx_mask:
            grid_vx_mask = verif_grid
        else:
            grid_vx_mask = verif_grid+vx_mask
        var_info_title = plot_title.get_var_info_title(
            fcst_var_name, fcst_var_level, fcst_var_extra, 'all'
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
        ax1.set_title(full_title, loc=title_loc)
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
                    savefig_name+'_init'
                    +fcst_init_hour.split(', ')[0][0:2]+'Z'
                )
        if verif_case == 'grid2grid' and verif_type == 'anom':
            savefig_name = savefig_name+'_'+var_name+'_'+fcst_var_level
        else:
            savefig_name = savefig_name+'_'+fcst_var_name+'_'+fcst_var_level
        savefig_name = savefig_name+'_all'
        savefig_name = (savefig_name+'_fhr'+fcst_lead[:-4]+'_'
                        +grid_vx_mask+'.png')
        logger.info("Saving image as "+savefig_name)
        plt.savefig(savefig_name)
        plt.clf()
        plt.close('all')
