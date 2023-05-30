#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_grid2grid_create_anomaly
Contact(s): Mallory Row
Abstract: This script is used to create anomaly
          data from MET grid_stat netCDF output
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
fhr_list = os.environ['fhr_list'].split(',')
#fhr_start = os.environ['fhr_start']
#fhr_end = os.environ['fhr_end']
#fhr_inc = os.environ['fhr_inc']

# Process run time agruments
if len(sys.argv) != 3:
    print("ERROR: Not given correct number of run time agruments..."
          +os.path.basename(__file__)+" VARNAME_VARLEVEL FILE_FORMAT")
    sys.exit(1)
else:
    if '_' not in sys.argv[1]:
        print("ERROR: variable and level runtime agrument formated "
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
        if os.path.exists(input_file):
            input_file_data = netcdf.Dataset(input_file)
            input_file_data_var_list = list(input_file_data.variables.keys())
            climo_var_level = 'climo_var_hold'
            for input_var in input_file_data_var_list:
                if 'CLIMO_MEAN_'+var_level in input_var:
                    climo_var_level = input_var
            if climo_var_level in input_file_data_var_list:
                output_dir = os.path.join(DATA, VERIF_CASE+'_'+STEP,
                                         'METplus_output',
                                          RUN+'.'
                                          +valid_date_dt.strftime('%Y%m%d'),
                                          MODEL, VERIF_CASE)
                output_file = os.path.join(output_dir, 'anomaly_'
                                           +VERIF_TYPE+'_'+job_name+'_init'
                                           +init_date_dt.strftime('%Y%m%d%H')+'_'
                                           +'fhr'+str(fhr).zfill(3)+'.nc')
                if not os.path.exists(output_file):
                    make_anomaly_output_file = True
                else:
                    make_anomaly_output_file = False
                    print(f"Output File exists: {output_file}")
            else:
                print(f"WARNING: {input_file} does not contain any "
                      +"climo variable cannot make anomaly data")
                make_anomaly_output_file = False
            input_file_data.close()
        else:
           print(f"\nWARNING: {input_file} does not exist")
           make_anomaly_output_file = False
        if make_anomaly_output_file:
            print("\nInput file: "+input_file)
            input_file_data = netcdf.Dataset(input_file)
            print("Output File: "+output_file)
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
                    print(f"WARNING: {input_file} does not contain "
                          f"{data_name} variable, cannot make anomaly data")
            output_file_data.close()
            input_file_data.close()
    valid_date_dt = valid_date_dt + datetime.timedelta(hours=int(valid_hr_inc))
    
print("END: "+os.path.basename(__file__))
