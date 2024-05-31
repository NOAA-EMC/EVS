#!/usr/bin/env python3
 
# =============================================================================
#
# NAME: mesoscale_stats_grid2obs_create_poe_job_scripts.sh
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# CONTRIBUTOR(S): RS, roshan.shrestha@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Create EVS MESOSCALE Grid2Obs - Statistics POE job scripts
# DEPENDENCIES: $SCRIPTSevs/mesoscale/stats/exevs_$MODELNAME_grid2obs_stats.sh
#
# =============================================================================

import sys
import os
import glob
from datetime import datetime
import numpy as np
import subprocess

print(f"BEGIN: {os.path.basename(__file__)}")

# Read in environment variables
job_type = os.environ['job_type']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
STEP = os.environ['STEP']
VERIF_CASE = os.environ['VERIF_CASE']
DATA = os.environ['DATA']
PBS_NODEFILE = os.environ['PBS_NODEFILE']

# If Using CFP, create POE scripts
if USE_CFP == 'YES':
    job_dir = os.path.join(DATA, VERIF_CASE, STEP, 'METplus_job_scripts', job_type)
    job_files = glob.glob(os.path.join(job_dir, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print(f"ERROR: No job files created in {job_dir}")
        sys.exit(1)
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
#--
    if machine == 'WCOSS2':
        nselect = subprocess.check_output(
            'cat '+PBS_NODEFILE+'| wc -l', shell=True, encoding='UTF-8'
        ).replace('\n', '')
        nnp = int(nselect) * int(nproc)
    else:
        nnp = nproc
#--
    iproc+=1
#    while iproc <= int(nproc):
    while iproc <= int(nnp):
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_job.write(f'{iproc-1} /bin/echo {iproc}\n')
        else:
            poe_job.write(f'/bin/echo {iproc}\n')
        iproc+=1
    poe_job.close()
else:
    print(f"ERROR: Cannot create POE scripts because USE_CFP is set to"
          + f" {USE_CFP}.  Please set USE_CFP=YES")
    sys.exit(1)

print(f"END: {os.path.basename(__file__)}")
