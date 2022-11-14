import matplotlib
import matplotlib.pyplot as plt
import datetime
import sys
import os
import numpy as np

class PlotSpecs:
    def __init__(self, logger, plot_type):
        """! Initalize PlotSpecs class

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
        if self.plot_type == 'time_series':
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
        elif self.plot_type in ['lead_average', 'valid_hour_average',
                                'threshold_average']:
            self.fig_size = (16., 16.)
            self.fig_subplot_top = 0.9
            self.fig_subplot_bottom = 0.05
            self.fig_subplot_right = 0.92
            self.fig_subplot_left = 0.12
            self.legend_frame_on = False
            self.legend_bbox = (0.5, 0.05)
            self.legend_ncol = 5
            self.fig_title_size = 18
        elif self.plot_type == 'lead_by_date':
            self.fig_size = (16., 16.)
            self.axis_title_pad = 5
            self.axis_title_loc = 'left'
            self.fig_subplot_top = 0.9
            self.fig_subplot_bottom = 0.075
            self.fig_subplot_right = 0.923
            self.fig_subplot_left = 0.15
            self.fig_title_size = 18
        elif self.plot_type == 'stat_by_level':
            self.fig_size = (16., 16.)
            self.fig_subplot_top = 0.925
            self.fig_subplot_bottom = 0.05
            self.fig_subplot_right = 0.925
            self.fig_subplot_left = 0.1
            self.legend_frame_on = False
            self.legend_bbox = (0.01, 0.995)
            self.legend_ncol = 1
            self.legend_font_size = 15
            self.legend_loc = 'upper left'
            self.fig_title_size = 18
        elif self.plot_type == 'lead_by_level':
            self.fig_size = (16., 16.)
            self.axis_title_pad = 5
            self.axis_title_loc = 'left'
            self.fig_subplot_top = 0.95
            self.fig_subplot_bottom = 0.025
            self.fig_subplot_right = 0.95
            self.fig_subplot_left = 0.1
            self.fig_title_size = 18
        elif self.plot_type == 'precip_spatial_map':
            self.fig_size = (8., 6.)
            self.fig_title_size = 13
            self.fig_subplot_right = 0.975
            self.fig_subplot_left = 0.025
            self.axis_label_size = 12
            self.xtick_label_size = 12
            self.axis_tick_size = 13
        elif self.plot_type == 'performance_diagram':
            self.fig_size = (16., 16.)
            self.fig_subplot_top = 0.9
            self.fig_subplot_bottom = 0.175
            self.fig_subplot_right = 0.85
            self.fig_subplot_left = 0.075
            self.legend_frame_on = True
            self.legend_loc = 'upper center'
            self.legend_ncol = 5
            self.legend_font_size = 16
            self.fig_title_size = 18
        else:
            self.logger.error(f"{self.plot_type} NOT RECOGNIZED")
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
            'ACC': 'Anomaly Correlation Coefficient',
            'BIAS': 'Bias',
            'CSI': 'Critical Success Index',
            'ETS': 'Equitable Threat Score',
            'FBAR': 'Forecast Mean',
            'FBAR_OBAR': 'Forecast and Observation Mean',
            'FBIAS': 'Frequency Bias',
            'FSS': 'Fraction Skill Score',
            'FY_OY': 'Forecast Yes - Obs Yes',
            'GSS': 'Gilbert Skill Score',
            'HSS': 'Heidke Skill Score',
            'OBAR': 'Observation Mean',
            'POD': 'Probability of Detection',
            'PERF_DIA': 'Performance Diagram',
            'RMSE': 'Root Mean Square Error',
            'S1': 'S1',
            'SRATIO': 'Success Ratio (1-FAR)'
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
            'APCP_A24/A24': '24 hour Accumulated Precipitation',
            'CAPE/P90-0': 'Mixed-Layer CAPE',
            'CAPE/Z0': 'Surface Based CAPE',
            'CWAT/L0': 'Cloud Water',
            'DPT/Z2': '2 meter Dewpoint',
            'GUST/Z0': 'Wind Gust',
            'HGT/CEILING': 'Ceiling',
            'HGT/NA': 'Geopotential Height',
            'HGT/P1': '1 hPa Geopotential Height',
            'HGT/P5': '5 hPa Geopotential Height',
            'HGT/P10': '10 hPa Geopotential Height',
            'HGT/P20': '20 hPa Geopotential Height',
            'HGT/P50': '50 hPa Geopotential Height',
            'HGT/P100': '100 hPa Geopotential Height',
            'HGT/P150': '150 hPa Geopotential Height',
            'HGT/P200': '200 hPa Geopotential Height',
            'HGT/P250': '250 hPa Geopotential Height',
            'HGT/P300': '300 hPa Geopotential Height',
            'HGT/P400': '400 hPa Geopotential Height',
            'HGT/P500': '500 hPa Geopotential Height',
            'HGT/P700': '700 hPa Geopotential Height',
            'HGT/P850': '850 hPa Geopotential Height',
            'HGT/P925': '925 hPa Geopotential Height',
            'HGT/P1000': '1000 hPa Geopotential Height',
            'HGT/TROPOPAUSE': 'Tropopause Geopotential Height',
            'HGT_ANOM_DAILYAVG/P500': ('500 hPa Daily Avg '
                                       +'Geopotential Height Anomaly'),
            'HGT_DECOMP_WV1_0-3/P500': ('500 hPa Geopotential Height: '
                                        +'Waves 0-3'),
            'HGT_DECOMP_WV1_0-20/P500': ('500 hPa Geopotential Height: '
                                         +'Waves 0-20'),
            'HGT_DECOMP_WV1_4-9/P500': ('500 hPa Geopotential Height: '
                                        +'Waves 4-9'),
            'HGT_DECOMP_WV1_10-20/P500': ('500 hPa Geopotential Height: '
                                          +'Waves 10-20'), 
            'HPBL/L0': 'Planetary Boundary Layer Height',
            'ICEC_DAILYAVG/Z0': 'Daily Avg Ice Concentration',
            'ICEC_WEEKLYAVG/Z0': 'Weekly Avg Ice Concentration',
            'O3MR/P1': '1 hPa Ozone Mixing Ratio',
            'O3MR/P5': '5 hPa Ozone Mixing Ratio',
            'O3MR/P10': '10 hPa Ozone Mixing Ratio',
            'O3MR/P20': '20 hPa Ozone Mixing Ratio',
            'O3MR/P30': '30 hPa Ozone Mixing Ratio',
            'O3MR/P50': '50 hPa Ozone Mixing Ratio',
            'O3MR/P70': '70 hPa Ozone Mixing Ratio',
            'O3MR/P100': '100 hPa Ozone Mixing Ratio',
            'PWAT/L0': 'Precipitable Water',
            'PRES/Z0': 'Surface Pressure',
            'PRMSL/Z0': 'Pressure Reduced to MSL',
            'RH/NA': 'Relative Humidity',
            'RH/P1': '1 hPa Relative Humidity',
            'RH/P5': '5 hPa Relative Humidity',
            'RH/P10': '10 hPa Relative Humidity',
            'RH/P20': '20 hPa Relative Humidity',
            'RH/P50': '50 hPa Relative Humidity',
            'RH/P100': '100 hPa Relative Humidity',
            'RH/P150': '150 hPa Relative Humidity',
            'RH/P200': '200 hPa Relative Humidity',
            'RH/P250': '250 hPa Relative Humidity',
            'RH/P300': '300 hPa Relative Humidity',
            'RH/P400': '400 hPa Relative Humidity',
            'RH/P500': '500 hPa Relative Humidity',
            'RH/P700': '700 hPa Relative Humidity',
            'RH/P850': '850 hPa Relative Humidity',
            'RH/P925': '925 hPa Relative Humidity',
            'RH/P1000': '1000 hPa Relative Humidity',
            'RH/Z2': '2 meter Relative Humidity',
            'SNOD_A24/Z0': '24 hour Snow Accumulation (derived from SNOD)',
            'SOILW/Z0.1-0': '0.1-0 meter Volumetric Soil Moisture Content',
            'SPFH/NA': 'Specific Humidity',
            'SPFH/P1': '1 hPa Specific Humidity',
            'SPFH/P5': '5 hPa Specific Humidity',
            'SPFH/P10': '10 hPa Specific Humidity',
            'SPFH/P20': '20 hPa Specific Humidity',
            'SPFH/P50': '50 hPa Specific Humidity',
            'SPFH/P100': '100 hPa Specific Humidity',
            'SPFH/P150': '150 hPa Specific Humidity',
            'SPFH/P200': '200 hPa Specific Humidity',
            'SPFH/P250': '250 hPa Specific Humidity',
            'SPFH/P300': '300 hPa Specific Humidity',
            'SPFH/P400': '400 hPa Specific Humidity',
            'SPFH/P500': '500 hPa Specific Humidity',
            'SPFH/P700': '700 hPa Specific Humidity',
            'SPFH/P850': '850 hPa Specific Humidity',
            'SPFH/P925': '925 hPa Specific Humidity',
            'SPFH/P1000': '1000 hPa Specific Humidity',
            'SPFH/Z2': '2 meter Specific Humidity',
            'SST_DAILYAVG/Z0': 'Daily Avg Sea Surface Temperature',
            'TCDC/TOTAL': 'Total Cloud Cover',
            'TMP/NA': 'Temperature',
            'TMP/P1': '1 hPa Temperature',
            'TMP/P5': '5 hPa Temperature',
            'TMP/P10': '10 hPa Temperature',
            'TMP/P20': '20 hPa Temperature',
            'TMP/P50': '50 hPa Temperature',
            'TMP/P100': '100 hPa Temperature',
            'TMP/P150': '150 hPa Temperature',
            'TMP/P100': '100 hPa Temperature',
            'TMP/P200': '200 hPa Temperature',
            'TMP/P250': '250 hPa Temperature',
            'TMP/P300': '300 hPa Temperature',
            'TMP/P400': '400 hPa Temperature',
            'TMP/P500': '500 hPa Temperature',
            'TMP/P700': '700 hPa Temperature',
            'TMP/P850': '850 hPa Temperature',
            'TMP/P925': '925 hPa Temperature',
            'TMP/P1000': '1000 hPa Temperature',
            'TMP/TROPOPAUSE': 'Tropopause Temperature',
            'TMP/Z2': '2 meter Temperature',
            'TMP_ANOM_DAILYAVG/Z2': '2 meter Daily Avg Temperature Anomaly',
            'TOZNE/L0': 'Total Ozone',
            'TSOIL/Z0.1-0': '0.1-0 meter Soil Temperature',
            'UGRD/NA': 'U-Component of Wind',
            'UGRD/P1': '1 hPa U-Component of Wind',
            'UGRD/P5': '5 hPa U-Component of Wind',
            'UGRD/P10': '10 hPa U-Component of Wind',
            'UGRD/P20': '20 hPa U-Component of Wind',
            'UGRD/P50': '50 hPa U-Component of Wind',
            'UGRD/P100': '100 hPa U-Component of Wind',
            'UGRD/P150': '150 hPa U-Component of Wind',
            'UGRD/P200': '200 hPa U-Component of Wind',
            'UGRD/P250': '250 hPa U-Component of Wind',
            'UGRD/P300': '300 hPa U-Component of Wind',
            'UGRD/P400': '400 hPa U-Component of Wind',
            'UGRD/P500': '500 hPa U-Component of Wind',
            'UGRD/P700': '700 hPa U-Component of Wind',
            'UGRD/P850': '850 hPa U-Component of Wind',
            'UGRD/P925': '925 hPa U-Component of Wind',
            'UGRD/P1000': '1000 hPa U-Component of Wind',
            'UGRD/Z10': '10 meter U-Component of Wind',
            'UGRD_VGRD/NA': 'Vector Wind',
            'UGRD_VGRD/P1': '1 hPa Vector Wind',
            'UGRD_VGRD/P5': '5 hPa Vector Wind',
            'UGRD_VGRD/P10': '10 hPa Vector Wind',
            'UGRD_VGRD/P20': '20 hPa Vector Wind',
            'UGRD_VGRD/P50': '50 hPa Vector Wind',
            'UGRD_VGRD/P100': '100 hPa Vector Wind',
            'UGRD_VGRD/P150': '150 hPa Vector Wind',
            'UGRD_VGRD/P200': '200 hPa Vector Wind',
            'UGRD_VGRD/P250': '250 hPa Vector Wind',
            'UGRD_VGRD/P300': '300 hPa Vector Wind',
            'UGRD_VGRD/P400': '400 hPa Vector Wind',
            'UGRD_VGRD/P500': '500 hPa Vector Wind',
            'UGRD_VGRD/P700': '700 hPa Vector Wind',
            'UGRD_VGRD/P850': '850 hPa Vector Wind',
            'UGRD_VGRD/P925': '925 hPa Vector Wind',
            'UGRD_VGRD/P1000': '1000 hPa Vector Wind',
            'UGRD_VGRD/Z10': '10 meter Vector Wind',
            'VIS/Z0': 'Visibility',
            'VGRD/NA': 'V-Component of Wind',
            'VGRD/P1': '1 hPa V-Component of Wind',
            'VGRD/P5': '5 hPa V-Component of Wind',
            'VGRD/P10': '10 hPa V-Component of Wind',
            'VGRD/P20': '20 hPa V-Component of Wind',
            'VGRD/P50': '50 hPa V-Component of Wind',
            'VGRD/P100': '100 hPa V-Component of Wind',
            'VGRD/P150': '150 hPa V-Component of Wind',
            'VGRD/P200': '200 hPa V-Component of Wind',
            'VGRD/P250': '250 hPa V-Component of Wind',
            'VGRD/P300': '300 hPa V-Component of Wind',
            'VGRD/P400': '400 hPa V-Component of Wind',
            'VGRD/P500': '500 hPa V-Component of Wind',
            'VGRD/P700': '700 hPa V-Component of Wind',
            'VGRD/P850': '850 hPa V-Component of Wind',
            'VGRD/P925': '925 hPa V-Component of Wind',
            'VGRD/P1000': '1000 hPa V-Component of Wind',
            'VGRD/Z10': '10 meter V-Component of Wind',
            'WEASD/Z0': 'Water Equivalent of Accumulated Snow Depth',
            'WEASD_A24/Z0': '24 hour Snow Accumulation (derived from WEASD)',
            'WNDSHR/P850-P200': 'Wind Shear (850-200 hPa)'
        }
        if var_name_level in list(var_plot_name_dict.keys()):
            var_plot_name = var_plot_name_dict[var_name_level]
        else:
            self.logger.debug(f"{var_name_level} not recognized, "
                              +f"using {var_name_level} on plot")
            var_plot_name = var_name_level
        return var_plot_name

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
             'ANTARCTIC': 'Antarctic 50S-90S',
             'Appalachia': 'Appalachia',
             'ARCTIC': 'Arctic 50N-90N',
             'ATL_MDR': 'Atlantic Main Development Region',
             'CONUS': 'CONUS',
             'CONUS_Central': 'CONUS - Central',
             'CONUS_East': 'CONUS - East',
             'CONUS_South': 'CONUS - South',
             'CONUS_West': 'CONUS - West',
             'CPlains': 'Central Plains',
             'DeepSouth': 'Deep South',
             'EPAC_MDR': 'East Pacific Main Development Region',
             'GLOBAL': 'Global',
             'GreatBasin': 'Great Basin',
             'Great Lakes': 'Great Lakes',
             'Mezquital': 'Mezquital',
             'MidAtlantic': 'Mid-Atlantic',
             'N60N90': '60N-90N',
             'NAO': 'Northern Atlantic Ocean',
             'NPO': 'Northern Pacific Ocean',
             'NHEM': 'Northern Hemisphere 20N-80N',
             'North Atlantic': 'North Atlantic',
             'NPlains': 'Northern Plains',
             'NRockies': 'Northern Rockies',
             'PacificNW': 'Pacific NW',
             'PacificSW': 'Pacific SW',
             'Prairie': 'Prairies',
             'S60S90': '60S-90S',
             'SAO': 'Southern Atlantic Ocean',
             'SPO': 'Southern Pacific Ocean',
             'SHEM': 'Southern Hemisphere 20S-80S',
             'Southeast': 'Southeast',
             'Southwest': 'Southwest',
             'SPlains': 'Southern Plains',
             'SRockies': 'Southern Rockies',
             'TROPICS': 'Tropics 20S-20N',
        }
        if vx_mask in list(vx_mask_plot_name_dict.keys()):
            vx_mask_plot_name = vx_mask_plot_name_dict[vx_mask]
        else:
            self.logger.debug(f"{vx_mask} not recognized, "
                              +f"using {vx_mask} on plot")
            vx_mask_plot_name = vx_mask
        return vx_mask_plot_name

    def get_dates_plot_name(self, date_type, start_date_hr, end_date_hr,
                            other_hr_list, forecast_hour):
        """! Get the full date information that will be displayed on the plot

             Args:
                 date_type     - type of dates (string, VALID or INIT)
                 start_date_hr - starting date and hour (string, YYYYmmddHH)
                 end_date_hr   - ending date and hour (string, YYYYmmddHH)
                 other_hr_list - list of hours for opposite of date_type
                                 (strings)
                 forecast_hour - forecast hour, if not applicable is NA
 
             Returns:
                 date_plot_name - full date information that
                                  will be displayed on the plot
                                  (string)
        """
        date_plot_name = date_type.lower()+' '
        start_date_hr_dt = datetime.datetime.strptime(start_date_hr, '%Y%m%d%H')
        end_date_hr_dt = datetime.datetime.strptime(end_date_hr, '%Y%m%d%H')
        date_plot_name = (date_plot_name
                          +start_date_hr_dt.strftime('%d%b%Y %H')+'Z-'
                          +end_date_hr_dt.strftime('%d%b%Y %H')+'Z, ')
        if date_type == 'VALID':
            date_plot_name = (date_plot_name
                              +'cycles: '+', '.join(other_hr_list))
        elif date_type == 'INIT':
            date_plot_name = (date_plot_name
                              +'valid: '+', '.join(other_hr_list))
        if forecast_hour != 'NA':
            forecast_day = int(forecast_hour)/24.
            if int(forecast_hour) % 24 == 0:
                forecast_day_plot = str(int(forecast_day))
            else: 
                forecast_day_plot = str(forecast_day)
            date_plot_name = (date_plot_name
                              +', Forecast Day '+forecast_day_plot+' '
                              +'(Hour '+forecast_hour+')')
        return date_plot_name

    def get_plot_title(self, plot_info_dict, date_info_dict, units):
        """! Construct the title for the plot

             Args:
                 plot_info_dict  - plot information dictionary (strings)
                 date_info_dict  - date information dictionary (strings)
                 units           - variable units (string)
 
             Returns:
                 plot_title - full plot title that will be 
                              displayed on the plot
                              (string)
        """
        plot_title = (
            self.get_stat_plot_name(plot_info_dict['stat'])+' - '
            +plot_info_dict['grid']+'/'
            +self.get_vx_mask_plot_name(plot_info_dict['vx_mask'])+'\n'
        )
        if date_info_dict['date_type'] == 'VALID':
            start_date_hr =  (date_info_dict['start_date']
                              +date_info_dict['valid_hr_start'])
            end_date_hr =  (date_info_dict['end_date']
                            +date_info_dict['valid_hr_end'])
            other_hr_list = [
                str(hr).zfill(2)+'Z' \
                for hr in range(int(date_info_dict['init_hr_start']),
                                int(date_info_dict['init_hr_end'])
                                +int(date_info_dict['init_hr_inc']),
                                int(date_info_dict['init_hr_inc']))
            ]
        elif date_info_dict['date_type'] == 'INIT':
            start_date_hr =  (date_info_dict['start_date']
                              +date_info_dict['init_hr_start'])
            end_date_hr =  (date_info_dict['end_date']
                            +date_info_dict['init_hr_end'])
            other_hr_list = [
                str(hr).zfill(2)+'Z' \
                for hr in range(int(date_info_dict['valid_hr_start']),
                                int(date_info_dict['valid_hr_end'])
                                +int(date_info_dict['valid_hr_inc']),
                                int(date_info_dict['valid_hr_inc']))
            ]
        if self.plot_type in ['time_series', 'stat_by_level',
                              'performance_diagram', 'threshold_average']:
            fhr_for_title = date_info_dict['forecast_hour']
        elif self.plot_type in ['lead_average', 'valid_hour_average',
                                'lead_by_date', 'lead_by_level']:
            fhr_for_title = 'NA'
        if plot_info_dict['fcst_var_name'] == 'HGT_DECOMP':
            var_name_for_title = (plot_info_dict['fcst_var_name']
                                  +'_'+plot_info_dict['interp_method'])
        else:
            var_name_for_title = plot_info_dict['fcst_var_name']
        if self.plot_type in ['stat_by_level', 'lead_by_level']:
            var_level_for_title = 'NA'
        else:
            var_level_for_title = plot_info_dict['fcst_var_level']
        if self.plot_type in ['performance_diagram', 'threshold_average']:
            var_thresh_for_title = 'NA'
        else:
            var_thresh_for_title = plot_info_dict['fcst_var_thresh']
        plot_title = (plot_title
                      +self.get_var_plot_name(var_name_for_title,
                                              var_level_for_title))
        plot_title = plot_title+' '+'('+units+')'
        if var_thresh_for_title != 'NA':
            plot_title = plot_title+' '+var_thresh_for_title
        if plot_info_dict['interp_method'] == 'NBRHD_SQUARE':
            plot_title = (plot_title+' '
                          +'Neighborhood Points: '
                          +plot_info_dict['interp_points'])
        plot_title = (plot_title+'\n'
                      +self.get_dates_plot_name(date_info_dict['date_type'],
                                                start_date_hr, end_date_hr,
                                                other_hr_list, fhr_for_title))
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
        if date_info_dict['date_type'] == 'VALID':
            date_type_start_hr = date_info_dict['valid_hr_start']
            date_type_end_hr = date_info_dict['valid_hr_end']
        elif date_info_dict['date_type'] == 'INIT':
            date_type_start_hr = date_info_dict['init_hr_start']
            date_type_end_hr = date_info_dict['init_hr_end']
        if plot_info_dict['fcst_var_name'] == 'HGT_DECOMP':
            var_name_for_savefig = (plot_info_dict['fcst_var_name']+'_'
                                    +plot_info_dict['interp_method'])
        else:
            var_name_for_savefig = plot_info_dict['fcst_var_name']
        if self.plot_type in ['time_series', 'stat_by_level',
                              'performance_diagram', 'threshold_average']:
            fhr_for_savefig = 'fhr'+date_info_dict['forecast_hour'].zfill(3)
        elif self.plot_type in ['lead_average', 'lead_by_level']:
            fhr_for_savefig = 'fhrmean'
        elif self.plot_type == 'lead_by_date':
            fhr_for_savefig = 'leaddate'
        elif self.plot_type == 'valid_hour_average':
            fhr_for_savefig = (
                'f'+str(date_info_dict['forecast_hours'][0]).zfill(3)+'to'
                'f'+str(date_info_dict['forecast_hours'][-1]).zfill(3)
            )
        savefig_name = (plot_info_dict['stat']+'_'
                        +var_name_for_savefig+'_'
                        +plot_info_dict['fcst_var_level']+'_')
        if self.plot_type == 'performance_diagram':
            var_thresh_for_savefig = ''.join(
                plot_info_dict['fcst_var_threshs']
            )
        elif self.plot_type == 'threshold_average':
            var_thresh_for_savefig = 'threshmean'
        else:
            if '||':
                var_thresh_for_savefig = (
                    plot_info_dict['fcst_var_thresh'].replace('||', '')
                )
            else:
                var_thresh_for_savefig = plot_info_dict['fcst_var_thresh']
        if var_thresh_for_savefig != 'NA':
            savefig_name = savefig_name+var_thresh_for_savefig+'_'
        if plot_info_dict['interp_method'] == 'NBRHD_SQUARE':
            savefig_name = (savefig_name
                            +plot_info_dict['interp_method']
                            +plot_info_dict['interp_points']+'_')
        savefig_name = (savefig_name
                        +plot_info_dict['grid']
                        +plot_info_dict['vx_mask']+'_')
        savefig_name = (savefig_name
                        +date_info_dict['date_type'].lower()
                        +date_info_dict['start_date']
                        +date_type_start_hr+'to'
                        +date_info_dict['end_date']
                        +date_type_end_hr+'_'
                        +fhr_for_savefig+'_'
                        +self.plot_type
                        +'.png')
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
        if stat in ['BIAS', 'FBIAS']:
            cmap_bias_original = plt.cm.PiYG_r
            colors_bias = cmap_bias_original(
                np.append(np.linspace(0,0.3,10), np.linspace(0.7,1,10))
            )
            subplot0_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
                'cmap_bias', colors_bias
            )
        else:
            subplot0_cmap = plt.cm.BuPu_r
        if stat in ['BIAS', 'FBIAS']:
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

    def get_centered_contour_levels(self, data, center_value, spacing):
        """! Get contour levels for plotting levels center on a certain
             value
                  Args:
                      data         - array of data to be contoured
                      center_value - center value of the levels (integer)
                      spacing      - float for spacing for power function,
                                     value of 1.0 gives evenly spaced
                                     contour intervals
                  Returns:
                      center_clevels - array of contour levels
        """
        if np.abs(np.nanmin(data)) > np.nanmax(data):
            cmax = np.abs(np.nanmin(data))
            cmin = np.nanmin(data)
        else:
            cmax = np.nanmax(data)
            cmin = -1 * np.nanmax(data)
        if cmax > 100:
            clevels_cmax = cmax - (cmax * 0.2)
            clevels_cmin = cmin + (cmin * 0.2)
        elif cmax > 10:
            clevels_cmax = cmax - (cmax * 0.1)
            clevels_cmin = cmin + (cmin * 0.1)
        else:
            clevels_cmax = cmax
            clevels_cmin = cmin
        if cmax > 1:
            clevels_round_cmin = round(clevels_cmin-1,0)
            clevels_round_cmax = round(clevels_cmax+1,0)
        else:
            clevels_round_cmin = round(clevels_cmin-0.1,1)
            clevels_round_cmax = round(clevels_cmax+0.1,1)
        steps = 6
        span = cmax
        dx = 1.0 / (steps-1)
        pos = np.array([0 + (i*dx)**spacing*span for i in range(steps)],
                       dtype=float)
        neg = np.array(pos[1:], dtype=float) * -1
        centered_clevels = np.append(neg[::-1], pos)
        if center_value != 0:
            centered_clevels = centered_clevels + center_value
        return centered_clevels

    def get_plot_contour_levels(self, stat, subplot0_data, subplotsN_data):
        """! Get contour levels

             Args:
                 stat           - statistic name (string)
                 subplot0_data  - array of data for subplot 0
                 subplotsN_data - array of data for other subplots

             Returns:
                 have_subplot0_levs  - boolean if have valid values
                                       subplot 0
                 subplot0_levs       - array of contour levels for
                                       subplot 0
                 have_subplotsN_levs - boolean if have valid values
                                       other subplots
                 subplotsN_levs      - array of contour levels for
                                       other subplots
        """
        have_subplot0_levs = False
        subplot0_levs = np.array([np.nan])
        if stat == 'ACC':
            have_subplot0_levs = True
            subplot0_levs = np.array([0.0, 0.25, 0.5, 0.6, 0.7, 0.8,
                                      0.9, 0.95, 0.99, 1])
        elif not np.ma.masked_invalid(subplot0_data).mask.all():
            cmax = np.nanmax(subplot0_data)
            if cmax > 100:
                spacing = 2.25
            elif cmax > 10:
                spacing = 2
            else:
                spacing = 1.75
            if stat == 'RMSE':
                steps = 12
                dx = 1.0 / (steps-1)
                have_subplot0_levs = True
                subplot0_levs = np.array(
                    [0+(i*dx)**spacing*cmax for i in range(steps)],
                    dtype=float
                )
            elif stat in ['BIAS', 'FBIAS']:
                if stat == 'BIAS':
                    center_value = 0
                elif stat == 'FBIAS':
                    center_value = 1
                have_subplot0_levs = True
                subplot0_levs = self.get_centered_contour_levels(
                    subplot0_data, center_value, spacing
                )
        have_subplotsN_levs = False
        subplotsN_levs = np.array([np.nan])
        if stat == 'ACC':
            have_subplotsN_levs = True
            subplotsN_levs = np.array([-0.5, -0.4, -0.3, -0.2, -0.1, -0.05,
                                       0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5])
        else:
            if np.shape(subplotsN_data) != np.shape([np.nan]):
                if stat in ['BIAS', 'FBIAS']:
                    have_subplotsN_levs = have_subplot0_levs
                    subplotsN_levs = subplot0_levs
                if not have_subplotsN_levs:
                    for N in range(len(subplotsN_data[:,0,0])):
                        if stat in ['BIAS', 'FBIAS']:
                            subplotN_data = subplotsN_data[N,:,:]
                            if np.nanmax(subplotN_data) > 100:
                                spacing = 2.25
                            elif np.nanmax(subplotN_data) > 100:
                                spacing = 2
                            else:
                                spacing = 1.75
                            if stat == 'BIAS':
                                center_value = 0
                            elif stat == 'FBIAS':
                                center_value = 1
                        else:
                            subplotN_data = (subplotsN_data[N,:,:]
                                             - subplot0_data)
                            center_value = 0
                            spacing = 1.25
                        if not np.ma.masked_invalid(subplotN_data).mask.all():
                            have_subplotsN_levs = True
                            subplotsN_levs = self.get_centered_contour_levels(
                                subplotN_data, center_value, spacing
                            )
                            break
        return have_subplot0_levs, subplot0_levs, have_subplotsN_levs, subplotsN_levs

    def get_vert_profile_levels(self, vert_profile):
        """! Get list of levels that make up the vertical profile

             Args:
                vert_profile - name of vertical profile (string)

             Returns:
                 vert_profile_levs - list of pressure levels that
                                     make up the vertical profile
                                     (strings)
        """
        vert_profile_levels_dict = {
            'all': ['P1000', 'P925', 'P850', 'P700', 'P500', 'P400', 'P300',
                    'P250', 'P200', 'P150', 'P100', 'P50', 'P20', 'P10',
                    'P5', 'P1'],
            'lower_trop': ['P1000', 'P925', 'P850', 'P700', 'P500'],
            'upper_trop': ['P500', 'P400', 'P300', 'P250', 'P200',
                           'P150', 'P100'],
            'trop': ['P1000', 'P925', 'P850', 'P700', 'P500', 'P500', 'P400',
                     'P300', 'P250', 'P200', 'P150', 'P100'],
            'strat': ['P100', 'P50', 'P20', 'P10', 'P5', 'P1']
        }
        if vert_profile in list(vert_profile_levels_dict.keys()):
            vert_profile_levels = vert_profile_levels_dict[vert_profile]
        else:
            self.logger.debug(f"{vert_profile} not recognized, "
                              +f"using all levels")
            vert_profile_levels = vert_profile_levels_dict['all']
        return vert_profile_levels

    def get_marker_plot_settings(self):
        """! Get dictionary plot settings for models

             Args:

             Returns: 
                 marker_plot_settings_dict - dictionary of
                                             marker plotting specifications
                                             (strings)
        """
        marker_plot_settings_dict = {
            'marker1': {'marker': 'o', 'markersize': 12},
            'marker2': {'marker': 'P', 'markersize': 14},
            'marker3': {'marker': '^', 'markersize': 14},
            'marker4': {'marker': 'X', 'markersize': 14},
            'marker5': {'marker': 's', 'markersize': 12},
            'marker6': {'marker': 'D', 'markersize': 12},
            'marker7': {'marker': 'v', 'markersize': 14},
            'marker8': {'marker': 'p', 'markersize': 14},
            'marker9': {'marker': '<', 'markersize': 14},
            'marker10': {'marker': 'd', 'markersize': 14},
            'marker11': {'marker': r'$\spadesuit$', 'markersize': 14},
            'marker12': {'marker': '>', 'markersize': 14},
            'marker13': {'marker': r'$\clubsuit$', 'markersize': 14},
        }
        return marker_plot_settings_dict

    def get_model_plot_settings(self):
        """! Get dictionary plot settings for models

             Args:

             Returns: 
                 model_plot_settings_dict - dictionary of
                                            model plotting specifications
                                            (strings)
        """
        model_plot_settings_dict = {
            'model1': {'color': '#000000',
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 3},
            'model2': {'color': '#fb2020',
                       'marker': '^', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model3': {'color': '#1e3cff',
                       'marker': 'X', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model4': {'color': '#00dc00',
                       'marker': 'P', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model5': {'color': '#e69f00',
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model6': {'color': '#56b4e9',
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model7': {'color': '#696969',
                       'marker': 's', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model8': {'color': '#8400c8',
                       'marker': 'D', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model9': {'color': '#d269c1',
                       'marker': 's', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 1.5},
            'model10': {'color': '#f0e492',
                        'marker': 'o', 'markersize': 6,
                        'linestyle': 'solid', 'linewidth': 1.5},
            'obs': {'color': '#aaaaaa',
                    'marker': 'None', 'markersize': 0,
                    'linestyle': 'solid', 'linewidth': 2},
            'gfs': {'color': '#000000',
                    'marker': 'o', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 3},
            'cfs': {'color': '#56b4e9',
                    'marker': 'o', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 1.5},
            'cmc': {'color': '#1e3cff',
                     'marker': 'X', 'markersize': 7,
                     'linestyle': 'solid', 'linewidth': 1.5},
            'ecmwf': {'color': '#fb2020',
                      'marker': '^', 'markersize': 7,
                      'linestyle': 'solid', 'linewidth': 1.5},
            'fnmoc': {'color': '#00dc00',
                      'marker': 'P', 'markersize': 7,
                      'linestyle': 'solid', 'linewidth': 1.5},
            'imd': {'color': '#8400c8',
                    'marker': 'D', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 1.5},
            'jma': {'color': '#696969',
                    'marker': 's', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 1.5},
            'ukmet': {'color': '#e69f00',
                      'marker': 'o', 'markersize': 7,
                      'linestyle': 'solid', 'linewidth': 1.5},
        }
        return model_plot_settings_dict
