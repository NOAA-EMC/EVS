#!/bin/sh -e
 
# =============================================================================
#
# NAME: cam_stats_grid2obs_create_job_script.sh
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Create EVS CAM Grid2Obs - Statistics job scripts
# DEPENDENCIES: $SCRIPTSevs/cam/stats/exevs_$MODELNAME_grid2obs_stats.sh
#
# =============================================================================

import sys
import os
import glob
import re
from datetime import datetime
import numpy as np
import cam_util as cutil
from cam_stats_grid2obs_var_defs import generate_stats_jobs_dict as var_defs

print(f"BEGIN: {os.path.basename(__file__)}")

# Read in environment variables
job_type = os.environ['job_type']
PYTHONPATH = os.environ['PYTHONPATH']
STEP = os.environ['STEP']
VERIF_CASE = os.environ['VERIF_CASE']
VERIF_TYPE = os.environ['VERIF_TYPES']
MODELNAME = os.environ['MODELNAME']
MET_PLUS_PATH = os.environ['MET_PLUS_PATH']
MET_PATH = os.environ['MET_PATH']
MET_CONFIG = os.environ['MET_CONFIG']
DATA = os.environ['DATA']
VDATE = os.environ['VDATE']
MET_PLUS_CONF = os.environ['MET_PLUS_CONF']
MET_PLUS_OUT = os.environ['MET_PLUS_OUT']
MET_CONFIG_OVERRIDES = os.environ['MET_CONFIG_OVERRIDES']
METPLUS_VERBOSITY = os.environ['METPLUS_VERBOSITY']
MET_VERBOSITY = os.environ['MET_VERBOSITY']
LOG_MET_OUTPUT_TO_METPLUS = os.environ['LOG_MET_OUTPUT_TO_METPLUS']
NEST = os.environ['NEST']
if job_type == 'reformat':
    VHOUR = os.environ['VHOUR']
    FHR_START = os.environ['FHR_START']
    FHR_INCR = os.environ['FHR_INCR']
    FHR_END = os.environ['FHR_END']
    COMINobs = os.environ['COMINobs']
    njob = os.environ['njob']
elif job_type == 'generate':
    VHOUR = os.environ['VHOUR']
    FHR_START = os.environ['FHR_START']
    FHR_INCR = os.environ['FHR_INCR']
    FHR_END = os.environ['FHR_END']
    VAR_NAME = os.environ['VAR_NAME']
    COMINfcst = os.environ['COMINfcst']
    MODEL_INPUT_TEMPLATE = os.environ['MODEL_INPUT_TEMPLATE']
    MASK_POLY_LIST = os.environ['MASK_POLY_LIST']
    njob = os.environ['njob']
    GRID = os.environ['GRID']
elif job_type == 'gather':
    njob = os.environ['njob']

# Get expanded details from variable name
if job_type == 'generate':
    plot_this_var = False
    if VAR_NAME in var_defs:
        if VERIF_TYPE in var_defs[VAR_NAME]:
            if MODELNAME in var_defs[VAR_NAME][VERIF_TYPE]:
                plot_this_var = True
                var_def = var_defs[VAR_NAME][VERIF_TYPE][MODELNAME]
                FCST_VAR1_NAME = var_def['var1_fcst_name']
                FCST_VAR1_LEVELS = var_def['var1_fcst_levels']
                FCST_VAR1_THRESHOLDS = var_def['var1_fcst_thresholds']
                FCST_VAR1_OPTIONS = var_def['var1_fcst_options']
                OBS_VAR1_NAME = var_def['var1_fcst_name']
                OBS_VAR1_LEVELS = var_def['var1_fcst_levels']
                OBS_VAR1_THRESHOLDS = var_def['var1_fcst_thresholds']
                OBS_VAR1_OPTIONS = var_def['var1_fcst_options']
                if 'var2_fcst_name' in var_def:
                    FCST_VAR2_NAME = var_def['var2_fcst_name']
                    FCST_VAR2_LEVELS = var_def['var2_fcst_levels']
                    FCST_VAR2_THRESHOLDS = var_def['var2_fcst_thresholds']
                    FCST_VAR2_OPTIONS = var_def['var2_fcst_options']
                    OBS_VAR2_NAME = var_def['var2_fcst_name']
                    OBS_VAR2_LEVELS = var_def['var2_fcst_levels']
                    OBS_VAR2_THRESHOLDS = var_def['var2_fcst_thresholds']
                    OBS_VAR2_OPTIONS = var_def['var2_fcst_options']
                else:
                    FCST_VAR2_NAME = ''
                    FCST_VAR2_LEVELS = ''
                    FCST_VAR2_THRESHOLDS = ''
                    FCST_VAR2_OPTIONS = ''
                    OBS_VAR2_NAME = ''
                    OBS_VAR2_LEVELS = ''
                    OBS_VAR2_THRESHOLDS = ''
                    OBS_VAR2_OPTIONS = ''
    if not plot_this_var:
        sys.exit(0)

