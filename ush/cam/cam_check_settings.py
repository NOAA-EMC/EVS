#!/usr/bin/env python3
"""
cam_check_settings.py
CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov
----------------------
Checks the user's environment and configuration settings for the cam component.

Environment Variables (Inputs):
        Various variables including machine, VERIF_CASE, STEP, config, and many
        others required for different workflow steps.

Outputs:
        - Prints fatal errors and exits if required environment variables are
            missing or if date/time formats are invalid.
        - Ensures all necessary configuration is present before proceeding with
            downstream steps.

This script is intended to be run as part of the cam component to
validate user and system settings before workflow execution.
"""

import calendar
import os
import re
import sys

print(f"BEGIN: {os.path.basename(__file__)}")

# Read in initial environment variables
top_level_env_vars = ['machine', 'VERIF_CASE', 'STEP', 'config']
for env_var in top_level_env_vars:
    if not env_var in os.environ:
        print(f"FATAL ERROR: variable \"{env_var}\" is not set in environment, "
              + f"review parent scripts.")
        sys.exit(1)
machine = os.environ['machine']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
config = os.environ['config']

# Set up a dictionary of variables to check for existence in the environment
evs_cam_settings_dict = {}
evs_cam_settings_dict['evs'] = [
    'model', 'machine', 'envir', 'SENDCOM', 'KEEPDATA', 'job', 'jobid', 'USE_CFP', 'nproc', 'NET', 
    'HOMEevs', 'config', 'evs_ver', 'ccpa_ver', 'obsproc_ver', 'pid', 'DATA', 
    'STEP', 'COMPONENT', 'RUN', 'VERIF_CASE',
    'HOMEevs', 'config', 'evs_ver', 'ccpa_ver', 'obsproc_ver', 'pid', 'DATA', 
    'COMIN', 'COMOUT', 'PARMevs', 'USHevs', 'EXECevs', 
    'FIXevs'
]
evs_cam_settings_dict['shared'] = []
evs_cam_settings_dict['modules'] = ['METPLUS_PATH', 'MET_ROOT']
evs_cam_settings_dict['RUN_GRID2OBS_PREP'] = [
        'MET_PLUS_CONF','MET_PLUS_OUT',
        'NEST','URL_HEAD','INITDATE'
        ]
evs_cam_settings_dict['RUN_GRID2OBS_STATS'] = ['RESTART_DIR', 'bufr_ROOT','VDATE']
evs_cam_settings_dict['RUN_GRID2OBS_PLOTS'] = [
        'MET_VERSION','IMG_HEADER','PRUNE_DIR','SAVE_DIR','LOG_TEMPLATE',
        'LOG_LEVEL','STAT_OUTPUT_BASE_DIR','STAT_OUTPUT_BASE_TEMPLATE',
        'COMOUTplots','RESTART_DIR','VDATE'
        ]
evs_cam_settings_dict['RUN_PRECIP_PREP'] = [
        'VERIF_TYPE', 'ACC','INITDATE'
        ]
evs_cam_settings_dict['RUN_PRECIP_STATS'] = [
        'MET_PLUS_CONF','MET_PLUS_OUT','MET_CONFIG_OVERRIDES', 
        'VHOUR','FHR_END_SHORT','FHR_INCR_SHORT','FHR_END_FULL',
        'FHR_INCR_FULL','COMINfcst','COMINobs','NEST',
        'OBSNAME','MIN_IHOUR','MODEL_ACC','OBS_ACC','ACC','BOOL_NBRHD','FCST_LEV',
        'FCST_THRESH','OBS_LEV','OBS_THRESH','OUTPUT_FLAG_NBRHD',
        'OUTPUT_FLAG_CATEG','NBRHD_WIDTHS','GRID','MODEL_INPUT_TEMPLATE',
        'MASK_POLY_LIST','RESTART_DIR','VDATE'
        ]
