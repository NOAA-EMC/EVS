#!/usr/bin/env python3
'''
Program Name: mesoscale_precip_stats_create_job_scripts.py
Contact(s): Mallory Row
Abstract: This creates multiple independent job scripts. These
          jobs contain all the necessary environment variables
          and commands to needed to run the specific
          use case.
'''

import sys
import os
import glob
import datetime
import mesoscale_util as m_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
SENDCOM = os.environ['SENDCOM']
COMOUT = os.environ['COMOUT']
COMOUTsmall = os.environ['COMOUTsmall']
COMOUTfinal = os.environ['COMOUTfinal']
FIXevs = os.environ['FIXevs']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
MODELNAME = os.environ['MODELNAME']
JOB_GROUP = os.environ['JOB_GROUP']
evs_run_mode = os.environ['evs_run_mode']
machine = os.environ['machine']
nproc = os.environ['nproc']
USE_CFP = os.environ['USE_CFP']
VDATE = os.environ['VDATE']
VHOUR_LIST = os.environ['VHOUR_LIST'].split(',')
CYC_LIST = os.environ['CYC_LIST'].split(' ')

# Make job group directory
JOB_GROUP_jobs_dir = os.path.join(DATA, 'jobs', JOB_GROUP)
if not os.path.exists(JOB_GROUP_jobs_dir):
    os.makedirs(JOB_GROUP_jobs_dir)

