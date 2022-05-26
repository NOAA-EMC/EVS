'''
Name: global_det_atmos_create_daily_avg_gridded_anomaly_data.py
Contact(s): Mallory Row
Abstract: This script is used to create daily anomaly
          data from MET grid_stat netCDF output
'''

import os
import sys
import numpy as np
import glob
import netCDF4 as netcdf
import datetime

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
TRUTH = os.environ['TRUTH']
DATE = os.environ['DATE']
netCDF_STARTDATE = os.environ['netCDF_STARTDATE']
netCDF_ENDDATE = os.environ['netCDF_ENDDATE']
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end'] 
valid_hr_inc = os.environ['valid_hr_inc']
fhr_end = os.environ['fhr_end']

# Get variable and level information to make anomaly data for
if len(sys.argv) == 2:
    var_level = sys.argv[1]
    if '_' not in sys.argv[1]:
        print("ERROR: variable and level runtime agrument formated "
              +"incorrectly, be sure to separate variable and level with "
              +"an underscore (_), example HGT_P500")
        sys.exit(1)
    else:
        var_level = sys.argv[1]
        print("Using var_level = "+var_level)
elif len(sys.argv) == 1:
    print("WARNING: No variable and length specified in runtime agrument "
          +"using default: HGT_P500")
    var_level = 'HGT_P500'
else:
    print("ERROR: Too many runtime agruments given, after script name follow "
          +"variable and level information formatted like HGT_P500")
    sys.exit(1)
output_var_level = (var_level.split('_')[0]+'_ANOM_'
                    +var_level.split('_')[-1])

# Set input and output directories
input_dir = os.path.join(DATA, VERIF_CASE+'_'+STEP, 'METplus_output')
output_dir = os.path.join(DATA, VERIF_CASE+'_'+STEP, 'METplus_output',
                          RUN+'.'+netCDF_ENDDATE, MODEL, VERIF_CASE)
# Get files
input_files_wildcard_list = glob.glob(
    os.path.join(input_dir, RUN+'.'+netCDF_STARTDATE, MODEL, VERIF_CASE,
                'grid_stat_'+VERIF_TYPE+'.'+job_name+'_*_'
                 +netCDF_STARTDATE+'_*_pairs.nc')
)
input_files_wildcard_list = (
    input_files_wildcard_list +
    glob.glob(
        os.path.join(input_dir, RUN+'.'+netCDF_ENDDATE, MODEL, VERIF_CASE,
                     'grid_stat_'+VERIF_TYPE+'.'+job_name+'_*_'
                     +netCDF_ENDDATE+'_*_pairs.nc')
    )
)

# Create output forecast hour files with forecast and observation anomaly data
for input_file in sorted(input_files_wildcard_list):
    print("\nInput file: "+input_file)
    input_file_data = netcdf.Dataset(input_file)
    input_file_data_var_list = list(input_file_data.variables.keys())
    if not 'CLIMO_MEAN_'+var_level+'_FULL' in input_file_data_var_list:
        print("ERROR: "+input_file+" does not contain variable "
              +"CLIMO_MEAN_"+var_level+"_FULL cannot make anomaly "
              +"data")
        sys.exit(1)
    output_file = input_file.replace('grid_stat_', '')
    print("Output File: "+output_file)
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
        output_file_data.createDimension(dim,
                                         len(input_file_data.dimensions[dim]))
    for data_name in ['FCST', 'OBS']:
        data_name_var_level = data_name+'_'+var_level+'_FULL'
        if data_name_var_level in input_file_data_var_list:
            write_data_name_var = output_file_data.createVariable(
                data_name+'_'+output_var_level,
                input_file_data.variables[data_name_var_level].datatype,
                input_file_data.variables[data_name_var_level].dimensions
            )
            for k in input_file_data.variables[data_name_var_level].ncattrs():
                if k == 'name':
                    write_data_name_var.setncatts(
                        {k: data_name+'_'+output_var_level}
                    )
                elif k == 'long_name':
                    write_data_name_var.setncatts(
                        {k: input_file_data.variables[data_name_var_level]\
                            .getncattr(k).replace(' at', ' Anomaly at')}
                    )
                else:
                    write_data_name_var.setncatts(
                        {k: input_file_data.variables[data_name_var_level]\
                         .getncattr(k)}
                    )
            write_data_name_var[:] = (
                input_file_data.variables[data_name_var_level][:]
                - input_file_data.variables['CLIMO_MEAN_'+var_level+'_FULL'][:]
            )
        else:
            print("ERROR: "+input_file+" does not contain variable "
                  +data_name_var_level+", cannot make anomaly data")
    output_file_data.close()
    input_file_data.close()

