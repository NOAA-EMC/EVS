#!/bin/bash -e
 
# =============================================================================
#
# NAME: cam_stats_snowfall_create_job_script.sh
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Create EVS CAM Snowfall - Statistics job scripts
# DEPENDENCIES: $SCRIPTSevs/cam/stats/exevs_$MODELNAME_snowfall_stats.sh
#
# =============================================================================

import sys
import os
import glob
import re
from datetime import datetime
import numpy as np
import cam_util as cutil
from cam_stats_snowfall_var_defs import generate_stats_jobs_dict as var_defs

print(f"BEGIN: {os.path.basename(__file__)}")

# Read in environment variables
cyc = os.environ['cyc']
job_type = os.environ['job_type']
PYTHONPATH = os.environ['PYTHONPATH']
COMPONENT = os.environ['COMPONENT']
NET = os.environ['NET']
STEP = os.environ['STEP']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
MODELNAME = os.environ['MODELNAME']
METPLUS_PATH = os.environ['METPLUS_PATH']
MET_ROOT = os.environ['MET_ROOT']
DATA = os.environ['DATA']
RESTART_DIR = os.environ['RESTART_DIR']
VDATE = os.environ['VDATE']
MET_PLUS_CONF = os.environ['MET_PLUS_CONF']
MET_PLUS_OUT = os.environ['MET_PLUS_OUT']
MET_CONFIG_OVERRIDES = os.environ['MET_CONFIG_OVERRIDES']
machine_conf = os.path.join(
    os.environ['PARMevs'], 'metplus_config', 'machine.conf'
)
if job_type == 'reformat':
    VERIF_TYPE = os.environ['VERIF_TYPE']
    NEST = os.environ['NEST']
    VHOUR = os.environ['VHOUR']
    FHR_GROUP_LIST = os.environ['FHR_GROUP_LIST']
    FHR_END_SHORT = os.environ['FHR_END_SHORT']
    FHR_INCR_SHORT = os.environ['FHR_INCR_SHORT']
    FHR_END_FULL = os.environ['FHR_END_FULL']
    FHR_INCR_FULL = os.environ['FHR_INCR_FULL']
    MIN_IHOUR = os.environ['MIN_IHOUR']
    COMINfcst = os.environ['COMINfcst']
    MODEL_INPUT_TEMPLATE = os.environ['MODEL_INPUT_TEMPLATE']
    njob = os.environ['njob']
    BUCKET_INTERVAL = os.environ['BUCKET_INTERVAL']
elif job_type == 'generate':
    VERIF_TYPE = os.environ['VERIF_TYPE']
    NEST = os.environ['NEST']
    #VHOUR_LIST = os.environ['VHOUR_LIST']
    VHOUR = os.environ['VHOUR']
    FHR_GROUP_LIST = os.environ['FHR_GROUP_LIST']
    FHR_END_SHORT = os.environ['FHR_END_SHORT']
    FHR_INCR_SHORT = os.environ['FHR_INCR_SHORT']
    FHR_END_FULL = os.environ['FHR_END_FULL']
    FHR_INCR_FULL = os.environ['FHR_INCR_FULL']
    MIN_IHOUR = os.environ['MIN_IHOUR']
    COMINobs = os.environ['COMINobs']
    MASK_POLY_LIST = os.environ['MASK_POLY_LIST']
    OBSNAME = os.environ['OBSNAME']
    njob = os.environ['njob']
elif job_type == 'gather':
    VERIF_TYPE = os.environ['VERIF_TYPE']
    NEST = os.environ['NEST']
    OBSNAME = os.environ['OBSNAME']
    njob = os.environ['njob']
elif job_type in ['gather2', 'gather3']:
    njob = os.environ['njob']
if VERIF_CASE == 'snowfall':
    if job_type == 'reformat':
        ACC = os.environ['ACC']
        MODEL_PCP_COMBINE_METHOD = os.environ['MODEL_PCP_COMBINE_METHOD']
        MODEL_PCP_COMBINE_COMMAND = os.environ['MODEL_PCP_COMBINE_COMMAND']
        VAR_NAME = os.environ['VAR_NAME']
    elif job_type == 'generate':
        ACC = os.environ['ACC']
        BOOL_NBRHD = os.environ['BOOL_NBRHD']
        OUTPUT_FLAG_NBRHD = os.environ['OUTPUT_FLAG_NBRHD']
        OUTPUT_FLAG_CATEG = os.environ['OUTPUT_FLAG_CATEG']
        NBRHD_WIDTHS = os.environ['NBRHD_WIDTHS']
        GRID = os.environ['GRID']
        VAR_NAME = os.environ['VAR_NAME']
    elif job_type in ['gather', 'gather2', 'gather3']:
        COMPONENT = os.environ['COMPONENT']

