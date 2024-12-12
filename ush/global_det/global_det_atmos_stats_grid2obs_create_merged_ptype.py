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
import netCDF4 as netcdf
import numpy as np
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
job_num_work_dir = os.environ['job_num_work_dir']

# Create merged ptype data
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
        # Check possible input files
        input_file_dict = {}
        missing_input_file_dict = {}
        for file_name_ptype in ['Rain', 'Snow', 'FrzRain', 'IcePel']:
            input_file_name_ptype = (
                f"regrid_data_plane_{VERIF_TYPE}_{file_name_ptype}_"
                +f"init{init_date_dt:%Y%m%d%H}_fhr{str(fhr).zfill(3)}.nc"
            )
            check_input_file_list = [
                os.path.join(full_path_job_num_work_dir, input_file_name_ptype),
                os.path.join(full_path_DATA, input_file_name_ptype),
                os.path.join(full_path_COMOUT, input_file_name_ptype),
                os.path.join(full_path_COMIN, input_file_name_ptype)
            ]
            missing_input_ptype_file_list = []
            input_file_dict[file_name_ptype] = 'NA'
            for check_input_file in check_input_file_list:
                if os.path.exists(check_input_file):
                    input_file_dict[file_name_ptype] = check_input_file
                    break
                else:
                    missing_input_ptype_file_list.append(check_input_file)
            missing_input_file_dict[file_name_ptype] = (
                missing_input_ptype_file_list
            )
        all_input_ptype_files_exist = True
        for file_name_ptype in list(input_file_dict.keys()):
            if input_file_dict[file_name_ptype] == 'NA':
                all_input_ptype_files_exist = False
        # Set output file
        output_file = os.path.join(
            full_path_job_num_work_dir,
            f"merged_ptype_{VERIF_TYPE}_{job_name}_"
            f"init{init_date_dt:%Y%m%d%H}_fhr{str(fhr).zfill(3)}.nc"
        )
        output_file_DATA = os.path.join(
            full_path_DATA, output_file.rpartition('/')[2]
        )
        output_file_COMOUT = os.path.join(
            full_path_COMOUT, output_file.rpartition('/')[2]
        )
        if os.path.exists(output_file_COMOUT):
            print(f"COMOUT Output File exists: {output_file_COMOUT}")
            make_merged_ptype_output_file = False
            gda_util.copy_file(output_file_COMOUT, output_file_DATA)
        else:
            make_merged_ptype_output_file = True
        if all_input_ptype_files_exist and make_merged_ptype_output_file:
            input_crain_file = input_file_dict['Rain']
            input_csnow_file = input_file_dict['Snow']
            input_cfrzr_file = input_file_dict['FrzRain']
            input_cicep_file = input_file_dict['IcePel']
            print(f"\nInput CRAIN File: {input_crain_file}")
            print(f"Input CSNOW File: {input_csnow_file}")
            print(f"Input CFRZR File: {input_cfrzr_file}")
            print(f"Input CICEP File: {input_cicep_file}")
            print(f"Output File: {output_file}")
            if not os.path.exists(full_path_job_num_work_dir):
                gda_util.make_dir(full_path_job_num_work_dir)
            input_crain_data = netcdf.Dataset(input_crain_file)
            input_csnow_data = netcdf.Dataset(input_csnow_file)
            input_cfrzr_data = netcdf.Dataset(input_cfrzr_file)
            input_cicep_data = netcdf.Dataset(input_cicep_file)
            input_crain = input_crain_data.variables['CRAIN'][:]
            input_csnow = input_csnow_data.variables['CSNOW'][:]
            input_cfrzr = input_cfrzr_data.variables['CFRZR'][:]
            input_cicep = input_cicep_data.variables['CICEP'][:]
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
            output_file_data = netcdf.Dataset(output_file, 'w',
                                              format='NETCDF3_CLASSIC')
            for attr in input_crain_data.ncattrs():
                output_file_data.setncattr(
                    attr, input_crain_data.getncattr(attr)
                )
            for dim in list(input_crain_data.dimensions.keys()):
                output_file_data.createDimension(
                    dim, len(input_crain_data.dimensions[dim])
                )
            for var in ['lat', 'lon']:
                output_merged_var = output_file_data.createVariable(
                    var, input_crain_data.variables[var].datatype,
                    input_crain_data.variables[var].dimensions
                )
                for k in input_crain_data.variables[var].ncattrs():
                    output_merged_var.setncatts(
                        {k: input_crain_data.variables[var].getncattr(k)}
                    )
            output_merged_var = output_file_data.createVariable(
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
            output_file_data.close()
            input_crain_data.close()
            input_csnow_data.close()
            input_cfrzr_data.close()
            input_cicep_data.close()
            if gda_util.check_file_exists_size(output_file):
                if SENDCOM == 'YES':
                    gda_util.copy_file(output_file, output_file_COMOUT)
        else:
            print(f"NOTE: Cannot make merged ptype file {output_file} - "
                  f"input file options do not exist")
            for file_name_ptype in list(input_file_dict.keys()):
                print(f"NOTE: Missing {file_name_ptype} files: "
                      +f"{','.join(missing_input_file_dict[file_name_ptype])}")
    valid_date_dt = valid_date_dt + datetime.timedelta(hours=int(valid_hr_inc))

print("END: "+os.path.basename(__file__))
