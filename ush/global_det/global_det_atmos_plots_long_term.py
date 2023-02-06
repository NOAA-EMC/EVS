'''
Name: global_det_atmos_plots_long_term.py
Contact(s): Mallory Row
Abstract: This script generates monthly long term stats plots.
'''

import sys
import os
import logging
import datetime
import dateutil
from dateutil.relativedelta import relativedelta
import calendar
import glob
import subprocess
import pandas as pd
pd.plotting.deregister_matplotlib_converters()
#pd.plotting.register_matplotlib_converters()
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import itertools
import global_det_atmos_util as gda_util
from global_det_atmos_plots_specs import PlotSpecs

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

def create_merged_dataset(logger, model_group_tuple, evs_var, evs_level, evs_vx_mask,
                          evs_stat, YYYYmm_dt_list):
    """! Create dataframe comprised of all verification systems
         Args:
             logger            - logger object
             model_group_tuple - tuple of model group name and
                                 list of models (strings)
             evs_var           - variable name in EVS (string)
             evs_level         - variable level in EVS (string)
             evs_vx_mask       - verification region in EVS (string)
             evs_stat          - statistic in EVS (string)
             YYYYmm_dt_list    - list of year and month datetime
                                 objects
         Returns:
             merged_df      - dataframe of stats from all
                              verification systems
    """
    logger.info("Reading data and creating merged dataset")
    # Set expected file columns
    expected_file_columns = [
        'SYS', 'YEAR', 'MONTH', 'DAY0', 'DAY1', 'DAY2', 'DAY3', 'DAY4',
        'DAY5', 'DAY6', 'DAY7', 'DAY8', 'DAY9', 'DAY10', 'DAY11', 'DAY12',
        'DAY13', 'DAY14', 'DAY15', 'DAY16'
    ] 
    # Merge dates
    verif_sys_start_date_dict = {
        'caplan_zhu': YYYYmm_dt_list[0].strftime('%Y%m'),
        'vsdb': '200801',
        'emc_verif_global': '202101',
        'evs': '202309'
    }
    # Mapping of verification system file notations
    if evs_var == 'UGRD_VGRD':
        if evs_stat == 'ME':
            caplan_zhu_var = 'SPD'
        else:
            caplan_zhu_var = 'UV'
        vsdb_var = 'WIND'
        emc_verif_global_var = evs_var
    else:
        caplan_zhu_var = evs_var
        vsdb_var = evs_var
        emc_verif_global_var = evs_var
    if evs_var == 'HGT':
        caplan_zhu_level = evs_level.replace('P', '')+'hpa'
    else:
        caplan_zhu_level = evs_level.replace('P', '')+'hPa'
    vsdb_level = evs_level
    emc_verif_global_level = evs_level
    if evs_vx_mask in ['NHEM', 'SHEM']:
        caplan_zhu_vx_mask = evs_vx_mask[0:2]
        vsdb_vx_mask = evs_vx_mask[0:2]+'X'
        emc_verif_global_vx_mask = evs_vx_mask[0:2]+'X'
    elif evs_vx_mask == 'TROPICS':
        caplan_zhu_vx_mask = evs_vx_mask.title()
        vsdb_vx_mask = evs_vx_mask[0:3]
        emc_verif_global_vx_mask = evs_vx_mask[0:3]
    else:
        caplan_zhu_vx_mask = evs_vx_mask
        vsdb_vx_mask = evs_vx_mask
        emc_verif_global_vx_mask = evs_vx_mask
    if evs_stat == 'ACC':
        caplan_zhu_stat = evs_stat.upper()[0:2]+'Wave1-20'
        vsdb_stat = evs_stat.upper()[0:2]
        emc_verif_global_stat = evs_stat.upper()
    elif evs_stat == 'ME':
        caplan_zhu_stat = 'Error'
        vsdb_stat = 'BIAS'
        emc_verif_global_stat = 'BIAS'
    elif evs_stat == 'RMSE':
        caplan_zhu_stat = evs_stat
        vsdb_stat = evs_stat
        emc_verif_global_stat = evs_stat
    else:
        caplan_zhu_stat = evs_stat
        vsdb_stat = evs_stat
        emc_verif_global_stat = evs_stat
    # Get individual model files paths and put in dataframe
    model_group = model_group_tuple[0]
    model_list = model_group_tuple[1]
    for model in model_list:
        if model_group == 'gfs_4cycles':
            valid_hour = model.replace('gfs', '')
            model_caplan_zhu_file_name = os.path.join(
                COMINmonthlystats, model.replace(valid_hour, ''),
                'caplan_zhu_'+caplan_zhu_var+caplan_zhu_stat
                +'_'+caplan_zhu_level+'_'+caplan_zhu_vx_mask+'_valid'
                +valid_hour+'.txt'
            )
            model_vsdb_file_name = os.path.join(
                COMINmonthlystats, model.replace(valid_hour, ''),
                'vsdb_'+vsdb_stat+'_'+vsdb_var+'_'+vsdb_level+'_G2'
                +vsdb_vx_mask+'_valid'+valid_hour+'.txt'
            )
            model_emc_verif_global_file_name = os.path.join(
                COMINmonthlystats, model.replace(valid_hour, ''),
                'emc_verif_global_'+emc_verif_global_stat+'_'
                +emc_verif_global_var+'_'+emc_verif_global_level
                +'_'+emc_verif_global_vx_mask+'_valid'+valid_hour+'.txt'
            )
            model_evs_file_name = os.path.join(
                COMINmonthlystats, model.replace(valid_hour, ''),
                'evs_'+evs_stat+'_'+evs_var+'_'+evs_level+'_'+evs_vx_mask
                +'_valid'+valid_hour+'.txt'
            )
        else:
            model_caplan_zhu_file_name = os.path.join(
                COMINmonthlystats, model,
                'caplan_zhu_'+caplan_zhu_var+caplan_zhu_stat
                +'_'+caplan_zhu_level+'_'+caplan_zhu_vx_mask+'_valid00Z.txt'
            )
            model_vsdb_file_name = os.path.join(
                COMINmonthlystats, model,
                'vsdb_'+vsdb_stat+'_'+vsdb_var+'_'+vsdb_level+'_G2'
                +vsdb_vx_mask+'_valid00Z.txt'
            )
            model_emc_verif_global_file_name = os.path.join(
                COMINmonthlystats, model,
                'emc_verif_global_'+emc_verif_global_stat+'_'
                +emc_verif_global_var+'_'+emc_verif_global_level
                +'_'+emc_verif_global_vx_mask+'_valid00Z.txt'
            )
            model_evs_file_name = os.path.join(
                COMINmonthlystats, model,
                'evs_'+evs_stat+'_'+evs_var+'_'+evs_level+'_'+evs_vx_mask
                +'_valid00Z.txt'
            )
        logger.debug(f"{model} Caplan-Zhu File: {model_caplan_zhu_file_name}")
        logger.debug(f"{model} VSDB File: {model_vsdb_file_name}")
        logger.debug(f"{model} EMC_verif-global File: "
                     +f"{model_emc_verif_global_file_name}")
        logger.debug(f"{model} EVS File: {model_evs_file_name}")
        for model_verif_sys_file_name in [model_caplan_zhu_file_name,
                                          model_vsdb_file_name,
                                          model_emc_verif_global_file_name,
                                          model_evs_file_name]:
            if os.path.exists(model_verif_sys_file_name):
                model_verif_sys_df = pd.read_table(model_verif_sys_file_name,
                                                   delimiter=' ', dtype='str',
                                                   skipinitialspace=True)
                if 'caplan_zhu' not in model_verif_sys_file_name:
                    model_all_verif_sys_df = model_all_verif_sys_df.append(
                        model_verif_sys_df, ignore_index=True
                    )
                else:
                    model_all_verif_sys_df = model_verif_sys_df.copy()
        model_merged_df = pd.DataFrame(
            index=pd.MultiIndex.from_product(
                [[model], [f"{dt:%Y%m}" for dt in YYYYmm_dt_list]],
                names=['model', 'YYYYmm']
            ),
            columns=expected_file_columns
        )
        for YYYYmm_dt in YYYYmm_dt_list:
            if YYYYmm_dt \
                    >= datetime.datetime.strptime(
                        verif_sys_start_date_dict['caplan_zhu'], '%Y%m'
                    ) \
                    and YYYYmm_dt < datetime.datetime.strptime(
                        verif_sys_start_date_dict['vsdb'], '%Y%m'
                    ):
                YYYYmm_dt_verif_sys = 'CZ'
            elif YYYYmm_dt \
                    >= datetime.datetime.strptime(
                        verif_sys_start_date_dict['vsdb'], '%Y%m'
                    ) \
                    and YYYYmm_dt < datetime.datetime.strptime(
                        verif_sys_start_date_dict['emc_verif_global'], '%Y%m'
                    ):
                YYYYmm_dt_verif_sys = 'VSDB'
            elif YYYYmm_dt \
                    >= datetime.datetime.strptime(
                        verif_sys_start_date_dict['emc_verif_global'], '%Y%m'
                    ) \
                    and YYYYmm_dt < datetime.datetime.strptime(
                        verif_sys_start_date_dict['evs'], '%Y%m'
                    ):
                YYYYmm_dt_verif_sys = 'EVG'
            else:
                YYYYmm_dt_verif_sys = 'EVS'
            model_verif_sys_YYYYmm_df = model_all_verif_sys_df.loc[
                (model_all_verif_sys_df['SYS'] == YYYYmm_dt_verif_sys)
                & (model_all_verif_sys_df['YEAR'] == f"{YYYYmm_dt:%Y}")
                & (model_all_verif_sys_df['MONTH'] == f"{YYYYmm_dt:%m}")
            ]
            if len(model_verif_sys_YYYYmm_df) == 0:
                model_merged_verif_sys_YYYYmm_values = []
                for col in expected_file_columns:
                    if col == 'SYS':
                        model_merged_verif_sys_YYYYmm_values.append(
                            YYYYmm_dt_verif_sys
                        )
                    elif col == 'YEAR':
                        model_merged_verif_sys_YYYYmm_values.append(
                            f"{YYYYmm_dt:%Y}"
                        )
                    elif col == 'MONTH':
                        model_merged_verif_sys_YYYYmm_values.append(
                            f"{YYYYmm_dt:%m}"
                        )
                    else:
                         model_merged_verif_sys_YYYYmm_values.append(np.nan)
            else:
                model_merged_verif_sys_YYYYmm_values = (
                    model_verif_sys_YYYYmm_df.values[0]
                )
            model_merged_df.loc[(model,f"{YYYYmm_dt:%Y%m}")] = (
                model_merged_verif_sys_YYYYmm_values
            )
        if model_list.index(model) == 0:
            merged_df = model_merged_df
        else:
            merged_df = pd.concat([merged_df, model_merged_df])
    return merged_df

