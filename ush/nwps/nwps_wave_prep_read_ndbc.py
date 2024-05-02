#!/usr/bin/env python3
'''
Name: nwps_wave_prep_read_ndbc.py
Contact(s): Samira Ardani(samira.ardani@noaa.gov)

Abstract: This Python code filters the Buoy IDs from NDBC, those have locations from the $FIXevs, 
then it copies the associate .txt files in to tmp directory and COMOUT.

'''          

import os
import pandas as pd
import datetime
import glob
import shutil
import numpy as np
import netCDF4 as nc


# Read in environment variables to use
VDATE = os.environ['VDATE']
DATA = os.environ['DATA']
DCOMROOT = os.environ['DCOMROOT']
SENDCOM = os.environ['SENDCOM']
FIXevs = os.environ ['FIXevs']
COMOUT = os.environ ['COMOUT']
RUN = os.environ['RUN']
COMPONENT = os. environ ['COMPONENT']
VERIF_CASE = os.environ ['VERIF_CASE']

# Set up date/time
VDATE_YMD = datetime.datetime.strptime(VDATE, '%Y%m%d')
VDATE_Y =  '{:04d}'.format(VDATE_YMD.year)
VDATE_M =  '{:02d}'.format(VDATE_YMD.month)
VDATE_D =  '{:02d}'.format(VDATE_YMD.day)

PDATE= VDATE_YMD-datetime.timedelta(days=1)
PDATE_YMD =  datetime.datetime.strftime(PDATE, '%Y%m%d')

all_ndbc = os.path.join(DCOMROOT,
                        f'{VDATE_YMD:%Y%m%d}','validation_data','marine','buoy')
fixed_buoys = os.path.join (FIXevs,'ndbc_stations','ndbc_stations.xml')

ndbc_for_nwps = os.path.join (DATA,'ndbc')
if not os.path.exists(ndbc_for_nwps):
    os.mkdir(ndbc_for_nwps)

output_nwps_ndbc = os.path.join(f'{COMOUT}.{VDATE}','ndbc')
if not os.path.exists(output_nwps_ndbc):
    os.mkdir(output_nwps_ndbc)

#########################################################################################
# Identify and filter available buoys in Great lakes region:
########################################################################################

buoy_id = []
buoy_lat = []
buoy_lon = []
myFile = open(fixed_buoys, 'r')
Lines = myFile.readlines()
for line in Lines:
    # myFile = list(myFile)
    ndbc_id = line.partition('station id="')[2].partition('"')[0]
    ndbc_lat = line.partition('lat="')[2].partition('"')[0]
    ndbc_lon = line.partition('lon="')[2].partition('"')[0]

    buoy_id.append(ndbc_id)
    buoy_lat.append(ndbc_lat)
    buoy_lon.append(ndbc_lon)

buoy_dict = {'buoy_id': buoy_id, 'buoy_lat': buoy_lat, 'buoy_lon': buoy_lon} 
df = pd.DataFrame(buoy_dict)
df[['buoy_lat','buoy_lon']] = df[['buoy_lat','buoy_lon']].apply(pd.to_numeric)
nwps_buoy_id = list(df['buoy_id'])

all_ndbc_files = glob.glob (os.path.join(all_ndbc,"*.txt"))
all_buoy_id = []
for ndbc_file in all_ndbc_files:
    ndbc_buoy_id = ndbc_file.rpartition('/')[2].partition('.')[0]
    all_buoy_id.append(ndbc_buoy_id)
    if ndbc_buoy_id in nwps_buoy_id:
        shutil.copy2(ndbc_file, ndbc_for_nwps)


#############################################################################
# Modify the copied .txt files to include the data for that particular VDATE:
# Altered from: Mallory Row's script for EVS-global_det component.
##############################################################################

ndbc_header1 = ("#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   "
                                +"PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE\n")
ndbc_header2 = ("#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   "
                                +"hPa  degC  degC  degC  nmi  hPa    ft\n")

tmp_nwps_ndbc_files = glob.glob(os.path.join(ndbc_for_nwps,"*.txt"))
for tmp_buoy_file in tmp_nwps_ndbc_files:
    tmp_id = tmp_buoy_file.rpartition('/')[2].partition('.')[0]
    dfff = pd.read_csv(tmp_buoy_file, sep=" ",skiprows=2, skipinitialspace=True,keep_default_na=False, dtype='str', header=None)
    new_df = dfff.loc[(dfff[0] == VDATE_Y)& (dfff[1] == VDATE_M)& (dfff[2] == VDATE_D)& (dfff[4] == '00')]
    tmp_nwps_ndbc = os.path.join (ndbc_for_nwps,f'{tmp_id}_edited.txt')
    tmp_nwps_ndbc_final = open (tmp_nwps_ndbc, 'w')
    tmp_nwps_ndbc_final.write(ndbc_header1)
    tmp_nwps_ndbc_final.write(ndbc_header2)
    tmp_nwps_ndbc_final.close()
    new_df.to_csv(tmp_nwps_ndbc, header=None, index=None, sep=' ', mode='a')
    
    output_nwps_ndbc_files = os.path.join(output_nwps_ndbc, f'{tmp_id}.txt')
    if SENDCOM == 'YES':
        if os.path.getsize(tmp_nwps_ndbc) > 0:
            shutil.copy2(tmp_nwps_ndbc, output_nwps_ndbc_files)

