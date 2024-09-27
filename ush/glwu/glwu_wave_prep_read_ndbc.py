#!/usr/bin/env python3
'''
Name: glwu_wave_prep_read_ndbc.py
Contact(s): Samira Ardani(samira.ardani@noaa.gov)
Cited: Mallory P. Row (mallory.row@noaa.gov)

Abstract: This Python code filters the Buoy IDs from NDBC, those have locations from the $FIXevs for Great Lakes regions, 
then it copies the associate .txt files in to tmp directory and COMOUT.

'''          

import os
import pandas as pd
import datetime
import glob
import shutil
import numpy as np
import netCDF4 as nc

# Define the variables

# Read in environment variables to use
INITDATE = os.environ['INITDATE']
DATA = os.environ['DATA']
DCOMROOT = os.environ['DCOMROOT']
SENDCOM = os.environ['SENDCOM']
FIXevs = os.environ ['FIXevs']
COMOUT = os.environ ['COMOUT']
RUN = os.environ['RUN']
COMPONENT = os. environ ['COMPONENT']
VERIF_CASE = os.environ ['VERIF_CASE']

# Set up date/time
INITDATE_YMD = datetime.datetime.strptime(INITDATE, '%Y%m%d')
INITDATE_Y =  '{:04d}'.format(INITDATE_YMD.year)
INITDATE_M =  '{:02d}'.format(INITDATE_YMD.month)
INITDATE_D =  '{:02d}'.format(INITDATE_YMD.day)

PDATE= INITDATE_YMD + datetime.timedelta(days=1)
PDATE_YMD =  datetime.datetime.strftime(PDATE, '%Y%m%d')

all_ndbc = os.path.join(DCOMROOT,
                        f'{PDATE_YMD}','validation_data','marine','buoy')
fixed_buoys = os.path.join (FIXevs,'ndbc_stations','ndbc_stations.xml')

ndbc_for_glwu = os.path.join (DATA,'ndbc')
if not os.path.exists(ndbc_for_glwu):
    os.mkdir(ndbc_for_glwu)

output_glwu_ndbc = os.path.join(f'{COMOUT}.{INITDATE}','ndbc')
if not os.path.exists(output_glwu_ndbc):
    os.mkdir(output_glwu_ndbc)

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
dff = df.loc[(df['buoy_lat']>40.8) & (df['buoy_lat']<49.0)& (df['buoy_lon']> -93.0) & (df['buoy_lon']< -73.0) ]
glwu_buoy_id = list(dff['buoy_id'])

all_ndbc_files = glob.glob (os.path.join(all_ndbc,"*.txt"))
all_buoy_id = []
for ndbc_file in all_ndbc_files:
    ndbc_buoy_id = ndbc_file.rpartition('/')[2].partition('.')[0]
    all_buoy_id.append(ndbc_buoy_id)
    if ndbc_buoy_id in glwu_buoy_id:
        shutil.copy2(ndbc_file, ndbc_for_glwu)


#############################################################################
# Modify the copied .txt files to include the data for that particular INITDATE:
##############################################################################

ndbc_header1 = ("#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   "
                                +"PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE\n")
ndbc_header2 = ("#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   "
                                +"hPa  degC  degC  degC  nmi  hPa    ft\n")

tmp_glwu_ndbc_files = glob.glob(os.path.join(ndbc_for_glwu,"*.txt"))
for tmp_buoy_file in tmp_glwu_ndbc_files:
    tmp_id = tmp_buoy_file.rpartition('/')[2].partition('.')[0]
    dfff = pd.read_csv(tmp_buoy_file, sep=" ",skiprows=2, skipinitialspace=True,keep_default_na=False, dtype='str', header=None)
    new_df = dfff.loc[(dfff[0] == INITDATE_Y)& (dfff[1] == INITDATE_M)& (dfff[2] == INITDATE_D)& (dfff[4] == '00')]
    tmp_glwu_ndbc = os.path.join (ndbc_for_glwu,f'{tmp_id}_edited.txt')
    tmp_glwu_ndbc_final = open (tmp_glwu_ndbc, 'w')
    tmp_glwu_ndbc_final.write(ndbc_header1)
    tmp_glwu_ndbc_final.write(ndbc_header2)
    tmp_glwu_ndbc_final.close()
    new_df.to_csv(tmp_glwu_ndbc, header=None, index=None, sep=' ', mode='a')
    
    output_glwu_ndbc_files = os.path.join(output_glwu_ndbc, f'{tmp_id}.txt')
    if SENDCOM == 'YES':
        if os.path.getsize(tmp_glwu_ndbc) > 0:
            shutil.copy2(tmp_glwu_ndbc, output_glwu_ndbc_files)

