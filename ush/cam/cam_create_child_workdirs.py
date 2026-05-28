#!/usr/bin/env python3
"""
cam_create_child_workdirs.py
CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov
----------------------
Creates and checks output directories used by child processors (MPMD
operations) in the cam component.

Environment Variables (Inputs):
    DATA: str
        Top-level data directory.
    VERIF_CASE: str
        Verification case name.
    STEP: str
        Workflow step (e.g., 'prep', 'stats', 'plots').
    job_type: str (if STEP == 'stats')
        Type of job for stats step.

Outputs:
    - Raises OSError if required output or working directories do not exist.
    - Sets up directory paths for downstream processing in the cam component.

This script is intended to be run as part of the cam component to ensure all
required output and working directories are present before launching child
processes.
"""

import os

import cam_util as cutil

DATA = os.environ['DATA']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
MODELNAME = os.environ['MODELNAME']
if STEP == 'stats':
    job_type = os.environ['job_type']

if STEP == 'prep':
    if VERIF_CASE == "precip" and MODELNAME != "cam":
        jobdir = os.path.join(
            DATA, VERIF_CASE, 'METplus_job_scripts'
        )
        outdir = os.path.join(
            DATA, VERIF_CASE, 'METplus_output'
        )
        workdirs = os.path.join(
            outdir, 'workdirs'
        )
    else:
        jobdir = os.path.join(
            DATA, VERIF_CASE, STEP, 'prep_job_scripts'
        )
        outdir = os.path.join(
            DATA, VERIF_CASE, 'data'
        )
        workdirs = os.path.join(
            outdir, 'workdirs'
        )
elif STEP == 'stats':
    jobdir = os.path.join(
        DATA, VERIF_CASE, 'METplus_job_scripts', job_type
    )
    outdir = os.path.join(
        DATA, VERIF_CASE, 'METplus_output'
    )
    workdirs = os.path.join(
        outdir, 'workdirs', job_type
    )
elif STEP == 'plots':
    jobdir = os.path.join(
        DATA, VERIF_CASE, 'plotting_job_scripts'
    )
    outdir = os.path.join(
        DATA, VERIF_CASE, 'out'
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
        elif STEP == "stats":
            print(
                "Done making working directories for child processes "
                + f"({job_type} jobs)."
            )
        elif STEP == "plots":
            print(
                "Done making working directories for child processes."
            )
        os.chdir(wd)