evs_cam_settings_dict['RUN_PRECIP_PLOTS'] = ['COMOUTplots','RESTART_DIR','VDATE']
evs_cam_settings_dict['RUN_SNOWFALL_PREP'] = ['INITDATE']
evs_cam_settings_dict['RUN_SNOWFALL_STATS'] = ['RESTART_DIR','VDATE']
evs_cam_settings_dict['RUN_SNOWFALL_PLOTS'] = ['COMOUTplots','RESTART_DIR','VDATE']
evs_cam_settings_dict['RUN_HEADLINE_PREP'] = ['INITDATE']
evs_cam_settings_dict['RUN_HEADLINE_STATS'] = ['VDATE']
evs_cam_settings_dict['RUN_HEADLINE_PLOTS'] = [
        'MET_VERSION','IMG_HEADER','PRUNE_DIR','SAVE_DIR','LOG_TEMPLATE',
        'LOG_LEVEL','STAT_OUTPUT_BASE_DIR','STAT_OUTPUT_BASE_TEMPLATE',
        'COMOUTplots','RESTART_DIR','VDATE']

# Check for existence of required env vars, by group in the dictionary
env_group_list = [
    'evs', 'shared', 'modules', 'RUN_'+VERIF_CASE.upper()+'_'+STEP.upper()
]
for env_group in env_group_list:
    env_var_list = evs_cam_settings_dict[env_group]
    for env_var in env_var_list:
        if not env_var in os.environ:
            if env_group == 'modules':
                print(f"FATAL ERROR: {env_var} is not set in environment, "
                      + f"review modules loaded in evs_setup_{machine}.sh")
            elif env_group == 'evs':
                print(f"FATAL ERROR: {env_var} is not set in environment, "
                      + "check parent scripts")
            else:
                print(f"FATAL ERROR: {env_var} is not set in environment, "
                      + f"check configuration file: {config}")
            sys.exit(1)

# Check for invalid date and time configurations
if STEP.upper() == 'PREP':
    date_name_list = ['INITDATE']
else:
    date_name_list = ['VDATE']
for date_name in date_name_list:
    date = os.environ[date_name]
    if len(date) != 8:
        print(f"FATAL ERROR: {date_name} is not in YYYYMMDD format")
        sys.exit(1)
    date_year = int(date[0:4])
    date_month = int(date[4:6])
    date_day = int(date[6:])
    if date_year <= 0:
        print(f"FATAL ERROR: Year value of {date_year:04d} in {date} is invalid."
              + f" Check {date_name} variable in config file: {config}")
        sys.exit(1)
    if date_month > 12 or date_month <= 0:
        print(f"FATAL ERROR: Month value of {date_month:02d} in {date} is invalid."
              + f" Check {date_name} variable in config file: {config}")
        sys.exit(1)
    if date_day > calendar.monthrange(date_year, date_month)[1]:
        print(f"FATAL ERROR: Day value of {date_day:02d} in {date} is invalid."
              + f" Check {date_name} variable in config file: {config}")
        sys.exit(1)

# Check for invalid values of variables that only have a few valid options
valid_config_var_values_dict = {
    'KEEPDATA': ['YES', 'NO'],
    'SENDCOM': ['YES', 'NO'],
}
if STEP.upper() == 'PREP':
    if VERIF_CASE.upper() == 'GRID2OBS':
        valid_config_var_values_dict['NEST'] = ['spc_otlk', 'conus']
if STEP.upper() == 'STATS':
    valid_config_var_values_dict['NEST'] = ['ak', 'conus', 'subreg', 'spc_otlk', 'firewx', 'hi', 'pr', 'gu']
    valid_config_var_values_dict['BOOL_NBRHD'] = ['True', 'False']
    valid_config_var_values_dict['OUTPUT_FLAG_NBRHD'] = ['NONE', 'STAT', 'BOTH']
    valid_config_var_values_dict['OUTPUT_FLAG_CATEG'] = ['NONE', 'STAT', 'BOTH']
for env_var in list(valid_config_var_values_dict.keys()):
    if env_var in os.environ:
        if 'LIST' in env_var.upper():
                for list_item in re.split(r'[,\s]+', os.environ[env_var]):
                    if list_item not in valid_config_var_values_dict[env_var]:
                        env_var_pass = False
                        failed_config_value = list_item
                    else:
                        env_var_pass = True
        else:
            if os.environ[env_var] not in valid_config_var_values_dict[env_var]:
                env_var_pass = False
                failed_config_value = os.environ[env_var]
            else: 
                env_var_pass = True
        if not env_var_pass:
            print(f"FATAL ERROR: The {env_var} value of {failed_config_value} is not a"
                  + f" valid option. Valid options are"
                  + f" {', '.join(valid_config_var_values_dict[env_var])}")
            sys.exit(1)
    else:
            continue