# Make a dictionary of environment variables needed to run this particular job
job_env_vars_dict = {
    'PYTHONPATH': PYTHONPATH,
    'VERIF_CASE': VERIF_CASE,
    'VERIF_TYPE': VERIF_TYPE,
    'MODELNAME': MODELNAME,
    'MET_PLUS_PATH': MET_PLUS_PATH,
    'MET_PATH': MET_PATH,
    'MET_CONFIG': MET_CONFIG,
    'DATA': DATA,
    'VDATE': VDATE,
    'MET_PLUS_CONF': MET_PLUS_CONF,
    'MET_PLUS_OUT': MET_PLUS_OUT,
    'MET_CONFIG_OVERRIDES': MET_CONFIG_OVERRIDES,
    'METPLUS_VERBOSITY': METPLUS_VERBOSITY,
    'MET_VERBOSITY': MET_VERBOSITY,
    'LOG_MET_OUTPUT_TO_METPLUS': LOG_MET_OUTPUT_TO_METPLUS,
    'NEST': NEST,
}
job_iterate_over_env_lists_dict = {}
job_dependent_vars = {}
if job_type == 'reformat':
    job_env_vars_dict['VHOUR'] = VHOUR
    job_env_vars_dict['FHR_START'] = FHR_START
    job_env_vars_dict['FHR_INCR'] = FHR_INCR
    job_env_vars_dict['FHR_END'] = FHR_END
    job_env_vars_dict['COMINfcst'] = COMINfcst
    job_env_vars_dict['MODEL_INPUT_TEMPLATE'] = MODEL_INPUT_TEMPLATE
elif job_type == 'generate':
    job_env_vars_dict['VHOUR'] = VHOUR
    job_env_vars_dict['FHR_START'] = FHR_START
    job_env_vars_dict['FHR_INCR'] = FHR_INCR
    job_env_vars_dict['FHR_END'] = FHR_END
    job_env_vars_dict['COMINfcst'] = COMINfcst
    job_env_vars_dict['MODEL_INPUT_TEMPLATE'] = MODEL_INPUT_TEMPLATE
    job_env_vars_dict['MASK_POLY_LIST'] = MASK_POLY_LIST
    job_env_vars_dict['FCST_VAR1_NAME']: FCST_VAR1_NAME
    job_env_vars_dict['FCST_VAR1_LEVELS']: FCST_VAR1_LEVELS
    job_env_vars_dict['FCST_VAR1_THRESHOLDS']: FCST_VAR1_THRESHOLDS
    job_env_vars_dict['FCST_VAR1_OPTIONS']: FCST_VAR1_OPTIONS
    job_env_vars_dict['OBS_VAR1_NAME']: OBS_VAR1_NAME
    job_env_vars_dict['OBS_VAR1_LEVELS']: OBS_VAR1_LEVELS
    job_env_vars_dict['OBS_VAR1_THRESHOLDS']: OBS_VAR1_THRESHOLDS
    job_env_vars_dict['OBS_VAR1_OPTIONS']: OBS_VAR1_OPTIONS
    job_env_vars_dict['FCST_VAR2_NAME']: FCST_VAR2_NAME
    job_env_vars_dict['FCST_VAR2_LEVELS']: FCST_VAR2_LEVELS
    job_env_vars_dict['FCST_VAR2_THRESHOLDS']: FCST_VAR2_THRESHOLDS
    job_env_vars_dict['FCST_VAR2_OPTIONS']: FCST_VAR2_OPTIONS
    job_env_vars_dict['OBS_VAR2_NAME']: OBS_VAR2_NAME
    job_env_vars_dict['OBS_VAR2_LEVELS']: OBS_VAR2_LEVELS
    job_env_vars_dict['OBS_VAR2_THRESHOLDS']: OBS_VAR2_THRESHOLDS
    job_env_vars_dict['OBS_VAR2_OPTIONS']: OBS_VAR2_OPTIONS
    job_env_vars_dict['GRID'] = GRID
