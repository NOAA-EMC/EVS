#!/usr/bin/env python3
'''
Name: cam_rrfs_chem_plots_specs.py
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This script defines plotting related settings.
'''
import matplotlib
import matplotlib.pyplot as plt
import datetime
import sys
import os
import numpy as np
import cam_rrfs_chem_util as gda_util

class PlotSpecs:
    def __init__(self, logger, plot_type):
        """! Initialize PlotSpecs class

             Args:
                 logger    - logger object
                 plot_type - type of graphic being produced (string)

             Returns:
        """
        self.plot_type = plot_type
        self.logger = logger
        self.font_weight = 'bold'
        self.axis_title_weight = 'bold'
        self.axis_title_size = 16
        self.axis_title_pad = 15
        self.axis_title_loc = 'center'
        self.axis_offset = False
        self.axis_label_weight = 'bold'
        self.axis_label_size = 16
        self.axis_label_pad = 10
        self.xtick_label_size = 16
        self.xtick_major_pad = 10
        self.ytick_label_size = 16
        self.ytick_major_pad = 10
        self.fig_title_weight = 'bold'
        self.fig_title_size = 16
        self.fig_subplot_right = 0.95
        self.fig_subplot_left = 0.1
        self.fig_subplot_top = 0.925
        self.fig_subplot_bottom = 0.075
        self.legend_handle_text_pad = 0.25
        self.legend_handle_length = 1.25
        self.legend_border_axis_pad = 0
        self.legend_col_space = 1.0
        self.legend_frame_on = True
        self.legend_bbox = (0,1)
        self.legend_font_size = 13
        self.legend_loc = 'center'
        self.legend_ncol = 1
        self.title_loc = 'center'
        self.fig_size=(16.,16.)
        if self.plot_type in ['time_series_fhr_mean',
                              'lead_average_no_diffplot',
                              'valid_hour_average_no_diffplot',
                              'threshold_average_no_diffplot']:
            self.fig_size = (16., 8.)
            self.fig_subplot_top = 0.87
            self.fig_subplot_bottom = 0.1
            self.fig_subplot_right = 0.925
            self.fig_subplot_left = 0.085
            self.axis_label_size = 15
            self.xtick_label_size = 15
            self.ytick_label_size = 15
            self.legend_frame_on = False
            self.legend_bbox = (0.5, 0.05)
            self.legend_ncol = 4
        elif self.plot_type in ['lead_average_vhr_mean',
                                'valid_hour_average_fhr_mean',
                                'threshold_average_fhrvhr_mean']:
            self.fig_size = (16., 16.)
            self.fig_subplot_top = 0.9
            self.fig_subplot_bottom = 0.05
            self.fig_subplot_right = 0.92
            self.fig_subplot_left = 0.12
            self.legend_frame_on = False
            self.legend_bbox = (0.5, 0.05)
            self.legend_ncol = 5
            self.fig_title_size = 18
        else:
            self.logger.error(f"{self.plot_type} not recongized")
            sys.exit(1)

    def set_up_plot(self):
        """! Set up the matplotlib rcParams

             Args:

             Returns:
        """
        plt.rcParams['font.weight'] = self.font_weight
        plt.rcParams['axes.titleweight'] = self.axis_title_weight
        plt.rcParams['axes.titlesize'] = self.axis_title_size
        plt.rcParams['axes.titlepad'] = self.axis_title_pad
        plt.rcParams['axes.titlelocation'] = self.axis_title_loc
        plt.rcParams['axes.labelweight'] = self.axis_label_weight
        plt.rcParams['axes.labelsize'] = self.axis_label_size
        plt.rcParams['axes.labelpad'] = self.axis_label_pad
        plt.rcParams['axes.formatter.useoffset'] = self.axis_offset
        plt.rcParams['xtick.labelsize'] = self.xtick_label_size
        plt.rcParams['xtick.major.pad'] = self.xtick_major_pad
        plt.rcParams['ytick.labelsize'] = self.ytick_label_size
        plt.rcParams['ytick.major.pad'] = self.ytick_major_pad
        plt.rcParams['figure.subplot.left'] = self.fig_subplot_left
        plt.rcParams['figure.subplot.right'] = self.fig_subplot_right
        plt.rcParams['figure.subplot.top'] = self.fig_subplot_top
        plt.rcParams['figure.subplot.bottom'] = self.fig_subplot_bottom
        plt.rcParams['figure.titleweight'] = self.fig_title_weight
        plt.rcParams['figure.titlesize'] = self.fig_title_size
        plt.rcParams['legend.handletextpad'] = self.legend_handle_text_pad
        plt.rcParams['legend.handlelength'] = self.legend_handle_length
        plt.rcParams['legend.borderaxespad'] = self.legend_border_axis_pad
        plt.rcParams['legend.columnspacing'] = self.legend_col_space
        plt.rcParams['legend.frameon'] = self.legend_frame_on
        if float(matplotlib.__version__[0:3]) >= 3.3:
            plt.rcParams['date.epoch'] = '0000-12-31T00:00:00'

    def get_stat_plot_name(self, stat):
        """! Get the full statistic name that will be
             displayed on the plot

             Args:
                 stat - abbreviated statistic name (string)

             Returns:
                 stat_plot_name - full statistic name that
                                  will be displayed on the plot
                                  (string)
        """
        stat_plot_name_dict = {
            'BIAS': 'Bias (Mean Error)',
            'CSI': 'Critical Success Index',
            'FBAR': 'Forecast Mean',
            'FBAR_OBAR': 'Forecast and Observation Mean',
            'ME': 'Mean Error (Bias)',
            'OBAR': 'Observation Mean',
            'RMSE': 'Root Mean Square Error'
        }
        if stat in list(stat_plot_name_dict.keys()):
            stat_plot_name = stat_plot_name_dict[stat]
        else:
            self.logger.debug(f"{stat} not recognized, using {stat} on plot")
            stat_plot_name = stat
        return stat_plot_name

    def get_var_plot_name(self, var_name, var_level):
        """! Get the full variable information that will be displayed
             on the plot

             Args:
                 var_name   - abbreviated variable name (string)
                 var_level  - abbreviated variable level (string)
             Returns:
                 var_plot_name - full variable information that
                                 will be displayed on the plot
                                 (string)
        """
        var_name_level = var_name+'/'+var_level
        var_plot_name_dict = {
            'PMTF/Z8': 'Particulate matter with diameters $\u2264$ 2.5 $\u03bcm$',
            'PMTC/Z8': 'Particulate matter with diameters $\u2264$ 10 $\u03bcm$',
            'AOTK/L0': 'Aerosol Optical Depth at 550nm',
            'AOD/L0': 'Aerosol Optical Depth at 550nm'
        }
        if var_name_level in list(var_plot_name_dict.keys()):
            var_plot_name = var_plot_name_dict[var_name_level]
        else:
            self.logger.debug(f"{var_name_level} not recognized, "
                              +f"using {var_name_level} on plot")
            var_plot_name = var_name_level
        return var_plot_name

    def get_obs_plot_name(self, ob_name):
        """! Get the full obs source name that will be
             displayed on the plot

             Args:
                 ob_name - abbreviated obs source name (string)

             Returns:
                 obs_plot_name - full obs source name that
                                 will be displayed on the plot
                                 (string)
        """
        obs_plot_name_dict = {
            'airnow': 'AIRNOW',
            'airnow_pm25': 'AIRNOW',
            'airnow_pm10': 'AIRNOW',
            'aeronet': 'AERONET',
            'aeronet_aod': 'AERONET',
        }
        if ob_name in list(obs_plot_name_dict.keys()):
            obs_plot_name = obs_plot_name_dict[ob_name]
        else:
            self.logger.debug(f"{ob_name} not recognized, "
                              +f"using {ob_name} on plot")
            obs_plot_name = ob_name
        return obs_plot_name

    def get_vx_mask_plot_name(self, vx_mask):
        """! Get the full verification masking information that will
             be displayed on the plot

             Args:
                 vx_mask - abbreviated verification mask name (string)

             Returns:
                 vx_mask_plot_name - full verification mask name that
                                     will be displayed on the plot
                                     (string)
        """
        vx_mask_plot_name_dict = {
             'Appalachia': 'Appalachia',
             'CONUS': 'CONUS',
             'CONUS_Central': 'CONUS - Central',
             'CONUS_East': 'CONUS - East',
             'CONUS_South': 'CONUS - South',
             'CONUS_West': 'CONUS - West',
             'CPlains': 'Central Plains',
             'DeepSouth': 'Deep South',
             'GreatBasin': 'Great Basin',
             'GreatLakes': 'Great Lakes',
             'Hawaii': 'Hawaii',
             'Mezquital': 'Mezquital',
             'MidAtlantic': 'Mid-Atlantic',
             'NorthAtlantic': 'Northeast (North Atlantic)',
             'NPlains': 'Northern Plains',
             'NRockies': 'Northern Rockies',
             'PacificNW': 'Pacific Northwest',
             'PacificSW': 'Pacific Southwest',
             'Prairie': 'Prairie',
             'PuertoRico': 'Puerto Rico',
             'Southeast': 'Southeast',
             'Southwest': 'Southwest',
             'SPlains': 'Southern Plains',
             'SRockies': 'Southern Rockies'
        }
        if vx_mask in list(vx_mask_plot_name_dict.keys()):
            vx_mask_plot_name = vx_mask_plot_name_dict[vx_mask]
        else:
            self.logger.debug(f"{vx_mask} not recognized, "
                              +f"using {vx_mask} on plot")
            vx_mask_plot_name = vx_mask
        return vx_mask_plot_name

    def get_dates_plot_name_by_fday(self, date_type, start_date, end_date,
                            date_type_hr_list, other_hr_list,
                            title_plot_hour_list, plot_type):
        """! Get the full date information that will be displayed on the plot

             Args:
                 date_type          - type of dates
                                      (string, VALID or INIT)
                 start_date         - starting date and hour
                                      (string, YYYYmmdd)
                 end_date           - ending date and hour
                                      (string, YYYYmmdd)
                 date_type_hr_list  - list of hours for
                                      date_type
                 other_hr_list      - list of hours for
                                      opposite of date_type
                                      (strings)
                 title_plot_hour_list - list of selected forecast/valid hour(s)
                 plot_type          - type of plot (string)

             Returns:
                 date_plot_name - full date information that
                                  will be displayed on the plot
                                  (string)
        """
        date_plot_name = date_type.lower()+' '
        start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
        end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
        date_plot_name = (date_plot_name
                          +start_date_dt.strftime('%d%b%Y')+'-'
                          +end_date_dt.strftime('%d%b%Y')+' ')
        title_other_hr_list = []
        if date_type == 'VALID':
            if plot_type in [ 'time_series_fhr_mean', 'lead_average_vhr_mean', 
                              'valid_hour_average_fhr_mean',
                              'threshold_average_fhrvhr_mean',
                              'lead_average_no_diffplot',
                              'valid_hour_average_no_diffplot',
                              'threshold_average_no_diffplot' ]:
                title_other_list=other_hr_list[0]
                if len(other_hr_list) > 1:
                    for i_other_hr in range(1,len(other_hr_list)):
                        title_other_list = ( title_other_lists + ", " +i_other_hr)
                date_plot_name = (date_plot_name+', init. hours: '+title_other_list)
                plot_hour_range=f"{title_plot_hour_list[0]}-{title_plot_hour_list[-1]}"
                if plot_type in [ 'time_series_fhr_mean',
                                  'valid_hour_average_fhr_mean',
                                  'threshold_average_fhrvhr_mean',
                                  'valid_hour_average_no_diffplot',
                                  'threshold_average_no_diffplot' ]:
                    date_plot_name = (date_plot_name+', fcst. hours:'+plot_hour_range+' hrs')
                else:
                    date_plot_name = (date_plot_name+', valid hours:'+plot_hour_range+'Z')
            else:
                for date_type_hr in date_type_hr_list:
                    for forecast_hour in forecast_hour_list:
                        other_hr = gda_util.get_init_hour(
                            int(date_type_hr.replace('Z', '')),
                            int(forecast_hour)
                        )
                        if str(other_hr).zfill(2)+'Z' not in title_other_hr_list \
                                and str(other_hr).zfill(2)+'Z' in other_hr_list:
                            title_other_hr_list.append(str(other_hr).zfill(2)+'Z')
                title_other_hr_list.sort()
                date_plot_name = (date_plot_name+', '.join(date_type_hr_list)
                                  +', init. hours: '
                                  +', '.join(title_other_hr_list))
        elif date_type == 'INIT':
            for date_type_hr in date_type_hr_list:
                for forecast_hour in forecast_hour_list:
                    other_hr = gda_util.get_valid_hour(
                        int(date_type_hr.replace('Z', '')),
                        int(forecast_hour)
                    )
                    if str(other_hr).zfill(2)+'Z' not in title_other_hr_list \
                            and str(other_hr).zfill(2)+'Z' in other_hr_list:
                        title_other_hr_list.append(str(other_hr).zfill(2)+'Z')
                    title_other_hr_list.append(str(init_hr).zfill(2)+'Z')
            title_other_hr_list.sort()
            date_plot_name = (date_plot_name+', '.join(date_type_hr_list)
                              +', valid: '+', '.join(title_other_hr_list))
        if plot_type not in [ 'time_series_fhr_mean', 'lead_average_vhr_mean',
                             'valid_hour_average_fhr_mean',
                             'threshold_average_fhrvhr_mean',
                             'lead_average_no_diffplot',
                             'valid_hour_average_no_diffplot',
                             'threshold_average_no_diffplot']:
            forecast_day_list = []
            for forecast_hour in forecast_hour_list:
                forecast_day = int(forecast_hour)/24.
                if int(forecast_hour) % 24 == 0:
                    forecast_day_list.append(str(int(forecast_day)))
                else:
                    forecast_day_list.append(str(forecast_day))
            if len(forecast_hour_list) == 1:
                date_plot_name = (date_plot_name
                                  +', Forecast Day '+forecast_day_list[0]+' '
                                  +'(Hour '+forecast_hour_list[0]+')')
            else:
                date_plot_name = (date_plot_name
                                  +'\nForecast Days '
                                  +','.join(forecast_day_list)+' '
                                  +'(Hours '+','.join(forecast_hour_list)+')')
        return date_plot_name

    def get_plot_title_by_fday(self, plot_info_dict, date_info_dict, units, selected_plot_hours ):
        """! Construct the title for the plot

             Args:
                 plot_info_dict  - plot information dictionary (strings)
                 date_info_dict  - date information dictionary (strings)
                 units           - variable units (string)
                 selected_plot_hours - list of selected forecast/valid hour for title (string)

             Returns:
                 plot_title - full plot title that will be
                              displayed on the plot
                              (string)
        """
        plot_title = (
            self.get_stat_plot_name(plot_info_dict['stat'])+' - '
            +self.get_vx_mask_plot_name(plot_info_dict['vx_mask'])+'\n'
        )
        if date_info_dict['date_type'] == 'VALID':
            date_type_hr_list = [
                str(hr).zfill(2)+'Z' \
                for hr in range(int(date_info_dict['valid_hr_start']),
                                int(date_info_dict['valid_hr_end'])
                                +int(date_info_dict['valid_hr_inc']),
                                int(date_info_dict['valid_hr_inc']))
            ]
            other_hr_list = [
                str(hr).zfill(2)+'Z' \
                for hr in range(int(date_info_dict['init_hr_start']),
                                int(date_info_dict['init_hr_end'])
                                +int(date_info_dict['init_hr_inc']),
                                int(date_info_dict['init_hr_inc']))
            ]
        elif date_info_dict['date_type'] == 'INIT':
            date_type_hr_list = [
                str(hr).zfill(2)+'Z' \
                for hr in range(int(date_info_dict['init_hr_start']),
                                int(date_info_dict['init_hr_end'])
                                +int(date_info_dict['init_hr_inc']),
                                int(date_info_dict['init_hr_inc']))
            ]
            other_hr_list = [
                str(hr).zfill(2)+'Z' \
                for hr in range(int(date_info_dict['valid_hr_start']),
                                int(date_info_dict['valid_hr_end'])
                                +int(date_info_dict['valid_hr_inc']),
                                int(date_info_dict['valid_hr_inc']))
            ]
        if self.plot_type in ['time_series', 
                              'performance_diagram', 'threshold_average']:
            hr_info_for_title = [date_info_dict['forecast_hours']]
        elif self.plot_type in ['time_series_fhr_mean',
                                'lead_average_vhr_mean',
                                'valid_hour_average_fhr_mean',
                                'threshold_average_fhrvhr_mean',
                                'lead_average_no_diffplot',
                                'valid_hour_average_no_diffplot',
                                'threshold_average_no_diffplot']:
            hr_info_for_title = selected_plot_hours
        else:
            hr_info_for_title = date_info_dict['forecast_hours']
        var_name_for_title = plot_info_dict['fcst_var_name']
        var_level_for_title = plot_info_dict['fcst_var_level']
        if self.plot_type in [ 'threshold_average_fhrvhr_mean',
                              'threshold_average_no_diffplot']:
            var_thresh_for_title = 'NA'
        else:
            var_thresh_for_title = plot_info_dict['fcst_var_thresh']
        plot_title = (plot_title
                      +self.get_var_plot_name(var_name_for_title,
                                              var_level_for_title))
        if plot_info_dict['fcst_var_name'] in [ 'AOTK', 'AOD']:
            units = 'unitless'
        elif plot_info_dict['fcst_var_name'] in [ 'PMTF', 'PMTC']:
            units = r'$\mu g/m^3$'
        else:
            units = 'unknown'
        plot_title = plot_title+' '+'('+units+')'
        if var_thresh_for_title != 'NA':
            var_thresh_symbol = var_thresh_for_title.replace("gt","$\u003E$").replace("ge","$\u2265$")
            if plot_info_dict['fcst_var_name'] in [ 'AOTK', 'AOD' ]:
                plot_title = plot_title+', '+var_thresh_symbol
            else:
                plot_title = plot_title+', '+var_thresh_symbol+' '+units
            thresh_value = float(plot_info_dict['fcst_var_thresh'][2:])
        plot_title = (plot_title+' - '
                      +'Validation: '
                      +self.get_obs_plot_name(plot_info_dict['obs_src_name']))
        if self.plot_type in [ 'time_series_fhr_mean', 'lead_average_vhr_mean',
                               'valid_hour_average_fhr_mean',
                               'threshold_average_fhrvhr_mean',
                               'lead_average_no_diffplot',
                               'valid_hour_average_no_diffplot',
                               'threshold_average_no_diffplot' ]:
            self.logger.debug(f"pass {self.plot_type} to get_dates_plot_name_by_fday")
            plot_title = (plot_title+'\n'
                      +self.get_dates_plot_name_by_fday(date_info_dict['date_type'],
                                                date_info_dict['start_date'],
                                                date_info_dict['end_date'],
                                                date_type_hr_list, other_hr_list,
                                                hr_info_for_title, self.plot_type))
        else:
            self.logger.debug(f"pass {self.plot_type} to get_dates_plot_name")
            plot_title = (plot_title+'\n'
                      +self.get_dates_plot_name(date_info_dict['date_type'],
                                                date_info_dict['start_date'],
                                                date_info_dict['end_date'],
                                                date_type_hr_list, other_hr_list,
                                                hr_info_for_title, self.plot_type,
                                                plot_info_dict['fcst_var_name']))
        return plot_title

    def get_savefig_name(self, image_dir, plot_info_dict, date_info_dict):
        """! Construct the full path to save the plot

             Args:
                 image_dir       - full path to directory of where
                                   to save (string)
                 plot_info_dict  - plot information dictionary (strings)
                 date_info_dict  - date information dictionary (strings)

             Returns:
                 image_path - full path of the name the plot will
                              be saved as (string)
        """
        component_savefig_name = 'rrfs_chem'
        if plot_info_dict['stat'] == 'PERFDIAG':
            metric_savefig_name = 'ctc'
        else:
            metric_savefig_name = plot_info_dict['stat']
        if 'fcst_var_thresh' in list(plot_info_dict.keys()):
            if plot_info_dict['fcst_var_thresh'] != 'NA':
                thresh_symbol, thresh_letter = gda_util.format_thresh(
                    plot_info_dict['fcst_var_thresh']
                )
                metric_savefig_name = (
                    metric_savefig_name+'_'
                    +thresh_letter.replace('.','p')
                )
        parameter_savefig_name = plot_info_dict['fcst_var_name']
        level_savefig_name = (
            plot_info_dict['fcst_var_level'].replace('-', '_')\
            .replace('.', 'p')
        )
        start_date_dt = datetime.datetime.strptime(
            date_info_dict['start_date'], '%Y%m%d'
        )
        end_date_dt = datetime.datetime.strptime(
            date_info_dict['end_date'], '%Y%m%d'
        )
        ndays = int((end_date_dt - start_date_dt).total_seconds()/86400) + 1

        savefig_name_label = plot_info_dict['fig_name_label']

        if self.plot_type in ['time_series', 'time_series_multifhr',
                              'time_series_fhr_mean']:
            plot_type_savefig_name = 'timeseries'
        elif self.plot_type in ['lead_average', 'lead_average_vhr_mean',
                                'lead_average_no_diffplot']:
            plot_type_savefig_name = 'fhrmean'
        elif self.plot_type in ['valid_hour_average',
                                'valid_hour_average_fhr_mean',
                                'valid_hour_average_no_diffplot']:
            plot_type_savefig_name = 'vhrmean'
        elif self.plot_type == 'performance_diagram':
            plot_type_savefig_name = 'perfdiag'
        elif self.plot_type in ['threshold_average',
                                'threshold_average_fhrvhr_mean',
                                'threshold_average_no_diffplot']:
            plot_type_savefig_name = 'threshmean'
        else:
            plot_type_savefig_name = self.plot_type.replace('_', '')

        if self.plot_type in ['time_series', 'time_series_multifhr',
                              'time_series_fhr_mean',
                              'valid_hour_average_fhr_mean',
                              'threshold_average_fhrvhr_mean',
                              'valid_hour_average_no_diffplot',
                              'threshold_average_no_diffplot',
                              'performance_diagram',
                              'threshold_average' ]:
            init_hr_savefig_name = f"init{date_info_dict['init_hr_start']}z"
            fcst_day_savefig_name = f"day{date_info_dict['fday_start']}"
            plot_type_savefig_name = (
                 plot_type_savefig_name+'_'+fcst_day_savefig_name+'_'+init_hr_savefig_name
            )
        if self.plot_type in [ 'lead_average', 'lead_average_vhr_mean',
                               'lead_average_no_diffplot' ]:
            init_hr_savefig_name = f"init{date_info_dict['init_hr_start']}z"
            plot_type_savefig_name = (
                 plot_type_savefig_name+'_dayna_'+init_hr_savefig_name
            )
        if self.plot_type == 'time_series_multifhr':
            plot_type_savefig_name = (
                 plot_type_savefig_name+'_'
                 +''.join(['f'+f.zfill(3) for \
                            f in date_info_dict['forecast_hours']])
            )
        grid_savefig_name = plot_info_dict['grid']
        region_savefig_dict = {
            'Appalachia': 'buk_apl',
            'CONUS': 'buk_conus',
            'CONUS_East': 'buk_conus_e',
            'CONUS_Central': 'buk_conus_c',
            'CONUS_South': 'buk_conus_s',
            'CONUS_West': 'buk_conus_w',
            'CPlains': 'buk_cpl',
            'DeepSouth': 'buk_ds',
            'GreatBasin': 'buk_grb',
            'GreatLakes': 'buk_grlk',
            'Hawaii': 'hawaii',
            'Mezquital': 'buk_mez',
            'MidAtlantic': 'buk_matl',
            'NorthAtlantic': 'buk_ne',
            'NPlains': 'buk_npl',
            'NRockies': 'buk_nrk',
            'PacificNW': 'buk_npw',
            'PacificSW': 'buk_psw',
            'Prairie': 'buk_pra',
            'PuertoRico':'puertorico',
            'Southeast': 'buk_se',
            'Southwest': 'buk_sw',
            'SPlains': 'buk_spl',
            'SRockies': 'buk_srk'
        }
        if plot_info_dict['vx_mask'] in list(region_savefig_dict.keys()):
            region_savefig_name = (
                region_savefig_dict[plot_info_dict['vx_mask']]
            )
        else:
            region_savefig_name = plot_info_dict['vx_mask']
        savefig_name = (
            'evs.'
            +component_savefig_name+'.'
            +metric_savefig_name+'.'
            +parameter_savefig_name+'_'+level_savefig_name+'.'
            +savefig_name_label+'.'
            +plot_type_savefig_name+'.'
            +grid_savefig_name+'_'+region_savefig_name
            +'.png'
        ).lower()
        image_path = os.path.join(image_dir, savefig_name)
        return image_path

    def get_logo_location(self, position, x_figsize, y_figsize, dpi):
        """! Get locations for the logos

             Args:
                 position  - side of image (string, "left" or "right")
                 x_figsize - image size in x direction (float)
                 y_figsize - image size in y direction(float)
                 dpi       - image dots per inch (float)

             Returns:
                 x_loc - logo position in x direction (float)
                 y_loc - logo position in y direction (float)
                 alpha - alpha value (float)
        """
        alpha = 0.5
        if x_figsize == 8 and y_figsize == 6:
            if position == 'left':
                x_loc = x_figsize * dpi * 0.0
                y_loc = y_figsize * dpi * 0.858
            elif position == 'right':
                x_loc = x_figsize * dpi * 0.9
                y_loc = y_figsize * dpi * 0.858
        elif x_figsize == 16 and y_figsize == 8:
            if position == 'left':
                x_loc = x_figsize * dpi * 0.0
                y_loc = y_figsize * dpi * 0.89
            elif position == 'right':
                x_loc = x_figsize * dpi * 0.948
                y_loc = y_figsize * dpi * 0.89
        elif x_figsize == 16 and y_figsize == 16:
            if position == 'left':
                x_loc = x_figsize * dpi * 0
                y_loc = y_figsize * dpi * 0.945
            elif position == 'right':
                x_loc = x_figsize * dpi * 0.948
                y_loc = y_figsize * dpi * 0.945
        return x_loc, y_loc, alpha

    def get_plot_colormaps(self, stat):
        """! Get colormaps for contour plots

             Args:
                 stat    - statistic name (string)

             Returns:
                 subplot0_cmap  - colormap for subplot 0
                 subplotsN_cmap - colormap for other subplots
        """
        if stat in ['BIAS', 'ME', 'FBIAS']:
            cmap_bias_original = plt.cm.PiYG_r
            colors_bias = cmap_bias_original(
                np.append(np.linspace(0,0.3,10), np.linspace(0.7,1,10))
            )
            subplot0_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
                'cmap_bias', colors_bias
            )
        else:
            subplot0_cmap = plt.cm.BuPu_r
        if stat in ['BIAS', 'ME', 'FBIAS']:
            subplotsN_cmap = subplot0_cmap
        else:
            if stat == 'RMSE':
                cmap_diff_original = plt.cm.bwr
            else:
                cmap_diff_original = plt.cm.bwr_r
            colors_diff = cmap_diff_original(
                np.append(np.linspace(0,0.425,10), np.linspace(0.575,1,10))
            )
            subplotsN_cmap = (
                matplotlib.colors.LinearSegmentedColormap.from_list('cmap_diff',
                                                                    colors_diff)
            )
        return subplot0_cmap, subplotsN_cmap

    def get_model_plot_settings(self):
        """! Get dictionary plot settings for models

             Args:

             Returns:
                 model_plot_settings_dict - dictionary of
                                            model plotting specifications
                                            (strings)
        """
        model_plot_settings_dict = {
            'model1': {'color': '#000000', 'markevery': None,
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 3},
            'model2': {'color': '#fb2020', 'markevery': None,
                       'marker': '^', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model3': {'color': '#1e3cff', 'markevery': None,
                       'marker': 'X', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model4': {'color': '#00dc00', 'markevery': None,
                       'marker': 'P', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model5': {'color': '#e69f00', 'markevery': None,
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model6': {'color': '#56b4e9', 'markevery': None,
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model7': {'color': '#696969', 'markevery': None,
                       'marker': 's', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model8': {'color': '#8400c8', 'markevery': None,
                       'marker': 'D', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model9': {'color': '#d269c1', 'markevery': None,
                       'marker': 's', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model10': {'color': '#f0e492', 'markevery': None,
                        'marker': 'o', 'markersize': 6,
                        'linestyle': 'solid', 'linewidth': 1.5},
            'obs': {'color': '#aaaaaa', 'markevery': None,
                    'marker': 'None', 'markersize': 0,
                    'linestyle': 'solid', 'linewidth': 2},
            'gfs': {'color': '#000000', 'markevery': None,
                    'marker': 'o', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 3},
            'gfs00Z': {'color': '#000000', 'markevery': None,
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 3},
            'gfs06Z': {'color': '#fb2020', 'markevery': None,
                       'marker': '^', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'gfs12Z': {'color': '#1e3cff', 'markevery': None,
                       'marker': 'X', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'gfs18Z': {'color': '#e69f00', 'markevery': None,
                       'marker': 'o', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'cfs': {'color': '#56b4e9', 'markevery': None,
                    'marker': 'o', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 1.5},
            'cmc': {'color': '#1e3cff', 'markevery': None,
                     'marker': 'X', 'markersize': 7,
                     'linestyle': 'solid', 'linewidth': 1.5},
            'cmc_regional': {'color': '#8400c8', 'markevery': None,
                             'marker': 'D', 'markersize': 6,
                             'linestyle': 'solid', 'linewidth': 1.5},
            'dwd': {'color': '#56b4e9', 'markevery': None,
                    'marker': 'o', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 1.5},
            'ecmwf': {'color': '#fb2020', 'markevery': None,
                      'marker': '^', 'markersize': 7,
                      'linestyle': 'solid', 'linewidth': 1.5},
            'fnmoc': {'color': '#00dc00', 'markevery': None,
                      'marker': 'P', 'markersize': 7,
                      'linestyle': 'solid', 'linewidth': 1.5},
            'imd': {'color': '#8400c8', 'markevery': None,
                    'marker': 'D', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 1.5},
            'jma': {'color': '#696969', 'markevery': None,
                    'marker': 's', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 1.5},
            'metfra': {'color': '#00dc00', 'markevery': None,
                      'marker': 'P', 'markersize': 7,
                      'linestyle': 'solid', 'linewidth': 1.5},
            'ukmet': {'color': '#e69f00', 'markevery': None,
                      'marker': 'o', 'markersize': 7,
                      'linestyle': 'solid', 'linewidth': 1.5},
        }
        return model_plot_settings_dict

    def get_model_plot_settings_linemarker(self):
        """! Get dictionary plot settings for models

             Args:

             Returns:
                 model_plot_settings_dict - dictionary of
                                            model plotting specifications
                                            (strings)
        """
        model_plot_settings_dict = {
            'model1': {'color': '#000000', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': 'solid', 'linewidth': 3},
            'model2': {'color': '#fb2020', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model3': {'color': '#1e3cff', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model4': {'color': '#00dc00', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model5': {'color': '#e69f00', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model6': {'color': '#56b4e9', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model7': {'color': '#696969', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model8': {'color': '#8400c8', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model9': {'color': '#d269c1', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model10': {'color': '#f0e492', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                        'linestyle': 'solid', 'linewidth': 1.5},
            'prod_raw': {'color': '#1e3cff', 'markevery': None,
                         'marker': 'None', 'markersize': 0,
                         'linestyle': 'solid', 'linewidth': 2},
            'dev_raw': {'color': '#fb2020', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': 'solid', 'linewidth': 2},
            'prod_bc': {'color': '#1e3cff', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': '--', 'linewidth': 2},
            'dev_bc': {'color': '#fb2020', 'markevery': None,
                       'marker': 'None', 'markersize': 0,
                       'linestyle': '--', 'linewidth': 2},
            'obsdot': {'color': '#000000', 'markevery': None,
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'None', 'linewidth': 0},
            'obs': {'color': '#aaaaaa', 'markevery': None,
                    'marker': 'None', 'markersize': 0,
                    'linestyle': 'solid', 'linewidth': 2},
        }
        return model_plot_settings_dict