def create_plots(logger, model_group, model_group_merged_df, plot_var,
                 plot_level, plot_vx_mask, plot_stat, plot_run_length,
                 logo_dir, images_dir):
    """! Create verification graphics
         Args:
             logger                - logger object
             model_group           - name model group name (strings)
             model_group_merged_df - dataframe for all models in model_group
                                     for all verification systems
             plot_var              - plotting variable name (string)
             plot_level            - plotting variable level (string)
             plot_vx_mask          - plotting verification region (string)
             plot_stat             - plotting statistic (string)
             plot_run_length       - plotting run length:
                                     allyears, past10years (string)
             logo_dir              - full path to logo directory
                                     (string)
             images_dir            - full path to output image directory
                                     (string)
         Returns:
    """
    logger.info(f"Creating plots for {plot_run_length}") 
    model_list = (model_group_merged_df.index.get_level_values(0)\
                  .unique().tolist())
    YYYYmm_list = (model_group_merged_df.index.get_level_values(1)\
                   .unique().tolist())
    plot_forecast_days = [str(x) for x in np.arange(1,11,1)]
    if plot_run_length == 'allyears':
        plot_run_length_running_mean = 3
        plot_run_length_YYYYmm_list = YYYYmm_list
    elif plot_run_length == 'past10years':
        plot_run_length_running_mean = 1
        tenyearsago_dt = (datetime.datetime.strptime(YYYYmm_list[-1], '%Y%m')
                          - relativedelta(years=10))
        plot_run_length_YYYYmm_list = (
            YYYYmm_list[YYYYmm_list.index(f"{tenyearsago_dt:%Y%m}"):]
        )
    plot_run_length_YYYYmm_dt_list = [
        datetime.datetime.strptime(YYYYmm, '%Y%m') for YYYYmm \
        in plot_run_length_YYYYmm_list
    ]
    # Common plot settings
    plot_left_logo = False
    plot_left_logo_path = os.path.join(logo_dir, 'noaa.png')
    if os.path.exists(plot_left_logo_path):
        plot_left_logo = True
        left_logo_img_array = matplotlib.image.imread(plot_left_logo_path)
    plot_right_logo = False
    plot_right_logo_path = os.path.join(logo_dir, 'nws.png')
    if os.path.exists(plot_right_logo_path):
        plot_right_logo = True
        right_logo_img_array = matplotlib.image.imread(plot_right_logo_path)
    if plot_var == 'HGT':
        plot_var_units = 'gpm'
    elif plot_var == 'UGRD_VGRD':
        plot_var_units = 'm/s'
    if model_group == 'gfs_4cycles':
        plot_hour = 'init 00Z, 06Z, 12Z, 18Z'
    else:
        plot_hour = 'valid 00Z'
    # Calculate running mean
    model_group_running_mean_df = pd.DataFrame(
        index=model_group_merged_df.index,
        columns=[f"DAY{str(x)}" for x in plot_forecast_days]
    )
    for model in model_list:
        for plot_forecast_day in plot_forecast_days:
            model_forecast_day = (model_group_merged_df.loc[(model)]\
                                  ['DAY'+str(plot_forecast_day)]\
                                  .to_numpy(dtype=float))
            for m in range(len(model_forecast_day)):
                start = m-int(plot_run_length_running_mean/2)
                end = m+int(plot_run_length_running_mean/2)
                if start >= 0 and end < len(model_forecast_day):
                    model_group_running_mean_df.loc[
                        (model,plot_run_length_YYYYmm_list[m])
                    ]['DAY'+str(plot_forecast_day)] = (
                        model_forecast_day[start:end+1].mean()
                    )
    # Make time series plots for each forecast day with differences
    plot_specs_lttsd = PlotSpecs(logger, 'long_term_time_series_diff')
    plot_specs_lttsd.set_up_plot()
    left_logo_xpixel_loc, left_logo_ypixel_loc, left_logo_alpha = (
        plot_specs_lttsd.get_logo_location(
            'left', plot_specs_lttsd.fig_size[0],
            plot_specs_lttsd.fig_size[1], plt.rcParams['figure.dpi']
        )
    )
    right_logo_xpixel_loc, right_logo_ypixel_loc, right_logo_alpha = (
        plot_specs_lttsd.get_logo_location(
            'right', plot_specs_lttsd.fig_size[0],
            plot_specs_lttsd.fig_size[1], plt.rcParams['figure.dpi']
        )
    )
    all_model_plot_settings_dict = plot_specs_lttsd.get_model_plot_settings()
    for plot_forecast_day in plot_forecast_days:
        plot_forecast_hour = str(int(plot_forecast_day)*24)
        logger.debug("Creating time series plot for "
                     +f"forecast day {plot_forecast_day}, "
                     +f"forecast hour {plot_forecast_hour}")
        image_name = os.path.join(
            images_dir, f"evs.global_det.{model_group}.{plot_stat}.".lower()
            +f"{plot_var}_{plot_level}.{plot_run_length}.timeseries_".lower()
            +f"{plot_hour.replace(' ', '').replace(',','')}_".lower()
            +f"f{plot_forecast_hour.zfill(3)}.g004_{plot_vx_mask}.png".lower()
        )
        stat_min_max_dict = {
            'ax1_stat_min': np.ma.masked_invalid(np.nan),
            'ax1_stat_max': np.ma.masked_invalid(np.nan),
            'ax2_stat_min': np.ma.masked_invalid(np.nan),
            'ax2_stat_max': np.ma.masked_invalid(np.nan)
        }
        fig, (ax1, ax2) = plt.subplots(2,1,
                                       figsize=(plot_specs_lttsd.fig_size[0],
                                                plot_specs_lttsd.fig_size[1]),
                                       sharex=True)
        fig.suptitle(
            plot_specs_lttsd.get_stat_plot_name(plot_stat)+' - G004/'
            +plot_specs_lttsd.get_vx_mask_plot_name(plot_vx_mask)+'\n'
            +plot_specs_lttsd.get_var_plot_name(plot_var, plot_level)+" "
            +f"({plot_var_units})\n"
            +f"valid {plot_run_length_YYYYmm_dt_list[0]:%b%Y}-"
            +f"valid {plot_run_length_YYYYmm_dt_list[-1]:%b%Y} {plot_hour}, "
            +f"Forecast Day {plot_forecast_day} (Hour {plot_forecast_hour})\n"
            +f"{plot_run_length_running_mean} Month Running Mean"
        )
        ax1.grid(True)
        ax1.set_xlim([plot_run_length_YYYYmm_dt_list[0],
                      plot_run_length_YYYYmm_dt_list[-1]])
        ax1.set_xticks(plot_run_length_YYYYmm_dt_list[::24])
        ax1.xaxis.set_major_formatter(md.DateFormatter('%Y'))
        ax1.xaxis.set_minor_locator(md.MonthLocator())
        ax1.set_ylabel(str(plot_run_length_running_mean)+' Month Running Mean')
        ax2.grid(True)
        ax2.set_xlim([plot_run_length_YYYYmm_dt_list[0],
                      plot_run_length_YYYYmm_dt_list[-1]])
        ax2.set_xticks(plot_run_length_YYYYmm_dt_list[::24])
        ax2.xaxis.set_major_formatter(md.DateFormatter('%Y'))
        ax2.xaxis.set_minor_locator(md.MonthLocator())
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Difference')
        ax2.set_title('Difference from '+model_list[0], loc='left')
        if plot_left_logo:
            left_logo_img = fig.figimage(
                left_logo_img_array, left_logo_xpixel_loc,
                left_logo_ypixel_loc, zorder=1, alpha=right_logo_alpha
            )
            left_logo_img.set_visible(True)
        if plot_right_logo:
            right_logo_img = fig.figimage(
                right_logo_img_array, right_logo_xpixel_loc,
                right_logo_ypixel_loc, zorder=1, alpha=right_logo_alpha
            )
        ax2.plot_date(
            plot_run_length_YYYYmm_dt_list,
            np.zeros_like(plot_run_length_YYYYmm_dt_list),
            color=all_model_plot_settings_dict[model_list[0]]['color'],
            linestyle='solid', linewidth=2,
            marker=None, markersize=0,
        )
        for model in model_list:
            model_plot_settings_dict = all_model_plot_settings_dict[model]
            model_forecast_day = np.ma.masked_invalid(
                model_group_merged_df.loc[(model)]\
                ['DAY'+str(plot_forecast_day)].to_numpy(dtype=float)
            )
            model_forecast_day_running_mean = np.ma.masked_invalid(
                model_group_running_mean_df.loc[(model)]\
                ['DAY'+str(plot_forecast_day)].to_numpy(dtype=float)
            )
            if model == model_list[0]:
                model0_forecast_day_running_mean = (
                    model_forecast_day_running_mean
                )
            model_model0_forecast_day_running_mean_diff = (
                model_forecast_day_running_mean
                - model0_forecast_day_running_mean
            )
            if len(model_forecast_day_running_mean) != \
                    np.ma.count_masked(model_forecast_day_running_mean):
                if np.ma.count_masked(model_forecast_day[-1]) == 1:
                    model_label = f"{model} --"
                else:
                    model_label = f"{model} {model_forecast_day[-1]:.3f}"
                ax1.plot_date(
                    plot_run_length_YYYYmm_dt_list,
                    model_forecast_day_running_mean,
                    color=model_plot_settings_dict['color'],
                    linestyle='solid', linewidth=2,
                    marker=None, markersize=0,
                    zorder=((len(model_list)-model_list.index(model))+4),
                    label=model_label
                )
                if model_forecast_day_running_mean.min() \
                        < stat_min_max_dict['ax1_stat_min'] \
                        or np.ma.is_masked(stat_min_max_dict['ax1_stat_min']):
                    stat_min_max_dict['ax1_stat_min'] = (
                        model_forecast_day_running_mean.min()
                    )
                if model_forecast_day_running_mean.max() > \
                        stat_min_max_dict['ax1_stat_max'] \
                        or np.ma.is_masked(stat_min_max_dict['ax1_stat_max']):
                    stat_min_max_dict['ax1_stat_max'] = (
                        model_forecast_day_running_mean.max()
                    )
            if len(model_model0_forecast_day_running_mean_diff) != \
                    np.ma.count_masked(model_model0_forecast_day_running_mean_diff):
                ax2.plot_date(
                    plot_run_length_YYYYmm_dt_list,
                    model_model0_forecast_day_running_mean_diff,
                    color=model_plot_settings_dict['color'],
                    linestyle='solid', linewidth=2,
                    marker=None, markersize=0,
                    zorder=((len(model_list)-model_list.index(model))+4)
                )
                if model_model0_forecast_day_running_mean_diff.min() \
                        < stat_min_max_dict['ax2_stat_min'] \
                        or np.ma.is_masked(stat_min_max_dict['ax2_stat_min']):
                    stat_min_max_dict['ax2_stat_min'] = (
                        model_model0_forecast_day_running_mean_diff.min()
                    )
                if model_model0_forecast_day_running_mean_diff.max() > \
                        stat_min_max_dict['ax2_stat_max'] \
                        or np.ma.is_masked(stat_min_max_dict['ax2_stat_max']):
                    stat_min_max_dict['ax2_stat_max'] = (
                        model_model0_forecast_day_running_mean_diff.max()
                    )
        subplot_num = 1
        for ax in fig.get_axes():
            stat_min = stat_min_max_dict['ax'+str(subplot_num)+'_stat_min']
            stat_max = stat_min_max_dict['ax'+str(subplot_num)+'_stat_max']
            preset_y_axis_tick_min = ax.get_yticks()[0]
            preset_y_axis_tick_max = ax.get_yticks()[-1]
            preset_y_axis_tick_inc = ax.get_yticks()[1]-ax.get_yticks()[0]
            if plot_stat in ['ACC'] and subplot_num == 1:
                y_axis_tick_inc = 0.1
            else:
                y_axis_tick_inc = preset_y_axis_tick_inc
            if np.ma.is_masked(stat_min):
                y_axis_min = preset_y_axis_tick_min
            else:
                if plot_stat in ['ACC'] and subplot_num == 1:
                    y_axis_min = round(stat_min,1) - y_axis_tick_inc
                else:
                    y_axis_min = preset_y_axis_tick_min
                    while y_axis_min > stat_min:
                        y_axis_min = y_axis_min - y_axis_tick_inc
            if np.ma.is_masked(stat_max):
                y_axis_max = preset_y_axis_tick_max
            else:
                if plot_stat in ['ACC'] and subplot_num == 1:
                    y_axis_max = 1
                else:
                    y_axis_max = preset_y_axis_tick_max + y_axis_tick_inc
                    while y_axis_max < stat_max:
                        y_axis_max = y_axis_max + y_axis_tick_inc
            ax.set_yticks(np.arange(y_axis_min,
                                    y_axis_max+y_axis_tick_inc,
                                    y_axis_tick_inc))
            ax.set_ylim([y_axis_min, y_axis_max])
            if stat_max >= ax.get_ylim()[1]:
                while stat_max >= ax.get_ylim()[1]:
                    y_axis_max = y_axis_max + y_axis_tick_inc
                    ax.set_yticks(np.arange(y_axis_min,
                                            y_axis_max +  y_axis_tick_inc,
                                            y_axis_tick_inc))
                    ax.set_ylim([y_axis_min, y_axis_max])
            if stat_min <= ax.get_ylim()[0]:
                while stat_min <= ax.get_ylim()[0]:
                    y_axis_min = y_axis_min - y_axis_tick_inc
                    ax.set_yticks(np.arange(y_axis_min,
                                            y_axis_max +  y_axis_tick_inc,
                                            y_axis_tick_inc))
                    ax.set_ylim([y_axis_min, y_axis_max])
            subplot_num+=1
        ax.text(
            0.5, 0.09,
            plot_run_length_YYYYmm_dt_list[-1].strftime('%b %Y')+' Mean',
            fontsize=16, ha='center', va='center', transform=ax1.transAxes
        )
        if len(ax1.lines) != 0:
            y_axis_min = ax1.get_yticks()[0]
            y_axis_max = ax1.get_yticks()[-1]
            y_axis_tick_inc = ax1.get_yticks()[1] - ax1.get_yticks()[0]
            stat_min = stat_min_max_dict['ax1_stat_min']
            stat_max = stat_min_max_dict['ax1_stat_max']
            legend = ax1.legend(
                bbox_to_anchor=(plot_specs_lttsd.legend_bbox[0],
                                plot_specs_lttsd.legend_bbox[1]),
                loc=plot_specs_lttsd.legend_loc,
                ncol=plot_specs_lttsd.legend_ncol,
                fontsize=plot_specs_lttsd.legend_font_size
            )
            plt.draw()
            inv = ax1.transData.inverted()
            legend_box = legend.get_window_extent()
            legend_box_inv = inv.transform(
                [(legend_box.x0,legend_box.y0),
                 (legend_box.x1,legend_box.y1)]
            )
            legend_box_inv_y1 = legend_box_inv[1][1]
            if stat_min < legend_box_inv_y1:
                while stat_min < legend_box_inv_y1:
                    y_axis_min = y_axis_min - y_axis_tick_inc
                    ax1.set_yticks(
                        np.arange(y_axis_min,
                                  y_axis_max + y_axis_tick_inc,
                                  y_axis_tick_inc)
                    )
                    ax1.set_ylim([y_axis_min, y_axis_max])
                    legend = ax1.legend(
                        bbox_to_anchor=(plot_specs_la.legend_bbox[0],
                                        plot_specs_la.legend_bbox[1]),
                        loc = plot_specs_la.legend_loc,
                        ncol = plot_specs_la.legend_ncol,
                        fontsize = plot_specs_la.legend_font_size
                    )
                    plt.draw()
                    inv = ax1.transData.inverted()
                    legend_box = legend.get_window_extent()
                    legend_box_inv = inv.transform(
                         [(legend_box.x0,legend_box.y0),
                          (legend_box.x1,legend_box.y1)]
                    )
                    legend_box_inv_y1 = legend_box_inv[1][1]
        logger.info("Saving image as "+image_name)
        plt.savefig(image_name)
        plt.clf()
        plt.close('all')
    # Make lead-year plots
    # Make annual mean plots 

