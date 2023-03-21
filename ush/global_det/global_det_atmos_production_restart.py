'''
Name: global_det_atmos_production_restart.py
Contact(s): Mallory Row
Abstract: 
'''

import os
import global_det_atmos_util as gda_util

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

# Do prep restart
if STEP == 'prep':
    INITDATE = os.environ['INITDATE']
    COMOUT_INITDATE = COMOUT+'.'+INITDATE
    if os.path.exists(COMOUT_INITDATE):
        print(f"Copying COMOUT {COMOUT_INITDATE} directory "
              +f"into working directory {cwd}")
        gda_util.run_shell_command(
            ['cp', '-rpv', COMOUT_INITDATE, os.path.join(cwd, '.')]
        )
elif STEP == 'stats':
    VDATE = os.environ['VDATE']
    MODELNAME = os.environ['MODELNAME']
    VERIF_CASE = os.environ['VERIF_CASE']
    STEP = os.environ['STEP']
    DATA_METplus_output = os.path.join(DATA, VERIF_CASE+'_'+STEP,
                                       'METplus_output')
    COMOUT_RUN_VDATE = os.path.join(COMOUT, RUN+'.'+VDATE)
    COMOUT_MODELNAME_VDATE = os.path.join(COMOUT, MODELNAME+'.'+VDATE)
    for COMOUT_VDATE in [COMOUT_RUN_VDATE, COMOUT_MODELNAME_VDATE]:
        if os.path.exists(COMOUT_VDATE):
            print(f"Copying COMOUT directory {COMOUT_VDATE} directory "
                  +f"into working directory {DATA_METplus_output}")
            gda_util.run_shell_command(
                ['cp', '-rpv', COMOUT_VDATE,
                 os.path.join(DATA_METplus_output, '.')]
            )

print("END: "+os.path.basename(__file__))