# Get expanded details from variable name
if job_type in ['generate', 'reformat']:
    plot_this_var = False
    if VAR_NAME in var_defs:
        if VERIF_TYPE in var_defs[VAR_NAME]:
            if MODELNAME in var_defs[VAR_NAME][VERIF_TYPE]:
                plot_this_var = True
                var_def = var_defs[VAR_NAME][VERIF_TYPE][MODELNAME]
                FCST_VAR_NAME = var_def['var1_fcst_name']
                FCST_VAR_LEVELS = var_def['var1_fcst_levels']
                FCST_VAR_THRESHOLDS = var_def['var1_fcst_thresholds']
                FCST_VAR_OPTIONS = var_def['var1_fcst_options']
                OBS_VAR_NAME = var_def['var1_obs_name']
                OBS_VAR_LEVELS = var_def['var1_obs_levels']
                OBS_VAR_THRESHOLDS = var_def['var1_obs_thresholds']
                OBS_VAR_OPTIONS = var_def['var1_obs_options']
                if job_type == 'reformat':
                    MODEL_PCP_COMBINE_COMMAND = MODEL_PCP_COMBINE_COMMAND.replace(
                        '{FCST_VAR_NAME}', FCST_VAR_NAME
                    )
    if not plot_this_var:
        print(f"ERROR: VAR_NAME \"{VAR_NAME}\" is not valid for VERIF_TYPE "
              + f"\"{VERIF_TYPE}\" and MODEL \"{MODELNAME}\". Check "
              + f"{USHevs}/{COMPONENT}/{COMPONENT}_stats_grid2obs_var_defs.py "
              + f"for valid configurations.")
        sys.exit(1)

# Make a dictionary of environment variables needed to run this particular job
job_env_vars_dict = {
    'cyc': cyc,
    'NET': NET,
    'STEP': STEP,
    'RUN': RUN,
    'PYTHONPATH': PYTHONPATH,
    'VERIF_CASE': VERIF_CASE,
    'MODELNAME': MODELNAME,
    'METPLUS_PATH': METPLUS_PATH,
    'MET_ROOT': MET_ROOT,
    'DATA': DATA,
    'RESTART_DIR': RESTART_DIR,
    'VDATE': VDATE,
    'MET_PLUS_CONF': MET_PLUS_CONF,
    'MET_PLUS_OUT': MET_PLUS_OUT,
    'MET_CONFIG_OVERRIDES': MET_CONFIG_OVERRIDES,
}
job_iterate_over_env_lists_dict = {}
job_dependent_vars = {}
if job_type == 'reformat':
    job_env_vars_dict['VERIF_TYPE'] = VERIF_TYPE
    job_env_vars_dict['NEST'] = NEST
    job_env_vars_dict['VHOUR'] = VHOUR
    job_env_vars_dict['FHR_GROUP_LIST'] = FHR_GROUP_LIST
    job_env_vars_dict['FHR_END_SHORT'] = FHR_END_SHORT
    job_env_vars_dict['FHR_INCR_SHORT'] = FHR_INCR_SHORT
    job_env_vars_dict['FHR_END_FULL'] = FHR_END_FULL
    job_env_vars_dict['FHR_INCR_FULL'] = FHR_INCR_FULL
    job_env_vars_dict['MIN_IHOUR'] = MIN_IHOUR
    job_env_vars_dict['COMINfcst'] = COMINfcst
    job_env_vars_dict['FCST_VAR_NAME'] = FCST_VAR_NAME
    job_env_vars_dict['FCST_VAR_LEVELS'] = FCST_VAR_LEVELS
    job_env_vars_dict['FCST_VAR_THRESHOLDS'] = FCST_VAR_THRESHOLDS
    job_env_vars_dict['FCST_VAR_OPTIONS'] = FCST_VAR_OPTIONS
    job_env_vars_dict['OBS_VAR_NAME'] = OBS_VAR_NAME
    job_env_vars_dict['OBS_VAR_LEVELS'] = OBS_VAR_LEVELS
    job_env_vars_dict['OBS_VAR_THRESHOLDS'] = OBS_VAR_THRESHOLDS
    job_env_vars_dict['OBS_VAR_OPTIONS'] = OBS_VAR_OPTIONS
    job_env_vars_dict['MODEL_INPUT_TEMPLATE'] = MODEL_INPUT_TEMPLATE
    job_env_vars_dict['BUCKET_INTERVAL'] = BUCKET_INTERVAL
    job_env_vars_dict['VAR_NAME'] = VAR_NAME
    job_iterate_over_env_lists_dict['FHR_GROUP_LIST'] = {
        'list_items': re.split(r'[\s,]+', FHR_GROUP_LIST),
        'exports': ['FHR_END','FHR_INCR']
    }
