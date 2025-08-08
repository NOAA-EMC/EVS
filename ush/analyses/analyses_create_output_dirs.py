#!/usr/bin/env python3
# =============================================================================
#
# NAME: analyses_create_output_dirs.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
#                 Perry Shafran, perry.shafran@noaa.gov
# PURPOSE: Define working/ output directories and create them if they don't
#          exist.
# DEPENDENCIES: os.path.join([
#                   SCRIPTSevs,COMPONENT,STEP,
#                   "_".join(["exevs",MODELNAME,VERIF_CASE,STEP+".sh"]
#               )]
#
# =============================================================================

import os
import re
from datetime import datetime, timedelta as td

print(f"BEGIN: {os.path.basename(__file__)}")

# Read in environment variables
evs_ver = os.environ['evs_ver']
COMIN = os.environ['COMIN']
COMOUT = os.environ['COMOUT']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
MODELNAME = os.environ['MODELNAME']
if STEP == 'prep':
    INITDATE = os.environ['INITDATE']
    vdate_dt = datetime.strptime(INITDATE, '%Y%m%d')
if VERIF_CASE == "precip":
    if STEP == 'prep':
        FHR_END_FULL = os.environ['FHR_END_FULL']
        FHR_END_SHORT = os.environ['FHR_END_SHORT']
        fhr_end_max = max(int(FHR_END_FULL), int(FHR_END_SHORT))
        start_date_dt = vdate_dt - td(hours=fhr_end_max)
        VERIF_TYPE = os.environ['VERIF_TYPE']
        OBSNAME = os.environ['OBSNAME']

# Define data base directorie
data_base_dir = os.path.join(DATA, VERIF_CASE, 'data')
data_dir_list = [data_base_dir]
if VERIF_CASE == 'precip':
    if STEP == 'prep':
        data_dir_list.append(os.path.join(data_base_dir, MODELNAME))
        data_dir_list.append(os.path.join(data_base_dir, OBSNAME))

# Create data directories and subdirectories
for data_dir in data_dir_list:
    if not os.path.exists(data_dir):
        print(f"Creating data directory: {data_dir}")
        os.makedirs(data_dir, mode=0o755)

# Create job script base directory
job_scripts_dirs = []
if STEP == 'prep':
    job_scripts_dirs.append(os.path.join(DATA, VERIF_CASE, 'prep_job_scripts'))
for job_scripts_dir in job_scripts_dirs:
    if not os.path.exists(job_scripts_dir):
        print(f"Creating job script directory: {job_scripts_dir}")
        os.makedirs(job_scripts_dir, mode=0o755)

# Define working and COMOUT directories
working_dir_list = []
COMOUT_dir_list = []
if STEP == 'prep':
    working_output_base_dir = os.path.join(
        DATA, VERIF_CASE
    )
    working_dir_list.append(working_output_base_dir)
    working_dir_list.append(os.path.join(
        working_output_base_dir, 'data', 'workdirs'
    ))
# Create working output and COMOUT directories
for working_dir in working_dir_list:
    if not os.path.exists(working_dir):
        print(f"Creating working output directory: {working_dir}")
        os.makedirs(working_dir, mode=0o755, exist_ok=True)
    else:
        print(f"Tried creating working output directory but already exists: {working_dir}")
for COMOUT_dir in COMOUT_dir_list:
    if not os.path.exists(COMOUT_dir):
        print(f"Creating COMOUT directory: {COMOUT_dir}")
        os.makedirs(COMOUT_dir, mode=0o755, exist_ok=True)

print(f"END: {os.path.basename(__file__)}")
