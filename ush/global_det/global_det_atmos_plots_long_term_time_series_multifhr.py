'''
Name: global_det_atmos_plots_long_term_time_series_multifhr.py
Contact(s): Mallory Row
Abstract: This script generates the plots for long term
          time series for 1 model with multiple forecast hours
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
import matplotlib.gridspec as gridspec
from global_det_atmos_plots_specs import PlotSpecs

class LongTermTimeSeriesMultiFhr:
    """
    Create long term time series multiple forecast hour graphic
    """

    def __init__(self, logger, input_dir, output_dir, logo_dir,
                 time_range, date_dt_list, model_group, model_list,
                 var_name, var_level, var_thresh, vx_mask, stat,
                 forecast_day_list, run_length_list):
        """! Initalize LongTermTimeSeriesMultiFhr class
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
                 vx_mask            - verification mask name (string)
                 stat               - statistic name (string)
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
        self.vx_mask = vx_mask
        self.stat = stat
        self.forecast_day_list = forecast_day_list
        self.run_length_list = run_length_list

    def make_long_term_time_series_multifhr(self):
        """! Create the long term time series multiple
             forecast hours graphic
             Args:
             Returns:
        """
        self.logger.info(f"Creating long term time series...")
        self.logger.debug(f"Input directory: {self.input_dir}")
        self.logger.debug(f"Output directory: {self.output_dir}")
        self.logger.debug(f"Logo directory: {self.logo_dir}")
        self.logger.debug(f"Time Range: {self.time_range}")
        if self.time_range not in ['monthly', 'yearly']:
            self.logger.error("CAN ONLY RUN TIME SERIES FOR "
                              +"TIME RANGE VALUES OF monthly OR yearly")
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
        self.logger.debug("Forecast Days: "
                          +f"{', '.join(self.forecast_day_list)}")
        self.logger.debug(f"Run Lengths: {', '.join(self.run_length_list)}")
        # Check only requested 1 model
        if len(self.model_list) != 1:
            self.logger.warning(
                f"Requested {str(len(self.model_list))} "
                +"models to plot, but multiple forecast hour time series can "
                +"only display 1 model, using first model"
            )
            self.model_list = self.model_list[0]
        # Check forecast hours
        if len(self.forecast_day_list) > 4:
            self.logger.warning(
                f"Requested {len(self.forecast_day_list)} "
                +"forecast days to plot, maximum is 4, plotting first 4"
            )
            self.forecast_day_list = self.forecast_day_list[:4]
        # Make job image directory
        output_image_dir = os.path.join(self.output_dir, 'images')
        if not os.path.exists(output_image_dir):
            os.makedirs(output_image_dir)
        self.logger.info(f"Plots will be in: {output_image_dir}")
        # Create merged dataset of verification systems
        if self.var_name == 'APCP':
            model_group_merged_df = (
                gda_util.merge_precip_long_term_stats_datasets(
                    self.logger, self.input_dir, self.time_range,
                    self.date_dt_list, self.model_group, self.model_list,
                    self.var_name, self.var_level, self.var_thresh,
                    self.vx_mask, self.stat
                )
            )
        else:
            model_group_merged_df = (
                gda_util.merge_grid2grid_long_term_stats_datasets(
                    self.logger, self.input_dir, self.time_range,
                    self.date_dt_list, self.model_group, self.model_list,
                    self.var_name, self.var_level, self.var_thresh,
                    self.vx_mask, self.stat 
                )
            )
        # Create plots
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
        elif self.var_name == 'APCP':
            model_hour = 'valid 12Z'
        else:
            model_hour = 'valid 00Z'
        plot_left_logo = False
        plot_left_logo_path = os.path.join(self.logo_dir, 'noaa.png')
        if os.path.exists(plot_left_logo_path):
            plot_left_logo = True
            left_logo_img_array = matplotlib.image.imread(plot_left_logo_path)
        plot_right_logo = False
        plot_right_logo_path = os.path.join(self.logo_dir, 'nws.png')
        if os.path.exists(plot_right_logo_path):
            plot_right_logo = True
            right_logo_img_array = matplotlib.image.imread(plot_right_logo_path)
        for run_length in self.run_length_list:
            if run_length == 'allyears':
                run_length_date_list = date_list
                run_length_date_dt_list = self.date_dt_list
                run_length_model_group_merged_df = model_group_merged_df
            elif run_length == 'past10years':
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
            self.logger.info(f"Working on plots for {run_length}: "
                             +f"{run_length_date_list[0]}-"
                             +f"{run_length_date_list[-1]}")
            # Make time series plots with all forecast days
            plot_specs_lttsmf = PlotSpecs(self.logger,
                                         'long_term_time_series_multifhr')
            plot_specs_lttsmf.set_up_plot()
            left_logo_xpixel_loc, left_logo_ypixel_loc, left_logo_alpha = (
                plot_specs_lttsmf.get_logo_location(
                    'left', plot_specs_lttsmf.fig_size[0],
                    plot_specs_lttsmf.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
            right_logo_xpixel_loc, right_logo_ypixel_loc, right_logo_alpha = (
                plot_specs_lttsmf.get_logo_location(
                    'right', plot_specs_lttsmf.fig_size[0],
                     plot_specs_lttsmf.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
            all_forecast_hour_plot_settings_dict = (
                plot_specs_lttsmf.get_forecast_hour_plot_settings()
            )
            #fss_width13_ge0p1.
            image_name = os.path.join(
                output_image_dir,
                f"evs.global_det.{self.model_list[0]}.{self.stat}.".lower()
                +f"{self.var_name}_{self.var_level}.{run_length}_".lower()
                +f"{self.time_range}.timeseries_".lower()
                +f"{model_hour.replace(' ', '').replace(',','')}_".lower()
                +''.join(["f"+str(int(d)*24).zfill(3)
                          for d in self.forecast_day_list]).lower()
                +f".g004_{self.vx_mask}.png".lower()
            )
            print(image_name)
def main():
    # Need settings
    INPUT_DIR = os.environ['HOME']
    OUTPUT_DIR = os.environ['HOME']
    LOGO_DIR = os.environ['HOME']
    TIME_RANGE = 'TIME_RANGE'
    DATE_DT_LIST = []
    MODEL_GROUP = 'MODEL_GROUP'
    MODEL_LIST = ['MODELA']
    VAR_NAME = 'VAR_NAME'
    VAR_LEVEL = 'VAR_LEVEL'
    VAR_THRESH = 'VAR_THRESH'
    VX_MASK = 'VX_MASK'
    STAT = 'STAT'
    FORECAST_DAY_LIST = ['1', '2']
    RUN_LENGTH_LIST = ['allyears', 'past10years'] 
    # Create OUTPUT_DIR
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    # Set up logging
    logging_dir = os.path.join(OUTPUT_DIR, 'logs')
    if not os.path.exists(logging_dir):
         os.makedirs(logging_dir)
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
    p = LongTermTimeSeriesMultiFhr(logger, INPUT_DIR, OUTPUT_DIR, LOGO_DIR,
                                   TIME_RANGE, DATE_DT_LIST, MODEL_GROUP,
                                   MODEL_LIST, VAR_NAME, VAR_LEVEL, VAR_THRESH,
                                   VX_MASK, STAT, FORECAST_DAY_LIST,
                                   RUN_LENGTH_LIST)
    p.make_long_term_time_series_multifhr()

if __name__ == "__main__":
    main()
