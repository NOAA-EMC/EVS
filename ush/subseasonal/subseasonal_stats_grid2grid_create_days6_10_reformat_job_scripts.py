#!/usr/bin/env python3
'''
Program Name: subseasonal_stats_grid2grid_create_days6_10_reformat_job_scripts.py
Contact(s): Shannon Shields
Abstract: This script is run by exevs_subseasonal_grid2grid_stats.sh
          in scripts/stats/subseasonal.
          This creates multiple independent job scripts. These
          jobs contain all the necessary environment variables
          and commands to needed to run the specific
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
DAYS = os.environ['DAYS']
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
#### reformat_data jobs
################################################
reformat_data_obs_jobs_dict = {
    'temp': {},
    'pres_lvls': {},
    'seaice': {},
    'sst': {},
}
reformat_data_gefs_jobs_dict = {
    'pres_lvls': {
        'GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                  'var1_levels': 'P500',
                                  'met_config_overrides': (
                                      "'climo_mean = obs;'"
                                  )},
                          'commands': [sub_util.metplus_command(
                                           'GenEnsProd_fcstSUBSEASONAL_'
                                           +'Days6_10NetCDF.conf'
                                       ),
                                       sub_util.metplus_command(
                                           'GridStat_fcstSUBSEASONAL_'
                                           +'obsGFS_climoERA5_'
                                           +'Days6_10NetCDF.conf'
                                       ),
                                       sub_util.python_command(
                                           'subseasonal_stats_grid2grid'
                                           '_create_days6_10_anomaly.py',
                                           ['HGT_P500',
                                            os.path.join(
                                                '$DATA',
                                                '${VERIF_CASE}_${STEP}',
                                                'METplus_output',
                                                '${RUN}.$DATE',
                                                '$MODEL', '$VERIF_CASE',
                                                'grid_stat_${VERIF_TYPE}_'
                                                +'${job_name}_'
                                                +'{lead?fmt=%2H}0000L_'
                                                +'{valid?fmt=%Y%m%d}_'
                                                +'{valid?fmt=%H}0000V_pairs.nc'
                                            )]
                                       )]},
    },
    'temp': {},
    'seaice': {},
    'sst': {},
}
reformat_data_cfs_jobs_dict = {
    'pres_lvls': {
        'GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                  'var1_levels': 'P500',
                                  'met_config_overrides': (
                                      "'climo_mean = obs;'"
                                  )},
                          'commands': [sub_util.metplus_command(
                                           'GenEnsProd_fcstCFS_'
                                           +'Days6_10NetCDF.conf'
                                       ),
                                       sub_util.metplus_command(
                                           'GridStat_fcstSUBSEASONAL_'
                                           +'obsGFS_climoERA5_'
                                           +'Days6_10NetCDF.conf'
                                       ),
                                       sub_util.python_command(
                                           'subseasonal_stats_grid2grid'
                                           '_create_days6_10_anomaly.py',
                                           ['HGT_P500',
                                            os.path.join(
                                                '$DATA',
                                                '${VERIF_CASE}_${STEP}',
                                                'METplus_output',
                                                '${RUN}.$DATE',
                                                '$MODEL', '$VERIF_CASE',
                                                'grid_stat_${VERIF_TYPE}_'
                                                +'${job_name}_'
                                                +'{lead?fmt=%2H}0000L_'
                                                +'{valid?fmt=%Y%m%d}_'
                                                +'{valid?fmt=%H}0000V_pairs.nc'
                                            )]
                                       )]},
    },
    'temp': {},
    'seaice': {},
    'sst': {},
}
reformat_data_model_jobs_dict = {
    'temp': {
        'TempAnom2m': {'env': {'var1_name': 'TMP',
                               'var1_levels': 'Z2'},
                       'commands': [sub_util.metplus_command(
                                        'GenEnsProd_fcstSUBSEASONAL_'
                                        +'Days6_10NetCDF.conf'
                                    ),
                                    sub_util.metplus_command(
                                        'GridStat_fcstSUBSEASONAL_'
                                        +'obsECMWF_climoERA5_'
                                        +'Days6_10NetCDF.conf'
                                    ),
                                    sub_util.python_command(
                                        'subseasonal_stats_grid2grid'
                                        '_create_days6_10_anomaly.py',
                                        ['TMP_Z2',
                                         os.path.join(
                                             '$DATA',
                                             '${VERIF_CASE}_${STEP}',
                                             'METplus_output',
                                             '${RUN}.$DATE',
                                             '$MODEL', '$VERIF_CASE',
                                             'grid_stat_${VERIF_TYPE}_'
                                             +'${job_name}_'
                                             +'{lead?fmt=%2H}0000L_'
                                             +'{valid?fmt=%Y%m%d}_'
                                             +'{valid?fmt=%H}0000V_pairs.nc'
                                         )]
                                    )]},
    },
    'pres_lvls': {},
    'seaice': {},
    'sst': {},
}


# Create job scripts
if JOB_GROUP in ['reformat_data', 'assemble_data']:
    if JOB_GROUP == 'reformat_data':
        JOB_GROUP_jobs_dict = reformat_data_model_jobs_dict
    elif JOB_GROUP == 'assemble_data':
        JOB_GROUP_jobs_dict = assemble_data_model_jobs_dict
    for verif_type in VERIF_CASE_STEP_type_list:
        print("----> Making job scripts for "+VERIF_CASE_STEP+" "
              +verif_type+" for job group "+JOB_GROUP)
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +verif_type)
        if verif_type == 'pres_lvls':
            for model_idx in range(len(model_list)):
                model = model_list[model_idx]
                if model == 'gefs':
                    JOB_GROUP_jobs_dict = reformat_data_gefs_jobs_dict
                elif model == 'cfs':
                    JOB_GROUP_jobs_dict = reformat_data_cfs_jobs_dict
        # Read in environment variables for verif_type
        for verif_type_job in list(JOB_GROUP_jobs_dict[verif_type].keys()):
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
            if JOB_GROUP == 'reformat_data':
                if verif_type in ['sst', 'seaice', 'temp', 'pres_lvls']:
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
            job_env_dict['DAYS'] = DAYS
            job_env_dict['CORRECT_INIT_DATE'] = CORRECT_INIT_DATE
            job_env_dict['CORRECT_LEAD_SEQ'] = CORRECT_LEAD_SEQ
            date_dt = valid_start_date_dt
            while date_dt <= valid_end_date_dt:
                sdate_dt = date_dt - datetime.timedelta(days=5)
                job_env_dict['D6_10START'] = sdate_dt.strftime('%Y%m%d')
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
                    # Do file checks
                    all_truth_file_exist = False
                    model_files_exist = False
                    write_job_cmds = False
                    check_model_files = True
                    if check_model_files:
                        (model_files_exist, valid_date_fhr_list,
                         model_copy_output_DATA2COMOUT_list) = (
                            sub_util.check_days6_10_model_files(job_env_dict)
                        )
                        job_env_dict['fhr_list'] = (
                            '"'+','.join(valid_date_fhr_list)+'"'
                        )
                        job_env_dict.pop('fhr_start')
                        job_env_dict.pop('fhr_end')
                        job_env_dict.pop('fhr_inc')
                    if JOB_GROUP == 'reformat_data':
                        if verif_type in ['temp', 'pres_lvls'] \
                                and verif_type_job in ['TempAnom2m',
                                                       'GeoHeightAnom']:
                            check_truth_files = True
                        else:
                            check_truth_files = False
                    elif JOB_GROUP == 'assemble_data':
                        check_truth_files = False
                    if check_truth_files:
                        (all_truth_file_exist,
                         truth_copy_output_DATA2COMOUT_list) = (
                            sub_util.check_days6_10_truth_files(job_env_dict)
                        )
                        if model_files_exist and all_truth_file_exist:
                            write_job_cmds = True
                        else:
                            write_job_cmds = False
                            print("WARNING: Missing > 80% of files")
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
                            job.write('export err=$?; err_chk'+'\n')
                    job.close()
                    job_env_dict.pop('fhr_list')
                    job_env_dict['fhr_start'] = fhr_start
                    job_env_dict['fhr_end'] = fhr_end
                    job_env_dict['fhr_inc'] = fhr_inc
                date_dt = date_dt + datetime.timedelta(hours=valid_date_inc)
        # Do reformat_data and assemble_data observation jobs
        if JOB_GROUP in ['reformat_data', 'assemble_data']:
            if JOB_GROUP == 'reformat_data':
                JOB_GROUP_obs_jobs_dict = reformat_data_obs_jobs_dict
            elif JOB_GROUP == 'assemble_data':
                JOB_GROUP_obs_jobs_dict = assemble_data_obs_jobs_dict
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
                    job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                    job_env_dict['valid_hr_start'] = date_dt.strftime('%H')
                    job_env_dict['valid_hr_end'] = date_dt.strftime('%H')
                    njobs+=1
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

print("END: "+os.path.basename(__file__))
