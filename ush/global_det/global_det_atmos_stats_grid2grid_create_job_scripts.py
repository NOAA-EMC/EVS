'''
Program Name: global_det_atmos_stats_grid2grid_create_job_scripts.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This creates multiple independent job scripts. These
          jobs contain all the necessary environment variables
          and METplus commands to needed to run the specific
          use case.
'''

import sys
import os
import glob
import datetime
import numpy as np
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
METPLUS_PATH = os.environ['METPLUS_PATH']
MET_ROOT = os.environ['MET_ROOT']
MET_bin_exec = os.environ['MET_bin_exec']
PARMevs = os.environ['PARMevs']
model_list = os.environ['model_list'].split(' ')

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
################################################
#### Reformat jobs
################################################
reformat_obs_jobs_dict = {
    'flux': {},
    'means': {},
    'ozone': {},
    'precip': {
        '24hrCCPA': {'env': {},
                     'commands': [gda_util.metplus_command(
                                      'PCPCombine_obs24hrCCPA.conf'
                                  )]}
    },
    'pres_levs': {},
    'sea_ice': {},
    'snow': {},
    'sst': {},
}
reformat_model_jobs_dict = {
    'flux': {
        'DailyAvg_LatentHeat': {'env': {'var1_name': 'LHTFL',
                                        'var1_levels': 'Z0',
                                        'valid_hr_start': '00',
                                        'valid_hr_end': '00',
                                        'valid_hr_inc': '24'},
                                 'commands': [gda_util.metplus_command(
                                                  'GridStat_fcstGLOBAL_DET_'
                                                  +'NetCDF.conf'
                                              ),
                                              gda_util.python_command(
                                                  'global_det_atmos_stats_grid2grid'
                                                  '_create_daily_avg.py',
                                                  ['LHTFL_Z0',
                                                   os.path.join(
                                                       '$DATA',
                                                       '${VERIF_CASE}_${STEP}',
                                                       'METplus_output',
                                                       '${RUN}.{valid?fmt=%Y%m%d}',
                                                       '$MODEL', '$VERIF_CASE',
                                                       'grid_stat_${VERIF_TYPE}.'
                                                       +'${job_name}_'
                                                       +'{lead?fmt=%2H}0000L_'
                                                       +'{valid?fmt=%Y%m%d}_'
                                                       +'{valid?fmt=%H}0000V_pairs.nc'
                                                   )]
                                              )]},

        'DailyAvg_SensibleHeat': {'env': {'var1_name': 'SHTFL',
                                          'var1_levels': 'Z0',
                                          'valid_hr_start': '00',
                                          'valid_hr_end': '00',
                                          'valid_hr_inc': '24'},
                                  'commands': [gda_util.metplus_command(
                                                   'GridStat_fcstGLOBAL_DET_'
                                                   +'NetCDF.conf'
                                               ),
                                               gda_util.python_command(
                                                  'global_det_atmos_stats_grid2grid'
                                                  '_create_daily_avg.py',
                                                  ['SHTFL_Z0',
                                                   os.path.join(
                                                       '$DATA',
                                                       '${VERIF_CASE}_${STEP}',
                                                       'METplus_output',
                                                       '${RUN}.{valid?fmt=%Y%m%d}',
                                                       '$MODEL', '$VERIF_CASE',
                                                       'grid_stat_${VERIF_TYPE}.'
                                                       +'${job_name}_'
                                                       +'{lead?fmt=%2H}0000L_'
                                                       +'{valid?fmt=%Y%m%d}_'
                                                       +'{valid?fmt=%H}0000V_pairs.nc'
                                                   )]
                                               )]}
    },
    'means': {},
    'ozone': {},
    'precip': {
        '24hrAccum': {'env': {'valid_hr': '12'},
                      'commands': [gda_util.metplus_command(
                                       'PCPCombine_fcstGLOBAL_DET_'
                                       +'24hrAccum_precip.conf'
                                   )]}
    },
    'pres_levs': {
        'DailyAvg_GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                           'var1_levels': 'P500',
                                           'met_config_overrides': (
                                              "'climo_mean = fcst;'"
                                           )},
                                   'commands': [gda_util.metplus_command(
                                                    'GridStat_fcstGLOBAL_DET_'
                                                    +'obsModelAnalysis_climoERAI_'
                                                    +'NetCDF.conf'
                                                ),
                                                gda_util.python_command(
                                                  'global_det_atmos_stats_grid2grid'
                                                  '_create_anomaly.py',
                                                   ['HGT_P500',
                                                    os.path.join(
                                                        '$DATA',
                                                        '${VERIF_CASE}_${STEP}',
                                                        'METplus_output',
                                                        '${RUN}.{valid?fmt=%Y%m%d}',
                                                        '$MODEL', '$VERIF_CASE',
                                                        'grid_stat_${VERIF_TYPE}.'
                                                        +'${job_name}_'
                                                        +'{lead?fmt=%2H}0000L_'
                                                        +'{valid?fmt=%Y%m%d}_'
                                                        +'{valid?fmt=%H}0000V_pairs.nc'
                                                    )]
                                                ),
                                                gda_util.python_command(
                                                  'global_det_atmos_stats_grid2grid'
                                                  '_create_daily_avg.py',
                                                   ['HGT_ANOM_P500',
                                                    os.path.join(
                                                        '$DATA',
                                                        '${VERIF_CASE}_${STEP}',
                                                        'METplus_output',
                                                        '${RUN}.{valid?fmt=%Y%m%d}',
                                                        '$MODEL', '$VERIF_CASE',
                                                        'anomaly_${VERIF_TYPE}.'
                                                        +'${job_name}_init'
                                                        +'{init?fmt=%Y%m%d%H}_'
                                                        +'fhr{lead?fmt=%3H}.nc'
                                                    )]
                                                )]}
    },
    'sea_ice': {},
    'snow': {
        '24hrAccum_WaterEqv': {'env': {'valid_hr': '12',
                                       'MODEL_var': 'WEASD'},
                               'commands': [gda_util.metplus_command(
                                                'PCPCombine_fcstGLOBAL_'
                                                +'DET_24hrAccum_snow.conf'
                                            )]},
        '24hrAccum_Depth': {'env': {'valid_hr': '12',
                                    'MODEL_var': 'SNOD'},
                            'commands': [gda_util.metplus_command(
                                             'PCPCombine_fcstGLOBAL_'
                                             +'DET_24hrAccum_snow.conf'
                                         )]}
    },
    'sst': {},
}