print(f"END: {os.path.basename(__file__)}")

# Get values for other environment variables
RUN = os.environ['RUN']
NET = os.environ['NET']
COMPONENT = os.environ['COMPONENT']
DATA = os.environ['DATA']
MODELNAME = os.environ['MODELNAME']
USER = os.environ['USER']
if STEP == 'stats':
    MODEL_INPUT_TEMPLATE = os.environ['MODEL_INPUT_TEMPLATE']
    COMINfcst = os.environ['COMINfcst']
    COMINobs = os.environ['COMINobs']
    VHOUR = os.environ['VHOUR']
if VERIF_CASE == 'precip':
    if STEP == 'prep':
        ACC = os.environ['ACC']
        if MODELNAME != "cam":
            COMINfcst = os.environ['COMINfcst']
            MODEL_INPUT_TEMPLATE = os.environ['MODEL_INPUT_TEMPLATE']
            FHR_END_SHORT = os.environ['FHR_END_SHORT']
            FHR_INCR_SHORT = os.environ['FHR_INCR_SHORT']
            FHR_END_FULL = os.environ['FHR_END_FULL']
            FHR_INCR_FULL = os.environ['FHR_INCR_FULL']
            MIN_IHOUR = os.environ['MIN_IHOUR']
            ACC = os.environ['ACC']
            MODEL_ACC = os.environ['MODEL_ACC']
            IHOUR_LIST = os.environ['IHOUR_LIST']
        else:
            COMINobs = os.environ['COMINobs']
            OBS_ACC = os.environ['OBS_ACC']
            VHOUR_LIST = os.environ['VHOUR_LIST']
    if STEP == 'stats':
        MASK_POLY_LIST=os.environ['MASK_POLY_LIST']
        FHR_END_SHORT = os.environ['FHR_END_SHORT']
        FHR_INCR_SHORT = os.environ['FHR_INCR_SHORT']
        FHR_END_FULL = os.environ['FHR_END_FULL']
        FHR_INCR_FULL = os.environ['FHR_INCR_FULL']
        MIN_IHOUR = os.environ['MIN_IHOUR']
        ACC = os.environ['ACC']
        MODEL_ACC = os.environ['MODEL_ACC']
        OBS_ACC = os.environ['OBS_ACC']
        NBRHD_WIDTHS=os.environ['NBRHD_WIDTHS']
elif VERIF_CASE == 'grid2obs':
    if STEP == 'stats':
        FHR_END_SHORT = os.environ['FHR_END_SHORT']
        FHR_INCR_SHORT = os.environ['FHR_INCR_SHORT']
        FHR_END_FULL = os.environ['FHR_END_FULL']
        FHR_INCR_FULL = os.environ['FHR_INCR_FULL']
        MIN_IHOUR = os.environ['MIN_IHOUR']
    
# Check current working directory
cwd = os.getcwd()
if cwd != DATA:
    print(f"Changing current working directory to {DATA}")
    os.chdir(DATA)

# Check whether or not configured directories exist
env_dir_list = ['DATA']
env_file_list = []
if STEP == 'prep':
    env_dir_list.append('METPLUS_PATH')
    env_dir_list.append('MET_ROOT')
    if VERIF_CASE == 'precip':
        if MODELNAME != 'cam':
            env_dir_list.append('COMINfcst')
        else:
            env_dir_list.append('COMINobs')
    if VERIF_CASE == 'grid2obs':
        env_dir_list.append('METPLUS_PATH')
        env_dir_list.append('MET_ROOT')
if STEP == 'stats':
    env_dir_list.append('METPLUS_PATH')
    env_dir_list.append('MET_ROOT')
    env_dir_list.append('COMINobs')
    env_dir_list.append('COMINfcst')
    if VERIF_CASE == 'precip':
        env_file_list.append('MASK_POLY_LIST')
if STEP == 'plots':
    env_dir_list.append('STAT_OUTPUT_BASE_DIR')
for env_dir in env_dir_list:
    if 'LIST' in env_dir.upper():
        for list_item in re.split(r'[,\s]+', os.environ[env_dir]):
            if not os.path.isdir(list_item):
                print(f"WARNING: {list_item} does not exist. Check {env_dir}"
                      + f" in parent scripts.")
    else:
        if not os.path.isdir(os.environ[env_dir]):
            print(f"WARNING: {os.environ[env_dir]} does not exist. Check"
                  + f" {env_dir} in parent scripts.")

