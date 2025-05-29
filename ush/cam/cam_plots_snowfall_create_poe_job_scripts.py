#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_plots_snowfall_create_poe_job_scripts.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Create EVS CAM Snowfall - Plots POE job scripts
# DEPENDENCIES: $SCRIPTSevs/cam/plots/exevs_$MODELNAME_snowfall_plots.sh
#
# =============================================================================

import sys
import os
import glob
from datetime import datetime
import numpy as np

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
