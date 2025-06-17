#!/usr/bin/env python3
'''
Name: aqm_copy_job_dir_output.py
Orginal Author: Mallory Row (mallory.row@noaa.gov)
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This copies MPMD working directory output to common DATA directory
Run By: scripts/plots/aqm/exevs_aqm_grid2obs.sh
'''

import os
import glob
import aqm_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
SENDCOM = os.environ['SENDCOM']
DATA = os.environ['DATA']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
evs_run_mode = os.environ['evs_run_mode']
fig_name_label = os.environ['fig_name_label']

# Copy files to desired location
if STEP == 'plots':
    job_work_JOB_GROUP_dir = os.path.join(
        DATA, f"{VERIF_CASE}_{STEP}", 'plot_output',
        'job_work_dir', JOB_GROUP
    )
    if JOB_GROUP == 'condense_stats':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
            fig_name_label, '*', '*', '*', 'condensed_stats*'
        )
    elif JOB_GROUP == 'filter_stats':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
            fig_name_label, '*', '*', '*', 'fcst*.stat'
        )
    elif JOB_GROUP == 'make_plots':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
            fig_name_label, '*', '*', '*', '*', '*.png'
        )
    elif JOB_GROUP == 'tar_images':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
            fig_name_label, '*', '*', '*', '*', '*.tar'
        )
    if SENDCOM == 'YES' and JOB_GROUP != 'tar_images':
        copy_from_job_to_DATA = False
    else:
        copy_from_job_to_DATA = True
output_file_JOB_list = glob.glob(job_wildcard_dir)
if STEP == 'plots' and JOB_GROUP == 'make_plots':
    job_wildcard_dir2 = os.path.join(
        job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
        fig_name_label, '*', '*', '*', '*', '*.gif'
    )
    output_file_JOB_list = (
        output_file_JOB_list
        + glob.glob(job_wildcard_dir2)
    )
if copy_from_job_to_DATA:
    for output_file_JOB in sorted(output_file_JOB_list, key=len):
        output_file_end_path = output_file_JOB.partition(
            job_work_JOB_GROUP_dir+'/'
        )[2].partition('/')[2]
        if STEP == 'plots':
            if JOB_GROUP == 'tar_images':
                output_file_DATA = os.path.join(
                    DATA, f"{VERIF_CASE}_{STEP}", 'plot_output', 'tar_files',
                    output_file_JOB.rpartition('/')[2]
                )
            else:
                output_file_DATA =  os.path.join(
                    DATA, f"{VERIF_CASE}_{STEP}", 'plot_output',
                    output_file_end_path
                )
        if not os.path.exists(output_file_DATA):
            gda_util.copy_file(output_file_JOB, output_file_DATA)
        else:
            print(f"WARNING: {output_file_DATA} exists")
print("END: "+os.path.basename(__file__))
