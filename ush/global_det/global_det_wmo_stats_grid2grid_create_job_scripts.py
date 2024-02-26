#!/usr/bin/env python3
'''
Name: global_det_wmo_stats_grid2grid_create_job_scripts.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This creates multiple independent job scripts. These
          jobs scripts contain all the necessary environment variables
          and commands to needed to run them.
Run By: scripts/stats/global_det/exevs_global_det_wmo_grid2grid_stats.sh
'''

import sys
import os
import glob
import datetime
import global_det_wmo_util as gdwmo_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMIN = os.environ['COMIN']
COMINgfs = os.environ['COMINgfs']
SENDCOM = os.environ['SENDCOM']
COMOUT = os.environ['COMOUT']
COMOUTsmall = os.environ['COMOUTsmall']
COMOUTfinal = os.environ['COMOUTfinal']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
VDATE = os.environ['VDATE']
MODELNAME = os.environ['MODELNAME']
JOB_GROUP = os.environ['JOB_GROUP']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
METPLUS_PATH = os.environ['METPLUS_PATH']
MET_ROOT = os.environ['MET_ROOT']
PARMevs = os.environ['PARMevs']

VDATE_dt = datetime.datetime.strptime(VDATE, '%Y%m%d')

# Check only running for GFS
if MODELNAME != 'gfs':
    print(f"ERROR: WMO stats are only run for gfs, exit")
    sys.exit(1)

# Set GFS file formats
anl_file_format = os.path.join(
    COMINgfs, MODELNAME+'.{valid?fmt=%Y%m%d}', '{valid?fmt=%2H}', 'atmos',
    MODELNAME+'.t{valid?fmt=%2H}z.pgrb2.0p25.anl'
)
fhr_file_format = os.path.join(
    COMINgfs, MODELNAME+'.{init?fmt=%Y%m%d}', '{init?fmt=%2H}', 'atmos',
    MODELNAME+'.t{init?fmt=%2H}z.pgrb2.0p25.f{lead?fmt=%3H}'
)

# WMO Specifications
valid_hour_list = ['00', '12']
fhr_list = [str(fhr) for fhr in range(12,240+12,12)]

# Get valid, init, forecast hour pairings
verif_time_list = gdwmo_util.get_time_info(
    VDATE, VDATE, 'VALID', valid_hour_list, valid_hour_list, fhr_list
)

# Set up job directory
njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, 'jobs', JOB_GROUP)
gdwmo_util.make_dir(JOB_GROUP_jobs_dir)

# Create job scripts
job_env_dict = gdwmo_util.initalize_job_env_dict()
if JOB_GROUP == 'generate_stats':
     print(f"----> Making job scripts for {VERIF_CASE} {STEP} "
           +f"for job group {JOB_GROUP}")
     for verif_time in verif_time_list:
         print(f"Working with valid time {verif_time['valid_time']:%Y%m%d%H}, "
               +f"forecast hour {verif_time['forecast_hour']}, "
               +f"init time {verif_time['init_time']:%Y%m%d%H}")
         job_env_dict['valid_date'] = f"{verif_time['valid_time']:%Y%m%d%H}"
         job_env_dict['fhr'] = verif_time['forecast_hour']
         # Set input file paths
         anl_file = gdwmo_util.format_filler(
             anl_file_format, verif_time['valid_time'],
             verif_time['valid_time'], 'anl', {}
         )
         log_missing_anl_file = os.path.join(
             DATA, 'mail_missing_'
             +anl_file.rpartition('/')[2].replace('.', '_')+'.sh'
         )
         job_env_dict['anl_file'] = anl_file
         fhr_file = gdwmo_util.format_filler(
             fhr_file_format, verif_time['valid_time'],
             verif_time['init_time'], verif_time['forecast_hour'],
             {}
         )
         log_missing_fhr_file = os.path.join(
             DATA, 'mail_missing_'
             +fhr_file.rpartition('/')[2].replace('.', '_')+'.sh'
         )
         job_env_dict['fhr_file'] = fhr_file
         # Check input files exist
         have_anl = gdwmo_util.check_file_exists_size(anl_file)
         if not have_anl and not os.path.exists(log_missing_anl_file):
             gdwmo_util.log_missing_file_model(
                 log_missing_anl_file, anl_file, MODELNAME,
                 verif_time['valid_time'], 'anl'
             )
         have_fhr = gdwmo_util.check_file_exists_size(fhr_file)
         if not have_fhr and not os.path.exists(log_missing_fhr_file):
             gdwmo_util.log_missing_file_model(
                 log_missing_fhr_file, fhr_file, MODELNAME,
                 verif_time['init_time'], verif_time['forecast_hour'].zfill(3)
             )
         # Set up output file paths
         tmp_fhr_stat_file = os.path.join(
             DATA , f"{RUN}.{verif_time['valid_time']:%Y%m%d}",
             MODELNAME, VERIF_CASE, f"grid_stat_{verif_time['forecast_hour']}"
             +f"0000L_{verif_time['valid_time']:%Y%m%d_%H%M%S}V.stat"
         )
         job_env_dict['tmp_fhr_stat_file'] = tmp_fhr_stat_file
         output_fhr_stat_file = os.path.join(
             COMOUTsmall, f"grid_stat_{verif_time['forecast_hour']}"
             +f"0000L_{verif_time['valid_time']:%Y%m%d_%H%M%S}V.stat"
         )
         job_env_dict['output_fhr_stat_file'] = output_fhr_stat_file
         if os.path.exists(output_fhr_stat_file):
             have_fhr_stat = True
         else:
             have_fhr_stat = False
         # Make job script
         njobs+=1
         job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
         print(f"Creating job script: {job_file}")
         job = open(job_file, 'w')
         job.write('#!/bin/bash\n')
         job.write('set -x\n')
         job.write('\n')
         for name, value in job_env_dict.items():
             job.write(f'export {name}="{value}"\n')
         job.write('\n')
         # If small stat file exists in COMOUTsmall then copy it
         # if not then run METplus
         if have_fhr_stat:
             job.write(
                 'if [ -f $output_fhr_stat_file ]; then '
                 +'cp -v $output_fhr_stat_file $tmp_fhr_stat_file; fi\n'
             )
             job.write('export err=$?; err_chk')
         else:
             if have_anl and have_fhr:
                 job.write(
                     gdwmo_util.metplus_command('GridStat_fcstGFS_obsGFS_ANL_'
                                                +'climoERA_INTERIM.conf')
                     +'\n'
                 )
                 job.write('export err=$?; err_chk\n')
                 if SENDCOM == 'YES':
                     job.write(
                         'if [ -f $tmp_fhr_stat_file ]; then '
                         +'cp -v $tmp_fhr_stat_file $output_fhr_stat_file; fi\n'
                     )
                     job.write('export err=$?; err_chk')
         job.close()
