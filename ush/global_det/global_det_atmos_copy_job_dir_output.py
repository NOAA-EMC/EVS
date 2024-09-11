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
DATA = os.environ['DATA']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
evs_run_mode = os.environ['evs_run_mode']

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
    for output_file_JOB in sorted(glob.glob(job_wildcard_dir), key=len):
        output_file_end_path = output_file_JOB.partition(
            job_work_JOB_GROUP_dir+'/'
        )[2].partition('/')[2]
        output_file_DATA = os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'METplus_output', output_file_end_path)
        if not os.path.exists(output_file_DATA):
            gda_util.copy_file(output_file_JOB, output_file_DATA)
        else:
            print(f"WARNING: {output_file_DATA} exists")

print("END: "+os.path.basename(__file__))
