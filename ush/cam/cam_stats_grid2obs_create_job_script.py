#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_stats_grid2obs_create_job_script.py
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
cyc = os.environ['cyc']
job_type = os.environ['job_type']
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
MET_PLUS_CONF = os.environ['MET_PLUS_CONF']
MET_PLUS_OUT = os.environ['MET_PLUS_OUT']
MET_CONFIG_OVERRIDES = os.environ['MET_CONFIG_OVERRIDES']
METPLUS_VERBOSITY = os.environ['METPLUS_VERBOSITY']
MET_VERBOSITY = os.environ['MET_VERBOSITY']
LOG_MET_OUTPUT_TO_METPLUS = os.environ['LOG_MET_OUTPUT_TO_METPLUS']
metplus_launcher = 'run_metplus.py'
if job_type == 'reformat':
    VERIF_TYPE = os.environ['VERIF_TYPE']
    NEST = os.environ['NEST']
    VHOUR = os.environ['VHOUR']
    #FHR_START = os.environ['FHR_START']
    #FHR_INCR = os.environ['FHR_INCR']
    #FHR_END = os.environ['FHR_END']
    FHR_GROUP_LIST = os.environ['FHR_GROUP_LIST']
    FHR_END_SHORT = os.environ['FHR_END_SHORT']
    FHR_INCR_SHORT = os.environ['FHR_INCR_SHORT']
    FHR_END_FULL = os.environ['FHR_END_FULL']
    FHR_INCR_FULL = os.environ['FHR_INCR_FULL']
    MIN_IHOUR = os.environ['MIN_IHOUR']
    COMINobs = os.environ['COMINobs']
    njob = os.environ['njob']
    USHevs = os.environ['USHevs']
    SKIP_IF_OUTPUT_EXISTS = os.environ['SKIP_IF_OUTPUT_EXISTS']
    if NEST == 'spc_otlk':
        COMINspcotlk = os.environ['COMINspcotlk']
        GRID_POLY_LIST = os.environ['GRID_POLY_LIST']
    if NEST == 'firewx':
        GRID_POLY_LIST = os.environ['GRID_POLY_LIST']
elif job_type == 'generate':
    VERIF_TYPE = os.environ['VERIF_TYPE']
    NEST = os.environ['NEST']
    VHOUR = os.environ['VHOUR']
    #FHR_START = os.environ['FHR_START']
    #FHR_INCR = os.environ['FHR_INCR']
    #FHR_END = os.environ['FHR_END']
    FHR_GROUP_LIST = os.environ['FHR_GROUP_LIST']
    FHR_END_SHORT = os.environ['FHR_END_SHORT']
    FHR_INCR_SHORT = os.environ['FHR_INCR_SHORT']
    FHR_END_FULL = os.environ['FHR_END_FULL']
    FHR_INCR_FULL = os.environ['FHR_INCR_FULL']
    MIN_IHOUR = os.environ['MIN_IHOUR']
    VAR_NAME = os.environ['VAR_NAME']
    COMINfcst = os.environ['COMINfcst']
    MODEL_INPUT_TEMPLATE = os.environ['MODEL_INPUT_TEMPLATE']
    if NEST not in ['firewx', 'spc_otlk']:
        MASK_POLY_LIST = os.environ['MASK_POLY_LIST']
    njob = os.environ['njob']
    GRID = os.environ['GRID']
    USHevs = os.environ['USHevs']
elif job_type == 'gather':
    VERIF_TYPE = os.environ['VERIF_TYPE']
    njob = os.environ['njob']