# Create reformat jobs directory
njobs = 0
reformat_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                 'reformat')
if not os.path.exists(reformat_jobs_dir):
    os.makedirs(reformat_jobs_dir)
for verif_type in VERIF_CASE_STEP_type_list:
    VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                   +verif_type)
    verif_type_reformat_obs_jobs_dict = (
        reformat_obs_jobs_dict[verif_type]
    )
    verif_type_reformat_model_jobs_dict = (
        reformat_model_jobs_dict[verif_type]
    )
    # Read in environment variables for verif_type
    if verif_type == 'precip':
        precip_file_accum_list = (os.environ \
            [VERIF_CASE_STEP_abbrev+'_precip_file_accum_list'] \
        .split(' '))
        precip_var_list = (os.environ \
            [VERIF_CASE_STEP_abbrev+'_precip_var_list'] \
        .split(' '))
    # Reformat obs jobs
    for verif_type_job in list(verif_type_reformat_obs_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, 'reformat',
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        # Add job specific environment variables
        for verif_type_job_env_var in \
                list(verif_type_reformat_obs_jobs_dict\
                     [verif_type_job]['env'].keys()):
            job_env_dict[verif_type_job_env_var] = (
                verif_type_reformat_obs_jobs_dict\
                [verif_type_job]['env'][verif_type_job_env_var]
            )
        verif_type_job_commands_list = (
            verif_type_reformat_obs_jobs_dict\
            [verif_type_job]['commands']
        )
        # Loop through and write job script for dates
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
            njobs+=1
            # Create job file
            job_file = os.path.join(reformat_jobs_dir, 'job'+str(njobs))
            print("Creating job script: "+job_file)
            job = open(job_file, 'w')
            job.write('#!/bin/sh\n')
            job.write('set -x\n')
            job.write('\n')
            # Set any environment variables for special cases
            # Write environment variables
            for name, value in job_env_dict.items():
                job.write('export '+name+'='+value+'\n')
            job.write('\n')
            # Write job commands
            for cmd in verif_type_job_commands_list:
                job.write(cmd+'\n')
            job.close()
            date_dt = date_dt + datetime.timedelta(days=1)
    # Reformat model jobs
    for verif_type_job in list(verif_type_reformat_model_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, 'reformat',
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        # Add job specific environment variables
        for verif_type_job_env_var in \
                list(verif_type_reformat_model_jobs_dict\
                     [verif_type_job]['env'].keys()):
            job_env_dict[verif_type_job_env_var] = (
                verif_type_reformat_model_jobs_dict\
                [verif_type_job]['env'][verif_type_job_env_var]
            )
        verif_type_job_commands_list = (
            verif_type_reformat_model_jobs_dict\
            [verif_type_job]['commands']
        )
        # Loop through and write job script for dates and models
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
            for model_idx in range(len(model_list)):
                job_env_dict['MODEL'] = model_list[model_idx]
                njobs+=1
                # Create job file
                job_file = os.path.join(reformat_jobs_dir, 'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/sh\n')
                job.write('set -x\n')
                job.write('\n')
                # Set any environment variables for special cases
                if verif_type == 'pres_levs':
                    job_env_dict['TRUTH'] = os.environ[
                        VERIF_CASE_STEP_abbrev_type+'_truth_name_list'
                    ].split(' ')[model_idx]
                if verif_type in ['flux', 'pres_levs']:
                    job_env_dict['netCDF_ENDDATE'] = date_dt.strftime('%Y%m%d')
                    job_env_dict['netCDF_STARTDATE'] = (
                        (date_dt - datetime.timedelta(days=1))\
                        .strftime('%Y%m%d')
                    )
                    netCDF_fhr_start = int(job_env_dict['fhr_start']) - 18
                    if netCDF_fhr_start > 0:
                        job_env_dict['netCDF_fhr_start'] = str(netCDF_fhr_start)
                    else:
                        job_env_dict['netCDF_fhr_start'] = (
                            job_env_dict['fhr_start']
                        )
                elif verif_type == 'precip':
                    job_env_dict['MODEL_var'] = precip_var_list[model_idx]
                    if precip_file_accum_list[model_idx] == 'continuous':
                        job_env_dict['pcp_combine_method'] = 'SUBTRACT'
                        job_env_dict['MODEL_accum'] = '{lead?fmt=%HH}'
                        job_env_dict['MODEL_levels'] = 'A{lead?fmt=%HH}'
                    else:
                        job_env_dict['pcp_combine_method'] = 'SUM'
                        job_env_dict['MODEL_accum'] = (
                            precip_file_accum_list[model_idx]
                        )
                        job_env_dict['MODEL_levels'] = (
                            'A'+job_env_dict['MODEL_accum']
                        )
                # Write environment variables
                for name, value in job_env_dict.items():
                    job.write('export '+name+'='+value+'\n')
                job.write('\n')
                # Write job commands
                for cmd in verif_type_job_commands_list:
                    job.write(cmd+'\n')
                job.close()
            date_dt = date_dt + datetime.timedelta(days=1)

################################################
#### Generate jobs
################################################
# Generate jobs information dictionary
generate_jobs_dict = {
    'flux': {
        'DailyAvg_LatentHeat': {'env': {'fcst_var1_name': 'LHTFL',
                                        'obs_var1_name': 'ET',
                                        'obs_conversion': ("'2.45 * 1000000 "
                                                           +"/ 86400'")},
                                'commands': [gda_util.metplus_command(
                                                 'GridStat_fcstGLOBAL_DET'
                                                 +'_obsGET_D.conf'
                                             )]},
        'DailyAvg_SensibleHeat': {'env': {'fcst_var1_name': 'SHTFL',
                                           'obs_var1_name': 'HDAY',
                                           'obs_conversion': "'1000000 / 86400'"},
                                  'commands': [gda_util.metplus_command(
                                                   'GridStat_fcstGLOBAL_DET'
                                                   +'_obsGET_D.conf'
                                               )]},
    },
    'means': {
        'CAPESfcBased': {'env': {'var1_name': 'CAPE',
                                 'var1_level': 'Z0',
                                  'var1_options': ''},
                         'commands': [gda_util.metplus_command(
                                          'GridStat_fcstGLOBAL_DET.conf'
                                      )]},
        'CloudWater': {'env': {'var1_name': 'CWAT',
                               'var1_level': 'L0',
                               'var1_options': ''},
                       'commands': [gda_util.metplus_command(
                                        'GridStat_fcstGLOBAL_DET.conf'
                                    )]},
        'GeoHeightTropopause': {'env': {'var1_name': 'HGT',
                                        'var1_level': 'L0',
                                        'var1_options': ("'GRIB_lvl_typ = 7; "
                                                         +'set_attr_level = '
                                                         +'"Tropopause";'+"'")},
                                'commands': [gda_util.metplus_command(
                                                 'GridStat_fcstGLOBAL_DET.conf'
                                             )]},
        'PBLHeight': {'env': {'var1_name': 'HPBL',
                              'var1_level': 'L0',
                              'var1_options': ''},
                      'commands': [gda_util.metplus_command(
                                       'GridStat_fcstGLOBAL_DET.conf'
                                   )]},
        'PrecipWater': {'env': {'var1_name': 'PWAT',
                                'var1_level': 'L0',
                                'var1_options': ''},
                        'commands': [gda_util.metplus_command(
                                         'GridStat_fcstGLOBAL_DET.conf'
                                     )]},
        'PresSeaLevel': {'env': {'var1_name': 'PRMSL',
                                 'var1_level': 'Z0',
                                 'var1_options': ''},
                         'commands': [gda_util.metplus_command(
                                          'GridStat_fcstGLOBAL_DET.conf'
                                      )]},
        'PresSfc': {'env': {'var1_name': 'PRES',
                            'var1_level': 'Z0',
                            'var1_options': ''},
                    'commands': [gda_util.metplus_command(
                                     'GridStat_fcstGLOBAL_DET.conf'
                                 )]},
        'PresTropopause': {'env': {'var1_name': 'PRES',
                                   'var1_level': 'L0',
                                   'var1_options': ("'GRIB_lvl_typ = 7; "
                                                    +'set_attr_level = '
                                                    +'"Tropopause";'+"'")},
                           'commands': [gda_util.metplus_command(
                                            'GridStat_fcstGLOBAL_DET.conf'
                                        )]},
        'RelHum2m': {'env': {'var1_name': 'RH',
                             'var1_level': 'Z2',
                             'var1_options': ''},
                     'commands': [gda_util.metplus_command(
                                      'GridStat_fcstGLOBAL_DET.conf'
                                  )]},
        'SnowWaterEqv': {'env': {'var1_name': 'WEASD',
                                 'var1_level': 'Z0',
                                 'var1_options': ''},
                         'commands': [gda_util.metplus_command(
                                          'GridStat_fcstGLOBAL_DET.conf'
                                      )]},
        'SpefHum2m': {'env': {'var1_name': 'SPFH',
                              'var1_level': 'Z2',
                              'var1_options': ''},
                      'commands': [gda_util.metplus_command(
                                       'GridStat_fcstGLOBAL_DET.conf'
                                   )]},
        'Temp2m': {'env': {'var1_name': 'TMP',
                           'var1_level': 'Z2',
                           'var1_options': ''},
                   'commands': [gda_util.metplus_command(
                                    'GridStat_fcstGLOBAL_DET.conf'
                                )]},
        'TempTropopause': {'env': {'var1_name': 'TMP',
                                   'var1_level': 'L0',
                                   'var1_options': ("'GRIB_lvl_typ = 7; "
                                                    +'set_attr_level = '
                                                    +'"Tropopause";'+"'")},
                           'commands': [gda_util.metplus_command(
                                            'GridStat_fcstGLOBAL_DET.conf'
                                        )]},
        'TempSoilTopLayer': {'env': {'var1_name': 'TSOIL',
                                     'var1_level': 'Z0-0.1',
                                     'var1_options': ''},
                             'commands': [gda_util.metplus_command(
                                              'GridStat_fcstGLOBAL_DET.conf'
                                          )]},
        'TotalOzone': {'env': {'var1_name': 'TOZNE',
                               'var1_level': 'L0',
                               'var1_options': ''}, 
                      'commands': [gda_util.metplus_command(
                                       'GridStat_fcstGLOBAL_DET.conf'
                                   )]},
        'UWind10m': {'env': {'var1_name': 'UGRD',
                             'var1_level': 'Z10',
                             'var1_options': ''},
                     'commands': [gda_util.metplus_command(
                                      'GridStat_fcstGLOBAL_DET.conf'
                                  )]},
        'VolSoilMoistTopLayer': {'env': {'var1_name': 'SOILW',
                                         'var1_level': 'Z0-0.1',
                                         'var1_options': ''},
                                 'commands': [gda_util.metplus_command(
                                                  'GridStat_fcstGLOBAL_DET.conf'
                                              )]},
        'VWind10m': {'env': {'var1_name': 'VGRD',
                             'var1_level': 'Z10',
                             'var1_options': ''},
                     'commands': [gda_util.metplus_command(
                                      'GridStat_fcstGLOBAL_DET.conf'
                                  )]},
    },
    'ozone': {
        'Ozone': {'env': {},
                  'commands': []},
    },
    'precip': {
        '24hrCCPA_G211_mm': {'env': {'grid': 'G211',
                                     'units': "'"+'"mm"'+"'",
                                     'thresh_list': ("'>0.1, >0.5, >1, >5, "
                                                     +">10, >25, >50, >75'"),
                                     'met_config_overrides': ''},
                             'commands': [gda_util.metplus_command(
                                              'GridStat_fcstGLOBAL_DET_'
                                              +'obs24hrCCPA.conf'
                                          )]},
        '24hrCCPA_G211_in': {'env': {'grid': 'G211',
                                     'units': "'"+'"in"'+"'",
                                     'thresh_list': ("'>0.01, >0.1, >0.25, "
                                                     +">0.5, >1, >2, >3'"),
                                     'met_config_overrides': ("'convert(x) = "
                                                              +"MM_to_IN(x);'")},
                             'commands': [gda_util.metplus_command(
                                              'GridStat_fcstGLOBAL_DET_'
                                              +'obs24hrCCPA.conf'
                                          )]},
        '24hrCCPA_G212_mm': {'env': {'grid': 'G212',
                                     'units': "'"+'"mm"'+"'",
                                     'thresh_list': ("'>0.1, >0.5, >1, >5, "
                                                     +">10, >25, >50, >75'"),
                                     'met_config_overrides': ''},
                             'commands': [gda_util.metplus_command(
                                              'GridStat_fcstGLOBAL_DET_'
                                              +'obs24hrCCPA.conf'
                                          )]},
        '24hrCCPA_G212_in': {'env': {'grid': 'G212',
                                     'units': "'"+'"in"'+"'",
                                     'thresh_list': ("'>0.01, >0.1, >0.25, "
                                                     +">0.5, >1, >2, >3'"),
                                     'met_config_overrides': ("'convert(x) = "
                                                              +"MM_to_IN(x);'")},
                             'commands': [gda_util.metplus_command(
                                              'GridStat_fcstGLOBAL_DET_'
                                              +'obs24hrCCPA.conf'
                                          )]},
        '24hrCCPA_G218_mm': {'env': {'grid': 'G218',
                                     'units': "'"+'"mm"'+"'",
                                     'thresh_list': ("'>0.1, >0.5, >1, >5, "
                                                     +">10, >25, >50, >75'"),
                                     'met_config_overrides': ''},
                             'commands': [gda_util.metplus_command(
                                              'GridStat_fcstGLOBAL_DET_'
                                              +'obs24hrCCPA.conf'
                                          )]},
        '24hrCCPA_G218_in': {'env': {'grid': 'G218',
                                     'units': "'"+'"in"'+"'",
                                     'thresh_list': ("'>0.01, >0.1, >0.25, "
                                                     +">0.5, >1, >2, >3'"),
                                     'met_config_overrides': ("'convert(x) = "
                                                              +"MM_to_IN(x);'")},
                             'commands': [gda_util.metplus_command(
                                              'GridStat_fcstGLOBAL_DET_'
                                              +'obs24hrCCPA.conf'
                                          )]},
        '24hrCCPA_Nbrhd_mm': {'env': {'units': "'"+'"mm"'+"'",
                                      'thresh_list': ("'>0.1, >0.5, >1, >5, "
                                                      +">10, >25, >50, >75'"),
                                      'met_config_overrides': ''},
                              'commands': [gda_util.metplus_command(
                                               'GridStat_fcstGLOBAL_DET_'
                                               +'obs24hrCCPA_Nbrhd.conf'
                                           )]},
        '24hrCCPA_Nbrhd_in': {'env': {'units': "'"+'"in"'+"'",
                                      'thresh_list': ("'>0.01, >0.1, >0.25, "
                                                      +">0.5, >1, >2, >3'"),
                                      'met_config_overrides': ("'convert(x) = "
                                                               +"MM_to_IN(x);'")},
                              'commands': [gda_util.metplus_command(
                                               'GridStat_fcstGLOBAL_DET_'
                                               +'obs24hrCCPA_Nbrhd.conf'
                                           )]},
    },
    'pres_levs': {
        'GeoHeight': {'env': {'var1_name': 'HGT',
                              'var1_levels': "'P1000, P700, P250'",
                              'met_config_overrides': "'climo_mean = fcst;'"},
                      'commands': [gda_util.metplus_command(
                                       'GridStat_fcstGLOBAL_DET_'
                                       +'obsModelAnalysis_climoERAI.conf'
                                   )]},
        'GeoHeight_FourierDecomp': {'env': {'var1_name': 'HGT',
                                            'var1_levels': 'P500',
                                            'met_config_overrides': ("'climo_"
                                                                     +"mean = "
                                                                     +"fcst;'")},
                                    'commands': [gda_util.metplus_command(
                                                     'GridStat_fcstGLOBAL_DET_'
                                                     +'obsModelAnalysis_'
                                                     +'climoERAI_FourierDecomp'
                                                     +'.conf'
                                                 )]},
        'DailyAvg_GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                           'var1_levels': 'P500',
                                           'met_config_overrides': (
                                               "'climo_mean = fcst;'"
                                           )},
                                   'commands': [gda_util.metplus_command(
                                                    'GridStat_fcstGLOBAL_DET_'
                                                    +'obsModelAnalysis_DailyAvgAnom'
                                                    +'.conf'
                                                )]},
        'PresSeaLevel': {'env': {'var1_name': 'PRMSL',
                                 'var1_levels': 'Z0',
                                 'met_config_overrides': "'climo_mean = fcst;'"},
                         'commands': [gda_util.metplus_command(
                                          'GridStat_fcstGLOBAL_DET_'
                                          +'obsModelAnalysis_climoERAI.conf'
                                      )]},
        'Temp': {'env': {'var1_name': 'TMP',
                         'var1_levels': "'P850, P500, P250'",
                         'met_config_overrides': "'climo_mean = fcst;'"},
                 'commands': [gda_util.metplus_command(
                                  'GridStat_fcstGLOBAL_DET_'
                                  +'obsModelAnalysis_climoERAI.conf'
                              )]},
        'Winds': {'env': {'var1_name': 'UGRD',
                          'var1_levels': "'P850, P500, P250'",
                          'var2_name': 'VGRD',
                          'var2_levels': "'P850, P500, P250'",
                          'met_config_overrides': "'climo_mean = fcst;'"},
                  'commands': [gda_util.metplus_command(
                                   'GridStat_fcstGLOBAL_DET_'
                                   +'obsModelAnalysis_climoERAI_Winds.conf'
                               )]},
    },
    'sea_ice': {
        'Concentration': {'env': {},
                          'commands': []},
        'Thickness': {'env': {},
                      'commands': []},
        'Extent': {'env': {},
                   'commands': []},
        'Volume': {'env': {},
                   'commands': []},
    },
    'snow': {
        '24hrNOHRSC_WaterEqv_G211': {'env': {'grid': 'G211',
                                             'file_name_var': 'WaterEqv',
                                             'var1_name': 'WEASD',
                                             'var1_convert': '2.54'},
                                     'commands': [gda_util.metplus_command(
                                                      'GridStat_fcstGLOBAL_DET_'
                                                      +'obs24hrNOHRSC.conf'
                                                  )]},
        '24hrNOHRSC_Depth_G211': {'env': {'grid': 'G211',
                                          'file_name_var': 'Depth',
                                          'var1_name': 'SNOD',
                                          'var1_convert': '25.4'},
                                  'commands': [gda_util.metplus_command(
                                                   'GridStat_fcstGLOBAL_DET_'
                                                   +'obs24hrNOHRSC.conf'
                                               )]},
        '24hrNOHRSC_WaterEqv_G212': {'env': {'grid': 'G212',
                                             'file_name_var': 'WaterEqv',
                                             'var1_name': 'WEASD',
                                             'var1_convert': '2.54'},
                                     'commands': [gda_util.metplus_command(
                                                      'GridStat_fcstGLOBAL_DET_'
                                                      +'obs24hrNOHRSC.conf'
                                                  )]},
        '24hrNOHRSC_Depth_G212': {'env': {'grid': 'G212',
                                          'file_name_var': 'Depth',
                                          'var1_name': 'SNOD',
                                          'var1_convert': '25.4'},
                                  'commands': [gda_util.metplus_command(
                                                   'GridStat_fcstGLOBAL_DET_'
                                                   +'obs24hrNOHRSC.conf'
                                               )]},
        '24hrNOHRSC_WaterEqv_G218': {'env': {'grid': 'G218',
                                             'file_name_var': 'WaterEqv',
                                             'var1_name': 'WEASD',
                                             'var1_convert': '2.54'},
                                     'commands': [gda_util.metplus_command(
                                                      'GridStat_fcstGLOBAL_DET_'
                                                      +'obs24hrNOHRSC.conf'
                                                  )]},
        '24hrNOHRSC_Depth_G218': {'env': {'grid': 'G218',
                                          'file_name_var': 'Depth',
                                          'var1_name': 'SNOD',
                                          'var1_convert': '25.4'},
                                  'commands': [gda_util.metplus_command(
                                                   'GridStat_fcstGLOBAL_DET_'
                                                   +'obs24hrNOHRSC.conf'
                                               )]},
        '24hrNOHRSC_WaterEqv_Nbrhd': {'env': {'file_name_var': 'WaterEqv',
                                              'var1_name': 'WEASD',
                                              'var1_convert': '2.54'},
                                      'commands': [gda_util.metplus_command(
                                                      'GridStat_fcstGLOBAL_DET_'
                                                      +'obs24hrNOHRSC_Nbrhd.conf'
                                                  )]},
        '24hrNOHRSC_Depth_Nbrhd': {'env': {'file_name_var': 'Depth',
                                           'var1_name': 'SNOD',
                                           'var1_convert': '25.4'},
                                   'commands': [gda_util.metplus_command(
                                                    'GridStat_fcstGLOBAL_DET_'
                                                    +'obs24hrNOHRSC_Nbrhd.conf'
                                                )]},
    },
    'sst': {
        'TempSeaSfc': {'env': {},
                       'commands': []},
    },
}
# Create generate jobs directory
njobs = 0
generate_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                 'generate')
if not os.path.exists(generate_jobs_dir):
    os.makedirs(generate_jobs_dir)
