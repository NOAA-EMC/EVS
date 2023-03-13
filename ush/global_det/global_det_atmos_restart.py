'''
Name: global_det_atmos_restart.py
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
              +"into working directory {cwd}")
        gda_util.run_shell_command(
            ['cp', '-r', COMOUT_INITDATE, os.path.join(cwd, '.')]
        )
    
print("END: "+os.path.basename(__file__))
