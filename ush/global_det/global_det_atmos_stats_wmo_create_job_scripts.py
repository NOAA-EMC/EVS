#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_wmo_create_job_scripts.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This creates multiple independent job scripts. These
          jobs scripts contain all the necessary environment variables
          and commands to needed to run them.
Run By: scripts/stats/global_det/exevs_global_det_atmos_wmo_stats.sh
'''

import sys
import os
import glob
import datetime
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMIN = os.environ['COMIN']
COMINgfs = os.environ['COMINgfs']
SENDCOM = os.environ['SENDCOM']
COMOUT = os.environ['COMOUT']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
VDATE = os.environ['VDATE']
VYYYYmm = os.environ['VYYYYmm']
MODELNAME = os.environ['MODELNAME']
JOB_GROUP = os.environ['JOB_GROUP']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
METPLUS_PATH = os.environ['METPLUS_PATH']
MET_ROOT = os.environ['MET_ROOT']
FIXevs = os.environ['FIXevs']

VDATE_dt = datetime.datetime.strptime(VDATE, '%Y%m%d')
VYYYYmm_dt = datetime.datetime.strptime(VYYYYmm, '%Y%m')

# Check only running for GFS
if MODELNAME != 'gfs':
    print(f"ERROR: {VERIF_CASE} stats are only run for gfs, exit")
    sys.exit(1)

# Set GFS file formats
anl_file_format = os.path.join(
    COMINgfs, MODELNAME+'.{valid?fmt=%Y%m%d}', '{valid?fmt=%2H}', 'atmos',
    MODELNAME+'.t{valid?fmt=%2H}z.pgrb2.0p25.anl'
)
fhr_0p25_file_format = os.path.join(
    COMINgfs, MODELNAME+'.{init?fmt=%Y%m%d}', '{init?fmt=%2H}', 'atmos',
    MODELNAME+'.t{init?fmt=%2H}z.pgrb2.0p25.f{lead?fmt=%3H}'
)
gaussin_file_format = os.path.join(
    COMIN, 'prep', COMPONENT, RUN+'.{init?fmt=%Y%m%d}', MODELNAME,
    MODELNAME+'.wmo.t{init?fmt=%2H}z.f{lead?fmt=%3H}'
)

# Set GDAS file format
cnvstat_file_format = os.path.join(
     COMINgfs, 'gdas.{valid?fmt=%Y%m%d}', '{valid?fmt=%2H}', 'atmos',
     'gdas.t{valid?fmt=%2H}z.cnvstat'
)
ascii2nc_file_format = os.path.join(
    COMIN, STEP, COMPONENT, RUN+'.{valid?fmt=%Y%m%d}', MODELNAME,
    VERIF_CASE, 'ascii2nc_{valid?fmt=%Y%m%d%H}.nc'
)

# WMO Verifcations
wmo_verif_list = ['grid2grid_upperair', 'grid2obs_upperair']
wmo_init_hour_list = ['00', '12']
wmo_verif_settings_dict = {
    'grid2grid_upperair': {'valid_hour_list': ['00', '12'],
                           'fhr_list': [str(fhr) for fhr \
                                        in range(12,240+12,12)]},
    'grid2obs_upperair': {'valid_hour_list': ['00', '12'],
                          'fhr_list': [str(fhr) for fhr \
                                       in range(12,240+12,12)]}
}
# Set up job directory
njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, 'jobs', JOB_GROUP)
gda_util.make_dir(JOB_GROUP_jobs_dir)

# Create job scripts
if JOB_GROUP == 'reformat_data':
     print(f"----> Making job scripts for {VERIF_CASE} grid2obs {STEP} "
           +f"for job group {JOB_GROUP}")
     grid2obs_valid_hour_list = (
         wmo_verif_settings_dict['grid2obs_upperair']['valid_hour_list']
     )
     job_env_dict = gda_util.initalize_job_env_dict('grid2obs', JOB_GROUP,
                                                    VERIF_CASE, 'grid2obs')
     for vhr in grid2obs_valid_hour_list:
         valid_time_dt = datetime.datetime.strptime(VDATE+vhr, '%Y%m%d%H')
         # Set input paths
         cnvstat_file = gda_util.format_filler(
             cnvstat_file_format, valid_time_dt, valid_time_dt, 'anl', {}
         )
         log_missing_cnvstat_file = os.path.join(
             DATA, 'mail_missing_'
             +cnvstat_file.rpartition('/')[2].replace('.', '_')+'.sh'
         )
         input_ascii2nc_file = os.path.join(
             DATA, 'gdas_cnvstat', f"ascii2nc_{valid_time_dt:%Y%m%d%H}.txt"
         )
         have_cnvstat = gda_util.check_file_exists_size(cnvstat_file)
         if not have_cnvstat and not os.path.exists(log_missing_cnvstat_file):
             gda_util.log_missing_file_truth(
                 log_missing_cnvstat_file, cnvstat_file, 'cnvstat',
                 valid_time_dt
             )
         # Set output paths
         tmp_ascii2nc_file = os.path.join(
             DATA, f"{RUN}.{valid_time_dt:%Y%m%d}", MODELNAME, VERIF_CASE,
             f"ascii2nc_{valid_time_dt:%Y%m%d%H}.nc"
         )
         output_ascii2nc_file = os.path.join(
             COMOUT, f"{RUN}.{valid_time_dt:%Y%m%d}", MODELNAME,
             VERIF_CASE, tmp_ascii2nc_file.rpartition('/')[2]
         )
         have_ascii2nc = os.path.exists(output_ascii2nc_file)
         # Set job variables
         job_env_dict['valid_date'] = f"{valid_time_dt:%Y%m%d%H}"
         job_env_dict['cnvstat_file'] = cnvstat_file
         job_env_dict['input_ascii2nc_file'] = input_ascii2nc_file
         job_env_dict['tmp_ascii2nc_file'] = tmp_ascii2nc_file
         job_env_dict['output_ascii2nc_file'] = output_ascii2nc_file
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
         # If ascii2nc file in COMOUT then copy it
         # if not create it
         if have_ascii2nc:
             job.write(
                 'if [ -f $output_ascii2nc_file ]; then '
                 +'cp -v $output_ascii2nc_file '
                 +'$tmp_ascii2nc_file; fi\n'
             )
             job.write(
                 'if [ -f $tmp_ascii2nc_file ]; then '
                 +'chmod 750 $tmp_ascii2nc_file; fi\n'
             )
             job.write(
                 'if [ -f $tmp_ascii2nc_file ]; then '
                 +'chgrp rstprod $tmp_ascii2nc_file; fi\n'
             )
         else:
             if have_cnvstat:
                 job.write(
                     gda_util.python_command('global_det_atmos_stats_wmo_'
                                             +'reformat_cnvstat.py', [])
                     +'\n'
                 )
                 job.write('export err=$?; err_chk\n')
                 job.write(
                     'if [ -f $input_ascii2nc_file ]; then '
                     +'chmod 750 $input_ascii2nc_file; fi\n'
                 )
                 job.write(
                     'if [ -f $input_ascii2nc_file ]; then '
                     +'chgrp rstprod $input_ascii2nc_file; fi\n'
                 )
                 job.write(
                     'if [ -f $input_ascii2nc_file ]; then '
                     +gda_util.metplus_command('ASCII2NC_obsCNVSTAT.conf')
                     +'; fi\n'
                 )
                 job.write('export err=$?; err_chk\n')
                 job.write(
                     'if [ -f $tmp_ascii2nc_file ]; then '
                     +'chmod 750 $tmp_ascii2nc_file; fi\n'
                 )
                 job.write(
                     'if [ -f $tmp_ascii2nc_file ]; then '
                     +'chgrp rstprod $tmp_ascii2nc_file; fi\n'
                 )
                 if SENDCOM == 'YES':
                     job.write(
                         'if [ -f $tmp_ascii2nc_file ]; then '
                         +'cp -v $tmp_ascii2nc_file '
                         +'$output_ascii2nc_file; fi\n'
                     )
                     job.write('export err=$?; err_chk\n')
                     job.write(
                         'if [ -f $output_ascii2nc_file ]; then '
                         +'chmod 750 $output_ascii2nc_file; fi\n'
                     )
                     job.write(
                         'if [ -f $output_ascii2nc_file ]; then '
                         +'chgrp rstprod $output_ascii2nc_file; fi\n'
                     )
elif JOB_GROUP == 'generate_stats':
     for wmo_verif in wmo_verif_list:
         job_env_dict = gda_util.initalize_job_env_dict(wmo_verif, JOB_GROUP,
                                                        VERIF_CASE, wmo_verif)
         job_env_dict['wmo_verif'] = wmo_verif
         print(f"----> Making job scripts for {VERIF_CASE} {wmo_verif} {STEP} "
               +f"for job group {JOB_GROUP}")
         # Set WMO verification specifications
         wmo_verif_valid_hour_list = (
             wmo_verif_settings_dict[wmo_verif]['valid_hour_list']
         )
         wmo_verif_fhr_list = (
             wmo_verif_settings_dict[wmo_verif]['fhr_list']
         )
         if wmo_verif == 'grid2grid_upperair':
             wmo_verif_metplus_conf_list = [
                 'GridStat_fcstGFS_obsGFS_ANL_climoERA_INTERIM_CNT.conf',
                 'GridStat_fcstGFS_obsGFS_ANL_climoERA_INTERIM_VCNT.conf',
                 'GridStat_fcstGFS_obsGFS_ANL_climoERA_INTERIM_GRAD.conf'
             ]
         elif wmo_verif == 'grid2obs_upperair':
             wmo_verif_metplus_conf_list = [
                 'PointStat_fcstGFS_obsADPUPA_climoERA_INTERIM_CNT.conf',
                 'PointStat_fcstGFS_obsADPUPA_climoERA_INTERIM_VCNT.conf'
             ]
         for vhr in wmo_verif_valid_hour_list:
             valid_time_dt = datetime.datetime.strptime(VDATE+vhr, '%Y%m%d%H')
             # Set truth input paths
             # grid2grid_upperair: model's own analysis
             # grid2obs_upperair: radiosondes
             if wmo_verif == 'grid2grid_upperair':
                 truth_file = gda_util.format_filler(
                     anl_file_format, valid_time_dt, valid_time_dt, 'anl', {}
                 )
             elif wmo_verif == 'grid2obs_upperair':
                 truth_file = gda_util.format_filler(
                     ascii2nc_file_format, valid_time_dt, valid_time_dt, 'anl', {}
                 )
             log_missing_truth_file = os.path.join(
                 DATA, 'mail_missing_'
                 +truth_file.rpartition('/')[2].replace('.', '_')+'.sh'
             )
             have_truth = gda_util.check_file_exists_size(truth_file)
             if not have_truth and not os.path.exists(log_missing_truth_file):
                 if wmo_verif == 'grid2grid_upperair':
                     gda_util.log_missing_file_model(
                         log_missing_truth_file, truth_file, MODELNAME,
                         valid_time_dt, 'anl'
                     )
                 else:
                     gda_util.log_missing_file_truth(
                         log_missing_truth_file, truth_file, 'cnvstat',
                         valid_time_dt
                     )
             for fhr in wmo_verif_fhr_list:
                 init_time_dt = (valid_time_dt
                                 - datetime.timedelta(hours=int(fhr)))
                 if f"{init_time_dt:%H}" not in wmo_init_hour_list:
                     print(f"Skipping forecast hour {fhr} with init"
                           +f"{init_time_dt:%Y%m%d%H} as init hour not in "
                           +f"WMO required init hours {wmo_init_hour_list}")
                     continue
                 # Set forecast input paths
                 # grid2grid_upperair: 0.25 degree lat-lon
                 # grid2obs_upperair: gaussian grid prepped files
                 if wmo_verif == 'grid2grid_upperair':
                     fhr_file = gda_util.format_filler(
                         fhr_0p25_file_format, valid_time_dt, init_time_dt,
                         fhr, {}
                     )
                 elif wmo_verif == 'grid2obs_upperair':
                     fhr_file = gda_util.format_filler(
                         gaussin_file_format, valid_time_dt, init_time_dt,
                         fhr, {}
                     )
                 log_missing_fhr_file = os.path.join(
                     DATA, 'mail_missing_'
                     +fhr_file.rpartition('/')[2].replace('.', '_')+'.sh'
                 )
                 have_fhr = gda_util.check_file_exists_size(fhr_file)
                 if not have_fhr and not os.path.exists(log_missing_fhr_file):
                     gda_util.log_missing_file_model(
                         log_missing_fhr_file, fhr_file, MODELNAME,
                         init_time_dt, fhr.zfill(3)
                     )
                 for wmo_verif_metplus_conf in wmo_verif_metplus_conf_list:
                     # Set up output file path
                     # grid2grid_upperair: grid_stat
                     # grid2obs_upperair: point_stat
                     if wmo_verif == 'grid2grid_upperair':
                         met_tool = 'grid_stat'
                     else:
                         met_tool = 'point_stat'
                     wmo_verif_metplus_conf_line_type = (
                         wmo_verif_metplus_conf.rpartition('_')[2]\
                         .replace('.conf', '')
                     )
                     tmp_fhr_stat_file = os.path.join(
                         DATA , f"{RUN}.{valid_time_dt:%Y%m%d}",
                         MODELNAME, VERIF_CASE, f"{met_tool}_{wmo_verif}_"
                         f"{wmo_verif_metplus_conf_line_type}_"
                         +f"{fhr.zfill(2)}0000L_"
                         +f"{valid_time_dt:%Y%m%d_%H%M%S}V.stat"
                     )
                     output_fhr_stat_file = os.path.join(
                         COMOUT, f"{RUN}.{valid_time_dt:%Y%m%d}", MODELNAME,
                         VERIF_CASE, tmp_fhr_stat_file.rpartition('/')[2]
                     )
                     if os.path.exists(output_fhr_stat_file):
                         have_fhr_stat = True
                     else:
                         have_fhr_stat = False
                     # Set wmo_verif job variables
                     job_env_dict['valid_date'] = f"{valid_time_dt:%Y%m%d%H}"
                     job_env_dict['fhr'] = fhr
                     job_env_dict['fhr_file'] = fhr_file
                     job_env_dict['tmp_fhr_stat_file'] = tmp_fhr_stat_file
                     job_env_dict['output_fhr_stat_file'] = (
                         output_fhr_stat_file
                     )
                     if wmo_verif == 'grid2grid_upperair':
                         job_env_dict['anl_file'] = truth_file
                     elif wmo_verif == 'grid2obs_upperair':
                         job_env_dict['ascii2nc_file'] = truth_file
                         wmo_global_radiosonde_file = os.path.join(
                             FIXevs, 'masks', 'WMO_GLOBAL_radiosondes.txt'
                         )
                         if os.path.exists(wmo_global_radiosonde_file):
                             with open(wmo_global_radiosonde_file) as wgr:
                                 job_env_dict['wmo_indiv_radiosondes'] = (
                                     ','.join(wgr.readline().split(' ')[1:])
                                 )
                     # Make job script
                     njobs+=1
                     job_file = os.path.join(JOB_GROUP_jobs_dir,
                                             'job'+str(njobs))
                     print(f"Creating job script: {job_file}")
                     job = open(job_file, 'w')
                     job.write('#!/bin/bash\n')
                     job.write('set -x\n')
                     job.write('\n')
                     for name, value in job_env_dict.items():
                         job.write(f'export {name}="{value}"\n')
                     job.write('\n')
                     # If small stat file exists in COMOUT then copy it
                     # if not then run METplus
                     if have_fhr_stat:
                         job.write(
                             'if [ -f $output_fhr_stat_file ]; then '
                             +'cp -v $output_fhr_stat_file '
                             +'$tmp_fhr_stat_file; fi\n'
                         )
                         job.write('export err=$?; err_chk')
                     else:
                         if have_truth and have_fhr:
                             job.write(
                                 gda_util.metplus_command(
                                     wmo_verif_metplus_conf
                                 )
                                 +'\n'
                             )
                             job.write('export err=$?; err_chk\n')
                             if SENDCOM == 'YES':
                                 job.write(
                                     'if [ -f $tmp_fhr_stat_file ]; then '
                                     +'cp -v $tmp_fhr_stat_file '
                                     +'$output_fhr_stat_file; fi\n'
                                 )
                                 job.write('export err=$?; err_chk')
                     job.close()
elif JOB_GROUP == 'gather_stats':
    job_env_dict = gda_util.initalize_job_env_dict('all', JOB_GROUP,
                                                   VERIF_CASE, 'all')
    print(f"----> Making job scripts for {VERIF_CASE} {STEP} "
          +f"for job group {JOB_GROUP}")
    job_env_dict['VDATE'] = VDATE
    # Set input file paths
    fhr_stat_files_wildcard = os.path.join(
        DATA , f"{RUN}.{VDATE}", MODELNAME, VERIF_CASE,
        f"*0000L_{VDATE}_*0000V.stat"
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
        COMOUT, f"{MODELNAME}.{VDATE}", tmp_stat_file.rpartition('/')[2]
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
    # If final stat file exists in COMOUT then copy it
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
                gda_util.metplus_command('StatAnalysis_fcstGFS_filter.conf')
                +'\n'
            )
            job.write('export err=$?; err_chk\n')
            if SENDCOM == 'YES':
                job.write(
                    'if [ -f $tmp_stat_file ]; then '
                    +'cp -v $tmp_stat_file $output_stat_file; fi\n'
                )
                job.write('export err=$?; err_chk')
    job.close()
elif JOB_GROUP == 'summarize_stats':
    job_env_dict = gda_util.initalize_job_env_dict('all', JOB_GROUP,
                                                   VERIF_CASE, 'all')
    job_env_dict['year_month'] = VYYYYmm
    job_env_dict['valid_date'] = VDATE
    # Get daily stat files in VYYYYmm
    VYYYYmm_daily_stats_dir = os.path.join(DATA, f"{VYYYYmm}_daily_stats")
    date_dt = VDATE_dt
    while date_dt >= VYYYYmm_dt:
        input_date_stat_file = os.path.join(
            COMIN, STEP, COMPONENT, f"{MODELNAME}.{date_dt:%Y%m%d}",
            f"{NET}.{STEP}.{MODELNAME}.{RUN}.{VERIF_CASE}."
            +f"v{date_dt:%Y%m%d}.stat"
        )
        tmp_date_stat_file = os.path.join(
            VYYYYmm_daily_stats_dir, input_date_stat_file.rpartition('/')[2]
        )
        if gda_util.check_file_exists_size(input_date_stat_file):
            print(f"Linking {input_date_stat_file} to {tmp_date_stat_file}")
            os.symlink(input_date_stat_file, tmp_date_stat_file)
        date_dt = date_dt - datetime.timedelta(days=1)
    job_env_dict['daily_stats_dir'] = VYYYYmm_daily_stats_dir
    # Make job scripts
    VYYYYmm_monthly_stats_dir = os.path.join(DATA, f"{VYYYYmm}_monthly_stats")
    job_env_dict['monthly_stats_dir'] = VYYYYmm_monthly_stats_dir
    for wmo_verif in wmo_verif_list:
        job_env_dict['wmo_verif'] = wmo_verif
        if wmo_verif == 'grid2grid_upperair':
            job_env_dict['obtype'] = f"{MODELNAME}_anl"
            job_env_dict['summary_columns'] = (
                'VCNT:RMSVE,VCNT:SPEED_ERR,CNT:ME,CNT:RMSE,CNT:ANOM_CORR,'
                +'GRAD:S1,CNT:MAE,CNT:RMSFA,CNT:RMSOA,CNT:FSTDEV,CNT:OSTDEV'
            )
        elif wmo_verif == 'grid2obs_upperair':
            job_env_dict['obtype'] = 'ADPUPA'
            job_env_dict['summary_columns'] = (
                'VCNT:RMSVE,VCNT:SPEED_ERR,CNT:ME,CNT:RMSE,CNT:MAE'
            )
        wmo_verif_metplus_conf = 'StatAnalysis_fcstGFS_summary.conf'
        for vhr in wmo_verif_settings_dict[wmo_verif]['valid_hour_list']:
            job_env_dict['valid_hour'] = vhr
            tmp_wmo_verif_vhr_stat_file = os.path.join(
                DATA , f"{RUN}.{VDATE}", MODELNAME, VERIF_CASE,
                f"{MODELNAME}.{wmo_verif}.{VYYYYmm}_{vhr}Z.summary.stat"
            )
            job_env_dict['tmp_wmo_verif_vhr_stat_file'] = (
                tmp_wmo_verif_vhr_stat_file
            )
            job_env_dict['tmp_wmo_verif_vhr_dump_row_file'] = (
                tmp_wmo_verif_vhr_stat_file.replace(
                    '.summary.', '.summary_dump_row.'
                )
            )
            output_wmo_verif_vhr_stat_file = os.path.join(
                COMOUT , f"{RUN}.{VDATE}", MODELNAME, VERIF_CASE,
                tmp_wmo_verif_vhr_stat_file.rpartition('/')[2]
            )
            job_env_dict['output_wmo_verif_vhr_stat_file'] = (
                output_wmo_verif_vhr_stat_file
            )
            job_env_dict['output_wmo_verif_vhr_dump_row_file'] = (
                output_wmo_verif_vhr_stat_file.replace(
                    '.summary.', '.summary_dump_row.'
                )
            )
            if os.path.exists(output_wmo_verif_vhr_stat_file):
                have_stat = True
            else:
                have_stat = False
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
            if have_stat:
                job.write(
                    'if [ -f $output_wmo_verif_vhr_stat_file ]; then '
                    +'cp -v $output_wmo_verif_vhr_stat_file '
                    +'$tmp_wmo_verif_vhr_stat_file; fi\n'
                )
                job.write('export err=$?; err_chk\n')
                job.write(
                    'if [ -f $output_wmo_verif_vhr_dump_row_file ]; then '
                    +'cp -v $output_wmo_verif_vhr_dump_row_file '
                    +'$tmp_wmo_verif_vhr_dump_row_file; fi\n'
                )
                job.write('export err=$?; err_chk')
            else:
                job.write(gda_util.metplus_command(wmo_verif_metplus_conf)
                          +'\n')
                job.write('export err=$?; err_chk\n')
                if SENDCOM == 'YES':
                    job.write(
                        'if [ -f $tmp_wmo_verif_vhr_stat_file ]; then '
                        +'cp -v $tmp_wmo_verif_vhr_stat_file '
                        +'$output_wmo_verif_vhr_stat_file; fi\n'
                    )
                    job.write('export err=$?; err_chk\n')
                    job.write(
                        'if [ -f $tmp_wmo_verif_vhr_dump_row_file ]; then '
                        +'cp -v $tmp_wmo_verif_vhr_dump_row_file '
                        +'$output_wmo_verif_vhr_dump_row_file; fi\n'
                    )
                    job.write('export err=$?; err_chk')
            job.close()

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(DATA, 'jobs', JOB_GROUP, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("NOTE: No job files created in "
              +os.path.join(DATA, 'jobs', JOB_GROUP))
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