elif job_type in ['gather2','gather3']:
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
                OBS_VAR1_NAME = var_def['var1_obs_name']
                OBS_VAR1_LEVELS = var_def['var1_obs_levels']
                OBS_VAR1_THRESHOLDS = var_def['var1_obs_thresholds']
                OBS_VAR1_OPTIONS = var_def['var1_obs_options']
                if 'var2_fcst_name' in var_def:
                    FCST_VAR2_NAME = var_def['var2_fcst_name']
                    FCST_VAR2_LEVELS = var_def['var2_fcst_levels']
                    FCST_VAR2_THRESHOLDS = var_def['var2_fcst_thresholds']
                    FCST_VAR2_OPTIONS = var_def['var2_fcst_options']
                    OBS_VAR2_NAME = var_def['var2_obs_name']
                    OBS_VAR2_LEVELS = var_def['var2_obs_levels']
                    OBS_VAR2_THRESHOLDS = var_def['var2_obs_thresholds']
                    OBS_VAR2_OPTIONS = var_def['var2_obs_options']
                else:
                    FCST_VAR2_NAME = ''
                    FCST_VAR2_LEVELS = ''
                    FCST_VAR2_THRESHOLDS = ''
                    FCST_VAR2_OPTIONS = ''
                    OBS_VAR2_NAME = ''
                    OBS_VAR2_LEVELS = ''
                    OBS_VAR2_THRESHOLDS = ''
                    OBS_VAR2_OPTIONS = ''
                OUTPUT_FLAG_CTC = (
                    var_defs[VAR_NAME][VERIF_TYPE]['output_types']['CTC']
                )
                OUTPUT_FLAG_SL1L2 = (
                    var_defs[VAR_NAME][VERIF_TYPE]['output_types']['SL1L2']
                )
                OUTPUT_FLAG_VL1L2 = (
                    var_defs[VAR_NAME][VERIF_TYPE]['output_types']['VL1L2']
                )
                OUTPUT_FLAG_CNT = (
                    var_defs[VAR_NAME][VERIF_TYPE]['output_types']['CNT']
                )
                OUTPUT_FLAG_VCNT = (
                    var_defs[VAR_NAME][VERIF_TYPE]['output_types']['VCNT']
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
    'PYTHONPATH': PYTHONPATH,
    'VERIF_CASE': VERIF_CASE,
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
}
job_iterate_over_env_lists_dict = {}
job_iterate_over_custom_lists_dict = {}
job_dependent_vars = {}
if job_type == 'reformat':
    job_env_vars_dict['VERIF_TYPE'] = VERIF_TYPE
    job_env_vars_dict['NEST'] = NEST
    job_env_vars_dict['VHOUR'] = VHOUR
    #job_env_vars_dict['FHR_START'] = FHR_START
    #job_env_vars_dict['FHR_INCR'] = FHR_INCR
    #job_env_vars_dict['FHR_END'] = FHR_END
    job_env_vars_dict['VERIF_TYPE'] = VERIF_TYPE
    job_env_vars_dict['FHR_GROUP_LIST'] = FHR_GROUP_LIST
    job_env_vars_dict['FHR_END_SHORT'] = FHR_END_SHORT
    job_env_vars_dict['FHR_INCR_SHORT'] = FHR_INCR_SHORT
    job_env_vars_dict['FHR_END_FULL'] = FHR_END_FULL
    job_env_vars_dict['FHR_INCR_FULL'] = FHR_INCR_FULL
    job_env_vars_dict['MIN_IHOUR'] = MIN_IHOUR
    job_env_vars_dict['COMINobs'] = COMINobs
    job_env_vars_dict['SKIP_IF_OUTPUT_EXISTS'] = SKIP_IF_OUTPUT_EXISTS
    job_iterate_over_env_lists_dict['FHR_GROUP_LIST'] = {
        'list_items': re.split(r'[\s,]+', FHR_GROUP_LIST),
        'exports': ['FHR_END','FHR_INCR']
    }
    if NEST == 'spc_otlk':
        job_env_vars_dict['metplus_launcher'] = metplus_launcher
        job_env_vars_dict['COMINspcotlk'] = COMINspcotlk
        job_env_vars_dict['GRID_POLY_LIST'] = GRID_POLY_LIST
        job_iterate_over_custom_lists_dict['DAY'] = {
            'custom_list': '1 2 3',
            'export_value': '{DAY}',
            'dependent_vars': {}
        }
    if NEST == 'firewx':
        job_env_vars_dict['GRID_POLY_LIST'] = GRID_POLY_LIST
    job_dependent_vars['FHR_START'] = {
        'exec_value': '',
        'bash_value': (
            '$(python -c \"import cam_util; print(cam_util.get_fhr_start('
            + '\'${VHOUR}\',0,\'${FHR_INCR}\',\'${MIN_IHOUR}\'))\")'
        ),
        'bash_conditional': '',
        'bash_conditional_value': '',
        'bash_conditional_else_value': ''
    }
