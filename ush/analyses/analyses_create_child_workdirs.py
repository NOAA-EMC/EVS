#!/usr/bin/env python3
# =============================================================================
#
# NAME: analyses_create_child_workdirs.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
#                 Perry Shafran, perry.shafran@noaa.gov
# PURPOSE: Write output directories used by child processors (MPMD operations)
#
# =============================================================================

import os
import analyses_util as cutil

DATA = os.environ['DATA']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
if STEP == 'stats':
    job_type = os.environ['job_type']

if STEP == 'prep':
    jobdir = os.path.join(
        DATA, VERIF_CASE, STEP, 'prep_job_scripts'
    )
    outdir = os.path.join(
        DATA, VERIF_CASE, 'data'
    )
    workdirs = os.path.join(
        outdir, 'workdirs'
    )
else:
    raise ValueError(f"Unrecognized STEP name: {STEP}")
if not os.path.exists(outdir):
    raise OSError(f"Output directory does not exist: {outdir}.")
else:
    if not os.path.exists(workdirs):
        raise OSError(
            f"Head working directory does not exist: {workdirs}."
        )
    else:
        wd = os.getcwd()
        os.chdir(outdir)
        job_scripts = [
            job_name for job_name in os.listdir(jobdir) 
            if job_name[:3] == 'job'
        ]
        for job_name in job_scripts:
            workdir = os.path.join(workdirs, job_name)
            if not os.path.exists(workdir):
                os.makedirs(workdir)
            # Exclude "workdirs" and "job" unless it's "completed_jobs"
            # "-prune" prevents recursion into those excluded dirs
            # Other than that, make all directories in current workdir
            cutil.run_shell_command([
                'find', '.', '\\(', '-path', 
                '\"*workdirs*\"', '-o', '\\(', '-path', '\"*job*\"', 
                '!', '-path', '\"*completed_jobs*\"', '\\)', '\\)', 
                '-prune', '-o', '-type', 'd', '-exec', 'mkdir', '-p', 
                os.path.join(workdir,'{}'), '\\;'
            ])
        if STEP == "prep":
            print(
                "Done making working directories for child prcoesses."
            )
        os.chdir(wd)

