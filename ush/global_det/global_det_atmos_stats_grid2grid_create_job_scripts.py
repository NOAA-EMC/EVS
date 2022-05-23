'''
Program Name: global_det_atmos_stats_grid2grid_create_job_scripts.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This creates multiple independent job scripts. These
          jobs contain all the necessary environment variables
          and METplus commands to needed to run the specific
          use case.
'''

import sys
import os
import glob
import datetime
import numpy as np
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
METPLUS_PATH = os.environ['METPLUS_PATH']
MET_ROOT = os.environ['MET_ROOT']
MET_bin_exec = os.environ['MET_bin_exec']
PARMevs = os.environ['PARMevs']
model_list = os.environ['model_list'].split(' ')
precip_file_accum_list = (os.environ \
                          [VERIF_CASE_STEP_abbrev+'_precip_file_accum_list'] \
                          .split(' '))
precip_var_list = (os.environ \
                   [VERIF_CASE_STEP_abbrev+'_precip_var_list'] \
                    .split(' '))

# Set up METplus job command dictionary
metplus_cmd_prefix = (
    os.path.join(METPLUS_PATH, 'ush', 'run_metplus.py')
    +' -c '+os.path.join(PARMevs, 'metplus_config', 'machine.conf')
    +' -c '+os.path.join(PARMevs, 'metplus_config', COMPONENT,
                         RUN+'_'+VERIF_CASE, STEP)
    +'/'
)

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
################################################
#### Reformat jobs
################################################
reformat_obs_jobs_dict = {
    'pres_levs': {},
    'means': {},
    'ozone': {},
    'precip': {'24hrCCPA': {'env': {},
                            'commands': [metplus_cmd_prefix
                                         +'PCPCombine_obs24hrCCPA.conf']}},
    'sea_ice': {},
    'snow': {},
    'sst': {},
}
reformat_model_jobs_dict = {
    'pres_levs': {},
    'means': {},
    'ozone': {},
    'precip': {'24hrAccum': {'env': {'valid_hr': '12',
                                     'MODEL_template': ('{MODEL}.precip.'
                                                        +'{init?fmt=%Y%m%d%H}.'
                                                        +'f{lead?fmt=%HHH}')},
                             'commands': [metplus_cmd_prefix
                                          +'PCPCombine_fcstGLOBAL_DET_'
                                          +'24hrAccum_precip.conf']}},
    'sea_ice': {},
    'snow': {'24hrAccum_WaterEqv': {'env': {'valid_hr': '12',
                                            'MODEL_var': 'WEASD'},
                                    'commands': [metplus_cmd_prefix
                                                 +'PCPCombine_fcstGLOBAL_DET_'
                                                 +'24hrAccum_snow.conf']},
             '24hrAccum_Depth': {'env': {'valid_hr': '12',
                                         'MODEL_var': 'SNOD'},
                                 'commands': [metplus_cmd_prefix
                                              +'PCPCombine_fcstGLOBAL_DET_'
                                              +'24hrAccum_snow.conf']}},
    'sst': {},
}

# Create reformat jobs directory
njobs = 0
reformat_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                 'reformat')
if not os.path.exists(reformat_jobs_dir):
    os.makedirs(reformat_jobs_dir)
