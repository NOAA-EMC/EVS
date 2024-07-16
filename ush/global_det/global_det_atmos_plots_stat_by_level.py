#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_stat_by_level.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script generates a stat by level plot.
          (x-axis: statistics value; y-axis: pressure levels)
          (EVS Graphics Naming Convention: vertprof)
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

class StatByLevel:
    """
    Make a stat by level graphic
    """

    def __init__(self, logger, input_dir, output_dir, model_info_dict,
                 date_info_dict, plot_info_dict, met_info_dict, logo_dir):
        """! Initalize StatByLevel class

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

    def make_stat_by_level(self):
        """! Make the stat by level graphic

             Args:

             Returns:
        """
        self.logger.info(f"Plot Type: Stat By Level")
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
            self.logger.error("Cannot make stat_by_level for stat "
                              +f"{self.plot_info_dict['stat']}")
            sys.exit(1)
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
            plot_dates = valid_dates
        elif self.date_info_dict['date_type'] == 'INIT':
            self.logger.debug("Based on date information, plot will display "
                              +"initialization dates "
                              +', '.join(format_init_dates)+" "
                              +"for forecast hour "
                              +f"{self.date_info_dict['forecast_hour']} "
                              +"with valid dates "
                              +', '.join(format_valid_dates))
            plot_dates = init_dates
        plot_specs_sbl = PlotSpecs(self.logger, 'stat_by_level')
        self.logger.info(f"Gathering data for {self.plot_info_dict['stat']} "
                         +"- vertical profile "
                         +f"{self.plot_info_dict['vert_profile']}")
        vert_profile_levels = plot_specs_sbl.get_vert_profile_levels(
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
        for level in vert_profile_levels:
            self.logger.debug(f"Building data for level {level}")
            vert_profile_levels_int[vert_profile_levels.index(level)] = (
                level[1:]
            )
            # Read in data
            level_input_dir = os.path.join(
                self.input_dir, '..', '..',
                f"{self.plot_info_dict['fcst_var_name'].lower()}_"
                +f"{level.lower()}",
                (self.plot_info_dict['vx_mask'].lower()\
                 .replace('global', 'glb').replace('conus', 'buk_conus'))
            )
            self.logger.info("Reading in model stat files "
                             +f"from {level_input_dir}")
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
                str(self.date_info_dict['forecast_hour'])
            )
            fcst_units.extend(
                all_model_df['FCST_UNITS'].values.astype('str').tolist()
            )
            # Calculate statistic
            self.logger.info("Calculating statstic "
                             +f"{self.plot_info_dict['stat']} "
                             +"from line type "
                             +f"{self.plot_info_dict['line_type']}")
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
            if level == vert_profile_levels[0]:
                stat_vert_profile_df = pd.DataFrame(
                    np.nan, model_idx_list,
                    columns=vert_profile_levels
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
                    self.logger, avg_method,
                    self.plot_info_dict['line_type'],
                    self.plot_info_dict['stat'], calc_avg_df
                )
                if not np.isnan(model_idx_forecast_hour_avg):
                    stat_vert_profile_df.loc[model_idx, level] = (
                        model_idx_forecast_hour_avg
                    )
        # Set up plot
        self.logger.info(f"Setting up plot")
        plot_specs_sbl.set_up_plot()
        stat_min = np.ma.masked_invalid(np.nan)
        stat_max = np.ma.masked_invalid(np.nan)
        stat_plot_name = plot_specs_sbl.get_stat_plot_name(
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
        plot_title = plot_specs_sbl.get_plot_title(
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
                plot_specs_sbl.get_logo_location(
                    'left', plot_specs_sbl.fig_size[0],
                    plot_specs_sbl.fig_size[1], plt.rcParams['figure.dpi']
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
                plot_specs_sbl.get_logo_location(
                    'right', plot_specs_sbl.fig_size[0],
                    plot_specs_sbl.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
        else:
            plot_right_logo = False
            self.logger.debug(f"{plot_right_logo_path} does not exist")
        image_name = plot_specs_sbl.get_savefig_name(
            self.output_dir, self.plot_info_dict, self.date_info_dict
        )
        # Make plot
        self.logger.info(f"Making plot")
        fig, ax = plt.subplots(1,1,figsize=(plot_specs_sbl.fig_size[0],
                                            plot_specs_sbl.fig_size[1]))
        ax.grid(True)
        ax.set_xlabel(stat_plot_name)
        ax.set_ylabel('Pressure Level (hPa)')
        ax.set_yscale('log')
        ax.minorticks_off()
        ax.set_yticks(vert_profile_levels_int)
        ax.set_yticklabels(vert_profile_levels_int)
        ax.set_ylim([vert_profile_levels_int[0],
                     vert_profile_levels_int[-1]])
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
        model_plot_settings_dict = plot_specs_sbl.get_model_plot_settings()
        for model_idx in model_idx_list:
            model_num = model_idx.split('/')[0]
            model_num_name = model_idx.split('/')[1]
            model_num_plot_name = model_idx.split('/')[2]
            model_num_obs_name = self.model_info_dict[model_num]['obs_name']
            model_num_data = stat_vert_profile_df.loc[model_idx]
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
            masked_vert_profile_levels_int = np.ma.masked_where(
                np.ma.getmask(masked_model_num_data),
                vert_profile_levels_int
            )
            if model_num_npts != 0:
                self.logger.debug(f"Plotting {model_num} [{model_num_name},"
                                  +f"{model_num_plot_name}]")
                ax.plot(
                    np.ma.compressed(masked_model_num_data),
                    np.ma.compressed(masked_vert_profile_levels_int),
                    color = model_num_plot_settings_dict['color'],
                    linestyle = model_num_plot_settings_dict['linestyle'],
                    linewidth = model_num_plot_settings_dict['linewidth'],
                    marker = model_num_plot_settings_dict['marker'],
                    markersize = model_num_plot_settings_dict['markersize'],
                    label = model_num_plot_name,
                    zorder = (len(list(self.model_info_dict.keys()))
                              - model_idx_list.index(model_idx) + 4)
                )
                if masked_model_num_data.min() < stat_min \
                        or np.ma.is_masked(stat_min):
                    stat_min = masked_model_num_data.min()
                if masked_model_num_data.max() > stat_max \
                        or np.ma.is_masked(stat_max):
                    stat_max = masked_model_num_data.max()
            else:
                self.logger.debug(f"{model_num} [{model_num_name},"
                                  +f"{model_num_plot_name}] has no points")
        preset_x_axis_tick_min = ax.get_xticks()[0]
        preset_x_axis_tick_max = ax.get_xticks()[-1]
        preset_x_axis_tick_inc = ax.get_xticks()[1] - ax.get_xticks()[0]
        if self.plot_info_dict['stat'] in ['ACC']:
            x_axis_tick_inc = 0.1
        else:
            x_axis_tick_inc = preset_x_axis_tick_inc
        if np.ma.is_masked(stat_min):
            x_axis_min = preset_x_axis_tick_min
        else:
            if self.plot_info_dict['stat'] in ['ACC']:
                x_axis_min = round(stat_min,1) - x_axis_tick_inc
            else:
                x_axis_min = preset_x_axis_tick_min
                while x_axis_min > stat_min:
                    x_axis_min = x_axis_min - x_axis_tick_inc
        if np.ma.is_masked(stat_max):
            x_axis_max = preset_x_axis_tick_max
        else:
            if self.plot_info_dict['stat'] in ['ACC']:
                x_axis_max = 1
            else:
                x_axis_max = preset_x_axis_tick_max + x_axis_tick_inc
                while x_axis_max < stat_max:
                    x_axis_max = x_axis_max + x_axis_tick_inc
        ax.set_xticks(
            np.arange(x_axis_min, x_axis_max+x_axis_tick_inc,
                      x_axis_tick_inc)
        )
        ax.set_xlim([x_axis_min, x_axis_max])
        if len(ax.lines) != 0:
            legend = ax.legend(
                bbox_to_anchor=(plot_specs_sbl.legend_bbox[0],
                                plot_specs_sbl.legend_bbox[1]),
                loc = plot_specs_sbl.legend_loc,
                ncol = plot_specs_sbl.legend_ncol,
                fontsize = plot_specs_sbl.legend_font_size
            )
            plt.draw()
            inv = ax.transData.inverted()
            legend_box = legend.get_window_extent()
            legend_box_inv = inv.transform(
                [(legend_box.x0,legend_box.y0),
                 (legend_box.x1,legend_box.y1)]
            )
            legend_box_inv_x1 = legend_box_inv[1][0]
            if stat_min < legend_box_inv_x1:
                while stat_min < legend_box_inv_x1:
                    x_axis_min = x_axis_min - x_axis_tick_inc
                    ax.set_xticks(
                        np.arange(x_axis_min,
                                  x_axis_max + x_axis_tick_inc,
                                  x_axis_tick_inc)
                    )
                    ax.set_xlim([x_axis_min, x_axis_max])
                    legend = ax.legend(
                        bbox_to_anchor=(plot_specs_sbl.legend_bbox[0],
                                        plot_specs_sbl.legend_bbox[1]),
                        loc = plot_specs_sbl.legend_loc,
                        ncol = plot_specs_sbl.legend_ncol,
                        fontsize = plot_specs_sbl.legend_font_size
                    )
                    plt.draw()
                    inv = ax.transData.inverted()
                    legend_box = legend.get_window_extent()
                    legend_box_inv = inv.transform(
                         [(legend_box.x0,legend_box.y0),
                          (legend_box.x1,legend_box.y1)]
                    )
                    legend_box_inv_x1 = legend_box_inv[1][0]
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
    p = StatByLevel(logger, INPUT_DIR, OUTPUT_DIR, MODEL_INFO_DICT,
                    DATE_INFO_DICT, PLOT_INFO_DICT, MET_INFO_DICT, LOGO_DIR)
    p.make_stat_by_level()

if __name__ == "__main__":
    main()