elif job_type == 'generate':
    job_env_vars_dict['VERIF_TYPE'] = VERIF_TYPE
    job_env_vars_dict['NEST'] = NEST
    job_env_vars_dict['VHOUR'] = VHOUR
    #job_env_vars_dict['FHR_START'] = FHR_START
    #job_env_vars_dict['FHR_INCR'] = FHR_INCR
    #job_env_vars_dict['FHR_END'] = FHR_END
    job_env_vars_dict['FHR_GROUP_LIST'] = FHR_GROUP_LIST
    job_env_vars_dict['FHR_END_SHORT'] = FHR_END_SHORT
    job_env_vars_dict['FHR_INCR_SHORT'] = FHR_INCR_SHORT
    job_env_vars_dict['FHR_END_FULL'] = FHR_END_FULL
    job_env_vars_dict['FHR_INCR_FULL'] = FHR_INCR_FULL
    job_env_vars_dict['MIN_IHOUR'] = MIN_IHOUR
    job_env_vars_dict['COMINfcst'] = COMINfcst
    job_env_vars_dict['MODEL_INPUT_TEMPLATE'] = MODEL_INPUT_TEMPLATE
    job_env_vars_dict['VAR_NAME'] = VAR_NAME
    job_env_vars_dict['FCST_VAR1_NAME'] = FCST_VAR1_NAME
    job_env_vars_dict['FCST_VAR1_LEVELS'] = FCST_VAR1_LEVELS
    job_env_vars_dict['FCST_VAR1_THRESHOLDS'] = FCST_VAR1_THRESHOLDS
    job_env_vars_dict['FCST_VAR1_OPTIONS'] = FCST_VAR1_OPTIONS
    job_env_vars_dict['OBS_VAR1_NAME'] = OBS_VAR1_NAME
    job_env_vars_dict['OBS_VAR1_LEVELS'] = OBS_VAR1_LEVELS
    job_env_vars_dict['OBS_VAR1_THRESHOLDS'] = OBS_VAR1_THRESHOLDS
    job_env_vars_dict['OBS_VAR1_OPTIONS'] = OBS_VAR1_OPTIONS
    job_env_vars_dict['FCST_VAR2_NAME'] = FCST_VAR2_NAME
    job_env_vars_dict['FCST_VAR2_LEVELS'] = FCST_VAR2_LEVELS
    job_env_vars_dict['FCST_VAR2_THRESHOLDS'] = FCST_VAR2_THRESHOLDS
    job_env_vars_dict['FCST_VAR2_OPTIONS'] = FCST_VAR2_OPTIONS
    job_env_vars_dict['OBS_VAR2_NAME'] = OBS_VAR2_NAME
    job_env_vars_dict['OBS_VAR2_LEVELS'] = OBS_VAR2_LEVELS
    job_env_vars_dict['OBS_VAR2_THRESHOLDS'] = OBS_VAR2_THRESHOLDS
    job_env_vars_dict['OBS_VAR2_OPTIONS'] = OBS_VAR2_OPTIONS
    job_env_vars_dict['GRID'] = GRID
    job_env_vars_dict['OUTPUT_FLAG_CTC'] = OUTPUT_FLAG_CTC
    job_env_vars_dict['OUTPUT_FLAG_SL1L2'] = OUTPUT_FLAG_SL1L2
    job_env_vars_dict['OUTPUT_FLAG_VL1L2'] = OUTPUT_FLAG_VL1L2
    job_env_vars_dict['OUTPUT_FLAG_CNT'] = OUTPUT_FLAG_CNT
    job_env_vars_dict['OUTPUT_FLAG_VCNT'] = OUTPUT_FLAG_VCNT
    job_iterate_over_env_lists_dict['FHR_GROUP_LIST'] = {
        'list_items': re.split(r'[\s,]+', FHR_GROUP_LIST),
        'exports': ['FHR_END','FHR_INCR']
    }
    if NEST == 'firewx':
        '''
        job_env_vars_dict['MASK_POLY_LIST'] = (
            f'{MET_PLUS_OUT}/{VERIF_TYPE}/genvxmask/{NEST}.'
            + '{valid?fmt=%Y%m%d}/'
            + f'{NEST}.' + 't{valid=%2H}z_f{lead=%2H}.nc'
        )
        job_dependent_vars['MASK_POLY_LIST'] = {
            'exec_value': '',
            'bash_value': (
                f'{MET_PLUS_OUT}/{VERIF_TYPE}/genvxmask/{NEST}.'
                + '${VDATE}'+ f'/{NEST}.t{VHOUR}z_'+ 'f${FHR}.nc'
            ),
            'bash_conditional': '',
            'bash_conditional_value': '',
            'bash_conditional_else_value': ''
        }
        '''
        job_iterate_over_custom_lists_dict['FHR'] = {
            'custom_list': '`seq ${FHR_START} ${FHR_INCR} ${FHR_END}`',
            'export_value': '(printf "%02d" $FHR)',
            'dependent_vars': {
                'names': ['MASK_POLY_LIST'],
                'values': [(
                    f'{MET_PLUS_OUT}/{VERIF_TYPE}/genvxmask/{NEST}.'
                    + '${VDATE}'+ f'/{NEST}_t{VHOUR}z_'+ 'f${FHR}.nc'
                )],
            }
        }
        
    elif NEST == 'spc_otlk':
        job_dependent_vars['MASK_POLY_LIST'] = {
            'exec_value': '',
            'bash_value': '',
            'bash_conditional': '[[ ${VHOUR} -lt 12 ]]',
            'bash_conditional_value': '"' + ', '.join(
                glob.glob(os.path.join(
                    MET_PLUS_OUT,VERIF_TYPE,'genvxmask',f'spc_otlk.{VDATE}',
                    f'spc_otlk_*_v*-{VDATE}1200_for{VHOUR}Z*'
                ))
            ) + '"',
            'bash_conditional_else_value': '"' + ', '.join(
                glob.glob(os.path.join(
                    MET_PLUS_OUT,VERIF_TYPE,'genvxmask',f'spc_otlk.{VDATE}',
                    f'spc_otlk_*_v{VDATE}*for{VHOUR}Z*'
                ))
            ) + '"'
        }
    else:
        job_env_vars_dict['MASK_POLY_LIST'] = MASK_POLY_LIST
    job_dependent_vars['FHR_START'] = {
        'exec_value': '',
        'bash_value': (
            '$(python -c \"import cam_util; print(cam_util.get_fhr_start('
            + '\'${VHOUR}\',0,\'${FHR_INCR}\',\'${MIN_IHOUR}\'))\")'
        ),
        'bash_conditional': '',
        'bash_conditional_value': '',
        'bash_conditional_else_value': ''
    }