### Do monthly grid-to-grid plots
# Set up monthly output directory
monthly_dir = os.path.join(DATA, 'monthly')
if not os.path.exists(monthly_dir):
    os.makedirs(monthly_dir)
print(f"Doing monthly grid-to-grid plots")
monthly_g2g_dir = os.path.join(monthly_dir, 'grid2grid')
monthly_logs_g2g_dir = os.path.join(monthly_dir, 'grid2grid', 'logs')
monthly_images_g2g_dir = os.path.join(monthly_dir, 'grid2grid', 'images')
if not os.path.exists(monthly_g2g_dir):
    os.makedirs(monthly_g2g_dir)
    os.makedirs(monthly_logs_g2g_dir)
    os.makedirs(monthly_images_g2g_dir)
print(f"Working in {monthly_g2g_dir}")
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
# Make plots for groupings
for model_group in list(model_group_dict.keys()):
    model_list = model_group_dict[model_group]
    print(f"Working on model group {model_group}: "
          +f"{' '.join(model_list)}")
    #model_group_dir = os.path.join(monthly_g2g_dir, model_group)
    now = datetime.datetime.now()
    logging_file = os.path.join(
        monthly_logs_g2g_dir,
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
        all_YYYYmm_dt_list = list(
            dateutil.rrule.rrule(
                dateutil.rrule.MONTHLY,
                dtstart=dateutil.parser.parse(start_YYYYmm+'01T000000'),
                until=dateutil.parser.parse(VDATEYYYY+VDATEmm+'01T000000')
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
            logger.info(f"Working on {var_name} {var_level} {vx_mask} {stat}")
            merged_df = create_merged_dataset(
                logger, (model_group, model_list), var_name, var_level, vx_mask,
                stat, all_YYYYmm_dt_list
            )
            for run_length in ['allyears', 'past10years']:
                create_plots(logger, model_group, merged_df, var_name,
                             var_level, vx_mask, stat, run_length,
                             os.path.join(FIXevs, 'logos'),
                             monthly_images_g2g_dir)

print("END: "+os.path.basename(__file__))