elif job_type == 'generate':
    job_env_vars_dict['VERIF_TYPE'] = VERIF_TYPE
    job_env_vars_dict['NEST'] = NEST
    #job_env_vars_dict['VHOUR_LIST'] = VHOUR_LIST
    job_env_vars_dict['VHOUR'] = VHOUR
    job_env_vars_dict['FHR_GROUP_LIST'] = FHR_GROUP_LIST
    job_env_vars_dict['FHR_END_SHORT'] = FHR_END_SHORT
    job_env_vars_dict['FHR_INCR_SHORT'] = FHR_INCR_SHORT
    job_env_vars_dict['FHR_END_FULL'] = FHR_END_FULL
    job_env_vars_dict['FHR_INCR_FULL'] = FHR_INCR_FULL
    job_env_vars_dict['MIN_IHOUR'] = MIN_IHOUR
    job_env_vars_dict['COMINobs'] = COMINobs
    job_env_vars_dict['FCST_VAR_NAME'] = FCST_VAR_NAME
    job_env_vars_dict['FCST_VAR_LEVELS'] = FCST_VAR_LEVELS
    job_env_vars_dict['FCST_VAR_THRESHOLDS'] = FCST_VAR_THRESHOLDS
    job_env_vars_dict['FCST_VAR_OPTIONS'] = FCST_VAR_OPTIONS
    job_env_vars_dict['OBS_VAR_NAME'] = OBS_VAR_NAME
    job_env_vars_dict['OBS_VAR_LEVELS'] = OBS_VAR_LEVELS
    job_env_vars_dict['OBS_VAR_THRESHOLDS'] = OBS_VAR_THRESHOLDS
    job_env_vars_dict['OBS_VAR_OPTIONS'] = OBS_VAR_OPTIONS
    job_env_vars_dict['MASK_POLY_LIST'] = MASK_POLY_LIST
    job_env_vars_dict['VAR_NAME'] = VAR_NAME
    #job_iterate_over_env_lists_dict['VHOUR_LIST'] = {
    #    'list_items': re.split(r'[\s,]+', VHOUR_LIST),
    #    'exports': [],
    #}
    job_iterate_over_env_lists_dict['FHR_GROUP_LIST'] = {
        'list_items': re.split(r'[\s,]+', FHR_GROUP_LIST),
        'exports': ['FHR_END','FHR_INCR']
    }
elif job_type == 'gather':
    job_env_vars_dict['VERIF_TYPE'] = VERIF_TYPE
    job_env_vars_dict['NEST'] = NEST
if VERIF_CASE == 'snowfall': 
    if job_type == 'reformat':
        job_env_vars_dict['ACC'] = ACC
        job_env_vars_dict['MODEL_PCP_COMBINE_METHOD'] = MODEL_PCP_COMBINE_METHOD
        job_env_vars_dict['MODEL_PCP_COMBINE_COMMAND'] = MODEL_PCP_COMBINE_COMMAND
        job_dependent_vars['FHR_START'] = {
            'exec_value': '',
            'bash_value': (
                '$(python -c \"import cam_util; print(cam_util.get_fhr_start('
                + '\'${VHOUR}\',\'${ACC}\',\'${FHR_INCR}\',\'${MIN_IHOUR}\'))\")'
            ),
            'bash_conditional': '',
            'bash_conditional_value': ''
        }
    elif job_type == 'generate':
        job_env_vars_dict['ACC'] = ACC
        job_env_vars_dict['BOOL_NBRHD'] = BOOL_NBRHD
        job_env_vars_dict['OUTPUT_FLAG_NBRHD'] = OUTPUT_FLAG_NBRHD
        job_env_vars_dict['OUTPUT_FLAG_CATEG'] = OUTPUT_FLAG_CATEG
        job_env_vars_dict['NBRHD_WIDTHS'] = NBRHD_WIDTHS
        job_env_vars_dict['GRID'] = GRID
        job_dependent_vars['FHR_START'] = {
            'exec_value': '',
            'bash_value': (
                '$(python -c \"import cam_util; print(cam_util.get_fhr_start('
                + '\'${VHOUR}\',\'${ACC}\',\'${FHR_INCR}\',\'${MIN_IHOUR}\'))\")'
            ),
            'bash_conditional': '',
            'bash_conditional_value': ''
        }
