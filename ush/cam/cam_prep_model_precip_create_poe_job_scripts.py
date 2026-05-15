#!/usr/bin/env python3
"""
cam_prep_model_precip_create_poe_job_scripts.py
CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov
----------------------
Creates POE job scripts for Precip verification in the cam component.

Environment Variables (Inputs):
    machine, USE_CFP, nproc, STEP, VERIF_CASE, DATA
    (and other variables required for job script creation and configuration)

Outputs:
    - Generates POE job scripts for running Precip verification in parallel.
    - Prints errors and exits if required environment variables are missing or
      invalid.

This script is intended to be run as part of the cam component to automate
creation of POE job scripts for Precip verification.
"""

import glob
import os
import sys

print(f"BEGIN: {os.path.basename(__file__)}")

# Read in environment variables
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
STEP = os.environ['STEP']
VERIF_CASE = os.environ['VERIF_CASE']
DATA = os.environ['DATA']

if USE_CFP == 'YES':
    job_dir = os.path.join(DATA, VERIF_CASE, 'METplus_job_scripts')
    job_files = sorted(glob.glob(os.path.join(job_dir, 'job*')))
    if not job_files:
        print(f"NOTE: No job files created in {job_dir}")
    
    # Clean up old POE job files
    poe_job_files = glob.glob(os.path.join(job_dir, 'poe_job*'))
    for poe_job_file in poe_job_files:
        os.remove(poe_job_file)

    iproc, node = 0, 1
    for job_path in job_files:
        job_filename = os.path.basename(job_path)
        if iproc >= int(nproc):
            iproc = 0
            node += 1

        poe_job_file = os.path.join(job_dir, f'poe_jobs{node}')
        with open(poe_job_file, 'a') as poe_job:
            if machine in ['HERA', 'ORION', 'S4', 'JET']:
                poe_job.write(f'{iproc} {job_path}\n')
            else:
                poe_job.write(f'{job_path}\n')
        iproc += 1

    # Fill remaining slots with dummy echo commands
    poe_job_file = os.path.join(job_dir, f'poe_jobs{node}')
    with open(poe_job_file, 'a') as poe_job:
        while iproc < int(nproc):
            if machine in ['HERA', 'ORION', 'S4', 'JET']:
                poe_job.write(f'{iproc} /bin/echo {iproc}\n')
            else:
                poe_job.write(f'/bin/echo {iproc}\n')
            iproc += 1
else:
    print(f"FATAL ERROR: Cannot create POE scripts because USE_CFP is set to {USE_CFP}. "
          "Please set USE_CFP=YES")
    sys.exit(1)

print(f"END: {os.path.basename(__file__)}")
