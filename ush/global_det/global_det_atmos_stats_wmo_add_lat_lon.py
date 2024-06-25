#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_wmo_add_lat_lon.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This gather the GridStat stat files and puts them in one
          file in the WMO required format for doma
Run By: Individual job scripts
'''

import sys
import os
import netCDF4 as netcdf
import numpy as np
import pandas as pd
import global_det_atmos_util as gda_util

# Read in environment variables
tmp_regriddataplane_file = os.environ['tmp_regriddataplane_file']

print("BEGIN: "+os.path.basename(__file__))

if os.path.exists(tmp_regriddataplane_file):
    print(f"Adding metadata to lat-lon in {tmp_regriddataplane_file}")
    tmp_regriddataplane = netcdf.Dataset(tmp_regriddataplane_file, 'a')
    lat = tmp_regriddataplane.variables['lat']
    lon = tmp_regriddataplane.variables['lon']
    elv = tmp_regriddataplane.variables['ELV']
    for k in ['coordinates', 'name', 'level', 'init_time',
              'init_time_ut', 'valid_time', 'valid_time_ut']:
        if k == 'name':
            lat.setncatts({k: lat.getncattr('long_name')})
            lon.setncatts({k: lon.getncattr('long_name')})
        else:
            lat.setncatts({k: elv.getncattr(k)})
            lon.setncatts({k: elv.getncattr(k)})
    tmp_regriddataplane.close()
else:
    print(f"NOTE: {tmp_regriddataplane_file} does not exist")

print("END: "+os.path.basename(__file__))
