#!/usr/bin/env python3
'''
Name: rtofs_prep_rej_argo.py
Contact(s): Samira Ardani(samira.ardani@noaa.gov)
Abstract: This Python code reads the .txt files from Argo float profiles, 
          identifies the call sign and type of rejected observation data with QC Std >4, 
          lists the call signs for further use in METplus configuration file.
'''          

import xarray as xr
import netCDF4 as nc
import os
import pandas as pd
import datetime
import glob
import shutil
import numpy as np


# Read in environment variables to use
INITDATE = os.environ['INITDATE']
DATA = os.environ['DATA']
DCOMROOT = os.environ['DCOMROOT']
COMROOT = os.environ ['COMROOT']
COMIN = os.environ ['COMIN']
SENDCOM = os.environ['SENDCOM']
COMOUTprep = os.environ['COMOUTprep']
RUN = os.environ['RUN']
rtofs_ver = os.environ['rtofs_ver']

# Set up date/time
INITDATE_YMD = datetime.datetime.strptime(INITDATE, '%Y%m%d')
mDATE= INITDATE_YMD-datetime.timedelta(days=1)
p1DATE = INITDATE_YMD + datetime.timedelta(days=1)
p2DATE= INITDATE_YMD + datetime.timedelta(days=2)
mDATE_YMD = datetime.datetime.strftime(mDATE, '%Y%m%d')
p1DATE_YMD = datetime.datetime.strftime(p1DATE, '%Y%m%d')
p2DATE_YMD = datetime.datetime.strftime(p2DATE, '%Y%m%d')
rtofs_qc_1 = os.path.join(COMROOT,
                        'rtofs',f"{rtofs_ver}",f"rtofs.{p1DATE_YMD}",
                        'ncoda/logs/profile_qc',
                        f"prof_argo_rpt.{INITDATE_YMD.strftime('%Y%m%d')}00.txt")

rtofs_qc_2 = os.path.join(COMROOT,
                        'rtofs',f"{rtofs_ver}",f"rtofs.{p2DATE_YMD}",
                        'ncoda/logs/profile_qc',
                        f"prof_argo_rpt.{p1DATE_YMD}00.txt")

rtofs_qc = os.path.join(COMOUTprep,
                        f"ocean.{INITDATE_YMD:%Y%m%d}",
                        'argo','rtofs_qc.txt')
combined = rtofs_qc
print (combined)
with open(combined, 'w') as outfile:
    for fname in [rtofs_qc_1, rtofs_qc_2]:
        with open(fname) as infile:
            outfile.write(infile.read())

#########################################################################################
# Identify and filter the call sign of profiles with rejected flag from QC ARTOFS outputs:
########################################################################################
num_profile = []
line_with_sign = []
rejected_temp = []
rejected_psal = []
call_signs = []
Rcpt_temp = []
Rcpt_psal = []
DTG_temp = []
DTG_psal = []
lookup = 'QC Std'
with open(rtofs_qc) as myFile:
    myFile = list(myFile)
    for num, line in enumerate(myFile, 0):
        if lookup in line:
            std_num=line.rpartition(' ')[2]
            if std_num > str(4):
                if "Salinity" in line:
                    num_profile.append(num-3)
                    call_sign= myFile[num-3].rpartition('= "')[2].rpartition('"')[0]
                    #print(call_sign)
                    call_signs.append(call_sign)
                    line_with_sign.append(myFile[num-3].strip())
                    rejected_psal.append(myFile[num-3].rpartition('= "')[2].rpartition('"')[0])
                    Rcpt_psal.append(myFile[num-3].rpartition('Rcpt= ')[2].rpartition('  Sign')[0])
                    DTG_psal.append(myFile[num-3].rpartition('DTG= ')[2].rpartition('  Rcpt')[0])
                if "Temperature" in line:
                    num_profile.append(num-2)
                    call_sign= myFile[num-2].rpartition('= "')[2].rpartition('"')[0]
                    #print(call_sign)
                    call_signs.append(call_sign)
                    line_with_sign.append(myFile[num-2].strip())
                    rejected_temp.append(myFile[num-2].rpartition('= "')[2].rpartition('"')[0])
                    Rcpt_temp.append(myFile[num-2].rpartition('Rcpt= ')[2].rpartition('  Sign')[0])
                    DTG_temp.append(myFile[num-2].rpartition('DTG= ')[2].rpartition('  Rcpt')[0])

