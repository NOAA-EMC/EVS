#!/usr/bin/env python3
'''
Name: global_det_wave_prep_trim_ndbc_files.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This trims the NDBC individual buoy text files
          for only data for a single date
Run By: scripts/prep/global_det/exevs_global_det_wave_prep.sh
'''


import os
import pandas as pd
import datetime
import glob
import shutil

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables to use
INITDATE = os.environ['INITDATE']
DATA = os.environ['DATA']
DCOMINndbc = os.environ['DCOMINndbc']
SENDCOM = os.environ['SENDCOM']
COMOUT = os.environ['COMOUT']

# Set up dates
INITDATE_dt = datetime.datetime.strptime(INITDATE, '%Y%m%d')
INITDATEp1_dt = INITDATE_dt + datetime.timedelta(days=1)

# Assign header columns in NDBC individual buoy files
ndbc_header1 = ("#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   "
                +"PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE\n")
ndbc_header2 = ("#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   "
                +"hPa  degC  degC  degC  nmi  hPa    ft\n")

# Trim down files for single date
for DCOMINndbc_file in glob.glob(os.path.join(DCOMINndbc,
                                             f"{INITDATEp1_dt:%Y%m%d}",
                                             'validation_data', 'marine',
                                             'buoy', '*.txt')):
    DATAndbc_file = os.path.join(DATA,
                                 f"ndbc_trimmed_{INITDATE_dt:%Y%m%d}_"
                                 +f"{DCOMINndbc_file.rpartition('/')[2]}")
    COMOUTndbc_file = os.path.join(f"{COMOUT}.{INITDATE_dt:%Y%m%d}",
                                   'ndbc',
                                   f"{DCOMINndbc_file.rpartition('/')[2]}")
    if not os.path.exists(COMOUTndbc_file):
        print(f"Trimming {DCOMINndbc_file} for {INITDATE_dt:%Y%m%d}")
        DCOMINndbc_file_df = pd.read_csv(
            DCOMINndbc_file, sep=" ", skiprows=2, skipinitialspace=True,
            keep_default_na=False, dtype='str', header=None,
            names=ndbc_header1[1:].split()
        )
        trimmed_DCOMINndbc_file_df = DCOMINndbc_file_df[
            (DCOMINndbc_file_df['YY'] == f"{INITDATE_dt:%Y}") \
             & (DCOMINndbc_file_df['MM'] == f"{INITDATE_dt:%m}") \
             & (DCOMINndbc_file_df['DD'] == f"{INITDATE_dt:%d}")
        ]
        DATAndbc_file_data = open(DATAndbc_file, 'w')
        DATAndbc_file_data.write(ndbc_header1)
        DATAndbc_file_data.write(ndbc_header2)
        DATAndbc_file_data.close()
        trimmed_DCOMINndbc_file_df.to_csv(
            DATAndbc_file, header=None, index=None, sep=' ', mode='a'
        )
        if SENDCOM == 'YES':
            if os.path.getsize(DATAndbc_file) > 0:
                print(f"Copying {DATAndbc_file} to {COMOUTndbc_file}")
                shutil.copy2(DATAndbc_file, COMOUTndbc_file)
            else:
                print("WARNING: {DATAndbc_file} empty, 0 sized")
