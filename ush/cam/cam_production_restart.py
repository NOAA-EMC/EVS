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

# Copy files for restart
if STEP == 'stats':
    VERIF_CASE = os.environ['VERIF_CASE']
    RESTART_DIR = os.environ['RESTART_DIR']
    working_dir = os.path.join(DATA, VERIF_CASE)
    completed_jobs_file = os.path.join(RESTART_DIR, 'completed_jobs.txt')
    if os.path.exists(RESTART_DIR):
        if (os.path.exists(completed_jobs_file) 
                and os.stat(completed_jobs_file).st_size != 0):
            print(f"Copying restart directory {RESTART_DIR} "
                  +f"into working directory {working_dir}")
            cutil.run_shell_command(
                ['cpreq', '-rpv', RESTART_DIR, working_dir]
            )
elif STEP == 'plots':
    COMOUTplots = os.environ['COMOUTplots']
    RESTART_DIR = os.environ['RESTART_DIR']
    SAVE_DIR = os.environ['SAVE_DIR']
    completed_jobs_file = os.path.join(RESTART_DIR, 'completed_jobs.txt')
    if os.path.exists(completed_jobs_file):
        if os.stat(completed_jobs_file).st_size != 0:
            cutil.run_shell_command(
                ['cpreq', '-rpv', os.path.join(RESTART_DIR,'*'), SAVE_DIR]
            )



print("END: "+os.path.basename(__file__))
