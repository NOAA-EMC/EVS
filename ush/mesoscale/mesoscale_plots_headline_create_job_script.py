#!/usr/bin/env python3
 
# =============================================================================
#
# NAME: mesoscale_plots_headline_create_job_script.sh
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Create EVS Mesoscale Headline - Plots job scripts
# DEPENDENCIES: $SCRIPTSevs/mesoscale/stats/exevs_$MODELNAME_headline_plots.sh
#
# =============================================================================

import sys
import os
import glob
import re
from datetime import datetime
import numpy as np
import mesoscale_util as mutil

print(f"BEGIN: {os.path.basename(__file__)}")

# Read in environment variables
PYTHONPATH = os.environ['PYTHONPATH']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']
VERIF_CASE = os.environ['VERIF_CASE']
MODELNAME = os.environ['MODELNAME']
MET_PLUS_PATH = os.environ['MET_PLUS_PATH']
MET_PATH = os.environ['MET_PATH']
MET_CONFIG = os.environ['MET_CONFIG']
DATA = os.environ['DATA']
VDATE = os.environ['VDATE']
VERIF_TYPE = os.environ['VERIF_TYPE']
USH_DIR = os.environ['USH_DIR']
FIXevs = os.environ['FIXevs']
MET_VERSION = os.environ['MET_VERSION']
IMG_HEADER = os.environ['IMG_HEADER']
PRUNE_DIR = os.environ['PRUNE_DIR']
SAVE_DIR = os.environ['SAVE_DIR']
RESTART_DIR = os.environ['RESTART_DIR']
LOG_TEMPLATE = os.environ['LOG_TEMPLATE']
LOG_LEVEL = os.environ['LOG_LEVEL']
STAT_OUTPUT_BASE_DIR = os.environ['STAT_OUTPUT_BASE_DIR']
STAT_OUTPUT_BASE_TEMPLATE = os.environ['STAT_OUTPUT_BASE_TEMPLATE']
MODELS = os.environ['MODELS']
PLOT_TYPE = os.environ['PLOT_TYPE']
DATE_TYPE = os.environ['DATE_TYPE']
VALID_BEG = os.environ['VALID_BEG']
VALID_END = os.environ['VALID_END']
INIT_BEG = os.environ['INIT_BEG']
INIT_END = os.environ['INIT_END']
VX_MASK_LIST = os.environ['VX_MASK_LIST']
INTERP = os.environ['INTERP']
EVAL_PERIOD = os.environ['EVAL_PERIOD']
FCST_VALID_HOUR = os.environ['FCST_VALID_HOUR']
FCST_INIT_HOUR = os.environ['FCST_INIT_HOUR']
FCST_LEAD = os.environ['FCST_LEAD']
LINE_TYPE = os.environ['LINE_TYPE']
VAR_NAME = os.environ['VAR_NAME']
STATS = os.environ['STATS']
FCST_LEVEL = os.environ['FCST_LEVEL']
OBS_LEVEL = os.environ['OBS_LEVEL']
FCST_THRESH = os.environ['FCST_THRESH']
OBS_THRESH = os.environ['OBS_THRESH']
INTERP_PNTS = os.environ['INTERP_PNTS']
CONFIDENCE_INTERVALS = os.environ['CONFIDENCE_INTERVALS']
DELETE_INTERMED_TOGGLE = os.environ['DELETE_INTERMED_TOGGLE']
PYTHONDONTWRITEBYTECODE = os.environ['PYTHONDONTWRITEBYTECODE']
njob = os.environ['njob']
COMPLETED_JOBS_FILE = os.environ['COMPLETED_JOBS_FILE']

# Make a dictionary of environment variables needed to run this particular job
job_env_vars_dict = {
    'PYTHONPATH': PYTHONPATH,
    'VERIF_CASE': VERIF_CASE,
    'VERIF_TYPE': VERIF_TYPE,
    'IMG_HEADER': IMG_HEADER,
    'USH_DIR': USH_DIR,
    'FIXevs': FIXevs,
    'PRUNE_DIR': PRUNE_DIR,
    'SAVE_DIR': SAVE_DIR,
    'RESTART_DIR': RESTART_DIR,
    'STAT_OUTPUT_BASE_DIR': STAT_OUTPUT_BASE_DIR,
    'STAT_OUTPUT_BASE_TEMPLATE': STAT_OUTPUT_BASE_TEMPLATE,
    'LOG_TEMPLATE': LOG_TEMPLATE.format(njob=njob),
    'LOG_LEVEL': LOG_LEVEL,
    'MET_VERSION': MET_VERSION,
    'MODELS': MODELS,
    'VDATE': VDATE,
    'DATE_TYPE': DATE_TYPE,
    'EVAL_PERIOD': EVAL_PERIOD,
    'VALID_BEG': VALID_BEG,
    'VALID_END': VALID_END,
    'INIT_BEG': INIT_BEG,
    'INIT_END': INIT_END,
    'FCST_INIT_HOUR': FCST_INIT_HOUR,
    'FCST_VALID_HOUR': FCST_VALID_HOUR,
    'FCST_LEVEL': FCST_LEVEL,
    'OBS_LEVEL': OBS_LEVEL,
    'var_name': VAR_NAME,
    'VX_MASK_LIST': VX_MASK_LIST,
    'FCST_LEAD': FCST_LEAD,
    'LINE_TYPE': LINE_TYPE,
    'INTERP': INTERP,
    'FCST_THRESH': FCST_THRESH,
    'OBS_THRESH': OBS_THRESH,
    'STATS': STATS,
    'CONFIDENCE_INTERVALS': CONFIDENCE_INTERVALS,
    'DELETE_INTERMED_TOGGLE': DELETE_INTERMED_TOGGLE,
    'INTERP_PNTS': INTERP_PNTS,
    'PLOT_TYPE': PLOT_TYPE,
    'PYTHONDONTWRITEBYTECODE': PYTHONDONTWRITEBYTECODE
}
job_iterate_over_env_lists_dict = {}
job_iterate_over_custom_lists_dict = {}
job_dependent_vars = {}

