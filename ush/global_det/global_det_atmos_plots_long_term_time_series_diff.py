#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_long_term_time_series_diff.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script generates the plots for long term
          time series with the difference.
          (x-axis: year; y-axis: statistics value)
          (EVS Graphics Naming Convention: timeseriesdiff)
'''

import sys
import os
import logging
import datetime
import dateutil
from dateutil.relativedelta import relativedelta
import pandas as pd
pd.plotting.deregister_matplotlib_converters()
#pd.plotting.register_matplotlib_converters()
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import global_det_atmos_util as gda_util
import global_det_atmos_long_term_util as gdalt_util
import matplotlib.gridspec as gridspec
from global_det_atmos_plots_specs import PlotSpecs

class LongTermTimeSeriesDiff:
    """
    Make long term time series plots with differences
    """

    def __init__(self, logger, input_dir, output_dir, logo_dir,
                 time_range, date_dt_list, model_group, model_list,
                 var_name, var_level, var_thresh, vx_grid, vx_mask, stat,
                 nbrhd, forecast_day_list, run_length_list):
        """! Initalize LongTermTimeSeriesDiff class
             Args:
                 logger             - logger object
                 input_dir          - path to input directory (string)
                 output_dir         - path to output directory (string)
                 logo_dir           - path to logo images (string)
                 time_range         - time range for plots:
                                      monthly or yearly(string)
                 date_dt_list       - list of datetime objects
                 model_group        - name of the model group (string)
                 model_list         - list of models in group (string)
                 var_name           - variable name (string)
                 var_level          - variable level (string)
                 var_thresh         - variable threshold (string)
                 vx_grid            - verification grid (string)
                 vx_mask            - verification mask name (string)
                 stat               - statistic name (string)
                 nbrhd              - neighborhood information (string)
                 forecast_days_list - list of forecast days (strings)
                 run_length_list    - list of length of times to plot
                                      (string)
             Returns:
        """
        self.logger = logger
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logo_dir = logo_dir
        self.time_range = time_range
        self.date_dt_list = date_dt_list
        self.model_group = model_group
        self.model_list = model_list
        self.var_name = var_name
        self.var_level = var_level
        self.var_thresh = var_thresh
        self.vx_grid = vx_grid
        self.vx_mask = vx_mask
        self.stat = stat
        self.nbrhd = nbrhd
        self.forecast_day_list = forecast_day_list
        self.run_length_list = run_length_list

    def make_long_term_time_series_diff(self):
        """! Make the long term time series difference graphic
             Args:
             Returns:
        """
        self.logger.info(f"Plot Type: Long-Term Time Series Difference")
        self.logger.debug(f"Input directory: {self.input_dir}")
        self.logger.debug(f"Output directory: {self.output_dir}")
        self.logger.debug(f"Logo directory: {self.logo_dir}")
        self.logger.debug(f"Time Range: {self.time_range}")
        if self.time_range not in ['monthly', 'yearly']:
            self.logger.error("Can only run time series difference for "
                              +"time range values of monthly or yearly")
            sys.exit(1)
        if self.time_range == 'monthly':
            self.logger.debug(f"Dates: {self.date_dt_list[0]:%Y%m}"
                              +f"-{self.date_dt_list[-1]:%Y%m}")
        elif self.time_range == 'yearly':
            self.logger.debug(f"Dates: {self.date_dt_list[0]:%Y}"
                              +f"-{self.date_dt_list[-1]:%Y}")
        self.logger.debug(f"Model Group: {self.model_group}")
        self.logger.debug(f"Models: {', '.join(self.model_list)}")
        self.logger.debug(f"Variable Name: {self.var_name}")
        self.logger.debug(f"Variable Level: {self.var_level}")
        self.logger.debug(f"Variable Threshold: {self.var_thresh}")
        self.logger.debug(f"Verification Grid: {self.vx_grid}")
        self.logger.debug(f"Verification Mask: {self.vx_mask}")
        self.logger.debug(f"Statistic: {self.stat}")
        self.logger.debug(f"Neighborhood: {self.nbrhd}")
        self.logger.debug("Forecast Days: "
                          +f"{', '.join(self.forecast_day_list)}")
        self.logger.debug(f"Run Lengths: {', '.join(self.run_length_list)}")
        # Make job image directory
        output_image_dir = os.path.join(self.output_dir, 'images')
        gda_util.make_dir(output_image_dir)
        self.logger.info(f"Plots will be in: {output_image_dir}")
        # Make merged dataset of verification systems
        if self.var_name == 'APCP':
            model_group_merged_df = (
                gdalt_util.merge_precip_long_term_stats_datasets(
                    self.logger, self.input_dir, self.time_range,
                    self.date_dt_list, self.model_group, self.model_list,
                    self.var_name, self.var_level, self.var_thresh,
                    self.vx_grid, self.vx_mask, self.stat, self.nbrhd
                )
            )
        else:
            model_group_merged_df = (
                gdalt_util.merge_grid2grid_long_term_stats_datasets(
                    self.logger, self.input_dir, self.time_range,
                    self.date_dt_list, self.model_group, self.model_list,
                    self.var_name, self.var_level, self.var_thresh,
                    self.vx_grid, self.vx_mask, self.stat, self.nbrhd
                )
            )
        # Make plots
        date_list = (model_group_merged_df.index.get_level_values(1)\
                     .unique().tolist())
        if self.var_name == 'HGT':
            var_units = 'gpm'
        elif self.var_name == 'UGRD_VGRD':
            #var_units = 'm/s'
            var_units = 'kt'
        elif self.var_name == 'APCP':
            var_units = self.var_thresh[-2:]
        if self.model_group == 'gfs_4cycles':
            model_hour = 'init 00Z, 06Z, 12Z, 18Z'
        elif self.var_name == 'APCP':
            model_hour = 'valid 12Z'
        else:
            model_hour = 'valid 00Z'
        plot_left_logo_path = os.path.join(self.logo_dir, 'noaa.png')
        if os.path.exists(plot_left_logo_path):
            plot_left_logo = True
            left_logo_img_array = matplotlib.image.imread(plot_left_logo_path)
        else:
            plot_left_logo = False
            self.logger.debug(f"{plot_left_logo_path} does not exist")
        plot_right_logo_path = os.path.join(self.logo_dir, 'nws.png')
        if os.path.exists(plot_right_logo_path):
            plot_right_logo = True
            right_logo_img_array = matplotlib.image.imread(plot_right_logo_path)
        else:
            plot_right_logo = False
            self.logger.debug(f"{plot_right_logo_path} does not exist")
        for run_length in self.run_length_list:
            if run_length == 'allyears':
                run_length_running_mean = 3
                run_length_date_list = date_list
                run_length_date_dt_list = self.date_dt_list
                run_length_model_group_merged_df = model_group_merged_df
            elif run_length == 'past10years':
                run_length_running_mean = 1
                if self.time_range == 'monthly':
                    tenyearsago_dt = (
                        datetime.datetime.strptime(date_list[-1], '%Y%m')
                        - relativedelta(years=10)
                    )
                    run_length_date_list = date_list[
                        date_list.index(f"{tenyearsago_dt:%Y%m}"):
                    ]
                elif self.time_range == 'yearly':
                    tenyearsago_dt = (
                        datetime.datetime.strptime(date_list[-1], '%Y')
                        - relativedelta(years=10)
                    )
                    run_length_date_list = date_list[
                        date_list.index(f"{tenyearsago_dt:%Y}"):
                    ]
                run_length_date_dt_list = self.date_dt_list[
                    self.date_dt_list.index(tenyearsago_dt):
                ]
                run_length_model_group_merged_df = (
                    model_group_merged_df.loc[
                        (self.model_list, run_length_date_list),:
                    ]
                )
            else:
                self.logger.warning(f"{run_length} not recongized, skipping,"
                                    +"use allyears or past10year")
                continue
            run_length_model_group_running_mean_df = pd.DataFrame(
                index=run_length_model_group_merged_df.index,
                columns=[f"DAY{str(x)}" for x in self.forecast_day_list]
            )
            for model in self.model_list:
                for forecast_day in self.forecast_day_list:
                    model_forecast_day = (run_length_model_group_merged_df\
                                          .loc[(model)]\
                                          ['DAY'+str(forecast_day)]\
                                          .to_numpy(dtype=float))
                    for m in range(len(model_forecast_day)):
                        start = m-int(run_length_running_mean/2)
                        end = m+int(run_length_running_mean/2)
                        if start >= 0 and end < len(model_forecast_day):
                            run_length_model_group_running_mean_df.loc[
                                (model,run_length_date_list[m])
                            ]['DAY'+str(forecast_day)] = (
                                model_forecast_day[start:end+1].mean()
                            )
            # Make time series plots for each forecast day with differences
            plot_specs_lttsd = PlotSpecs(self.logger,
                                         'long_term_time_series_diff')
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
            all_model_plot_settings_dict = (
                plot_specs_lttsd.get_model_plot_settings()
            )
            for forecast_day in self.forecast_day_list:
                forecast_hour = str(int(forecast_day)*24)
                self.logger.info("Making time series difference plot for "
                                 +f"{run_length}:"
                                 +f"{run_length_date_list[0]}-"
                                 +f"{run_length_date_list[-1]} "
                                 +f"forecast day {forecast_day} ("
                                 +f"forecast hour {forecast_hour})")
                if 'FSS' in self.stat:
                    nbrhd_width_pts = int(
                        np.sqrt(int(self.nbrhd.split('/')[1]))
                    )
                    image_name_stat_thresh = 'fss_width'+str(nbrhd_width_pts)
                else:
                    image_name_stat_thresh = self.stat
                if self.var_thresh != 'NA':
                    image_name_stat_thresh = (
                        image_name_stat_thresh
                        +f"_{self.var_thresh.replace('.','p')}"
                    )
                image_name = os.path.join(
                    output_image_dir,
                    f"evs.global_det.{self.model_group}.".lower()
                    +f"{image_name_stat_thresh}.".lower()
                    +f"{self.var_name}_{self.var_level}.{run_length}_".lower()
                    +f"{self.time_range}.timeseriesdiff_".lower()
                    +f"{model_hour.replace(' ', '').replace(',','')}_".lower()
                    +f"f{forecast_hour.zfill(3)}.".lower()
                    +f"{self.vx_grid}_{self.vx_mask}.png".lower()
                )
                shape = [len(self.model_list),
                         len(run_length_date_list)]
                model_group_forecast_day_running_mean = np.ma.masked_invalid(
                    run_length_model_group_running_mean_df[
                        ['DAY'+str(forecast_day)]
                    ].to_numpy(dtype=float).reshape(shape)
                )
                model0_forecast_day_running_mean = np.ma.masked_invalid(
                    run_length_model_group_running_mean_df\
                    .loc[(self.model_list[0])]\
                    ['DAY'+str(forecast_day)].to_numpy(dtype=float)
                )
                stat_min_max_dict = {
                    'ax1_stat_min': (
                        model_group_forecast_day_running_mean.min()
                    ),
                    'ax1_stat_max': (
                        model_group_forecast_day_running_mean.max()
                    ),
                    'ax2_stat_min': (
                        (model_group_forecast_day_running_mean
                         -model0_forecast_day_running_mean).min()
                    ),
                    'ax2_stat_max': (
                        (model_group_forecast_day_running_mean
                         -model0_forecast_day_running_mean).max()
                    )
                }
                fig, (ax1, ax2) = plt.subplots(
                    2,1,
                    figsize=(plot_specs_lttsd.fig_size[0],
                             plot_specs_lttsd.fig_size[1]),
                    sharex=True
                )
                if self.time_range == 'monthly':
                    dates_for_title = (
                        f"{run_length_date_dt_list[0]:%b%Y}"
                        +f"-{run_length_date_dt_list[-1]:%b%Y}"
                    )
                elif self.time_range == 'yearly':
                    dates_for_title = (
                        f"{run_length_date_dt_list[0]:%Y}"
                        +f"-{run_length_date_dt_list[-1]:%Y}"
                    )
                if self.var_thresh == 'NA':
                    var_thresh_for_title = ''
                else:
                    var_thresh_for_title = ', '+self.var_thresh
                if self.nbrhd == 'NA':
                    nbrhd_for_title = ''
                else:
                    nbrhd_pts = self.nbrhd.split('/')[1]
                    if self.vx_grid == 'G240':
                        dx = 4.7625
                    nbrhd_width_km = round(np.sqrt(int(nbrhd_pts)) * dx)
                    nbrhd_for_title = (', Neighborhood: '
                                       +nbrhd_pts+' Points, '
                                       +str(nbrhd_width_km)+' km')
                fig.suptitle(
                    plot_specs_lttsd.get_stat_plot_name(self.stat)+' - '
                    +f"{self.vx_grid}/"
                    +plot_specs_lttsd.get_vx_mask_plot_name(self.vx_mask)+'\n'
                    +plot_specs_lttsd.get_var_plot_name(self.var_name,
                                                        self.var_level)+" "
                    +f"({var_units}){var_thresh_for_title}{nbrhd_for_title}\n"
                    +f"valid {dates_for_title} {model_hour}, "
                    +f"Forecast Day {forecast_day} (Hour {forecast_hour})\n"
                    +f"{run_length_running_mean} "
                    +f"{self.time_range.replace('ly','').title()} Running Mean"
                )
                ax1.grid(True)
                ax1.set_xlim([run_length_date_dt_list[0],
                              run_length_date_dt_list[-1]])
                if self.time_range == 'monthly':
                    ax1.set_xticks(run_length_date_dt_list[::24])
                    ax1.xaxis.set_minor_locator(md.MonthLocator())
                    ax2.xaxis.set_minor_locator(md.MonthLocator())
                elif self.time_range == 'yearly':
                    ax1.set_xticks(run_length_date_dt_list[::4])
                ax1.xaxis.set_major_formatter(md.DateFormatter('%Y'))
                ax1.set_ylabel(
                    str(run_length_running_mean)
                    +self.time_range.replace('ly','').title()+' '
                    +'Running Mean'
                )
                ax2.grid(True)
                ax2.set_xlabel('Year')
                ax2.set_ylabel('Difference')
                ax2.set_title('Difference from '+self.model_list[0],
                              loc='left')
                if plot_left_logo:
                    left_logo_img = fig.figimage(
                        left_logo_img_array, left_logo_xpixel_loc,
                        left_logo_ypixel_loc, zorder=1,
                        alpha=right_logo_alpha
                    )
                    left_logo_img.set_visible(True)
                if plot_right_logo:
                    right_logo_img = fig.figimage(
                        right_logo_img_array, right_logo_xpixel_loc,
                        right_logo_ypixel_loc, zorder=1,
                        alpha=right_logo_alpha
                    )
                ax2.plot_date(
                    run_length_date_dt_list,
                    np.zeros_like(run_length_date_dt_list),
                    fmt='-', linewidth=2, markersize=0,
                    color=(all_model_plot_settings_dict\
                           [self.model_list[0]]['color']),
                )
                for model in self.model_list:
                    self.logger.debug(f"Plotting {model}")
                    model_plot_settings_dict = (
                        all_model_plot_settings_dict[model]
                    )
                    model_forecast_day = np.ma.masked_invalid(
                        run_length_model_group_merged_df.loc[(model)]\
                        ['DAY'+str(forecast_day)].to_numpy(dtype=float)
                    )
                    model_forecast_day_running_mean = np.ma.masked_invalid(
                        run_length_model_group_running_mean_df.loc[(model)]\
                        ['DAY'+str(forecast_day)].to_numpy(dtype=float)
                    )
                    if len(model_forecast_day_running_mean) != \
                            np.ma.count_masked(
                                model_forecast_day_running_mean
                            ):
                        legend_mean = np.ma.mean(
                            model_forecast_day_running_mean
                        )
                        if np.ma.is_masked(legend_mean):
                            model_label = f"{model} --"
                        else:
                            model_label = (f"{model} "
                                           +f"{legend_mean:.3f}")
                        ax1.plot_date(
                            run_length_date_dt_list,
                            model_forecast_day_running_mean,
                            fmt='-', linewidth=2, markersize=0,
                            color=model_plot_settings_dict['color'],
                            zorder=((len(self.model_list)
                                    -self.model_list.index(model))+4),
                            label=model_label
                        )
                    else:
                        self.logger.debug(f"{model} is fully masked")
                    self.logger.debug(f"Plotting {model} difference from "
                                      +f"{self.model_list[0]}")
                    model_model0_forecast_day_running_mean_diff = (
                        model_forecast_day_running_mean
                        - model0_forecast_day_running_mean
                    )
                    if len(model_model0_forecast_day_running_mean_diff) != \
                            np.ma.count_masked(
                                model_model0_forecast_day_running_mean_diff
                            ):
                        ax2.plot_date(
                            run_length_date_dt_list,
                            model_model0_forecast_day_running_mean_diff,
                            fmt='-', linewidth=2, markersize=0,
                            color=model_plot_settings_dict['color'],
                            zorder=((len(self.model_list)
                                    -self.model_list.index(model))+4)
                        )
                    else:
                        self.logger.debug(f"{model} difference from "
                                          +f"{self.model_list[0]} is fully "
                                          +"masked")
                subplot_num = 1
                for ax in fig.get_axes():
                    stat_min = (stat_min_max_dict\
                                ['ax'+str(subplot_num)+'_stat_min'])
                    stat_max = (stat_min_max_dict\
                                ['ax'+str(subplot_num)+'_stat_max'])
                    preset_y_axis_tick_min = ax.get_yticks()[0]
                    preset_y_axis_tick_max = ax.get_yticks()[-1]
                    preset_y_axis_tick_inc = (ax.get_yticks()[1]
                                              -ax.get_yticks()[0])
                    if self.stat in ['ACC'] and subplot_num == 1:
                        y_axis_tick_inc = 0.1
                    else:
                        y_axis_tick_inc = preset_y_axis_tick_inc
                    if np.ma.is_masked(stat_min):
                        y_axis_min = preset_y_axis_tick_min
                    else:
                        if self.stat in ['ACC'] and subplot_num == 1:
                             y_axis_min = round(stat_min,1) - y_axis_tick_inc
                        else:
                            y_axis_min = preset_y_axis_tick_min
                            while y_axis_min > stat_min:
                                y_axis_min = y_axis_min - y_axis_tick_inc
                    if np.ma.is_masked(stat_max):
                        y_axis_max = preset_y_axis_tick_max
                    else:
                        if self.stat in ['ACC'] and subplot_num == 1:
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
                                                    y_axis_max
                                                    + y_axis_tick_inc,
                                                    y_axis_tick_inc))
                            ax.set_ylim([y_axis_min, y_axis_max])
                    if stat_min <= ax.get_ylim()[0]:
                        while stat_min <= ax.get_ylim()[0]:
                            y_axis_min = y_axis_min - y_axis_tick_inc
                            ax.set_yticks(np.arange(y_axis_min,
                                                    y_axis_max +
                                                    y_axis_tick_inc,
                                                    y_axis_tick_inc))
                            ax.set_ylim([y_axis_min, y_axis_max])
                    subplot_num+=1
                if self.time_range == 'monthly':
                    mean_date_strf = '%b %Y'
                elif self.time_range == 'yearly':
                    mean_date_strf = '%Y'
                if len(ax1.lines) != 0:
                    y_axis_min = ax1.get_yticks()[0]
                    y_axis_max = ax1.get_yticks()[-1]
                    y_axis_tick_inc = (ax1.get_yticks()[1]
                                       - ax1.get_yticks()[0])
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
                                bbox_to_anchor=(plot_specs_lttsd.legend_bbox[0],
                                                plot_specs_lttsd.legend_bbox[1]),
                                loc = plot_specs_lttsd.legend_loc,
                                ncol = plot_specs_lttsd.legend_ncol,
                                fontsize = plot_specs_lttsd.legend_font_size
                            )
                            plt.draw()
                            inv = ax1.transData.inverted()
                            legend_box = legend.get_window_extent()
                            legend_box_inv = inv.transform(
                                [(legend_box.x0,legend_box.y0),
                                 (legend_box.x1,legend_box.y1)]
                            )
                            legend_box_inv_y1 = legend_box_inv[1][1]
                self.logger.info("Saving image as "+image_name)
                plt.savefig(image_name)
                plt.clf()
                plt.close('all')

def main():
    # Need settings
    INPUT_DIR = os.environ['HOME']
    OUTPUT_DIR = os.environ['HOME']
    LOGO_DIR = os.environ['HOME']
    TIME_RANGE = 'TIME_RANGE'
    DATE_DT_LIST = []
    MODEL_GROUP = 'MODEL_GROUP'
    MODEL_LIST = ['MODELA', 'MODELB']
    VAR_NAME = 'VAR_NAME'
    VAR_LEVEL = 'VAR_LEVEL'
    VAR_THRESH = 'VAR_THRESH'
    VX_GRID = 'VX_GRID'
    VX_MASK = 'VX_MASK'
    STAT = 'STAT'
    NBRHD = 'NBRHD'
    FORECAST_DAY_LIST = ['1', '2']
    RUN_LENGTH_LIST = ['allyears', 'past10years']
    # Make OUTPUT_DIR
    gda_util.make_dir(OUTPUT_DIR)
    # Set up logging
    logging_dir = os.path.join(OUTPUT_DIR, 'logs')
    gda_util.make_dir(logging_dir)
    job_logging_file = os.path.join(logging_dir,
                                    os.path.basename(__file__)+'_runon'
                                    +datetime.datetime.now()\
                                    .strftime('%Y%m%d%H%M%S')+'.log')
    logger = logging.getLogger(job_logging_file)
    logger.setLevel('DEBUG')
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
        + '%(message)s',
        '%m/%d %H:%M:%S'
    )
    file_handler = logging.FileHandler(job_logging_file, mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger_info = f"Log file: {job_logging_file}"
    print(logger_info)
    logger.info(logger_info)
    p = LongTermTimeSeriesDiff(logger, INPUT_DIR, OUTPUT_DIR, LOGO_DIR,
                               TIME_RANGE, DATE_DT_LIST, MODEL_GROUP,
                               MODEL_LIST, VAR_NAME, VAR_LEVEL, VAR_THRESH,
                               VX_GRID, VX_MASK, STAT, NBRHD,
                               FORECAST_DAY_LIST, RUN_LENGTH_LIST)
    p.make_long_term_time_series_diff()

if __name__ == "__main__":
    main()