elif job_type == 'gather':
    job_env_vars_dict['VERIF_TYPE'] = VERIF_TYPE

# Make a list of commands needed to run this particular job
job_cmd_list_iterative = []
job_cmd_list = []
if STEP == 'prep':
    pass
elif STEP == 'stats':
    if job_type == 'reformat':
        if NEST == 'spc_otlk':
            job_cmd_list_iterative.append(
                f'python '
                + f'{USHevs}/{COMPONENT}/'
                + f'{COMPONENT}_{STEP}_{VERIF_CASE}_gen_{NEST}_mask.py'
            )
        elif NEST == 'firewx':
            job_cmd_list_iterative.append(
                f'{metplus_launcher} -c '
                + f'{MET_PLUS_CONF}/'
                + f'GenVxMask_{str(NEST).upper()}.conf'
            )
        job_cmd_list_iterative.append(
            f'{metplus_launcher} -c '
            + f'{MET_PLUS_CONF}/'
            + f'PB2NC_obs{VERIF_TYPE.upper()}.conf'
        )
    if job_type == 'generate':
        if FCST_VAR2_NAME:
            if NEST == 'firewx':
                job_cmd_list_iterative.append(
                    f'{metplus_launcher} -c '
                    + f'{MET_PLUS_CONF}/'
                    + f'PointStat_fcst{COMPONENT.upper()}_'
                    + f'obs{VERIF_TYPE.upper()}_{str(NEST).upper()}_VAR2.conf'
                )
            else:
                job_cmd_list_iterative.append(
                    f'{metplus_launcher} -c '
                    + f'{MET_PLUS_CONF}/'
                    + f'PointStat_fcst{COMPONENT.upper()}_obs{VERIF_TYPE.upper()}_VAR2.conf'
                )
        else:
            if NEST == 'firewx':
                job_cmd_list_iterative.append(
                    f'{metplus_launcher} -c '
                    + f'{MET_PLUS_CONF}/'
                    + f'PointStat_fcst{COMPONENT.upper()}_'
                    + f'obs{VERIF_TYPE.upper()}_{str(NEST).upper()}.conf'
                )
            else:
                job_cmd_list_iterative.append(
                    f'{metplus_launcher} -c '
                    + f'{MET_PLUS_CONF}/'
                    + f'PointStat_fcst{COMPONENT.upper()}_obs{VERIF_TYPE.upper()}.conf'
                )
    elif job_type == 'gather':
        job_cmd_list.append(
            f'{metplus_launcher} -c '
            + f'{MET_PLUS_CONF}/'
            + f'StatAnalysis_fcst{COMPONENT.upper()}_obs{VERIF_TYPE.upper()}'
            + f'_GatherByDay.conf'
        )
    elif job_type == 'gather2':
        job_cmd_list.append(
            f'{metplus_launcher} -c '
            + f'{MET_PLUS_CONF}/'
            + f'StatAnalysis_fcst{COMPONENT.upper()}'
            + f'_GatherByCycle.conf'
        )
    elif job_type == 'gather3':
        job_cmd_list.append(
            f'{metplus_launcher} -c '
            + f'{MET_PLUS_CONF}/'
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
