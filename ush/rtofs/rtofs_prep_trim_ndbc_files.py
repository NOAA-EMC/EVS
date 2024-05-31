#!/usr/bin/env python3
'''
Name: rtofs_prep_trim_ndbc_files.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This trims the NDBC individual buoy text files
          for only data for a single date
Run By: scripts/prep/rtofs/exevs_rtofs_prep.sh
'''


import os
import pandas as pd
import datetime
import glob
import shutil

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables to use
VDATE = os.environ['VDATE']
DATA = os.environ['DATA']
DCOMROOT = os.environ['DCOMROOT']
SENDCOM = os.environ['SENDCOM']
COMOUTprep = os.environ['COMOUTprep']
RUN = os.environ['RUN']
MET_NDBC_STATIONS = os.environ['MET_NDBC_STATIONS']

# Set up dates
VDATE_dt = datetime.datetime.strptime(VDATE, '%Y%m%d')

# Assign header columns in NDBC individual buoy files
ndbc_header1 = ("#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   "
                +"PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE\n")
ndbc_header2 = ("#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   "
                +"hPa  degC  degC  degC  nmi  hPa    ft\n")

# Read in location data file
buoy_with_loc_list = []
for line in open(MET_NDBC_STATIONS, 'r'):
    buoy_with_loc_list.append(
        line.partition('<station id="')[2].partition('"')[0]
    )

# Trim down files for single date
# and only include those with location data
for ndbc_input_file in glob.glob(os.path.join(DCOMROOT,
                                             f"{VDATE_dt:%Y%m%d}",
                                             'validation_data', 'marine',
                                             'buoy', '*.txt')):
    buoy_id = ndbc_input_file.rpartition('/')[2].partition('.')[0]
    if buoy_id not in buoy_with_loc_list:
        continue
    ndbc_tmp_file = os.path.join(DATA, f"rtofs.{VDATE_dt:%Y%m%d}",
                                 RUN, 'buoy', f"{buoy_id}.txt")
    ndbc_output_file = os.path.join(COMOUTprep, f"rtofs.{VDATE_dt:%Y%m%d}",
                                    RUN, 'buoy', f"{buoy_id}.txt")
    if not os.path.exists(ndbc_output_file):
        #print(f"Trimming {ndbc_input_file} for {VDATE_dt:%Y%m%d}")
        #ndbc_input_file_df = pd.read_csv(
        #    ndbc_input_file, sep=" ", skiprows=2, skipinitialspace=True,
        #    keep_default_na=False, dtype='str', header=None,
        #    names=ndbc_header1[1:].split()
        #)
        #trimmed_ndbc_input_file_df = ndbc_input_file_df[
        #    (ndbc_input_file_df['YY'] == f"{VDATE_dt:%Y}") \
        #     & (ndbc_input_file_df['MM'] == f"{VDATE_dt:%m}") \
        #     & (ndbc_input_file_df['DD'] == f"{VDATE_dt:%d}")
        #]
        #ndbc_tmp_file_data = open(ndbc_tmp_file, 'w')
        #ndbc_tmp_file_data.write(ndbc_header1)
        #ndbc_tmp_file_data.write(ndbc_header2)
        #ndbc_tmp_file_data.close()
        #trimmed_ndbc_input_file_df.to_csv(
        #    ndbc_tmp_file, header=None, index=None, sep=' ', mode='a'
        #)
        if os.path.getsize(ndbc_input_file) > 0:
            print(f"Copying {ndbc_input_file} to {ndbc_tmp_file}")
            shutil.copy2(ndbc_input_file, ndbc_tmp_file)
        else:
            print("WARNING: {ndbc_input_file} empty, 0 sized")
        if SENDCOM == 'YES':
            if os.path.getsize(ndbc_tmp_file) > 0:
                print(f"Copying {ndbc_tmp_file} to {ndbc_output_file}")
                shutil.copy2(ndbc_tmp_file, ndbc_output_file)
            else:
                print("WARNING: {ndbc_tmp_file} empty, 0 sized")
