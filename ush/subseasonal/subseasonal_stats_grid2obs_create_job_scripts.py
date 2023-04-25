'''
Program Name: subseasonal_stats_grid2obs_create_job_scripts.py
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
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
METPLUS_PATH = os.environ['METPLUS_PATH']
MET_ROOT = os.environ['MET_ROOT']
MET_bin_exec = os.environ['MET_bin_exec']
PARMevs = os.environ['PARMevs']
model_list = os.environ['model_list'].split(' ')

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
                                'obs_bufr_var_list': ("'TOB'")},
                        'commands': [sub_util.metplus_command(
                                         'PB2NC_obsPrepbufr.conf'
                                     )]},
    }
}
reformat_data_model_jobs_dict = {
    'PrepBufr': {}
}

################################################
#### assemble_data jobs
################################################
assemble_data_obs_jobs_dict = {
    'PrepBufr': {}
}
assemble_data_model_jobs_dict = {
    'PrepBufr': {
        'TempAnom2m': {'env': {'prepbufr': 'nam',
                               'obs_window': '900',
                               'msg_type': 'ADPSFC',
                               'var1_fcst_name': 'TMP',
                               'var1_fcst_levels': 'Z2',
                               'var1_fcst_options': '',
                               'var1_obs_name': 'TMP',
                               'var1_obs_levels': 'Z2',
                               'var1_obs_options': '',
                               'met_config_overrides': ("'climo_mean "
                                                        +"= fcst;'")},
                       'commands': [sub_util.metplus_command(
                                        'PointStat_fcstSUBSEASONAL_'
                                        +'obsPrepbufr_climoERA5_'
                                        +'MPR.conf'
                                    ),
                                    sub_util.python_command(
                                        'subseasonal_stats_'
                                        'grid2obs_create_anomaly.py',
                                        ['TMP_Z2',
                                         os.path.join(
                                             '$DATA',
                                             '${VERIF_CASE}_${STEP}',
                                             'METplus_output',
                                             '${RUN}.'
                                             +'{valid?fmt=%Y%m%d}',
                                             '$MODEL', '$VERIF_CASE',
                                             'point_stat_'
                                             +'${VERIF_TYPE}_'
                                             +'${job_name}_'
                                             +'{lead?fmt=%2H}0000L_'
                                             +'{valid?fmt=%Y%m%d}_'
                                             +'{valid?fmt=%H}0000V'
                                             +'.stat'
                                         )]
                                    )]},
    }
}

################################################
#### generate_stats jobs
################################################
generate_stats_jobs_dict = {
    'PrepBufr': {
        'WeeklyAvg_TempAnom2m': {'env': {'prepbufr': 'nam',
                                         'obs_window': '900',
                                         'msg_type': 'ADPSFC',
                                         'var1_fcst_name': 'TMP',
                                         'var1_fcst_levels': 'Z2',
                                         'var1_fcst_options': '',
                                         'var1_obs_name': 'TMP',
                                         'var1_obs_levels': 'Z2',
                                         'var1_obs_options': '',
                                         'met_config_overrides': ("'climo_mean "
                                                                  +"= fcst;'")},
                                 'commands': [sub_util.python_command(
                                                 'subseasonal_stats_'
                                                 'grid2obs_create_weekly_avg.py',
                                                 ['TMP_ANOM_Z2',
                                                   os.path.join(
                                                       '$DATA',
                                                       '${VERIF_CASE}_${STEP}',
                                                       'METplus_output',
                                                       '${RUN}.'
                                                       +'{valid?fmt=%Y%m%d}',
                                                       '$MODEL', '$VERIF_CASE',
                                                       'anomaly_${VERIF_TYPE}_'
                                                       +'TempAnom2m_init'
                                                       +'{init?fmt=%Y%m%d%H}_'
                                                       +'fhr{lead?fmt=%3H}.stat'
                                                 ),
                                                 os.path.join(
                                                    '$COMIN', 'stats',
                                                    '$COMPONENT',
                                                    '${RUN}.{valid?fmt=%Y%m%d}',
                                                    '$MODEL', '$VERIF_CASE',
                                                    'anomaly_${VERIF_TYPE}_'
                                                    +'TempAnom2m_init'
                                                    +'{init?fmt=%Y%m%d%H}_'
                                                    +'fhr{lead?fmt=%3H}.stat'
                                                )]
                                            ),
                                            'nweekly_avg_stat_files='
                                            +'$(ls '+os.path.join(
                                                '$DATA',
                                                '${VERIF_CASE}_${STEP}',
                                                'METplus_output',
                                                '${RUN}.${DATE}',
                                                '$MODEL', '$VERIF_CASE',
                                                'weekly_avg_*.stat'
                                            )+'|wc -l)',
                                            ('if [ $nweekly_avg_stat_files '
                                            +'-ne 0 ]; then'),
                                            sub_util.metplus_command(
                                                'StatAnalysis_'
                                                +'fcstSUBSEASONAL_'
                                                +'obsPrepbufr_MPRtoSL1L2.conf'
                                            ),
                                            'fi']},
        'Temp2m': {'env': {'prepbufr': 'nam',
                           'obs_window': '900',
                           'msg_type': 'ADPSFC',
                           'var1_fcst_name': 'TMP',
                           'var1_fcst_levels': 'Z2',
                           'var1_fcst_options': '',
                           'var1_obs_name': 'TMP',
                           'var1_obs_levels': 'Z2',
                           'var1_obs_options': '',
                           'met_config_overrides': ''},
                   'commands': [sub_util.metplus_command(
                                    'PointStat_fcstSUBSEASONAL_'
                                    +'obsPrepbufr.conf'
                                )]},
    }
}

################################################
#### gather_stats jobs
################################################
gather_stats_jobs_dict = {'env': {},
                          'commands': [sub_util.metplus_command(
                                           'StatAnalysis_fcstSUBSEASONAL.conf'
                                       )]}

# Create job scripts
if JOB_GROUP in ['reformat_data', 'assemble_data', 'generate_stats']:
    if JOB_GROUP == 'reformat_data':
        JOB_GROUP_jobs_dict = reformat_data_model_jobs_dict
    if JOB_GROUP == 'assemble_data':
        JOB_GROUP_jobs_dict = assemble_data_model_jobs_dict
    elif JOB_GROUP == 'generate_stats':
        JOB_GROUP_jobs_dict = generate_stats_jobs_dict
    for verif_type in VERIF_CASE_STEP_type_list:
        print("----> Making job scripts for "+VERIF_CASE_STEP+" "
              +verif_type+" for job group "+JOB_GROUP)
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +verif_type)
        # Read in environment variables for verif_type
        for verif_type_job in list(JOB_GROUP_jobs_dict[verif_type].keys()):
            # Initialize job environment dictionary
            job_env_dict = gda_util.initalize_job_env_dict(
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
                if verif_type == 'sfc' \
                        and verif_type_job == 'TempAnom2m':
                    if int(job_env_dict['valid_hr_start']) - 12 > 0:
                        job_env_dict['valid_hr_start'] = str(
                            int(job_env_dict['valid_hr_start']) - 12
                        )
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
                job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                job_env_dict['valid_hr_start'] = date_dt.strftime('%H')
                job_env_dict['valid_hr_end'] = date_dt.strftime('%H')
                for model_idx in range(len(model_list)):
                    job_env_dict['MODEL'] = model_list[model_idx]
                    njobs+=1
                    # Create job file
                    job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
                    print("Creating job script: "+job_file)
                    job = open(job_file, 'w')
                    job.write('#!/bin/bash\n')
                    job.write('set -x\n')
                    job.write('\n')
                    # Set any environment variables for special cases
                    if JOB_GROUP in ['assemble_data', 'generate_stats']:
                        if verif_type == 'pres_levs':
                            job_env_dict['grid'] = 'G004'
                            mask_list = [
                                'G004_GLOBAL', 'G004_NHEM', 'G004_SHEM',
                                'G004_TROPICS', 'Bukovsky_G004_CONUS',
                                'Alaska_G004'
                            ]
                        elif verif_type in ['sfc', 'ptype']:
                            job_env_dict['grid'] = 'G104'
                            mask_list = [
                                'Bukovsky_G104_CONUS', 'Bukovsky_G104_CONUS_East',
                                'Bukovsky_G104_CONUS_West',
                                'Bukovsky_G104_CONUS_South',
                                'Bukovsky_G104_CONUS_Central',
                                'Bukovsky_G104_Appalachia',
                                'Bukovsky_G104_CPlains',
                                'Bukovsky_G104_DeepSouth',
                                'Bukovsky_G104_GreatBasin',
                                'Bukovsky_G104_GreatLakes',
                                'Bukovsky_G104_Mezquital',
                                'Bukovsky_G104_MidAtlantic',
                                'Bukovsky_G104_NorthAtlantic',
                                'Bukovsky_G104_NPlains',
                                'Bukovsky_G104_NRockies',
                                'Bukovsky_G104_PacificNW',
                                'Bukovsky_G104_PacificSW',
                                'Bukovsky_G104_Prairie',
                                'Bukovsky_G104_Southeast',
                                'Bukovsky_G104_Southwest',
                                'Bukovsky_G104_SPlains',
                                'Bukovsky_G104_SRockies',
                                'Alaska_G104'
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
                    if JOB_GROUP == 'generate_stats':
                        if verif_type_job == 'DailyAvg_TempAnom2m':
                            if int(job_env_dict['fhr_inc']) < 24:
                                job_env_dict['fhr_inc'] = '24'
                    # Do file checks
                    check_model_files = True
                    if check_model_files:
                        model_files_exist, valid_date_fhr_list = (
                            gda_util.check_model_files(job_env_dict)
                        )
                        job_env_dict['fhr_list'] = (
                            '"'+','.join(valid_date_fhr_list)+'"'
                        )
                        job_env_dict.pop('fhr_start')
                        job_env_dict.pop('fhr_end')
                        job_env_dict.pop('fhr_inc')
                    if JOB_GROUP == 'assemble_data':
                        check_truth_files = False
                    elif JOB_GROUP in ['reformat_data', 'generate_stats']:
                        if verif_type == 'ptype' \
                                and JOB_GROUP == 'reformat_data':
                            check_truth_files = False
                        else: 
                            check_truth_files = True
                    if check_truth_files:
                        all_truth_file_exist = gda_util.check_truth_files(
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
                     # Check job and model being run
                    if job_env_dict['MODEL'] \
                            in ['cmc', 'ecmwf', 'fnmoc',
                                'imd', 'jma', 'ukmet'] \
                            and verif_type_job == 'SpefHum':
                        write_job_cmds = False
                    elif job_env_dict['MODEL'] \
                            in ['jma'] \
                            and verif_type_job == 'RelHum':
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
        # Do reformat_data and assemble_data observation jobs
        if JOB_GROUP in ['reformat_data', 'assemble_data']:
            if JOB_GROUP == 'reformat_data':
                JOB_GROUP_obs_jobs_dict = reformat_data_obs_jobs_dict
            elif JOB_GROUP == 'assemble_data':
                JOB_GROUP_obs_jobs_dict = assemble_data_obs_jobs_dict
            for verif_type_job in list(JOB_GROUP_obs_jobs_dict[verif_type]\
                                       .keys()):
                # Initialize job environment dictionary
                job_env_dict = gda_util.initalize_job_env_dict(
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
                    all_truth_file_exist = gda_util.check_truth_files(
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
elif JOB_GROUP == 'gather_stats':
    print("----> Making job scripts for "+VERIF_CASE_STEP+" "
      +"for job group "+JOB_GROUP)
    # Initialize job environment dictionary
    job_env_dict = gda_util.initalize_job_env_dict(
        JOB_GROUP, JOB_GROUP,
        VERIF_CASE_STEP_abbrev, JOB_GROUP
    )
    # Loop through and write job script for dates and models
    date_dt = start_date_dt
    while date_dt <= end_date_dt:
        job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
        for model_idx in range(len(model_list)):
            job_env_dict['MODEL'] = model_list[model_idx]
            njobs+=1
            # Create job file
            job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
            print("Creating job script: "+job_file)
            job = open(job_file, 'w')
            job.write('#!/bin/bash\n')
            job.write('set -x\n')
            job.write('\n')
            # Set any environment variables for special cases
            # Write environment variables
            for name, value in job_env_dict.items():
                job.write('export '+name+'='+value+'\n')
            job.write('\n')
            # Do file checks
            stat_files_exist = gda_util.check_stat_files(job_env_dict)
            if stat_files_exist:
                write_job_cmds = True
            else:
                write_job_cmds = False
            # Write job commands
            if write_job_cmds:
                for cmd in gather_stats_jobs_dict['commands']:
                    job.write(cmd+'\n')
            job.close()
        date_dt = date_dt + datetime.timedelta(days=1)

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(DATA, VERIF_CASE_STEP,
                                       'METplus_job_scripts', JOB_GROUP,
                                       'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("WARNING: No job files created in "
              +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                            JOB_GROUP))
    poe_files = glob.glob(os.path.join(DATA, VERIF_CASE_STEP,
                                       'METplus_job_scripts', JOB_GROUP,
                                       'poe*'))
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
        poe_filename = os.path.join(DATA, VERIF_CASE_STEP,
                                    'METplus_job_scripts',
                                    JOB_GROUP, 'poe_jobs'+str(node))
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
               str(iproc-1)+' '
               +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                             JOB_GROUP, job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                             JOB_GROUP, job)+'\n'
            )
        poe_file.close()
        njob+=1
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(DATA, VERIF_CASE_STEP,
                                'METplus_job_scripts',
                                JOB_GROUP, 'poe_jobs'+str(node))
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
