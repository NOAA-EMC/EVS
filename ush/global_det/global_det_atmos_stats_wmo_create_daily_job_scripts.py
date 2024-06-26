#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_wmo_create_daily_job_scripts.py
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
import netCDF4 as netcdf
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMIN = os.environ['COMIN']
COMINgfs = os.environ['COMINgfs']
COMINobsproc = os.environ['COMINobsproc']
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

# Set file formats
anl_file_format = os.path.join(
    COMINgfs, MODELNAME+'.{valid?fmt=%Y%m%d}', '{valid?fmt=%2H}', 'atmos',
    MODELNAME+'.t{valid?fmt=%2H}z.pgrb2.0p25.anl'
)
fhr_0p25_file_format = os.path.join(
    COMINgfs, MODELNAME+'.{init?fmt=%Y%m%d}', '{init?fmt=%2H}', 'atmos',
    MODELNAME+'.t{init?fmt=%2H}z.pgrb2.0p25.f{lead?fmt=%3H}'
)
gaussian_file_format = os.path.join(
    COMIN, 'prep', COMPONENT, RUN+'.{init?fmt=%Y%m%d}', MODELNAME,
    MODELNAME+'.wmo.t{init?fmt=%2H}z.f{lead?fmt=%3H}'
)
cnvstat_file_format = os.path.join(
     COMINgfs, 'gdas.{valid?fmt=%Y%m%d}', '{valid?fmt=%2H}', 'atmos',
     'gdas.t{valid?fmt=%2H}z.cnvstat'
)
cnvstat_txt_file_format = os.path.join(
    DATA, 'gdas_cnvstat', 'gdas_cnvstat_{valid?fmt=%Y%m%d%H}.txt'
)
prepbufr_file_format = os.path.join(
    COMINobsproc, 'gdas.{valid?fmt=%Y%m%d}', '{valid?fmt=%2H}', 'atmos',
    'gdas.t{valid?fmt=%2H}z.prepbufr'
)
cnvstat_ascii2nc_file_format = os.path.join(
    DATA, RUN+'.{valid?fmt=%Y%m%d}', MODELNAME, VERIF_CASE,
    'ascii2nc_gdas_cnvstat_{valid?fmt=%Y%m%d%H}.nc'
)
prepbufr_pb2nc_file_format = os.path.join(
    DATA, RUN+'.{valid?fmt=%Y%m%d}', MODELNAME, VERIF_CASE,
    'pb2nc_gdas_prepbufr_{valid?fmt=%Y%m%d%H}.nc'
)
regriddataplane_file_format = os.path.join(
    DATA , RUN+'.{valid?fmt=%Y%m%d}', MODELNAME, VERIF_CASE,
    'regrid_data_plane_init{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
)
stat_file_format = os.path.join(
    DATA , RUN+'.{valid?fmt=%Y%m%d}', MODELNAME, VERIF_CASE,
    '{met_tool?fmt=str}_{wmo_verif?fmt=str}_{line_type?fmt=str}_'
    +'{lead?fmt=%2H}0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
)
pcpcombine_file_format = os.path.join(
    DATA , RUN+'.{valid?fmt=%Y%m%d}', MODELNAME, VERIF_CASE,
    'pcp_combine_precip_accum{accum?fmt=str}H_init{init?fmt=%Y%m%d%H}_'
    'fhr{lead?fmt=%3H}.nc'
)
daily_stat_file_format = os.path.join(
    DATA, MODELNAME+'.{valid?fmt=%Y%m%d}',
    f"{NET}.{STEP}.{MODELNAME}.{RUN}.{VERIF_CASE}."
    +'v{valid?fmt=%Y%m%d}.stat'
)


# WMO Verifcations
wmo_verif_list = ['grid2grid_upperair', 'grid2obs_upperair', 'grid2obs_sfc']
wmo_init_hour_list = ['00', '12']
wmo_verif_settings_dict = {
    'grid2grid_upperair': {'valid_hour_list': ['00', '12'],
                           'fhr_list': [str(fhr) for fhr \
                                        in range(12,240+12,12)]},
    'grid2obs_upperair': {'valid_hour_list': ['00', '12'],
                          'fhr_list': [str(fhr) for fhr \
                                       in range(12,240+12,12)]},
    'grid2obs_sfc': {'valid_hour_list': ['00', '03', '06', '09',
                                         '12', '15', '18', '21'],
                     'fhr_list': [str(fhr) for fhr \
                                  in [*range(0,72,3), *range(72,240+6,6)]]},
}
# Set up job directory
njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, 'jobs', JOB_GROUP)
gda_util.make_dir(JOB_GROUP_jobs_dir)

