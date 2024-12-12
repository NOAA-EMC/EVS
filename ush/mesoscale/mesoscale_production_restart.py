#!/usr/bin/env python3
'''
Name: mesoscale_production_restart.py
Contact(s): Marcel Caron
Abstract:
'''

import os
import glob
import mesoscale_util as cutil

print("BEGIN: "+os.path.basename(__file__))

cwd = os.getcwd()
print("Working in: "+cwd)

# Read in common environment variables
DATA = os.environ['DATA']
COMOUT = os.environ['COMOUT']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']

# Copy files for restart
if STEP == 'plots':
    COMOUTplots = os.environ['COMOUTplots']
    RESTART_DIR = os.environ['RESTART_DIR']
    COMPLETED_JOBS_FILE = os.environ['COMPLETED_JOBS_FILE']
    working_dir = os.path.join(DATA, VERIF_CASE, 'out')
    completed_jobs_file = os.path.join(RESTART_DIR, COMPLETED_JOBS_FILE)
    if os.path.exists(completed_jobs_file):
        if os.stat(completed_jobs_file).st_size != 0:
            cutil.run_shell_command(
                ['cp', '-rpv', os.path.join(RESTART_DIR,'*'), working_dir]
            )

print("END: "+os.path.basename(__file__))
