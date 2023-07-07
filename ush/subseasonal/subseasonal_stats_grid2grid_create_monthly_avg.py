#!/usr/bin/env python3
'''
Name: subseasonal_stats_grid2grid_create_monthly_avg.py
Contact(s): Shannon Shields
Abstract: This script is used to create monthly average
          for variable from netCDF output
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
MONTHLYSTART = os.environ['MONTHLYSTART']
DATE = os.environ['DATE']
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end'] 
valid_hr_inc = os.environ['valid_hr_inc']
fhr_list = os.environ['fhr_list'].split(',')
fhr_inc = '12'
#fhr_end = os.environ['fhr_end']
#fhr_inc = os.environ['fhr_inc']

# Process run time arguments
if len(sys.argv) != 4:
    print("ERROR: Not given correct number of run time arguments..."
          +os.path.basename(__file__)+" VARNAME_VARLEVEL DATAROOT_FILE_FORMAT "
          +"COMIN_FILE_FORMAT")
    sys.exit(1)
else:
    if '_' not in sys.argv[1]:
        print("ERROR: variable and level runtime agrument formatted "
              +"incorrectly, be sure to separate variable and level with "
              +"an underscore (_), example HGT_P500")
        sys.exit(1)
    else:
        var_level = sys.argv[1]
        print("Using var_level = "+var_level)
    DATAROOT_file_format = sys.argv[2]
    COMIN_file_format = sys.argv[3]

# Set input and output directories
output_dir = os.path.join(DATA, VERIF_CASE+'_'+STEP, 'METplus_output',
                          RUN+'.'+DATE)

# Create monthly average files
print("\nCreating monthly average files")
valid_hr = int(valid_hr_start)
while valid_hr <= int(valid_hr_end):
    if job_name == 'MonthlyAvg_GeoHeightAnom':
        if int(valid_hr) % 12 != 0 :
            valid_hr+=int(valid_hr_inc)
            continue
    monthly_avg_valid_end = datetime.datetime.strptime(DATE+str(valid_hr),
                                                       '%Y%m%d%H')
    if job_name == 'MonthlyAvg_GeoHeightAnom':
        monthly_avg_valid_start = (monthly_avg_valid_end
                                  - datetime.timedelta(hours=156))
    else:
        monthly_avg_valid_start = datetime.datetime.strptime(MONTHLYSTART
                                                             +str(valid_hr),
                                                             '%Y%m%d%H')
    monthly_avg_day_end = int(fhr_list[-1])/24
    monthly_avg_day_start = 30
    monthly_avg_day = monthly_avg_day_start
    while monthly_avg_day <= monthly_avg_day_end:
        monthly_avg_day_fhr_end = int(monthly_avg_day * 24)
        monthly_avg_file_list = []
        if job_name == 'MonthlyAvg_GeoHeightAnom':
            monthly_avg_day_fhr_start = monthly_avg_day_fhr_end - 156
        else:
            monthly_avg_day_fhr_start = monthly_avg_day_fhr_end - 720
        monthly_avg_day_init = (monthly_avg_valid_end
                               - datetime.timedelta(days=monthly_avg_day))
        monthly_avg_day_fhr = monthly_avg_day_fhr_start
        output_file = os.path.join(output_dir, MODEL,
                                   VERIF_CASE,
                                   'monthly_avg_'
                                   +VERIF_TYPE+'_'+job_name+'_init'
                                   +monthly_avg_day_init.strftime('%Y%m%d%H')
                                   +'_valid'
                                   +monthly_avg_valid_start\
                                   .strftime('%Y%m%d%H')+'to'
                                   +monthly_avg_valid_end\
                                   .strftime('%Y%m%d%H')+'.nc')
        if os.path.exists(output_file):
            os.remove(output_file)
        monthly_avg_fcst_sum = 0
        monthly_avg_fcst_file_list = []
        monthly_avg_obs_sum = 0
        monthly_avg_obs_file_list = []
        while monthly_avg_day_fhr <= monthly_avg_day_fhr_end:
            monthly_avg_day_fhr_valid = (
                monthly_avg_day_init
                + datetime.timedelta(hours=monthly_avg_day_fhr)
            )
            monthly_avg_day_fhr_DATAROOT_input_file = sub_util.format_filler(
                    DATAROOT_file_format, monthly_avg_day_fhr_valid,
                    monthly_avg_day_init, 
                    str(monthly_avg_day_fhr), {}
            )
            monthly_avg_day_fhr_COMIN_input_file = sub_util.format_filler(
                    COMIN_file_format, monthly_avg_day_fhr_valid,
                    monthly_avg_day_init,
                    str(monthly_avg_day_fhr), {}
            )
            if os.path.exists(monthly_avg_day_fhr_COMIN_input_file):
                monthly_avg_day_fhr_input_file = (
                    monthly_avg_day_fhr_COMIN_input_file)
            else:
                monthly_avg_day_fhr_input_file = (
                    monthly_avg_day_fhr_DATAROOT_input_file
                )
            if os.path.exists(monthly_avg_day_fhr_input_file):
                print("Input file for forecast hour "+str(monthly_avg_day_fhr)
                      +', valid '+str(monthly_avg_day_fhr_valid)
                      +', init '+str(monthly_avg_day_init)+": "
                      +monthly_avg_day_fhr_input_file)
                input_file_data = netcdf.Dataset(monthly_avg_day_fhr_input_file)
                input_file_data_var_list = list(input_file_data.variables.keys())
                fcst_var_level = 'fcst_var_hold'
                obs_var_level = 'obs_var_hold'
                for input_var in input_file_data_var_list:
                    if 'FCST_'+var_level in input_var:
                        fcst_var_level = input_var
                    if 'OBS_'+var_level in input_var:
                        obs_var_level = input_var
                if fcst_var_level in input_file_data_var_list:
                    monthly_avg_fcst_sum = (monthly_avg_fcst_sum +
                                           input_file_data.variables[
                                               fcst_var_level
                                           ][:])
                    monthly_avg_fcst_file_list.append(monthly_avg_day_fhr_input_file)
                if obs_var_level in input_file_data_var_list:
                    monthly_avg_obs_sum = (monthly_avg_obs_sum +
                                          input_file_data.variables[
                                              obs_var_level
                                          ][:])
                    monthly_avg_obs_file_list.append(monthly_avg_day_fhr_input_file)
            else:
                print("No input file for forecast hour "+str(monthly_avg_day_fhr)
                      +', valid '+str(monthly_avg_day_fhr_valid)
                      +', init '+str(monthly_avg_day_init)+" "
                      +monthly_avg_day_fhr_DATAROOT_input_file+" or "
                      +monthly_avg_day_fhr_COMIN_input_file)
            if job_name == 'MonthlyAvg_GeoHeightAnom':
                monthly_avg_day_fhr+=12
            else:
                monthly_avg_day_fhr+=int(fhr_inc)
        if len(monthly_avg_fcst_file_list) >= 49:
            monthly_avg_fcst = (
                monthly_avg_fcst_sum/len(monthly_avg_fcst_file_list)
            )
        if len(monthly_avg_obs_file_list) >= 49:
            monthly_avg_obs = (
                monthly_avg_obs_sum/len(monthly_avg_obs_file_list)
            )
        if job_name == 'MonthlyAvg_GeoHeightAnom':
            expected_nfiles = 14
        else:
            if fhr_inc == '6':
                expected_nfiles = 29
            elif fhr_inc == '12':
                expected_nfiles = 49
        if len(monthly_avg_fcst_file_list) >= expected_nfiles \
                and len(monthly_avg_obs_file_list) >= expected_nfiles:
            print("Output File: "+output_file)
            output_file_data = netcdf.Dataset(output_file, 'w',
                                              format='NETCDF3_CLASSIC')
            for attr in input_file_data.ncattrs():
                if attr == 'FileOrigins':
                    output_file_data.setncattr(
                        attr, 'Monthly Fcst Mean from '
                        +','.join(monthly_avg_fcst_file_list)+';'
                        +'Monthly Obs Mean from '
                        +','.join(monthly_avg_obs_file_list)
                    )
                else:
                    output_file_data.setncattr(
                        attr, input_file_data.getncattr(attr)
                    )
            for dim in list(input_file_data.dimensions.keys()):
                output_file_data.createDimension(
                    dim,
                    len(input_file_data.dimensions[dim])
                )
            for data_name in ['FCST', 'OBS']:
                for input_var in input_file_data_var_list:
                    if data_name+'_'+var_level in input_var:
                        input_var_level = input_var
                write_data_name_var = output_file_data.createVariable(
                    data_name+'_'+var_level+'_MONTHLYAVG',
                    input_file_data.variables[input_var_level]\
                    .datatype,
                    input_file_data.variables[input_var_level]\
                    .dimensions
                )
                k_valid_time = monthly_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                k_valid_time_ut = int(
                    (monthly_avg_valid_end
                     -datetime.datetime.strptime('19700101','%Y%m%d'))\
                    .total_seconds()
                )
                k_init_time = monthly_avg_day_init.strftime('%Y%m%d_%H%M%S')
                k_init_time_ut = int(
                    (monthly_avg_day_init
                     -datetime.datetime.strptime('19700101','%Y%m%d'))\
                    .total_seconds()
                )
                for k \
                        in input_file_data.variables[
                            input_var_level
                        ].ncattrs():
                    if k == 'valid_time':
                        write_data_name_var.setncatts(
                            {k: k_valid_time}
                        )
                    elif k == 'valid_time_ut':
                        write_data_name_var.setncatts(
                            {k: k_valid_time_ut}
                        )
                    elif k == 'init_time' and data_name == 'FCST':
                        write_data_name_var.setncatts(
                            {k: k_init_time}
                        )
                    elif k == 'init_time_ut' and data_name == 'FCST':
                        write_data_name_var.setncatts(
                            {k: k_init_time_ut}
                        )
                    elif k == 'init_time' and data_name == 'OBS':
                        write_data_name_var.setncatts(
                            {k: k_valid_time}
                        )
                    elif k == 'init_time_ut' and data_name == 'OBS':
                        write_data_name_var.setncatts(
                            {k: k_valid_time_ut}
                        )
                    else:
                        write_data_name_var.setncatts(
                            {k: input_file_data.variables[
                                 input_var_level
                             ].getncattr(k)}
                        )
                if data_name == 'FCST':
                    write_data_name_var[:] = monthly_avg_fcst
                elif data_name == 'OBS':
                    write_data_name_var[:] = monthly_avg_obs
            if len(list(output_file_data.variables.keys())) == 0:
                print("No variables in "+output_file+", removing")
                output_file_data.close()
                os.remove(output_file)
            else:
                output_file_data.close()
            input_file_data.close()
        else:
            print("WARNING: Cannot create monthly average file "+output_file+" "
                  +"; need at least "+str(expected_nfiles)+" input files")
        if job_name == 'MonthlyAvg_GeoHeightAnom':
            monthly_avg_day+=1
        else:
            monthly_avg_day+=1
        print("")
    valid_hr+=int(valid_hr_inc)
    
print("END: "+os.path.basename(__file__))
