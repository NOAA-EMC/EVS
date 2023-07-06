#!/usr/bin/env python3
'''
Name: cam_plots_precip_spatial_map.py
Contact(s): Marcel Caron, Mallory Row
Abstract: This script generates a spatial map for precip
'''

import netCDF4 as netcdf
import pyproj
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
import glob
import logging
import sys
import datetime
import subprocess
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy import config
from cam_plots_specs import PlotSpecs

class PrecipSpatialMap:
    """
    Create a precipitation spatial map graphic
    """

    def __init__(self, logger, input_dir, output_dir, model_info_dict,
                 date_info_dict, plot_info_dict, met_info_dict, logo_dir, 
                 cartopy_data_dir):
        """! Initalize PrecipSpatialMap class
             Args:
                 logger           - logger object
                 input_dir        - path to input directory (string)
                 output_dir       - path to output directory (string)
                 model_info_dict  - model infomation dictionary (strings)
                 plot_info_dict   - plot information dictionary (strings)
                 date_info_dict   - date information dictionary (strings)
                 met_info_dict    - MET information dictionary (strings)
                 logo_dir         - directory with logo images (string)
                 cartopy_data_dir - directory with cartopy shapefiles (string)
 
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
        self.cartopy_data_dir = cartopy_data_dir

    def make_precip_spatial_map(self):
        """! Create the precipitation spatial map graphic
             Args:
             Returns:
        """
        self.logger.info(f"Creating preciptation spatial map...")
        self.logger.debug(f"Input directory: {self.input_dir}")
        self.logger.debug(f"Output directory: {self.output_dir}")
        self.logger.debug(f"Model information dictionary: "
                          +f"{self.model_info_dict}")
        self.logger.debug(f"Date information dictionary: "
                          +f"{self.date_info_dict}")
        self.logger.debug(f"Plot information dictionary: "
                          +f"{self.plot_info_dict}")
        # Make job image directory
        output_image_dir = os.path.join(self.output_dir, 'precip', 'na')
        if not os.path.exists(output_image_dir):
            os.makedirs(output_image_dir)
        self.logger.info(f"Plots will be in: {output_image_dir}")
        # Set valid and initialization dates
        valid_date_dt = datetime.datetime.strptime(
            self.date_info_dict['end_date']
            +self.date_info_dict['valid_hr_end'], '%Y%m%d%H'
        )
        init_date_dt = (
            valid_date_dt 
            - datetime.timedelta(
                hours=int(self.date_info_dict['forecast_hour']))
        )
        # Set contour levels and color map
        clevs_in = [0.01, 0.10, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50,
                    1.75, 2.00, 2.50, 3.00, 4.00, 5.00, 7.00, 10.00,
                    15.00, 20.00]
        colorlist_in = ['#7fff00', '#00cd00', '#008b00', '#104e8b',
                        '#1e90ff', '#00b2ee', '#00eeee', '#8968cd',
                        '#912cee', '#8b008b', '#8b0000', '#cd0000',
                        '#ee4000', '#ff7f00', '#cd8500', '#ffd700',
                        '#ffff00', '#ffff02']
        cmap_over_color_in = '#ffaeb9'
        clevs_mm = [0.1, 2, 5, 10, 15, 20, 25, 35, 50, 75, 100, 125,
                    150, 175, 200]
        colorlist_mm = ['chartreuse', 'green', 'blue', 'dodgerblue',
                        'deepskyblue', 'cyan', 'mediumpurple',
                        'mediumorchid', 'darkmagenta', 'darkred',
                        'crimson', 'orangered', 'darkorange',
                        'goldenrod', 'yellow']
        cmap_over_color_mm = '#ffaeb9'
        # Set Cartopy shapefile location
        config['data_dir'] = self.cartopy_data_dir
        # Read in data
        self.logger.info(f"Reading in model files from {self.input_dir}")
        for model_num in self.model_info_dict:
            model_num_dict = self.model_info_dict[model_num]
            model_num_name = model_num_dict['name']
            model_num_plot_name = model_num_dict['plot_name']
            model_num_obs_name = model_num_dict['obs_name']
            model_num_data_dir = os.path.join(
                self.input_dir,
                valid_date_dt.strftime('atmos.%Y%m%d'),
            )
            make_plot = False
            if model_num == 'obs':
                image_data_source = 'qpe'
                image_forecast_hour = '024'
            else:
                image_data_source = model_num_name
                image_forecast_hour = (
                    self.date_info_dict['forecast_hour'].zfill(3)
                )
            image_region_dict = {
                'CONUS': 'conus',
                'Alaska': 'ak',
                'Hawaii': 'hi',
                'PuertoRico': 'pr'
            }
            image_name = os.path.join(
                output_image_dir,
                image_data_source
                +'.v'+valid_date_dt.strftime('%Y%m%d%H')+'.'
                +image_forecast_hour+'h.'
                +image_region_dict[self.plot_info_dict['vx_mask']]+'.png'
            )
            if model_num == 'obs':
                model_num_files = glob.glob(os.path.join(
                    model_num_data_dir,
                    '*',
                    'precip',
                    valid_date_dt.strftime(f'{model_num_name}.%Y%m%d'),
                    valid_date_dt.strftime(
                       f'{model_num_name}.t%Hz.a24h.'
                       + f'{image_region_dict[self.plot_info_dict["vx_mask"]]}'
                       + f'.nc'
                    ),
                ))
                if model_num_files:
                    model_num_file = model_num_files[0]
                    if not os.path.exists(image_name):
                        make_plot = True
                    else: 
                        make_plot = False
                else:
                    make_plot = False
                    self.logger.warning(f"No input files exist, "
                                        +"not making plot")
            else:
                model_num_file = os.path.join(
                    model_num_data_dir,
                    model_num,
                    'precip',
                    init_date_dt.strftime(f'{model_num_name}.init%Y%m%d'),
                    init_date_dt.strftime(
                       f'{model_num_name}.t%Hz.'
                       + f'f{self.date_info_dict["forecast_hour"].zfill(3)}.'
                       + f'a24h.'
                       + f'{image_region_dict[self.plot_info_dict["vx_mask"]]}'
                       + f'.nc'
                    ),
                )
                if not os.path.exists(image_name):
                    if os.path.exists(model_num_file):
                        make_plot = True
                    else:
                        make_plot = False
                        self.logger.warning(f"{model_num_file} does not exist, "
                                        +"not making plot")
                else:
                    make_plot = False
            if make_plot:
                self.logger.debug("Plotting data from "+model_num_file)
                precip_data = netcdf.Dataset(model_num_file)
                precip_lat = precip_data.variables['lat'][:]
                precip_lon = precip_data.variables['lon'][:]
                if model_num_name == 'mrms':
                    precip_var_key = 'MultiSensor_QPE_01H_Pass2_Z0'
                else:
                    precip_var_key = 'APCP_24'
                precip_APCP_A24 = precip_data.variables[precip_var_key][:]
                var_name = precip_data.variables[precip_var_key].getncattr('name')
                var_level = precip_data.variables[precip_var_key].getncattr('level')
                var_units = precip_data.variables[precip_var_key].getncattr('units')
                if precip_lat.ndim == 1 and precip_lon.ndim == 1:
                    x, y = np.meshgrid(precip_lon, precip_lat)
                elif precip_lat.ndim == 2 and precip_lon.ndim == 2:
                    x = precip_lon
                    y = precip_lat

                file_init_time = (precip_data.variables[precip_var_key]\
                                  .getncattr('init_time'))
                file_valid_time = (precip_data.variables[precip_var_key]\
                                   .getncattr('valid_time'))
                file_init_time_dt = datetime.datetime.strptime(
                    file_init_time, '%Y%m%d_%H%M%S'
                )
                file_valid_time_dt = datetime.datetime.strptime(
                    file_valid_time, '%Y%m%d_%H%M%S'
                )
                if valid_date_dt != file_valid_time_dt:
                    self.logger.error(f"FILE VALID TIME {file_valid_time_dt} "
                                      +"DOES NOT MATCH EXPECTED VALID TIME "
                                      +f"{valid_date_dt}")
                    sys.exit(1)
                if model_num != 'obs':
                    if init_date_dt != file_init_time_dt:
                        self.logger.error(f"FILE INIT TIME {file_init_time_dt} "
                                          +"DOES NOT MATCH EXPECTED INIT TIME "
                                          +f"{init_date_dt}")
                        sys.exit(1)
                if var_units in ['mm', 'kg/m^2']:
                    self.logger.info(f"Converting from {var_units} to " 
                                     +"inches")
                    precip_APCP_A24 = precip_APCP_A24 * 0.0393701
                    var_units = 'inches'
                self.logger.info(f"Doing plot set up")
                plot_specs_psm = PlotSpecs(self.logger, 'precip_spatial_map')
                plot_specs_psm.set_up_plot()
                forecast_day = int(self.date_info_dict['forecast_hour'])/24.
                if int(self.date_info_dict['forecast_hour']) % 24 == 0:
                    forecast_day_plot = str(int(forecast_day))
                else:
                    forecast_day_plot = str(forecast_day)
                if model_num == 'obs':
                    plot_title = (
                        model_num_plot_name+' '
                        +plot_specs_psm.get_var_plot_name(var_name, var_level)+' '
                        +f'({var_units})\n'
                        +'valid '
                        +(valid_date_dt-datetime.timedelta(hours=24))\
                        .strftime('%d%b%Y %H')+'Z to '
                        +valid_date_dt.strftime('%d%b%Y %H')+'Z'
                    )
                else:
                    plot_title = (
                        model_num_plot_name+' '
                        +plot_specs_psm.get_var_plot_name(var_name, var_level)+' '
                        +f'({var_units})\n'
                        +'Forecast Day '+forecast_day_plot+' '
                        +'(Hour '+self.date_info_dict['forecast_hour']+')\n'
                        +'valid '
                        +(valid_date_dt-datetime.timedelta(hours=24))\
                        .strftime('%d%b%Y %H')+'Z to '
                        +valid_date_dt.strftime('%d%b%Y %H')+'Z'
                    )
                plot_left_logo = False
                plot_left_logo_path = os.path.join(self.logo_dir, 'noaa.png')
                if os.path.exists(plot_left_logo_path):
                    plot_left_logo = True
                    left_logo_img_array = matplotlib.image.imread(
                        plot_left_logo_path
                    )
                    left_logo_xpixel_loc,left_logo_ypixel_loc,left_logo_alpha = (
                        plot_specs_psm.get_logo_location(
                            'left', plot_specs_psm.fig_size[0],
                             plot_specs_psm.fig_size[1],
                             plt.rcParams['figure.dpi']
                        )
                    )
                plot_right_logo = False
                plot_right_logo_path = os.path.join(self.logo_dir, 'nws.png')
                if os.path.exists(plot_right_logo_path):
                    plot_right_logo = True
                    right_logo_img_array = matplotlib.image.imread(
                        plot_right_logo_path
                    )
                    right_logo_xpixel_loc,right_logo_ypixel_loc,right_logo_alpha = (
                        plot_specs_psm.get_logo_location(
                            'right', plot_specs_psm.fig_size[0],
                            plot_specs_psm.fig_size[1],
                            plt.rcParams['figure.dpi']
                        )
                    )
                if var_units == 'inches':
                    clevs = clevs_in
                    cmap = matplotlib.colors.ListedColormap(colorlist_in)
                    cmap_over_color = cmap_over_color_in
                elif var_units in ['mm', 'kg/m^2']:
                    clevs = clevs_mm
                    cmap = matplotlib.colors.ListedColormap(colorlist_mm)
                    cmap_over_color = cmap_over_color_mm
                norm = matplotlib.colors.BoundaryNorm(clevs, cmap.N)
                # Create plot
                self.logger.info(f"Creating plot for {model_num_file}")
                fig = plt.figure(figsize=(plot_specs_psm.fig_size[0],
                                          plot_specs_psm.fig_size[1]))
                gs_hspace, gs_wspace = 0, 0
                gs_bottom, gs_top = 0.125, 0.85
                gs = gridspec.GridSpec(1,1, bottom=gs_bottom, top=gs_top,
                                       hspace=gs_hspace, wspace=gs_wspace)
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
                if self.plot_info_dict['vx_mask'] == 'CONUS':
                    extent = [-124,-70,18.0,50.0]
                    central_lon = -97.6
                    central_lat = 35.4
                elif self.plot_info_dict['vx_mask'] == 'Alaska':
                    extent = [-180,-110,45.0,75.0]
                    central_lon = -145
                    central_lat = 60
                elif self.plot_info_dict['vx_mask'] == 'PuertoRico':
                    extent = [-75,-60,12.0,25.0]
                    central_lon = -67.5
                    central_lat = 18.5
                elif self.plot_info_dict['vx_mask'] == 'Hawaii':
                    extent = [-165,-150,15.0,25.0]
                    central_lon = -157.5
                    central_lat = 20
                myproj=ccrs.LambertConformal(central_longitude=central_lon,
                                             central_latitude=central_lat,
                                             false_easting=0.0,
                                             false_northing=0.0,
                                             secant_latitudes=None,
                                             standard_parallels=None,
                                             globe=None)
                ax1 = fig.add_subplot(gs[0], projection=myproj)
                ax1.set_extent(extent)
                ax1.add_feature(cfeature.COASTLINE.with_scale('50m'),
                                zorder=2, linewidth=1)
                ax1.add_feature(cfeature.BORDERS.with_scale('50m'),
                                zorder=2, linewidth=1)
                ax1.add_feature(cfeature.STATES.with_scale('50m'),
                                zorder=2, linewidth=1)
                
                # Sanitize lons if plot crosses the dateline
                ax_ul = (0.,1.)
                ax_ur = (1.,1.)
                ax_ul_display = ax1.transAxes.transform(ax_ul)
                ax_ur_display = ax1.transAxes.transform(ax_ur)
                ax_ul_data = ax1.transData.inverted().transform(ax_ul_display)
                ax_ur_data = ax1.transData.inverted().transform(ax_ur_display)
                ax_ul_cartesian = ccrs.PlateCarree().transform_point(*ax_ul_data, src_crs=myproj)
                ax_ur_cartesian = ccrs.PlateCarree().transform_point(*ax_ur_data, src_crs=myproj)
                if ax_ul_cartesian[0] > ax_ur_cartesian[0]:
                    x = np.mod(x, 360.)         

                CF1 = ax1.contourf(x, y, precip_APCP_A24,
                                   transform=ccrs.PlateCarree(),
                                   levels=clevs, norm=norm,
                                   cmap=cmap, extend='max')
                CF1.cmap.set_over(cmap_over_color)
                cbar_left = gs.get_grid_positions(fig)[2][0]
                cbar_width = (gs.get_grid_positions(fig)[3][-1]
                              - gs.get_grid_positions(fig)[2][0])
                cbar_bottom = 0.075
                cbar_height = 0.03
                cbar_ax = fig.add_axes(
                    [cbar_left, cbar_bottom, cbar_width, cbar_height]
                )
                cbar = fig.colorbar(CF1, cax=cbar_ax,
                                    orientation='horizontal',
                                    ticks=CF1.levels)
                cbar.ax.set_xlabel(f'Precipitation ({var_units})',
                                   labelpad = 0)
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
                # Convert png to gif, if possible
                check_convert = subprocess.run(
                    ['which', 'convert'], stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                if check_convert.returncode == 0:
                    self.logger.info(f"Converting {image_name} to "
                                     +f"{image_name.replace('.png', '.gif')}")
                    run_convert = subprocess.run(
                        ['convert', image_name,
                         image_name.replace('.png', '.gif')]
                    )
                else:
                    self.logger.warning("convert executable not in PATH, "
                                        "not creating gif of image")

def main():
    # Need settings
    INPUT_DIR = os.environ['HOME']
    OUTPUT_DIR = os.environ['HOME']
    LOGO_DIR = os.environ['HOME'],
    CARTOPY_DIR = os.environ['cartopyDataDir']
    MODEL_INFO_DICT = {
        'model1': {'name': 'MODEL_A',
                   'plot_name': 'PLOT_MODEL_A',
                   'obs_name': 'MODEL_A_OBS'},
        'obs': {'name': 'OBS',
                'plot_name': 'PLOT_OBS',
                'obs_name': 'OBS'}
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
        'version': '10.1.1'
    }
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
    p = PrecipSpatialMap(logger, INPUT_DIR, OUTPUT_DIR, MODEL_INFO_DICT,
                         DATE_INFO_DICT, PLOT_INFO_DICT, MET_INFO_DICT,
                         LOGO_DIR, cartopyDataDir)
    p.make_precip_spatial_map()

if __name__ == "__main__":
    main()