################################################
#### assemble_data jobs
################################################
assemble_data_obs_jobs_dict = {
    'accum24hr': {
        '24hrCCPA': {'env': {'ccpa_file_accum': '6'},
                     'commands': [m_util.metplus_command(
                                      'PcpCombine_obsCCPA.conf'
                                  )]}
    },
    'accum03hr': {
        '03hrCCPA': {'env': {'ccpa_file_accum': '3'},
                     'commands': [m_util.metplus_command(
                                      'PcpCombine_obsCCPA.conf'
                                  )]}
    },
    'accum01hr': {
        '01hrCCPA': {'env': {'ccpa_file_accum': '1'},
                     'commands': [m_util.metplus_command(
                                      'PcpCombine_obsCCPA.conf'
                                  )]}
    }
}
assemble_data_model_jobs_dict = {
    'accum24hr': {
        '24hrAccum_CONUS': {'env': {'area': 'conus'},
                            'commands': [m_util.metplus_command(
                                             'PcpCombine_fcstMESOSCALE_APCP.conf'
                                         )]},
        '24hrAccum_ALASKA': {'env': {'area': 'alaska'},
                              'commands': [m_util.metplus_command(
                                              'PcpCombine_fcstMESOSCALE_APCP.conf'
                                           )]},
        '24hrAccum_HAWAII': {'env': {'area': 'hawaii'},
                             'commands': [m_util.metplus_command(
                                             'PcpCombine_fcstMESOSCALE_APCP.conf'
                                          )]},
        '24hrAccum_PUERTO_RICO': {'env': {'area': 'puerto_rico'},
                                          'commands': [m_util.metplus_command(
                                                           'PcpCombine_''fcstMESOSCALE_APCP.conf'
                                                       )]},
    },
    'accum03hr': {
        '03hrAccum_CONUS': {'env': {'area': 'conus'},
                            'commands': [m_util.metplus_command(
                                             'PcpCombine_fcstMESOSCALE_APCP.conf'
                                         )]},
        '03hrAccum_ALASKA': {'env': {'area': 'alaska'},
                             'commands': [m_util.metplus_command(
                                              'PcpCombine_fcstMESOSCALE_APCP.conf'
                                          )]},
    },
    'accum01hr': {
        '01hrAccum_CONUS': {'env': {'area': 'conus'},
                            'commands': [m_util.metplus_command(
                                             'PcpCombine_fcstMESOSCALE_APCP.conf'
                                         )]},
        '01hrAccum_ALASKA': {'env': {'area': 'alaska'},
                             'commands': [m_util.metplus_command(
                                              'PcpCombine_fcstMESOSCALE_APCP.conf'
                                          )]},
    }
}
################################################
#### generate_stats jobs
################################################
generate_stats_jobs_dict = {
    'accum24hr': {
        '24hrAccum_CONUS_CTC': {'env': {'area': 'conus',
                                        'grid': os.environ['CONUS_CTC_GRID'],
                                        'obs': os.environ['CONUS_VERIF_SOURCE'],
                                        'nbhrd_list': '1',
                                        'mask_list': (f"{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS_East.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS_West.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS_Central.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +'_CONUS_South.nc'),
                                        'CTC_STAT_FLAG': 'STAT',
                                        'NBRCNT_STAT_FLAG': 'NONE'},
                                'commands': [m_util.metplus_command(
                                             'GridStat_fcstMESOSCALE_obs'
                                             +os.environ['CONUS_VERIF_SOURCE'].upper()
                                             +'.conf'
                                         )]},
        '24hrAccum_CONUS_NBRCNT': {'env': {'area': 'conus',
                                           'grid': os.environ['CONUS_NBRCNT_GRID'],
                                           'obs': os.environ['CONUS_VERIF_SOURCE'],
                                           'nbhrd_list': os.environ['NBRHD_WIDTHS'],
                                           'mask_list': (f"{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS.nc,{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS_East.nc,{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS_West.nc,{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS_Central.nc, {FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +'_CONUS_South.nc'),
                                           'CTC_STAT_FLAG': 'NONE',
                                           'NBRCNT_STAT_FLAG': 'STAT'},
                                   'commands': [m_util.metplus_command(
                                                    'GridStat_fcstMESOSCALE_obs'
                                                    +os.environ['CONUS_VERIF_SOURCE'].upper()
                                                    +'.conf'
                                                )]},
        '24hrAccum_ALASKA_CTC': {'env': {'area': 'alaska',
                                         'grid': os.environ['ALASKA_CTC_GRID'],
                                         'obs': os.environ['ALASKA_VERIF_SOURCE'],
                                         'nbhrd_list': '1',
                                         'mask_list': (f"{FIXevs}/masks/Alaska_"
                                                       +f"{os.environ['ALASKA_CTC_GRID']}"
                                                       +'.nc'),
                                         'CTC_STAT_FLAG': 'STAT',
                                         'NBRCNT_STAT_FLAG': 'NONE'},
                                 'commands': [m_util.metplus_command(
                                                 'GridStat_fcstMESOSCALE_obs'
                                                 +os.environ['ALASKA_VERIF_SOURCE'].upper()
                                                 +'.conf'
                                              )]},
        '24hrAccum_ALASKA_NBRCNT': {'env': {'area': 'alaska',
                                            'grid': os.environ['ALASKA_NBRCNT_GRID'],
                                            'obs': os.environ['ALASKA_VERIF_SOURCE'],
                                            'nbhrd_list': os.environ['NBRHD_WIDTHS'],
                                            'CTC_STAT_FLAG': 'NONE',
                                            'mask_list': (f"{FIXevs}/masks/Alaska_"
                                                          +f"{os.environ['ALASKA_NBRCNT_GRID']}"
                                                          +'.nc'),
                                            'NBRCNT_STAT_FLAG': 'STAT'},
                                    'commands': [m_util.metplus_command(
                                                     'GridStat_fcstMESOSCALE_obs'
                                                      +os.environ['ALASKA_VERIF_SOURCE'].upper()
                                                      +'.conf'
                                                 )]},
    },
    'accum03hr': {
        '03hrAccum_CONUS_CTC': {'env': {'area': 'conus',
                                        'grid': os.environ['CONUS_CTC_GRID'],
                                        'obs': os.environ['CONUS_VERIF_SOURCE'],
                                        'nbhrd_list': '1',
                                        'mask_list': (f"{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS_East.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS_West.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS_Central.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +'_CONUS_South.nc'),
                                        'CTC_STAT_FLAG': 'STAT',
                                        'NBRCNT_STAT_FLAG': 'NONE'},
                                'commands': [m_util.metplus_command(
                                             'GridStat_fcstMESOSCALE_obs'
                                             +os.environ['CONUS_VERIF_SOURCE'].upper()
                                             +'.conf'
                                         )]},
        '03hrAccum_CONUS_NBRCNT': {'env': {'area': 'conus',
                                           'grid': os.environ['CONUS_NBRCNT_GRID'],
                                           'obs': os.environ['CONUS_VERIF_SOURCE'],
                                           'nbhrd_list': os.environ['NBRHD_WIDTHS'],
                                           'mask_list': (f"{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS.nc,{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS_East.nc,{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS_West.nc,{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS_Central.nc,{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +'_CONUS_South.nc'),
                                           'CTC_STAT_FLAG': 'NONE',
                                           'NBRCNT_STAT_FLAG': 'STAT'},
                                'commands': [m_util.metplus_command(
                                                 'GridStat_fcstMESOSCALE_obs'
                                                 +os.environ['CONUS_VERIF_SOURCE'].upper()
                                                 +'.conf'
                                             )]},
        '03hrAccum_ALASKA_CTC': {'env': {'area': 'alaska',
                                         'grid': os.environ['ALASKA_CTC_GRID'],
                                         'obs': os.environ['ALASKA_VERIF_SOURCE'],
                                         'nbhrd_list': '1',
                                         'mask_list': (f"{FIXevs}/masks/Alaska_"
                                                       +f"{os.environ['ALASKA_CTC_GRID']}"
                                                       +'.nc'),
                                         'CTC_STAT_FLAG': 'STAT',
                                         'NBRCNT_STAT_FLAG': 'NONE'},
                                 'commands': [m_util.metplus_command(
                                                 'GridStat_fcstMESOSCALE_obs'
                                                 +os.environ['ALASKA_VERIF_SOURCE'].upper()
                                                 +'.conf'
                                              )]},
        '03hrAccum_ALASKA_NBRCNT': {'env': {'area': 'alaska',
                                            'grid': os.environ['ALASKA_NBRCNT_GRID'],
                                            'obs': os.environ['ALASKA_VERIF_SOURCE'],
                                            'nbhrd_list': os.environ['NBRHD_WIDTHS'],
                                            'mask_list': (f"{FIXevs}/masks/Alaska_"
                                                          +f"{os.environ['ALASKA_NBRCNT_GRID']}"
                                                          +'.nc'),
                                            'CTC_STAT_FLAG': 'NONE',
                                            'NBRCNT_STAT_FLAG': 'STAT'},
                                    'commands': [m_util.metplus_command(
                                                     'GridStat_fcstMESOSCALE_obs'
                                                      +os.environ['ALASKA_VERIF_SOURCE'].upper()
                                                      +'.conf'
                                                 )]},
    },
    'accum01hr': {
        '01hrAccum_CONUS_CTC': {'env': {'area': 'conus',
                                        'grid': os.environ['CONUS_CTC_GRID'],
                                        'obs': os.environ['CONUS_VERIF_SOURCE'],
                                        'nbhrd_list': '1',
                                        'mask_list': (f"{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS_East.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS_West.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +f"_CONUS_Central.nc,{FIXevs}/masks/Bukovsky_"
                                                      +f"{os.environ['CONUS_CTC_GRID']}"
                                                      +'_CONUS_South.nc'),
                                        'CTC_STAT_FLAG': 'STAT',
                                        'NBRCNT_STAT_FLAG': 'NONE'},
                                'commands': [m_util.metplus_command(
                                             'GridStat_fcstMESOSCALE_obs'
                                             +os.environ['CONUS_VERIF_SOURCE'].upper()
                                             +'.conf'
                                         )]},
        '01hrAccum_CONUS_NBRCNT': {'env': {'area': 'conus',
                                           'grid': os.environ['CONUS_NBRCNT_GRID'],
                                           'obs': os.environ['CONUS_VERIF_SOURCE'],
                                           'nbhrd_list': os.environ['NBRHD_WIDTHS'],
                                           'mask_list': (f"{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS.nc,{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS_East.nc,{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS_West.nc,{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +f"_CONUS_Central.nc,{FIXevs}/masks/Bukovsky_"
                                                         +f"{os.environ['CONUS_NBRCNT_GRID']}"
                                                         +'_CONUS_South.nc'),
                                           'CTC_STAT_FLAG': 'NONE',
                                           'NBRCNT_STAT_FLAG': 'STAT'},
                                'commands': [m_util.metplus_command(
                                                 'GridStat_fcstMESOSCALE_obs'
                                                 +os.environ['CONUS_VERIF_SOURCE'].upper()
                                                 +'.conf'
                                             )]},
        '01hrAccum_ALASKA_CTC': {'env': {'area': 'alaska',
                                         'grid': os.environ['ALASKA_CTC_GRID'],
                                         'obs': os.environ['ALASKA_VERIF_SOURCE'],
                                         'nbhrd_list': '1',
                                         'mask_list': (f"{FIXevs}/masks/Alaska_"
                                                       +f"{os.environ['ALASKA_CTC_GRID']}"
                                                       +'.nc'),
                                         'CTC_STAT_FLAG': 'STAT',
                                         'NBRCNT_STAT_FLAG': 'NONE'},
                                 'commands': [m_util.metplus_command(
                                                 'GridStat_fcstMESOSCALE_obs'
                                                 +os.environ['ALASKA_VERIF_SOURCE'].upper()
                                                 +'.conf'
                                              )]},
        '01hrAccum_ALASKA_NBRCNT': {'env': {'area': 'alaska',
                                            'grid': os.environ['ALASKA_NBRCNT_GRID'],
                                            'obs': os.environ['ALASKA_VERIF_SOURCE'],
                                            'nbhrd_list': os.environ['NBRHD_WIDTHS'],
                                            'mask_list': (f"{FIXevs}/masks/Alaska_"
                                                          +f"{os.environ['ALASKA_NBRCNT_GRID']}"
                                                          +'.nc'),
                                            'CTC_STAT_FLAG': 'NONE',
                                            'NBRCNT_STAT_FLAG': 'STAT'},
                                    'commands': [m_util.metplus_command(
                                                     'GridStat_fcstMESOSCALE_obs'
                                                      +os.environ['ALASKA_VERIF_SOURCE'].upper()
                                                      +'.conf'
                                                 )]},
    },
}

################################################
#### gather_stats jobs
################################################
gather_stats_jobs_dict = {'env': {},
                          'commands': [m_util.metplus_command(
                              'StatAnalysis_fcstMESOSCALE.conf'
                          )]}

# Write jobs
njob = 0
if JOB_GROUP == 'assemble_data':
    for VHOUR in VHOUR_LIST:
        accum_list = ['01']
        if int(VHOUR) % 3 == 0:
            accum_list.append('03')
        if int(VHOUR) == 12:
            accum_list.append('24')
        # Loop through and write job script for dates
        for accum in accum_list:
            print(f"----> Making job scripts for {VERIF_CASE} {STEP} "
                  +f"accum{accum}hr for job group {JOB_GROUP}")
            JOB_GROUP_accum_obs_jobs_dict = (
                assemble_data_obs_jobs_dict[f"accum{accum}hr"]
            )
            JOB_GROUP_accum_model_jobs_dict = (
                assemble_data_model_jobs_dict[f"accum{accum}hr"]
            )
            valid_start_date_dt = datetime.datetime.strptime(
                VDATE+VHOUR.zfill(2), '%Y%m%d%H'
            )
            valid_end_date_dt = datetime.datetime.strptime(
                VDATE+VHOUR.zfill(2), '%Y%m%d%H'
            )
            valid_date_inc = 24
            fhrs = range(
                int(os.environ[f"ACCUM{accum}_FHR_START"]),
                (int(os.environ[f"ACCUM{accum}_FHR_END"])
                 +int(os.environ[f"ACCUM{accum}_FHR_INCR"])),
                int(os.environ[f"ACCUM{accum}_FHR_INCR"])
            )
            date_dt = valid_start_date_dt
            while date_dt <= valid_end_date_dt:
                # Write model jobs
                job_env_dict = m_util.initalize_job_env_dict()
                job_env_dict['valid_hour_start'] = date_dt.strftime('%H')
                job_env_dict['valid_hour_end'] = date_dt.strftime('%H')
                job_env_dict['valid_hour_inc'] = '24'
                job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                job_env_dict['accum'] = accum
                for accum_job in list(JOB_GROUP_accum_model_jobs_dict.keys()):
                    job_env_dict['job_name'] = accum_job
                    for env_var in list(JOB_GROUP_accum_model_jobs_dict\
                                        [accum_job]['env'].keys()):
                        job_env_dict[env_var] = (JOB_GROUP_accum_model_jobs_dict\
                                                 [accum_job]['env'][env_var])
                    for fhr in fhrs:
                        init_dt = date_dt - datetime.timedelta(hours=fhr)
                        if f"{init_dt:%H}" in CYC_LIST:
                            job_env_dict['fcst_hour'] = str(fhr).zfill(2)
                            if MODELNAME == 'rap' \
                                    and f"{init_dt:%H}" not in ['03','09', 
                                                                '15','21'] \
                                    and fhr > 21:
                                continue
                            if MODELNAME == 'nam':
                                if f"{init_dt:%H}" in ['06', '18']:
                                    bucket_intvl = 3
                                elif f"{init_dt:%H}" in ['00', '12']:
                                    bucket_intvl = 12
                                if accum == '01' and \
                                        fhr % bucket_intvl != 1:
                                    pcp_combine_method = 'SUBTRACT'
                                else:
                                    pcp_combine_method = 'SUM'
                                if pcp_combine_method == 'SUM':
                                    if accum == '01':
                                        input_accum = '01'
                                        input_level = 'A1'
                                    elif job_env_dict['area'] \
                                            in ['hawaii', 'puerto_rico'] \
                                            and f"{init_dt:%H}" in ['00', '12']:
                                        input_accum = '12'
                                        input_level = 'A12'
                                    else:
                                        input_accum = '03'
                                        input_level = 'A3'
                                if pcp_combine_method == 'SUBTRACT':
                                    accum_in_fhr_file = fhr % bucket_intvl
                                    if accum_in_fhr_file == 0:
                                        accum_in_fhr_file = bucket_intvl
                                    shift_sec = (fhr - accum_in_fhr_file)*3600
                                    input_accum = (
                                        'A{lead?fmt=%H?shift=-'+str(shift_sec)
                                        +'}'
                                    )
                                    input_level = input_accum
                            else: # assuming continuous buckets
                                bucket_intvl = (
                                    job_env_dict['fcst_hour'].zfill(1)
                                )
                                pcp_combine_method = 'SUBTRACT'
                                input_accum = 'A{lead?fmt=%H}'
                                input_level = input_accum
                            job_env_dict['pcp_combine_method'] = (
                                pcp_combine_method
                            )
                            job_env_dict['input_accum'] = input_accum
                            job_env_dict['input_level'] = input_level
                            job_env_dict['bucket_intvl'] = (
                                str(bucket_intvl)+'H'
                            )
                            # Check for expected job input and output files
                            (job_all_model_input_file_exist,
                             job_model_input_files_list,
                             job_all_model_COMOUT_file_exist,
                             job_model_COMOUT_files_list,
                             job_model_DATA_files_list) = (
                                 m_util.precip_check_model_input_output_files(
                                       job_env_dict
                                 )
                            )
                            # Create job file
                            njob+=1
                            job_env_dict['job_id'] = 'job'+str(njob)
                            job_file = os.path.join(JOB_GROUP_jobs_dir,
                                                    'job'+str(njob))
                            print("Creating job script: "+job_file)
                            job = open(job_file, 'w')
                            job.write('#!/bin/bash\n')
                            job.write('set -x\n')
                            job.write('\n')
                            # Write environment variables
                            for name, value in job_env_dict.items():
                                job.write(f"export {name}='{value}'\n")
                            job.write('\n')
                            # Write job commands
                            if not job_all_model_COMOUT_file_exist:
                                if job_all_model_input_file_exist:
                                    for cmd in (JOB_GROUP_accum_model_jobs_dict\
                                                [accum_job]['commands']):
                                        job.write(cmd+'\n')
                                    if SENDCOM == 'YES':
                                        for job_model_COMOUT_file \
                                                in job_model_COMOUT_files_list:
                                            job.write(
                                                'cp -v '
                                                +job_model_DATA_files_list[
                                                    job_model_COMOUT_files_list.index(
                                                        job_model_COMOUT_file
                                                    )
                                                ]+' '+job_model_COMOUT_file+'\n'
                                            )
                                else:
                                    for job_model_input_file in job_model_input_files_list:
                                        if not m_util.check_file(job_model_input_file):
                                            print("NOTE: MISSING or ZERO SIZE input "
                                                  +f"file for job {job_file}: "
                                                  +f"{job_model_input_file}")
                            job.close()
                # Write observation jobs
                job_env_dict = m_util.initalize_job_env_dict()
                job_env_dict['valid_hour_start'] = date_dt.strftime('%H')
                job_env_dict['valid_hour_end'] = date_dt.strftime('%H')
                job_env_dict['valid_hour_inc'] = '24'
                job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                job_env_dict['accum'] = accum
                for accum_job in list(JOB_GROUP_accum_obs_jobs_dict.keys()):
                    job_env_dict['job_name'] = accum_job
                    for env_var in list(JOB_GROUP_accum_obs_jobs_dict\
                                        [accum_job]['env'].keys()):
                        job_env_dict[env_var] = (JOB_GROUP_accum_obs_jobs_dict\
                                                 [accum_job]['env'][env_var])
                    # Check for expected job input and output files
                    (job_all_obs_input_file_exist,
                     job_obs_input_files_list,
                     job_all_obs_COMOUT_file_exist,
                     job_obs_COMOUT_files_list,
                     job_obs_DATA_files_list) = (
                        m_util.precip_check_obs_input_output_files(
                            job_env_dict
                        )
                    )
                    # Create job file
                    njob+=1
                    job_env_dict['job_id'] = 'job'+str(njob)
                    job_file = os.path.join(JOB_GROUP_jobs_dir,
                                            'job'+str(njob))
                    print("Creating job script: "+job_file)
                    job = open(job_file, 'w')
                    job.write('#!/bin/bash\n')
                    job.write('set -x\n')
                    job.write('\n')
                    # Write environment variables
                    for name, value in job_env_dict.items():
                        job.write(f"export {name}='{value}'\n")
                    job.write('\n')
                    # Write job commands
                    if not job_all_obs_COMOUT_file_exist:
                        if job_all_obs_input_file_exist:
                            for cmd in (JOB_GROUP_accum_obs_jobs_dict\
                                        [accum_job]['commands']):
                                job.write(cmd+'\n')
                            if SENDCOM == 'YES':
                                for job_obs_COMOUT_file in job_obs_COMOUT_files_list:
                                    job.write(
                                        'cp -v '
                                         +job_obs_DATA_files_list[
                                              job_obs_COMOUT_files_list.index(
                                                  job_obs_COMOUT_file
                                              )
                                         ]+' '+job_obs_COMOUT_file+'\n'
                                    )
                        else:
                            for job_obs_input_file in job_obs_input_files_list:
                                if not m_util.check_file(job_obs_input_file):
                                    print("NOTE: MISSING or ZERO SIZE input file for"
                                          f" job {job_file}: {job_obs_input_file}")
                    job.close()
                date_dt = date_dt + datetime.timedelta(hours=valid_date_inc)
elif JOB_GROUP == 'generate_stats':
    for VHOUR in VHOUR_LIST:
        accum_list = ['01']
        if int(VHOUR) % 3 == 0:
            accum_list.append('03')
        if int(VHOUR) == 12:
            accum_list.append('24')
        # Loop through and write job script for dates
        for accum in accum_list:
            print(f"----> Making job scripts for {VERIF_CASE} {STEP} "
                  +f"accum{accum}hr for job group {JOB_GROUP}")
            JOB_GROUP_accum_jobs_dict = (
                generate_stats_jobs_dict[f"accum{accum}hr"]
            )
            valid_start_date_dt = datetime.datetime.strptime(
                VDATE+VHOUR.zfill(2), '%Y%m%d%H'
            )
            valid_end_date_dt = datetime.datetime.strptime(
                VDATE+VHOUR.zfill(2), '%Y%m%d%H'
            )
            valid_date_inc = 24
            fhrs = range(
                int(os.environ[f"ACCUM{accum}_FHR_START"]),
                (int(os.environ[f"ACCUM{accum}_FHR_END"])
                 +int(os.environ[f"ACCUM{accum}_FHR_INCR"])),
                int(os.environ[f"ACCUM{accum}_FHR_INCR"])
            )
            date_dt = valid_start_date_dt
            while date_dt <= valid_end_date_dt:
                # Write jobs
                job_env_dict = m_util.initalize_job_env_dict()
                job_env_dict['valid_hour_start'] = date_dt.strftime('%H')
                job_env_dict['valid_hour_end'] = date_dt.strftime('%H')
                job_env_dict['valid_hour_inc'] = '24'
                job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                job_env_dict['accum'] = accum
                job_env_dict['thresh_list'] = os.environ[f"ACCUM{accum}_THRESH"]
                for accum_job in list(JOB_GROUP_accum_jobs_dict.keys()):
                    job_env_dict['job_name'] = accum_job
                    for env_var in list(JOB_GROUP_accum_jobs_dict\
                                        [accum_job]['env'].keys()):
                        job_env_dict[env_var] = (JOB_GROUP_accum_jobs_dict\
                                                 [accum_job]['env'][env_var])
                    job_env_dict['OBS'] = job_env_dict['obs'].upper()
                    for fhr in fhrs:
                        init_dt = date_dt - datetime.timedelta(hours=fhr)
                        if f"{init_dt:%H}" in CYC_LIST:
                            job_env_dict['fcst_hour'] = str(fhr).zfill(2)
                            if MODELNAME == 'rap' \
                                    and f"{init_dt:%H}" not in ['03','09',
                                                                '15','21'] \
                                    and fhr > 21:
                                continue
                            # Check for expected job input and output files
                            (job_all_obs_input_file_exist,
                             job_obs_input_files_list,
                             job_all_obs_COMOUT_file_exist,
                             job_obs_COMOUT_files_list,
                             job_obs_DATA_files_list) = (
                                 m_util.precip_check_obs_input_output_files(
                                       job_env_dict
                                 )
                            )
                            (job_all_model_input_file_exist,
                             job_model_input_files_list,
                             job_all_model_COMOUT_file_exist,
                             job_model_COMOUT_files_list,
                             job_model_DATA_files_list) = (
                                 m_util.precip_check_model_input_output_files(
                                       job_env_dict
                                 )
                            )
                            # Create job file
                            njob+=1
                            job_env_dict['job_id'] = 'job'+str(njob)
                            job_file = os.path.join(JOB_GROUP_jobs_dir,
                                                    'job'+str(njob))
                            print("Creating job script: "+job_file)
                            job = open(job_file, 'w')
                            job.write('#!/bin/bash\n')
                            job.write('set -x\n')
                            job.write('\n')
                            # Write environment variables
                            for name, value in job_env_dict.items():
                                job.write(f"export {name}='{value}'\n")
                            job.write('\n')
                            # Write job commands
                            if not job_all_model_COMOUT_file_exist:
                                if job_all_obs_input_file_exist \
                                        and job_all_model_input_file_exist:
                                    for cmd in (JOB_GROUP_accum_jobs_dict\
                                                [accum_job]['commands']):
                                        job.write(cmd+'\n')
                                    if SENDCOM == 'YES':
                                        for job_model_COMOUT_file \
                                                in job_model_COMOUT_files_list:
                                            job.write(
                                                'cp -v '
                                                +job_model_DATA_files_list[
                                                    job_model_COMOUT_files_list.index(
                                                        job_model_COMOUT_file
                                                    )
                                                ]+' '+job_model_COMOUT_file+'\n'
                                            )
                                else:
                                    for job_obs_input_file in job_obs_input_files_list:
                                        if not m_util.check_file(job_obs_input_file):
                                            print("NOTE: MISSING or ZERO SIZE input file for"
                                                  f" job {job_file}: {job_obs_input_file}")
                                    for job_model_input_file in job_model_input_files_list:
                                        if not m_util.check_file(job_model_input_file):
                                            print("NOTE: MISSING or ZERO SIZE input file for"
                                                  f" job {job_file}: {job_model_input_file}")
                            job.close()
                date_dt = date_dt + datetime.timedelta(hours=valid_date_inc)
elif JOB_GROUP == 'gather_stats':
    # Loop through and write job script for dates
    print(f"----> Making job scripts for {VERIF_CASE} {STEP} "
          +f"for job group {JOB_GROUP}")
    valid_start_date_dt = datetime.datetime.strptime(VDATE, '%Y%m%d')
    valid_end_date_dt = datetime.datetime.strptime(VDATE, '%Y%m%d')
    valid_date_inc = 24
    date_dt = valid_start_date_dt
    while date_dt <= valid_end_date_dt:
        # Write jobs
        job_env_dict = m_util.initalize_job_env_dict()
        job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
        # Create job file
        njob+=1
        job_env_dict['job_id'] = 'job'+str(njob)
        job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njob))
        print("Creating job script: "+job_file)
        job = open(job_file, 'w')
        job.write('#!/bin/bash\n')
        job.write('set -x\n')
        job.write('\n')
        # Write environment variables
        for name, value in job_env_dict.items():
            job.write(f"export {name}='{value}'\n")
        job.write('\n')
        # Check files exist
        check_DATE_stat_dir = os.path.join(
            COMOUT, f"{RUN}.{date_dt:%Y%m%d}", MODELNAME, VERIF_CASE
        )
        if len(glob.glob(check_DATE_stat_dir+'/*.stat')) != 0:
            write_job_cmds = True
        else:
            write_job_cmds = False
            print(f"WARNING: No files matching {check_DATE_stat_dir}/*.stat")
        # Write job commands
        if write_job_cmds:
            for cmd in gather_stats_jobs_dict['commands']:
                job.write(cmd+'\n')
        job.close()
        date_dt = date_dt + datetime.timedelta(hours=valid_date_inc)

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(DATA, 'jobs', JOB_GROUP, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("WARNING: No job files created in "
              +os.path.join(os.path.join(DATA, 'jobs', JOB_GROUP, 'job*')))
    poe_files = glob.glob(os.path.join(DATA, 'jobs', JOB_GROUP, 'poe*'))
    npoe_files = len(poe_files)
    if npoe_files > 0:
        for poe_file in poe_files:
            os.remove(poe_file)
    njob, iproc, node = 1, 0, 1
    while njob <= njob_files:
        job = 'job'+str(njob)
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            if iproc >= int(nproc):
                iproc = 0
                node+=1
        poe_filename = os.path.join(DATA, 'jobs', JOB_GROUP,
                                    'poe_jobs'+str(node))
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
               str(iproc-1)+' '
               +os.path.join(DATA, 'jobs', JOB_GROUP, job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(DATA, 'jobs', JOB_GROUP, job)+'\n'
            )
        poe_file.close()
        njob+=1
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(DATA, 'jobs', JOB_GROUP,
                                'poe_jobs'+str(node))
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
