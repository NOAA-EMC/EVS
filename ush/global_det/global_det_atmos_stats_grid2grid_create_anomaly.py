#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_grid2grid_create_anomaly
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script is used to create anomaly
          data from MET grid_stat netCDF output.
Run By: individual statistics job scripts generated through
        ush/global_det/global_det_atmos_stats_grid2grid_create_job_scripts.py
'''

import os
import sys
import numpy as np
import glob
import netCDF4 as netcdf
import datetime
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
COMOUT = os.environ['COMOUT']
SENDCOM = os.environ['SENDCOM']
RUN = os.environ['RUN']
NET = os.environ['NET']
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

# Process run time agruments
if len(sys.argv) != 3:
    print("FATAL ERROR: Not given correct number of run time agruments..."
          +os.path.basename(__file__)+" VARNAME_VARLEVEL FILE_FORMAT")
    sys.exit(1)
else:
    if '_' not in sys.argv[1]:
        print("FATAL ERROR: variable and level runtime agrument formated "
              +"incorrectly, be sure to separate variable and level with "
              +"an underscore (_), example HGT_P500")
        sys.exit(1)
    else:
        var_level = sys.argv[1]
        print("Using var_level = "+var_level)
    file_format = sys.argv[2]
output_var_level = (var_level.split('_')[0]+'_ANOM_'
                    +var_level.split('_')[-1])

# Create fcst and obs anomaly data
STARTDATE_dt = datetime.datetime.strptime(
    DATE+valid_hr_start, '%Y%m%d%H'
)
ENDDATE_dt = datetime.datetime.strptime(
    DATE+valid_hr_end, '%Y%m%d%H'
)
valid_date_dt = STARTDATE_dt
while valid_date_dt <= ENDDATE_dt:
    for fhr_str in fhr_list:
        fhr = int(fhr_str)
        init_date_dt = valid_date_dt - datetime.timedelta(hours=fhr)
        input_file = gda_util.format_filler(
            file_format, valid_date_dt, init_date_dt, str(fhr), {}
        )
        output_DATA_file = os.path.join(
            DATA, VERIF_CASE+'_'+STEP, 'METplus_output',
            RUN+'.'+valid_date_dt.strftime('%Y%m%d'),
            MODEL, VERIF_CASE, 'anomaly_'+VERIF_TYPE+'_'
            +job_name+'_init'+init_date_dt.strftime('%Y%m%d%H')+'_'
            +'fhr'+str(fhr).zfill(3)+'.nc'
        )
        output_COMOUT_file = os.path.join(
            COMOUT, RUN+'.'+valid_date_dt.strftime('%Y%m%d'),
            MODEL, VERIF_CASE, 'anomaly_'+VERIF_TYPE+'_'
            +job_name+'_init'+init_date_dt.strftime('%Y%m%d%H')+'_'
            +'fhr'+str(fhr).zfill(3)+'.nc'
        )
        if gda_util.check_file_exists_size(input_file):
            input_file_data = netcdf.Dataset(input_file)
            input_file_data_var_list = list(input_file_data.variables.keys())
            climo_var_level = 'climo_var_hold'
            for input_var in input_file_data_var_list:
                if 'CLIMO_MEAN_'+var_level in input_var:
                    climo_var_level = input_var
            if climo_var_level in input_file_data_var_list:
                if os.path.exists(output_COMOUT_file):
                    gda_util.copy_file(output_COMOUT_file, output_DATA_file)
                    make_anomaly_output_file = False
                else:
                    if not os.path.exists(output_DATA_file):
                        make_anomaly_output_file = True
                    else:
                        make_anomaly_output_file = False
                        print(f"DATA Output File exists: {output_DATA_file}")
                        if SENDCOM == 'YES' \
                                and gda_util.check_file_exists_size(
                                    output_DATA_file
                                ):
                            gda_util.copy_file(output_DATA_file,
                                               output_COMOUT_file)
            else:
                print(f"NOTE: Cannot make anomaly file {output_DATA_file} - "
                      +f"{input_file} does not contain CLIMO_MEAN_{var_level}")
                make_anomaly_output_file = False
            input_file_data.close()
        else:
           print(f"NOTE: Cannot make anomaly file {output_DATA_file} - "
                 +f"{input_file} does not exist")
           make_anomaly_output_file = False
        if make_anomaly_output_file:
            print(f"\nInput file: {input_file}")
            input_file_data = netcdf.Dataset(input_file)
            print(f"DATA Output File: {output_DATA_file}")
            print(f"COMOUT Output File: {output_COMOUT_file}")
            output_file_data = netcdf.Dataset(output_DATA_file, 'w',
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
                for k in input_file_data.variables[input_var_name].ncattrs():
                    write_data_name_var.setncatts(
                        {k: input_file_data.variables[input_var_name]\
                            .getncattr(k)}
                    )
                write_data_name_var[:] = (
                    input_file_data.variables[input_var_name][:]
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
                    print(f"NOTE: No {data_name} anomaly data for "
                          +f"{output_DATA_file} - {input_file} does not "
                          +f"contain {data_name}_{var_level}")
            output_file_data.close()
            input_file_data.close()
            if SENDCOM == 'YES' \
                    and gda_util.check_file_exists_size(output_DATA_file):
                gda_util.copy_file(output_DATA_file, output_COMOUT_file)
    valid_date_dt = valid_date_dt + datetime.timedelta(hours=int(valid_hr_inc))

print("END: "+os.path.basename(__file__))
