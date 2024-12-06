#!/usr/bin/env python3
'''
Name: global_det_atmos_copy_job_dir_output.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This copies MPMD working directory output to common DATA directory
Run By: scripts/stats/global_det/exevs_global_det_atmos_grid2grid_stats.sh
'''

import os
import glob
import global_det_atmos_util as gda_util

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
if STEP == 'plots':
    NDAYS = os.environ['NDAYS']

# Copy files to desired location
if STEP == 'stats':
    copy_from_job_to_DATA = True
    if VERIF_CASE == 'wmo':
        job_work_JOB_GROUP_dir = os.path.join(
            DATA, 'job_work_dir', JOB_GROUP
        )
    else:
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
            f"last{NDAYS}days", '*', '*', '*', 'condensed_stats*'
        )
    elif JOB_GROUP == 'filter_stats':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
            f"last{NDAYS}days", '*', '*', '*', 'fcst*.stat'
        )
    elif JOB_GROUP == 'make_plots':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
            f"last{NDAYS}days", '*', '*', '*', '*', '*.png'
        )
    elif JOB_GROUP == 'tar_images':
        job_wildcard_dir = os.path.join(
            job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
            f"last{NDAYS}days", '*', '*', '*', '*', '*.tar'
        )
    if SENDCOM == 'YES' and JOB_GROUP != 'tar_images':
        copy_from_job_to_DATA = False
    else:
        copy_from_job_to_DATA = True
output_file_JOB_list = glob.glob(job_wildcard_dir)
if STEP == 'plots' and JOB_GROUP == 'make_plots':
    job_wildcard_dir2 = os.path.join(
        job_work_JOB_GROUP_dir, 'job*', f"{RUN}.*", '*',
        f"last{NDAYS}days", '*', '*', '*', '*', '*.gif'
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
        if STEP == 'stats':
            if VERIF_CASE == 'wmo':
                output_file_DATA = os.path.join(
                    DATA, output_file_end_path
                )
            else:
                output_file_DATA = os.path.join(
                    DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output',
                    output_file_end_path
                )
        elif STEP == 'plots':
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
else:
     print(f"NOTE: Not copying files to common DATA directory for {JOB_GROUP}")
print("END: "+os.path.basename(__file__))