for env_file in env_file_list:
    if 'LIST' in env_file.upper():
        for list_item in re.split(r'[,\s]+', os.environ[env_file]):
            if not os.path.exists(list_item):
                print(f"WARNING: {list_item} does not exist. Check {env_file}"
                      + f" in parent scripts.")
    else:
        if not os.path.exists(os.environ[env_file]):
            print(f"WARNING: {os.environ[env_file]} does not exist. Check"
                  + f" {env_file} in parent scripts.")

# Check whether or not other variables are invalid
if STEP == 'prep':
    if VERIF_CASE == 'precip':
            if MODELNAME == "cam":
                for VHOUR in re.split(r'[\s,]+', VHOUR_LIST.strip()):
                    if int(VHOUR) < 0 or int(VHOUR) > 23:
                        if int(VHOUR) == 24:
                            print(f"FATAL ERROR: VHOUR is set to {VHOUR}, which is equivalent to 00."
                                  + f" Please change the VHOUR to 00 instead in {config}.")
                            sys.exit(1)
                        else:
                            print(f"FATAL ERROR: VHOUR is set to {VHOUR}, which is not a valid time"
                                  + f" of day. Please set VHOUR to a two-digit integer between"
                                  + f"00 and 23 in {config}.")
                            sys.exit(1)
            else:
                if int(MIN_IHOUR) < 0 or int(MIN_IHOUR) > 23:
                    if int(MIN_IHOUR) == 24:
                        print(f"FATAL ERROR: MIN_IHOUR is set to {MIN_IHOUR}, which is equivalent to 00."
                              + f" Please change the MIN_IHOUR to 00 instead in {config}.")
                        sys.exit(1)
                    else:
                        print(f"FATAL ERROR: MIN_IHOUR is set to {MIN_IHOUR}, which is not a valid time"
                              + f" of day. Please set MIN_IHOUR to a two-digit integer between"
                              + f"00 and 23 in {config}.")
                        sys.exit(1)
                if int(FHR_END_SHORT) < 0:
                    print(f"FATAL ERROR: FHR_END_SHORT is set to {FHR_END_SHORT}, which is invalid."
                          + f" Please set FHR_END_SHORT to a positive integer in {config}.")
                    sys.exit(1)
                if int(FHR_INCR_SHORT) < 0:
                    print(f"FATAL ERROR: FHR_INCR_SHORT is set to {FHR_INCR_SHORT}, which is invalid."
                          + f" Please set FHR_INCR_SHORT to a positive integer in {config}.")
                    sys.exit(1)
                if int(FHR_END_FULL) < 0:
                    print(f"FATAL ERROR: FHR_END_FULL is set to {FHR_END_FULL}, which is invalid."
                          + f" Please set FHR_END_FULL to a positive integer in {config}.")
                    sys.exit(1)
                if int(FHR_INCR_FULL) < 0:
                    print(f"FATAL ERROR: FHR_INCR_FULL is set to {FHR_INCR_FULL}, which is invalid."
                          + f" Please set FHR_INCR_FULL to a positive integer in {config}.")
                    sys.exit(1)
                for IHOUR in re.split(r'[\s,]+', IHOUR_LIST.strip()):
                    if int(IHOUR) < 0 or int(IHOUR) > 23:
                        if int(IHOUR) == 24:
                            print(f"FATAL ERROR: IHOUR is set to {IHOUR}, which is equivalent to 00."
                                  + f" Please change the IHOUR to 00 instead in {config}.")
                            sys.exit(1)
                        else:
                            print(f"FATAL ERROR: IHOUR is set to {IHOUR}, which is not a valid time"
                                  + f" of day. Please set IHOUR to a two-digit integer between"
                                  + f"00 and 23 in {config}.")
                            sys.exit(1)
                for MODEL_ACC_i in re.split(r'[,\s]+', MODEL_ACC):
                    for ACC_i in re.split(r'[,\s]+', ACC):
                        if len(MODEL_ACC_i) != 2:
                            print(f"FATAL ERROR: MODEL_ACC is set to {MODEL_ACC_i}, which has"
                                  + f" {len(MODEL_ACC_i)} digits, but two digits are required."
                                  + f" Please check the configuration file: {config}")
                            sys.exit(1)
                        if int(MODEL_ACC_i) <= 0:
                            print(f"FATAL ERROR: MODEL_ACC is set to {MODEL_ACC_i}, but must be a"
                                  + f" positive integer. Please check the configuration file:"
                                  + f" {config}")
                            sys.exit(1)
                        if len(ACC_i) != 2:
                            print(f"FATAL ERROR: ACC is set to {ACC_i}, which has"
                                  + f" {len(ACC_i)} digits, but two digits are required."
                                  + f" Please check the configuration file: {config}")
                            sys.exit(1)
                        if int(ACC_i) <= 0:
                            print(f"FATAL ERROR: ACC is set to {ACC_i}, but must be a"
                                  + f" positive integer. Please check the configuration file:"
                                  + f" {config}")
                            sys.exit(1)
                        elif int(ACC_i) < int(MODEL_ACC_i):
                            print(f"WARNING: ACC is set to {ACC_i}, and is smaller than the"
                                  + f" MODEL_ACC ({MODEL_ACC_i}), which will cause an error"
                                  + f" if no other options are listed. Please check the"
                                  + f" configuration file: {config}")
                if len(ACC) != 2:
                    print(f"FATAL ERROR: ACC is set to {ACC}, which has"
                          + f" {len(ACC)} digits, but two digits are required."
                          + f" Please check the configuration file: {config}")
                    sys.exit(1)
                elif int(ACC) <= 0:
                    print(f"FATAL ERROR: ACC is set to {ACC}, but must be a"
                          + f" positive integer. Please check the configuration file:"
                          + f" {config}")
                    sys.exit(1)
