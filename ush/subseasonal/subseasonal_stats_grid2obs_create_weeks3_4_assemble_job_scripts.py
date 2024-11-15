#!/usr/bin/env python3
'''
Program Name: subseasonal_stats_grid2obs_create_weeks3_4_assemble_job_scripts.py
Contact(s): Shannon Shields
Abstract: This script is run by exevs_subseasonal_grid2obs_stats.sh
          in scripts/stats/subseasonal.
          This creates multiple independent job scripts. These
          jobs contain all the necessary environment variables
          and commands needed to run the specific
          use case.
'''

import sys
import os
import glob
import datetime
import numpy as np
import subseasonal_util as sub_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
WEEKS = os.environ['WEEKS']
CORRECT_INIT_DATE = os.environ['CORRECT_INIT_DATE']
CORRECT_LEAD_SEQ = os.environ['CORRECT_LEAD_SEQ']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
METPLUS_PATH = os.environ['METPLUS_PATH']
MET_ROOT = os.environ['MET_ROOT']
PARMevs = os.environ['PARMevs']
model_list = os.environ['model_list'].split(' ')
members = os.environ['members']
njobs = os.environ['njobs']

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')

# Set up job directory
JOB_GROUP_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                  'METplus_job_scripts', JOB_GROUP)
if not os.path.exists(JOB_GROUP_jobs_dir):
    os.makedirs(JOB_GROUP_jobs_dir)

################################################
#### assemble_data jobs
################################################
assemble_data_obs_jobs_dict = {
    'prepbufr': {}
}
assemble_data_model_jobs_dict = {
    'prepbufr': {
        'TempAnom2m': {'env': {'prepbufr': 'nam',
                               'obs_window': '900',
                               'msg_type': 'ADPSFC',
                               'var1_fcst_name': 'TMP_Z2_ENS_MEAN',
                               'var1_fcst_levels': 'Z2',
                               'var1_fcst_options': '',
                               'var1_obs_name': 'TMP',
                               'var1_obs_levels': 'Z2',
                               'var1_obs_options': '',
                               'met_config_overrides': ("'climo_mean "
                                                        +"= obs;'")},
                       'commands': [sub_util.metplus_command(
                                        'PointStat_fcstSUBSEASONAL_'
                                        +'obsPrepbufr_climoERA5_'
                                        +'Weeks3_4MPR.conf'
                                    ),
                                    sub_util.python_command(
                                        'subseasonal_stats_'
                                        'grid2obs_create_'
                                        'weeks3_4_anomaly.py',
                                        []
                                    )]},
    }
}


