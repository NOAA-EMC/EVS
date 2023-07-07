#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_prep_grid2obs_create_job_script.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Create EVS CAM Grid2Obs - Prepare job scripts
# DEPENDENCIES: $SCRIPTSevs/cam/stats/exevs_$MODELNAME_grid2obs_prep.sh
#
# =============================================================================

import sys
import os
import re
import glob
import shutil
from datetime import datetime, timedelta as td
import numpy as np

print(f"BEGIN: {os.path.basename(__file__)}")

# Read in environment variables
STEP = os.environ['STEP']
VERIF_CASE = os.environ['VERIF_CASE']
MODELNAME = os.environ['MODELNAME']
MET_PLUS_PATH = os.environ['MET_PLUS_PATH']
MET_PATH = os.environ['MET_PATH']
MET_CONFIG = os.environ['MET_CONFIG']
DATA = os.environ['DATA']
VDATE = os.environ['VDATE']
njob = os.environ['njob']
COMPONENT = os.environ['COMPONENT']
NEST = os.environ['NEST']
USHevs = os.environ['USHevs']
if NEST == 'spc_otlk':
    if STEP == 'prep':
        TEMP_DIR = os.environ['TEMP_DIR']
        DAY = os.environ['DAY']
        VHOUR_GROUP = os.environ['VHOUR_GROUP']
        URL_HEAD = os.environ['URL_HEAD']
        metplus_launcher = os.environ['metplus_launcher']

# Make a dictionary of environment variables needed to run this particular job
job_env_vars_dict = {}
if NEST == 'spc_otlk':
    if STEP == 'prep':
        job_env_vars_dict['NEST'] = NEST
        job_env_vars_dict['VDATE'] = VDATE
        job_env_vars_dict['DAY'] = DAY
        job_env_vars_dict['VHOUR_GROUP'] = VHOUR_GROUP
        job_env_vars_dict['URL_HEAD'] = URL_HEAD
        job_env_vars_dict['TEMP_DIR'] = TEMP_DIR


# Make a list of commands needed to run this particular job
job_cmd_list = []
if STEP == 'prep':
    if COMPONENT == 'cam':
        if NEST == 'spc_otlk':
            job_cmd_list.append(
                f"python {USHevs}/{COMPONENT}/"
                + f"{COMPONENT}_{STEP}_{VERIF_CASE}_gen_{NEST}_mask.py"
            )
        else:
            print(f"ERROR: {NEST} is not a valid NEST for"
                  + f" cam/grid2obs/prep")
            sys.exit(1)
    else:
        print(f"ERROR: {COMPONENT} is not a valid COMPONENT for"
              + f" cam/grid2obs/prep (please use 'cam')")
        sys.exit(1)
else:
    print(f"ERROR: {STEP} is not a valid STEP for cam/grid2obs/prep (please"
          + f" use 'prep')")
    sys.exit(1)

# Write job script
job_dir = os.path.join(DATA, VERIF_CASE, STEP, 'prep_job_scripts')
if not os.path.exists(job_dir):
    os.makedirs(job_dir)
job_file = os.path.join(job_dir, f'job{njob}')
print(f"Creating job script: {job_file}")
job = open(job_file, 'w')
job.write('#!/bin/bash\n')
job.write('set -x \n')
job.write('\n')
for name, value in job_env_vars_dict.items():
    job.write(f'export {name}={value}\n')
job.write('\n')
for cmd in job_cmd_list:
    job.write(f'{cmd}\n')
job.close()

print(f"END: {os.path.basename(__file__)}")
