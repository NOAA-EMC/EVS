'''
Name: plot_threshold_by_lead.py
Contact(s): Shannon Shields
Abstract: Reads average from plot_time_series.py to make threshold-lead plots
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
import matplotlib.gridspec as gridspec

import plot_util as plot_util
from plot_util import get_lead_avg_file

# add metplus directory to path so the wrappers and utilities can be found
sys.path.insert(0, os.path.abspath(os.environ['HOMEMETplus']))
from metplus.util import do_string_sub

#### EMC-evs title creation script
import plot_title as plot_title

# Plot Settings
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.titlepad'] = 5
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.labelpad'] = 10
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['xtick.major.pad'] = 5
plt.rcParams['ytick.major.pad'] = 5
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['figure.subplot.left'] = 0.1
plt.rcParams['figure.subplot.right'] = 0.95
plt.rcParams['figure.titleweight'] = 'bold'
plt.rcParams['figure.titlesize'] = 16
title_loc = 'center'
cmap_bias = plt.cm.PiYG_r
cmap = plt.cm.BuPu
cmap_diff = plt.cm.coolwarm_r
noaa_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHevs'], 'subseasonal', 'noaa.png')
)
noaa_logo_alpha = 0.5
nws_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHevs'], 'subseasonal', 'nws.png')
)
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
fcst_lead_list = [os.environ['FCST_LEAD'].split(', ')]
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
    fcst_leads = plot_info[0]
    fcst_lead_timedeltas = np.full_like(fcst_leads, np.nan, dtype=float)
    for fcst_lead in fcst_leads:
        fcst_lead_idx = fcst_leads.index(fcst_lead)
        fcst_lead_timedelta = datetime.timedelta(
            hours=int(fcst_lead[:-4]),
            minutes=int(fcst_lead[-4:-2]),
            seconds=int(fcst_lead[-2:])
        ).total_seconds()
        fcst_lead_timedeltas[fcst_lead_idx] = float(fcst_lead_timedelta)
    fcst_lead_timedeltas_str = []
    for tdelta in fcst_lead_timedeltas:
        h = int(tdelta/3600)
        m = int((tdelta-(h*3600))/60)
        s = int(tdelta-(h*3600)-(m*60))
        if h < 10:
            tdelta_str = f"{h:01d}"
        elif h < 100:
            tdelta_str = f"{h:02d}"
        else:
            tdelta_str = f"{h:03d}"
        if m != 0:
            tdelta_str+=f":{m:02d}"
        if s != 0:
            tdelta_str+=f":{s:02d}"
        fcst_lead_timedeltas_str.append(tdelta_str)
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
    xmesh, ymesh = np.meshgrid(fcst_var_thresh_counts, fcst_lead_timedeltas)
    obs_var_threshs_format = np.full_like(
        obs_var_threshs, np.nan, dtype=object
    )
    for obs_var_thresh in obs_var_threshs:
        obs_var_thresh_idx = obs_var_threshs.index(obs_var_thresh)
        obs_var_thresh_symbol, obs_var_thresh_letter = (
            plot_util.format_thresh(obs_var_thresh)
        )
        obs_var_threshs_format[obs_var_thresh_idx] = obs_var_thresh_letter
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
            nsubplots = nmodels + 1
        else:
            nsubplots = nmodels
        if nsubplots == 1:
            x_figsize, y_figsize = 14, 7
            row, col = 1, 1
            hspace, wspace = 0, 0
            bottom, top = 0.175, 0.825
            suptitle_y_loc = 0.92125
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.865
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.865
            cbar_bottom = 0.06
            cbar_height = 0.02
        elif nsubplots == 2:
            x_figsize, y_figsize = 14, 7
            row, col = 1, 2
            hspace, wspace = 0, 0.1
            bottom, top = 0.175, 0.825
            suptitle_y_loc = 0.92125
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.865
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.865
            cbar_bottom = 0.06
            cbar_height = 0.02
        elif nsubplots > 2 and nsubplots <= 4:
            x_figsize, y_figsize = 14, 14
            row, col = 2, 2
            hspace, wspace = 0.15, 0.1
            bottom, top = 0.125, 0.9
            suptitle_y_loc = 0.9605
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
            cbar_bottom = 0.03
            cbar_height = 0.02
        elif nsubplots > 4 and nsubplots <= 6:
            x_figsize, y_figsize = 14, 14
            row, col = 3, 2
            hspace, wspace = 0.15, 0.1
            bottom, top = 0.125, 0.9
            suptitle_y_loc = 0.9605
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
            cbar_bottom = 0.03
            cbar_height = 0.02
        elif nsubplots > 6 and nsubplots <= 8:
            x_figsize, y_figsize = 14, 14
            row, col = 4, 2
            hspace, wspace = 0.175, 0.1
            bottom, top = 0.125, 0.9
            suptitle_y_loc = 0.9605
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
            cbar_bottom = 0.03
            cbar_height = 0.02
        elif nsubplots > 8 and nsubplots <= 10:
            x_figsize, y_figsize = 14, 14
            row, col = 5, 2
            hspace, wspace = 0.225, 0.1
            bottom, top = 0.125, 0.9
            suptitle_y_loc = 0.9605
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
            cbar_bottom = 0.03
            cbar_height = 0.02
        else:
            logger.error("Too many subplots selected, max. is 10")
            sys.exit(1)
        if (stat == 'fbar_obar' or stat == 'orate_frate'
                or stat == 'baser_frate'):
            avg_file_cols = ['LEADS', 'VALS', 'OBS_VALS']
        else:
            avg_file_cols = ['LEADS', 'VALS']
        suptitle_x_loc = (plt.rcParams['figure.subplot.left']
                         +plt.rcParams['figure.subplot.right'])/2.
        fig = plt.figure(figsize=(x_figsize, y_figsize))
        gs = gridspec.GridSpec(
            row, col,
            bottom = bottom, top = top,
            hspace = hspace, wspace = wspace,
        )
        noaa_logo_xpixel_loc = (
            x_figsize * plt.rcParams['figure.dpi'] * noaa_logo_x_scale
        )
        noaa_logo_ypixel_loc = (
            y_figsize * plt.rcParams['figure.dpi'] * noaa_logo_y_scale
        )
        nws_logo_xpixel_loc = (
            x_figsize * plt.rcParams['figure.dpi'] * nws_logo_x_scale
        )
        nws_logo_ypixel_loc = (
            y_figsize * plt.rcParams['figure.dpi'] * nws_logo_y_scale
        )
        #### EMC_evs set up subplots
        subplot_num = 0
        while subplot_num < nsubplots:
            ax = plt.subplot(gs[subplot_num])
            ax.grid(True)
            if len(fcst_var_thresh_counts) >= 15:
                ax.set_xticks(fcst_var_thresh_counts[::2])
                ax.set_xticklabels(fcst_var_threshs_val[::2])
            elif len(fcst_var_thresh_counts) >= 25:
                ax.set_xticks(fcst_var_thresh_counts[::4])
                ax.set_xticklabels(fcst_var_threshs_val[::4])
            else:
                ax.set_xticks(fcst_var_thresh_counts)
                ax.set_xticklabels(fcst_var_threshs_val)
            ax.set_xlim([fcst_var_thresh_counts[0],
                         fcst_var_thresh_counts[-1]])
            if ax.is_last_row() \
                    or (nsubplots % 2 != 0 and subplot_num == nsubplots -1):
                ax.set_xlabel('Forecast Threshold')
            else:
                plt.setp(ax.get_xticklabels(), visible=False)
            if len(fcst_lead_timedeltas) >= 15:
                ax.set_yticks(fcst_lead_timedeltas[::2])
                ax.set_yticklabels(fcst_lead_timedeltas_str[::2])
            elif len(fcst_lead_timedeltas) >= 25:
                ax.set_yticks(fcst_lead_timedeltas[::4])
                ax.set_yticklabels(fcst_lead_timedeltas_str[::4])
            else:
                ax.set_yticks(fcst_lead_timedeltas)
                ax.set_yticklabels(fcst_lead_timedeltas_str)
            ax.set_ylim([fcst_lead_timedeltas[0],
                         fcst_lead_timedeltas[-1]])
            if ax.is_first_col() \
                    or (nsubplots % 2 != 0 and subplot_num == nsubplots -1):
                ax.set_ylabel('Forecast Hour')
            else:
                plt.setp(ax.get_yticklabels(), visible=False)
            subplot_num+=1
        avg_cols_to_array = avg_file_cols[1:]
        # Reading in model lead average files produced from plot_time_series.py
        obs_plotted = False
        get_clevels = True
        make_colorbar = False
        logger.info("Reading in model data")
        for model_info in model_info_list:
            model_num = model_info_list.index(model_info) + 1
            model_idx = model_info_list.index(model_info)
            model_name = model_info[0]
            model_plot_name = model_info[1]
            model_obtype = model_info[2]
            model_avg_data = np.empty(
                [len(avg_cols_to_array), len(fcst_leads),
                 len(fcst_var_threshs_format)]
            )
            model_avg_data.fill(np.nan)
            for vt in range(len(fcst_var_threshs_format)):
                fcst_var_thresh = fcst_var_threshs[vt]
                obs_var_thresh = obs_var_threshs[vt]
                fcst_var_thresh_format = fcst_var_threshs_format[vt]
                obs_var_thresh_format = obs_var_threshs_format[vt]
                logger.info("Working on forecast lead averages "
                            +"for forecast variable "+fcst_var_name+" "
                            +fcst_var_level+" "+fcst_var_thresh_format)
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
                        for fcst_lead in fcst_leads:
                            fcst_lead_idx = fcst_leads.index(fcst_lead)
                            if fcst_lead in model_avg_file_data_leads:
                                model_fcst_lead_idx = (
                                    model_avg_file_data_leads.index(
                                        fcst_lead
                                    )
                                )
                            for col in avg_cols_to_array:
                                col_idx = avg_cols_to_array.index(col)
                                model_avg_file_data_col = (
                                    model_avg_file_data.loc[:][col].tolist()
                                )
                                if (model_avg_file_data_col\
                                        [model_fcst_lead_idx]
                                        != '--'):
                                    model_avg_data[col_idx,
                                                   fcst_lead_idx, vt] = (
                                        float(model_avg_file_data_col \
                                              [model_fcst_lead_idx])
                                    )
                else:
                    logger.warning("Model "+str(model_num)+" "+model_name+" "
                                   +"with plot name "+model_plot_name+" "
                                   +"file: "+lead_avg_file+" does not exist")
            model_avg_data = np.ma.masked_invalid(model_avg_data)
            if (stat == 'fbar_obar' or stat == 'orate_frate'
                    or stat == 'baser_frate'):
                if not obs_plotted:
                    obs_avg_data = model_avg_data[1,:,:]
                    ax = plt.subplot(gs[0])
                    ax.set_title('obs', loc='left')
                    if not model_avg_data[1,:,:].mask.all():
                        logger.debug("Plotting observations")
                        obs_avg_data = model_avg_data[1,:,:]
                        CF1 = ax.contourf(xmesh, ymesh, obs_avg_data,
                                          cmap=cmap,
                                          locator=matplotlib\
                                              .ticker.MaxNLocator(
                                              symmetric=True
                                          ), extend='both')
                        C1 = ax.contour(xmesh, ymesh, obs_avg_data,
                                        levels=CF1.levels,
                                        colors='k',
                                        linewidths=1.0)
                        ax.clabel(C1, CF1.levels,
                                  fmt='%1.2f',
                                  inline=True,
                                  fontsize=12.5)
                        obs_plotted = True
                ax = plt.subplot(gs[model_num])
                ax.set_title(model_plot_name+'-obs', loc='left')
                model_obs_diff = (
                    model_avg_data[0,:,:]
                    - model_avg_data[1,:,:]
                )
                if not model_obs_diff.mask.all():
                    logger.debug("Plotting model "+str(model_num)+" "
                                 +model_name+" - obs "
                                 +"with name on plot "+model_plot_name+" "
                                 +"- obs")
                    if get_clevels:
                        clevels_diff = plot_util.get_clevels(model_obs_diff)
                        CF2 = ax.contourf(xmesh, ymesh, model_obs_diff,
                                          levels=clevels_diff,
                                          cmap=cmap_diff,
                                          locator= matplotlib\
                                              .ticker.MaxNLocator(
                                              symmetric=True
                                          ),
                                          extend='both')
                        get_clevels = False
                        make_colorbar = True
                        colorbar_CF = CF2
                        colorbar_CF_ticks = CF2.levels
                        colorbar_label = 'Difference'
                    else:
                        CF = ax.contourf(xmesh, ymesh, model_obs_diff,
                                         levels=CF2.levels,
                                         cmap=cmap_diff,
                                         locator= matplotlib\
                                             .ticker.MaxNLocator(
                                             symmetric=True
                                         ),
                                         extend='both')
            elif stat == 'bias' or stat == 'fbias':
                ax = plt.subplot(gs[model_idx])
                ax.set_title(model_plot_name, loc='left')
                if not model_avg_data[0,:,:].mask.all():
                    logger.debug("Plotting model "+str(model_num)
                                 +" "+model_name+" with name on plot "
                                 +model_plot_name)
                    if get_clevels:
                        #clevels_bias = plot_util.get_clevels(
                        #    model_avg_data[0,:,:]
                        # )
                        clevels_bias = np.array(
                            [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8]
                        )
                        CF1 = ax.contourf(xmesh, ymesh, model_avg_data[0,:,:],
                                          levels=clevels_bias,
                                          cmap=cmap_bias,
                                          locator=\
                                          matplotlib.ticker.MaxNLocator(
                                              symmetric=True
                                          ), extend='both')
                        C1 = ax.contour(xmesh, ymesh, model_avg_data[0,:,:],
                                        levels=CF1.levels,
                                        colors='k',
                                        linewidths=1.0)
                        ax.clabel(C1, C1.levels,
                                  fmt='%1.2f',
                                  inline=True,
                                  fontsize=12.5)
                        get_clevels = False
                        make_colorbar = True
                        colorbar_CF = CF1
                        colorbar_CF_ticks = CF1.levels
                        colorbar_label = 'Bias'
                    else:
                        CF = ax.contourf(xmesh, ymesh, model_avg_data[0,:,:],
                                         levels=CF1.levels,
                                         cmap=cmap_bias,
                                         locator=\
                                         matplotlib.ticker.MaxNLocator(
                                              symmetric=True
                                         ), extend='both')
                        C = ax.contour(xmesh, ymesh, model_avg_data[0,:,:],
                                       levels=CF1.levels,
                                       colors='k',
                                       linewidths=1.0)
                        ax.clabel(C, C.levels,
                                  fmt='%1.2f',
                                  inline=True,
                                  fontsize=12.5)
            else:
                ax = plt.subplot(gs[model_idx])
                if model_num == 1:
                    model1_name = model_name
                    model1_plot_name = model_plot_name
                    model1_avg_data = model_avg_data[0,:,:]
                    ax.set_title(model_plot_name, loc='left')
                    if not model1_avg_data.mask.all():
                        logger.debug("Plotting model "+str(model_num)+" "
                                     +model_name+" with name on plot "
                                     +model_plot_name)
                        CF1 = ax.contourf(xmesh, ymesh, model_avg_data[0,:,:],
                                          cmap=cmap,
                                          extend='both')
                        C1 = ax.contour(xmesh, ymesh, model_avg_data[0,:,:],
                                        levels=CF1.levels,
                                        colors='k',
                                        linewidths=1.0)
                        ax.clabel(C1, C1.levels,
                                  fmt='%1.2f',
                                  inline=True,
                                  fontsize=12.5)
                else:
                    ax.set_title(model_plot_name+'-'+model1_plot_name,
                                 loc='left')
                    model_model1_diff = (model_avg_data[0,:,:]
                                         - model1_avg_data)
                    if not model_model1_diff.mask.all():
                        logger.debug("Plotting model "+str(model_num)+" "
                                     +model_name+" - model 1 "+model1_name+" "
                                     +"with name on plot "+model_plot_name+" "
                                     +"- "+model1_plot_name)
                        if get_clevels:
                            clevels_diff = plot_util.get_clevels(
                                model_model1_diff
                            )
                            CF2 = ax.contourf(xmesh, ymesh, model_model1_diff,
                                              levels=clevels_diff,
                                              cmap=cmap_diff,
                                              locator= \
                                              matplotlib.ticker.MaxNLocator(
                                                  symmetric=True
                                              ),
                                              extend='both')
                            get_clevels = False
                            make_colorbar = True
                            colorbar_CF = CF2
                            colorbar_CF_ticks = CF2.levels
                            colorbar_label = 'Difference'
                        else:
                            CF = ax.contourf(xmesh, ymesh, model_model1_diff,
                                             levels=CF2.levels,
                                             cmap=cmap_diff,
                                             locator= \
                                             matplotlib.ticker.MaxNLocator(
                                                 symmetric=True
                                             ),
                                             extend='both')
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
        full_title = (
            stat_plot_name+'\n'
            +var_info_title+', '+vx_mask_title+'\n'
            +date_info_title
        )
        fig.suptitle(full_title,
                     x = suptitle_x_loc, y = suptitle_y_loc,
                     horizontalalignment = title_loc,
                     verticalalignment = title_loc)
        noaa_img = fig.figimage(noaa_logo_img_array,
                                noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
                                zorder=1, alpha=noaa_logo_alpha)
        nws_img = fig.figimage(nws_logo_img_array,
                               nws_logo_xpixel_loc, nws_logo_ypixel_loc,
                               zorder=1, alpha=nws_logo_alpha)
        plt.subplots_adjust(
            left = noaa_img.get_extent()[1] \
                   /(plt.rcParams['figure.dpi']*x_figsize),
            right = nws_img.get_extent()[0] \
                    /(plt.rcParams['figure.dpi']*x_figsize)
        )
        #### EMC-evs add colorbar
        cbar_left = (
            noaa_img.get_extent()[1]/(plt.rcParams['figure.dpi']*x_figsize)
        )
        cbar_width = (
            nws_img.get_extent()[0]/(plt.rcParams['figure.dpi']*x_figsize)
            - noaa_img.get_extent()[1]/(plt.rcParams['figure.dpi']*x_figsize)
        )
        if make_colorbar:
            cax = fig.add_axes(
                [cbar_left, cbar_bottom, cbar_width, cbar_height]
            )
            cbar = fig.colorbar(colorbar_CF,
                                cax = cax,
                                orientation = 'horizontal',
                                ticks = colorbar_CF_ticks)
            cbar.ax.set_xlabel(colorbar_label, labelpad = 0)
            cbar.ax.xaxis.set_tick_params(pad=0)
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
        if verif_case == 'precip':
            savefig_name = savefig_name+'_all'
        savefig_name = savefig_name+'_fhrmean_'+grid_vx_mask+'.png'
        plt.savefig(savefig_name)
        plt.clf()
        plt.close('all')