# Create daily average files
print("\nCreating daily average files")
valid_hr = int(valid_hr_start)
while valid_hr <= int(valid_hr_end):
    daily_avg_valid_end = datetime.datetime.strptime(DATE+str(valid_hr),
                                                     '%Y%m%d%H')
    daily_avg_valid_start = daily_avg_valid_end - datetime.timedelta(hours=18)
    daily_avg_day_end = int(fhr_end)/24
    daily_avg_day_start = 1
    daily_avg_day = daily_avg_day_start
    while daily_avg_day <= daily_avg_day_end:
        daily_avg_file_list = []
        daily_avg_day_fhr_end = daily_avg_day * 24
        daily_avg_day_fhr_start = daily_avg_day_fhr_end - 18
        daily_avg_day_init = (daily_avg_valid_end
                              - datetime.timedelta(days=daily_avg_day))
        daily_avg_day_fhr = daily_avg_day_fhr_start
        output_file = os.path.join(output_dir, VERIF_TYPE+'.'+job_name+'_init'
                                   +daily_avg_day_init.strftime('%Y%m%d%H')
                                   +'_valid'
                                   +daily_avg_valid_start\
                                   .strftime('%Y%m%d%H')+'to'
                                   +daily_avg_valid_end\
                                   .strftime('%Y%m%d%H')+'.nc')
        if os.path.exists(output_file):
            os.remove(output_file)
        print("Output File: "+output_file)
        daily_avg_fcst_anom_sum = 0
        daily_avg_obs_anom_sum = 0
        while daily_avg_day_fhr <= daily_avg_day_fhr_end:
            daily_avg_day_fhr_valid = (
                daily_avg_day_init
                + datetime.timedelta(hours=daily_avg_day_fhr)
            )
            daily_avg_day_fhr_input_file = os.path.join(
                input_dir, RUN+'.'+daily_avg_day_fhr_valid.strftime('%Y%m%d'),
                MODEL, VERIF_CASE, VERIF_TYPE+'.'+job_name+'_'
                +str(daily_avg_day_fhr).zfill(2)+'0000L_'
                +daily_avg_day_fhr_valid.strftime('%Y%m%d')+'_'
                +daily_avg_day_fhr_valid.strftime('%H')+'0000V_pairs.nc'
            )
            if os.path.exists(daily_avg_day_fhr_input_file):
                print("Input file for forecast hour "+str(daily_avg_day_fhr)
                      +', valid '+str(daily_avg_day_fhr_valid)
                      +', init '+str(daily_avg_day_init)+": "
                      +daily_avg_day_fhr_input_file)
                input_file_data = netcdf.Dataset(daily_avg_day_fhr_input_file)
                daily_avg_fcst_anom_sum = (daily_avg_fcst_anom_sum +
                                           input_file_data.variables[
                                               'FCST_'+output_var_level
                                           ][:])
                daily_avg_obs_anom_sum = (daily_avg_obs_anom_sum +
                                          input_file_data.variables[
                                              'OBS_'+output_var_level
                                          ][:])
                daily_avg_file_list.append(daily_avg_day_fhr_input_file)
            else:
                print("No input file for forecast hour "+str(daily_avg_day_fhr)
                      +', valid '+str(daily_avg_day_fhr_valid)
                      +', init '+str(daily_avg_day_init))
            daily_avg_day_fhr+=6
        if len(daily_avg_file_list) != 0:
            daily_avg_fcst_anom_avg = (
                daily_avg_fcst_anom_sum/len(daily_avg_file_list)
            )
            daily_avg_obs_anom_avg = (
                daily_avg_obs_anom_sum/len(daily_avg_file_list)
            )
            output_file_data = netcdf.Dataset(output_file, 'w',
                                              format='NETCDF3_CLASSIC')
            for attr in input_file_data.ncattrs():
                if attr == 'FileOrigins':
                    output_file_data.setncattr(
                        attr, 'Daily Mean from '+','.join(daily_avg_file_list)
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
                write_data_name_var = output_file_data.createVariable(
                    data_name+'_'+output_var_level,
                    input_file_data.variables[data_name+'_'+output_var_level]\
                    .datatype,
                    input_file_data.variables[data_name+'_'+output_var_level]\
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
                            data_name+'_'+output_var_level
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
                                    data_name+'_'+output_var_level
                             ].getncattr(k)}
                        )
                if data_name == 'FCST':
                    write_data_name_var[:] = daily_avg_fcst_anom_avg
                elif data_name == 'OBS':
                    write_data_name_var[:] = daily_avg_obs_anom_avg      
            output_file_data.close()
            input_file_data.close()
        daily_avg_day+=1
    valid_hr+=int(valid_hr_inc)
    
print("END: "+os.path.basename(__file__))