rejected_temp_file = os.path.join (COMOUTprep,f"ocean.{INITDATE_YMD:%Y%m%d}", 'argo',f"rejected_temp_{INITDATE_YMD:%Y%m%d}.txt")
file1 = open(rejected_temp_file,'w')
for temp_ID in rejected_temp:
    file1.write(temp_ID+" ")
file1.close()

rejected_psal_file = os.path.join (COMOUTprep, f"ocean.{INITDATE_YMD:%Y%m%d}", 'argo',f"rejected_psal_{INITDATE_YMD:%Y%m%d}.txt")    
file2 = open(rejected_psal_file,'w')
for psal_ID in rejected_psal:
#    file2.write(psal_ID+"\n")
    file2.write(psal_ID+" ")
file2.close()

print(rejected_psal)
print(rejected_temp)
print(Rcpt_psal)
print(DTG_psal)
print(Rcpt_temp)
print(DTG_temp)
###################################################################

#### USER CONFIGURATION ####

ASCII2NC_input_file = os.path.join (COMOUTprep, f"ocean.{INITDATE_YMD:%Y%m%d}", 'argo' , f"argo.{INITDATE_YMD:%Y%m%d}.nc")  # Path to input NetCDF file from ASCII2NC
ASCII2NC_output_file = os.path.join(COMOUTprep , f"ocean.{INITDATE_YMD:%Y%m%d}", 'argo' , f"argo.{INITDATE_YMD:%Y%m%d}_filtered.nc")     # Path for output file
sid_temp = rejected_temp
sid_psal = rejected_psal

#convert to sets and combine:
stations_to_exclude = set(sid_temp) | set(sid_psal)            # Set of station IDs to exclude (case-sensitive)

# Load and Filter
print(f"Loading: {ASCII2NC_input_file}")
ds = xr.open_dataset(ASCII2NC_input_file)

# Check if station_id variable exists
if 'hdr_sid_table' not in ds.variables:
            raise ValueError("hdr_sid_table variable not found in NetCDF file.")

# Step 1: Get obs ? hdr index
obs_hdr_idx = ds['obs_hid'].values.astype(np.int64) # shape: (nobs,)

# Step 2: Get hdr ? sid index
hdr_sid_idx = ds['hdr_sid'].values.astype(np.int64)  # shape: (nhdr,)


# Decode station_id (it's usually stored as byte strings)
# Step 3: Get SID strings
sid_chars = ds['hdr_sid_table'].values.astype(str)  # shape: (nhdr_sid, mxstr2)
sid_strings = np.array([''.join(row).strip() for row in sid_chars])  # shape: (nhdr_sid,)

# Step 4: Map each obs to its station ID
obs_sid_idx = hdr_sid_idx[obs_hdr_idx]  # shape: (nobs,)
obs_station_ids = sid_strings[obs_sid_idx]



# Build mask to keep only stations not in the exclusion list
keep_mask = np.array([sid not in stations_to_exclude for sid in obs_station_ids])
keep_indices = np.where(keep_mask)[0]

print(f"Original obs: {len(obs_hdr_idx)}")
print(f"Keeping {len(keep_indices)} observations after filtering.")

# Step 6: Apply filtering and rename nobs ? obs
obs_dim_in = 'nobs'

ds_filtered = ds.isel({obs_dim_in: keep_indices})


# Save to new file
print(f"Writing filtered output to: {ASCII2NC_output_file}")
ds_filtered.to_netcdf(ASCII2NC_output_file)

print("Done.")