# Do assemble_data observation jobs
if JOB_GROUP in ['reformat_data', 'assemble_data']:
    if JOB_GROUP == 'reformat_data':
        JOB_GROUP_obs_jobs_dict = reformat_data_obs_jobs_dict
    elif JOB_GROUP == 'assemble_data':
        JOB_GROUP_obs_jobs_dict = assemble_data_obs_jobs_dict
    for verif_type in VERIF_CASE_STEP_type_list:
        print("----> Making job scripts for "+VERIF_CASE_STEP+" "
              +verif_type+" for job group "+JOB_GROUP)
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +verif_type)
        # Read in environment variables for verif_type
        for verif_type_job in list(JOB_GROUP_obs_jobs_dict[verif_type]\
                                   .keys()):
            # Initialize job environment dictionary
            job_env_dict = sub_util.initialize_job_env_dict(
                verif_type, JOB_GROUP, VERIF_CASE_STEP_abbrev_type,
                verif_type_job
            )
            job_env_dict.pop('fhr_start')
            job_env_dict.pop('fhr_end')
            job_env_dict.pop('fhr_inc')
            # Add job specific environment variables
            for verif_type_job_env_var in \
                    list(JOB_GROUP_obs_jobs_dict[verif_type]\
                         [verif_type_job]['env'].keys()):
                job_env_dict[verif_type_job_env_var] = (
                    JOB_GROUP_obs_jobs_dict[verif_type]\
                    [verif_type_job]['env'][verif_type_job_env_var]
                )
            verif_type_job_commands_list = (
                JOB_GROUP_obs_jobs_dict[verif_type]\
                [verif_type_job]['commands']
            ) 
            # Loop through and write job script for dates and models
            if JOB_GROUP == 'assemble_data':
                if verif_type == 'prepbufr':
                    job_env_dict['valid_hr_start'] = '00'
                    job_env_dict['valid_hr_end'] = '00'
                    job_env_dict['valid_hr_inc'] = '12'
            valid_start_date_dt = datetime.datetime.strptime(
                start_date+job_env_dict['valid_hr_start'],
                '%Y%m%d%H'
            )
            valid_end_date_dt = datetime.datetime.strptime(
                end_date+job_env_dict['valid_hr_end'],
                '%Y%m%d%H'
            )
            valid_date_inc = int(job_env_dict['valid_hr_inc'])
            date_dt = valid_start_date_dt
            while date_dt <= valid_end_date_dt:
                sdate_dt = date_dt - datetime.timedelta(days=14)
                job_env_dict['START'] = sdate_dt.strftime('%Y%m%d')
                job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                job_env_dict['valid_hr_start'] = date_dt.strftime('%H')
                job_env_dict['valid_hr_end'] = date_dt.strftime('%H')
                njobs = (int(njobs) + 1)
                # Create job file
                job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/bash\n')
                job.write('set -x\n')
                job.write('\n')
                # Set any environment variables for special cases
                # Do file checks
                all_truth_file_exist = sub_util.check_truth_files(
                    job_env_dict
                )
                if all_truth_file_exist:
                    write_job_cmds = True
                else:
                    write_job_cmds = False
                # Write environment variables
                for name, value in job_env_dict.items():
                    job.write('export '+name+'='+value+'\n')
                job.write('\n')
                # Write job commands
                if write_job_cmds:
                    for cmd in verif_type_job_commands_list:
                        job.write(cmd+'\n')
                        job.write('export err=$?; err_chk'+'\n')
                job.close()
                date_dt = date_dt + datetime.timedelta(hours=valid_date_inc)
        # Create model job scripts
        if JOB_GROUP in ['reformat_data', 'assemble_data']:
            if JOB_GROUP == 'reformat_data':
                JOB_GROUP_jobs_dict = reformat_data_model_jobs_dict
            elif JOB_GROUP == 'assemble_data':
                JOB_GROUP_jobs_dict = assemble_data_model_jobs_dict
            for verif_type_job in list(JOB_GROUP_jobs_dict[verif_type]\
                                       .keys()):
                # Initialize job environment dictionary
                job_env_dict = sub_util.initialize_job_env_dict(
                    verif_type, JOB_GROUP, VERIF_CASE_STEP_abbrev_type,
                    verif_type_job
                )
                # Add job specific environment variables
                for verif_type_job_env_var in \
                        list(JOB_GROUP_jobs_dict[verif_type]\
                             [verif_type_job]['env'].keys()):
                    job_env_dict[verif_type_job_env_var] = (
                        JOB_GROUP_jobs_dict[verif_type]\
                        [verif_type_job]['env'][verif_type_job_env_var]
                    )
                fhr_start = job_env_dict['fhr_start']
                fhr_end = job_env_dict['fhr_end']
                fhr_inc = job_env_dict['fhr_inc']
                verif_type_job_commands_list = (
                    JOB_GROUP_jobs_dict[verif_type]\
                    [verif_type_job]['commands']
                )
                # Loop through and write job script for dates and models
                if JOB_GROUP == 'assemble_data':
                    if verif_type == 'prepbufr' \
                            and verif_type_job == 'TempAnom2m':
                        job_env_dict['valid_hr_start'] = '00'
                        job_env_dict['valid_hr_end'] = '00'
                        job_env_dict['valid_hr_inc'] = '12'
                valid_start_date_dt = datetime.datetime.strptime(
                    start_date+job_env_dict['valid_hr_start'],
                    '%Y%m%d%H'
                )
                valid_end_date_dt = datetime.datetime.strptime(
                    end_date+job_env_dict['valid_hr_end'],
                    '%Y%m%d%H'
                )
                valid_date_inc = int(job_env_dict['valid_hr_inc'])
                job_env_dict['WEEKS'] = WEEKS
                job_env_dict['CORRECT_INIT_DATE'] = CORRECT_INIT_DATE
                job_env_dict['CORRECT_LEAD_SEQ'] = CORRECT_LEAD_SEQ
                date_dt = valid_start_date_dt
                while date_dt <= valid_end_date_dt:
                    sdate_dt = date_dt - datetime.timedelta(days=14)
                    job_env_dict['W3_4START'] = sdate_dt.strftime('%Y%m%d')
                    job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                    job_env_dict['valid_hr_start'] = date_dt.strftime('%H')
                    job_env_dict['valid_hr_end'] = date_dt.strftime('%H')
                    for model_idx in range(len(model_list)):
                        job_env_dict['MODEL'] = model_list[model_idx]
                        njobs = (int(njobs) + 1)
                        job_env_dict['job_num'] = str(njobs)
                        # Create job file
                        job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
                        print("Creating job script: "+job_file)
                        job = open(job_file, 'w')
                        job.write('#!/bin/bash\n')
                        job.write('set -x\n')
                        job.write('\n')
                        # Create job working directory
                        job_env_dict['job_num_work_dir'] = os.path.join(
                            DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',
                            'job_work_dir', JOB_GROUP,
                            f"job{job_env_dict['job_num']}"
                        )
                        job_env_dict['MET_TMP_DIR'] = os.path.join(
                            job_env_dict['job_num_work_dir'], 'tmp'
                        )
                        # Set any environment variables for special cases
                        if JOB_GROUP == 'assemble_data':
                            if verif_type == 'prepbufr':
                                job_env_dict['grid'] = 'G003'
                                mask_list = [
                                    'G003_GLOBAL',
                                    'Bukovsky_G003_CONUS',
                                    'Hawaii_G003',
                                    'Alaska_G003'
                                ]
                            for mask in mask_list:
                                if mask == mask_list[0]:
                                    env_var_mask_list = ("'"+job_env_dict['FIXevs']
                                                         +"/masks/"+mask+".nc, ")
                                elif mask == mask_list[-1]:
                                    env_var_mask_list = (env_var_mask_list
                                                         +job_env_dict['FIXevs']
                                                         +"/masks/"+mask+".nc'")
                                else:
                                    env_var_mask_list = (env_var_mask_list
                                                         +job_env_dict['FIXevs']
                                                         +"/masks/"+mask+".nc, ")
                            job_env_dict['mask_list'] = env_var_mask_list
                        # Do file checks
                        check_model_files = True
                        check_truth_files = True
                        if check_model_files:
                            (model_files_exist, valid_date_fhr_list,
                             model_copy_output_list) = (
                                sub_util.check_weeks3_4_model_files(job_env_dict)
                            )
                            job_env_dict['fhr_list'] = (
                                '"'+','.join(valid_date_fhr_list)+'"'
                            )
                            job_env_dict.pop('fhr_start')
                            job_env_dict.pop('fhr_end')
                            job_env_dict.pop('fhr_inc')
                        if check_truth_files:
                            (all_truth_file_exist,
                             truth_copy_output_list) = (
                                sub_util.check_weeks3_4_truth_files(job_env_dict)
                            )
                            if model_files_exist and all_truth_file_exist:
                                write_job_cmds = True
                            else:
                                write_job_cmds = False
                        else:
                            if model_files_exist:
                                write_job_cmds = True
                            else:
                                write_job_cmds = False
                        # Write environment variables
                        for name, value in job_env_dict.items():
                            job.write('export '+name+'='+value+'\n')
                        job.write('\n')
                        # Write job commands
                        if write_job_cmds:
                            if not os.path.exists(job_env_dict['job_num_work_dir']):
                                os.makedirs(job_env_dict['job_num_work_dir'])
                            for cmd in verif_type_job_commands_list:
                                job.write(cmd+'\n')
                                job.write('export err=$?; err_chk'+'\n')
                            # Copy files to COMOUT restart dir
                            # to be used in possible restart
                            if job_env_dict['SENDCOM'] == 'YES':
                                for model_output_file_tuple \
                                        in model_copy_output_list:
                                    job.write(f'if [ -f "{model_output_file_tuple[0]}" ]; then '
                                              +f"cp -v {model_output_file_tuple[0]} "
                                              +f"{model_output_file_tuple[1]}"
                                              +f"; fi\n")
                        else:
                            if JOB_GROUP == 'assemble_data':
                                if verif_type_job == 'TempAnom2m':
                                    job.write(verif_type_job_commands_list[1])
                        job.close()
                        job_env_dict.pop('fhr_list')
                        job_env_dict['fhr_start'] = fhr_start
                        job_env_dict['fhr_end'] = fhr_end
                        job_env_dict['fhr_inc'] = fhr_inc
                    date_dt = date_dt + datetime.timedelta(hours=valid_date_inc)


print("END: "+os.path.basename(__file__))
