#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_nohrsc_spatial_map.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script generates a spatial map for 24 hour NOHRSC snowfall.
          (lat-lon plots; contours: snowfall)
          (EVS Graphics Naming Convention: nohrsc.vYYYYmmdd12.024h.conus.[gif][png])
'''

import netCDF4 as netcdf
import pyproj
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
import logging
import sys
import datetime
import subprocess
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy import config
import global_det_atmos_util as gda_util
from global_det_atmos_plots_specs import PlotSpecs

class NOHRSCSpatialMap:
    """
    Make a NOHRSC spatial map graphic
    """

    def __init__(self, logger, input_dir, DATA_output_dir, COMOUT_output_dir,
                 date_info_dict, plot_info_dict, logo_dir):
        """! Initalize NOHRSCSpatialMap class
             Args:
                 logger            - logger object
                 input_dir         - path to input directory (string)
                 DATA_output_dir   - path to DATA output directory (string)
                 COMOUT_output_dir - path to COMOUT output directory (string)
                 plot_info_dict    - plot information dictionary (strings)
                 date_info_dict    - date information dictionary (strings)
                 logo_dir          - directory with logo images (string)

             Returns:
        """
        self.logger = logger
        self.input_dir = input_dir
        self.DATA_output_dir = DATA_output_dir
        self.COMOUT_output_dir = COMOUT_output_dir
        self.date_info_dict = date_info_dict
        self.plot_info_dict = plot_info_dict
        self.logo_dir = logo_dir

    def make_nohrsc_spatial_map(self):
        """! Make the NOHRSCn spatial map graphic
             Args:
             Returns:
        """
        self.logger.info(f"Plot Type: NOHRSC Spatial Map")
        self.logger.debug(f"Input directory: {self.input_dir}")
        self.logger.debug(f"Output directory: {self.DATA_output_dir}")
        self.logger.debug(f"Date information dictionary: "
                          +f"{self.date_info_dict}")
        self.logger.debug(f"Plot information dictionary: "
                          +f"{self.plot_info_dict}")
        # Set valid date
        valid_date_dt = datetime.datetime.strptime(
            self.date_info_dict['end_date']
            +self.date_info_dict['valid_hr_end'], '%Y%m%d%H'
        )
        # Set contour levels and color map
        clevs_in = [0, 0.1, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36, 48,
                    60, 72, 96, 120]
        colorlist_in = ['#e4eef5', '#bdd7e7', '#6baed6', '#3282bd', '#09519c',
                        '#092694', '#fffc96', '#ffc400', '#ff8700', '#db1f00',
                        '#9d1300', '#690900', '#360200', '#ccccff', '#9f8cd8',
                        '#7c52a5', '#561c72']
        cmap_under_color_in = '#ffffff'
        cmap_over_color_in = '#2e0533'
        clevs_m = [0.1, 0.5, 1, 2, 3, 4, 5, 10, 15, 20, 25, 35, 50]
        colorlist_m = ['#a8e7e9', '#70e4ea', '#69b5d5', '#669ce5', '#5065d0',
                        '#4739ce', '#561ec1', '#7300be', '#b705c6', '#970983',
                        '#a01c60', '#c03b60', '#924b4a']
        cmap_under_color_m = '#ffffff'
        cmap_over_color_m = '#5d2c2e'
        # Set Cartopy shapefile location
        config['data_dir'] = config['repo_data_dir']
        # Convert NOHRSC grib2 to netCDF and read in data
        self.logger.info(f"Reading in NOHRSC file from {self.input_dir}")
        nohrsc_grib2_file = os.path.join(
            self.input_dir,
            'nohrsc_snow_24hrAccum_valid'+valid_date_dt.strftime('%Y%m%d%H')
            +'.grb2'
        )
        nohrsc_netcdf_file = os.path.join(
            self.input_dir,
            'nohrsc_snow_24hrAccum_valid'+valid_date_dt.strftime('%Y%m%d%H')
            +'.nc'
        )
        check_wgrib2 = subprocess.run(
            ['which', 'wgrib2'], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if check_wgrib2.returncode == 0:
            self.logger.info(f"Converting {nohrsc_grib2_file} GRIB2 file to "
                             +f"{nohrsc_netcdf_file} netCDF file")
            run_convert = subprocess.run(
                ['wgrib2', nohrsc_grib2_file, '-netcdf',
                 nohrsc_netcdf_file]
            )
        else:
            self.logger.error("wgrib2 executable not in PATH")
            sys.exit(1)
        make_png = False
        make_gif = False
        DATA_png_name = os.path.join(
            self.DATA_output_dir,
            'nohrsc.v'+valid_date_dt.strftime('%Y%m%d%H')+'.024h.'
            +self.plot_info_dict['vx_mask']+'.png'
        )
        COMOUT_png_name = DATA_png_name.replace(
            self.DATA_output_dir, self.COMOUT_output_dir
        )
        if not os.path.exists(DATA_png_name):
            if os.path.exists(nohrsc_netcdf_file):
                make_png = True
            else:
                make_png = False
                self.logger.info(f"{nohrsc_netcdf_file} does not exist")
        else:
            make_png = False
        if make_png and os.path.exists(COMOUT_png_name):
            gda_util.copy_file(COMOUT_png_name, DATA_png_name)
            make_png = False
        if make_png:
            self.logger.debug(f"Plotting data from {nohrsc_netcdf_file}")
            nohrsc_data = netcdf.Dataset(nohrsc_netcdf_file)
            nohrsc_lat = nohrsc_data.variables['latitude'][:]
            nohrsc_lon = nohrsc_data.variables['longitude'][:]
            nohrsc_ASNOW_surface = nohrsc_data.variables['ASNOW_surface'][0,:,:]
            var_name = (nohrsc_data.variables['ASNOW_surface']\
                        .getncattr('long_name'))
            var_level = (nohrsc_data.variables['ASNOW_surface']
                         .getncattr('level'))
            var_units = (nohrsc_data.variables['ASNOW_surface']\
                         .getncattr('units'))
            if nohrsc_lat.ndim == 1 and nohrsc_lon.ndim == 1:
                x, y = np.meshgrid(nohrsc_lon, nohrsc_lat)
            elif nohrsc_lat.ndim == 2 and nohrsc_lon.ndim == 2:
                x = nohrsc_lon
                y = nohrsc_lat
            if var_units == 'm':
                self.logger.info(f"Converting from {var_units} to "
                                 +"inches")
                nohrsc_ASNOW_surface = nohrsc_ASNOW_surface * 39.3701
                var_units = 'inches'
            nohrsc_ASNOW_surface = np.ma.masked_equal(nohrsc_ASNOW_surface, 0)
            self.logger.info(f"Setting up plot")
            plot_specs_nsm = PlotSpecs(self.logger, 'nohrsc_spatial_map')
            plot_specs_nsm.set_up_plot()
            plot_title = (
                f'NOHRSC 24 hour {var_name} ({var_units})\n'
                +'valid '
                +(valid_date_dt-datetime.timedelta(hours=24))\
                .strftime('%d%b%Y %H')+'Z to '
                +valid_date_dt.strftime('%d%b%Y %H')+'Z'
            )
            plot_left_logo_path = os.path.join(self.logo_dir, 'noaa.png')
            if os.path.exists(plot_left_logo_path):
                plot_left_logo = True
                left_logo_img_array = matplotlib.image.imread(
                    plot_left_logo_path
                )
                left_logo_xpixel_loc,left_logo_ypixel_loc,left_logo_alpha = (
                    plot_specs_nsm.get_logo_location(
                        'left', plot_specs_nsm.fig_size[0],
                         plot_specs_nsm.fig_size[1],
                         plt.rcParams['figure.dpi']
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
                right_logo_xpixel_loc,right_logo_ypixel_loc,right_logo_alpha = (
                    plot_specs_nsm.get_logo_location(
                        'right', plot_specs_nsm.fig_size[0],
                        plot_specs_nsm.fig_size[1],
                        plt.rcParams['figure.dpi']
                    )
                )
            else:
                plot_right_logo = False
                self.logger.debug(f"{plot_right_logo_path} does not exist")
            if var_units == 'inches':
                clevs = clevs_in
                cmap = matplotlib.colors.ListedColormap(colorlist_in)
                cmap_under_color = cmap_under_color_in
                cmap_over_color = cmap_over_color_in
            elif var_units == 'm':
                clevs = clevs_m
                cmap = matplotlib.colors.ListedColormap(colorlist_m)
                cmap_under_color = cmap_under_color_m
                cmap_over_color = cmap_over_color_m
            norm = matplotlib.colors.BoundaryNorm(clevs, cmap.N)
            # Make plot
            self.logger.info(f"Making plot")
            fig = plt.figure(figsize=(plot_specs_nsm.fig_size[0],
                                      plot_specs_nsm.fig_size[1]))
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
            if self.plot_info_dict['vx_mask'] == 'conus':
                extent = [-124,-70,18.0,50.0]
                central_lon = -97.6
                central_lat = 35.4
            elif self.plot_info_dict['vx_mask'] == 'alaska':
                extent = [-180,-110,45.0,75.0]
                central_lon = -145
                central_lat = 60
            myproj=ccrs.LambertConformal(central_longitude=central_lon,
                                         central_latitude=central_lat,
                                         false_easting=0.0,
                                         false_northing=0.0,
                                         globe=None)
            ax1 = fig.add_subplot(gs[0], projection=myproj)
            ax1.set_extent(extent)
            ax1.add_feature(cfeature.COASTLINE.with_scale('50m'),
                            zorder=2, linewidth=1)
            ax1.add_feature(cfeature.BORDERS.with_scale('50m'),
                            zorder=2, linewidth=1)
            ax1.add_feature(cfeature.STATES.with_scale('50m'),
                            zorder=2, linewidth=1)
            CF1 = ax1.contourf(x, y, nohrsc_ASNOW_surface,
                               transform=ccrs.PlateCarree(),
                               levels=clevs, norm=norm,
                               cmap=cmap, extend='max')
            CF1.cmap.set_over(cmap_under_color)
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
            cbar.ax.set_xlabel(f'Total Snowfall ({var_units})',
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
            self.logger.info(f"Saving image as {DATA_png_name}")
            plt.savefig(DATA_png_name)
            plt.clf()
            plt.close('all')
            gda_util.copy_file(DATA_png_name, COMOUT_png_name)
        DATA_gif_name = DATA_png_name.replace('.png', '.gif')
        COMOUT_gif_name = COMOUT_png_name.replace('.png', '.gif')
        if os.path.exists(COMOUT_gif_name):
            gda_util.copy_file(COMOUT_gif_name, DATA_gif_name)
            make_gif = False
        elif os.path.exists(DATA_png_name) \
                and not os.path.exists(DATA_gif_name):
            make_gif = True
        if make_gif:
            # Convert png to gif, if possible
            check_convert = subprocess.run(
                ['which', 'convert'], stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if check_convert.returncode == 0:
                self.logger.info(f"Converting {DATA_png_name} to "
                                 +f"{DATA_gif_name}")
                run_convert = subprocess.run(
                    ['convert', DATA_png_name, DATA_gif_name]
                )
                gda_util.copy_file(DATA_gif_name, COMOUT_gif_name)
            else:
                self.logger.warning("convert executable not in PATH")

def main():
    # Need settings
    INPUT_DIR = os.environ['HOME']
    DATA_OUTPUT_DIR = os.environ['HOME']
    COMOUT_OUTPUT_DIR = os.environ['HOME']
    LOGO_DIR = os.environ['HOME']
    DATE_INFO_DICT = {
        'date_type': 'DATE_TYPE',
        'start_date': 'START_DATE',
        'end_date': 'END_DATE',
        'valid_hr_start': 'VALID_HR_START',
        'valid_hr_end': 'VALID_HR_END',
        'valid_hr_inc': 'VALID_HR_INC',
    }
    PLOT_INFO_DICT = {
        'line_type': 'LINE_TYPE',
        'stat': 'STAT',
        'vx_mask': 'VX_MASK',
        'obs_var_name': 'OBS_VAR_NAME',
        'obs_var_level': 'OBS_VAR_LEVEL',
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
    p = NOHRSCSpatialMap(logger, INPUT_DIR, DATA_OUTPUT_DIR, COMOUT_OUTPUT_DIR,
                         DATE_INFO_DICT, PLOT_INFO_DICT, LOGO_DIR)
    p.make_nohrsc_spatial_map()


if __name__ == "__main__":
    main()
