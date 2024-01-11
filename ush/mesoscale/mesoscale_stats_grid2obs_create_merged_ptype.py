#!/usr/bin/env python3
'''
Program Name: mesoscale_stats_grid2obs_create_merged_ptype.py
Contact(s): Marcel Caron, Mallory Row, Roshan Shrestha
Abstract: This creates a merged precipitation type file used for
          calculating MET MCTC line type.
          1-rain, 2-snow, 3-freezing rain, 4-ice pellets
'''

import os
import sys
import netCDF4 as netcdf
import numpy as np
import datetime
import mesoscale_util as cutil

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
NET = os.environ['NET']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
VERIF_TYPE = os.environ['VERIF_TYPE']
job_name = os.environ['job_name']
MODELNAME = os.environ['MODELNAME']
NEST = os.environ['NEST']
COMINfcst = os.environ['COMINfcst']
MODEL_INPUT_TEMPLATE = os.environ['MODEL_INPUT_TEMPLATE']
VDATE = os.environ['VDATE']
VHOUR= os.environ['VHOUR']
fhr = os.environ['FHR']
#fhr = os.environ['FHR_START']
fhr = int(fhr)

# Create merged ptype data
valid_date_dt = datetime.datetime.strptime(
    VDATE+VHOUR, '%Y%m%d%H'
)
init_date_dt = valid_date_dt - datetime.timedelta(hours=fhr)
output_dir = os.path.join(DATA, VERIF_CASE, 'data', MODELNAME, 'merged_ptype')
output_merged_ptype_file = os.path.join(
    output_dir, 'merged_ptype_'+VERIF_TYPE+'_'+NEST+'_'+job_name+'_'
    +'init'+init_date_dt.strftime('%Y%m%d%H')
    +'_fhr'+str(fhr).zfill(3)+'.nc'
)

# Create temp nc files for reading
regrid_dir = os.path.join(
    DATA, VERIF_CASE, 'METplus_output', VERIF_TYPE, 'regrid_data_plane', f'{MODELNAME}.{VDATE}'
)
regrid_fname = (f'regrid_data_plane_{MODELNAME}_t{VHOUR}z_{VERIF_TYPE}_{NEST}_'
              + f'{job_name}_fhr{str(fhr).zfill(2)}.nc')
input_nc_file = os.path.join(regrid_dir, regrid_fname)
if os.path.exists(input_nc_file):
    input_data = netcdf.Dataset(input_nc_file)
    ptypes = [
        'CRAIN', 'CSNOW', 'CFRZR', 'CICEP'
    ]
    all_input_ptype_files_exist = True
    for ptype in ptypes:
        if not ptype in input_data.variables:
            print("WARNING: "+ptype+" does not exist in "+input_grib2_file)
            all_input_ptype_files_exist = False
    if all_input_ptype_files_exist:
        print("\nInput File: "+input_nc_file)

        input_crain = input_data.variables['CRAIN'][:]
        input_csnow = input_data.variables['CSNOW'][:]
        input_cfrzr = input_data.variables['CFRZR'][:]
        input_cicep = input_data.variables['CICEP'][:]
        input_lats = input_data.variables['lat'][:]
        input_lons = input_data.variables['lon'][:]
        print("Output Merged Ptype File: "+output_merged_ptype_file)
        if os.path.exists(output_merged_ptype_file):
            os.remove(output_merged_ptype_file)
        merged_ptype = np.zeros_like(input_crain)
        for x in range(len(input_crain[:,0])):
            for y in range(len(input_crain[0,:])):
                crain_xy = input_crain[x,y]
                csnow_xy = input_csnow[x,y]
                cfrzr_xy = input_cfrzr[x,y]
                cicep_xy = input_cicep[x,y]
                ptype_xy_list = [crain_xy, csnow_xy, cfrzr_xy, cicep_xy]
                if ptype_xy_list.count(1.0) == 1: # one ptype
                    if crain_xy == 1.0:
                        merged_ptype[x,y] = 1
                    elif csnow_xy == 1.0:
                        merged_ptype[x,y] = 2
                    elif cfrzr_xy == 1.0:
                        merged_ptype[x,y] = 3
                    elif cicep_xy == 1.0:
                        merged_ptype[x,y] = 4
                elif ptype_xy_list.count('1.0') > 1: # more than ptype
                    print("more than 1 ptype")
        output_merged_ptype_data = netcdf.Dataset(
            output_merged_ptype_file, 'w', format='NETCDF3_CLASSIC'
        )

        for attr in input_data.ncattrs():
            output_merged_ptype_data.setncattr(
                attr, input_data.getncattr(attr)
            )
        for dim in list(input_data.dimensions.keys()):
            output_merged_ptype_data.createDimension(
                dim, len(input_data.dimensions[dim])
            )
        var_data = {'lat': input_lats, 'lon': input_lons}
        for var in ['lat', 'lon']:
            output_merged_var = output_merged_ptype_data.createVariable(
                var, input_data.variables[var].datatype,
                input_data.variables[var].dimensions
            )
            for k in input_data.variables[var].ncattrs():
                output_merged_var.setncatts(
                    {k: input_data.variables[var].getncattr(k)}
                )
            output_merged_var[:] = var_data[var][:]
        output_merged_var = output_merged_ptype_data.createVariable(
            'PTYPE', input_data.variables[var].datatype,
            input_data.variables[var].dimensions
        )
        var = 'CRAIN'
        for k in input_data.variables[var].ncattrs():
            if k in ['name']:
                output_merged_var.setncatts({k: 'PTYPE_L0'})
            elif k == 'long_name':
                output_merged_var.setncatts({k: 'Precipitation Type'})
            else:
                output_merged_var.setncatts(
                    {k: input_data.variables[var].getncattr(k)}
                )

        output_merged_var[:] = merged_ptype[:]
        output_merged_ptype_data.close()

        input_data.close()
else:
    print(f"\nWARNING: Missing input files ({input_nc_file}) cannot make"
          + f" output file " + output_merged_ptype_file)

print("END: "+os.path.basename(__file__))
