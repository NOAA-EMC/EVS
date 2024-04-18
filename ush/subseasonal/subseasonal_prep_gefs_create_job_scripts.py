#!/usr/bin/env python3
'''
Program Name: subseasonal_prep_gefs_create_job_scripts.py
Contact(s): Shannon Shields
Abstract: This script is run by exevs_subseasonal_gefs_prep.sh
          in scripts/prep/subseasonal.
          This creates an independent job script for GEFS prep data. 
          This job contains all the necessary environment variables
          and commands needed to run the specific
          job.
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
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
model_list = os.environ['model_list'].split(' ')
gefs_members = os.environ['gefs_members']

start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')

# Set up job directory
njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, STEP,
                                  'prep_job_scripts', JOB_GROUP)
if not os.path.exists(JOB_GROUP_jobs_dir):
    os.makedirs(JOB_GROUP_jobs_dir)

################################################
#### retrieve_data jobs
################################################
retrieve_data_jobs_dict = {'env': {},
                          'commands': [sub_util.python_command(
                                           'get_gefs_subseasonal_data_files_'
                                           'prep.py',
                                           []
                                       )]}

# Create job scripts
if JOB_GROUP == 'retrieve_data':
    print("----> Making job scripts for job group "+JOB_GROUP)
    # Initialize job environment dictionary
    job_env_dict = sub_util.initialize_prep_job_env_dict(
        JOB_GROUP, JOB_GROUP,
        JOB_GROUP
    )
    # Loop through and write job script for dates and models
    date_dt = start_date_dt
    while date_dt <= end_date_dt:
        job_env_dict['INITDATE'] = date_dt.strftime('%Y%m%d')
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
            # Check if prep files already exist in output dir
            # If so, adjust fhr_list for restart
            check_prep_files = True
            if check_prep_files:
                prep_fhr_list = (
                    sub_util.check_gefs_prep_files(job_env_dict)
                )
                job_env_dict['fhr_list'] = (
                    '"'+','.join(prep_fhr_list)+'"'
                )
            # Write environment variables
            for name, value in job_env_dict.items():
                job.write('export '+name+'='+value+'\n')
            job.write('\n')
            write_job_cmds = True
            if len(prep_fhr_list) == 0:
                write_job_cmds = False
            # Write job commands
            if write_job_cmds:
                for cmd in retrieve_data_jobs_dict['commands']:
                    job.write(cmd+'\n')
                    job.write('export err=$?; err_chk'+'\n')
            job.close()
        date_dt = date_dt + datetime.timedelta(days=1)

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(DATA, STEP,
                                       'prep_job_scripts', JOB_GROUP,
                                       'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("FATAL ERROR: No job files created in "
              +os.path.join(DATA, STEP, 'prep_job_scripts',
                            JOB_GROUP))
        sys.exit(1)
    poe_files = glob.glob(os.path.join(DATA, STEP,
                                       'prep_job_scripts', JOB_GROUP,
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
        poe_filename = os.path.join(DATA, STEP,
                                    'prep_job_scripts',
                                    JOB_GROUP, 'poe_jobs'+str(node))
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
               str(iproc-1)+' '
               +os.path.join(DATA, STEP, 'prep_job_scripts',
                             JOB_GROUP, job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(DATA, STEP, 'prep_job_scripts',
                             JOB_GROUP, job)+'\n'
            )
        poe_file.close()
        njob+=1
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(DATA, STEP,
                                'prep_job_scripts',
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