# Make a list of commands needed to run this particular job
metplus_launcher = 'run_metplus.py'
job_cmd_list_iterative = []
job_cmd_list = []
if VERIF_CASE == 'snowfall':
    if STEP == 'prep':
        pass
    elif STEP == 'stats':
        if job_type == 'reformat':
            job_cmd_list_iterative.append(
                f'{metplus_launcher} -c {machine_conf} '
                + f'-c {MET_PLUS_CONF}/'
                + f'PCPCombine_fcst{COMPONENT.upper()}.conf'
            )
            job_cmd_list.append(
                f'python -c '
                + '\"import cam_util as cutil; cutil.copy_data_to_restart('
                + '\\\"${DATA}\\\", \\\"${RESTART_DIR}\\\", '
                + 'verif_case=\\\"${VERIF_CASE}\\\", '
                + 'verif_type=\\\"${VERIF_TYPE}\\\", '
                + 'vx_mask=\\\"${NEST}\\\", '
                + 'met_tool=\\\"pcp_combine\\\", '
                + 'vdate=\\\"${VDATE}\\\", '
                + 'vhour=\\\"${VHOUR}\\\", '
                + 'fhr_start=\\\"${FHR_START}\\\", '
                + 'fhr_end=\\\"${FHR_END}\\\", '
                + 'fhr_incr=\\\"${FHR_INCR}\\\", '
                + 'model=\\\"${MODELNAME}\\\", '
                + 'var_name=\\\"${VAR_NAME}\\\", '
                + 'acc=\\\"${ACC}\\\"'
                + ')\"'
            )
        if job_type == 'generate':
            job_cmd_list_iterative.append(
                f'{metplus_launcher} -c {machine_conf} '
                + f'-c {MET_PLUS_CONF}/'
                + f'GridStat_fcst{COMPONENT.upper()}_obs{OBSNAME.upper()}.conf'
            )
            job_cmd_list_iterative.append(
                f'python -c '
                + '\"import cam_util as cutil; cutil.copy_data_to_restart('
                + '\\\"${DATA}\\\", \\\"${RESTART_DIR}\\\", '
                + 'verif_case=\\\"${VERIF_CASE}\\\", '
                + 'verif_type=\\\"${VERIF_TYPE}\\\", '
                + 'met_tool=\\\"grid_stat\\\", '
                + 'vdate=\\\"${VDATE}\\\", '
                + 'vhour=\\\"${VHOUR}\\\", '
                + 'fhr_start=\\\"${FHR_START}\\\", '
                + 'fhr_end=\\\"${FHR_END}\\\", '
                + 'fhr_incr=\\\"${FHR_INCR}\\\", '
                + 'model=\\\"${MODELNAME}\\\", '
                + 'var_name=\\\"${VAR_NAME}\\\", '
                + 'acc=\\\"${ACC}\\\", '
                + 'nbrhd=\\\"${BOOL_NBRHD}\\\"'
                + ')\"'
            )
        elif job_type == 'gather':
            job_cmd_list.append(
                f'{metplus_launcher} -c {machine_conf} '
                + f'-c {MET_PLUS_CONF}/'
                + f'StatAnalysis_fcst{COMPONENT.upper()}_obs{OBSNAME.upper()}'
                + f'_GatherByDay.conf'
            )
            job_cmd_list.append(
                f'python -c '
                + '\"import cam_util as cutil; cutil.copy_data_to_restart('
                + '\\\"${DATA}\\\", \\\"${RESTART_DIR}\\\", '
                + 'verif_case=\\\"${VERIF_CASE}\\\", '
                + 'verif_type=\\\"${VERIF_TYPE}\\\", '
                + 'met_tool=\\\"stat_analysis\\\", '
                + 'vdate=\\\"${VDATE}\\\", '
                + 'net=\\\"${NET}\\\", '
                + 'step=\\\"${STEP}\\\", '
                + 'model=\\\"${MODELNAME}\\\", '
                + 'run=\\\"${RUN}\\\", '
                + f'job_type=\\\"{job_type}\\\"'
                + ')\"'
            )
        elif job_type == 'gather2':
            job_cmd_list.append(
                f'{metplus_launcher} -c {machine_conf} '
                + f'-c {MET_PLUS_CONF}/'
                + f'StatAnalysis_fcst{COMPONENT.upper()}'
                + f'_GatherByCycle.conf'
            )
            job_cmd_list.append(
                f'python -c '
                + '\"import cam_util as cutil; cutil.copy_data_to_restart('
                + '\\\"${DATA}\\\", \\\"${RESTART_DIR}\\\", '
                + 'verif_case=\\\"${VERIF_CASE}\\\", '
                + 'met_tool=\\\"stat_analysis\\\", '
                + 'vdate=\\\"${VDATE}\\\", '
                + 'net=\\\"${NET}\\\", '
                + 'step=\\\"${STEP}\\\", '
                + 'model=\\\"${MODELNAME}\\\", '
                + 'run=\\\"${RUN}\\\", '
                + 'cyc=\\\"${cyc}\\\", '
                + f'job_type=\\\"{job_type}\\\"'
                + ')\"'
            )
        elif job_type == 'gather3':
            job_cmd_list.append(
                f'{metplus_launcher} -c {machine_conf} '
                + f'-c {MET_PLUS_CONF}/'
                + f'StatAnalysis_fcst{COMPONENT.upper()}'
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
