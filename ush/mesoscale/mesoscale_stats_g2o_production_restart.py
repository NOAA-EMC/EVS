# =============================================================================
#
# NAME: mesoscale_stats_g2o_production_restart.py
# CONTRIBUTOR(S): Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# CONTRIBUTOR(S): RS, roshan.shrestha@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Make files ready for restart 
#
# =============================================================================


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
STEP = os.environ['STEP']

# Copy files for restart
if STEP == 'stats':
    VDATE = os.environ['VDATE']
    MODELNAME = os.environ['MODELNAME']
    VERIF_CASE = os.environ['VERIF_CASE']
    VERIF_TYPE = os.environ['VERIF_TYPE']
    STEP = os.environ['STEP']

    DATA_METplus_output = os.path.join(DATA, VERIF_CASE,
                                       'METplus_output')
    
    COMOUT_RUN_VDATE_VERIF_CASE = glob.glob(
        os.path.join(COMOUT, RUN+'.'+VDATE, '*', VERIF_CASE)
    )

    COMOUT_RUN_VDATE_VERIF_CASE.append(
        os.path.join(COMOUT, MODELNAME+'.'+VDATE)
    )

    DAT1 = DATA.rsplit('/',1)[0]
    COMOUT_RUN_VDATE_VERIF_CASE3 = glob.glob(
        os.path.join(VERIF_CASE,'METplus_output',VERIF_TYPE+'/point_stat',
                     MODELNAME+'.'+VDATE)
    )
    DAT2 = cutil.run_shell_commandc(
            ['find', DAT1, '-type d | grep', VERIF_CASE, '| grep', 
             VERIF_TYPE+'/point_stat', '| grep', MODELNAME+'.'+VDATE,
             '| sort | uniq']
            )
    DAT3 = DAT2.splitlines()
    for DAT4 in DAT3:
        print(f"DAT4 = {DAT4}")
        COMOUT_RUN_VDATE_VERIF_CASE.append(
            DAT4
        )

    DATA_METplus_V = os.path.join(DATA_METplus_output, VERIF_TYPE+'/point_stat')
    for COMOUT_VDATE in COMOUT_RUN_VDATE_VERIF_CASE:
        if os.path.exists(COMOUT_VDATE):
            DATA_METplus_VDATE = COMOUT_VDATE.replace(
                COMOUT, DATA_METplus_output
            ).rpartition('/')[0]
            DATA_METplus_VDATE = os.path.join(DATA_METplus_V, MODELNAME+'.'+VDATE)
            
            cutil.run_shell_command(
                ['mkdir', '-p', DATA_METplus_VDATE]
            )

            CN = os.system('ls '+COMOUT_VDATE+'/ | wc -l')
            if ( CN > 0):
                print(f"Copying COMOUT directory {COMOUT_VDATE} directory "                                    +f"into working directory {DATA_METplus_VDATE}")
                cutil.run_shell_command(
                    ['cp', '-pv', COMOUT_VDATE+'/*.*', DATA_METplus_VDATE+'/']
                )


print("END: "+os.path.basename(__file__))
