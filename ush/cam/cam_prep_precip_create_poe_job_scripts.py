#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_prep_precip_create_poe_job_scripts.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Create EVS CAM Precipitation - Prepare POE job scripts
# DEPENDENCIES: $SCRIPTSevs/cam/prep/exevs_$MODELNAME_precip_prep.sh
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
    job_dir = os.path.join(DATA, VERIF_CASE, STEP, 'prep_job_scripts')
    job_files = glob.glob(os.path.join(job_dir, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print(f"NOTE: No job files created in {job_dir}")
    poe_job_files = glob.glob(os.path.join(job_dir, f'poe_job*'))
    npoe_job_files = len(poe_job_files)
    if npoe_job_files > 0:
        for poe_job_file in poe_job_files:
            os.remove(poe_job_file)
    njob, iproc, node = 1, 0, 1
    while njob <= njob_files:
        job_filename = f'job{njob}'
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            if iproc >= int(nproc):
                iproc = 0
                node+=1
        poe_job_file = os.path.join(job_dir, f'poe_jobs{node}')
        poe_job = open(poe_job_file, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_job.write(f'{iproc-1} {os.path.join(job_dir, job_filename)}\n')
        else:
            poe_job.write(f'{os.path.join(job_dir, job_filename)}\n')
        poe_job.close()
        njob+=1
    poe_job_file = os.path.join(job_dir, f'poe_jobs{node}')
    poe_job = open(poe_job_file, 'a')
    iproc+=1
    while iproc <= int(nproc):
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_job.write(f'{iproc-1} /bin/echo {iproc}\n')
        else:
            poe_job.write(f'/bin/echo {iproc}\n')
        iproc+=1
    poe_job.close()
else:
    print(f"FATAL ERROR: Cannot create POE scripts because USE_CFP is set to"
          + f" {USE_CFP}.  Please set USE_CFP=YES")
    sys.exit(1)

print(f"END: {os.path.basename(__file__)}")
