'''
Name: mesoscale_precip_prep.py
Contact(s): Mallory Row
Abstract: 
'''

import os
import datetime
import glob
import shutil
import sys

print(f"BEGIN: {os.path.basename(__file__)}")

cwd = os.getcwd()
print(f"Working in: {cwd}")

# Read in common environment variables
DATA = os.environ['DATA']
COMINccpa = os.environ['COMINccpa']
COMINmrms = os.environ['COMINmrms']
COMOUT = os.environ['COMOUT']
INITDATE = os.environ['INITDATE']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']

# Make COMOUT directory for dates
COMOUT_INITDATE = f"{COMOUT}.{INITDATE}"
DATA_INITDATE = os.path.join(DATA, f"{RUN}.{INITDATE}")
for dir_INITDATE in [COMOUT_INITDATE, DATA_INITDATE]:
    if not os.path.exists(dir_INITDATE):
        os.makedirs(dir_INITDATE)
    print(f"Marking directory {dir_INITDATE}")

# Get CCPA files
DATA_INITDATE_ccpa = os.path.join(DATA_INITDATE, 'ccpa')
COMOUT_INITDATE_ccpa = os.path.join(COMOUT_INITDATE, 'ccpa')
for dir_INITDATE in [COMOUT_INITDATE_ccpa, DATA_INITDATE_ccpa]:
    if not os.path.exists(dir_INITDATE):
        os.makedirs(dir_INITDATE)
    print(f"Marking directory {dir_INITDATE}")
for hour in range(0,24,1):
    print(f"Getting CCPA files valid {INITDATE} {str(hour).zfill(2)}Z")
    if hour > 0 and hour <= 6:
        COMINccpa_hour_dir = os.path.join(COMINccpa, f"ccpa.{INITDATE}", '06')
    elif hour > 6 and hour <= 12:
        COMINccpa_hour_dir = os.path.join(COMINccpa, f"ccpa.{INITDATE}", '12')
    elif hour > 12 and hour <= 18:
        COMINccpa_hour_dir = os.path.join(COMINccpa, f"ccpa.{INITDATE}", '18')
    elif hour == 0:
        COMINccpa_hour_dir = os.path.join(COMINccpa, f"ccpa.{INITDATE}", '00')
    else:
        INITDATEm1 = (
            datetime.datetime.strptime(INITDATE, '%Y%m%d')
            + datetime.timedelta(days=1)
        ).strftime('%Y%m%d')
        COMINccpa_hour_dir = os.path.join(COMINccpa, f"ccpa.{INITDATEm1}", '00')
    accum_list = ['01']
    if hour % 3 == 0:
        accum_list.append('03')
    if hour % 6 == 0:
        accum_list.append('06')
    for accum in accum_list:
        COMINccpa_hour_accum_file = os.path.join(
            COMINccpa_hour_dir,
            f"ccpa.t{str(hour).zfill(2)}z.{accum}h.hrap.conus.gb2"
        )
        if os.path.exists(COMINccpa_hour_accum_file):
            DATAccpa_hour_accum_file = os.path.join(
                DATA_INITDATE_ccpa,
                COMINccpa_hour_accum_file.rpartition('/')[2]
            )
            print(f"Copying {COMINccpa_hour_accum_file} to "
                  +f"{DATAccpa_hour_accum_file}")
            shutil.copy2(COMINccpa_hour_accum_file, DATAccpa_hour_accum_file)

# Get MRMS files
DATA_INITDATE_mrms = os.path.join(DATA_INITDATE, 'mrms')
COMOUT_INITDATE_mrms = os.path.join(COMOUT_INITDATE, 'mrms')
for dir_INITDATE in [COMOUT_INITDATE_mrms, DATA_INITDATE_mrms]:
    if not os.path.exists(dir_INITDATE):
        os.makedirs(dir_INITDATE)
    print(f"Marking directory {dir_INITDATE}")
for area in ['alaska']:
    COMINmrms_area = os.path.join(COMINmrms, area, 'MultiSensorQPE')
    for hour in range(0,24,1):
        print(f"Getting {area} MRMS files valid {INITDATE} "
              +f"{str(hour).zfill(2)}Z")
        accum_list = ['01']
        if hour % 3 == 0:
            accum_list.append('03')
        if hour % 6 == 0:
            accum_list.append('06')
        for accum in accum_list:
            COMINmrms_area_hour_accum_gzfile = os.path.join(
                COMINmrms_area, f"MultiSensor_QPE_{accum}H_Pass2_00.00_"
                +f"{INITDATE}-{str(hour).zfill(2)}0000.grib2.gz"
            )
            if os.path.exists(COMINmrms_area_hour_accum_gzfile):
                DATAmrms_area_hour_accum_gzfile = os.path.join(
                    DATA_INITDATE_mrms,
                    COMINmrms_area_hour_accum_gzfile.rpartition('/')[2]
                )
                print(f"Copying {COMINmrms_area_hour_accum_gzfile} to "
                      +f"{DATAmrms_area_hour_accum_gzfile}")
                shutil.copy2(COMINmrms_area_hour_accum_gzfile,
                             DATAmrms_area_hour_accum_gzfile)
                print(f"Unzipping {DATAmrms_area_hour_accum_gzfile}")
                os.system(f"gunzip {DATAmrms_area_hour_accum_gzfile}")
                DATAmrms_area_hour_accum_file = os.path.join(
                    DATA_INITDATE_mrms, f"{area}_"
                    +f"{DATAmrms_area_hour_accum_gzfile.rpartition('/')[2].replace('.gz', '')}"
                )
                print("Moving "
                      +f"{DATAmrms_area_hour_accum_gzfile.replace('.gz', '')} "
                      +f"to {DATAmrms_area_hour_accum_file}")
                os.system("mv "
                         +f"{DATAmrms_area_hour_accum_gzfile.replace('.gz', '')} "
                         +f"{DATAmrms_area_hour_accum_file}")

print(f"END: {os.path.basename(__file__)}")