# Make a list of commands needed to run this particular job
metplus_launcher = 'run_metplus.py'
job_cmd_list_iterative = []
job_cmd_list = []
if STEP == 'prep':
    pass
elif STEP == 'stats':
    if job_type == 'reformat':
        job_cmd_list_iterative.append(
            f'{metplus_launcher} -c '
            + f'{MET_PLUS_CONF}/'
            + f'PB2NC_obs{OBSNAME.upper()}.conf'
        )
    if job_type == 'generate':
        job_cmd_list_iterative.append(
            f'{metplus_launcher} -c '
            + f'{MET_PLUS_CONF}/'
            + f'PointStat_fcst{COMPONENT.upper()}_obs{OBSNAME.upper()}.conf'
        )
    elif job_type == 'gather':
        job_cmd_list.append(
            f'{metplus_launcher} -c '
            + f'{MET_PLUS_CONF}/'
            + f'StatAnalysis_fcst{COMPONENT.upper()}_obs{OBSNAME.upper()}'
            + f'_GatherByDay.conf'
        )
elif STEP == 'plots':
    pass

# Write job script
indent = ''
indent_width = 4
iterative_first = True
job_dir = os.path.join(DATA, VERIF_CASE, STEP, 'METplus_job_scripts', job_type)
if not os.path.exists(job_dir):
    os.makedirs(job_dir)
job_file = os.path.join(job_dir, f'job{njob}')
print(f"Creating job script: {job_file}")
job = open(job_file, 'w')
job.write('#!/bin/sh\n')
job.write('set -x \n')
job.write('\n')
job.write(f'export job_name=\"job{njob}\"\n')
for name, value in job_env_vars_dict.items():
    job.write(f'export {name}=\"{value}\"\n')
job.write('\n')
if not iterative_first:
    for cmd in job_cmd_list:
        job.write(f'{cmd}\n')
for name_list, values in job_iterate_over_env_lists_dict.items():
    name = name_list.replace('_LIST','')
    items = ' '.join([f'\"{item}\"' for item in values['list_items']])
    job.write(f'{indent}for {name} in {items}; do\n')
    indent = indent_width*' ' + indent 
    job.write(f'{indent}export {name}=${name}\n')
    for var_name, value in values['exports'].items():
        job.write(f'{indent}export {var_name}=\"{value}\"\n'
for name, value in job_dependent_vars.items():
    if value["exec_value"]:
        exec(f"{name}={value['exec_value']}")
        job.write(
            f'{indent}export {name}={globals()[name]}\n'
        )
    elif value["bash_value"]:
        job.write(f'{indent}export {name}={value["bash_value"]}\n')
    if (value["bash_conditional"] 
            and value["bash_conditional_value"]):
        job.write(
            f'{indent}if {value["bash_conditional"]};'
            + f' then\n'
        )
        job.write(
            f'{indent}{" "*indent_width}export {name}='
            + f'{value["bash_conditional_value"]}\n'
        )
        job.write(f'{indent}fi\n')
for cmd in job_cmd_list_iterative:
    job.write(f'{indent}{cmd}\n')
for name_list, value_list in job_iterate_over_env_lists_dict.items():
    indent = indent[indent_width:]
    job.write(f'{indent}done\n')
if iterative_first:
    for cmd in job_cmd_list:
        job.write(f'{cmd}\n')
job.close()

print(f"END: {os.path.basename(__file__)}")
