#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_performance_diagram.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script generates a performance_diagram plot.
          (x-axis: success ratio; y-axis: probability of detection; contours: csi, frequency bias)
          (EVS Graphics Naming Convention: perfdiag)
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

class PerformanceDiagram:
    """
    Make a performance_diagram graphic
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

    def make_performance_diagram(self):
        """! Make the performance_diagram graphic

             Args:

             Returns:
        """
        self.logger.info(f"Plot Type: Performance Diagram")
        self.logger.debug(f"Input directory: {self.input_dir}")
        self.logger.debug(f"Output directory: {self.output_dir}")
        self.logger.debug(f"Model information dictionary: "
                          +f"{self.model_info_dict}")
        self.logger.debug(f"Date information dictionary: "
                          +f"{self.date_info_dict}")
        self.logger.debug(f"Plot information dictionary: "
                          +f"{self.plot_info_dict}")
        # Check stat
        if self.plot_info_dict['stat'] != 'PERFDIAG':
            self.logger.error("Cannot make performance diagram for stat "
                              +f"{self.plot_info_dict['stat']}")
            sys.exit(1)
        # Set stats to calculate for diagram
        perf_diag_stat_list = ['SRATIO', 'POD', 'CSI']
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
        # Read in data
        self.logger.info(f"Reading in model stat files from {self.input_dir}")
        # Make dataframe for all thresholds
        self.logger.info("Building dataframe for all thresholds")
        fcst_units = []
        for fcst_var_thresh in self.plot_info_dict['fcst_var_threshs']:
            self.logger.debug("Building data for forecast threshold "
                              +f"{fcst_var_thresh}")
            fcst_var_thresh_idx = (self.plot_info_dict['fcst_var_threshs']\
                                   .index(fcst_var_thresh))
            obs_var_thresh = (self.plot_info_dict['obs_var_threshs']\
                              [fcst_var_thresh_idx])
            all_model_df = gda_util.build_df(
                'make_plots', self.logger, self.input_dir, self.output_dir,
                self.model_info_dict, self.met_info_dict,
                self.plot_info_dict['fcst_var_name'],
                self.plot_info_dict['fcst_var_level'],
                fcst_var_thresh,
                self.plot_info_dict['obs_var_name'],
                self.plot_info_dict['obs_var_level'],
                obs_var_thresh,
                self.plot_info_dict['line_type'],
                self.plot_info_dict['grid'],
                self.plot_info_dict['vx_mask'],
                self.plot_info_dict['interp_method'],
                self.plot_info_dict['interp_points'],
                self.date_info_dict['date_type'],
                plot_dates, format_valid_dates,
                self.date_info_dict['forecast_hour']
            )
            fcst_units.extend(
                all_model_df['FCST_UNITS'].values.astype('str').tolist()
            )
            model_idx_list = (
                all_model_df.index.get_level_values(0).unique().tolist()
            )
            if fcst_var_thresh == self.plot_info_dict['fcst_var_threshs'][0]:
                perf_diag_stat_avg_df = pd.DataFrame(
                    np.nan, pd.MultiIndex.from_product(
                        [model_idx_list,
                         perf_diag_stat_list],
                         names=['model', 'stat']
                    ),
                    columns=self.plot_info_dict['fcst_var_threshs']
                )
            # Calculate statistics mean
            for stat in perf_diag_stat_list:
                self.logger.info(f"Calculating statstic {stat} from line type "
                                 +f"{self.plot_info_dict['line_type']}")
                stat_df, stat_array = gda_util.calculate_stat(
                    self.logger, all_model_df,
                    self.plot_info_dict['line_type'], stat
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
                    model_idx_fcst_var_thresh_avg = gda_util.calculate_average(
                       self.logger, avg_method,
                       self.plot_info_dict['line_type'], stat, calc_avg_df
                    )
                    if not np.isnan(model_idx_fcst_var_thresh_avg):
                        perf_diag_stat_avg_df.loc[(model_idx,stat),
                                                  fcst_var_thresh] = (
                            model_idx_fcst_var_thresh_avg
                        )
        # Set up plot
        self.logger.info(f"Setting up plot")
        plot_specs_pd = PlotSpecs(self.logger, 'performance_diagram')
        plot_specs_pd.set_up_plot()
        csi_colors = ['#ffffff', '#f5f5f5', '#ececec', '#dfdfdf', '#cbcbcb',
                       '#b2b2b2','#8e8e8e', '#6f6f6f', '#545454', '#3f3f3f']
        cmap_csi = matplotlib.colors.ListedColormap(csi_colors)
        pd_ticks = np.arange(0.001, 1.001, 0.001)
        pd_sr, pd_pod = np.meshgrid(pd_ticks, pd_ticks)
        pd_bias = pd_pod / pd_sr
        pd_csi = 1.0 / (1.0 / pd_sr + 1.0 / pd_pod - 1.0)
        pd_bias_clevs = [0.1, 0.2, 0.4, 0.6, 0.8, 1.,
                         1.2, 1.5, 2., 3., 5., 10.]
        stat_plot_name = plot_specs_pd.get_stat_plot_name(
             self.plot_info_dict['stat']
        )
        POD_plot_name = plot_specs_pd.get_stat_plot_name('POD')
        SRATIO_plot_name = plot_specs_pd.get_stat_plot_name('SRATIO')
        CSI_plot_name = plot_specs_pd.get_stat_plot_name('CSI')
        fcst_units = np.unique(fcst_units)
        fcst_units = np.delete(fcst_units, np.where(fcst_units == 'nan'))
        if len(fcst_units) > 1:
            self.logger.error(f"Have multilple units: {', '.join(fcst_units)}")
            sys.exit(1)
        elif len(fcst_units) == 0:
            self.logger.debug("Cannot get variables units, leaving blank")
            fcst_units = ['']
        plot_title = plot_specs_pd.get_plot_title(
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
                plot_specs_pd.get_logo_location(
                    'left', plot_specs_pd.fig_size[0],
                    plot_specs_pd.fig_size[1], plt.rcParams['figure.dpi']
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
                plot_specs_pd.get_logo_location(
                    'right', plot_specs_pd.fig_size[0],
                    plot_specs_pd.fig_size[1], plt.rcParams['figure.dpi']
                )
            )
        else:
            plot_right_logo = False
            self.logger.debug(f"{plot_right_logo_path} does not exist")
        image_name = plot_specs_pd.get_savefig_name(
            self.output_dir, self.plot_info_dict, self.date_info_dict
        )
        # Make plot
        self.logger.info(f"Making plot")
        fig, ax = plt.subplots(1,1, figsize=(plot_specs_pd.fig_size[0],
                                             plot_specs_pd.fig_size[1]))
        fig.suptitle(plot_title)
        ax.grid(False)
        ax.set_xlabel(SRATIO_plot_name)
        ax.set_xlim([0,1])
        ax.set_xticks(np.arange(0,1.1,0.1))
        ax.set_ylabel(POD_plot_name)
        ax.set_ylim([0,1])
        ax.set_yticks(np.arange(0,1.1,0.1))
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
        CBIAS = plt.contour(pd_sr, pd_pod, pd_bias, pd_bias_clevs,
                            colors='gray', linestyles='dashed')
        radius = 0.75
        CBIAS_label_loc = []
        for bias_val in pd_bias_clevs:
            x = np.sqrt(np.power(radius, 2)/(np.power(bias_val, 2)+1))
            y = np.sqrt(np.power(radius, 2) - np.power(x, 2))
            CBIAS_label_loc.append((x,y))
        plt.clabel(CBIAS, fmt='%1.1f', manual=CBIAS_label_loc)
        CFCSI = plt.contourf(pd_sr, pd_pod, pd_csi,
                             np.arange(0., 1.1, 0.1), cmap=cmap_csi,
                             extend='neither')
        cbar_left = ax.get_position().x1 + 0.05
        cbar_bottom = ax.get_position().y0
        cbar_width = 0.01
        cbar_height = ax.get_position().y1 - ax.get_position().y0
        cbar_ax = fig.add_axes(
            [cbar_left, cbar_bottom, cbar_width, cbar_height]
        )
        cbar = plt.colorbar(CFCSI, orientation='vertical', cax=cbar_ax,
                            ticks=CFCSI.levels)
        #cbar.dividers.set_color('black')
        #cbar.dividers.set_linewidth(2)
        cbar.set_label(CSI_plot_name)
        f = lambda m,c,ls,lw,ms,mec: plt.plot(
            [], [], marker=m, mec=mec, mew=2.,
            c=c, ls=ls, lw=lw, ms=ms)[0]
        thresh_marker_plot_settings_dict = (
            plot_specs_pd.get_marker_plot_settings()
        )
        if len(self.plot_info_dict['fcst_var_threshs']) > \
                len(list(thresh_marker_plot_settings_dict.keys())):
          self.logger.error("Requested number of thresholds ("
                            +f"{len(self.plot_info_dict['fcst_var_threshs'])} "
                            +", "
                            +','.join(self.plot_info_dict['fcst_var_threshs'])
                            +") exceeds the preset marking settings, "
                            +"reduce number of thresholds to <= "
                            +f"{len(list(thresh_marker_plot_settings_dict.keys()))}")
          sys.exit(1)
        thresh_legend_handles = []
        thresh_mark_dict = {}
        for fcst_var_thresh in self.plot_info_dict['fcst_var_threshs']:
            fcst_var_thresh_num = (
                self.plot_info_dict['fcst_var_threshs'].index(fcst_var_thresh)
                + 1
            )
            if fcst_var_thresh in list(thresh_marker_plot_settings_dict.keys()):
                fcst_var_thresh_marker_dict = (
                    thresh_marker_plot_settings_dict[fcst_var_thresh]
                )
            else:
                fcst_var_thresh_marker_dict = (
                    thresh_marker_plot_settings_dict\
                    ['marker'+str(fcst_var_thresh_num)]
                )
            thresh_legend_handles.append(
                f(fcst_var_thresh_marker_dict['marker'],
                  'white', 'solid', 0,
                  fcst_var_thresh_marker_dict['markersize'],
                  'black')
            )
            thresh_mark_dict[fcst_var_thresh] = fcst_var_thresh_marker_dict
        thresh_legend_labels = [
            f'{t} {fcst_units[0]}'
            for t in self.plot_info_dict['fcst_var_threshs']
        ]
        thresh_legend = ax.legend(
            thresh_legend_handles, thresh_legend_labels,
            bbox_to_anchor=(0.5, -0.075),
            loc = 'upper center',
            ncol = plot_specs_pd.legend_ncol,
            fontsize = plot_specs_pd.legend_font_size
        )
        plt.draw()
        ax.add_artist(thresh_legend)
        model_legend_handles = []
        model_legend_labels = []
        model_plot_settings_dict = plot_specs_pd.get_model_plot_settings()
        for model_idx in model_idx_list:
            model_num = model_idx.split('/')[0]
            model_num_name = model_idx.split('/')[1]
            model_num_plot_name = model_idx.split('/')[2]
            model_num_obs_name = self.model_info_dict[model_num]['obs_name']
            model_num_data = perf_diag_stat_avg_df.loc[model_idx]
            if model_num_name in list(model_plot_settings_dict.keys()):
                model_num_plot_settings_dict = (
                    model_plot_settings_dict[model_num_name]
                )
            else:
                model_num_plot_settings_dict = (
                    model_plot_settings_dict[model_num]
                )
            model_num_SRATIO = model_num_data.loc['SRATIO']
            masked_model_num_SRATIO = np.ma.masked_invalid(model_num_SRATIO)
            model_num_npts_SRATIO = (
                len(masked_model_num_SRATIO)
                - np.ma.count_masked(masked_model_num_SRATIO)
            )
            model_num_POD = model_num_data.loc['POD']
            masked_model_num_POD = np.ma.masked_invalid(model_num_POD)
            model_num_npts_POD = (
                len(masked_model_num_POD)
                - np.ma.count_masked(masked_model_num_POD)
            )
            self.logger.debug(f"Plotting {model_num} [{model_num_name},"
                              +f"{model_num_plot_name}]")
            if model_num_npts_SRATIO != 0 and model_num_npts_POD != 0:
                ax.plot(
                    masked_model_num_SRATIO, masked_model_num_POD,
                    color = model_num_plot_settings_dict['color'],
                    linestyle = model_num_plot_settings_dict['linestyle'],
                    linewidth = 2*model_num_plot_settings_dict['linewidth'],
                    marker = 'None',
                    markersize = 0,
                    zorder = (len(list(self.model_info_dict.keys()))
                              - model_idx_list.index(model_idx) + 4)
                )
                model_legend_labels.append(model_num_plot_name)
                model_legend_handles.append(
                    f('',
                      model_num_plot_settings_dict['color'],
                      model_num_plot_settings_dict['linestyle'],
                      8, 0, 'white')
                )
                for fcst_var_thresh in self.plot_info_dict['fcst_var_threshs']:
                    ax.scatter(
                        model_num_SRATIO[fcst_var_thresh],
                        model_num_POD[fcst_var_thresh],
                        c = model_num_plot_settings_dict['color'],
                        linewidth = 2,
                        edgecolors='white',
                        marker = thresh_mark_dict[fcst_var_thresh]['marker'],
                        s = thresh_mark_dict[fcst_var_thresh]['markersize']**2,
                        zorder=40
                    )
            else:
                self.logger.debug(f"{model_num} [{model_num_name},"
                                  +f"{model_num_plot_name}] has no points")
        inv = ax.transData.inverted()
        legend_box = thresh_legend.get_frame().get_bbox()
        legend_box_inv = inv.transform([(legend_box.x0,legend_box.y0),
                                        (legend_box.x1,legend_box.y1)])
        model_legend = ax.legend(
            model_legend_handles, model_legend_labels,
            bbox_to_anchor=(0.5, legend_box_inv[0][1]*1.1),
            loc = 'upper center',
            ncol = plot_specs_pd.legend_ncol,
            fontsize = plot_specs_pd.legend_font_size
        )
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
        'fcst_var_threshs': ['FCST_VAR_THRESHS'],
        'obs_var_name': 'OBS_VAR_NAME',
        'obs_var_level': 'OBS_VAR_LEVEL',
        'obs_var_threshs': ['OBS_VAR_THRESHS'],
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
    p = PerformanceDiagram(logger, INPUT_DIR, OUTPUT_DIR, MODEL_INFO_DICT,
                           DATE_INFO_DICT, PLOT_INFO_DICT, MET_INFO_DICT,
                           LOGO_DIR)
    p.make_performance_diagram()

if __name__ == "__main__":
    main()
