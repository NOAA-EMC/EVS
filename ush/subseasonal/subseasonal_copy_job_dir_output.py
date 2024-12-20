#!/usr/bin/env python3   
'''                      
Program Name: subseasonal_copy_job_dir_output.py
Contact(s): Shannon Shields
Abstract: This script is run by all stats and plots scripts in scripts/.
          This copies MPMD working directory output to common DATA directory.
'''

import os
import glob
import subseasonal_util as sub_util

print("BEGIN: "+os.path.basename(__file__))

#Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']

# Copy files to desired location
if STEP == 'stats':
    job_work_JOB_GROUP_dir = os.path.join(
        DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',
        'job_work_dir', JOB_GROUP
    )
    if JOB_GROUP == 'gather_stats':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', '*.*', '*'
        )
    else:
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*', VERIF_CASE, '*'
        )
elif STEP == 'plots':
    job_work_JOB_GROUP_dir = os.path.join(
        DATA, f"{VERIF_CASE}_{STEP}", 'plot_output',
        'job_work_dir', JOB_GROUP
    )
    if JOB_GROUP == 'condense_stats':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
            '*', 'model1_*.stat'
        )
    elif JOB_GROUP == 'filter_stats':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
            '*', 'fcst*.stat'
        )
    elif JOB_GROUP == 'make_plots':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
            '*', '*', '*.png'
        )
    elif JOB_GROUP == 'tar_images':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
            '*', '*.tar'
        )
output_file_JOB_list = glob.glob(job_wildcard_dir)
for output_file_JOB in sorted(output_file_JOB_list, key=len):
    output_file_end_path = output_file_JOB.partition(
        job_work_JOB_GROUP_dir+'/'
    )[2].partition('/')[2]
    if STEP == 'stats':
        output_file_DATA = os.path.join(
            DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',
            output_file_end_path
        )
    elif STEP == 'plots':
        output_file_DATA =  os.path.join(
            DATA, f"{VERIF_CASE}_{STEP}", 'plot_output',
            output_file_end_path
        )
    if not os.path.exists(output_file_DATA):
        sub_util.copy_file(output_file_JOB, output_file_DATA)

print("END: "+os.path.basename(__file__))
