#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_grid2grid_create_wind_shear.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script is used to create wind shear
          data from MET grid_stat netCDF output.
Run By: individual statistics job scripts generated through
        ush/global_det/global_det_atmos_plots_grid2grid_create_job_scripts.py
'''

import os
import numpy as np
import glob
import netCDF4 as netcdf
import datetime
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
COMOUT = os.environ['COMOUT']
COMIN = os.environ['COMIN']
SENDCOM = os.environ['SENDCOM']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
VERIF_TYPE = os.environ['VERIF_TYPE']
job_name = os.environ['job_name']
MODEL = os.environ['MODEL']
DATE = os.environ['DATE']
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end']
valid_hr_inc = os.environ['valid_hr_inc']
fhr_list = os.environ['fhr_list'].split(', ')
#fhr_start = os.environ['fhr_start']
#fhr_end = os.environ['fhr_end']
#fhr_inc = os.environ['fhr_inc']
job_num_work_dir = os.environ['job_num_work_dir']
# Needed netCDF variables
req_var_level_list = ['FCST_UGRD_P850_FULL', 'OBS_UGRD_P850_FULL',
                      'FCST_UGRD_P200_FULL', 'OBS_UGRD_P200_FULL',
                      'FCST_VGRD_P850_FULL', 'OBS_VGRD_P850_FULL',
                      'FCST_VGRD_P200_FULL', 'OBS_VGRD_P200_FULL']
output_var_level = 'WNDSHR_P850_P200'

# Create fcst and obs wind shear data
STARTDATE_dt = datetime.datetime.strptime(
    DATE+valid_hr_start, '%Y%m%d%H'
)
ENDDATE_dt = datetime.datetime.strptime(
    DATE+valid_hr_end, '%Y%m%d%H'
)
valid_date_dt = STARTDATE_dt
while valid_date_dt <= ENDDATE_dt:
    # Set full paths for dates
    full_path_job_num_work_dir = os.path.join(
        job_num_work_dir, f"{RUN}.{valid_date_dt:%Y%m%d}", MODEL, VERIF_CASE
    )
    full_path_DATA = os.path.join(
        DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',
        f"{RUN}.{valid_date_dt:%Y%m%d}", MODEL, VERIF_CASE
    )
    full_path_COMIN = os.path.join(
        COMIN, STEP, COMPONENT, f"{RUN}.{valid_date_dt:%Y%m%d}",
        MODEL, VERIF_CASE
    )
    full_path_COMOUT = os.path.join(
        COMOUT, f"{RUN}.{valid_date_dt:%Y%m%d}", MODEL, VERIF_CASE
    )
    for fhr_str in fhr_list:
        fhr = int(fhr_str)
        init_date_dt = valid_date_dt - datetime.timedelta(hours=fhr)
        input_file_name =  (
            f"grid_stat_{VERIF_TYPE}_{job_name}_{str(fhr).zfill(2)}0000L_"
            +f"{valid_date_dt:%Y%m%d_%H}0000V_pairs.nc"
        )
        # Check possible input files
        check_input_file_list = [
            os.path.join(full_path_job_num_work_dir, input_file_name),
            os.path.join(full_path_DATA, input_file_name),
            os.path.join(full_path_COMOUT, input_file_name),
            os.path.join(full_path_COMIN, input_file_name)
        ]
        found_input = False
        for check_input_file in check_input_file_list:
            if os.path.exists(check_input_file):
                input_file = check_input_file
                found_input = True
                break
        # Set output file
        output_file = os.path.join(
            full_path_job_num_work_dir, f"wind_shear_{VERIF_TYPE}_{job_name}_"
            +f"init{init_date_dt:%Y%m%d%H}_fhr{str(fhr).zfill(3)}.nc"
        )
        output_file_DATA = os.path.join(
            full_path_DATA, output_file.rpartition('/')[2]
        )
        output_file_COMOUT = os.path.join(
            full_path_COMOUT, output_file.rpartition('/')[2]
        )
        # Check input and output files
        if os.path.exists(output_file_COMOUT):
            print(f"COMOUT Output File exists: {output_file_COMOUT}")
            make_wind_shear_output_file = False
            gda_util.copy_file(output_file_COMOUT, output_file_DATA)
        else:
            make_wind_shear_output_file = True
        if found_input and make_wind_shear_output_file:
            input_file_data = netcdf.Dataset(input_file)
            input_file_data_var_list = list(input_file_data.variables.keys())
            if all(v in input_file_data_var_list \
                   for v in req_var_level_list):
               make_wind_shear_output_file = True
            else:
                for req_var_level in req_var_level_list:
                    if req_var_level not in input_file_data_var_list:
                        print("NOTE: Cannot make wind shear file "
                              +f"{output_file} - {input_file} does "
                              +f"not contain variable {req_var_level}")
                make_wind_shear_output_file = False
            input_file_data.close()
        else:
            print("NOTE: Cannot make wind shear file "
                  +f"{output_file} - input file options "
                  +f"{', '.join(check_input_file_list)} "
                  +"do not exist")
            make_wind_shear_output_file = False
        if make_wind_shear_output_file:
            print(f"\nInput file: {input_file}")
            input_file_data = netcdf.Dataset(input_file)
            print(f"Output File: {output_file}")
            if not os.path.exists(full_path_job_num_work_dir):
                gda_util.make_dir(full_path_job_num_work_dir)
            output_file_data = netcdf.Dataset(output_file, 'w',
                                              format='NETCDF3_CLASSIC')
            for attr in input_file_data.ncattrs():
                if attr == 'MET_tool':
                    continue
                elif attr == 'FileOrigins':
                    output_file_data.setncattr(
                        attr, 'Generated from '+__file__
                    )
                else:
                    output_file_data.setncattr(
                        attr, input_file_data.getncattr(attr)
                    )
            for dim in list(input_file_data.dimensions.keys()):
                output_file_data.createDimension(
                    dim, len(input_file_data.dimensions[dim])
                )
            for input_var_name in ['lat', 'lon']:
                write_data_name_var = output_file_data.createVariable(
                    input_var_name,
                    input_file_data.variables[input_var_name].datatype,
                    input_file_data.variables[input_var_name].dimensions
                )
                for k in (input_file_data.variables[input_var_name].ncattrs()):
                    write_data_name_var.setncatts(
                        {k: input_file_data.variables[input_var_name].getncattr(k)}
                    )
                write_data_name_var[:] = (
                    input_file_data.variables[input_var_name][:]
                )
            for data_name in ['FCST', 'OBS']:
                data_name_ugrd850 = (
                    input_file_data.variables[data_name+'_UGRD_P850_FULL'][:]
                )
                data_name_vgrd850 = (
                    input_file_data.variables[data_name+'_VGRD_P850_FULL'][:]
                )
                data_name_ugrd200 = (
                    input_file_data.variables[data_name+'_UGRD_P200_FULL'][:]
                )
                data_name_vgrd200 = (
                    input_file_data.variables[data_name+'_VGRD_P200_FULL'][:]
                )
                data_name_wind850 = np.sqrt(
                    data_name_ugrd850**2 + data_name_vgrd850**2
                )
                data_name_wind200 = np.sqrt(
                    data_name_ugrd200**2 + data_name_vgrd200**2
                )
                write_data_name_var = output_file_data.createVariable(
                    data_name+'_'+output_var_level,
                    input_file_data.variables[data_name+'_UGRD_P850_FULL']\
                    .datatype,
                    input_file_data.variables[data_name+'_UGRD_P850_FULL']\
                    .dimensions
                )
                for k \
                        in (input_file_data.variables\
                            [data_name+'_UGRD_P850_FULL']\
                            .ncattrs()):
                    if k == 'name':
                        write_data_name_var.setncatts(
                            {k: data_name+'_'+output_var_level}
                        )
                    elif k == 'long_name':
                        write_data_name_var.setncatts(
                            {k: 'Wind Shear for P850-P200'}
                        )
                    elif k == 'level':
                        write_data_name_var.setncatts(
                            {k: 'P850-P200'}
                        )
                    else:
                        write_data_name_var.setncatts(
                            {k: input_file_data.variables\
                             [data_name+'_UGRD_P850_FULL']\
                             .getncattr(k)}
                        )
                write_data_name_var[:] = (data_name_wind200 - data_name_wind850)
            output_file_data.close()
            input_file_data.close()
            if gda_util.check_file_exists_size(output_file):
                if SENDCOM == 'YES':
                    gda_util.copy_file(output_file, output_file_COMOUT)
    valid_date_dt = valid_date_dt + datetime.timedelta(hours=int(valid_hr_inc))

print("END: "+os.path.basename(__file__))
