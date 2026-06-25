#!/usr/bin/env python3
"""
cam_prep_model_precip_create_job_script.py
CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov
----------------------
Creates job scripts for Precip verification in the cam component.

Environment Variables (Inputs):
    Various variables including vhr, job_type, PYTHONPATH, COMPONENT, NET,
    STEP, RUN, VERIF_CASE, MODELNAME, METPLUS_PATH, MET_ROOT, DATA, and many
    others required for job script creation and configuration.

Outputs:
    - Generates job scripts for running reformatting portion of Precip 
      verification.
    - Prints errors and exits if required environment variables are missing or
      invalid.

This script is intended to be run as part of the cam component to automate
creation of job scripts for Precip verification.
"""

import glob
import os
import re
from datetime import datetime

import cam_util as cutil

print(f"BEGIN: {os.path.basename(__file__)}")

# Read in environment variables
vhr = os.environ['vhr']
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
SENDCOM = os.environ['SENDCOM']
INITDATE = os.environ['INITDATE']
IHOUR = os.environ['IHOUR']
MET_PLUS_CONF = os.environ['MET_PLUS_CONF']
MET_CONFIG_OVERRIDES = os.environ['MET_CONFIG_OVERRIDES']
machine_conf = os.path.join(
    os.environ['PARMevs'], 'metplus_config', 'machine.conf'
)
COMPLETED_JOBS_DIR = os.environ['COMPLETED_JOBS_DIR']
VERIF_TYPE = os.environ['VERIF_TYPE']
NEST = os.environ['NEST']
IHOUR = os.environ['IHOUR']
FHR_GROUP_LIST = os.environ['FHR_GROUP_LIST']
FHR_END_SHORT = os.environ['FHR_END_SHORT']
FHR_INCR_SHORT = os.environ['FHR_INCR_SHORT']
FHR_END_FULL = os.environ['FHR_END_FULL']
FHR_INCR_FULL = os.environ['FHR_INCR_FULL']
MIN_IHOUR = os.environ['MIN_IHOUR']
COMINfcst = os.environ['COMINfcst']
MODEL_INPUT_TEMPLATE = os.environ['MODEL_INPUT_TEMPLATE']
njob = os.environ['njob']
MET_PLUS_OUT = os.path.join(
    os.environ['MET_PLUS_OUT'], 'workdirs', f'job{njob}'
)
BUCKET_INTERVAL = os.environ['BUCKET_INTERVAL']
MODEL_ACC = os.environ['MODEL_ACC']
ACC = os.environ['ACC']
COMPONENT = os.environ['COMPONENT']
MODEL_PCP_COMBINE_METHOD = os.environ['MODEL_PCP_COMBINE_METHOD']
MODEL_PCP_COMBINE_COMMAND = os.environ['MODEL_PCP_COMBINE_COMMAND']
USE_ZERO_ACCUM = os.environ['USE_ZERO_ACCUM']

# Make a dictionary of environment variables needed to run this particular job
job_env_vars_dict = {
    'vhr': vhr,
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
    'SENDCOM': SENDCOM,
    'INITDATE': INITDATE,
    'IHOUR': IHOUR,
    'MET_PLUS_CONF': MET_PLUS_CONF,
    'MET_PLUS_OUT': MET_PLUS_OUT,
    'MET_CONFIG_OVERRIDES': MET_CONFIG_OVERRIDES,
}
job_iterate_over_env_lists_dict = {}
job_dependent_vars = {}
job_env_vars_dict['VERIF_TYPE'] = VERIF_TYPE
job_env_vars_dict['NEST'] = NEST
job_env_vars_dict['FHR_GROUP_LIST'] = FHR_GROUP_LIST
job_env_vars_dict['FHR_END_SHORT'] = FHR_END_SHORT
job_env_vars_dict['FHR_INCR_SHORT'] = FHR_INCR_SHORT
job_env_vars_dict['FHR_END_FULL'] = FHR_END_FULL
job_env_vars_dict['FHR_INCR_FULL'] = FHR_INCR_FULL
job_env_vars_dict['MIN_IHOUR'] = MIN_IHOUR
job_env_vars_dict['COMINfcst'] = COMINfcst
job_env_vars_dict['MODEL_INPUT_TEMPLATE'] = MODEL_INPUT_TEMPLATE
job_env_vars_dict['BUCKET_INTERVAL'] = BUCKET_INTERVAL
job_iterate_over_env_lists_dict['FHR_GROUP_LIST'] = {
    'list_items': re.split(r'[\s,]+', FHR_GROUP_LIST),
    'exports': ['FHR_END','FHR_INCR']
}
job_env_vars_dict['MODEL_ACC'] = MODEL_ACC
job_env_vars_dict['ACC'] = ACC
job_env_vars_dict['MODEL_PCP_COMBINE_METHOD'] = MODEL_PCP_COMBINE_METHOD
job_env_vars_dict['MODEL_PCP_COMBINE_COMMAND'] = MODEL_PCP_COMBINE_COMMAND
job_env_vars_dict['USE_ZERO_ACCUM'] = USE_ZERO_ACCUM
job_dependent_vars['FHR_START'] = {
    'exec_value': '',
    'bash_value': (
        '$(python -c \"import cam_util; print(cam_util.get_fhr_start('
        + '\'${IHOUR}\',\'${ACC}\',\'${FHR_INCR}\',\'${MIN_IHOUR}\',use_vhour=False))\")'
    ),
    'bash_conditional': '',
    'bash_conditional_value': ''
}
job_dependent_vars['MODEL_INPUT_LEVS'] = {
    'exec_value': '',
    'bash_value': (
        '\"'
        + ', '.join(
            ['A'+item for item in re.split(r'[\s,]+', MODEL_ACC)]
        )
        +'\"'
    ),
    'bash_conditional': '',
    'bash_conditional_value': ''
}
job_dependent_vars['MODEL_INPUT_VAR_NAMES'] = {
    'exec_value': '',
    'bash_value': (
        '\"'
        + ', '.join(
            ['APCP' for item in re.split(r'[\s,]+', MODEL_ACC)]
        )
        +'\"'
    ),
    'bash_conditional': '',
    'bash_conditional_value': ''
}

