'''
Name: cam_production_restart.py
Contact(s): Marcel Caron
Abstract: 
'''

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
'''
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
            cutil.run_shell_command(
                ['cp', '-rpv', COMOUT_VDATE, DATA_METplus_VDATE]
            )
'''
if STEP == 'stats':
    VERIF_CASE = os.environ['VERIF_CASE']
    RESTART_DIR = os.environ['RESTART_DIR']
    working_dir = os.path.join(DATA, VERIF_CASE)
    if os.path.exists(RESTART_DIR):
        print(f"Copying restart directory {RESTART_DIR} "
              +f"into working directory {working_dir}")
        cutil.run_shell_command(
            ['cp', '-rpv', RESTART_DIR, working_dir]
        )
elif STEP == 'plots':
    COMOUTplots = os.environ['COMOUTplots']
    RESTART_DIR = os.environ['RESTART_DIR']
    SAVE_DIR = os.environ['SAVE_DIR']
    completed_jobs_file = os.path.join(RESTART_DIR, 'completed_jobs.txt')
    if os.path.exists(completed_jobs_file):
        if os.stat(completed_jobs_file).st_size != 0:
            cutil.run_shell_command(
                ['cp', '-rpv', os.path.join(RESTART_DIR,'*'), SAVE_DIR]
            )



print("END: "+os.path.basename(__file__))