for verif_type in VERIF_CASE_STEP_type_list:
    VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                   +verif_type)
    verif_type_generate_jobs_dict = generate_jobs_dict[verif_type]
    # Generate model jobs
    for verif_type_job in list(verif_type_generate_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, 'generate',
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        # Add job specific environment variables
        for verif_type_job_env_var in \
                list(verif_type_generate_jobs_dict\
                     [verif_type_job]['env'].keys()):
            job_env_dict[verif_type_job_env_var] = (
                verif_type_generate_jobs_dict\
                [verif_type_job]['env'][verif_type_job_env_var]
            )
        verif_type_job_commands_list = (
            verif_type_generate_jobs_dict\
            [verif_type_job]['commands']
        )
        # Loop through and write job script for dates and models
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
            for model_idx in range(len(model_list)):
                job_env_dict['MODEL'] = model_list[model_idx]
                njobs+=1
                # Create job file
                job_file = os.path.join(generate_jobs_dir, 'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/sh\n')
                job.write('set -x\n')
                job.write('\n')
                # Set any environment variables for special cases
                if verif_type == 'pres_levs':
                    job_env_dict['TRUTH'] = os.environ[
                        VERIF_CASE_STEP_abbrev_type+'_truth_name_list' 
                    ].split(' ')[model_idx]
                # Write environment variables
                for name, value in job_env_dict.items():
                    job.write('export '+name+'='+value+'\n')
                job.write('\n')
                # Write job commands
                for cmd in verif_type_job_commands_list:
                    job.write(cmd+'\n')
                job.close()
            date_dt = date_dt + datetime.timedelta(days=1)

################################################
#### Gather jobs
################################################
# Gather jobs information dictionary
gather_jobs_dict = {'env': {},
                    'commands': [gda_util.metplus_command(
                                     'StatAnalysis_fcstGLOBAL_DET.conf'
                                 )]}
njobs = 0
gather_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                               'gather')
if not os.path.exists(gather_jobs_dir):
    os.makedirs(gather_jobs_dir)
