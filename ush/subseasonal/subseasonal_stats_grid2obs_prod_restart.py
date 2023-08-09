#!/usr/bin/env python3
'''
Name: subseasonal_stats_grid2obs_prod_restart.py
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
if STEP == 'stats':
    VDATE = os.environ['VDATE']
    MODELNAME = os.environ['MODELNAME']
    VERIF_CASE = os.environ['VERIF_CASE']
    STEP = os.environ['STEP']
    DATA_METplus_output = os.path.join(DATA, VERIF_CASE+'_'+STEP,
                                       'METplus_output')
    COMOUT_RUN_VDATE_VERIF_CASE = glob.glob(
        os.path.join(COMOUT, RUN+'.'+VDATE, '*', VERIF_CASE)
    )
    COMOUT_RUN_VDATE_VERIF_CASE.append(
        os.path.join(COMOUT, MODELNAME+'.'+VDATE)
    )
    for COMOUT_VDATE in COMOUT_RUN_VDATE_VERIF_CASE:
        if os.path.exists(COMOUT_VDATE):
            DATA_METplus_VDATE = COMOUT_VDATE.replace(
                COMOUT, DATA_METplus_output
            ).rpartition('/')[0]
            print(f"Copying COMOUT directory {COMOUT_VDATE} directory "
                  +f"into working directory {DATA_METplus_VDATE}")
            sub_util.run_shell_command(
                ['cp', '-rpv', COMOUT_VDATE, DATA_METplus_VDATE]
            )

print("END: "+os.path.basename(__file__))
