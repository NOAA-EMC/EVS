#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_grid2obs_create_merged_ptype.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This creates a merged precipitation type file used for
          calculating MET MCTC line type.
          (1-rain, 2-snow, 3-freezing rain, 4-ice pellets)
Run By: individual statistics job scripts generated through
        ush/global_det/global_det_atmos_plots_grid2obs_create_job_scripts.py
'''

import os
import sys
import netCDF4 as netcdf
import numpy as np
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

# Process run time agruments
if len(sys.argv) != 5:
    print("FATAL ERROR: Not given correct number of run time agruments..."
          +os.path.basename(__file__)+" "
          +"CRAIN_FILE CSNOW_FILE CFRZR_FILE CICEP_FILE")
    sys.exit(1)
input_crain_file_format = sys.argv[1]
input_csnow_file_format = sys.argv[2]
input_cfrzr_file_format = sys.argv[3]
input_cicep_file_format = sys.argv[4]

# Create merged ptype data
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
        input_crain_file = gda_util.format_filler(
            input_crain_file_format, valid_date_dt, init_date_dt, str(fhr), {}
        )
        input_csnow_file = gda_util.format_filler(
            input_csnow_file_format, valid_date_dt, init_date_dt, str(fhr), {}
        )
        input_cfrzr_file = gda_util.format_filler(
            input_cfrzr_file_format, valid_date_dt, init_date_dt, str(fhr), {}
        )
        input_cicep_file = gda_util.format_filler(
            input_cicep_file_format, valid_date_dt, init_date_dt, str(fhr), {}
        )
        all_input_ptype_files_exist = True
        missing_input_ptype_file_list = []
        for input_ptype_file in [input_crain_file, input_csnow_file,
                                 input_cfrzr_file, input_cicep_file]:
            if not gda_util.check_file_exists_size(input_ptype_file):
                all_input_ptype_files_exist = False
                missing_input_ptype_file_list.append(
                    input_ptype_file
                )
        output_DATA_merged_ptype_file = os.path.join(
            DATA, VERIF_CASE+'_'+STEP, 'METplus_output',
            RUN+'.'+valid_date_dt.strftime('%Y%m%d'), MODEL, VERIF_CASE,
            'merged_ptype_'+VERIF_TYPE+'_'+job_name+'_'
            +'init'+init_date_dt.strftime('%Y%m%d%H')
            +'_fhr'+str(fhr).zfill(3)+'.nc'
        )
        output_COMOUT_merged_ptype_file = os.path.join(
            COMOUT,
            RUN+'.'+valid_date_dt.strftime('%Y%m%d'), MODEL, VERIF_CASE,
            'merged_ptype_'+VERIF_TYPE+'_'+job_name+'_'
            +'init'+init_date_dt.strftime('%Y%m%d%H')
            +'_fhr'+str(fhr).zfill(3)+'.nc'
        )
        if os.path.exists(output_COMOUT_merged_ptype_file):
            if not os.path.exits(output_DATA_merged_ptype_file):
                gda_util.copy_file(output_COMOUT_merged_ptype_file,
                                   output_DATA_merged_ptype_file)
        else:
            if all_input_ptype_files_exist:
                if not os.path.exists(output_DATA_merged_ptype_file):
                    make_merged_ptype_output_file = True
                else:
                    make_merged_ptype_output_file = False
                    print("DATA Output File exists: "
                          +output_DATA_merged_ptype_file)
                    if SENDCOM == 'YES' \
                            and gda_util.check_file_exists_size(
                                output_DATA_merged_ptype_file
                            ):
                        gda_util.copy_file(output_DATA_merged_ptype_file,
                                           output_COMOUT_merged_ptype_file)
            else:
                make_merged_ptype_output_file = False
                print("NOTE: Cannot make merged ptype file "
                      +f"{output_DATA_merged_ptype_file} - "
                      +"missing one of the input files "
                      +f"{', '.join(missing_input_ptype_file_list)}")
        if make_merged_ptype_output_file:
            print(f"\nInput CRAIN File: {input_crain_file}")
            print(f"Input CSNOW File: {input_csnow_file}")
            print(f"Input CFRZR File: {input_cfrzr_file}")
            print(f"Input CICEP File: {input_cicep_file}")
            input_crain_data = netcdf.Dataset(input_crain_file)
            input_csnow_data = netcdf.Dataset(input_csnow_file)
            input_cfrzr_data = netcdf.Dataset(input_cfrzr_file)
            input_cicep_data = netcdf.Dataset(input_cicep_file)
            input_crain = input_crain_data.variables['CRAIN'][:]
            input_csnow = input_csnow_data.variables['CSNOW'][:]
            input_cfrzr = input_cfrzr_data.variables['CFRZR'][:]
            input_cicep = input_cicep_data.variables['CICEP'][:]
            print("DATA Output Merged Ptype File: "
                  +output_DATA_merged_ptype_file)
            print("COMOUT Output Merged Ptype File: "
                  +output_COMOUT_merged_ptype_file)
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
                output_DATA_merged_ptype_file, 'w', format='NETCDF3_CLASSIC'
            )
            for attr in input_crain_data.ncattrs():
                output_merged_ptype_data.setncattr(
                    attr, input_crain_data.getncattr(attr)
                )
            for dim in list(input_crain_data.dimensions.keys()):
                output_merged_ptype_data.createDimension(
                    dim, len(input_crain_data.dimensions[dim])
                )
            for var in ['lat', 'lon']:
                output_merged_var = output_merged_ptype_data.createVariable(
                    var, input_crain_data.variables[var].datatype,
                    input_crain_data.variables[var].dimensions
                )
                for k in input_crain_data.variables[var].ncattrs():
                    output_merged_var.setncatts(
                        {k: input_crain_data.variables[var].getncattr(k)}
                    )
            output_merged_var = output_merged_ptype_data.createVariable(
                'PTYPE', input_crain_data.variables[var].datatype,
                input_crain_data.variables[var].dimensions
            )
            var = 'CRAIN'
            for k in input_crain_data.variables[var].ncattrs():
                if k == 'name':
                    output_merged_var.setncatts({k: 'PTYPE_L0'})
                elif k == 'long_name':
                    output_merged_var.setncatts({k: 'Preciptation Type'})
                else:
                    output_merged_var.setncatts(
                        {k: input_crain_data.variables[var].getncattr(k)}
                    )
            output_merged_var[:] = merged_ptype[:]
            output_merged_ptype_data.close()
            input_crain_data.close()
            input_csnow_data.close()
            input_cfrzr_data.close()
            input_cicep_data.close()
            if SENDCOM == 'YES' \
                    and gda_util.check_file_exists_size(
                        output_DATA_merged_ptype_file
                    ):
                gda_util.copy_file(output_DATA_merged_ptype_file,
                                   output_COMOUT_merged_ptype_file)
    valid_date_dt = valid_date_dt + datetime.timedelta(hours=int(valid_hr_inc))

print("END: "+os.path.basename(__file__))
