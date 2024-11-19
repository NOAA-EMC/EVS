#!/usr/bin/env python3
'''
Name: subseasonal_stats_grid2grid_create_days6_10_anomaly.py
Contact(s): Shannon Shields
Abstract: This script is run by subseasonal_stats_grid2grid_create_days6_10_
          reformat_job_scripts.py in ush/subseasonal.
          This script is used to create anomaly
          data from MET grid_stat netCDF output.
'''

import os
import sys
import numpy as np
import glob
import netCDF4 as netcdf
import datetime
import subseasonal_util as sub_util

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
MODEL = os.environ['MODEL']
D6_10START = os.environ['D6_10START']
DATE = os.environ['DATE']
var1_name = os.environ['var1_name']
var1_levels = os.environ['var1_levels']
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end']
valid_hr_inc = os.environ['valid_hr_inc']
fhr_list = os.environ['CORRECT_LEAD_SEQ'].split(',')
job_num_work_dir = os.environ['job_num_work_dir']

# Check variable settings
if ' ' in var1_levels or ',' in var1_levels:
    print("ERROR: Cannot accept list of levels")
    sys.exit(1)

# Set variable to make anomalies
var_level = f"{var1_name}_{var1_levels}"
output_var_level = f"{var1_name}_ANOM_{var1_levels}"

# Create fcst and obs anomaly data
STARTDATE_dt = datetime.datetime.strptime(
    D6_10START+valid_hr_start, '%Y%m%d%H'
)
ENDDATE_dt = datetime.datetime.strptime(
    DATE+valid_hr_end, '%Y%m%d%H'
)
fhr_start = int(fhr_list[0])
fhr_end = int(fhr_list[-1])
valid_date_dt = STARTDATE_dt
fhr = fhr_start
while valid_date_dt <= ENDDATE_dt and fhr <= fhr_end:
    # Set full paths for dates
    full_path_job_num_work_dir = os.path.join(
        job_num_work_dir, RUN+'.'
        +ENDDATE_dt.strftime('%Y%m%d'),
        MODEL, VERIF_CASE
    )
    full_path_DATA = os.path.join(
        DATA, VERIF_CASE+'_'+STEP, 'METplus_output',
        RUN+'.'+ENDDATE_dt.strftime('%Y%m%d'),
        MODEL, VERIF_CASE
    )
    init_date_dt = valid_date_dt - datetime.timedelta(hours=fhr)
    input_file_name =  (
        f"grid_stat_{VERIF_TYPE}_{job_name}_{str(fhr).zfill(2)}0000L_"
        +f"{valid_date_dt:%Y%m%d_%H}0000V_pairs.nc"
    )
    # Check possible input files
    check_input_file_list = [
        os.path.join(full_path_job_num_work_dir, input_file_name),
        os.path.join(full_path_DATA, input_file_name)
    ]
    found_input = False
    for check_input_file in check_input_file_list:
        if os.path.exists(check_input_file):
            input_file = check_input_file
            found_input = True
            break
    # Set output file
    output_file = os.path.join(
        full_path_job_num_work_dir, 'anomaly_'
        +VERIF_TYPE+'_'+job_name+'_init'
        +init_date_dt.strftime('%Y%m%d%H')+'_'
        +'fhr'+str(fhr).zfill(3)+'.nc'
    )
    output_file_DATA = os.path.join(
        full_path_DATA, output_file.rpartition('/')[2]
    )
    if found_input:
        print("\nInput file: "+input_file)
        input_file_data = netcdf.Dataset(input_file)
        input_file_data_var_list = list(input_file_data.variables.keys())
        climo_var_level = 'climo_var_hold'
        for input_var in input_file_data_var_list:
            if 'CLIMO_MEAN_'+var_level in input_var:
                climo_var_level = input_var
        if not climo_var_level in input_file_data_var_list:
            print("WARNING: "+input_file+" does not contain any "
                  +"climo variable cannot make anomaly data")
        else:
            print("Output File: "+output_file)
            if not os.path.exists(full_path_job_num_work_dir):
                os.makedirs(full_path_job_num_work_dir)
            if os.path.exists(output_file):
                os.remove(output_file)
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
            for data_name in ['FCST', 'OBS']:
                input_var_level = 'input_var_hold'
                for input_var in input_file_data_var_list:
                    if data_name+'_'+var_level in input_var:
                        input_var_level = input_var
                if input_var_level in input_file_data_var_list:
                    write_data_name_var = output_file_data.createVariable(
                        data_name+'_'+output_var_level,
                        input_file_data.variables[input_var_level].datatype,
                        input_file_data.variables[input_var_level].dimensions
                    )
                    for k in \
                            input_file_data.variables[input_var_level]\
                            .ncattrs():
                        if k == 'name':
                            write_data_name_var.setncatts(
                                {k: data_name+'_'+output_var_level}
                            )
                        elif k == 'long_name':
                            write_data_name_var.setncatts(
                                {k: input_file_data.variables[input_var_level]\
                                 .getncattr(k).replace(' at', ' Anomaly at')}
                            )
                        else:
                            write_data_name_var.setncatts(
                                {k: input_file_data.variables[input_var_level]\
                                 .getncattr(k)}
                            )
                        write_data_name_var[:] = (
                            input_file_data.variables[input_var_level][:]
                            -
                            input_file_data.variables[climo_var_level][:]
                        )
                else:
                    print("WARNING: "+input_file+" does not contain "
                          +data_name+" variable, cannot make anomaly data")
            output_file_data.close()
            input_file_data.close()
    else:
        print("\nWARNING: "+input_file+" does not exist")
    valid_date_dt = valid_date_dt + datetime.timedelta(hours=int(valid_hr_inc))
    fhr+=int(valid_hr_inc)
    
print("END: "+os.path.basename(__file__))
