#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_time_series.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script generates a time series plot.
          (x-axis: dates; y-axis: statistics value)
          (EVS Graphics Naming Convention: timeseries)
'''

import sys
import os
import logging
import datetime
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
import global_det_atmos_util as gda_util
from global_det_atmos_plots_specs import PlotSpecs

class TimeSeries:
    """
    Create a time series graphic
    """

    def __init__(self, logger, input_dir, output_dir, model_info_dict,
                 date_info_dict, plot_info_dict, met_info_dict, logo_dir):
        """! Initalize TimeSeries class

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

    def make_time_series(self):
        """! Create the time series graphic

             Args:

             Returns:
        """
        self.logger.info(f"Creating time series...")
        self.logger.debug(f"Input directory: {self.input_dir}")
        self.logger.debug(f"Output directory: {self.output_dir}")
        self.logger.debug(f"Model information dictionary: "
                          +f"{self.model_info_dict}")
        self.logger.debug(f"Date information dictionary: "
                          +f"{self.date_info_dict}")
        self.logger.debug(f"Plot information dictionary: "
                          +f"{self.plot_info_dict}")
        # Get dates to plot
        self.logger.info("Creating valid and init date arrays")
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
            self.date_info_dict['forecast_hour']
        )
        format_valid_dates = [valid_dates[d].strftime('%Y%m%d_%H%M%S') \
                              for d in range(len(valid_dates))]
        format_init_dates = [init_dates[d].strftime('%Y%m%d_%H%M%S') \
                             for d in range(len(init_dates))]
        if self.date_info_dict['date_type'] == 'VALID':
            self.logger.debug("Based on date information, plot will display "
                              +"valid dates "+', '.join(format_valid_dates)+" "
                              +"for forecast hour "
                              +f"{self.date_info_dict['forecast_hour']} "
                              +"with initialization dates "
                              +', '.join(format_init_dates))
            if len(valid_dates) == 0:
                plot_dates = np.arange(
                    datetime.datetime.strptime(
                        self.date_info_dict['start_date']
                        +self.date_info_dict['valid_hr_start'],
                        '%Y%m%d%H'
                    ),
                    datetime.datetime.strptime(
                        self.date_info_dict['end_date']
                        +self.date_info_dict['valid_hr_end'],
                        '%Y%m%d%H'
                    )
                    +datetime.timedelta(
                        hours=int(self.date_info_dict['valid_hr_inc'])
                    ),
                    datetime.timedelta(
                        hours=int(self.date_info_dict['valid_hr_inc'])
                    )
                ).astype(datetime.datetime)
            else:
                plot_dates = valid_dates
        elif self.date_info_dict['date_type'] == 'INIT':
            self.logger.debug("Based on date information, plot will display "
                              +"initialization dates "
                              +', '.join(format_init_dates)+" "
                              +"for forecast hour "
                              +f"{self.date_info_dict['forecast_hour']} "
                              +"with valid dates "
                              +', '.join(format_valid_dates))
            if len(init_dates) == 0:
                plot_dates = np.arange(
                    datetime.datetime.strptime(
                        self.date_info_dict['start_date']
                        +self.date_info_dict['init_hr_start'],
                        '%Y%m%d%H'
                    ),
                    datetime.datetime.strptime(
                        self.date_info_dict['end_date']
                        +self.date_info_dict['init_hr_end'],
                        '%Y%m%d%H'
                    )
                    +datetime.timedelta(
                        hours=int(self.date_info_dict['init_hr_inc'])
                    ),
                    datetime.timedelta(
                        hours=int(self.date_info_dict['init_hr_inc'])
                    )
                ).astype(datetime.datetime)
            else:
                plot_dates = init_dates
        # Read in data
        self.logger.info(f"Reading in model stat files from {self.input_dir}")
        all_model_df = gda_util.build_df(
            self.logger, self.input_dir, self.output_dir,
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
            str(self.date_info_dict['forecast_hour'])
        )
        # Calculate statistic
        self.logger.info(f"Calculating statstic {self.plot_info_dict['stat']} "
                         +f"from line type {self.plot_info_dict['line_type']}")
        if self.plot_info_dict['stat'] == 'FBAR_OBAR':
            stat_df, stat_array = gda_util.calculate_stat(
                self.logger, all_model_df, self.plot_info_dict['line_type'],
                'FBAR'
            )
            obar_stat_df, obar_stat_array = gda_util.calculate_stat(
                self.logger, all_model_df, self.plot_info_dict['line_type'],
                'OBAR'
            )
        else:
            stat_df, stat_array = gda_util.calculate_stat(
                self.logger, all_model_df, self.plot_info_dict['line_type'],
                self.plot_info_dict['stat']
            )
        if self.plot_info_dict['event_equalization'] == 'YES':
            self.logger.debug("Doing event equalization")
            masked_stat_array = np.ma.masked_invalid(stat_array)
            stat_array = np.ma.mask_cols(masked_stat_array)
            stat_array = stat_array.filled(fill_value=np.nan)
            model_idx_list = (
                stat_df.index.get_level_values(0).unique().tolist()
            )
            for model_idx in model_idx_list:
                model_idx_num = model_idx_list.index(model_idx)
                stat_df.loc[model_idx] = stat_array[model_idx_num,:]
                all_model_df.loc[model_idx] = (
                    all_model_df.loc[model_idx].where(
                        stat_df.loc[model_idx].notna()
                ).values)
            if self.plot_info_dict['stat'] == 'FBAR_OBAR':
                masked_obar_stat_array = np.ma.masked_invalid(obar_stat_array)
                obar_stat_array = np.ma.mask_cols(masked_obar_stat_array)
                obar_stat_array = obar_stat_array.filled(fill_value=np.nan)
                model_idx_list = (
                   obar_stat_df.index.get_level_values(0).unique().tolist()
                )
                for model_idx in model_idx_list:
                    model_idx_num = model_idx_list.index(model_idx)
                    obar_stat_df.loc[model_idx] = (
                        obar_stat_array[model_idx_num,:]
                    )
                    all_model_df.loc[model_idx] = (
                        all_model_df.loc[model_idx].where(
                            obar_stat_df.loc[model_idx].notna()
                    ).values)
        # Set up plot
        self.logger.info(f"Doing plot set up")
        plot_specs_ts = PlotSpecs(self.logger, 'time_series')
        plot_specs_ts.set_up_plot()
        n_xticks = 5
        if len(plot_dates) < n_xticks:
            xtick_intvl = 1
        else:
            xtick_intvl = int(len(plot_dates)/n_xticks)
        date_intvl = int((plot_dates[1]-plot_dates[0]).total_seconds())
        stat_min = np.ma.masked_invalid(np.nan)
        stat_max = np.ma.masked_invalid(np.nan)
        stat_plot_name = plot_specs_ts.get_stat_plot_name(
             self.plot_info_dict['stat']
        )
        fcst_units = all_model_df['FCST_UNITS'].values.astype('str').tolist()
        fcst_units = np.unique(fcst_units)
        fcst_units = np.delete(fcst_units, np.where(fcst_units == 'nan'))
        if len(fcst_units) > 1:
            self.logger.error(f"Have multilple units: {', '.join(fcst_units)}")
            sys.exit(1)
        elif len(fcst_units) == 0:
            self.logger.debug("Cannot get variables units, leaving blank")
            fcst_units = ['']
        plot_title = plot_specs_ts.get_plot_title(
            self.plot_info_dict, self.date_info_dict,
            fcst_units[0]
        )
        plot_left_logo = False
        plot_left_logo_path = os.path.join(self.logo_dir, 'noaa.png')
        if os.path.exists(plot_left_logo_path):
            plot_left_logo = True
            left_logo_img_array = matplotlib.image.imread(
                plot_left_logo_path
            )
            left_logo_xpixel_loc, left_logo_ypixel_loc, left_logo_alpha = (
                plot_specs_ts.get_logo_location(
                    'left', plot_specs_ts.fig_size[0],
                    plot_specs_ts.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
        plot_right_logo = False
        plot_right_logo_path = os.path.join(self.logo_dir, 'nws.png')
        if os.path.exists(plot_right_logo_path):
            plot_right_logo = True
            right_logo_img_array = matplotlib.image.imread(
                plot_right_logo_path
            )
            right_logo_xpixel_loc, right_logo_ypixel_loc, right_logo_alpha = (
                plot_specs_ts.get_logo_location(
                    'right', plot_specs_ts.fig_size[0],
                    plot_specs_ts.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
        image_name = plot_specs_ts.get_savefig_name(
            self.output_dir, self.plot_info_dict, self.date_info_dict
        )
        # Create plot
        self.logger.info(f"Creating plot for {self.plot_info_dict['stat']} ")
        fig, ax = plt.subplots(1,1,figsize=(plot_specs_ts.fig_size[0],
                                            plot_specs_ts.fig_size[1]))
        ax.grid(True)
        ax.set_xlabel(self.date_info_dict['date_type'].title()+' Date')
        ax.set_xlim([plot_dates[0], plot_dates[-1]])
        ax.set_xticks(plot_dates[::xtick_intvl])
        ax.xaxis.set_major_formatter(md.DateFormatter('%HZ %d%b%Y'))
        hr_minor_tick_type = self.date_info_dict['date_type'].lower()
        ax.xaxis.set_minor_locator(
            md.HourLocator(byhour=range(
                int(self.date_info_dict[f"{hr_minor_tick_type}_hr_start"]),
                int(self.date_info_dict[f"{hr_minor_tick_type}_hr_end"])+1,
                int(self.date_info_dict[f"{hr_minor_tick_type}_hr_inc"])
            ))
        )
        ax.set_ylabel(stat_plot_name)
        fig.suptitle(plot_title)
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
        model_plot_settings_dict = plot_specs_ts.get_model_plot_settings()
        model_idx_list = (
            stat_df.index.get_level_values(0).unique().tolist()
        )
        obs_plotted = False
        for model_idx in model_idx_list:
            model_num = model_idx.split('/')[0]
            model_num_name = model_idx.split('/')[1]
            model_num_plot_name = model_idx.split('/')[2]
            model_num_obs_name = self.model_info_dict[model_num]['obs_name']
            model_num_data = stat_df.loc[model_idx]
            if model_num_name in list(model_plot_settings_dict.keys()):
                model_num_plot_settings_dict = (
                    model_plot_settings_dict[model_num_name]
                )
            else:
                model_num_plot_settings_dict = (
                    model_plot_settings_dict[model_num]
                )
            masked_model_num_data = np.ma.masked_invalid(model_num_data)
            model_num_npts = (
                len(masked_model_num_data)
                - np.ma.count_masked(masked_model_num_data)
            )
            masked_plot_dates = np.ma.masked_where(
                np.ma.getmask(masked_model_num_data), plot_dates
            )
            if self.plot_info_dict['stat'] == 'FBAR_OBAR':
                obar_model_num_data = obar_stat_df.loc[model_idx]
                obar_masked_model_num_data = np.ma.masked_invalid(
                    obar_model_num_data
                )
                obar_model_num_npts = (
                    len(obar_masked_model_num_data)
                    - np.ma.count_masked(obar_masked_model_num_data)
                )
                obar_masked_plot_dates = np.ma.masked_where(
                    np.ma.getmask(obar_masked_model_num_data), plot_dates
                )
            if model_num_npts != 0:
                self.logger.debug(f"Plotting {model_num} - {model_num_name} "
                                  +f"- {model_num_plot_name}")
                if self.plot_info_dict['line_type'] in ['CNT', 'GRAD',
                                                        'CTS', 'NBRCTS',
                                                        'NBRCNT', 'VCNT']:
                    avg_method = 'mean'
                    calc_avg_df = model_num_data
                    if self.plot_info_dict['stat'] == 'FBAR_OBAR':
                        obar_calc_avg_df = obar_model_num_data
                else:
                    avg_method = 'aggregation'
                    calc_avg_df = all_model_df.loc[model_idx]
                    if self.plot_info_dict['stat'] == 'FBAR_OBAR':
                        obar_calc_avg_df = all_model_df.loc[model_idx]
                if self.plot_info_dict['stat'] == 'FBAR_OBAR':
                    model_num_avg = gda_util.calculate_average(
                        self.logger, avg_method,
                        self.plot_info_dict['line_type'],
                        'FBAR', calc_avg_df
                    )
                    obar_model_num_avg = gda_util.calculate_average(
                        self.logger, avg_method,
                        self.plot_info_dict['line_type'],
                        'OBAR', obar_calc_avg_df
                    )
                else:
                    model_num_avg = gda_util.calculate_average(
                        self.logger, avg_method,
                        self.plot_info_dict['line_type'],
                        self.plot_info_dict['stat'], calc_avg_df
                    )
                if np.abs(model_num_avg) >= 10:
                    model_num_avg_label = format(round(model_num_avg, 2),
                                                 '.2f')
                else:
                    model_num_avg_label = format(round(model_num_avg, 3),
                                                  '.3f')
                if self.plot_info_dict['stat'] == 'FBAR_OBAR':
                    if np.abs(obar_model_num_avg) >= 10:
                        obar_model_num_avg_label = format(
                            round(obar_model_num_avg, 2), '.2f'
                        )
                    else:
                        obar_model_num_avg_label = format(
                            round(obar_model_num_avg, 3), '.3f'
                        )
                ax.plot_date(
                    np.ma.compressed(masked_plot_dates),
                    np.ma.compressed(masked_model_num_data),
                    fmt=model_num_plot_settings_dict['marker'],
                    color = model_num_plot_settings_dict['color'],
                    linestyle = model_num_plot_settings_dict['linestyle'],
                    linewidth = model_num_plot_settings_dict['linewidth'],
                    markersize = model_num_plot_settings_dict['markersize'],
                    label = (model_num_plot_name+' '+model_num_avg_label+' '
                             +str(model_num_npts)+' days'),
                    zorder = (len(list(self.model_info_dict.keys()))
                              - model_idx_list.index(model_idx) + 4)
                )
                if masked_model_num_data.min() < stat_min \
                        or np.ma.is_masked(stat_min):
                    stat_min = masked_model_num_data.min()
                if masked_model_num_data.max() > stat_max \
                        or np.ma.is_masked(stat_max):
                    stat_max = masked_model_num_data.max()
                if self.plot_info_dict['stat'] == 'FBAR_OBAR':
                    if not obs_plotted and obar_model_num_npts != 0:
                        self.logger.debug("Plotting observation mean from "
                                          +f"{model_num} - {model_num_name} "
                                          +f"- {model_num_plot_name}")
                        obs_plot_settings_dict = (
                            model_plot_settings_dict['obs']
                        )
                        ax.plot_date(
                            np.ma.compressed(obar_masked_plot_dates),
                            np.ma.compressed(obar_masked_model_num_data),
                            fmt = obs_plot_settings_dict['marker'],
                            color = obs_plot_settings_dict['color'],
                            linestyle = obs_plot_settings_dict['linestyle'],
                            linewidth = obs_plot_settings_dict['linewidth'],
                            markersize = obs_plot_settings_dict['markersize'],
                            label = ('obs '+obar_model_num_avg_label+' '
                                     +str(obar_model_num_npts)+' days'),
                            zorder = 4
                        )
                        if obar_masked_model_num_data.min() < stat_min \
                                or np.ma.is_masked(stat_min):
                            stat_min = obar_masked_model_num_data.min()
                        if obar_masked_model_num_data.max() > stat_max \
                                or np.ma.is_masked(stat_max):
                            stat_max = obar_masked_model_num_data.max()
                        obs_plotted = True
            else:
                self.logger.debug(f"{model_num} - {model_num_name} "
                                  +f"- {model_num_plot_name} has no points")
        preset_y_axis_tick_min = ax.get_yticks()[0]
        preset_y_axis_tick_max = ax.get_yticks()[-1]
        preset_y_axis_tick_inc = ax.get_yticks()[1] - ax.get_yticks()[0]
        if self.plot_info_dict['stat'] in ['ACC']:
            y_axis_tick_inc = 0.1
        elif self.plot_info_dict['stat'] in ['FBIAS'] \
                and self.plot_info_dict['fcst_var_name'] \
                in ['SNOD_A24', 'WEASD_A24']:
            y_axis_tick_inc = 1
        else:
            y_axis_tick_inc = preset_y_axis_tick_inc
        if np.ma.is_masked(stat_min):
            y_axis_min = preset_y_axis_tick_min
        else:
            if self.plot_info_dict['stat'] in ['ACC']:
                y_axis_min = round(stat_min,1) - y_axis_tick_inc
            elif self.plot_info_dict['stat'] in ['FBIAS'] \
                    and self.plot_info_dict['fcst_var_name'] \
                    in ['SNOD_A24', 'WEASD_A24']:
                y_axis_min = 0
            else:
                y_axis_min = preset_y_axis_tick_min
                while y_axis_min > stat_min:
                    y_axis_min = y_axis_min - y_axis_tick_inc
        if np.ma.is_masked(stat_max):
            y_axis_max = preset_y_axis_tick_max
        else:
            if self.plot_info_dict['stat'] in ['ACC']:
                y_axis_max = 1
            elif self.plot_info_dict['stat'] in ['FBIAS'] \
                    and self.plot_info_dict['fcst_var_name'] \
                    in ['SNOD_A24', 'WEASD_A24']:
                y_axis_max = 10
            else:
                y_axis_max = preset_y_axis_tick_max + y_axis_tick_inc
                while y_axis_max < stat_max:
                    y_axis_max = y_axis_max + y_axis_tick_inc
        ax.set_yticks(
            np.arange(y_axis_min, y_axis_max+y_axis_tick_inc, y_axis_tick_inc)
        )
        ax.set_ylim([y_axis_min, y_axis_max])
        if len(ax.lines) != 0:
            legend = ax.legend(
                bbox_to_anchor=(plot_specs_ts.legend_bbox[0],
                                plot_specs_ts.legend_bbox[1]),
                loc = plot_specs_ts.legend_loc,
                ncol = plot_specs_ts.legend_ncol,
                fontsize = plot_specs_ts.legend_font_size
            )
            plt.draw()
            inv = ax.transData.inverted()
            legend_box = legend.get_window_extent()
            legend_box_inv = inv.transform(
                [(legend_box.x0,legend_box.y0),
                 (legend_box.x1,legend_box.y1)]
            )
            legend_box_inv_y1 = legend_box_inv[1][1]
            if stat_min < legend_box_inv_y1:
                while stat_min < legend_box_inv_y1:
                    y_axis_min = y_axis_min - y_axis_tick_inc
                    ax.set_yticks(
                        np.arange(y_axis_min,
                                  y_axis_max + y_axis_tick_inc,
                                  y_axis_tick_inc)
                    )
                    ax.set_ylim([y_axis_min, y_axis_max])
                    legend = ax.legend(
                        bbox_to_anchor=(plot_specs_ts.legend_bbox[0],
                                        plot_specs_ts.legend_bbox[1]),
                        loc = plot_specs_ts.legend_loc,
                        ncol = plot_specs_ts.legend_ncol,
                        fontsize = plot_specs_ts.legend_font_size
                    )
                    plt.draw()
                    inv = ax.transData.inverted()
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
        'forecast_hour': 'FORECAST_HOUR'
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
        'version': '11.0.2'
    }
    # Create OUTPUT_DIR
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
    p = TimeSeries(logger, INPUT_DIR, OUTPUT_DIR, MODEL_INFO_DICT,
                   DATE_INFO_DICT, PLOT_INFO_DICT, MET_INFO_DICT, LOGO_DIR)
    p.make_time_series()

if __name__ == "__main__":
    main()
