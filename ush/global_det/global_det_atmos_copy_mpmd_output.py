#!/usr/bin/env python3
'''
Name: global_det_atmos_copy_mpmd_output.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This copies MPMD working directory output to the
          desired final location
Run By: scripts/stats/global_det/exevs_global_det_atmos_grid2grid_stats.sh
'''

import os
import glob
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMOUT = os.environ['COMOUT']
SENDCOM = os.environ['SENDCOM']
DATA = os.environ['DATA']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
evs_run_mode = os.environ['evs_run_mode']

# Copy files to desired location
mpmd_JOB_GROUP_output_dir = os.path.join(
    DATA, f"{VERIF_CASE}_{STEP}", 'METplus_output', 'mpmd_work_dir', JOB_GROUP
)
print(mpmd_JOB_GROUP_output_dir)
if STEP == 'stats':
    mpmd_wildcard_dir = os.path.join(
        mpmd_JOB_GROUP_output_dir, 'job*', RUN+'.*', '*', VERIF_CASE, '*'
    )
    for mpmd_output_file in sorted(glob.glob(mpmd_wildcard_dir), key=len):
        output_end_path = mpmd_output_file.partition(
            mpmd_JOB_GROUP_output_dir+'/'
        )[2].partition('/')[2]
        if SENDCOM == 'YES':
            final_output_file = os.path.join(COMOUT, output_end_path)
        else:
            final_output_file = os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                             'METplus_output', output_end_path)
        if not os.path.exists(final_output_file):
            gda_util.copy_file(mpmd_output_file, final_output_file)
        else:
            print(f"WARNING: {final_output_file} exists")

print("END: "+os.path.basename(__file__))
