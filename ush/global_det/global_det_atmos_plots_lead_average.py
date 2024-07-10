#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_lead_average.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script generates a lead average plot.
          (x-axis: forecast hour; y-axis: statistics value)
          (EVS Graphics Naming Convention: fhrmean)
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
import matplotlib.dates as md
import global_det_atmos_util as gda_util
from global_det_atmos_plots_specs import PlotSpecs

class LeadAverage:
    """
    Make a lead average graphic
    """

    def __init__(self, logger, input_dir, output_dir, model_info_dict,
                 date_info_dict, plot_info_dict, met_info_dict, logo_dir):
        """! Initalize LeadAverage class

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

    def make_lead_average(self):
        """! Make the lead average graphic

             Args:

             Returns:
        """
        self.logger.info("Plot Type: Lead Average")
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
            self.logger.error("Cannot make lead_average for stat "
                              +f"{self.plot_info_dict['stat']}")
            sys.exit(1)
        # Make dataframe for all forecast hours
        self.logger.info("Building dataframe for all forecast hours")
        self.logger.info(f"Reading in model stat files from {self.input_dir}")
        fcst_units = []
        for forecast_hour in self.date_info_dict['forecast_hours']:
            self.logger.info(f"Building data for forecast hour {forecast_hour}")
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
            format_valid_dates = [valid_dates[d].strftime('%Y%m%d_%H%M%S') \
                                  for d in range(len(valid_dates))]
            format_init_dates = [init_dates[d].strftime('%Y%m%d_%H%M%S') \
                                 for d in range(len(init_dates))]
            if self.date_info_dict['date_type'] == 'VALID':
                self.logger.debug("Based on date information, plot will display "
                                  +"valid dates "+', '.join(format_valid_dates)+" "
                                  +"for forecast hour "
                                  +f"{forecast_hour} with initialization dates "
                                  +', '.join(format_init_dates))
                plot_dates = valid_dates
            elif self.date_info_dict['date_type'] == 'INIT':
                self.logger.debug("Based on date information, plot will display "
                                  +"initialization dates "
                                  +', '.join(format_init_dates)+" "
                                  +"for forecast hour "
                                  +f"{forecast_hour} with valid dates "
                                  +', '.join(format_valid_dates))
                plot_dates = init_dates
            # Read in data
            all_model_df = gda_util.build_df(
                'make_plots', self.logger, self.input_dir, self.output_dir,
                self.model_info_dict, self.met_info_dict,
                self.plot_info_dict['fcst_var_name'],
                self.plot_info_dict['fcst_var_level'],
                self.plot_info_dict['fcst_var_thresh'],
                self.plot_info_dict['obs_var_name'],
                self.plot_info_dict['obs_var_level'],
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
                all_model_df['FCST_UNITS'].values.astype('str').tolist()
            )
            # Calculate statistic mean and 95% confidence intervals
            self.logger.info(f"Calculating statstic {self.plot_info_dict['stat']} "
                             +f"from line type {self.plot_info_dict['line_type']} "
                             +"average and 95% confidence intervals")
            stat_df, stat_array = gda_util.calculate_stat(
                self.logger, all_model_df, self.plot_info_dict['line_type'],
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
            if forecast_hour == self.date_info_dict['forecast_hours'][0]:
                forecast_hours_avg_df = pd.DataFrame(
                    np.nan, model_idx_list,
                    columns=self.date_info_dict['forecast_hours']
                )
                forecast_hours_ci_df = pd.DataFrame(
                    np.nan, model_idx_list,
                    columns=self.date_info_dict['forecast_hours']
                )
            for model_idx in model_idx_list:
                model_idx_num = model_idx_list.index(model_idx)
                if self.plot_info_dict['line_type'] in ['CNT', 'GRAD',
                                                        'CTS', 'NBRCTS',
                                                        'NBRCNT', 'VCNT']:
                    avg_method = 'mean'
                    calc_avg_df = stat_df.loc[model_idx]
                else:
                    avg_method = 'aggregation'
                    calc_avg_df = all_model_df.loc[model_idx]
                model_idx_forecast_hour_avg = gda_util.calculate_average(
                    self.logger, avg_method, self.plot_info_dict['line_type'],
                    self.plot_info_dict['stat'], calc_avg_df
                )
                if not np.isnan(model_idx_forecast_hour_avg) \
                        and not np.ma.is_masked(model_idx_forecast_hour_avg):
                    forecast_hours_avg_df.loc[model_idx, forecast_hour] = (
                        model_idx_forecast_hour_avg
                    )
                if model_idx == model_idx_list[0]:
                    model1_stat_df = stat_df.loc[model_idx]
                else:
                    model_idx_model1_diff = np.ma.masked_invalid(
                        stat_df.loc[model_idx] - model1_stat_df
                    )
                    nsamples = (len(model_idx_model1_diff)
                                -np.ma.count_masked(model_idx_model1_diff))
                    model_idx_model1_diff_mean = np.mean(model_idx_model1_diff)
                    model_idx_model1_diff_std = np.std(model_idx_model1_diff)
                    ##Null Hypothesis: mean(M1-M2)=0,
                    ##M1-M2 follows normal distribution.
                    ##plot the 5% conf interval of difference of means
                    ##F*SD/sqrt(N-1),
                    ##F=1.96 for infinite samples, F=2.0 for nsz=60,
                    ##F=2.042 for nsz=30, F=2.228 for nsz=10
                    if nsamples > 1:
                        model_idx_model1_diff_mean_std_err = (
                            model_idx_model1_diff_std/np.sqrt(nsamples-1)
                        )
                        if nsamples >= 80:
                            ci = 1.960 * model_idx_model1_diff_mean_std_err
                        elif nsamples >=40 and nsamples < 80:
                            ci = 2.000 * model_idx_model1_diff_mean_std_err
                        elif nsamples >= 20 and nsamples < 40:
                            ci = 2.042 * model_idx_model1_diff_mean_std_err
                        elif nsamples > 0 and nsamples < 20:
                            ci = 2.228 * model_idx_model1_diff_mean_std_err
                    else:
                        ci = np.nan
                    forecast_hours_ci_df.loc[model_idx, forecast_hour] = ci
                    #from scipy import stats
                    #scipy_ci = stats.t.interval(
                    #    alpha=0.95,
                    #    df=len(np.ma.compressed(model_idx_model1_diff))-1,
                    #    loc=0,
                    #    scale=stats.sem(np.ma.compressed(model_idx_model1_diff))
                    #)
        # Set up plot
        self.logger.info(f"Setting up plot")
        plot_specs_la = PlotSpecs(self.logger, 'lead_average')
        plot_specs_la.set_up_plot()
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
        stat_min_max_dict = {
            'ax1_stat_min': np.ma.masked_invalid(np.nan),
            'ax1_stat_max': np.ma.masked_invalid(np.nan),
            'ax2_stat_min': np.ma.masked_invalid(np.nan),
            'ax2_stat_max': np.ma.masked_invalid(np.nan)
        }
        stat_plot_name = plot_specs_la.get_stat_plot_name(
             self.plot_info_dict['stat']
        )
        fcst_units = np.unique(fcst_units)
        fcst_units = np.delete(fcst_units, np.where(fcst_units == 'nan'))
        if len(fcst_units) > 1:
            self.logger.error(f"Have multilple units: {', '.join(fcst_units)}")
            sys.exit(1)
        elif len(fcst_units) == 0:
            self.logger.debug("Cannot get variables units, leaving blank")
            fcst_units = ['']
        plot_title = plot_specs_la.get_plot_title(
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
                plot_specs_la.get_logo_location(
                    'left', plot_specs_la.fig_size[0],
                    plot_specs_la.fig_size[1], plt.rcParams['figure.dpi']
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
                plot_specs_la.get_logo_location(
                    'right', plot_specs_la.fig_size[0],
                    plot_specs_la.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
        else:
            plot_right_logo = False
            self.logger.debug(f"{plot_right_logo_path} does not exist")
        image_name = plot_specs_la.get_savefig_name(
            self.output_dir, self.plot_info_dict, self.date_info_dict
        )
        # Make plot
        self.logger.info(f"Making plot")
        fig, (ax1, ax2) = plt.subplots(2,1,
                                       figsize=(plot_specs_la.fig_size[0],
                                                plot_specs_la.fig_size[1]),
                                       sharex=True)
        fig.suptitle(plot_title)
        ax1.grid(True)
        ax1.set_ylabel(stat_plot_name)
        ax2.grid(True)
        ax2.set_xlabel('Forecast Hour')
        ax2.set_xlim([self.date_info_dict['forecast_hours'][0],
                      self.date_info_dict['forecast_hours'][-1]])
        ax2.set_xticks(xticks)
        ax2.set_ylabel('Difference')
        ax2.set_title('Difference from '
                      +self.model_info_dict['model1']['plot_name'], loc='left')
        props = {'boxstyle': 'square',
                 'pad': 0.35,
                 'facecolor': 'white',
                 'linestyle': 'solid',
                 'linewidth': 1,
                 'edgecolor': 'black'}
        ax2.text(0.995, 1.05, 'Note: points outside the '
                 +'outline bars are significant at the 95% '
                 +'confidence level', ha='right', va='center',
                 fontsize=13, bbox=props, transform=ax2.transAxes)
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
        model_plot_settings_dict = plot_specs_la.get_model_plot_settings()
        model_idx_list = (
            forecast_hours_avg_df.index.get_level_values(0).unique().tolist()
        )
        ci_bar_max_widths = np.append(
            np.diff(self.date_info_dict['forecast_hours']),
            self.date_info_dict['forecast_hours'][-1]
            -self.date_info_dict['forecast_hours'][-2]
        )/1.5
        ci_bar_min_widths = np.append(
            np.diff(self.date_info_dict['forecast_hours']),
            self.date_info_dict['forecast_hours'][-1]
            -self.date_info_dict['forecast_hours'][-2]
        )/len(list(self.model_info_dict.keys()))
        ci_bar_intvl_widths = (
            (ci_bar_max_widths-ci_bar_min_widths)
            /len(list(self.model_info_dict.keys()))
        )
        for model_idx in model_idx_list:
            model_num = model_idx.split('/')[0]
            model_num_name = model_idx.split('/')[1]
            model_num_plot_name = model_idx.split('/')[2]
            model_num_obs_name = self.model_info_dict[model_num]['obs_name']
            model_num_data = forecast_hours_avg_df.loc[model_idx]
            if model_num_name in list(model_plot_settings_dict.keys()):
                model_num_plot_settings_dict = (
                    model_plot_settings_dict[model_num_name]
                )
            else:
                model_num_plot_settings_dict = (
                    model_plot_settings_dict[model_num]
                )
            masked_model_num_data = np.ma.masked_invalid(model_num_data)
            if model_num == 'model1':
                 model1_masked_model_num_data = masked_model_num_data
                 model1_name = model_num_name
                 model1_plot_name = model_num_plot_name
            model_num_npts = (
                len(masked_model_num_data)
                - np.ma.count_masked(masked_model_num_data)
            )
            masked_forecast_hours = np.ma.masked_where(
                np.ma.getmask(masked_model_num_data),
                forecast_hours_avg_df.columns.values.tolist()
            )
            self.logger.debug(f"Plotting {model_num} [{model_num_name},"
                              +f"{model_num_plot_name}]")
            if model_num_npts != 0:
                ax1.plot(
                    np.ma.compressed(masked_forecast_hours),
                    np.ma.compressed(masked_model_num_data),
                    color = model_num_plot_settings_dict['color'],
                    linestyle = model_num_plot_settings_dict['linestyle'],
                    linewidth = model_num_plot_settings_dict['linewidth'],
                    marker = model_num_plot_settings_dict['marker'],
                    markersize = model_num_plot_settings_dict['markersize'],
                    label = model_num_plot_name,
                    zorder = (len(list(self.model_info_dict.keys()))
                              - model_idx_list.index(model_idx) + 4)
                )
                if masked_model_num_data.min() \
                        < stat_min_max_dict['ax1_stat_min'] \
                        or np.ma.is_masked(stat_min_max_dict['ax1_stat_min']):
                    stat_min_max_dict['ax1_stat_min'] = (
                        masked_model_num_data.min()
                    )
                if masked_model_num_data.max() \
                        > stat_min_max_dict['ax1_stat_max'] \
                        or np.ma.is_masked(stat_min_max_dict['ax1_stat_max']):
                    stat_min_max_dict['ax1_stat_max'] = (
                        masked_model_num_data.max()
                    )
            else:
                self.logger.debug(f"{model_num} [{model_num_name},"
                                  +f"{model_num_plot_name}] has no points")
            masked_model_num_model1_diff_data = np.ma.masked_invalid(
                model_num_data - model1_masked_model_num_data
            )
            model_num_diff_npts = (
                len(masked_model_num_model1_diff_data)
                - np.ma.count_masked(masked_model_num_model1_diff_data)
            )
            masked_diff_forecast_hours = np.ma.masked_where(
                np.ma.getmask(masked_model_num_model1_diff_data),
                forecast_hours_avg_df.columns.values.tolist()
            )
            self.logger.debug(f"Plotting {model_num} [{model_num_name},"
                              +f"{model_num_plot_name}] difference from "
                              +f"model1 [{model1_name},"
                              +f"{model1_plot_name}]")
            if model_num_diff_npts != 0:
                ax2.plot(
                    np.ma.compressed(masked_diff_forecast_hours),
                    np.ma.compressed(masked_model_num_model1_diff_data),
                    color = model_num_plot_settings_dict['color'],
                    linestyle = model_num_plot_settings_dict['linestyle'],
                    linewidth = model_num_plot_settings_dict['linewidth'],
                    marker = model_num_plot_settings_dict['marker'],
                    markersize = model_num_plot_settings_dict['markersize'],
                    zorder = (len(list(self.model_info_dict.keys()))
                              - model_idx_list.index(model_idx) + 4)
                )
                if masked_model_num_model1_diff_data.min() \
                        < stat_min_max_dict['ax2_stat_min'] \
                        or np.ma.is_masked(stat_min_max_dict['ax2_stat_min']):
                    stat_min_max_dict['ax2_stat_min'] = (
                        masked_model_num_model1_diff_data.min()
                    )
                if masked_model_num_model1_diff_data.max() \
                        > stat_min_max_dict['ax2_stat_max'] \
                        or np.ma.is_masked(stat_min_max_dict['ax2_stat_max']):
                    stat_min_max_dict['ax2_stat_max'] = (
                        masked_model_num_model1_diff_data.max()
                    )
            else:
                self.logger.debug(f"{model_num} [{model_num_name},"
                                  +f"{model_num_plot_name}] difference from "
                                  +f"model1 [{model1_name},{model1_plot_name}] "
                                  +"has no points")
                                  
            if model_num == 'model1':
                ax2.plot(
                    forecast_hours_avg_df.columns.values.tolist(),
                    np.zeros_like(forecast_hours_avg_df.columns.values.tolist()),
                    color = model_num_plot_settings_dict['color'],
                    linestyle = model_num_plot_settings_dict['linestyle'],
                    linewidth = model_num_plot_settings_dict['linewidth'],
                    marker = None,
                    markersize = model_num_plot_settings_dict['markersize'],
                    zorder = (len(list(self.model_info_dict.keys()))
                              - model_idx_list.index(model_idx) + 4)
                )
            if model_num != 'model1':
                masked_model_num_model1_diff_ci_data = np.ma.masked_invalid(
                    forecast_hours_ci_df.loc[model_idx]
                )
                model_num_ci_npts = (
                    len(masked_model_num_model1_diff_ci_data)
                    - np.ma.count_masked(masked_model_num_model1_diff_ci_data)
                )
                masked_ci_forecast_hours = np.ma.masked_where(
                    np.ma.getmask(masked_model_num_model1_diff_ci_data),
                    forecast_hours_ci_df.columns.values.tolist()
                )
                self.logger.debug(f"Plotting {model_num} ["
                                  +f"{model_num_name},"
                                  +f"{model_num_plot_name}] difference "
                                  +f"from model1 [{model1_name},"
                                  +f"{model1_plot_name}] "
                                  +"confidence intervals")
                if model_num_ci_npts != 0:
                    ci_min = masked_model_num_model1_diff_ci_data.min()
                    ci_max = masked_model_num_model1_diff_ci_data.max()
                    if ci_min < stat_min_max_dict['ax2_stat_min'] \
                            or np.ma.is_masked(stat_min_max_dict['ax2_stat_min']):
                        if not np.ma.is_masked(ci_min):
                            stat_min_max_dict['ax2_stat_min'] = ci_min
                    if ci_max > stat_min_max_dict['ax2_stat_max'] \
                            or np.ma.is_masked(stat_min_max_dict['ax2_stat_max']):
                        if not np.ma.is_masked(ci_max):
                            stat_min_max_dict['ax2_stat_max'] = ci_max
                    cmasked_ci_forecast_hours = np.ma.compressed(
                        masked_ci_forecast_hours
                    )
                    cmasked_model_num_model1_diff_ci_data = np.ma.compressed(
                        masked_model_num_model1_diff_ci_data
                    )
                    cmasked_ci_bar_max_widths = np.ma.compressed(
                        np.ma.masked_where(
                            np.ma.getmask(masked_model_num_model1_diff_ci_data),
                            ci_bar_max_widths
                        )
                    )
                    cmasked_ci_bar_intvl_widths = np.ma.compressed(
                        np.ma.masked_where(
                            np.ma.getmask(masked_model_num_model1_diff_ci_data),
                            ci_bar_intvl_widths
                        )
                    )
                    for fhr_idx in range(len(cmasked_ci_forecast_hours)):
                        fhr = cmasked_ci_forecast_hours[fhr_idx]
                        fhr_ci = (
                            cmasked_model_num_model1_diff_ci_data[fhr_idx]
                        )
                        ax2.bar(fhr, 2*np.absolute(fhr_ci),
                                bottom=-1*np.absolute(fhr_ci),
                                width=(cmasked_ci_bar_max_widths[fhr_idx]
                                       -(cmasked_ci_bar_intvl_widths[fhr_idx]
                                       *model_idx_list.index(model_idx))),
                                color = 'None',
                                edgecolor=model_num_plot_settings_dict['color'],
                                linewidth=1)
                else:
                    self.logger.debug(f"{model_num}: ["
                                      +f"{model_num_name},"
                                      +f"{model_num_plot_name}] difference "
                                      +f"from model1 [{model1_name},"
                                      +f"{model1_plot_name}] "
                                      +"confidence intervals has no points")
        subplot_num = 1
        for ax in fig.get_axes():
            stat_min = stat_min_max_dict['ax'+str(subplot_num)+'_stat_min']
            stat_max = stat_min_max_dict['ax'+str(subplot_num)+'_stat_max']
            preset_y_axis_tick_min = ax.get_yticks()[0]
            preset_y_axis_tick_max = ax.get_yticks()[-1]
            preset_y_axis_tick_inc = ax.get_yticks()[1] - ax.get_yticks()[0]
            if self.plot_info_dict['stat'] in ['ACC'] and subplot_num == 1:
                y_axis_tick_inc = 0.1
            else:
                y_axis_tick_inc = preset_y_axis_tick_inc
            if np.ma.is_masked(stat_min):
                y_axis_min = preset_y_axis_tick_min
            else:
                if self.plot_info_dict['stat'] in ['ACC'] and subplot_num == 1:
                    y_axis_min = round(stat_min,1) - y_axis_tick_inc
                else:
                    y_axis_min = preset_y_axis_tick_min
                    while y_axis_min > stat_min:
                        y_axis_min = y_axis_min - y_axis_tick_inc
            if np.ma.is_masked(stat_max):
                y_axis_max = preset_y_axis_tick_max
            else:
                if self.plot_info_dict['stat'] in ['ACC'] and subplot_num == 1:
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
        if len(ax1.lines) != 0:
            y_axis_min = ax1.get_yticks()[0]
            y_axis_max = ax1.get_yticks()[-1]
            y_axis_tick_inc = ax1.get_yticks()[1] - ax1.get_yticks()[0]
            stat_min = stat_min_max_dict['ax1_stat_min']
            stat_max = stat_min_max_dict['ax1_stat_max']
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
        'forecast_hours': ['FORECAST_HOURS']
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
        'fcst_var_level': 'FCST_VAR_LEVEL',
        'fcst_var_thresh': 'FCST_VAR_THRESH',
        'obs_var_name': 'OBS_VAR_NAME',
        'obs_var_level': 'OBS_VAR_LEVEL',
        'obs_var_thresh': 'OBS_VAR_THRESH',
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
    p = LeadAverage(logger, INPUT_DIR, OUTPUT_DIR, MODEL_INFO_DICT,
                    DATE_INFO_DICT, PLOT_INFO_DICT, MET_INFO_DICT, LOGO_DIR)
    p.make_lead_average()

if __name__ == "__main__":
    main()
