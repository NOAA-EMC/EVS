'''
Name: global_det_atmos_production_restart.py
Contact(s): Mallory Row
Abstract: 
'''

import os
import glob
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
            gda_util.run_shell_command(
                ['cp', '-rpv', COMOUT_VDATE, DATA_METplus_VDATE]
            )
elif STEP == 'plots':
    end_date = str(os.environ['end_date'])
    VERIF_CASE = os.environ['VERIF_CASE']
    NDAYS = str(os.environ['NDAYS'])
    VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
    VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                                 .split(' '))
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        DATA_plot_output = os.path.join(DATA, VERIF_CASE+'_'+STEP,
                                        'plot_output', RUN+'.'+end_date,
                                        VERIF_CASE+'_'+VERIF_CASE_STEP_type)
        COMOUT_RUN_end_date_VERIF_CASE_type_NDAYS = os.path.join(
            COMOUT, VERIF_CASE+'_'+VERIF_CASE_STEP_type,
            'last'+NDAYS+'days'
        )
        if os.path.exists(COMOUT_RUN_end_date_VERIF_CASE_type_NDAYS):
            print("Copying COMOUT directory "
                  +f"{COMOUT_RUN_end_date_VERIF_CASE_type_NDAYS} directory "
                  +f"into working directory {DATA_plot_output}")
            gda_util.run_shell_command(
                ['cp', '-rpv', COMOUT_RUN_end_date_VERIF_CASE_type_NDAYS,
                 DATA_plot_output]
            )

print("END: "+os.path.basename(__file__))
