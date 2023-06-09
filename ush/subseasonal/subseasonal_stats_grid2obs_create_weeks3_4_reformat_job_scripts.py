#!/usr/bin/env python3
'''
Program Name: subseasonal_stats_grid2obs_create_weeks3_4_reformat_job_scripts.py
Contact(s): Shannon Shields
Abstract: This creates multiple independent job scripts. These
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
MET_bin_exec = os.environ['MET_bin_exec']
PARMevs = os.environ['PARMevs']
model_list = os.environ['model_list'].split(' ')
members = os.environ['members']
njobs = os.environ['njobs']

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')

# Set up job directory
#njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                  'METplus_job_scripts', JOB_GROUP)
if not os.path.exists(JOB_GROUP_jobs_dir):
    os.makedirs(JOB_GROUP_jobs_dir)

################################################
#### reformat_data jobs
################################################
reformat_data_obs_jobs_dict = {
    'PrepBufr': {
        'PrepbufrNAM': {'env': {'prepbufr': 'nam',
                                'obs_window': '900',
                                'msg_type': 'ADPSFC',
                                'obs_bufr_var_list': "'TOB'"},
                        'commands': [sub_util.metplus_command(
                                         'PB2NC_obsPrepbufr.conf'
                                     )]},
    }
}
reformat_data_model_jobs_dict = {
    'PrepBufr': {
        'GenEnsProd': {'env': {'var1_name': 'TMP',
                               'var1_levels': 'Z2'},
                       'commands': [sub_util.metplus_command(
                                        'GenEnsProd_fcstSUBSEASONAL_'
                                        +'Weeks3_4NetCDF.conf'
                                    )]},
    }
}


# Do reformat_data observation jobs
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
            job_env_dict = sub_util.initalize_job_env_dict(
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
            if JOB_GROUP == 'reformat_data':
                if verif_type == 'PrepBufr':
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
                all_truth_file_exist = sub_util.check_weeks3_4_truth_files(
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
                job_env_dict = sub_util.initalize_job_env_dict(
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
                if JOB_GROUP == 'reformat_data':
                    if verif_type == 'PrepBufr' \
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
                    job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                    job_env_dict['valid_hr_start'] = date_dt.strftime('%H')
                    job_env_dict['valid_hr_end'] = date_dt.strftime('%H')
                    for model_idx in range(len(model_list)):
                        job_env_dict['MODEL'] = model_list[model_idx]
                        njobs = (int(njobs) + 1)
                        # Create job file
                        job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
                        print("Creating job script: "+job_file)
                        job = open(job_file, 'w')
                        job.write('#!/bin/bash\n')
                        job.write('set -x\n')
                        job.write('\n')
                        # Set any environment variables for special cases
                        if JOB_GROUP == 'reformat_data':
                            if verif_type == 'PrepBufr':
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
                        check_truth_files = False
                        if check_model_files:
                            model_files_exist, valid_date_fhr_list = (
                                sub_util.check_weeks3_4_model_files(job_env_dict)
                            )
                            job_env_dict['fhr_list'] = (
                                '"'+','.join(valid_date_fhr_list)+'"'
                            )
                            job_env_dict.pop('fhr_start')
                            job_env_dict.pop('fhr_end')
                            job_env_dict.pop('fhr_inc')
                        if check_truth_files:
                            all_truth_file_exist = sub_util.check_truth_files(
                                job_env_dict
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
                            for cmd in verif_type_job_commands_list:
                                job.write(cmd+'\n')
                        job.close()
                        job_env_dict.pop('fhr_list')
                        job_env_dict['fhr_start'] = fhr_start
                        job_env_dict['fhr_end'] = fhr_end
                        job_env_dict['fhr_inc'] = fhr_inc
                    date_dt = date_dt + datetime.timedelta(hours=valid_date_inc)


print("END: "+os.path.basename(__file__))
