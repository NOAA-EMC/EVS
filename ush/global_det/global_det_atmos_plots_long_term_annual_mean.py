#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_long_term_annual_mean.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script generates the plots for long term
          annual means.
          (x-axis: forecast day; y-axis: statistics value)
          (EVS Graphics Naming Convention: annualmean)
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

class LongTermAnnualMean:
    """
    Make long term annual means
    """

    def __init__(self, logger, input_dir, output_dir, logo_dir,
                 time_range, date_dt_list, model_group, model_list,
                 var_name, var_level, var_thresh, vx_grid, vx_mask, stat,
                 nbrhd, forecast_day_list, run_length_list):
        """! Initalize LongTermAnnualMean class
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

    def make_long_term_annual_mean(self):
        """! Make the long term annual mean graphic
             Args:
             Returns:
        """
        self.logger.info(f"Plot Type: Long-Term Annual Mean")
        self.logger.debug(f"Input directory: {self.input_dir}")
        self.logger.debug(f"Output directory: {self.output_dir}")
        self.logger.debug(f"Logo directory: {self.logo_dir}")
        self.logger.debug(f"Time Range: {self.time_range}")
        if self.time_range == 'monthly':
            self.logger.error("Can only make annual mean plot for "
                              +"time range of annual")
            sys.exit(1)
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
            # Make annual mean
            self.logger.info(f"Making annual mean plot for {run_length}: "
                             +f"{run_length_date_list[0]}-"
                             +f"{run_length_date_list[-1]}")
            plot_specs_ltam = PlotSpecs(self.logger,
                                         'long_term_annual_mean')
            plot_specs_ltam.set_up_plot()
            if self.stat == 'FSS':
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
                +f"{run_length}_{self.time_range}.annualmean_".lower()
                +f"{model_hour.replace(' ', '').replace(',','')}".lower()
                +f".{self.vx_grid}_{self.vx_mask}.png".lower()
            )
            nsubplots = len(self.model_list)
            if nsubplots == 1:
                gs_row, gs_col = 1, 1
                gs_hspace, gs_wspace = 0, 0
                gs_bottom, gs_top = 0.05, 0.85
                x_legend, y_legend, legend_factor = 0.925, 0.8275, 0.025
                legend_fontsize = 12
            elif nsubplots == 2:
                gs_row, gs_col = 1, 2
                gs_hspace, gs_wspace = 0, 0.1
                gs_bottom, gs_top = 0.05, 0.85
                x_legend, y_legend, legend_factor = 0.925, 0.8275, 0.025
                legend_fontsize = 12
            elif nsubplots > 2 and nsubplots <= 4:
                gs_row, gs_col = 2, 2
                gs_hspace, gs_wspace = 0.15, 0.1
                gs_bottom, gs_top = 0.05, 0.9
                x_legend, y_legend, legend_factor = 0.95, 0.9, 0.02
                legend_fontsize = 18
            elif nsubplots > 4 and nsubplots <= 6:
                gs_row, gs_col = 3, 2
                gs_hspace, gs_wspace = 0.15, 0.1
                gs_bottom, gs_top = 0.05, 0.9
                x_legend, y_legend, legend_factor = 0.95, 0.9, 0.02
                legend_fontsize = 18
            elif nsubplots > 6 and nsubplots <= 8:
                gs_row, gs_col = 4, 2
                gs_hspace, gs_wspace = 0.175, 0.1
                gs_bottom, gs_top = 0.05, 0.9
                x_legend, y_legend, legend_factor = 0.95, 0.9, 0.02
                legend_fontsize = 18
            elif nsubplots > 8 and nsubplots <= 10:
                gs_row, gs_col = 5, 2
                gs_hspace, gs_wspace = 0.225, 0.1
                gs_bottom, gs_top = 0.05, 0.9
                x_legend, y_legend, legend_factor = 0.95, 0.9, 0.02
                legend_fontsize = 18
            else:
                self.logger.error("Too many subplots requested, maximum is 10")
                sys.exit(1)
            if nsubplots <= 2:
                plot_specs_ltam.fig_size = (16., 8.)
                plot_specs_ltam.fig_title_size = 16
                plt.rcParams['figure.titlesize'] = (
                    plot_specs_ltam.fig_title_size
                )
            cmap_colors = plt.cm.get_cmap('viridis_r')
            fig = plt.figure(figsize=(plot_specs_ltam.fig_size[0],
                                      plot_specs_ltam.fig_size[1]))
            gs = gridspec.GridSpec(gs_row, gs_col,
                                   bottom=gs_bottom, top=gs_top,
                                   hspace=gs_hspace, wspace=gs_wspace)
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
                plot_specs_ltam.get_stat_plot_name(self.stat)+' - '
                +f"{self.vx_grid}/"
                +plot_specs_ltam.get_vx_mask_plot_name(self.vx_mask)+'\n'
                +plot_specs_ltam.get_var_plot_name(self.var_name,
                                                   self.var_level)+" "
                +f"({var_units}){var_thresh_for_title}{nbrhd_for_title}\n"
                +f"valid {run_length_date_dt_list[0]:%Y}-"
                +f"{run_length_date_dt_list[-1]:%Y}, {model_hour}"
            )
            left_logo_xpixel_loc, left_logo_ypixel_loc, left_logo_alpha = (
                plot_specs_ltam.get_logo_location(
                    'left', plot_specs_ltam.fig_size[0],
                    plot_specs_ltam.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
            right_logo_xpixel_loc, right_logo_ypixel_loc, right_logo_alpha = (
                plot_specs_ltam.get_logo_location(
                    'right', plot_specs_ltam.fig_size[0],
                     plot_specs_ltam.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
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
                right_logo_img.set_visible(True)
            year_colors_dict = {}
            cmap_color_inc = int(cmap_colors.N/len(run_length_date_list)-1)
            for year in run_length_date_list:
                if year == run_length_date_list[-1]:
                    year_colors_dict[year] = '#000000'
                else:
                    year_colors_dict[year] = matplotlib.colors.rgb2hex(
                        cmap_colors((int(year)-int(run_length_date_list[0]))
                                    *cmap_color_inc)
                    )
                plt.text(x_legend,
                         (y_legend-((int(year)-int(run_length_date_list[0]))
                          *legend_factor)),
                         year, fontsize=legend_fontsize, ha='center', va='top',
                         color=year_colors_dict[year],
                         transform=fig.transFigure)
            model_group_merged = np.ma.masked_invalid(
                model_group_merged_df[
                    ['DAY'+str(x) for x in self.forecast_day_list]
                ].to_numpy(dtype=float)
            )
            stat_min = model_group_merged.min()
            stat_max = model_group_merged.max()
            for model in self.model_list:
                self.logger.debug(f"Plotting {model}")
                ax = plt.subplot(gs[self.model_list.index(model)])
                ax.set_title(model, loc='left')
                ax.grid(True)
                for year in run_length_date_list:
                    model_year_mean_values = np.ma.masked_invalid(
                        np.ones_like(self.forecast_day_list, dtype=float)
                        *np.nan
                    )
                    for fd_idx in range(len(self.forecast_day_list)):
                        model_year_mean_values[fd_idx] = (
                            model_group_merged_df.loc[(model, year)]\
                            ['DAY'+str(self.forecast_day_list[fd_idx])]
                        )
                    ax.plot(self.forecast_day_list,
                            model_year_mean_values,
                            color=year_colors_dict[year],
                            linestyle='solid', linewidth=2,
                            marker=None, markersize=0)
                ax.set_xticks(self.forecast_day_list)
                ax.set_xticklabels(self.forecast_day_list)
                ax.set_xlim([self.forecast_day_list[0],
                             self.forecast_day_list[-1]])
                if ax.get_subplotspec().is_last_row() or (nsubplots % 2 != 0 \
                        and self.model_list.index(model) == nsubplots-2):
                    ax.set_xlabel('Forecast Day')
                else:
                    plt.setp(ax.get_xticklabels(), visible=False)
                if ax.get_subplotspec().is_first_col():
                    ax.set_ylabel('Mean')
                else:
                    plt.setp(ax.get_yticklabels(), visible=False)
                if self.model_list.index(model) == 0:
                    preset_y_axis_tick_min = ax.get_yticks()[0]
                    preset_y_axis_tick_max = ax.get_yticks()[-1]
                    preset_y_axis_tick_inc = (ax.get_yticks()[1]
                                              -ax.get_yticks()[0])
                    if self.stat == 'ACC':
                        y_axis_tick_inc = 0.1
                    else:
                        y_axis_tick_inc = preset_y_axis_tick_inc
                    if np.ma.is_masked(stat_min):
                        y_axis_min = preset_y_axis_tick_min
                    else:
                        if self.stat == 'ACC':
                            y_axis_min = (round(stat_min,1) - y_axis_tick_inc)
                        else:
                            y_axis_min = preset_y_axis_tick_min
                        while y_axis_min > stat_min:
                            y_axis_min = y_axis_min - y_axis_tick_inc
                    if np.ma.is_masked(stat_max):
                        y_axis_max = preset_y_axis_tick_max
                    else:
                        if self.stat == 'ACC':
                            y_axis_max = 1
                        else:
                            y_axis_max = preset_y_axis_tick_max + y_axis_tick_inc
                        while y_axis_max < stat_max:
                            y_axis_max = y_axis_max + y_axis_tick_inc
                    y_ticks = np.arange(y_axis_min,
                                        y_axis_max+y_axis_tick_inc,
                                        y_axis_tick_inc)
                ax.set_yticks(y_ticks)
                ax.set_ylim([y_axis_min, y_axis_max])
            for year in run_length_date_list:
                plt.text(x_legend,
                         (y_legend-((int(year)-int(run_length_date_list[0]))
                          *legend_factor)),
                         year, fontsize=legend_fontsize, ha='center', va='top',
                         color=year_colors_dict[year],
                         transform=fig.transFigure)
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
    NBRHD = 'NBHRD'
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
    p = LongTermAnnualMean(logger, INPUT_DIR, OUTPUT_DIR, LOGO_DIR,
                           TIME_RANGE, DATE_DT_LIST, MODEL_GROUP,
                           MODEL_LIST, VAR_NAME, VAR_LEVEL, VAR_THRESH,
                           VX_GRID, VX_MASK, STAT, FORECAST_DAY_LIST,
                           RUN_LENGTH_LIST)
    p.make_long_term_annual_mean()

if __name__ == "__main__":
    main()
