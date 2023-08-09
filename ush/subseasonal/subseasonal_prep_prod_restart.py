#!/usr/bin/env python3
'''
Name: subseasonal_prep_prod_restart.py
Contact: Shannon Shields
Abstract:
'''

import os
import glob
import subseasonal_util as sub_util

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
if STEP == 'prep':
    VDATE = os.environ['VDATE']
    MODELNAME = os.environ['MODELNAME']
    STEP = os.environ['STEP']
    DATA_prep_output = os.path.join(DATA, STEP,
                                    'data')
    COMOUT_RUN_VDATE = glob.glob(
        os.path.join(COMOUT+'.'+VDATE, '*')
    )
    for COMOUT_VDATE in COMOUT_RUN_VDATE:
        if os.path.exists(COMOUT_VDATE):
            DATA_prep_VDATE = COMOUT_VDATE.replace(
                COMOUT, DATA_prep_output
            ).rpartition('/')[0]
            print(f"Copying COMOUT directory {COMOUT_VDATE} directory "
                  +f"into working directory {DATA_prep_VDATE}")
            sub_util.run_shell_command(
                ['cp', '-rpv', COMOUT_VDATE, DATA_prep_VDATE]
            )

print("END: "+os.path.basename(__file__))
