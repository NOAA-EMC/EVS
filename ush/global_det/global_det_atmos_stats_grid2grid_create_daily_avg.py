#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_grid2grid_create_daily_avg.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script is used to create daily average
          for variable from netCDF output.
Run By: individual statistics job scripts generated through
        ush/global_det/global_det_atmos_plots_grid2grid_create_job_scripts.py
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
fhr_inc = '12'
#fhr_end = os.environ['fhr_end']
#fhr_inc = os.environ['fhr_inc']

# Process run time agruments
if len(sys.argv) != 4:
    print("FATAL ERROR: Not given correct number of run time agruments..."
          +os.path.basename(__file__)+" VARNAME_VARLEVEL DATA_FILE_FORMAT "
          +"COMIN_FILE_FORMART")
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
    DATA_file_format = sys.argv[2]
    COMIN_file_format = sys.argv[3]

# Create daily average files
print("\nCreating daily average files")
valid_hr = int(valid_hr_start)
while valid_hr <= int(valid_hr_end):
    if job_name == 'DailyAvg_GeoHeightAnom':
        if int(valid_hr) % 12 != 0 :
            valid_hr+=int(valid_hr_inc)
            continue
    daily_avg_valid_end = datetime.datetime.strptime(DATE+str(valid_hr),
                                                     '%Y%m%d%H')
    if job_name == 'DailyAvg_GeoHeightAnom':
        daily_avg_valid_start = (daily_avg_valid_end
                                 - datetime.timedelta(hours=12))
    else:
        daily_avg_valid_start = (daily_avg_valid_end
                                 - datetime.timedelta(hours=24))
    daily_avg_day_end = int(fhr_list[-1])/24
    daily_avg_day_start = 1
    daily_avg_day = daily_avg_day_start
    while daily_avg_day <= daily_avg_day_end:
        daily_avg_file_list = []
        daily_avg_day_fhr_end = int(daily_avg_day * 24)
        if job_name == 'DailyAvg_GeoHeightAnom':
            daily_avg_day_fhr_start = daily_avg_day_fhr_end - 12
        else:
            daily_avg_day_fhr_start = daily_avg_day_fhr_end - 24
        daily_avg_day_init = (daily_avg_valid_end
                              - datetime.timedelta(days=daily_avg_day))
        daily_avg_day_fhr = daily_avg_day_fhr_start
        output_DATA_file = os.path.join(
            DATA, VERIF_CASE+'_'+STEP, 'METplus_output', RUN+'.'+DATE, MODEL,
            VERIF_CASE, 'daily_avg_'+VERIF_TYPE+'_'+job_name+'_init'
            +daily_avg_day_init.strftime('%Y%m%d%H')+'_valid'
            +daily_avg_valid_start.strftime('%Y%m%d%H')+'to'
            +daily_avg_valid_end.strftime('%Y%m%d%H')+'.nc'
        )
        output_COMOUT_file = os.path.join(
            COMOUT, RUN+'.'+DATE, MODEL,
            VERIF_CASE, 'daily_avg_'+VERIF_TYPE+'_'+job_name+'_init'
            +daily_avg_day_init.strftime('%Y%m%d%H')+'_valid'
            +daily_avg_valid_start.strftime('%Y%m%d%H')+'to'
            +daily_avg_valid_end.strftime('%Y%m%d%H')+'.nc'
        )
        daily_avg_fcst_sum = 0
        daily_avg_fcst_file_list = []
        daily_avg_obs_sum = 0
        daily_avg_obs_file_list = []
        while daily_avg_day_fhr <= daily_avg_day_fhr_end:
            daily_avg_day_fhr_valid = (
                daily_avg_day_init
                + datetime.timedelta(hours=daily_avg_day_fhr)
            )
            daily_avg_day_fhr_DATA_input_file = gda_util.format_filler(
                    DATA_file_format, daily_avg_day_fhr_valid,
                    daily_avg_day_init,
                    str(daily_avg_day_fhr), {}
            )
            daily_avg_day_fhr_COMIN_input_file = gda_util.format_filler(
                    COMIN_file_format, daily_avg_day_fhr_valid,
                    daily_avg_day_init,
                    str(daily_avg_day_fhr), {}
            )
            if os.path.exists(daily_avg_day_fhr_COMIN_input_file):
                daily_avg_day_fhr_input_file = (
                    daily_avg_day_fhr_COMIN_input_file)
            else:
                daily_avg_day_fhr_input_file = (
                    daily_avg_day_fhr_DATA_input_file
                )
            if os.path.exists(daily_avg_day_fhr_input_file):
                print("Input file for forecast hour "+str(daily_avg_day_fhr)
                      +', valid '+str(daily_avg_day_fhr_valid)
                      +', init '+str(daily_avg_day_init)+": "
                      +daily_avg_day_fhr_input_file)
                input_file_data = netcdf.Dataset(daily_avg_day_fhr_input_file)
                input_file_data_var_list = list(input_file_data.variables.keys())
                fcst_var_level = 'fcst_var_hold'
                obs_var_level = 'obs_var_hold'
                for input_var in input_file_data_var_list:
                    if 'FCST_'+var_level in input_var:
                        fcst_var_level = input_var
                    if 'OBS_'+var_level in input_var:
                        obs_var_level = input_var
                if fcst_var_level in input_file_data_var_list:
                    daily_avg_fcst_sum = (daily_avg_fcst_sum +
                                          input_file_data.variables[
                                              fcst_var_level
                                          ][:])
                    daily_avg_fcst_file_list.append(daily_avg_day_fhr_input_file)
                if obs_var_level in input_file_data_var_list:
                    daily_avg_obs_sum = (daily_avg_obs_sum +
                                         input_file_data.variables[
                                             obs_var_level
                                         ][:])
                    daily_avg_obs_file_list.append(daily_avg_day_fhr_input_file)
            else:
                print("No input file for forecast hour "+str(daily_avg_day_fhr)
                      +', valid '+str(daily_avg_day_fhr_valid)
                      +', init '+str(daily_avg_day_init)+" "
                      +daily_avg_day_fhr_DATA_input_file+" or "
                      +daily_avg_day_fhr_COMIN_input_file)
            if job_name == 'DailyAvg_GeoHeightAnom':
                daily_avg_day_fhr+=12
            else:
                daily_avg_day_fhr+=int(fhr_inc)
        if len(daily_avg_fcst_file_list) != 0:
            daily_avg_fcst = (
                daily_avg_fcst_sum/len(daily_avg_fcst_file_list)
            )
        if len(daily_avg_obs_file_list) != 0:
            daily_avg_obs = (
                daily_avg_obs_sum/len(daily_avg_obs_file_list)
            )
        if job_name == 'DailyAvg_GeoHeightAnom':
            expected_nfiles = 2
        else:
            if fhr_inc == '6':
                expected_nfiles = 5
            elif fhr_inc == '12':
                expected_nfiles = 3
        if os.path.exists(output_COMOUT_file):
            if not os.path.exists(output_DATA_file):
                gda_util.copy_file(output_COMOUT_file, output_DATA_file)
                make_daily_avg_output_file = False
        else:
            if len(daily_avg_fcst_file_list) == expected_nfiles \
                    and len(daily_avg_obs_file_list) == expected_nfiles:
                if not os.path.exists(output_DATA_file):
                    make_daily_avg_output_file = True
                else:
                    make_daily_avg_output_file = False
                    print(f"DATA Output File exists: {output_DATA_file}")
                    if SENDCOM == 'YES' \
                            and gda_util.check_file_exists_size(
                                output_DATA_file
                            ):
                        gda_util.copy_file(output_DATA_file,
                                           output_COMOUT_file)
            else:
                print("NOTE: Cannot create daily average file "
                      +output_DATA_file+"; need "+str(expected_nfiles)+" "
                      +"input files")
                make_daily_avg_output_file = False
        if make_daily_avg_output_file:
            print(f"DATA Output File: {output_DATA_file}")
            print(f"COMOUT Output File: {output_COMOUT_file}")
            output_file_data = netcdf.Dataset(output_DATA_file, 'w',
                                              format='NETCDF3_CLASSIC')
            for attr in input_file_data.ncattrs():
                if attr == 'FileOrigins':
                    output_file_data.setncattr(
                        attr, 'Daily Fcst Mean from '
                        +','.join(daily_avg_fcst_file_list)+';'
                        +'Daily Obs Mean from '
                        +','.join(daily_avg_obs_file_list)
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
            for input_var_name in ['lat', 'lon']:
                write_data_name_var = output_file_data.createVariable(
                    input_var_name,
                    input_file_data.variables[input_var_name]\
                    .datatype,
                    input_file_data.variables[input_var_name]\
                    .dimensions
                )
                for k in input_file_data.variables[input_var_name].ncattrs():
                    write_data_name_var.setncatts(
                        {k: input_file_data.variables[
                                input_var_name
                         ].getncattr(k)}
                    )
                write_data_name_var[:] = (
                    input_file_data.variables[input_var_name][:]
                )
            for data_name in ['FCST', 'OBS']:
                for input_var in input_file_data_var_list:
                    if data_name+'_'+var_level in input_var:
                        input_var_level = input_var
                write_data_name_var = output_file_data.createVariable(
                    data_name+'_'+var_level+'_DAILYAVG',
                    input_file_data.variables[input_var_level]\
                    .datatype,
                    input_file_data.variables[input_var_level]\
                    .dimensions
                )
                k_valid_time = daily_avg_valid_end.strftime('%Y%m%d_%H%M%S')
                k_valid_time_ut = int(
                    (daily_avg_valid_end
                     -datetime.datetime.strptime('19700101','%Y%m%d'))\
                    .total_seconds()
                )
                k_init_time = daily_avg_day_init.strftime('%Y%m%d_%H%M%S')
                k_init_time_ut = int(
                    (daily_avg_day_init
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
                    write_data_name_var[:] = daily_avg_fcst
                elif data_name == 'OBS':
                    write_data_name_var[:] = daily_avg_obs
            if len(list(output_file_data.variables.keys())) == 0:
                print("No variables in "+output_file+", removing")
                output_file_data.close()
                os.remove(output_file)
            else:
                output_file_data.close()
            input_file_data.close()
            if SENDCOM == 'YES' \
                    and gda_util.check_file_exists_size(output_DATA_file):
                gda_util.copy_file(output_DATA_file, output_COMOUT_file)
        if job_name == 'DailyAvg_GeoHeightAnom':
            daily_avg_day+=1
        else:
            daily_avg_day+=int(fhr_inc)/24.
        print("")
    valid_hr+=int(valid_hr_inc)

print("END: "+os.path.basename(__file__))