# Make a list of commands needed to run this particular job
job_cmd_list_iterative = []
job_cmd_list = []
if STEP == 'prep':
    pass
elif STEP == 'stats':
    pass
elif STEP == 'plots':
    if f'job{njob}' in mutil.get_completed_jobs(os.path.join(RESTART_DIR, COMPLETED_JOBS_FILE)):
        job_cmd_list_iterative.append(
            f'#jobs were restarted, and the following command has already run successfully'
        )
        job_cmd_list_iterative.append(
            f'#python '
            + f'{USH_DIR}/{PLOT_TYPE}.py'
        )
    else:
        job_cmd_list_iterative.append(
            f'python '
            + f'{USH_DIR}/{PLOT_TYPE}.py'
        )
        job_cmd_list_iterative.append(
            f"python -c "
            + f"'import mesoscale_util; mesoscale_util.mark_job_completed("
            + f"\"{os.path.join(RESTART_DIR, COMPLETED_JOBS_FILE)}\", "
            + f"\"job{njob}\")'"
        )

# Write job script
indent = ''
indent_width = 4
iterative_first = True
job_dir = os.path.join(DATA, VERIF_CASE, STEP, 'plotting_job_scripts')
if not os.path.exists(job_dir):
    os.makedirs(job_dir)
job_file = os.path.join(job_dir, f'job{njob}')
print(f"Creating job script: {job_file}")
job = open(job_file, 'w')
job.write('#!/bin/bash\n')
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
    for var_name in values['exports']:
        job.write(f'{indent}TARGET_{var_name}=\"{var_name}_$'+'{'+f'{name}'+'}\"\n')
        job.write(f'{indent}export {var_name}=$'+'{!'+f'TARGET_{var_name}'+'}\n')
        #job.write(f'{indent}export {var_name}=\"{value}\"\n')
for name, value in job_dependent_vars.items():
    if value["exec_value"]:
        exec(f"{name}={value['exec_value']}")
        job.write(
            f'{indent}export {name}={globals()[name]}\n'
        )
    elif value["bash_value"]:
        job.write(f'{indent}export {name}={value["bash_value"]}\n')
    if (value["bash_conditional"] 
            and (
            value["bash_conditional_value"] 
            or value["bash_conditional_else_value"])):
        job.write(
            f'{indent}if {value["bash_conditional"]};'
            + f' then\n'
        )
        job.write(
            f'{indent}{" "*indent_width}export {name}='
            + f'{value["bash_conditional_value"]}\n'
        )
        if (value["bash_conditional_else_value"]):
            job.write(
                f'{indent}else'
                + f'\n'
            )
            job.write(
                f'{indent}{" "*indent_width}export {name}='
                + f'{value["bash_conditional_else_value"]}\n'
            )
        job.write(f'{indent}fi\n')
for name, value in job_iterate_over_custom_lists_dict.items():
    job.write(f"{indent}for {name} in {value['custom_list']}; do\n")
    indent = indent_width*' ' + indent
    job.write(f"{indent}export {name}=${value['export_value']}\n")
    if value['dependent_vars']:
        dep_names = value['dependent_vars']['names']
        dep_values = value['dependent_vars']['values']
        for dn, dep_name in enumerate(dep_names):
            job.write(f"{indent}export {dep_name}={dep_values[dn]}\n")
for cmd in job_cmd_list_iterative:
    job.write(f'{indent}{cmd}\n')
for name, value in job_iterate_over_custom_lists_dict.items():
    indent = indent[indent_width:]
    job.write(f'{indent}done\n')
for name_list, value_list in job_iterate_over_env_lists_dict.items():
    indent = indent[indent_width:]
    job.write(f'{indent}done\n')
if iterative_first:
    for cmd in job_cmd_list:
        job.write(f'{cmd}\n')
job.close()

print(f"END: {os.path.basename(__file__)}")
