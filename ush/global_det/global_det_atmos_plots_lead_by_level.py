#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_lead_by_level.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script generates a lead by level plot.
          (x-axis: forecast hour; y-axis: pressure levels; contours: statistics values)
          (EVS Graphics Naming Convention: vertprof_fhrmean)
'''

import sys
import os
import logging
import datetime
import glob
import pandas as pd
pd.plotting.deregister_matplotlib_converters()
#pd.plotting.register_matplotlib_converters()
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import global_det_atmos_util as gda_util
from global_det_atmos_plots_specs import PlotSpecs

class LeadByLevel:
    """
    Make a lead by level graphic
    """

    def __init__(self, logger, input_dir, output_dir, model_info_dict,
                 date_info_dict, plot_info_dict, met_info_dict, logo_dir):
        """! Initalize LeadByLevel class

             Args:
                 logger          - logger object
                 input_dir       - path to input directory (string)
                 output_dir      - path to output directory (string)
                 model_info_dict - model infomation dictionary (strings)
                 plot_info_dict  - plot information dictionary (strings)
                 date_info_dict  - date information dictionary (strings)
                 met_info_dict   - MET information dictionary (strings)
                 logo_dir        - directory with logo images (string)

             Returns:
        """
        self.logger = logger
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.model_info_dict = model_info_dict
        self.date_info_dict = date_info_dict
        self.plot_info_dict = plot_info_dict
        self.met_info_dict = met_info_dict
        self.logo_dir = logo_dir

    def make_lead_by_level(self):
        """! Make the lead by level graphic

             Args:

             Returns:
        """
        self.logger.info(f"Plot Type: Lead By Level...")
        self.logger.debug(f"Input directory: {self.input_dir}")
        self.logger.debug(f"Output directory: {self.output_dir}")
        self.logger.debug(f"Model information dictionary: "
                          +f"{self.model_info_dict}")
        self.logger.debug(f"Date information dictionary: "
                          +f"{self.date_info_dict}")
        self.logger.debug(f"Plot information dictionary: "
                          +f"{self.plot_info_dict}")
        # Check stat
        if self.plot_info_dict['stat'] == 'FBAR_OBAR':
            self.logger.error("Cannot make lead_by_level for stat "
                              +f"{self.plot_info_dict['stat']}")
            sys.exit(1)
        plot_specs_lbl = PlotSpecs(self.logger, 'lead_by_level')
        self.logger.info(f"Building data for {self.plot_info_dict['stat']} "
                         +"- vertical profile "
                         +f"{self.plot_info_dict['vert_profile']}")
        vert_profile_levels = plot_specs_lbl.get_vert_profile_levels(
            self.plot_info_dict['vert_profile']
        )
        if self.plot_info_dict['fcst_var_name'] == 'O3MR' and \
                self.plot_info_dict['vert_profile'] in ['all', 'strat']:
            vert_profile_levels.append('P1')
            if self.plot_info_dict['vert_profile'] == 'all':
                for lvl in ['P1000', 'P850', 'P700', 'P500', 'P300',
                            'P250', 'P200']:
                    vert_profile_levels.remove(lvl)
        vert_profile_levels_int = np.empty(len(vert_profile_levels),
                                           dtype=int)
        self.plot_info_dict['fcst_var_level'] = (
            self.plot_info_dict['vert_profile']
        )
        self.plot_info_dict['obs_var_level'] = (
            self.plot_info_dict['vert_profile']
        )
        fcst_units = []
        # Make datafram for all levels and all forecast hours
        for level in vert_profile_levels:
            vert_profile_levels_int[vert_profile_levels.index(level)] = (
                level[1:]
            )
            for forecast_hour in self.date_info_dict['forecast_hours']:
                self.logger.info(f"Building data for level {level} "
                                 +f"forecast hour {forecast_hour}")
                # Get dates to plot
                self.logger.debug("Making valid and init date arrays")
                valid_dates, init_dates = gda_util.get_plot_dates(
                    self.logger,
                    self.date_info_dict['date_type'],
                    self.date_info_dict['start_date'],
                    self.date_info_dict['end_date'],
                    self.date_info_dict['valid_hr_start'],
                    self.date_info_dict['valid_hr_end'],
                    self.date_info_dict['valid_hr_inc'],
                    self.date_info_dict['init_hr_start'],
                    self.date_info_dict['init_hr_end'],
                    self.date_info_dict['init_hr_inc'],
                    forecast_hour
                )
                format_valid_dates = [
                    valid_dates[d].strftime('%Y%m%d_%H%M%S') \
                    for d in range(len(valid_dates))
                ]
                format_init_dates = [
                    init_dates[d].strftime('%Y%m%d_%H%M%S') \
                    for d in range(len(init_dates))
                ]
                if self.date_info_dict['date_type'] == 'VALID':
                    self.logger.debug("Based on date information, "
                                      +"plot will display valid dates "
                                      +', '.join(format_valid_dates)+" "
                                      +"for forecast hour "
                                      +f"{forecast_hour} with "
                                      +"initialization dates "
                                      +', '.join(format_init_dates))
                    plot_dates = valid_dates
                elif self.date_info_dict['date_type'] == 'INIT':
                    self.logger.debug("Based on date information, "
                                      +"plot will display "
                                      +"initialization dates "
                                      +', '.join(format_init_dates)+" "
                                      +"for forecast hour "
                                      +f"{forecast_hour} with valid dates "
                                      +', '.join(format_valid_dates))
                    plot_dates = init_dates
                # Read in data
                level_input_dir = os.path.join(
                    self.input_dir, '..', '..',
                    f"{self.plot_info_dict['fcst_var_name'].lower()}_"
                    +f"{level.lower()}",
                    (self.plot_info_dict['vx_mask'].lower()\
                     .replace('global', 'glb').replace('conus', 'buk_conus'))
                )
                self.logger.info("Reading in model stat files from "
                                 +f"{level_input_dir}")
                all_model_df = gda_util.build_df(
                    'make_plots', self.logger, level_input_dir, self.output_dir,
                    self.model_info_dict, self.met_info_dict,
                    self.plot_info_dict['fcst_var_name'],
                    level,
                    self.plot_info_dict['fcst_var_thresh'],
                    self.plot_info_dict['obs_var_name'],
                    level,
                    self.plot_info_dict['obs_var_thresh'],
                    self.plot_info_dict['line_type'],
                    self.plot_info_dict['grid'],
                    self.plot_info_dict['vx_mask'],
                    self.plot_info_dict['interp_method'],
                    self.plot_info_dict['interp_points'],
                    self.date_info_dict['date_type'],
                    plot_dates, format_valid_dates,
                    str(forecast_hour)
                )
                fcst_units.extend(
                    all_model_df['FCST_UNITS'].values.astype('str')\
                    .tolist()
                )
                # Calculate statistic mean
                self.logger.info("Calculating statstic "
                                 +f"{self.plot_info_dict['stat']} "
                                 +"from line type "
                                 +f"{self.plot_info_dict['line_type']} "
                                 +"average")
                stat_df, stat_array = gda_util.calculate_stat(
                    self.logger, all_model_df,
                    self.plot_info_dict['line_type'],
                    self.plot_info_dict['stat']
                )
                model_idx_list = (
                    stat_df.index.get_level_values(0).unique().tolist()
                )
                if self.plot_info_dict['event_equalization'] == 'YES':
                    self.logger.info("Doing event equalization")
                    masked_stat_array = np.ma.masked_invalid(stat_array)
                    stat_array = np.ma.mask_cols(masked_stat_array)
                    stat_array = stat_array.filled(fill_value=np.nan)
                    for model_idx in model_idx_list:
                        model_idx_num = model_idx_list.index(model_idx)
                        stat_df.loc[model_idx] = stat_array[model_idx_num,:]
                        all_model_df.loc[model_idx] = (
                            all_model_df.loc[model_idx].where(
                                stat_df.loc[model_idx].notna()
                        ).values)
                if forecast_hour \
                        == self.date_info_dict['forecast_hours'][0] \
                        and level == vert_profile_levels[0]:
                    stat_vert_prof_forecast_hours_avg_df = pd.DataFrame(
                        np.nan, pd.MultiIndex.from_product(
                            [model_idx_list,
                             self.date_info_dict['forecast_hours']],
                            names=['model', 'fhr']
                        ),
                        columns=vert_profile_levels
                    )
                for model_idx in model_idx_list:
                    model_idx_num = model_idx_list.index(model_idx)
                    if self.plot_info_dict['line_type'] in ['CNT', 'GRAD',
                                                            'CTS',
                                                            'NBRCTS',
                                                            'NBRCNT',
                                                            'VCNT']:
                        avg_method = 'mean'
                        calc_avg_df = stat_df.loc[model_idx]
                    else:
                        avg_method = 'aggregation'
                        calc_avg_df = all_model_df.loc[model_idx]
                    model_idx_forecast_hour_avg = gda_util.calculate_average(
                       self.logger, avg_method,
                       self.plot_info_dict['line_type'],
                       self.plot_info_dict['stat'], calc_avg_df
                    )
                    if not np.isnan(model_idx_forecast_hour_avg):
                        stat_vert_prof_forecast_hours_avg_df.loc[
                            (model_idx, forecast_hour), level
                        ] = model_idx_forecast_hour_avg
        # Set up plot
        self.logger.info(f"Setting up plot")
        plot_specs_lbl = PlotSpecs(self.logger, 'lead_by_level')
        plot_specs_lbl.set_up_plot()
        model_idx_list = (
            stat_vert_prof_forecast_hours_avg_df.index\
            .get_level_values(0).unique().tolist()
        )
        fhr_idx_list = (
            stat_vert_prof_forecast_hours_avg_df.index\
            .get_level_values(1).unique().tolist()
        )
        ymesh, xmesh = np.meshgrid(vert_profile_levels_int, fhr_idx_list)
        nsubplots = len(model_idx_list)
        if nsubplots == 1:
            gs_row, gs_col = 1, 1
            gs_hspace, gs_wspace = 0, 0
            gs_bottom, gs_top = 0.225, 0.85
            cbar_bottom = 0.075
            cbar_height = 0.02
        elif nsubplots == 2:
            gs_row, gs_col = 1, 2
            gs_hspace, gs_wspace = 0, 0.1
            gs_bottom, gs_top = 0.225, 0.85
            cbar_bottom = 0.075
            cbar_height = 0.02
        elif nsubplots > 2 and nsubplots <= 4:
            gs_row, gs_col = 2, 2
            gs_hspace, gs_wspace = 0.15, 0.1
            gs_bottom, gs_top = 0.125, 0.9
            cbar_bottom = 0.04
            cbar_height = 0.02
        elif nsubplots > 4 and nsubplots <= 6:
            gs_row, gs_col = 3, 2
            gs_hspace, gs_wspace = 0.15, 0.1
            gs_bottom, gs_top = 0.125, 0.9
            cbar_bottom = 0.04
            cbar_height = 0.02
        elif nsubplots > 6 and nsubplots <= 8:
            gs_row, gs_col = 4, 2
            gs_hspace, gs_wspace = 0.175, 0.1
            gs_bottom, gs_top = 0.125, 0.9
            cbar_bottom = 0.04
            cbar_height = 0.02
        elif nsubplots > 8 and nsubplots <= 10:
            gs_row, gs_col = 5, 2
            gs_hspace, gs_wspace = 0.225, 0.1
            gs_bottom, gs_top = 0.125, 0.9
            cbar_bottom = 0.04
            cbar_height = 0.02
        else:
            self.logger.error("Too many subplots requested, maximum is 10")
            sys.exit(1)
        if nsubplots <= 2:
            plot_specs_lbl.fig_size = (16., 8.)
            plot_specs_lbl.fig_title_size = 16
            plt.rcParams['figure.titlesize'] = plot_specs_lbl.fig_title_size
        if nsubplots >= 2:
            n_xticks = 8
        else:
            n_xticks = 17
        if len(self.date_info_dict['forecast_hours']) <= n_xticks:
            xticks = self.date_info_dict['forecast_hours']
        else:
            xticks = []
            for fhr in self.date_info_dict['forecast_hours']:
                if int(fhr) % 24 == 0:
                    xticks.append(fhr)
            if len(xticks) > n_xticks:
                xtick_intvl = int(len(xticks)/n_xticks)
                xticks = xticks[::xtick_intvl]
        vert_profile_levels_int_ticks = vert_profile_levels_int
        if self.plot_info_dict['vert_profile'] == 'all' \
                and self.plot_info_dict['fcst_var_name'] != 'O3MR':
            for del_lev in [925, 700, 500, 250, 100]:
                vert_profile_levels_int_ticks = np.delete(
                    vert_profile_levels_int_ticks,
                    np.where(vert_profile_levels_int_ticks == del_lev)
                )
        elif self.plot_info_dict['vert_profile'] == 'trop':
            vert_profile_levels_int_ticks = np.delete(
                vert_profile_levels_int_ticks,
                np.where(vert_profile_levels_int_ticks == 925)
            )
        fcst_units = np.unique(fcst_units)
        fcst_units = np.delete(fcst_units, np.where(fcst_units == 'nan'))
        if len(fcst_units) > 1:
            self.logger.error(f"Have multilple units: {', '.join(fcst_units)}")
            sys.exit(1)
        elif len(fcst_units) == 0:
            self.logger.debug("Cannot get variables units, leaving blank")
            fcst_units = ['']
        plot_title = plot_specs_lbl.get_plot_title(
            self.plot_info_dict, self.date_info_dict,
            fcst_units[0]
        )
        plot_left_logo_path = os.path.join(self.logo_dir, 'noaa.png')
        if os.path.exists(plot_left_logo_path):
            plot_left_logo = True
            left_logo_img_array = matplotlib.image.imread(
                plot_left_logo_path
            )
            left_logo_xpixel_loc, left_logo_ypixel_loc, left_logo_alpha = (
                plot_specs_lbl.get_logo_location(
                    'left', plot_specs_lbl.fig_size[0],
                    plot_specs_lbl.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
        else:
            plot_left_logo = False
            self.logger.debug(f"{plot_left_logo_path} does not exist")
        plot_right_logo_path = os.path.join(self.logo_dir, 'nws.png')
        if os.path.exists(plot_right_logo_path):
            plot_right_logo = True
            right_logo_img_array = matplotlib.image.imread(
                 plot_right_logo_path
            )
            right_logo_xpixel_loc, right_logo_ypixel_loc, right_logo_alpha = (
                plot_specs_lbl.get_logo_location(
                    'right', plot_specs_lbl.fig_size[0],
                    plot_specs_lbl.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
        else:
            plot_right_logo = False
            self.logger.debug(f"{plot_right_logo_path} does not exist")
        image_name = plot_specs_lbl.get_savefig_name(
            self.output_dir, self.plot_info_dict, self.date_info_dict
        )
        subplot0_cmap, subplotsN_cmap = plot_specs_lbl.get_plot_colormaps(
            self.plot_info_dict['stat']
        )
        subplot0_data = (
            stat_vert_prof_forecast_hours_avg_df.loc[
                model_idx_list[0]
            ].values
        )
        for model_idx in model_idx_list[1:]:
            subplotN_data = (
                stat_vert_prof_forecast_hours_avg_df.loc[
                    model_idx
                ].values
            )
            if model_idx == model_idx_list[1]:
                subplotsN_data = [subplotN_data]
            else:
                subplotsN_data = np.concatenate((subplotsN_data,
                                                 [subplotN_data]))
        if len(model_idx_list) == 1:
            subplotsN_data = [np.nan]
        (have_subplot0_levs, subplot0_levs,
         have_subplotsN_levs, subplotsN_levs) = (
            plot_specs_lbl.get_plot_contour_levels(
                self.plot_info_dict['stat'], subplot0_data, subplotsN_data
            )
        )
        make_colorbar = False
        # Make plot
        self.logger.info(f"Making plot")
        fig = plt.figure(figsize=(plot_specs_lbl.fig_size[0],
                                  plot_specs_lbl.fig_size[1]))
        gs = gridspec.GridSpec(gs_row, gs_col,
                               bottom=gs_bottom, top=gs_top,
                               hspace=gs_hspace, wspace=gs_wspace)
        fig.suptitle(plot_title)
        if plot_left_logo:
            left_logo_img = fig.figimage(
                left_logo_img_array,
                left_logo_xpixel_loc - (left_logo_xpixel_loc * 0.5),
                left_logo_ypixel_loc, zorder=1, alpha=right_logo_alpha
            )
            left_logo_img.set_visible(True)
        if plot_right_logo:
            right_logo_img = fig.figimage(
                right_logo_img_array, right_logo_xpixel_loc,
                right_logo_ypixel_loc, zorder=1, alpha=right_logo_alpha
            )
        for model_idx in model_idx_list:
            model_num = model_idx.split('/')[0]
            model_num_name = model_idx.split('/')[1]
            model_num_plot_name = model_idx.split('/')[2]
            model_num_obs_name = (
                self.model_info_dict[model_num]['obs_name']
            )
            model_num_data = stat_vert_prof_forecast_hours_avg_df.loc[
                model_idx
            ].values
            masked_model_num_data = np.ma.masked_invalid(model_num_data)
            ax = plt.subplot(gs[model_idx_list.index(model_idx)])
            ax.grid(True)
            ax.set_xlim([self.date_info_dict['forecast_hours'][0],
                         self.date_info_dict['forecast_hours'][-1]])
            ax.set_xticks(xticks)
            if ax.get_subplotspec().is_last_row() \
                    or (nsubplots % 2 != 0 \
                        and model_idx_list.index(model_idx) \
                        == nsubplots-1):
                ax.set_xlabel('Forecast Hour')
            else:
                plt.setp(ax.get_xticklabels(), visible=False)
            ax.set_yscale('log')
            ax.minorticks_off()
            ax.set_yticks(vert_profile_levels_int_ticks)
            ax.set_yticklabels(vert_profile_levels_int_ticks)
            ax.set_ylim([vert_profile_levels_int[0],
                         vert_profile_levels_int[-1]])
            if ax.get_subplotspec().is_first_col() \
                    or (nsubplots % 2 != 0 \
                        and model_idx_list.index(model_idx) \
                        == nsubplots -1):
                ax.set_ylabel('Pressure Level (hPa)')
            else:
                plt.setp(ax.get_yticklabels(), visible=False)
            if model_idx == model_idx_list[0]:
                self.logger.debug(f"Plotting {model_num} ["
                                  +f"{model_num_name},"
                                  +f"{model_num_plot_name}]")
                ax.set_title(model_num_plot_name)
                subplot_name = model_num_name
                subplot0_plot_name = model_num_plot_name
                subplot0_data = masked_model_num_data
                if not subplot0_data.mask.all():
                    if have_subplot0_levs:
                        CF0 = ax.contourf(xmesh, ymesh, subplot0_data,
                                          levels=subplot0_levs,
                                          cmap=subplot0_cmap,
                                          extend='both')
                    else:
                        CF0 = ax.contourf(xmesh, ymesh, subplot0_data,
                                          cmap=subplot0_cmap,
                                          extend='both')
                    C0 = ax.contour(xmesh, ymesh, subplot0_data,
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
                    if self.plot_info_dict['stat'] in ['BIAS', 'ME', 'FBIAS']:
                        if not make_colorbar:
                            make_colorbar = True
                            cbar_CF = CF0
                            cbar_ticks = CF0.levels
                            cbar_label = plot_specs_lbl.get_stat_plot_name(
                                self.plot_info_dict['stat']
                            )
                else:
                    self.logger.debug(f"{model_num} [{model_num_name},"
                                      +f"{model_num_plot_name}] is fully "
                                      +"masked")
            else:
                if self.plot_info_dict['stat'] in ['BIAS', 'ME', 'FBIAS']:
                    self.logger.debug(f"Plotting {model_num} ["
                                      +f"{model_num_name},"
                                      +f"{model_num_plot_name}]")
                    ax.set_title(model_num_plot_name)
                    subplotN_data = masked_model_num_data
                else:
                    self.logger.debug(f"Plotting {model_num} ["
                                      +f"{model_num_name},"
                                      +f"{model_num_plot_name}] "
                                      +"difference from model1 ["
                                      +f"{subplot_name},"
                                      +f"{subplot0_plot_name}]")
                    ax.set_title(model_num_plot_name+'-'+subplot0_plot_name)
                    subplotN_data = masked_model_num_data - subplot0_data
                if not subplotN_data.mask.all():
                    if have_subplotsN_levs:
                        CFN = ax.contourf(xmesh, ymesh, subplotN_data,
                                          levels=subplotsN_levs,
                                          cmap=subplotsN_cmap,
                                          extend='both')
                        if self.plot_info_dict['stat'] in ['BIAS', 'ME',
                                                           'FBIAS']:
                            CN = ax.contour(xmesh, ymesh, subplotN_data,
                                            levels=CFN.levels, colors='k',
                                            linewidths=1.0)
                            CN_labels_list = []
                            for lev in CN.levels:
                                if str(lev).split('.')[1] == '0':
                                    CN_labels_list.append(str(int(lev)))
                                else:
                                    CN_labels_list.append(
                                        str(round(lev,3)).rstrip('0')
                                    )
                            CN_fmt = {}
                            for lev, label in zip(CN.levels,
                                                  CN_labels_list):
                                CN_fmt[lev] = label
                            ax.clabel(CN, CN.levels,
                                      fmt=CN_fmt, inline=True,
                                      fontsize=12.5)
                        if not make_colorbar:
                            make_colorbar = True
                            cbar_CF = CFN
                            cbar_ticks = CFN.levels
                            if self.plot_info_dict['stat'] in ['BIAS', 'ME',
                                                               'FBIAS']:
                                cbar_label = (
                                    plot_specs_lbl.get_stat_plot_name(
                                        self.plot_info_dict['stat']
                                    )
                                )
                            else:
                                cbar_label = 'Difference'
                    else:
                        self.logger.debug("Do not have contour levels "
                                          +"to plot")
                else:
                    if self.plot_info_dict['stat'] in ['BIAS', 'ME', 'FBIAS']:
                        self.logger.debug(f"{model_num} ["
                                          +f"{model_num_name},"
                                          +f"{model_num_plot_name}] is fully "
                                          +"masked")
                    else:
                        self.logger.debug(f"{model_num} ["
                                          +f"{model_num_name},"
                                          +f"{model_num_plot_name}] "
                                          +"difference from model1 ["
                                          +f"{subplot_name},"
                                          +f"{subplot0_plot_name}] is fully "
                                          +"masked")
                    if os.environ['evs_run_mode'] == 'production' \
                            and model_num_plot_name == 'jma' \
                            and (int(self.date_info_dict['forecast_hours'][1])\
                            - int(self.date_info_dict['forecast_hours'][0])) \
                            == 12:
                        ax.set_title('Forecasts not available at 12-h intervals',
                                     loc='right')
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
    MODEL_INFO_DICT = {
        'model1': {'name': 'MODEL_A',
                   'plot_name': 'PLOT_MODEL_A',
                   'obs_name': 'MODEL_A_OBS'},
    }
    DATE_INFO_DICT = {
        'date_type': 'DATE_TYPE',
        'start_date': 'START_DATE',
        'end_date': 'END_DATE',
        'valid_hr_start': 'VALID_HR_START',
        'valid_hr_end': 'VALID_HR_END',
        'valid_hr_inc': 'VALID_HR_INC',
        'init_hr_start': 'INIT_HR_START',
        'init_hr_end': 'INIT_HR_END',
        'init_hr_inc': 'INIT_HR_INC',
        'forecast_hour': ['FORECAST_HOURS']
    }
    PLOT_INFO_DICT = {
        'line_type': 'LINE_TYPE',
        'grid': 'GRID',
        'stat': 'STAT',
        'vx_mask': 'VX_MASK',
        'event_equalization': 'EVENT_EQUALIZATION',
        'interp_method': 'INTERP_METHOD',
        'interp_points': 'INTERP_POINTS',
        'fcst_var_name': 'FCST_VAR_NAME',
        'fcst_var_thresh': 'FCST_VAR_THRESH',
        'obs_var_name': 'OBS_VAR_NAME',
        'obs_var_thresh': 'OBS_VAR_THRESH',
        'vert_profile': 'all'
    }
    MET_INFO_DICT = {
        'root': '/PATH/TO/MET',
        'version': '12.0'
    }
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
    p = LeadByLevel(logger, INPUT_DIR, OUTPUT_DIR, MODEL_INFO_DICT,
                    DATE_INFO_DICT, PLOT_INFO_DICT, MET_INFO_DICT, LOGO_DIR)
    p.make_lead_by_level()

if __name__ == "__main__":
    main()