# Create job scripts
if JOB_GROUP == 'reformat_data':
     # Do not run for grid2grid_upperair
     wmo_verif_list.remove('grid2grid_upperair')
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
         for vhr in wmo_verif_valid_hour_list:
             valid_time_dt = datetime.datetime.strptime(VDATE+vhr, '%Y%m%d%H')
             # Reformat observations
             for key_chk in ['fhr', 'fhr_file', 'tmp_regriddataplane_file',
                             'output_regriddataplane_file']:
                 if key_chk in list(job_env_dict.keys()):
                     job_env_dict.pop(key_chk)
             # Set input paths
             if wmo_verif == 'grid2obs_upperair':
                 obs_file = gda_util.format_filler(
                     cnvstat_file_format, valid_time_dt, valid_time_dt,
                     'anl', {}
                 )
                 input_ascii2nc_file = gda_util.format_filler(
                     cnvstat_txt_file_format, valid_time_dt, valid_time_dt,
                     'anl', {}
                 )
                 obtype = 'cnvstat'
             elif wmo_verif == 'grid2obs_sfc':
                 if int(vhr) % 6 == 0:
                     obs_file = gda_util.format_filler(
                         prepbufr_file_format, valid_time_dt, valid_time_dt,
                         'anl', {}
                     )
                     obs_window = '0'
                 else:
                     obs_file = gda_util.format_filler(
                         prepbufr_file_format,
                         valid_time_dt + datetime.timedelta(hours=3),
                         valid_time_dt + datetime.timedelta(hours=3),
                         'anl', {}
                     )
                     obs_window = '-10800'
                 obtype = 'prepbufr'
             log_missing_obs_file = os.path.join(
                 DATA, 'mail_missing_'
                 +obs_file.rpartition('/')[2].replace('.', '_')+'.sh'
             )
             have_obs = gda_util.check_file_exists_size(obs_file)
             if not have_obs and not os.path.exists(log_missing_obs_file):
                 gda_util.log_missing_file_truth(
                     log_missing_obs_file, obs_file, obtype,
                     valid_time_dt
                 )
             # Set output paths
             if wmo_verif == 'grid2obs_upperair':
                 tmp_obs2nc_file = gda_util.format_filler(
                     cnvstat_ascii2nc_file_format, valid_time_dt,
                     valid_time_dt, 'anl', {}
                 )
             elif wmo_verif == 'grid2obs_sfc':
                 tmp_obs2nc_file = gda_util.format_filler(
                     prepbufr_pb2nc_file_format, valid_time_dt, valid_time_dt,
                     'anl', {}
                 )
             output_obs2nc_file = os.path.join(
                 COMOUT, f"{RUN}.{valid_time_dt:%Y%m%d}", MODELNAME,
                 VERIF_CASE, tmp_obs2nc_file.rpartition('/')[2]
             )
             have_obs2nc = os.path.exists(output_obs2nc_file)
             # Set job variables
             job_env_dict['valid_date'] = f"{valid_time_dt:%Y%m%d%H}"
             job_env_dict['COMINobsproc'] = COMINobsproc
             job_env_dict['obs_file'] = obs_file
             job_env_dict['tmp_obs2nc_file'] = tmp_obs2nc_file
             job_env_dict['output_obs2nc_file'] = output_obs2nc_file
             if wmo_verif == 'grid2obs_upperair':
                 job_env_dict['input_ascii2nc_file'] = input_ascii2nc_file
             elif wmo_verif == 'grid2obs_sfc':
                 job_env_dict['obs_window'] = obs_window
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
             # If obs2nc file in COMOUT then copy it
             # if not create it
             if have_obs2nc:
                 job.write(
                     'if [ -f $output_obs2nc_file ]; then '
                     +'cp -v $output_obs2nc_file '
                     +'$tmp_obs2nc_file; fi\n'
                 )
                 job.write(
                     'if [ -f $tmp_obs2nc_file ]; then '
                     +'chmod 750 $tmp_obs2nc_file; fi\n'
                 )
                 job.write(
                     'if [ -f $tmp_obs2nc_file ]; then '
                     +'chgrp rstprod $tmp_obs2nc_file; fi\n'
                 )
             else:
                 if have_obs:
                     if wmo_verif == 'grid2obs_upperair':
                         job.write(
                             gda_util.python_command('global_det_atmos_stats_'
                                                     +'wmo_reformat_cnvstat.py',
                                                     [])
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
                             +gda_util.metplus_command(
                                 'ASCII2NC_obsCNVSTAT.conf'
                             )
                             +'; fi\n'
                         )
                         job.write('export err=$?; err_chk\n')
                     elif wmo_verif == 'grid2obs_sfc':
                         job.write(
                             gda_util.metplus_command('PB2NC_obsPrepbufr.conf')
                             +'\n'
                         )
                         job.write('export err=$?; err_chk\n')
                     job.write(
                         'if [ -f $tmp_obs2nc_file ]; then '
                         +'chmod 750 $tmp_obs2nc_file; fi\n'
                     )
                     job.write(
                         'if [ -f $tmp_obs2nc_file ]; then '
                         +'chgrp rstprod $tmp_obs2nc_file; fi\n'
                     )
                     if SENDCOM == 'YES':
                         job.write(
                             'if [ -f $tmp_obs2nc_file ]; then '
                             +'cp -v $tmp_obs2nc_file '
                             +'$output_obs2nc_file; fi\n'
                         )
                         job.write('export err=$?; err_chk\n')
                         job.write(
                             'if [ -f $output_obs2nc_file ]; then '
                             +'chmod 750 $output_obs2nc_file; fi\n'
                         )
                         job.write(
                             'if [ -f $output_obs2nc_file ]; then '
                             +'chgrp rstprod $output_obs2nc_file; fi\n'
                         )
             # Reformat forecasts
             if wmo_verif == 'grid2obs_sfc':
                 wmo_verif_fhr_list = (
                     wmo_verif_settings_dict[wmo_verif]['fhr_list']
                 )
                 for key_chk in ['COMINobsproc', 'obs_file', 'tmp_obs2nc_file',
                                 'output_obs2nc_file', 'input_ascii2nc_file']:
                     if key_chk in list(job_env_dict.keys()):
                         job_env_dict.pop(key_chk)
                 for fhr in wmo_verif_fhr_list:
                     init_time_dt = (valid_time_dt
                                     - datetime.timedelta(hours=int(fhr)))
                     if f"{init_time_dt:%H}" not in wmo_init_hour_list:
                         print(f"Skipping forecast hour {fhr} with init "
                               +f"{init_time_dt:%Y%m%d%H} as init hour not in "
                               +"WMO required init hours "
                               +f"{wmo_init_hour_list}")
                         continue
                     # Set forecast input paths
                     # grid2obs_sfc: gaussian grid prepped files
                     fhr_file = gda_util.format_filler(
                         gaussian_file_format, valid_time_dt, init_time_dt,
                         fhr, {}
                     )
                     log_missing_fhr_file = os.path.join(
                         DATA, 'mail_missing_'
                         +fhr_file.rpartition('/')[2].replace('.', '_')+'.sh'
                     )
                     have_fhr = gda_util.check_file_exists_size(fhr_file)
                     if not have_fhr and \
                             not os.path.exists(log_missing_fhr_file):
                         gda_util.log_missing_file_model(
                             log_missing_fhr_file, fhr_file, MODELNAME,
                             init_time_dt, fhr.zfill(3)
                         )
                     # Set forecst output paths
                     tmp_regriddataplane_file = gda_util.format_filler(
                         regriddataplane_file_format, valid_time_dt,
                         init_time_dt, fhr, {}
                     )
                     output_regriddataplane_file = os.path.join(
                         COMOUT, f"{RUN}.{valid_time_dt:%Y%m%d}", MODELNAME,
                         VERIF_CASE, tmp_regriddataplane_file.rpartition('/')[2]
                     )
                     have_fhr_regriddataplane = os.path.exists(
                         output_regriddataplane_file
                     )
                     # Set wmo_verif job variables
                     job_env_dict['fhr'] = fhr
                     job_env_dict['fhr_file'] = fhr_file
                     job_env_dict['tmp_regriddataplane_file'] = (
                         tmp_regriddataplane_file
                     )
                     job_env_dict['output_regriddataplane_file'] = (
                         output_regriddataplane_file
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
                     if have_fhr_regriddataplane:
                         job.write(
                             'if [ -f $output_regriddataplane_file ]; then '
                             +'cp -v $output_regriddataplane_file '
                             +'$tmp_regriddataplane_file; fi\n'
                         )
                         job.write('export err=$?; err_chk')
                     else:
                         job.write(
                             gda_util.metplus_command(
                                 'RegridDataPlane_fcstGFS.conf'
                             )+'\n'
                         )
                         job.write('export err=$?; err_chk\n')
                         job.write(
                            'if [ -f $tmp_regriddataplane_file ]; then '
                            +gda_util.python_command(
                                'global_det_atmos_stats_wmo_add_lat_lon.py',
                                []
                            )+'; fi\n'
                         )
                         job.write('export err=$?; err_chk\n')
                         if SENDCOM == 'YES':
                             job.write(
                                 'if [ -f $tmp_regriddataplane_file ]; then '
                                 +'cp -v $tmp_regriddataplane_file '
                                 +'$output_regriddataplane_file; fi\n'
                             )
                             job.write('export err=$?; err_chk')
elif JOB_GROUP == 'assemble_data':
     # Do not run for grid2grid_upperair, grid2obs_upperair
     wmo_verif_list.remove('grid2grid_upperair')
     wmo_verif_list.remove('grid2obs_upperair')
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
         for vhr in wmo_verif_valid_hour_list:
             valid_time_dt = datetime.datetime.strptime(VDATE+vhr, '%Y%m%d%H')
             pb2nc_file = gda_util.format_filler(
                 prepbufr_pb2nc_file_format, valid_time_dt, valid_time_dt,
                 'anl', {}
             )
             for fhr in wmo_verif_fhr_list:
                 init_time_dt = (valid_time_dt
                                 - datetime.timedelta(hours=int(fhr)))
                 if f"{init_time_dt:%H}" not in wmo_init_hour_list:
                         print(f"Skipping forecast hour {fhr} with init "
                               +f"{init_time_dt:%Y%m%d%H} as init hour not in "
                               +"WMO required init hours "
                               +f"{wmo_init_hour_list}")
                         continue
                 # Set forecast input paths
                 # grid2obs_sfc: regrid_data_plane files
                 fhr_file = gda_util.format_filler(
                     regriddataplane_file_format, valid_time_dt, init_time_dt,
                     fhr, {}
                 )
                 have_fhr = gda_util.check_file_exists_size(fhr_file)
                 # Match TMP/Z2, elevation, latitude, and longitude
                 tmp_fhr_stat_file = gda_util.format_filler(
                     stat_file_format, valid_time_dt, init_time_dt,
                     fhr,
                     {'met_tool': 'point_stat', 'wmo_verif': wmo_verif,
                      'line_type': 'MPR'}
                 )
                 tmp_fhr_elv_correction_stat_file = (
                     tmp_fhr_stat_file.replace(
                         f"point_stat_{wmo_verif}_MPR_",
                         f"point_stat_{wmo_verif}_MPR_elv_correction_"
                     )
                 )
                 output_fhr_stat_file = os.path.join(
                     COMOUT, f"{RUN}.{valid_time_dt:%Y%m%d}", MODELNAME,
                     VERIF_CASE, tmp_fhr_stat_file.rpartition('/')[2]
                 )
                 output_fhr_elv_correction_stat_file = (
                     output_fhr_stat_file.replace(
                         f"point_stat_{wmo_verif}_MPR_",
                         f"point_stat_{wmo_verif}_MPR_elv_correction_"
                     )
                 )
                 have_fhr_stat = os.path.exists(output_fhr_stat_file)
                 have_fhr_elv_correction_stat = (
                     os.path.exists(output_fhr_elv_correction_stat_file)
                 )
                 # Set wmo_verif job variables
                 job_env_dict['valid_date'] = f"{valid_time_dt:%Y%m%d%H}"
                 job_env_dict['pb2nc_file'] = pb2nc_file
                 job_env_dict['fhr'] = fhr
                 job_env_dict['fhr_file'] = fhr_file
                 job_env_dict['tmp_fhr_stat_file'] = tmp_fhr_stat_file
                 job_env_dict['output_fhr_stat_file'] = (
                     output_fhr_stat_file
                 )
                 job_env_dict['tmp_fhr_elv_correction_stat_file'] = (
                     tmp_fhr_elv_correction_stat_file
                 )
                 job_env_dict['output_fhr_elv_correction_stat_file'] = (
                     output_fhr_elv_correction_stat_file
                 )
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
                 if have_fhr_stat and have_fhr_elv_correction_stat:
                     job.write(
                         'if [ -f $output_fhr_stat_file ]; then '
                         +'cp -v $output_fhr_stat_file '
                         +'$tmp_fhr_stat_file; fi\n'
                     )
                     job.write('export err=$?; err_chk\n')
                     job.write(
                         'if [ -f $output_fhr_elv_correction_stat_file ]; '
                         +'then cp -v $output_fhr_elv_correction_stat_file '
                         +'$tmp_fhr_elv_correction_stat_file; fi\n'
                     )
                     job.write('export err=$?; err_chk')
                 elif have_fhr_stat and not have_fhr_elv_correction_stat:
                     job.write(
                         'if [ -f $output_fhr_stat_file ]; then '
                         +'cp -v $output_fhr_stat_file '
                         +'$tmp_fhr_stat_file; fi\n'
                     )
                     job.write('export err=$?; err_chk\n')
                     job.write(
                        'if [ -f $tmp_fhr_stat_file ]; then '
                        +gda_util.python_command('global_det_atmos_stats_'
                                                 +'wmo_elv_correction.py',
                                                 [])
                        +'; fi\n'
                     )
                     job.write('export err=$?; err_chk\n')
                     if SENDCOM == 'YES':
                         job.write(
                             'if [ -f $tmp_fhr_elv_correction_stat_file ]; '
                             +'then cp -v $tmp_fhr_elv_correction_stat_file '
                             +'$output_fhr_elv_correction_stat_file; fi\n'
                         )
                         job.write('export err=$?; err_chk')
                 else:
                     if have_fhr:
                         job.write(
                             gda_util.metplus_command(
                                 'PointStat_fcstGFS_obsADPSFC_MPR.conf'
                             )
                             +'\n'
                         )
                         job.write('export err=$?; err_chk\n')
                         if SENDCOM == 'YES':
                             job.write(
                                 'if [ $tmp_fhr_stat_file ]; then '
                                 +'cp -v $tmp_fhr_stat_file '
                                 +'$output_fhr_stat_file; fi\n'
                             )
                             job.write('export err=$?; err_chk\n')
                         job.write(
                            'if [ -f $tmp_fhr_stat_file ]; then '
                            +gda_util.python_command('global_det_atmos_stats_'
                                                     +'wmo_elv_correction.py',
                                                     [])
                            +'; fi\n'
                         )
                         job.write('export err=$?; err_chk\n')
                         if SENDCOM == 'YES':
                             job.write(
                                 'if [ -f $tmp_fhr_elv_correction_stat_file '
                                 +']; then cp -v '
                                 +'$tmp_fhr_elv_correction_stat_file '
                                 +'$output_fhr_elv_correction_stat_file; '
                                 +'fi\n'
                             )
                             job.write('export err=$?; err_chk')
                 # Make precip accumulations
                 job_env_dict.pop('tmp_fhr_stat_file')
                 job_env_dict.pop('output_fhr_stat_file')
                 job_env_dict.pop('pb2nc_file')
                 job_env_dict.pop('tmp_fhr_elv_correction_stat_file')
                 job_env_dict.pop('output_fhr_elv_correction_stat_file')
                 for accum in [6, 24]:
                     fhr_maccum = int(fhr)-accum
                     if fhr_maccum < 0:
                         continue
                     if int(fhr) % accum != 0:
                         continue
                     fhr_maccum_file = gda_util.format_filler(
                         gaussian_file_format, valid_time_dt, init_time_dt,
                         str(fhr_maccum), {}
                     )
                     log_missing_fhr_maccum_file = os.path.join(
                         DATA, 'mail_missing_'
                         +fhr_maccum_file.rpartition('/')[2].replace('.', '_')
                         +'.sh'
                     )
                     have_fhr_maccum = gda_util.check_file_exists_size(
                         fhr_maccum_file
                     )
                     if not have_fhr_maccum \
                             and not \
                             os.path.exists(log_missing_fhr_maccum_file):
                         gda_util.log_missing_file_model(
                             log_missing_fhr_maccum_file, fhr_maccum_file,
                             MODELNAME, init_time_dt, str(fhr_maccum).zfill(3)
                         )
                     tmp_fhr_accum_pcpcombine_file = gda_util.format_filler(
                         pcpcombine_file_format, valid_time_dt, init_time_dt,
                         fhr, {'accum': str(accum)}
                     )
                     output_fhr_accum_pcpcombine_file = os.path.join(
                         COMOUT, f"{RUN}.{valid_time_dt:%Y%m%d}", MODELNAME,
                         VERIF_CASE,
                         tmp_fhr_accum_pcpcombine_file.rpartition('/')[2]
                     )
                     have_fhr_accum_pcpcombine = (
                         os.path.exists(output_fhr_accum_pcpcombine_file)
                     )
                     # Set wmo_verif job variables
                     job_env_dict['valid_date'] = f"{valid_time_dt:%Y%m%d%H}"
                     job_env_dict['fhr'] = fhr
                     job_env_dict['fhr_file'] = fhr_file
                     job_env_dict['accum'] = str(accum)
                     job_env_dict['fhr_minus_accum_file'] = fhr_maccum_file
                     job_env_dict['tmp_fhr_accum_pcpcombine_file'] = (
                         tmp_fhr_accum_pcpcombine_file
                     )
                     job_env_dict['output_fhr_accum_pcpcombine_file'] = (
                         output_fhr_accum_pcpcombine_file
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
                     # If pcpcombine file exists in COMOUT then copy it
                     # if not then run METplus
                     if have_fhr_accum_pcpcombine:
                         job.write(
                             'if [ -f $output_fhr_accum_pcpcombine_file ]; '
                             +'then cp -v $output_fhr_accum_pcpcombine_file '
                             +'$tmp_fhr_accum_pcpcombine_file; fi\n'
                         )
                         job.write('export err=$?; err_chk')
                     else:
                         if have_fhr and have_fhr_maccum:
                             job.write(
                                 gda_util.metplus_command(
                                     'PCPCombine_fcstGFS.conf'
                                 )
                                 +'\n'
                             )
                             job.write('export err=$?; err_chk\n')
                             if SENDCOM == 'YES':
                                 job.write(
                                     'if [ -f $tmp_fhr_accum_pcpcombine_file '
                                     +']; then cp -v '
                                     +'$tmp_fhr_accum_pcpcombine_file '
                                     +'$output_fhr_accum_pcpcombine_file; fi\n'
                                 )
                                 job.write('export err=$?; err_chk')
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
                 'PointStat_fcstGFS_obsADPUPA_CNT.conf',
                 'PointStat_fcstGFS_obsADPUPA_VCNT.conf'
             ]
             wmo_global_radiosonde_file = os.path.join(
                 FIXevs, 'masks', 'WMO_GLOBAL_radiosondes.txt'
             )
             if os.path.exists(wmo_global_radiosonde_file):
                 with open(wmo_global_radiosonde_file) as wgr:
                     wmo_indiv_radiosondes = (
                         ','.join(wgr.readline().split(' ')[1:])
                     )
         elif wmo_verif == 'grid2obs_sfc':
             wmo_verif_metplus_conf_list = [
                 'PointStat_fcstGFS_obsADPSFC_MCTC.conf',
                 'PointStat_fcstGFS_obsADPSFC_VCNT.conf',
                 'PointStat_fcstGFS_obsADPSFC_CNT.conf',
                 'PointStat_fcstGFS_obsADPSFC_MCTCprecip24H.conf',
                 'PointStat_fcstGFS_obsADPSFC_MCTCprecip6H.conf',
                 'StatAnalysis_fcstGFS_obsADPSFC_MPRtoCNT.conf'
             ]
         for vhr in wmo_verif_valid_hour_list:
             valid_time_dt = datetime.datetime.strptime(VDATE+vhr, '%Y%m%d%H')
             # Set truth input paths
             # grid2grid_upperair: model's own analysis
             # grid2obs_upperair: radiosondes
             # grid2obs_sfc: SYNOP stations
             if wmo_verif == 'grid2grid_upperair':
                 truth_file = gda_util.format_filler(
                     anl_file_format, valid_time_dt, valid_time_dt, 'anl', {}
                 )
             elif wmo_verif == 'grid2obs_upperair':
                 obtype = 'cnvstat'
                 truth_file = gda_util.format_filler(
                     cnvstat_ascii2nc_file_format, valid_time_dt,
                     valid_time_dt, 'anl', {}
                 )
             elif wmo_verif == 'grid2obs_sfc':
                 obtype = 'prepbufr'
                 truth_file = gda_util.format_filler(
                     prepbufr_pb2nc_file_format, valid_time_dt, valid_time_dt,
                     'anl', {}
                 )
                 if os.path.exists(truth_file):
                     pb2nc_data = netcdf.Dataset(truth_file)
                     pb2nc_data_hdr_sid_table = (
                         pb2nc_data.variables['hdr_sid_table'][:]
                     )
                     synop_stations = [i.tobytes(fill_value='/////', order='C')
                                       for i in pb2nc_data_hdr_sid_table]
                     synop_station_list = [''.join(i.decode('UTF-8', 'ignore')\
                                           .replace('/','').split())
                                           for i in synop_stations]
                 else:
                     synop_station_list = []
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
                         log_missing_truth_file, truth_file, obtype,
                         valid_time_dt
                     )
             for fhr in wmo_verif_fhr_list:
                 init_time_dt = (valid_time_dt
                                 - datetime.timedelta(hours=int(fhr)))
                 if f"{init_time_dt:%H}" not in wmo_init_hour_list:
                     print(f"Skipping forecast hour {fhr} with init "
                           +f"{init_time_dt:%Y%m%d%H} as init hour not in "
                           +f"WMO required init hours {wmo_init_hour_list}")
                     continue
                 # Set forecast input paths
                 # grid2grid_upperair: 0.25 degree lat-lon
                 # grid2obs_upperair: gaussian grid prepped files
                 # grid2obs_sfc: gaussian grid prepped files,
                 #               pcpcombine files, and MPR stat files
                 if wmo_verif == 'grid2grid_upperair':
                     fhr_file = gda_util.format_filler(
                         fhr_0p25_file_format, valid_time_dt, init_time_dt,
                         fhr, {}
                     )
                 else:
                     fhr_file = gda_util.format_filler(
                         gaussian_file_format, valid_time_dt, init_time_dt,
                         fhr, {}
                     )
                     if wmo_verif == 'grid2obs_sfc':
                         fhr_stat_elv_correction_file = gda_util.format_filler(
                              stat_file_format, valid_time_dt, init_time_dt,
                              fhr,
                              {'met_tool': 'point_stat',
                               'wmo_verif': wmo_verif, 'line_type': 'MPR'}
                         ).replace(
                             f"point_stat_{wmo_verif}_MPR_",
                             f"point_stat_{wmo_verif}_MPR_elv_correction_"
                         )
                         have_fhr_elv_correction_stat = (
                             os.path.exists(fhr_stat_elv_correction_file)
                         )
                         for accum in [6, 24]:
                             fhr_accum_file = gda_util.format_filler(
                                 pcpcombine_file_format, valid_time_dt,
                                 init_time_dt, fhr, {'accum': str(accum)}
                             )
                             if int(fhr)-accum >= 0 \
                                     and int(fhr) % accum == 0:
                                 have_fhr_accum = (
                                     gda_util.check_file_exists_size(
                                         fhr_accum_file
                                     )
                                 )
                             else:
                                 have_fhr_accum = False
                             if accum == 6:
                                 have_fhr_accum6H = have_fhr_accum
                                 fhr_accum6H_file = fhr_accum_file
                             elif accum == 24:
                                 have_fhr_accum24H = have_fhr_accum
                                 fhr_accum24H_file = fhr_accum_file
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
                     # grid2obs_sfc: point_stat and stat_analysis
                     wmo_verif_metplus_conf_line_type = (
                         wmo_verif_metplus_conf.rpartition('_')[2]\
                         .replace('.conf', '')
                     )
                     if wmo_verif_metplus_conf_line_type == 'MCTCprecip6H':
                         fhr_file = fhr_accum6H_file
                         have_fhr = have_fhr_accum6H
                     elif wmo_verif_metplus_conf_line_type == 'MCTCprecip24H':
                         fhr_file = fhr_accum24H_file
                         have_fhr = have_fhr_accum24H
                     elif wmo_verif_metplus_conf_line_type == 'MPRtoCNT':
                         fhr_file = fhr_stat_elv_correction_file
                         have_fhr =  have_fhr_elv_correction_stat
                     if wmo_verif == 'grid2grid_upperair':
                         met_tool = 'grid_stat'
                     else:
                         if wmo_verif_metplus_conf_line_type == 'MPRtoCNT':
                             met_tool = 'stat_analysis'
                         else:
                             met_tool = 'point_stat'
                     tmp_fhr_stat_file = gda_util.format_filler(
                         stat_file_format, valid_time_dt, init_time_dt,
                         fhr,
                         {'met_tool': met_tool,
                          'wmo_verif': wmo_verif,
                          'line_type': wmo_verif_metplus_conf_line_type}
                     )
                     output_fhr_stat_file = os.path.join(
                         COMOUT, f"{RUN}.{valid_time_dt:%Y%m%d}", MODELNAME,
                         VERIF_CASE, tmp_fhr_stat_file.rpartition('/')[2]
                     )
                     have_fhr_stat = os.path.exists(output_fhr_stat_file)
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
                         job_env_dict['wmo_indiv_radiosondes'] = (
                             wmo_indiv_radiosondes
                         )
                     elif wmo_verif == 'grid2obs_sfc':
                         job_env_dict['pb2nc_file'] = truth_file
                         job_env_dict['synop_stations'] = (
                             ','.join(synop_station_list)
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
    job_env_dict['valid_date'] = VDATE
    metplus_conf_list = [
        'filter', 'filter_station_info'
    ]
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
    tmp_stat_file = gda_util.format_filler(
        daily_stat_file_format,
        datetime.datetime.strptime(VDATE, '%Y%m%d'),
        datetime.datetime.strptime(VDATE, '%Y%m%d'),
        'anl', {}
    )
    tmp_stat_station_file = tmp_stat_file.replace(
        '.wmo.', '.wmo.station_info.'
    )
    output_stat_file = os.path.join(
        COMOUT, f"{MODELNAME}.{VDATE}", tmp_stat_file.rpartition('/')[2]
    )
    output_stat_station_file = os.path.join(
        COMOUT, f"{MODELNAME}.{VDATE}",
        tmp_stat_station_file.rpartition('/')[2]
    )
    for metplus_conf in metplus_conf_list:
        if metplus_conf == 'filter':
            job_env_dict['tmp_stat_file'] = tmp_stat_file
            job_env_dict['output_stat_file'] = output_stat_file
            have_stat = os.path.exists(output_stat_file)
        elif metplus_conf == 'filter_station_info':
            job_env_dict['tmp_stat_file'] = tmp_stat_station_file
            job_env_dict['tmp_stat_unfiltered_file'] = (
                tmp_stat_station_file.replace(
                    '.station_info.', '.station_info.unfiltered.'
                )
            )
            job_env_dict['output_stat_file'] = output_stat_station_file
            have_stat = os.path.exists(output_stat_station_file)
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
                    gda_util.metplus_command('StatAnalysis_fcstGFS_'
                                             +f"{metplus_conf}.conf")
                    +'\n'
                )
                job.write('export err=$?; err_chk\n')
                if metplus_conf == 'filter_station_info':
                    job.write(
                        gda_util.python_command('global_det_atmos_stats_wmo_'
                                                +'filter_stations.py', [])
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
