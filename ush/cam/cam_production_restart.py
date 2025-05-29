#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_production_restart.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Check the appropriate restart directory for restart files and copy
#          the available files to the working directory
#
# =============================================================================

import os
import glob
from pathlib import Path
import cam_util as cutil

print("BEGIN: "+os.path.basename(__file__))

cwd = os.getcwd()
print("Working in: "+cwd)

# Read in common environment variables
DATA = os.environ['DATA']
COMOUT = os.environ['COMOUT']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']
VERIF_CASE = os.environ['VERIF_CASE']

# Copy files for restart
if STEP == 'stats':
    VERIF_CASE = os.environ['VERIF_CASE']
    RESTART_DIR = os.environ['RESTART_DIR']
    COMPLETED_JOBS_DIR = os.environ['COMPLETED_JOBS_DIR']
    working_dir = os.path.join(DATA, VERIF_CASE)
    completed_jobs_dir = os.path.join(
        RESTART_DIR, COMPLETED_JOBS_DIR
    )
    if os.path.exists(RESTART_DIR):
        if (os.path.exists(completed_jobs_dir) 
                and any(p.is_file() for p in Path(completed_jobs_dir).rglob('*'))):
            print(f"Copying restart directory {RESTART_DIR} "
                  +f"into working directory {working_dir}")
            cutil.run_shell_command(
                ['cp', '-rpv', RESTART_DIR, working_dir]
            )
elif STEP == 'plots':
    COMOUTplots = os.environ['COMOUTplots']
    RESTART_DIR = os.environ['RESTART_DIR']
    COMPLETED_JOBS_DIR = os.environ['COMPLETED_JOBS_DIR']
    working_dir = os.path.join(DATA, VERIF_CASE, 'out')
    if VERIF_CASE == "grid2obs":
        completed_jobs_dir = os.path.join(
            RESTART_DIR, 
            COMPLETED_JOBS_DIR
        )
    elif VERIF_CASE == "precip":
        completed_jobs_dir = os.path.join(
            RESTART_DIR, 
            COMPLETED_JOBS_DIR
        )
    else:
        completed_jobs_dir = os.path.join(
            RESTART_DIR, 
            COMPLETED_JOBS_DIR
        )
    if os.path.exists(completed_jobs_dir):
        if any(p.is_file() for p in Path(completed_jobs_dir).rglob('*')):
            print(f"Copying restart directory {RESTART_DIR} "
                  +f"into working directory {working_dir}")
            cutil.run_shell_command(
                ['cp', '-rpv', os.path.join(RESTART_DIR,'*'), working_dir]
            )


print("END: "+os.path.basename(__file__))
