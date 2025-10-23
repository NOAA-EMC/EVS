#!/usr/bin/env python3
"""
cam_plots_snowfall_create_poe_job_scripts.py
CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov
----------------------
Creates POE (parallel execution) job scripts for EVS CAM Snowfall plots in the
cam component.

Environment Variables (Inputs):
    machine, USE_CFP, nproc, STEP, VERIF_CASE, DATA, and others required for
    job script creation and parallelization.

Outputs:
    - Generates POE job scripts for parallel plotting execution.
    - Prints notes if no job files are found or if required environment
      variables are missing.

This script is intended to be run as part of the cam component to automate
creation of POE job scripts for Snowfall plotting.
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

# If Using CFP, create POE scripts
if USE_CFP == 'YES':
    job_dir = os.path.join(DATA, VERIF_CASE, 'plotting_job_scripts')
    job_files = glob.glob(os.path.join(job_dir, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print(f"NOTE: No job files created in {job_dir}")

    # Remove any existing poe_job* files
    for poe_job_file in glob.glob(os.path.join(job_dir, 'poe_job*')):
        os.remove(poe_job_file)

    njob, iproc, node = 1, 0, 1
    while njob <= njob_files:
        job_filename = f'job{njob}'
        job_path = os.path.join(job_dir, job_filename)

        if not os.path.isfile(job_path):
            njob += 1
            continue

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
        njob += 1

    # Fill remaining processors with /bin/echo commands
    poe_job_file = os.path.join(job_dir, f'poe_jobs{node}')
    with open(poe_job_file, 'a') as poe_job:
        while iproc < int(nproc):
            if machine in ['HERA', 'ORION', 'S4', 'JET']:
                poe_job.write(f'{iproc} /bin/echo {iproc}\n')
            else:
                poe_job.write(f'/bin/echo {iproc}\n')
            iproc += 1

else:
    print(f"FATAL ERROR: Cannot create POE scripts because USE_CFP is set to {USE_CFP}. Please set USE_CFP=YES")
    sys.exit(1)

print(f"END: {os.path.basename(__file__)}")