# Initialize job environment dictionary
job_env_dict = gda_util.initalize_job_env_dict(
    verif_type, 'gather',
    VERIF_CASE_STEP_abbrev_type, verif_type_job
)
# Loop through and write job script for dates and models
date_dt = start_date_dt
while date_dt <= end_date_dt:
    job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
    for model_idx in range(len(model_list)):
        job_env_dict['MODEL'] = model_list[model_idx]
        njobs+=1
        # Create job file
        job_file = os.path.join(gather_jobs_dir, 'job'+str(njobs))
        print("Creating job script: "+job_file)
        job = open(job_file, 'w')
        job.write('#!/bin/sh\n')
        job.write('set -x\n')
        job.write('\n')
        # Set any environment variables for special cases
        # Write environment variables
        for name, value in job_env_dict.items():
            job.write('export '+name+'='+value+'\n')
        job.write('\n')
        # Write job commands
        for cmd in gather_jobs_dict['commands']:
            job.write(cmd+'\n')
            job.close()
    date_dt = date_dt + datetime.timedelta(days=1)

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    for group in ['reformat', 'generate', 'gather']:
        job_files = glob.glob(os.path.join(DATA, VERIF_CASE_STEP,
                                           'METplus_job_scripts', group,
                                           'job*'))
        njob_files = len(job_files)
        if njob_files == 0:
            print("ERROR: No job files created in "
                  +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                group))
            continue
        njob, iproc, node = 1, 0, 1
        while njob <= njob_files:
            job = 'job'+str(njob)
            if machine in ['HERA', 'ORION', 'S4', 'JET']:
                if iproc >= int(nproc):
                    poe_file.close()
                    iproc = 0
                    node+=1
            poe_filename = os.path.join(DATA, VERIF_CASE_STEP,
                                        'METplus_job_scripts',
                                        group, 'poe_jobs'+str(node))
            if iproc == 0:
                poe_file = open(poe_filename, 'w')
            iproc+=1
            if machine in ['HERA', 'ORION', 'S4', 'JET']:
                poe_file.write(
                    str(iproc-1)+' '
                    +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                  group, job)+'\n'
                )
            else:
                poe_file.write(
                    os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                 group, job)+'\n'
                )
            njob+=1
        poe_file.close()
        # If at final record and have not reached the
        # final processor then write echo's to
        # poe script for remaining processors
        poe_file = open(poe_filename, 'a')
        iproc+=1
        while iproc <= int(nproc):
            if machine in ['HERA', 'ORION', 'S4', 'JET']:
                poe_file.write(
                    str(iproc-1)+' /bin/echo '+str(iproc)+'\n'
                )
            else:
                poe_file.write(
                    '/bin/echo '+str(iproc)+'\n'
                )
            iproc+=1
    poe_file.close()

print("END: "+os.path.basename(__file__))