elif JOB_GROUP == 'gather_stats':
    job_env_dict['VDATE'] = VDATE
    # Set input file paths
    fhr_stat_files_wildcard = os.path.join(
        DATA , f"{RUN}.{VDATE}", MODELNAME, VERIF_CASE,
        f"grid_stat_*0000L_{VDATE}_*0000V.stat"
    )
    if len(glob.glob(fhr_stat_files_wildcard)) != 0:
        have_fhr_stat_files = True
    else:
        have_fhr_stat_files = False
    # Set output file paths
    tmp_stat_file = os.path.join(
        DATA, f"{MODELNAME}.{VDATE}",
        f"{NET}.{STEP}.{MODELNAME}.{RUN}.{VERIF_CASE}.v{VDATE}.stat"
    )
    job_env_dict['tmp_stat_file'] = tmp_stat_file
    output_stat_file = os.path.join(
        COMOUTfinal,
        f"{NET}.{STEP}.{MODELNAME}.{RUN}.{VERIF_CASE}.v{VDATE}.stat"
    )
    job_env_dict['output_stat_file'] = output_stat_file
    if os.path.exists(output_stat_file):
        have_stat = True
    else:
        have_stat = False
    # Make job script
    njobs+=1
    job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
    print(f"Creating job script: {job_file}")
    job = open(job_file, 'w')
    job.write('#!/bin/bash\n')
    job.write('set -x\n')
    job.write('\n')
    for name, value in job_env_dict.items():
        job.write(f'export {name}="{value}"\n')
    job.write('\n')
    # If final stat file exists in COMOUTfinal then copy it
    # if not then run METplus
    if have_stat:
        job.write(
            'if [ -f $output_stat_file ]; then '
            +'cp -v $output_stat_file $tmp_stat_file; fi\n'
        )
        job.write('export err=$?; err_chk')
    else:
        if have_fhr_stat_files:
            job.write(
                gdwmo_util.metplus_command('StatAnalysis_fcstGFS.conf')
                +'\n'
            )
            job.write('export err=$?; err_chk\n')
            if SENDCOM == 'YES':
                job.write(
                    'if [ -f $tmp_stat_file ]; then '
                    +'cp -v $tmp_stat_file $output_stat_file; fi\n'
                )
                job.write('export err=$?; err_chk')

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(DATA, 'jobs', JOB_GROUP, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("NOTE: No job files created in "
              +os.path.join(DATA, 'job', JOB_GROUP))
    poe_files = glob.glob(os.path.join(DATA, 'jobs', JOB_GROUP, 'poe*'))
    npoe_files = len(poe_files)
    if npoe_files > 0:
        for poe_file in poe_files:
            os.remove(poe_file)
    njob, iproc, node = 1, 0, 1
    while njob <= njob_files:
        job = f"job{str(njob)}"
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            if iproc >= int(nproc):
                iproc = 0
                node+=1
        poe_filename = os.path.join(DATA, 'jobs', JOB_GROUP,
                                    f"poe_jobs{str(node)}")
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
               f"{str(iproc-1)} "
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
                                f"poe_jobs{str(node)}")
    poe_file = open(poe_filename, 'a')
    iproc+=1
    while iproc <= int(nproc):
       if machine in ['HERA', 'ORION', 'S4', 'JET']:
           poe_file.write(
               f"{str(iproc-1)} /bin/echo {str(iproc)}\n"
           )
       else:
           poe_file.write(
               f"/bin/echo {str(iproc)}\n"
           )
       iproc+=1
    poe_file.close()

print("END: "+os.path.basename(__file__))
