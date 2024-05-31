#!/usr/bin/env python3
# =============================================================================
#
# NAME: mesoscale_get_data_files.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: 
# DEPENDENCIES: os.path.join([
#                   SCRIPTSevs,COMPONENT,STEP,
#                   "_".join(["exevs",MODELNAME,VERIF_CASE,STEP+".sh"]
#               )]
#
# =============================================================================

import os
import datetime

print(f"BEGIN: {os.path.basename(__file__)}")

# Read in common environment variables
RUN = os.environ['RUN']
NET = os.environ['NET']
COMPONENT = os.environ['COMPONENT']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
DATA = os.envoron['DATA']
MODELNAME = os.environ['MODELNAME']
COMINfcst = os.environ['COMINfcst']
MODEL_INPUT_TEMPLATE = os.environ['MODEL_INPUT_TEMPLATE']
VDATE = os.environ['VDATE']
USER = os.environ['USER']
evs_run_mode = os.environ['evs_run_mode']
config = os.environ['config']
if STEP == 'stats':
    COMINobs = os.environ['COMINobs']
    VHOUR = os.environ['VHOUR']
    FHR_START = os.environ['FHR_START']
    FHR_END = os.environ['FHR_END']
    FHR_INCR = os.environ['FHR_INCR']
if evs_run_mode != 'production':
    machine = os.environ['machine']

# Read in case-dependent variables
if VERIF_CASE == 'precip':
    if STEP == 'stats':
        ACC = os.environ['ACC']
        MODEL_ACC = os.environ['MODEL_ACC']
        OBS_ACC = os.environ['OBS_ACC']
        
# Check current working directory
cwd = os.getcwd()
if cwd != DATA:
    print(f"Changing current working directory to {DATA}")
    os.chdir(DATA)

# Check variables

if VERIF_CASE == 'precip':
    if STEP == 'stats':
        if int(MODEL_ACC) <= 0:
            print(f"ERROR: MODEL_ACC is set to {MODEL_ACC}, but must be a"
                  + f" positive integer. Please check the configuration file:"
                  + f" {config}")
            sys.exit(1)
        elif int(MODEL_ACC) > int(FHR_START):
            print(f"ERROR: MODEL_ACC is set to {MODEL_ACC}, and is larger"
                  + f" than the FHR_START ({FHR_START}), which is not allowed."
                  + f" Please check the configuration file: {config}")
            sys.exit(1)
        if int(OBS_ACC) <= 0:
            print(f"ERROR: OBS_ACC is set to {OBS_ACC}, but must be a"
                  + f" positive integer. Please check the configuration file:"
                  + f" {config}")
            sys.exit(1)
        elif int(OBS_ACC) > int(FHR_START):
            print(f"ERROR: OBS_ACC is set to {OBS_ACC}, and is larger"
                  + f" than the FHR_START ({FHR_START}), which is not allowed."
                  + f" Please check the configuration file: {config}")
            sys.exit(1)
        if int(ACC) <= 0:
            print(f"ERROR: ACC is set to {ACC}, but must be a"
                  + f" positive integer. Please check the configuration file:"
                  + f" {config}")
            sys.exit(1)
        elif int(ACC) > int(FHR_START):
            print(f"ERROR: ACC is set to {ACC}, and is larger"
                  + f" than the FHR_START ({FHR_START}), which is not allowed."
                  + f" Please check the configuration file: {config}")
            sys.exit(1)
        elif int(ACC) < int(MODEL_ACC):
            print(f"ERROR: ACC is set to {ACC}, and is smaller than the"
                  + f" MODEL_ACC ({MODEL_ACC}), which is not allowed."
                  + f" Please check the configuration file: {config}")
            sys.exit(1)
        elif int(ACC) < int(OBS_ACC):
            print(f"ERROR: ACC is set to {ACC}, and is smaller than the"
                  + f" OBS_ACC ({OBS_ACC}), which is not allowed."
                  + f" Please check the configuration file: {config}")
            sys.exit(1)
                 





