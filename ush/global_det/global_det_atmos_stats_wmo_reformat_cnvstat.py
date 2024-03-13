#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_wmo_reformat_cnvstat.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This reformats the GDAS cnvstat diag anl files
          for MET's ascii2nc
Run By: Individual job scripts
'''

import sys
import os
import datetime
import numpy as np
import pandas as pd
import netCDF4 as netcdf
import tarfile
import gzip
import shutil
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMIN = os.environ['COMIN']
COMINgfs = os.environ['COMINgfs']
SENDCOM = os.environ['SENDCOM']
COMOUT = os.environ['COMOUT']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
valid_date = os.environ['valid_date']
JOB_GROUP = os.environ['JOB_GROUP']
cnvstat_file = os.environ['cnvstat_file']
input_ascii2nc_file = os.environ['input_ascii2nc_file']

valid_date_dt = datetime.datetime.strptime(valid_date, '%Y%m%d%H')
var_list = ['t', 'uv', 'q']

ascii2nc_df_dict = {
    'Message_Type': [],
    'Station_ID': [],
    'Valid_Time': [],
    'Lat': [],
    'Lon': [],
    'Elevation': [],
    'Variable_Name': [],
    'Level': [],
    'Height': [],
    'QC_String': [],
    'Observation_Value': []
}

os.chdir(os.path.join(DATA, 'gdas_cnvstat'))
print(f"Working in {os.path.join(DATA, 'gdas_cnvstat')}")

for diag_var in var_list:
    # Get file
    diag_var_file = f"diag_conv_{diag_var}_anl.{valid_date_dt:%Y%m%d%H}.nc4"
    diag_var_zipfile = f"{diag_var_file}.gz"
    if not os.path.exists(diag_var_file):
        with tarfile.open(cnvstat_file, 'r') as tf:
            print(f"Extracting {diag_var_zipfile} from {cnvstat_file}")
            tf.extract(member=diag_var_zipfile)
        with gzip.open(diag_var_zipfile, 'rb') as dvzf:
            with open(diag_var_file, 'wb') as dvf:
                print(f"Unzipping {diag_var_zipfile} to {diag_var_file}")
                shutil.copyfileobj(dvzf, dvf)
    if gda_util.check_file_exists_size(diag_var_file):
        print(f"Processing {diag_var_file}")
        diag_var_nc = netcdf.Dataset(diag_var_file, 'r')
        diag_var_df_dict = {}
        for var in diag_var_nc.variables:
            # Station_ID and Observation_Class variables need
            # to be converted from byte string to string
            if var in ['Station_ID', 'Observation_Class']:
                data = diag_var_nc.variables[var][:]
                data = [i.tobytes(fill_value='/////', order='C')
                        for i in data]
                data = np.array(
                    [''.join(i.decode('UTF-8', 'ignore').split())
                     for i in data]
                )
                diag_var_df_dict[var] = data
            elif len(diag_var_nc.variables[var].shape) == 1:
                diag_var_df_dict[var] = diag_var_nc.variables[var][:]
            diag_var_df = pd.DataFrame(diag_var_df_dict)
        # Assimilated: Analysis_Use_Flag = 1
        diag_var_assim_df = diag_var_df[diag_var_df.Analysis_Use_Flag == 1.0]
        # Rawinsonde: Observation_Type = 120 [t, q], 220 [uv]
        if diag_var == 'uv':
            ob_type = 220
        else:
            ob_type = 120
        diag_var_rawinsonde = diag_var_assim_df[
            (diag_var_assim_df['Observation_Type'].isin([ob_type]))
             & (diag_var_assim_df['Pressure']\
                .isin([925, 850, 700, 500, 250, 100]))
        ]
        station_id_list = diag_var_rawinsonde['Station_ID'].tolist()
        reltimes = (diag_var_rawinsonde['Time'].to_numpy()
                    * datetime.timedelta(hours=1))
        valid_time_list = [
            datetime.datetime.strftime(valid_date_dt+reltime,
                                       '%Y%m%d_%H%M%S') \
            for reltime in reltimes
        ]
        lat_list = diag_var_rawinsonde['Latitude'].tolist()
        lon_list = diag_var_rawinsonde['Longitude'].tolist()
        elv_list = diag_var_rawinsonde['Station_Elevation'].tolist()
        pres_list = [
            f"P{round(p)}" for p in diag_var_rawinsonde['Pressure'].tolist()
        ]
        height_list = diag_var_rawinsonde['Height'].tolist()
        qc_string_list = [
            round(qc) for qc in diag_var_rawinsonde['Prep_QC_Mark']\
                .tolist()
        ]
        if diag_var == 'uv':
            message_type_list = ['ADPUPA'] * (2*len(diag_var_rawinsonde))
            station_id_list.extend(station_id_list)
            valid_time_list.extend(valid_time_list)
            lat_list.extend(lat_list)
            lon_list.extend(lon_list)
            elv_list.extend(elv_list)
            var_list = ['UGRD'] * len(diag_var_rawinsonde)
            var_list.extend(['VGRD'] * len(diag_var_rawinsonde))
            pres_list.extend(pres_list)
            height_list.extend(height_list)
            qc_string_list.extend(qc_string_list)
            value_list = diag_var_rawinsonde['u_Observation'].tolist()
            value_list.extend(diag_var_rawinsonde['v_Observation'].tolist())
        else:
            message_type_list = ['ADPUPA'] * len(diag_var_rawinsonde)
            if diag_var == 't':
                grib_var = 'TMP'
            elif diag_var == 'q':
                grib_var = 'SPFH'
                mixing_ratio = (
                    diag_var_rawinsonde['Observation'].to_numpy()/
                    (1-diag_var_rawinsonde['Observation'].to_numpy())
                )
            var_list = [grib_var] * len(diag_var_rawinsonde)
            value_list = diag_var_rawinsonde['Observation'].tolist()
        ascii2nc_df_dict['Message_Type'].extend(message_type_list)
        ascii2nc_df_dict['Station_ID'].extend(station_id_list)
        ascii2nc_df_dict['Valid_Time'].extend(valid_time_list)
        ascii2nc_df_dict['Lat'].extend(lat_list)
        ascii2nc_df_dict['Lon'].extend(lon_list)
        ascii2nc_df_dict['Elevation'].extend(elv_list)
        ascii2nc_df_dict['Variable_Name'].extend(var_list)
        ascii2nc_df_dict['Level'].extend(pres_list)
        ascii2nc_df_dict['Height'].extend(height_list)
        ascii2nc_df_dict['QC_String'].extend(qc_string_list)
        ascii2nc_df_dict['Observation_Value'].extend(value_list)
        diag_var_nc.close()
ascii2nc_df = pd.DataFrame(ascii2nc_df_dict)
# Filter out bad heights
ascii2nc = ascii2nc_df[ascii2nc_df['Height'] < 9999999]
# Write out dataframe
print(f"Writing file to {input_ascii2nc_file}")
ascii2nc_df.to_csv(
    input_ascii2nc_file, header=None, index=None, sep=' ', mode='w'
)

os.chdir(DATA)

print("END: "+os.path.basename(__file__))