for verif_type in VERIF_CASE_STEP_type_list:
    VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                   +verif_type)
    verif_type_reformat_obs_jobs_dict = (
        reformat_obs_jobs_dict[verif_type]
    )
    verif_type_reformat_model_jobs_dict = (
        reformat_model_jobs_dict[verif_type]
    )
    # Reformat obs jobs
    for verif_type_job in list(verif_type_reformat_obs_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, 'reformat',
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        # Add job specific environment variables
        for verif_type_job_env_var in \
                list(verif_type_reformat_obs_jobs_dict\
                     [verif_type_job]['env'].keys()):
            job_env_dict[verif_type_job_env_var] = (
                verif_type_reformat_obs_jobs_dict\
                [verif_type_job]['env'][verif_type_job_env_var]
            )
        verif_type_job_commands_list = (
            verif_type_reformat_obs_jobs_dict\
            [verif_type_job]['commands']
        )
        # Loop through and write job script for dates
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
            njobs+=1
            # Create job file
            job_file = os.path.join(reformat_jobs_dir, 'job'+str(njobs))
            print("Creating job script: "+job_file)
            job = open(job_file, 'w')
            job.write('#!/bin/sh\n')
            job.write('set -x\n')
            job.write('\n')
            # Set any environment variables for special cases
            # Write environment variables
            for name, value in job_env_dict.items():
                job.write('export '+name+'='+value+'\n')
            job.write('\n')
            # Write job commands
            for cmd in verif_type_job_commands_list:
                job.write(cmd+'\n')
            job.close()
            date_dt = date_dt + datetime.timedelta(days=1)
    # Reformat model jobs
    for verif_type_job in list(verif_type_reformat_model_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, 'reformat',
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        # Add job specific environment variables
        for verif_type_job_env_var in \
                list(verif_type_reformat_model_jobs_dict\
                     [verif_type_job]['env'].keys()):
            job_env_dict[verif_type_job_env_var] = (
                verif_type_reformat_model_jobs_dict\
                [verif_type_job]['env'][verif_type_job_env_var]
            )
        verif_type_job_commands_list = (
            verif_type_reformat_model_jobs_dict\
            [verif_type_job]['commands']
        )
        # Loop through and write job script for dates and models
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
            for model_idx in range(len(model_list)):
                job_env_dict['MODEL'] = model_list[model_idx]
                njobs+=1
                # Create job file
                job_file = os.path.join(reformat_jobs_dir, 'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/sh\n')
                job.write('set -x\n')
                job.write('\n')
                # Set any environment variables for special cases
                if verif_type == 'precip':
                    job_env_dict['MODEL_var'] = precip_var_list[model_idx]
                    if precip_file_accum_list[model_idx] == 'continuous':
                        job_env_dict['pcp_combine_method'] = 'SUBTRACT'
                        job_env_dict['MODEL_accum'] = '{lead?fmt=%HH}'
                        job_env_dict['MODEL_levels'] = 'A{lead?fmt=%HH}'
                    else:
                        job_env_dict['pcp_combine_method'] = 'SUM'
                        job_env_dict['MODEL_accum'] = (
                            precip_file_accum_list[model_idx]
                        )
                        job_env_dict['MODEL_levels'] = (
                            'A'+job_env_dict['MODEL_accum']
                        )
                # Write environment variables
                for name, value in job_env_dict.items():
                    job.write('export '+name+'='+value+'\n')
                job.write('\n')
                # Write job commands
                for cmd in verif_type_job_commands_list:
                    job.write(cmd+'\n')
                job.close()
            date_dt = date_dt + datetime.timedelta(days=1)

################################################
#### Statistics jobs
################################################
# Statistics jobs information dictionary
stats_jobs_dict = {
    'pres_levs': {},
    'means': {},
    'ozone': {},
    'precip': {},
    'sea_ice': {},
    'snow': {},
    'sst': {},
}

################################################
#### Gather jobs
################################################
# Gather jobs information dictionary
gather_jobs_dict = {'env': {},
                    'commands': []},

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    for group in ['reformat', 'make_met_data', 'gather']:
        job_files = glob.glob(os.path.join(DATA, VERIF_CASE_STEP,
                                           'METplus_job_scripts', group,
                                           'job*'))
        njob_files = len(job_files)
        if njob_files == 0:
            print("ERROR: No job files created in "
                  +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                group))
        njob, iproc, node = 1, 0, 1
        while njob <= njob_files:
            job = 'job'+str(njob)
            if machine in ['HERA', 'ORION', 'S4', 'JET']:
                if iproc >= int(nproc):
                    poe_file.close()
                    iproc = 0
                    node+=1
            poe_filename = os.path.join(DATA, VERIF_CASE_STEP,
                                        'METplus_job_scripts',
                                        group, 'poe_jobs'+str(node))
            if iproc == 0:
                poe_file = open(poe_filename, 'w')
            iproc+=1
            if machine in ['HERA', 'ORION', 'S4', 'JET']:
                poe_file.write(
                    str(iproc-1)+' '
                    +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                  group, job)+'\n'
                )
            else:
                poe_file.write(
                    os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                 group, job)+'\n'
                )
            njob+=1
        poe_file.close()
        # If at final record and have not reached the
        # final processor then write echo's to
        # poe script for remaining processors
        poe_file = open(poe_filename, 'a')
        iproc+=1
        while iproc <= int(nproc):
            if machine in ['HERA', 'ORION', 'S4', 'JET']:
                poe_file.write(
                    str(iproc-1)+' /bin/echo '+str(iproc)+'\n'
                )
            else:
                poe_file.write(
                    '/bin/echo '+str(iproc)+'\n'
                )
            iproc+=1
    poe_file.close()

print("END: "+os.path.basename(__file__))
