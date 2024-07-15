#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_long_term_lead_by_date.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script generates the plots for long term
          lead by date.
          (x-axis: forecast day; y-axis: months and years; contours: statistics values)
          (EVS Graphics Naming Convention: leaddate)
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

class LongTermLeadByDate:
    """
    Make long term lead by date
    """

    def __init__(self, logger, input_dir, output_dir, logo_dir,
                 time_range, date_dt_list, model_group, model_list,
                 var_name, var_level, var_thresh, vx_grid, vx_mask, stat,
                 nbrhd, forecast_day_list, run_length_list):
        """! Initalize LongTermLeadByDate class
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

    def make_long_term_lead_by_date(self):
        """! Make the long term lead by date graphic
             Args:
             Returns:
        """
        self.logger.info(f"Plot Type: Long-Term Lead By Date")
        self.logger.debug(f"Input directory: {self.input_dir}")
        self.logger.debug(f"Output directory: {self.output_dir}")
        self.logger.debug(f"Logo directory: {self.logo_dir}")
        self.logger.debug(f"Time Range: {self.time_range}")
        if self.time_range not in ['monthly', 'yearly']:
            self.logger.error("Can only run lead by date for "
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
        self.logger.debug(f"Neighborhood: {self.nbrhd}")
        self.logger.debug(f"Statistic: {self.stat}")
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
            forecast_day_float_list = [
                float(i) for i in self.forecast_day_list
            ]
            ymesh, xmesh = np.meshgrid(run_length_date_dt_list,
                                       forecast_day_float_list)
            # Make lead by date
            self.logger.info(f"Making lead by date plot for {run_length}: "
                             +f"{run_length_date_list[0]}-"
                             +f"{run_length_date_list[-1]}")
            plot_specs_ltlbd = PlotSpecs(self.logger,
                                         'long_term_lead_by_date')
            plot_specs_ltlbd.set_up_plot()
            subplot0_cmap, subplotsN_cmap = (
                plot_specs_ltlbd.get_plot_colormaps(self.stat)
            )
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
                +f"{run_length}_{self.time_range}.leaddate_".lower()
                +f"{model_hour.replace(' ', '').replace(',','')}".lower()
                +f".{self.vx_grid}_{self.vx_mask}.png".lower()
            )
            nsubplots = len(self.model_list)
            if nsubplots == 1:
                gs_row, gs_col = 1, 1
                gs_hspace, gs_wspace = 0, 0
                gs_bottom, gs_top = 0.225, 0.82
                cbar_bottom = 0.075
                cbar_height = 0.02
            elif nsubplots == 2:
                gs_row, gs_col = 1, 2
                gs_hspace, gs_wspace = 0, 0.1
                gs_bottom, gs_top = 0.225, 0.82
                cbar_bottom = 0.075
                cbar_height = 0.02
            elif nsubplots > 2 and nsubplots <= 4:
                gs_row, gs_col = 2, 2
                gs_hspace, gs_wspace = 0.15, 0.1
                gs_bottom, gs_top = 0.125, 0.89
                cbar_bottom = 0.04
                cbar_height = 0.02
            elif nsubplots > 4 and nsubplots <= 6:
                gs_row, gs_col = 3, 2
                gs_hspace, gs_wspace = 0.15, 0.1
                gs_bottom, gs_top = 0.125, 0.89
                cbar_bottom = 0.04
                cbar_height = 0.02
            elif nsubplots > 6 and nsubplots <= 8:
                gs_row, gs_col = 4, 2
                gs_hspace, gs_wspace = 0.175, 0.1
                gs_bottom, gs_top = 0.125, 0.89
                cbar_bottom = 0.04
                cbar_height = 0.02
            elif nsubplots > 8 and nsubplots <= 10:
                gs_row, gs_col = 5, 2
                gs_hspace, gs_wspace = 0.225, 0.1
                gs_bottom, gs_top = 0.125, 0.89
                cbar_bottom = 0.04
                cbar_height = 0.02
            else:
                self.logger.error("Too many subplots requested, maximum is 10")
                sys.exit(1)
            if nsubplots <= 2:
                plot_specs_ltlbd.fig_size = (16., 8.)
                plot_specs_ltlbd.fig_title_size = 16
                plt.rcParams['figure.titlesize'] = (
                    plot_specs_ltlbd.fig_title_size
                )
            fig = plt.figure(figsize=(plot_specs_ltlbd.fig_size[0],
                                      plot_specs_ltlbd.fig_size[1]))
            gs = gridspec.GridSpec(gs_row, gs_col,
                                   bottom=gs_bottom, top=gs_top,
                                   hspace=gs_hspace, wspace=gs_wspace)
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
                plot_specs_ltlbd.get_stat_plot_name(self.stat)+' - '
                +f"{self.vx_grid}/"
                +plot_specs_ltlbd.get_vx_mask_plot_name(self.vx_mask)+'\n'
                +plot_specs_ltlbd.get_var_plot_name(self.var_name,
                                                   self.var_level)+" "
                +f"({var_units}){var_thresh_for_title}{nbrhd_for_title}\n"
                +f"valid {dates_for_title}, {model_hour}\n"
                +f"{run_length_running_mean} "
                +f"{self.time_range.replace('ly','').title()} Running Mean"
            )
            left_logo_xpixel_loc, left_logo_ypixel_loc, left_logo_alpha = (
                plot_specs_ltlbd.get_logo_location(
                    'left', plot_specs_ltlbd.fig_size[0],
                    plot_specs_ltlbd.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
            right_logo_xpixel_loc, right_logo_ypixel_loc, right_logo_alpha = (
                plot_specs_ltlbd.get_logo_location(
                    'right', plot_specs_ltlbd.fig_size[0],
                     plot_specs_ltlbd.fig_size[1], plt.rcParams['figure.dpi']
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
            shape = [len(self.model_list),
                     len(run_length_date_list),
                     len(self.forecast_day_list)]
            model_group_running_mean = np.ma.masked_invalid(
                run_length_model_group_running_mean_df\
                    .loc[[m for m in self.model_list]]
                    [['DAY'+str(x) for x in self.forecast_day_list]]\
                    .to_numpy(dtype=float).reshape(shape)
            )
            model0_running_mean = np.ma.masked_invalid(
                run_length_model_group_running_mean_df\
                .loc[(self.model_list[0])]\
                [['DAY'+str(x) for x in self.forecast_day_list]]\
                .to_numpy(dtype=float)
            )
            (have_subplot0_levs, subplot0_levs,
             have_subplotsN_levs, subplotsN_levs) = (
                plot_specs_ltlbd.get_plot_contour_levels(
                    self.stat, model0_running_mean,
                    model_group_running_mean[1:,:,:]
                )
            )
            # Get difference levels for bias
            if self.stat in ['BIAS', 'ME', 'FBIAS']:
                cmap_diff_original = plt.cm.bwr
                colors_diff = cmap_diff_original(
                    np.append(np.linspace(0,0.425,10), np.linspace(0.575,1,10))
                )
                subplotsN_cmap = (
                    matplotlib.colors.LinearSegmentedColormap.from_list(
                        'cmap_diff', colors_diff
                    )
                )
                subplotsN_data = model_group_running_mean[1:,:,:]
                subplot0_data = model0_running_mean
                center_value = 0
                spacing = 1.25
                for N in range(len(subplotsN_data[:,0,0])):
                    subplotN_data = (subplotsN_data[N,:,:] - subplot0_data)
                    if not np.ma.masked_invalid(subplotN_data).mask.all():
                        subplotsN_levs = (
                            plot_specs_ltlbd.get_centered_contour_levels(
                                subplotN_data, center_value, spacing
                            )
                        )
                        break
            make_colorbar = False
            for model in self.model_list:
                ax = plt.subplot(gs[self.model_list.index(model)])
                ax.grid(True)
                model_running_mean = np.ma.masked_invalid(
                    run_length_model_group_running_mean_df.loc[(model)]\
                    [['DAY'+str(x) for x in self.forecast_day_list]]\
                    .to_numpy(dtype=float)
                )
                if model == self.model_list[0]:
                    self.logger.debug(f"Plotting {model}")
                    ax.set_title(model)
                    if not model0_running_mean.mask.all():
                        if have_subplot0_levs:
                            CF0 = ax.contourf(xmesh, ymesh,
                                              model0_running_mean.T,
                                              levels=subplot0_levs,
                                              cmap=subplot0_cmap,
                                              extend='both')
                        else:
                            CF0 = ax.contourf(xmesh, ymesh,
                                              model0_running_mean.T,
                                              cmap=subplot0_cmap,
                                              extend='both')
                        C0 = ax.contour(xmesh, ymesh, model0_running_mean.T,
                                        levels=CF0.levels, colors='k',
                                        linewidths=1.0)
                        C0_labels_list = []
                        for lev in C0.levels:
                            if str(lev).split('.')[1] == '0':
                                C0_labels_list.append(str(int(lev)))
                            else:
                                C0_labels_list.append(
                                    str(round(lev,3)).rstrip('0')
                                )
                        C0_fmt = {}
                        for lev, label in zip(C0.levels, C0_labels_list):
                            C0_fmt[lev] = label
                        ax.clabel(C0, C0.levels, fmt=C0_fmt, inline=True,
                                  fontsize=12.5)
                    else:
                        self.logger.debug(f"{model} is fully masked")
                else:
                    self.logger.debug(f"Plotting {model} difference from "
                                      +f"{self.model_list[0]}")
                    ax.set_title(model+'-'+self.model_list[0])
                    subplotN_data = model_running_mean-model0_running_mean
                    if not subplotN_data.mask.all():
                        if have_subplotsN_levs:
                            CFN = ax.contourf(xmesh, ymesh, subplotN_data.T,
                                              levels=subplotsN_levs,
                                              cmap=subplotsN_cmap,
                                              extend='both')
                        else:
                            self.logger.debug("Do not have contour levels "
                                              +"to plot")
                        if not make_colorbar:
                            make_colorbar = True
                            cbar_CF = CFN
                            cbar_ticks = CFN.levels
                            cbar_label = 'Difference'
                    else:
                        self.logger.debug(f"{model} difference from "
                                          +f"{self.model_list[0]} is fully "
                                          +"masked")
                ax.set_xticks(forecast_day_float_list)
                ax.set_xticklabels(self.forecast_day_list)
                ax.set_xlim([forecast_day_float_list[0],
                             forecast_day_float_list[-1]])
                if ax.get_subplotspec().is_last_row() or (nsubplots % 2 != 0 \
                        and self.model_list.index(model) == nsubplots-2):
                    ax.set_xlabel('Forecast Day')
                else:
                    plt.setp(ax.get_xticklabels(), visible=False)
                ax.set_ylim([run_length_date_dt_list[0],
                             run_length_date_dt_list[-1]])
                if self.time_range == 'monthly':
                    ax.set_yticks(run_length_date_dt_list[::24])
                    ax.yaxis.set_minor_locator(md.MonthLocator())
                elif self.time_range == 'yearly':
                    ax.set_yticks(run_length_date_dt_list[::4])
                    ax.yaxis.set_major_formatter(md.DateFormatter('%Y'))
                ax.yaxis.set_major_formatter(md.DateFormatter('%Y'))
                if ax.get_subplotspec().is_first_col():
                    ax.set_ylabel('Year')
                else:
                    plt.setp(ax.get_yticklabels(), visible=False)
            if make_colorbar:
                cbar_left = gs.get_grid_positions(fig)[2][0]
                cbar_width = (gs.get_grid_positions(fig)[3][-1]
                              - gs.get_grid_positions(fig)[2][0])
                cbar_ax = fig.add_axes(
                    [cbar_left, cbar_bottom, cbar_width, cbar_height]
                )
                cbar = fig.colorbar(cbar_CF, cax=cbar_ax,
                                    orientation='horizontal',
                                    ticks=cbar_ticks)
                cbar.ax.set_xlabel(cbar_label, labelpad = 0)
                cbar.ax.xaxis.set_tick_params(pad=0)
                cbar_tick_labels_list = []
                for tick in cbar.get_ticks():
                    if str(tick).split('.')[1] == '0':
                        cbar_tick_labels_list.append(
                            str(int(tick))
                        )
                    else:
                        cbar_tick_labels_list.append(
                            str(round(tick,3)).rstrip('0')
                        )
                cbar.ax.set_xticklabels(cbar_tick_labels_list)
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
    p = LongTermLeadByDate(logger, INPUT_DIR, OUTPUT_DIR, LOGO_DIR,
                           TIME_RANGE, DATE_DT_LIST, MODEL_GROUP,
                           MODEL_LIST, VAR_NAME, VAR_LEVEL, VAR_THRESH,
                           VX_GRID, VX_MASK, STAT, NBRHD,
                           FORECAST_DAY_LIST, RUN_LENGTH_LIST)
    p.make_long_term_lead_by_date()

if __name__ == "__main__":
    main()
