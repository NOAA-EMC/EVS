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
import itertools
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
obs_file = os.environ['obs_file']
input_ascii2nc_file = os.environ['input_ascii2nc_file']

valid_date_dt = datetime.datetime.strptime(valid_date, '%Y%m%d%H')

diag_var_dict = {
    't': 'Temperature',
    'q': 'Specific Humidity',
    'uv': 'Wind'
}
wmo_level_list = [925, 850, 700, 500, 250, 100]
wmo_var_list = ['HGT', 'TMP', 'UGRD', 'VGRD', 'RH']

if os.path.exists(input_ascii2nc_file):
    os.remove(input_ascii2nc_file)

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
print(f"Working in {os.getcwd()}")

for diag_var in list(diag_var_dict.keys()):
    # Get file
    diag_var_file = f"diag_conv_{diag_var}_anl.{valid_date_dt:%Y%m%d%H}.nc4"
    diag_var_zipfile = f"{diag_var_file}.gz"
    if not os.path.exists(diag_var_file):
        with tarfile.open(obs_file, 'r') as tf:
            print(f"Extracting {diag_var_zipfile} from {obs_file}")
            tf.extract(member=diag_var_zipfile)
        with gzip.open(diag_var_zipfile, 'rb') as dvzf:
            with open(diag_var_file, 'wb') as dvf:
                print(f"Unzipping {diag_var_zipfile} to {diag_var_file}")
                shutil.copyfileobj(dvzf, dvf)
    if gda_util.check_file_exists_size(diag_var_file):
        print(f"Processing {diag_var_dict[diag_var]} from {diag_var_file}")
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
        # Rawinsonde: Observation_Type = 120 [t, q, ps], 220 [uv]
        if diag_var == 'uv':
            ob_type = 220
        else:
            ob_type = 120
        diag_var_rawinsonde_df = diag_var_assim_df[
            (diag_var_assim_df['Observation_Type'].isin([ob_type]))
            & (diag_var_assim_df['Pressure'].isin(wmo_level_list))
        ]
        # Put into dataframe for MET to read
        station_id_list = diag_var_rawinsonde_df['Station_ID'].tolist()
        reltimes = (diag_var_rawinsonde_df['Time'].to_numpy()
                    * datetime.timedelta(hours=1))
        valid_time_list = [
            datetime.datetime.strftime(valid_date_dt+reltime,
                                       '%Y%m%d_%H%M%S') \
            for reltime in reltimes
        ]
        lat_list = diag_var_rawinsonde_df['Latitude'].tolist()
        lon_list = diag_var_rawinsonde_df['Longitude'].tolist()
        elv_list = diag_var_rawinsonde_df['Station_Elevation'].tolist()
        pres_list = diag_var_rawinsonde_df['Pressure'].tolist()
        height_list = diag_var_rawinsonde_df['Height'].tolist()
        qc_string_list = [
            round(qc) for qc in diag_var_rawinsonde_df['Prep_QC_Mark']\
                .tolist()
        ]
        anl_use_list = diag_var_rawinsonde_df['Analysis_Use_Flag'].tolist()
        if diag_var == 'uv':
            message_type_list = ['ADPUPA'] * (2*len(diag_var_rawinsonde_df))
            station_id_list.extend(station_id_list)
            valid_time_list.extend(valid_time_list)
            lat_list.extend(lat_list)
            lon_list.extend(lon_list)
            elv_list.extend(elv_list)
            var_list = ['UGRD'] * len(diag_var_rawinsonde_df)
            var_list.extend(['VGRD'] * len(diag_var_rawinsonde_df))
            pres_list.extend(pres_list)
            height_list.extend(height_list)
            qc_string_list.extend(qc_string_list)
            value_list = diag_var_rawinsonde_df['u_Observation'].tolist()
            value_list.extend(diag_var_rawinsonde_df['v_Observation'].tolist())
        else:
            message_type_list = ['ADPUPA'] * len(diag_var_rawinsonde_df)
            if diag_var == 't':
                grib_var = 'TMP'
            elif diag_var == 'q':
                grib_var = 'SPFH'
            elif diag_var == 'ps':
                grib_var = 'PRES'
                pres_list = ['Z0'] * len(diag_var_rawinsonde_df)
            var_list = [grib_var] * len(diag_var_rawinsonde_df)
            value_list = diag_var_rawinsonde_df['Observation'].tolist()
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

tmp_ascii2nc_df = pd.DataFrame(ascii2nc_df_dict)

# Constants pulled from MetPy
water_molecular_weight = 18.015268
dry_air_molecular_weight = 28.96546
epsilon = water_molecular_weight/dry_air_molecular_weight
radius_earth = 6371008.7714
gravity = 9.80665

