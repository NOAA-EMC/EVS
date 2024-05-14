#!/usr/bin/env python3
'''
Name: subseasonal_stats_grid2grid_create_days6_10_avg.py
Contact(s): Shannon Shields
Abstract: This script is run by subseasonal_stats_grid2grid_create_job_
          scripts.py in ush/subseasonal.
          This script is used to create Days 6-10 average
          for variable from netCDF output.
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
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end'] 
valid_hr_inc = os.environ['valid_hr_inc']
fhr_list = os.environ['fhr_list'].split(',')
fhr_inc = '12'

# Process run time arguments
if len(sys.argv) != 4:
    print("FATAL ERROR: Not given correct number of run time arguments..."
          +os.path.basename(__file__)+" VARNAME_VARLEVEL DATAROOT_FILE_FORMAT "
          +"COMIN_FILE_FORMAT")
    sys.exit(1)
else:
    if '_' not in sys.argv[1]:
        print("FATAL ERROR: variable and level runtime argument formatted "
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

# Create Days 6-10 average files
print("\nCreating Days 6-10 average files")
valid_hr = int(valid_hr_start)
while valid_hr <= int(valid_hr_end):
    days_avg_valid_end = datetime.datetime.strptime(DATE+str(valid_hr),
                                                    '%Y%m%d%H')
    days_avg_valid_start = datetime.datetime.strptime(D6_10START
                                                      +str(valid_hr),
                                                      '%Y%m%d%H')
    days_avg_day_end = int(fhr_list[-1])/24
    days_avg_day_start = 10
    days_avg_day = days_avg_day_start
    while days_avg_day <= days_avg_day_end:
        days_avg_day_fhr_end = int(days_avg_day * 24)
        days_avg_file_list = []
        days_avg_day_fhr_start = days_avg_day_fhr_end - 120
        days_avg_day_init = (days_avg_valid_end
                            - datetime.timedelta(days=days_avg_day))
        days_avg_day_fhr = days_avg_day_fhr_start
        output_file = os.path.join(output_dir, MODEL,
                                   VERIF_CASE,
                                   'days6_10_avg_'
                                   +VERIF_TYPE+'_'+job_name+'_init'
                                   +days_avg_day_init.strftime('%Y%m%d%H')
                                   +'_valid'
                                   +days_avg_valid_start\
                                   .strftime('%Y%m%d%H')+'to'
                                   +days_avg_valid_end\
                                   .strftime('%Y%m%d%H')+'.nc')
        if os.path.exists(output_file):
            os.remove(output_file)
        days_avg_fcst_sum = 0
        days_avg_fcst_file_list = []
        days_avg_obs_sum = 0
        days_avg_obs_file_list = []
        days_avg_climo_sum = 0
        days_avg_climo_file_list = []
        while days_avg_day_fhr <= days_avg_day_fhr_end:
            days_avg_day_fhr_valid = (
                days_avg_day_init
                + datetime.timedelta(hours=days_avg_day_fhr)
            )
            days_avg_day_fhr_DATAROOT_input_file = sub_util.format_filler(
                    DATAROOT_file_format, days_avg_day_fhr_valid,
                    days_avg_day_init, 
                    str(days_avg_day_fhr), {}
            )
            days_avg_day_fhr_COMIN_input_file = sub_util.format_filler(
                    COMIN_file_format, days_avg_day_fhr_valid,
                    days_avg_day_init,
                    str(days_avg_day_fhr), {}
            )
            if os.path.exists(days_avg_day_fhr_COMIN_input_file):
                days_avg_day_fhr_input_file = (
                    days_avg_day_fhr_COMIN_input_file)
            else:
                days_avg_day_fhr_input_file = (
                    days_avg_day_fhr_DATAROOT_input_file
                )
            if os.path.exists(days_avg_day_fhr_input_file):
                print("Input file for forecast hour "+str(days_avg_day_fhr)
                      +', valid '+str(days_avg_day_fhr_valid)
                      +', init '+str(days_avg_day_init)+": "
                      +days_avg_day_fhr_input_file)
                input_file_data = netcdf.Dataset(days_avg_day_fhr_input_file)
                input_file_data_var_list = list(input_file_data.variables.keys())
                fcst_var_level = 'fcst_var_hold'
                obs_var_level = 'obs_var_hold'
                climo_var_level = 'climo_var_hold'
                for input_var in input_file_data_var_list:
                    if 'FCST_'+var_level in input_var:
                        fcst_var_level = input_var
                    if 'OBS_'+var_level in input_var:
                        obs_var_level = input_var
                    if job_name in ['Days6_10Avg_GeoHeight',
                                    'Days6_10Avg_Temp2m']:
                        if 'CLIMO_MEAN_'+var_level in input_var:
                            climo_var_level = input_var
                if fcst_var_level in input_file_data_var_list:
                    days_avg_fcst_sum = (days_avg_fcst_sum +
                                        input_file_data.variables[
                                            fcst_var_level
                                        ][:])
                    days_avg_fcst_file_list.append(days_avg_day_fhr_input_file)
                if obs_var_level in input_file_data_var_list:
                    days_avg_obs_sum = (days_avg_obs_sum +
                                       input_file_data.variables[
                                           obs_var_level
                                       ][:])
                    days_avg_obs_file_list.append(days_avg_day_fhr_input_file)
                if job_name in ['Days6_10Avg_GeoHeight',
                                'Days6_10Avg_Temp2m']:
                    if climo_var_level in input_file_data_var_list:
                        days_avg_climo_sum = (days_avg_climo_sum +
                                             input_file_data.variables[
                                                 climo_var_level
                                             ][:])
                        days_avg_climo_file_list.append(days_avg_day_fhr_input_file)
            else:
                print("No input file for forecast hour "+str(days_avg_day_fhr)
                      +', valid '+str(days_avg_day_fhr_valid)
                      +', init '+str(days_avg_day_init)+" "
                      +days_avg_day_fhr_DATAROOT_input_file+" or "
                      +days_avg_day_fhr_COMIN_input_file)
            days_avg_day_fhr+=int(fhr_inc)
        if len(days_avg_fcst_file_list) >= 9:
            days_avg_fcst = (
                days_avg_fcst_sum/len(days_avg_fcst_file_list)
            )
        if len(days_avg_obs_file_list) >= 9:
            days_avg_obs = (
                days_avg_obs_sum/len(days_avg_obs_file_list)
            )
        if job_name in ['Days6_10Avg_GeoHeight',
                        'Days6_10Avg_Temp2m']:
            if len(days_avg_climo_file_list) >= 9:
                days_avg_climo = (
                    days_avg_climo_sum/len(days_avg_climo_file_list)
                )
        if fhr_inc == '12':
            expected_nfiles = 9
        if len(days_avg_fcst_file_list) >= expected_nfiles \
                and len(days_avg_obs_file_list) >= expected_nfiles:
            print("Output File: "+output_file)
            output_file_data = netcdf.Dataset(output_file, 'w',
                                              format='NETCDF3_CLASSIC')
            for attr in input_file_data.ncattrs():
                if attr == 'FileOrigins':
                    if job_name in ['Days6_10Avg_GeoHeight',
                                    'Days6_10Avg_Temp2m']:
                        output_file_data.setncattr(
                            attr, 'Days 6-10 Fcst Mean from '
                            +','.join(days_avg_fcst_file_list)+';'
                            +'Days 6-10 Obs Mean from '
                            +','.join(days_avg_obs_file_list)+';'
                            +'Days 6-10 Climo Mean from '
                            +','.join(days_avg_climo_file_list)
                        )
                    else:
                        output_file_data.setncattr(
                            attr, 'Days 6-10 Fcst Mean from '
                            +','.join(days_avg_fcst_file_list)+';'
                            +'Days 6-10 Obs Mean from '
                            +','.join(days_avg_obs_file_list)
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
            if job_name in ['Days6_10Avg_GeoHeight',
                            'Days6_10Avg_Temp2m']:
                for data_name in ['FCST', 'OBS', 'CLIMO_MEAN']:
                    for input_var in input_file_data_var_list:
                        if data_name+'_'+var_level in input_var:
                            input_var_level = input_var
                    write_data_name_var = output_file_data.createVariable(
                        data_name+'_'+var_level+'_DAYS6_10AVG',
                        input_file_data.variables[input_var_level]\
                        .datatype,
                        input_file_data.variables[input_var_level]\
                        .dimensions
                    )
                    k_valid_time = days_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                    k_valid_time_ut = int(
                        (days_avg_valid_end
                         -datetime.datetime.strptime('19700101','%Y%m%d'))\
                        .total_seconds()
                    )
                    k_init_time = days_avg_day_init.strftime('%Y%m%d_%H%M%S')
                    k_init_time_ut = int(
                        (days_avg_day_init
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
                        elif k == 'init_time' and data_name == 'CLIMO_MEAN':
                            write_data_name_var.setncatts(
                                {k: k_valid_time}
                            )
                        elif k == 'init_time_ut' and data_name == 'CLIMO_MEAN':
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
                        write_data_name_var[:] = days_avg_fcst
                    elif data_name == 'OBS':
                        write_data_name_var[:] = days_avg_obs
                    elif data_name == 'CLIMO_MEAN':
                        write_data_name_var[:] = days_avg_climo
            else:
                for data_name in ['FCST', 'OBS']:
                    for input_var in input_file_data_var_list:
                        if data_name+'_'+var_level in input_var:
                            input_var_level = input_var
                    write_data_name_var = output_file_data.createVariable(
                        data_name+'_'+var_level+'_DAYS6_10AVG',
                        input_file_data.variables[input_var_level]\
                        .datatype,
                        input_file_data.variables[input_var_level]\
                        .dimensions
                    )
                    k_valid_time = days_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                    k_valid_time_ut = int(
                        (days_avg_valid_end
                         -datetime.datetime.strptime('19700101','%Y%m%d'))\
                        .total_seconds()
                    )
                    k_init_time = days_avg_day_init.strftime('%Y%m%d_%H%M%S')
                    k_init_time_ut = int(
                        (days_avg_day_init
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
                        write_data_name_var[:] = days_avg_fcst
                    elif data_name == 'OBS':
                        write_data_name_var[:] = days_avg_obs
            if len(list(output_file_data.variables.keys())) == 0:
                print("No variables in "+output_file+", removing")
                output_file_data.close()
                os.remove(output_file)
            else:
                output_file_data.close()
            input_file_data.close()
        else:
            print("WARNING: Cannot create Days 6-10 average file "
                  +output_file+" "
                  +"; need at least "+str(expected_nfiles)+" input files")
        days_avg_day+=1
        print("")
    valid_hr+=int(valid_hr_inc)
    
print("END: "+os.path.basename(__file__))
