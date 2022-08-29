import matplotlib
import matplotlib.pyplot as plt
import datetime
import sys
import os

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
        self.axis_title_size = 20
        self.axis_offset = False
        self.axis_title_pad = 15
        self.axis_label_weight = 'bold'
        self.axis_label_size = 16
        self.axis_label_pad = 10
        self.xtick_label_size = 16
        self.xtick_major_pad = 10
        self.ytick_label_size = 16
        self.ytick_major_pad = 10
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
        self.legend_font_size = 17
        self.legend_loc = 'center right'
        self.legend_ncol = 1
        self.title_loc = 'center'
        self.fig_size=(14.,14.)
        if self.plot_type == 'time_series':
            self.fig_size = (14., 7.)
            self.axis_title_size = 16
            self.fig_subplot_top = 0.825
            self.fig_subplot_bottom = 0.125
            self.fig_subplot_right = 0.95
            self.fig_subplot_left = 0.15
            self.legend_frame_on = False
            self.legend_bbox = (0.5, 0.05)
            self.legend_font_size = 13
            self.legend_loc = 'center'
            self.legend_ncol = 5
        else:
            self.logger.warning(f"{self.plot_type} NOT RECOGNIZED")
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
            'FBIAS': 'Frequency Bias',
            'FSS': 'Fraction Skill Score',
            'FY_OY': 'Forecast Yes - Obs Yes',
            'GSS': 'Gilbert Skill Score',
            'POD': 'Probability of Detection',
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
            'HGT_ANOM/P500': '500 hPa Geopotential Height Anomaly',
            'HGT_DECOMP_WV1_0-3/P500': ('500 hPa Geopotential Height: '
                                        +'Waves 0-3'),
            'HGT_DECOMP_WV1_0-20/P500': ('500 hPa Geopotential Height: '
                                         +'Waves 0-20'),
            'HGT_DECOMP_WV1_4-9/P500': ('500 hPa Geopotential Height: '
                                        +'Waves 4-9'),
            'HGT_DECOMP_WV1_10-20/P500': ('500 hPa Geopotential Height: '
                                          +'Waves 10-20'), 
            'HPBL/L0': 'Planetary Boundary Layer Height',
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
            'TCDC/TOTAL': 'Total Cloud Cover',
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
            'TMP_ANOM/Z2': '2 meter Temperature Anomaly',
            'TOZNE': 'Total Ozone',
            'TSOIL/Z0.1-0': '0.1-0 meter Soil Temperature',
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
            'WEASD_A24/Z0': '24 hour Snow Accumulation (derived from WEASD)'
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
             'Appalachia': 'Appalachia',
             'CONUS': 'CONUS',
             'CONUS_Central': 'CONUS - Central',
             'CONUS_East': 'CONUS - East',
             'CONUS_South': 'CONUS - South',
             'CONUS_West': 'CONUS - West',
             'CPlains': 'Central Plains',
             'DeepSouth': 'Deep South',
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
                              +'cycles: '+', '.join(other_hr_list)+'\n')
        elif date_type == 'INIT':
            date_plot_name = (date_plot_name
                              +'valid: '+', '.join(other_hr_list)+'\n')
        if forecast_hour != 'NA':
            forecast_day = int(forecast_hour)/24.
            if int(forecast_hour) % 24 == 0:
                forecast_day_plot = str(int(forecast_day))
            else: 
                forecast_day_plot = str(forecast_day)
            date_plot_name = (date_plot_name
                              +'Forecast Day '+forecast_day_plot+' '
                              +'(Forecast Hour '+forecast_hour+')')
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
            +self.get_vx_mask_plot_name(plot_info_dict['grid'])+'/'
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
        if self.plot_type == 'time_series':
            if plot_info_dict['fcst_var_name'] == 'HGT_DECOMP':
                plot_title = (
                    plot_title
                    +self.get_var_plot_name(
                        plot_info_dict['fcst_var_name']
                        +'_'+plot_info_dict['interp_method'],
                        plot_info_dict['fcst_var_level']
                    )
                )
            else:
                plot_title = (
                    plot_title
                    +self.get_var_plot_name(
                        plot_info_dict['fcst_var_name'],
                        plot_info_dict['fcst_var_level']
                    )
                )
            plot_title = (
                plot_title+' '
                +'('+units+')'
            )
            if plot_info_dict['fcst_var_thresh'] != 'NA':
                plot_title = (
                    plot_title+' '
                    +plot_info_dict['fcst_var_thresh']
                )
            if plot_info_dict['interp_method'] == 'NBRHD_SQUARE':
                plot_title = (
                    plot_title+' '
                    +'Neighborhood Points: '
                    +plot_info_dict['interp_points']
                )
            plot_title = (
                plot_title+'\n'
                +self.get_dates_plot_name(date_info_dict['date_type'],
                                          start_date_hr, end_date_hr,
                                          other_hr_list,
                                          date_info_dict['forecast_hour'])
            )
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
        savefig_name = plot_info_dict['stat']+'_'
        if plot_info_dict['interp_method'] == 'NBRHD_SQUARE':
            savefig_name = (
                savefig_name
                +plot_info_dict['interp_method']
                +plot_info_dict['interp_points']+'_'
            )
        if plot_info_dict['fcst_var_name'] == 'HGT_DECOMP':
            savefig_name = (
                savefig_name
                +plot_info_dict['fcst_var_name']+'_'
                +plot_info_dict['interp_method']+'_'
                +plot_info_dict['fcst_var_level']+'_'
            )
        else:
            savefig_name = (
                savefig_name
                +plot_info_dict['fcst_var_name']+'_'
                +plot_info_dict['fcst_var_level']+'_'
            )
        if plot_info_dict['fcst_var_thresh'] != 'NA':
            savefig_name = (
                savefig_name
                +plot_info_dict['fcst_var_thresh']+'_'
            )
        savefig_name = (
            savefig_name
            +plot_info_dict['grid']
            +plot_info_dict['vx_mask']+'_'
        )
        savefig_name = (
            savefig_name
            +date_info_dict['date_type'].lower()
            +date_info_dict['start_date']
            +date_type_start_hr+'to'
            +date_info_dict['end_date']
            +date_type_end_hr+'_'
            +'fhr'+date_info_dict['forecast_hour'].zfill(3)
            +'.png'
        )
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
        if x_figsize == 14 and y_figsize == 7:
            if position == 'left':
                x_loc = x_figsize * dpi * 0.15
                y_loc = y_figsize * dpi * 0.86
            elif position == 'right':
                x_loc = x_figsize * dpi * 0.9
                y_loc = y_figsize * dpi * 0.86
        return x_loc, y_loc, alpha

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
                       'linestyle': 'solid', 'linewidth': 3},
            'model3': {'color': '#1e3cff',
                       'marker': 'X', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 3},
            'model4': {'color': '#00dc00',
                       'marker': 'P', 'markersize': 7,
                       'linestyle': 'solid', 'linewidth': 3},
            'model5': {'color': '#e69f00',
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 3},
            'model6': {'color': '#56b4e9',
                       'marker': 'o', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 3},
            'model7': {'color': '#696969',
                       'marker': 's', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 3},
            'model8': {'color': '#8400c8',
                       'marker': 'D', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 3},
            'model9': {'color': '#d269c1',
                       'marker': 's', 'markersize': 6,
                       'linestyle': 'solid', 'linewidth': 3},
            'model10': {'color': '#f0e492',
                        'marker': 'o', 'markersize': 6,
                        'linestyle': 'solid', 'linewidth': 3},
            'obs': {'color': '#aaaaaa',
                    'marker': 'None', 'markersize': 0,
                    'linestyle': 'solid', 'linewidth': 4},
            'GFS': {'color': '#000000',
                    'marker': 'o', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 3},
            'ECMWF': {'color': '#fb2020',
                      'marker': '^', 'markersize': 7,
                      'linestyle': 'solid', 'linewidth': 3},
            'FNMOC': {'color': '#1e3cff',
                      'marker': 'X', 'markersize': 7,
                      'linestyle': 'solid', 'linewidth': 3},
            'CMC': {'color': '#00dc00',
                    'marker': 'P', 'markersize': 7,
                    'linestyle': 'solid', 'linewidth': 3},
            'UKMET': {'color': '#e69f00',
                      'marker': 'o', 'markersize': 7,
                      'linestyle': 'solid', 'linewidth': 3},
            'CFSR': {'color': '#56b4e9',
                     'marker': 'o', 'markersize': 6,
                     'linestyle': 'solid', 'linewidth': 3},
            'JMA': {'color': '#696969',
                    'marker': 's', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 3},
            'IMD': {'color': '#8400c8',
                    'marker': 'D', 'markersize': 6,
                    'linestyle': 'solid', 'linewidth': 3},
        }
        return model_plot_settings_dict
