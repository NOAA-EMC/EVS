#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_long_term_useful_forecast_days.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script generates the plots for long term
          useful forecast days.
          (x-axis: year; y-axis: useful forecast day)
          (EVS Graphics Naming Convention: useful_fcst_days_timeseries)
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
import itertools
from global_det_atmos_plots_specs import PlotSpecs

class LongTermUsefulForecastDays:
    """
    Make long term time useful forecast days plots
    """

    def __init__(self, logger, input_dir, output_dir, logo_dir,
                 time_range, date_dt_list, model_group, model_list,
                 var_name, var_level, var_thresh, vx_grid, vx_mask, stat,
                 nbrhd, run_length_list):
        """! Initalize LongTermUsefulForecastDays class
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
        self.run_length_list = run_length_list

    def make_long_term_useful_forecast_days_time_series(self):
        """! Make the long term useful forecast days
             time series graphics

             Args:
             Returns:
        """
        self.logger.info(f"Plot Type: Long-term Useful Forecast Day "
                         +f"Time Series")
        self.logger.debug(f"Input directory: {self.input_dir}")
        self.logger.debug(f"Output directory: {self.output_dir}")
        self.logger.debug(f"Logo directory: {self.logo_dir}")
        self.logger.debug(f"Time Range: {self.time_range}")
        if self.time_range not in ['monthly', 'yearly']:
            self.logger.error("Can only run useful forecast days for "
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
        model_group_merged_df_fcst_day_list = []
        for col in model_group_merged_df.columns:
            if 'DAY' in col:
                model_group_merged_df_fcst_day_list.append(
                    col.replace('DAY', '')
                )
        # Make plots
        date_list = (model_group_merged_df.index.get_level_values(1)\
                     .unique().tolist())
        if self.var_name == 'HGT':
            var_units = 'gpm'
        elif self.var_name == 'UGRD_VGRD':
            var_units = 'm/s'
        elif self.var_name == 'APCP':
            var_units = self.var_thresh[-2:]
        if self.model_group == 'gfs_4cycles':
            model_hour = 'init 00Z, 06Z, 12Z, 18Z'
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
        if self.stat == 'ACC':
            ufd_stat_threshold_colors_dict = {'0.6': '#000000',
                                              '0.65': '#FB2020',
                                              '0.7': '#00DC00',
                                              '0.75': '#1E3CFF',
                                              '0.8': '#E69F00',
                                              '0.85': '#00C8C8',
                                              '0.9': '#A0E632',
                                              '0.95': '#A000C8'}
        else:
            self.logger.error(f"Thresholds to use for {self.stat} not known")
            sys.exit(1)
        model_group_useful_fday_df = pd.DataFrame(
            index=model_group_merged_df.index,
            columns=[f"{str(x)}" for x in \
                     list(ufd_stat_threshold_colors_dict.keys())]
        )
        ufd_thresh_list = model_group_useful_fday_df.columns
        for model in self.model_list:
            for date in date_list:
                model_date = np.ma.masked_invalid(
                    model_group_merged_df.loc[(model, date)]\
                    [[f"DAY{x}" for x in model_group_merged_df_fcst_day_list]]
                    .to_numpy(dtype=float)
                )
                if not model_date.mask.all():
                    for ufd_thresh \
                            in list(ufd_stat_threshold_colors_dict.keys()):
                        model_group_useful_fday_df.loc[(model, date)]\
                            [ufd_thresh] = np.interp(
                            float(ufd_thresh),
                            model_date.compressed()[::-1],
                            np.ma.masked_where(
                                np.ma.getmask(model_date),
                                np.array(model_group_merged_df_fcst_day_list,
                                         dtype=float)
                            ).compressed()[::-1],
                            left=np.nan, right=np.nan
                        )
        for run_length in self.run_length_list:
            if run_length == 'allyears':
                run_length_running_mean = 13
                run_length_date_list = date_list
                run_length_date_dt_list = self.date_dt_list
                run_length_model_group_useful_fday_df = (
                    model_group_useful_fday_df
                )
            elif run_length == 'past10years':
                run_length_running_mean = 6
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
                run_length_model_group_useful_fday_df = (
                    model_group_useful_fday_df.loc[
                        (self.model_list, run_length_date_list),:
                    ]
                )
            else:
                self.logger.warning(f"{run_length} not recongized, skipping,"
                                    +"use allyears or past10year")
                continue
            run_length_model_group_useful_fday_running_mean_df = pd.DataFrame(
                index=run_length_model_group_useful_fday_df.index,
                columns=run_length_model_group_useful_fday_df.columns
            )
            for model in self.model_list:
                for ufd_thresh \
                        in run_length_model_group_useful_fday_df.columns:
                    model_ufd_thresh = np.ma.masked_invalid(
                        run_length_model_group_useful_fday_df\
                        .loc[(model)][ufd_thresh].to_numpy(dtype=float)
                    )
                    for m in range(len(model_ufd_thresh)):
                        start = m-int(run_length_running_mean/2)
                        end = m+int(run_length_running_mean/2)
                        if start >= 0 and end < len(model_ufd_thresh):
                            if len(model_ufd_thresh[start:end+1].compressed()) \
                                    >= round(0.75
                                             *len(model_ufd_thresh\
                                                  [start:end+1])):
                                run_length_model_group_useful_fday_running_mean_df\
                                .loc[(model,run_length_date_list[m])]\
                                [ufd_thresh] = (
                                    model_ufd_thresh[start:end+1].mean()
                                )
            # Make time series for each model
            plot_specs_ts = PlotSpecs(self.logger, 'time_series')
            plot_specs_ts.set_up_plot()
            plt.rcParams['figure.subplot.top'] = 0.85
            left_logo_xpixel_loc, left_logo_ypixel_loc, left_logo_alpha = (
                plot_specs_ts.get_logo_location(
                    'left', plot_specs_ts.fig_size[0],
                    plot_specs_ts.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
            right_logo_xpixel_loc, right_logo_ypixel_loc, right_logo_alpha = (
                plot_specs_ts.get_logo_location(
                    'right', plot_specs_ts.fig_size[0],
                     plot_specs_ts.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
            for model in self.model_list:
                self.logger.debug("Making time series plot for "
                                  +f"{run_length}: "
                                  +f"{run_length_date_list[0]}-"
                                  +f"{run_length_date_list[-1]} for "
                                  +f"{model} useful forecast days, where "
                                  +f"{self.stat} is "
                                  +f"{', '.join(ufd_thresh_list)}")
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
                    f"evs.global_det.{model}.{image_name_stat_thresh}.".lower()
                    +f"{self.var_name}_{self.var_level}.".lower()
                    +f"{run_length}_{self.time_range}.".lower()
                    +f"useful_fcst_days_timeseries_".lower()
                    +f"{model_hour.replace(' ', '').replace(',','')}.".lower()
                    +f"{self.vx_grid}_{self.vx_mask}.png".lower()
                )
                fig, ax = plt.subplots(1,1,figsize=(plot_specs_ts.fig_size[0],
                                                    plot_specs_ts.fig_size[1]))
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
                    f"{model.upper()} Forecast Days Exceeding Given "
                    +plot_specs_ts.get_stat_plot_name(self.stat)+' Values\n'
                    +plot_specs_ts.get_var_plot_name(self.var_name,
                                                     self.var_level)+" "
                    +f"({var_units}){var_thresh_for_title}{nbrhd_for_title}, "
                    +f"{self.vx_grid}/"
                    +plot_specs_ts.get_vx_mask_plot_name(self.vx_mask)+'\n'
                    +f"valid {dates_for_title} {model_hour}\n"
                    +f"Dotted Line: {self.time_range.title()} Mean, "
                    +f"Solid Line: {run_length_running_mean} "
                    +f"{self.time_range.replace('ly','').title()} Running Mean"
                )
                ax.grid(True)
                ax.set_xlabel('Year')
                ax.set_xlim([run_length_date_dt_list[0],
                             run_length_date_dt_list[-1]])
                if self.time_range == 'monthly':
                    ax.set_xticks(run_length_date_dt_list[::24])
                    ax.xaxis.set_minor_locator(md.MonthLocator())
                elif self.time_range == 'yearly':
                    ax.set_xticks(run_length_date_dt_list[::4])
                ax.xaxis.set_major_formatter(md.DateFormatter('%Y'))
                ax.set_ylabel('Forecast Day')
                ax.set_yticks(range(0,11,1))
                ax.set_ylim([0, 10])
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
                for ufd_thresh in ufd_thresh_list:
                    self.logger.info(f"Plotting {ufd_thresh}")
                    ax.plot_date(
                        run_length_date_dt_list,
                        np.ma.masked_invalid(
                            run_length_model_group_useful_fday_df\
                            .loc[(model)][[ufd_thresh]].to_numpy(dtype=float)
                        ),
                        fmt='.', linewidth=1, markersize=0,
                        color=ufd_stat_threshold_colors_dict[ufd_thresh],
                    )
                    ax.plot_date(
                        run_length_date_dt_list,
                        np.ma.masked_invalid(
                            run_length_model_group_useful_fday_running_mean_df\
                            .loc[(model)][[ufd_thresh]].to_numpy(dtype=float)
                        ),
                        fmt='-', linewidth=2, markersize=0,
                        color=ufd_stat_threshold_colors_dict[ufd_thresh],
                        label=f"{self.stat}={ufd_thresh}"
                    )
                if len(ax.lines) != 0:
                    legend = ax.legend(
                        bbox_to_anchor=(plot_specs_ts.legend_bbox[0],
                                        plot_specs_ts.legend_bbox[1]),
                        loc = plot_specs_ts.legend_loc,
                        ncol = len(ufd_thresh_list),
                        fontsize = plot_specs_ts.legend_font_size
                    )
                self.logger.info("Saving image as "+image_name)
                plt.savefig(image_name)
                plt.clf()
                plt.close('all')
            # Make time series for models for two thresholds
            all_model_plot_settings_dict = (
                plot_specs_ts.get_model_plot_settings()
            )
            if self.stat == 'ACC':
                ufd_two_thresh = ['0.6', '0.8']
            self.logger.debug("Making time series plot for "
                              +f"{run_length}: "
                              +f"{run_length_date_list[0]}-"
                              +f"{run_length_date_list[-1]} for "
                              +f"{self.model_group} useful forecast days, where "
                              +f"{self.stat} is "
                              +f"{ufd_two_thresh[0]} and {ufd_two_thresh[1]}")
            if 'FSS' in self.stat:
                nbrhd_width_pts = int(np.sqrt(int(self.nbrhd.split('/')[1])))
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
                +f"{self.var_name}_{self.var_level}.".lower()
                +f"{run_length}_{self.time_range}.".lower()
                +f"useful_fcst_days_timeseries_".lower()
                +f"{model_hour.replace(' ', '').replace(',','')}.".lower()
                +f"{self.vx_grid}_{self.vx_mask}.png".lower()
            )
            fig, ax = plt.subplots(1,1,figsize=(plot_specs_ts.fig_size[0],
                                                plot_specs_ts.fig_size[1]))
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
                    f"Forecast Days Where "
                    +plot_specs_ts.get_stat_plot_name(self.stat)+' Equals '
                    +f"{ufd_two_thresh[0]} and {ufd_two_thresh[1]}\n"
                    +plot_specs_ts.get_var_plot_name(self.var_name,
                                                     self.var_level)+" "
                    +f"({var_units}){var_thresh_for_title}{nbrhd_for_title}, "
                    +f"{self.vx_grid}/"
                    +plot_specs_ts.get_vx_mask_plot_name(self.vx_mask)+'\n'
                    +f"valid {dates_for_title} {model_hour}\n"
                    +f"Dotted Line: {self.time_range.title()} Mean, "
                    +f"Solid Line: {run_length_running_mean} "
                    +f"{self.time_range.replace('ly','').title()} Running Mean"
                )
            ax.grid(True)
            ax.set_xlabel('Year')
            ax.set_xlim([run_length_date_dt_list[0],
                         run_length_date_dt_list[-1]])
            if self.time_range == 'monthly':
                ax.set_xticks(run_length_date_dt_list[::24])
                ax.xaxis.set_minor_locator(md.MonthLocator())
            elif self.time_range == 'yearly':
                ax.set_xticks(run_length_date_dt_list[::4])
            ax.xaxis.set_major_formatter(md.DateFormatter('%Y'))
            ax.set_ylabel('Forecast Day')
            ax.set_yticks(range(0,11,1))
            ax.set_ylim([0, 10])
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
            for model in self.model_list:
                model_plot_settings_dict = (
                    all_model_plot_settings_dict[model]
                )
                for ufd_thresh in ufd_two_thresh:
                    self.logger.debug(f"Plotting {model} {ufd_thresh}")
                    ax.plot_date(
                        run_length_date_dt_list,
                        np.ma.masked_invalid(
                            run_length_model_group_useful_fday_df\
                            .loc[(model)][[ufd_thresh]].to_numpy(dtype=float)
                        ),
                        fmt='.', linewidth=1, markersize=0,
                        color=model_plot_settings_dict['color'],
                    )
                    if ufd_thresh == ufd_two_thresh[0]:
                        model_label = model
                    else:
                        model_label = '_nolegend_'
                    ax.plot_date(
                        run_length_date_dt_list,
                        np.ma.masked_invalid(
                            run_length_model_group_useful_fday_running_mean_df\
                            .loc[(model)][[ufd_thresh]].to_numpy(dtype=float)
                        ),
                        fmt='-', linewidth=2, markersize=0,
                        color=model_plot_settings_dict['color'],
                        label=model_label
                    )
            if self.stat == 'ACC':
                ax.text(1.01, 0.83, f"{self.stat}={ufd_two_thresh[0]}",
                        fontsize=11, transform=ax.transAxes)
                ax.text(1.01, 0.63, f"{self.stat}={ufd_two_thresh[1]}",
                        fontsize=11, transform=ax.transAxes)
            if len(ax.lines) != 0:
                legend = ax.legend(
                    bbox_to_anchor=(plot_specs_ts.legend_bbox[0],
                                    plot_specs_ts.legend_bbox[1]),
                    loc = plot_specs_ts.legend_loc,
                    ncol = len(self.model_list),
                    fontsize = plot_specs_ts.legend_font_size
                )
            self.logger.info("Saving image as "+image_name)
            plt.savefig(image_name)
            plt.clf()
            plt.close('all')

    def make_long_term_useful_forecast_days_histogram(self):
        """! Make the long term useful forecast days histogram
             graphics

             Args:
             Returns:
        """
        self.logger.info(f"Plot Type: Long-Term Useful Forecast Day Histogram")
        self.logger.debug(f"Input directory: {self.input_dir}")
        self.logger.debug(f"Output directory: {self.output_dir}")
        self.logger.debug(f"Logo directory: {self.logo_dir}")
        self.logger.debug(f"Time Range: {self.time_range}")
        if self.time_range not in ['monthly', 'yearly']:
            self.logger.error("Can only run useful forecast days for "
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
        self.logger.debug(f"Verification Mask: {self.vx_mask}")
        self.logger.debug(f"Statistic: {self.stat}")
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
        model_group_merged_df_fcst_day_list = []
        for col in model_group_merged_df.columns:
            if 'DAY' in col:
                model_group_merged_df_fcst_day_list.append(
                    col.replace('DAY', '')
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
        if self.stat == 'ACC':
             ufd_stat_threshold_list = ['0.6']
        else:
            self.logger.error(f"Thresholds to use for {self.stat} not known")
            sys.exit(1)
        model_group_useful_fday_df = pd.DataFrame(
            index=model_group_merged_df.index,
            columns=[f"{str(x)}" for x in ufd_stat_threshold_list]
        )
        for model in self.model_list:
            for date in date_list:
                model_date = np.ma.masked_invalid(
                    model_group_merged_df.loc[(model, date)]\
                    [[f"DAY{x}" for x in model_group_merged_df_fcst_day_list]]
                    .to_numpy(dtype=float)
                )
                if not model_date.mask.all():
                    for ufd_thresh in ufd_stat_threshold_list:
                        model_ufd_thresh_date_value = np.interp(
                            float(ufd_thresh),
                            model_date.compressed()[::-1],
                            np.ma.masked_where(
                                np.ma.getmask(model_date),
                                np.array(model_group_merged_df_fcst_day_list,
                                         dtype=float)
                            ).compressed()[::-1],
                            left=np.nan, right=np.nan
                        )
                        model_group_useful_fday_df.loc[(model, date)]\
                            [ufd_thresh] = model_ufd_thresh_date_value
                        if np.isnan(model_ufd_thresh_date_value) \
                                and model == 'gfs' and self.var_name == 'HGT' \
                                and self.var_level == 'P500' \
                                and self.vx_mask == 'NHEM' \
                                and model_hour == 'valid 00Z' \
                                and self.stat == 'ACC' \
                                and ufd_thresh == '0.6' \
                                and self.time_range == 'yearly':
                            excel_file_name = os.path.join(
                                self.input_dir, model,
                                'usefulfcstdays_ACC06_HGT_P500_NHEM_'
                                +'valid00Z.txt'
                            )
                            excel_df = pd.read_table(
                                excel_file_name, delimiter=' ',
                                skipinitialspace=True,
                                index_col=0
                            )
                            model_group_useful_fday_df.loc[(model, date)]\
                                [ufd_thresh] = (
                                excel_df.loc[int(date)].values[0]
                            )
        for run_length in self.run_length_list:
            if run_length == 'allyears':
                run_length_running_mean = 13
                run_length_date_list = date_list
                run_length_date_dt_list = self.date_dt_list
                run_length_model_group_useful_fday_df = (
                    model_group_useful_fday_df
                )
            elif run_length == 'past10years':
                run_length_running_mean = 6
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
                run_length_model_group_useful_fday_df = (
                    model_group_useful_fday_df.loc[
                        (self.model_list, run_length_date_list),:
                    ]
                )
            else:
                self.logger.warning(f"{run_length} not recongized, skipping,"
                                    +"use allyears or past10year")
                continue
            # Make histogram for each model and threshold
            plot_specs_h = PlotSpecs(self.logger, 'histogram')
            plot_specs_h.set_up_plot()
            left_logo_xpixel_loc, left_logo_ypixel_loc, left_logo_alpha = (
                plot_specs_h.get_logo_location(
                    'left', plot_specs_h.fig_size[0],
                    plot_specs_h.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
            right_logo_xpixel_loc, right_logo_ypixel_loc, right_logo_alpha = (
                plot_specs_h.get_logo_location(
                    'right', plot_specs_h.fig_size[0],
                     plot_specs_h.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
            for model_thresh in list(
                itertools.product(self.model_list,
                                  ufd_stat_threshold_list)
            ):
                model = model_thresh[0]
                thresh = model_thresh[1]
                self.logger.debug("Making histogram plot for "
                                  +f"{run_length}: "
                                  +f"{run_length_date_list[0]}-"
                                  +f"{run_length_date_list[-1]} for "
                                  +f"{model} useful forecast days, where "
                                  +f"{self.stat} is {thresh}")
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
                    f"evs.global_det.{model}.{image_name_stat_thresh}_".lower()
                    +f"{thresh.replace('.', 'p')}.".lower()
                    +f"{self.var_name}_{self.var_level}.".lower()
                    +f"{run_length}_{self.time_range}.".lower()
                    +f"useful_fcst_days_hist_".lower()
                    +f"{model_hour.replace(' ', '').replace(',','')}.".lower()
                    +f"{self.vx_grid}_{self.vx_mask}.png".lower()
                )
                fig, ax = plt.subplots(1,1,figsize=(plot_specs_h.fig_size[0],
                                                    plot_specs_h.fig_size[1]))
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
                    f"Day At Which {model.upper()} Forecast Loses Useful Skill ("
                    +plot_specs_h.get_stat_plot_name(self.stat)+f"={thresh})\n"
                    +plot_specs_h.get_var_plot_name(self.var_name,
                                                    self.var_level)+" "
                    +f"({var_units}){var_thresh_for_title}{nbrhd_for_title}, "
                    +f"{self.vx_grid}/"
                    +plot_specs_h.get_vx_mask_plot_name(self.vx_mask)+'\n'
                    +f"{self.time_range.title()} Mean"
                )
                run_length_dates = np.asarray(run_length_date_list,
                                              dtype=float)
                ax.grid(True)
                ax.set_xlabel('Year')
                ax.set_xlim([run_length_dates[0],
                             run_length_dates[-1]])
                if self.time_range == 'monthly':
                    ax.set_xticks(run_length_dates[::24])
                elif self.time_range == 'yearly':
                    ax.set_xticks(run_length_dates[::2])
                ax.set_ylabel('Forecast Day')
                ax.set_yticks(range(0,11,1))
                ax.set_ylim([0, 10])
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
                ax.bar(run_length_dates,
                       np.ma.masked_invalid(
                            run_length_model_group_useful_fday_df\
                            .loc[(model)][thresh].to_numpy(dtype=float)
                        ))
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
    RUN_LENGTH_LIST = ['allyears']
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
    p = LongTermUsefulForecastDays(logger, INPUT_DIR, OUTPUT_DIR, LOGO_DIR,
                                   TIME_RANGE, DATE_DT_LIST, MODEL_GROUP,
                                   MODEL_LIST, VAR_NAME, VAR_LEVEL, VAR_THRESH,
                                   VX_GRID, VX_MASK, STAT, NBRHD, RUN_LENGTH_LIST)
    p.make_long_term_useful_forecast_days_time_series()

if __name__ == "__main__":
    main()
