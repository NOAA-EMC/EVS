#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_time_series_multifhr.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script generates a time series plot with
          multiple forecast hours for 1 model.
          (x-axis: dates; y-axis: statistics value)
          (EVS Graphics Naming Convention: timeseries)
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

class TimeSeriesMultiFhr:
    """
    Make a time series multiple forecast hour graphic
    """

    def __init__(self, logger, input_dir, output_dir, model_info_dict,
                 date_info_dict, plot_info_dict, met_info_dict, logo_dir):
        """! Initalize TimeSeriesMultiFhr class

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

    def make_time_series_multifhr(self):
        """! Make the time series multiple foreast hours graphic

             Args:

             Returns:
        """
        self.logger.info(f"Plot Type: Time Series (Multiple Forecast Hours)")
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
            self.logger.error("Cannot make time_series_multifhr for stat "
                               +f"{self.plot_info_dict['stat']}")
            sys.exit(1)
        # Check only requested 1 model
        if len(list(self.model_info_dict.keys())) != 1:
            self.logger.warning(
                f"Requested {str(len(list(self.model_info_dict.keys())))} "
                +"models to plot, but multiple forecast hour time series can "
                +"only display 1 model, using first model"
            )
            self.model_info_dict = self.model_info_dict[
                list(self.model_info_dict.keys())[0]
            ]
        # Check forecast hours
        if len(self.date_info_dict['forecast_hours']) > 4:
            self.logger.warning(
                f"Requested {len(self.date_info_dict['forecast_hours'])} "
                +"forecast hours to plot, maximum is 4, plotting first 4"
            )
            self.date_info_dict['forecast_hours'] = (
                self.date_info_dict['forecast_hours'][:4]
            )
        # Make dataframe for all forecast hours
        self.logger.info("Building dataframe for all forecast hours")
        fcst_units = []
        for forecast_hour in self.date_info_dict['forecast_hours']:
            self.logger.debug("Building data for forecast hour "
                              +f"{forecast_hour}")
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
                self.logger.debug("Based on date information, "
                                  "plot will display valid dates "
                                  +', '.join(format_valid_dates)+" "
                                  +f"for forecast hour {forecast_hour} "
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
                self.logger.debug("Based on date information, "
                                  +"plot will display initialization dates "
                                  +', '.join(format_init_dates)+" "
                                  +f"for forecast hour {forecast_hour} "
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
                forecast_hour
            )
            fcst_units.extend(
                all_model_df['FCST_UNITS'].values.astype('str').tolist()
            )
            # Calculate statistic
            self.logger.info(f"Calculating statstic {self.plot_info_dict['stat']} "
                             +f"from line type {self.plot_info_dict['line_type']}")
            forecast_hour_stat_df, forecast_hour_stat_array = gda_util.calculate_stat(
                self.logger, all_model_df, self.plot_info_dict['line_type'],
                self.plot_info_dict['stat']
            )
            if forecast_hour == self.date_info_dict['forecast_hours'][0]:
                all_forecast_hour_stat_df = pd.DataFrame(
                    index=forecast_hour_stat_df.index,
                    columns=[self.date_info_dict['forecast_hours']]
                )
                all_forecast_hour_stat_avg_df = pd.DataFrame(
                    index=(forecast_hour_stat_df.index.get_level_values(0)\
                           .unique().tolist()),
                    columns=[self.date_info_dict['forecast_hours']]
                )
            all_forecast_hour_stat_df[forecast_hour] = (
                forecast_hour_stat_array[0]
            )
            if self.plot_info_dict['line_type'] in ['CNT', 'GRAD',
                                                    'CTS', 'NBRCTS',
                                                    'NBRCNT', 'VCNT']:
                avg_method = 'mean'
                calc_avg_df = all_forecast_hour_stat_df[forecast_hour]
            else:
                avg_method = 'aggregation'
                calc_avg_df = all_model_df.loc[
                    forecast_hour_stat_df.index.get_level_values(0)\
                    .unique().tolist()[0]
                  ]
            forecast_hour_avg = gda_util.calculate_average(
                self.logger, avg_method,
                self.plot_info_dict['line_type'],
                self.plot_info_dict['stat'], calc_avg_df
            )
            all_forecast_hour_stat_avg_df[forecast_hour] = (
                forecast_hour_avg
            )
        shape = [len(list(self.model_info_dict.keys())),
                 len(self.date_info_dict['forecast_hours'])]
        all_forecast_hour_stat_array = (
            all_forecast_hour_stat_df.to_numpy()
        )
        # Set up plot
        self.logger.info(f"Setting up plot")
        plot_specs_tsmf = PlotSpecs(self.logger, 'time_series_multifhr')
        plot_specs_tsmf.set_up_plot()
        n_xticks = 5
        if len(plot_dates) < n_xticks:
            xtick_intvl = 1
        else:
            xtick_intvl = int(len(plot_dates)/n_xticks)
        date_intvl = int((plot_dates[1]-plot_dates[0]).total_seconds())
        stat_min = np.ma.masked_invalid(all_forecast_hour_stat_array).min()
        stat_max = np.ma.masked_invalid(all_forecast_hour_stat_array).max()
        stat_plot_name = plot_specs_tsmf.get_stat_plot_name(
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
        plot_title = plot_specs_tsmf.get_plot_title(
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
                plot_specs_tsmf.get_logo_location(
                    'left', plot_specs_tsmf.fig_size[0],
                    plot_specs_tsmf.fig_size[1], plt.rcParams['figure.dpi']
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
                plot_specs_tsmf.get_logo_location(
                    'right', plot_specs_tsmf.fig_size[0],
                    plot_specs_tsmf.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
        else:
            plot_right_logo = False
            self.logger.debug(f"{plot_right_logo_path} does not exist")
        all_forecast_hour_plot_settings_dict = (
            plot_specs_tsmf.get_forecast_hour_plot_settings()
        )
        image_name = plot_specs_tsmf.get_savefig_name(
            self.output_dir, self.plot_info_dict, self.date_info_dict
        )
        image_name = image_name.replace(
            'evs.global_det.',
            'evs.global_det.'+self.model_info_dict['model1']['name'].lower()
            +'.'
        )
        # Make plot
        self.logger.info(f"Making plot")
        fig, ax = plt.subplots(1,1,figsize=(plot_specs_tsmf.fig_size[0],
                                            plot_specs_tsmf.fig_size[1]))
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
        fig.suptitle(f"{self.model_info_dict['model1']['name'].upper()} "
                     +f"{plot_title}")
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
        for forecast_hour in self.date_info_dict['forecast_hours']:
            forecast_hour_idx = self.date_info_dict['forecast_hours'].index(
                forecast_hour
            )
            forecast_hour_data = (all_forecast_hour_stat_df[forecast_hour]\
                                  .to_numpy())[:,0]
            forecast_hour_avg = (all_forecast_hour_stat_avg_df[forecast_hour]\
                                 .to_numpy())[0,0]
            if f"fhr{forecast_hour.zfill(3)}" \
                    in list(all_forecast_hour_plot_settings_dict.keys()):
                forecast_hour_plot_settings_dict = (
                    all_forecast_hour_plot_settings_dict[
                        f"fhr{forecast_hour.zfill(3)}"
                    ]
                )
            else:
                forecast_hour_plot_settings_dict = (
                    all_forecast_hour_plot_settings_dict[
                        f"fhr_n{str(forecast_hour_idx+1)}"
                    ]
                )
            masked_forecast_hour_data = np.ma.masked_invalid(
                forecast_hour_data
            )
            forecast_hour_npts = (
                len(masked_forecast_hour_data)
                - np.ma.count_masked(masked_forecast_hour_data)
            )
            masked_plot_dates = np.ma.masked_where(
                np.ma.getmask(masked_forecast_hour_data), plot_dates
            )
            self.logger.debug(f"Plotting {forecast_hour}")
            if forecast_hour_npts != 0:
                if np.abs(forecast_hour_avg) >= 10:
                    forecast_hour_avg_label = format(
                        round(forecast_hour_avg, 2), '.2f'
                    )
                else:
                    forecast_hour_avg_label = format(
                        round(forecast_hour_avg, 3), '.3f'
                    )
                ax.plot_date(
                    np.ma.compressed(masked_plot_dates),
                    np.ma.compressed(masked_forecast_hour_data),
                    fmt = forecast_hour_plot_settings_dict['marker'],
                    color = forecast_hour_plot_settings_dict['color'],
                    linestyle = forecast_hour_plot_settings_dict['linestyle'],
                    linewidth = forecast_hour_plot_settings_dict['linewidth'],
                    markersize = forecast_hour_plot_settings_dict['markersize'],
                    label = (f"Day {str(int(int(forecast_hour)/24))}"+' '
                             +forecast_hour_avg_label+' '
                             +str(forecast_hour_npts)+' days'),
                    zorder = (len(self.date_info_dict['forecast_hours'])
                              - self.date_info_dict['forecast_hours']\
                              .index(forecast_hour) + 4)
                )
            else:
                self.logger.debug(f"{forecast_hour} has no points")
        preset_y_axis_tick_min = ax.get_yticks()[0]
        preset_y_axis_tick_max = ax.get_yticks()[-1]
        preset_y_axis_tick_inc = ax.get_yticks()[1] - ax.get_yticks()[0]
        if self.plot_info_dict['stat'] in ['ACC']:
            y_axis_tick_inc = 0.1
        else:
            y_axis_tick_inc = preset_y_axis_tick_inc
        if np.ma.is_masked(stat_min):
            y_axis_min = preset_y_axis_tick_min
        else:
            if self.plot_info_dict['stat'] in ['ACC']:
                y_axis_min = round(stat_min,1) - y_axis_tick_inc
            else:
                y_axis_min = preset_y_axis_tick_min
                while y_axis_min > stat_min:
                    y_axis_min = y_axis_min - y_axis_tick_inc
        if np.ma.is_masked(stat_max):
            y_axis_max = preset_y_axis_tick_max
        else:
            if self.plot_info_dict['stat'] in ['ACC']:
                y_axis_max = 1
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
                bbox_to_anchor=(plot_specs_tsmf.legend_bbox[0],
                                plot_specs_tsmf.legend_bbox[1]),
                loc = plot_specs_tsmf.legend_loc,
                ncol = plot_specs_tsmf.legend_ncol,
                fontsize = plot_specs_tsmf.legend_font_size
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
                        bbox_to_anchor=(plot_specs_tsmf.legend_bbox[0],
                                        plot_specs_tsmf.legend_bbox[1]),
                        loc = plot_specs_tsmf.legend_loc,
                        ncol = plot_specs_tsmf.legend_ncol,
                        fontsize = plot_specs_tsmf.legend_font_size
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
        'forecast_hours': ['FORECAST_HOUR']
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
    p = TimeSeriesMultiFhr(logger, INPUT_DIR, OUTPUT_DIR, MODEL_INFO_DICT,
                           DATE_INFO_DICT, PLOT_INFO_DICT, MET_INFO_DICT,
                           LOGO_DIR)
    p.make_time_series_multifhr()

if __name__ == "__main__":
    main()
