#!/usr/bin/env python3

"""! Do prep work for GHRSST OSPO production files 
Args:
    daily_source_file - daily source file (string)
    daily_dest_file   - daily destination file (string)
    date_dt           - date (datetime object)
    log_missing_file  - text file path to write that production file is missing (string)
Returns:
"""

import os
import datetime
import glob
import shutil
import sys
import netCDF4 as netcdf
import global_ens_atmos_util as gea_util

print("BEGIN: "+os.path.basename(__file__))



# Read in common environment variables
DCOMINghrsst = os.environ['DCOMINghrsst']
COMOUTgefs = os.environ['COMOUTgefs']
SENDCOM = os.environ['SENDCOM']
vdaym1 = os.environ['vdaym1']
print(vdaym1)

# Input definitions
daily_source_file=os.path.join(DCOMINghrsst,vdaym1,'validation_data','marine','ghrsst',vdaym1+'_OSPO_L4_GHRSST.nc')
daily_dest_file = os.path.join(COMOUTgefs, 'ghrsst.t00z.nc')

# Temporary file name
daily_prepped_file = os.path.join(os.getcwd(), 'atmos.'+daily_source_file.rpartition('/')[2])

# Prep daily file
if os.path.exists(daily_source_file):
    gea_util.copy_file(daily_source_file, daily_prepped_file)
if os.path.exists(daily_prepped_file):
    if os.path.getsize(daily_prepped_file) > 0:
        daily_prepped_data = netcdf.Dataset(daily_prepped_file, 'a', format='NETCDF3_CLASSIC')
        ghrsst_ospo_date_since_dt = datetime.datetime.strptime('1981-01-01 00:00:00','%Y-%m-%d %H:%M:%S')
        daily_prepped_data['time'][:] = daily_prepped_data['time'][:][0] + 43200
    else:
        print("WARNING: "+daily_prepped_file+" empty, 0 sized")
else:
    print("WARNING: "+daily_prepped_file+" does not exist")
daily_prepped_data.close()
if SENDCOM == 'YES':
    gea_util.copy_file(daily_prepped_file, daily_dest_file)
print("END: "+os.path.basename(__file__))








                                                                                                                    
