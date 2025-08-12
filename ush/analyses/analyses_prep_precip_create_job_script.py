#!/usr/bin/env python3
# =============================================================================
#
# NAME: analyses_prep_precip_create_job_script.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
#                 Perry Shafran, perry.shafran@noaa.gov
# PURPOSE: Create EVS analyses Precipitation - Prepare job scripts
# DEPENDENCIES: $SCRIPTSevs/analyses/stats/exevs_$MODELNAME_precip_prep.sh
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
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
VERIF_TYPE = os.environ['VERIF_TYPE']
MODELNAME = os.environ['MODELNAME']
METPLUS_PATH = os.environ['METPLUS_PATH']
MET_ROOT = os.environ['MET_ROOT']
DATA = os.environ['DATA']
INITDATE = os.environ['INITDATE']
VHOUR_LIST = os.environ['VHOUR_LIST']
njob = os.environ['njob']
COMPONENT = os.environ['COMPONENT']
COMINobs = os.environ['COMINobs']
if VERIF_CASE == 'precip': 
    OBS_ACC = os.environ['OBS_ACC']
    ACC = os.environ['ACC']
    OBSNAME = os.environ['OBSNAME']
    NEST = os.environ['NEST']

# Make a dictionary of environment variables needed to run this particular job
job_env_vars_dict = {}

# Make a list of commands needed to run this particular job
job_cmd_list = []
if STEP == 'prep':
    if COMPONENT == 'analyses':
        if VERIF_CASE == 'precip':
            if OBSNAME == 'ccpa':
                for VHOUR in re.split(r'[\s,]+', VHOUR_LIST):
                    INITDATEHOUR = datetime.strptime(f'{INITDATE}{VHOUR}','%Y%m%d%H')
                    subtract_hours_inc=int(OBS_ACC)
                    subtract_hours=0
                    max_subtract_hours=int(ACC)
                    while subtract_hours < max_subtract_hours:
                        INITDATEHOURm = INITDATEHOUR - td(hours=subtract_hours)
                        INITDATEm = INITDATEHOURm.strftime('%Y%m%d')
                        VHOURm = INITDATEHOURm.strftime('%H')
                        COMOUTobs = os.path.join(
                            DATA, VERIF_CASE, 'data', 'workdirs', f'job{njob}', 
                            'ccpa', f'{RUN}.{INITDATEm}', 'ccpa'
                        )
                        if not os.path.isfile(os.path.join(
                                COMOUTobs, 
                                f'ccpa.t{VHOURm}z.{OBS_ACC}h.hrap.{NEST}.gb2')):
                            job_cmd_list.append(
                                f"if [ ! -d \"{COMOUTobs}\" ]; then mkdir -p \"{COMOUTobs}\";"
                                + f" fi"
                            )
                            if int(VHOURm) > 18:
                                INITDATEmp1 = (
                                    INITDATEHOURm + td(days=1)
                                ).strftime('%Y%m%d')
                                infiles=os.path.join(
                                    COMINobs, f'ccpa.{INITDATEmp1}', '*', 
                                    f'ccpa.t{VHOURm}z.{OBS_ACC}h.hrap.{NEST}.gb2'
                                )
                            else:
                                infiles=os.path.join(
                                    COMINobs, f'ccpa.{INITDATEm}', '*', 
                                    f'ccpa.t{VHOURm}z.{OBS_ACC}h.hrap.{NEST}.gb2'
                                )
                            if not glob.glob(infiles):
                                print(f"WARNING: Currently there are no matches for"
                                      + f" {infiles}. This is normal, and these"
                                      + f" files may appear later, to be"
                                      + f" captured by another prep cycle. Will"
                                      + f" not attempt to copy into the prep"
                                      + f" archive ... Continuing to the next"
                                      + f" valid datetime.")
                                subtract_hours+=subtract_hours_inc
                                continue
                            for infile in glob.glob(infiles):
                                job_cmd_list.append(
                                    f"if [ -f \"{infile}\" ]; then cp \"{infile}\""
                                    + f" \"{COMOUTobs}/.\"; else echo \"WARNING: Input {OBSNAME}"
                                    + f" file does not exist: {infile} ..."
                                    + f" Continuing to the next valid datetime.\"; fi"
                                )
                        subtract_hours+=subtract_hours_inc
            else:
                print(f"FATAL ERROR: {OBSNAME} is not a valid reference data source")
                sys.exit(1)
        else:
            print(f"FATAL ERROR: {VERIF_CASE} is not a valid VERIF_CASE for"
                  + f" cam_precip_prep.sh (please use 'precip')")
            sys.exit(1)
    else:
        print(f"FATAL ERROR: {COMPONENT} is not a valid COMPONENT for"
              + f" cam_precip_prep.sh (please use 'cam')")
        sys.exit(1)
else:
    print(f"FATAL ERROR: {STEP} is not a valid STEP for cam_precip_prep.sh (please"
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