# Make a list of commands needed to run this particular job
metplus_launcher = 'run_metplus.py'
job_cmd_list_iterative = []
job_cmd_list = []
if FHR_GROUP_LIST:
    if not f'job{njob}' in cutil.get_completed_jobs(os.path.join(RESTART_DIR, COMPLETED_JOBS_DIR)):
        job_cmd_list_iterative.append(
            f'{metplus_launcher} -c {machine_conf} '
            + f'-c {MET_PLUS_CONF}/'
            + f'PCPCombine_fcst{COMPONENT.upper()}.conf'
        )
        job_cmd_list_iterative.append(
            f'python -c '
            + '\"import cam_util as cutil; cutil.copy_data_to_restart('
            + '\\\"${DATA}\\\", \\\"${RESTART_DIR}\\\", '
            + f'njob=\\\"{njob}\\\", '
            + 'verif_case=\\\"${VERIF_CASE}\\\", '
            + 'verif_type=\\\"${VERIF_TYPE}\\\", '
            + 'vx_mask=\\\"${NEST}\\\", '
            + 'met_tool=\\\"pcp_combine\\\", '
            + 'idate=\\\"${INITDATE}\\\", '
            + 'ihour=\\\"${IHOUR}\\\", '
            + 'fhr_start=\\\"${FHR_START}\\\", '
            + 'fhr_end=\\\"${FHR_END}\\\", '
            + 'fhr_incr=\\\"${FHR_INCR}\\\", '
            + 'model=\\\"${MODELNAME}\\\", '
            + 'acc=\\\"${ACC}\\\"'
            + ')\"'
        )
        job_cmd_list.append(
            "python -c "
            + f"'import cam_util; cam_util.mark_job_completed("
            + f"\"{RESTART_DIR}\", \"{DATA}\", \"{VERIF_CASE}\", \"{COMPLETED_JOBS_DIR}\", "
            + f"\"job{njob}\", job_type=\"prep_precip\")'"
        )

# Write job script
indent = ''
indent_width = 4
iterative_first = True
job_dir = os.path.join(DATA, VERIF_CASE, 'METplus_job_scripts')
if not os.path.exists(job_dir):
    os.makedirs(job_dir)
job_file = os.path.join(job_dir, f'job{njob}')
if not job_cmd_list and not job_cmd_list_iterative:
    print(f"No commands to run / not creating job script: {job_file}")
else:
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
            job.write(f'export err=$?; err_chk'+'\n')
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
        job.write(f'{indent}export err=$?; err_chk'+'\n')
    for name_list, value_list in job_iterate_over_env_lists_dict.items():
        indent = indent[indent_width:]
        job.write(f'{indent}done\n')
    if iterative_first:
        for cmd in job_cmd_list:
            job.write(f'{cmd}\n')
            job.write(f'export err=$?; err_chk'+'\n')
    job.close()

print(f"END: {os.path.basename(__file__)}")