if STEP == 'stats':
    if int(VHOUR) < 0 or int(VHOUR) > 23:
        if int(VHOUR) == 24:
            print(f"FATAL ERROR: VHOUR is set to {VHOUR}, which is equivalent to 00."
                  + f" Please change the VHOUR to 00 instead in {config}.")
            sys.exit(1)
        else:
            print(f"FATAL ERROR: VHOUR is set to {VHOUR}, which is not a valid time"
                  + f" of day. Please set VHOUR to a two-digit integer between"
                  + f"00 and 23 in {config}.")
            sys.exit(1)
    if VERIF_CASE == 'precip':
        if int(MIN_IHOUR) < 0 or int(MIN_IHOUR) > 23:
            if int(MIN_IHOUR) == 24:
                print(f"FATAL ERROR: MIN_IHOUR is set to {MIN_IHOUR}, which is equivalent to 00."
                      + f" Please change the MIN_IHOUR to 00 instead in {config}.")
                sys.exit(1)
            else:
                print(f"FATAL ERROR: MIN_IHOUR is set to {MIN_IHOUR}, which is not a valid time"
                      + f" of day. Please set MIN_IHOUR to a two-digit integer between"
                      + f"00 and 23 in {config}.")
                sys.exit(1)
        if int(FHR_END_SHORT) < 0:
            print(f"FATAL ERROR: FHR_END_SHORT is set to {FHR_END_SHORT}, which is invalid."
                  + f" Please set FHR_END_SHORT to a positive integer in {config}.")
            sys.exit(1)
        if int(FHR_INCR_SHORT) < 0:
            print(f"FATAL ERROR: FHR_INCR_SHORT is set to {FHR_INCR_SHORT}, which is invalid."
                  + f" Please set FHR_INCR_SHORT to a positive integer in {config}.")
            sys.exit(1)
        if int(FHR_END_FULL) < 0:
            print(f"FATAL ERROR: FHR_END_FULL is set to {FHR_END_FULL}, which is invalid."
                  + f" Please set FHR_END_FULL to a positive integer in {config}.")
            sys.exit(1)
        if int(FHR_INCR_FULL) < 0:
            print(f"FATAL ERROR: FHR_INCR_FULL is set to {FHR_INCR_FULL}, which is invalid."
                  + f" Please set FHR_INCR_FULL to a positive integer in {config}.")
            sys.exit(1)
        for MODEL_ACC_i in re.split(r'[,\s]+', MODEL_ACC):
            for OBS_ACC_i in re.split(r'[,\s]+', OBS_ACC):
                for ACC_i in re.split(r'[,\s]+', ACC):
                    if len(MODEL_ACC_i) != 2:
                        print(f"FATAL ERROR: MODEL_ACC is set to {MODEL_ACC_i}, which has"
                              + f" {len(MODEL_ACC_i)} digits, but two digits are required."
                              + f" Please check the configuration file: {config}")
                        sys.exit(1)
                    if int(MODEL_ACC_i) <= 0:
                        print(f"FATAL ERROR: MODEL_ACC is set to {MODEL_ACC_i}, but must be a"
                              + f" positive integer. Please check the configuration file:"
                              + f" {config}")
                        sys.exit(1)
                    if OBS_ACC_i != "VARIABLE":
                        if len(OBS_ACC_i) != 2:
                            print(f"FATAL ERROR: OBS_ACC is set to {OBS_ACC_i}, which has"
                                  + f" {len(OBS_ACC_i)} digits, but two digits are required."
                                  + f" Please check the configuration file: {config}")
                            sys.exit(1)
                        elif int(OBS_ACC_i) <= 0:
                            print(f"FATAL ERROR: OBS_ACC is set to {OBS_ACC_i}, but must be a"
                                  + f" positive integer. Please check the configuration file:"
                                  + f" {config}")
                            sys.exit(1)
                    if len(ACC_i) != 2:
                        print(f"FATAL ERROR: ACC is set to {ACC_i}, which has"
                              + f" {len(ACC_i)} digits, but two digits are required."
                              + f" Please check the configuration file: {config}")
                        sys.exit(1)
                    if int(ACC_i) <= 0:
                        print(f"FATAL ERROR: ACC is set to {ACC_i}, but must be a"
                              + f" positive integer. Please check the configuration file:"
                              + f" {config}")
                        sys.exit(1)
                    elif int(ACC_i) < int(MODEL_ACC_i):
                        print(f"WARNING: ACC is set to {ACC_i}, and is smaller than the"
                              + f" MODEL_ACC ({MODEL_ACC_i}), which will cause an error"
                              + f" if no other options are listed. Please check the"
                              + f" configuration file: {config}")
                    elif OBS_ACC_i != "VARIABLE":
                        if int(ACC_i) < int(OBS_ACC_i):
                            print(f"WARNING: ACC is set to {ACC_i}, and is smaller than the"
                                  + f" OBS_ACC ({OBS_ACC_i}), which will cause an error"
                                  + f" if no other options are listed. Please check the"
                                  + f" configuration file: {config}")
    elif VERIF_CASE == 'grid2obs':
        if int(MIN_IHOUR) < 0 or int(MIN_IHOUR) > 23:
            if int(MIN_IHOUR) == 24:
                print(f"FATAL ERROR: MIN_IHOUR is set to {MIN_IHOUR}, which is equivalent to 00."
                      + f" Please change the MIN_IHOUR to 00 instead in {config}.")
                sys.exit(1)
            else:
                print(f"FATAL ERROR: MIN_IHOUR is set to {MIN_IHOUR}, which is not a valid time"
                      + f" of day. Please set MIN_IHOUR to a two-digit integer between"
                      + f"00 and 23 in {config}.")
                sys.exit(1)
        if int(FHR_END_SHORT) < 0:
            print(f"FATAL ERROR: FHR_END_SHORT is set to {FHR_END_SHORT}, which is invalid."
                  + f" Please set FHR_END_SHORT to a positive integer in {config}.")
            sys.exit(1)
        if int(FHR_INCR_SHORT) < 0:
            print(f"FATAL ERROR: FHR_INCR_SHORT is set to {FHR_INCR_SHORT}, which is invalid."
                  + f" Please set FHR_INCR_SHORT to a positive integer in {config}.")
            sys.exit(1)
        if int(FHR_END_FULL) < 0:
            print(f"FATAL ERROR: FHR_END_FULL is set to {FHR_END_FULL}, which is invalid."
                  + f" Please set FHR_END_FULL to a positive integer in {config}.")
            sys.exit(1)
        if int(FHR_INCR_FULL) < 0:
            print(f"FATAL ERROR: FHR_INCR_FULL is set to {FHR_INCR_FULL}, which is invalid."
                  + f" Please set FHR_INCR_FULL to a positive integer in {config}.")
            sys.exit(1)

print(f"END: {os.path.basename(__file__)}")
