#!/usr/bin/env python3
"""
cam_production_restart.py
CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
----------------------
Checks the appropriate restart directory for restart files and copies the
available files to the working directory for the cam component.

Environment Variables (Inputs):
    DATA, COMOUT, NET, RUN, COMPONENT, STEP, VERIF_CASE, RESTART_DIR,
    COMPLETED_JOBS_DIR

Outputs:
    - Copies restart files from the restart directory to the working directory.

This script is intended to be run as part of the cam component to automate
the management of restart files during production runs.
"""

import os
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
if STEP == 'prep':
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
elif STEP == 'stats':
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
    if VERIF_CASE in ['radar','severe']:
        working_dir = os.path.join(DATA, 'out')
    else:
        working_dir = os.path.join(DATA, VERIF_CASE, 'out')
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