# Calculate geopotential heigh and relative humidity
print("Calculating Geopotential Height and Relative Humidity")
for sid_level in \
        list(itertools.product(tmp_ascii2nc_df['Station_ID'].unique(),
                               tmp_ascii2nc_df['Level'].unique())):
    sid = sid_level[0]
    level = sid_level[1]
    tmp_row = tmp_ascii2nc_df[
        (tmp_ascii2nc_df['Station_ID'] == sid)
        & (tmp_ascii2nc_df['Level'] == level)
        & (tmp_ascii2nc_df['Variable_Name'] == 'TMP')
    ]
    spfh_row = tmp_ascii2nc_df[
        (tmp_ascii2nc_df['Station_ID'] == sid)
        & (tmp_ascii2nc_df['Level'] == level)
        & (tmp_ascii2nc_df['Variable_Name'] == 'SPFH')
    ]
    # Geopotential Height
    if len(tmp_row) == 1:
        if tmp_row.iloc[0]['Height'] < 9999999:
            geo_height = (
                (gravity*radius_earth*tmp_row.iloc[0]['Height'])
                    /(radius_earth+tmp_row.iloc[0]['Height'])
                )/gravity
        else:
            geo_height = 'NA'
    else:
        geo_height = 'NA'
    # Relative Humidity
    if len(tmp_row) == 1 and len(spfh_row) == 1:
        if tmp_row.iloc[0]['Valid_Time'] == spfh_row.iloc[0]['Valid_Time'] \
                and tmp_row.iloc[0]['Height'] == spfh_row.iloc[0]['Height'] \
                and tmp_row.iloc[0]['Lat'] == spfh_row.iloc[0]['Lat'] \
                and tmp_row.iloc[0]['Lon'] == spfh_row.iloc[0]['Lon']:
            pres = float(level)
            tmpK = float(tmp_row.iloc[0]['Observation_Value'])
            tmpC = tmpK - 273.15
            spfh = float(spfh_row.iloc[0]['Observation_Value'])
            mixing_ratio = spfh/(1-spfh)
            # MetPy [Bolton (1980)]
            sat_vap_pres = (
                6.112 *
                np.exp((17.67*tmpC)/(tmpC+243.5))
            )
            sat_mixing_ratio = epsilon*(sat_vap_pres/(pres-sat_vap_pres))
            rh = (
                (mixing_ratio/(epsilon+mixing_ratio))
                *((epsilon+sat_mixing_ratio)/sat_mixing_ratio)
            )*100.
        else:
            rh = 'NA'
    else:
        rh = 'NA'
    if len(tmp_row) == 1:
        for met_var in ['HGT', 'RH']:
            if met_var == 'HGT':
                met_var_value = geo_height
            elif met_var == 'RH':
                met_var_value = rh
            if met_var_value == 'NA':
                continue
            ascii2nc_df_dict['Message_Type'].append(
                tmp_row.iloc[0]['Message_Type']
            )
            ascii2nc_df_dict['Station_ID'].append(
                tmp_row.iloc[0]['Station_ID']
            )
            ascii2nc_df_dict['Valid_Time'].append(
                tmp_row.iloc[0]['Valid_Time']
            )
            ascii2nc_df_dict['Lat'].append(
                tmp_row.iloc[0]['Lat']
            )
            ascii2nc_df_dict['Lon'].append(
                tmp_row.iloc[0]['Lon']
            )
            ascii2nc_df_dict['Elevation'].append(
                tmp_row.iloc[0]['Elevation']
            )
            ascii2nc_df_dict['Variable_Name'].append(met_var)
            ascii2nc_df_dict['Level'].append(
                tmp_row.iloc[0]['Level']
            )
            ascii2nc_df_dict['Height'].append(
                tmp_row.iloc[0]['Height']
            )
            ascii2nc_df_dict['QC_String'].append(
                tmp_row.iloc[0]['QC_String']
            )
            ascii2nc_df_dict['Observation_Value'].append(
                str(met_var_value)
            )

# Make dataframe
ascii2nc_df = pd.DataFrame(ascii2nc_df_dict)

# Keep only needed variables
ascii2nc_df = ascii2nc_df[
    (ascii2nc_df['Variable_Name'].isin(wmo_var_list))
]

# Write out dataframe
print(f"Writing file to {input_ascii2nc_file}")
ascii2nc_df.to_csv(
    input_ascii2nc_file, header=None, index=None, sep=' ', mode='w'
)

os.chdir(DATA)
print(f"Back in {os.getcwd()}")

print("END: "+os.path.basename(__file__))
