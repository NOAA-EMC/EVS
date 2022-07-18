'''
Program Name: global_det_atmos_stats_grid2obs_create_job_scripts.py
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
    'pres_levs': {
        'PrepbufrGDAS': {'env': {'prepbufr': 'gdas',
                                 'obs_window': '1800',
                                 'msg_type': "'ADPUPA, AIRCAR, AIRCFT'",
                                 'obs_bufr_var_list': ("'ZOB, UOB, VOB, TOB, "
                                                       +"QOB, D_RH'")},
                         'commands': [gda_util.metplus_command(
                                          'PB2NC_obsPrepbufr.conf'
                                      )]}
    },
    'sfc': {
        'PrepbufrGDAS': {'env': {'prepbufr': 'gdas',
                                 'obs_window': '1800',
                                 'msg_type': "'ADPUPA, AIRCAR, AIRCFT'",
                                 'obs_bufr_var_list': ("'D_CAPE, D_MLCAPE, "
                                                       +"D_PBL'"),
                                 'valid_hr_inc': '6'},
                         'commands': [gda_util.metplus_command(
                                          'PB2NC_obsPrepbufr.conf'
                                      )]},
        'PrepbufrNAM': {'env': {'prepbufr': 'nam',
                                'obs_window': '900',
                                'msg_type': 'ADPSFC',
                                'obs_bufr_var_list': ("'PMO, UOB, VOB, MXGS, "
                                                      +"TOB, TDO, D_RH, QOB, "
                                                      +"HOVI, CEILING, TOCC'")},
                        'commands': [gda_util.metplus_command(
                                         'PB2NC_obsPrepbufr.conf'
                                     )]},
        'PrepbufrRAP_P': {'env': {'prepbufr': 'rap_p',
                                  'obs_window': '900',
                                  'msg_type': 'ADPSFC',
                                  'obs_bufr_var_list': ("'PMO, UOB, VOB, MXGS, "
                                                        +"TOB, TDO, D_RH, QOB, "
                                                        +"HOVI, CEILING, TOCC'")},
                          'commands': [gda_util.metplus_command(
                                           'PB2NC_obsPrepbufr.conf'
                                       )]},
    },
    'sea_ice': {}
}
reformat_model_jobs_dict = {
    'pres_levs': {},
    'sfc': {},
    'sea_ice': {}
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
            if verif_type == 'sfc' \
                    and verif_type_job in ['PrepbufrNAM',
                                           'PrepbufrRAP_P']:
                job_env_dict['PB2NC_ENDDATE'] = date_dt.strftime('%Y%m%d')
                job_env_dict['PB2NC_STARTDATE'] = (
                    (date_dt - datetime.timedelta(hours=24))\
                    .strftime('%Y%m%d')
                )
            else:
                job_env_dict['PB2NC_ENDDATE'] = date_dt.strftime('%Y%m%d')
                job_env_dict['PB2NC_STARTDATE'] = date_dt.strftime('%Y%m%d')
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
    'pres_levs': {
        'GeoHeight': {'env': {'prepbufr': 'gdas',
                              'obs_window': '1800',
                              'msg_type': "'ADPUPA, AIRCAR, AIRCFT'",
                              'var1_name': 'HGT',
                              'var1_levels': ("'P1000, P925, P850, "
                                              +"P700, P500, P400, "
                                              +"P300, P250, P200, "
                                              +"P150, P100, P50, "
                                              +"P20, P10, P5, P1'"),
                              'var1_options': '',
                              'met_config_overrides': ''},
                      'commands': [gda_util.metplus_command(
                                       'PointStat_fcstGLOBAL_DET_'
                                       +'obsPrepbufr.conf'
                                   )]},
        'RelHum': {'env': {'prepbufr': 'gdas',
                           'obs_window': '1800',
                           'msg_type': "'ADPUPA, AIRCAR, AIRCFT'",
                           'var1_name': 'RH',
                           'var1_levels': ("'P1000, P925, P850, "
                                           +"P700, P500, P400, "
                                           +"P300, P250, P200, "
                                           +"P150, P100, P50, "
                                           +"P20, P10, P5, P1'"),
                           'var1_options': '',
                           'met_config_overrides': ''},
                   'commands': [gda_util.metplus_command(
                                    'PointStat_fcstGLOBAL_DET_'
                                    +'obsPrepbufr.conf'
                                )]},
        'SpefHum': {'env': {'prepbufr': 'gdas',
                            'obs_window': '1800',
                            'msg_type': "'ADPUPA, AIRCAR, AIRCFT'",
                            'var1_name': 'SPFH',
                            'var1_levels': ("'P1000, P925, P850, "
                                            +"P700, P500, P400, "
                                            +"P300, P250, P200, "
                                            +"P150, P100, P50, "
                                            +"P20, P10, P5, P1'"),
                            'var1_options': '',
                            'met_config_overrides': ''},
                    'commands': [gda_util.metplus_command(
                                     'PointStat_fcstGLOBAL_DET_'
                                     +'obsPrepbufr.conf'
                                 )]},
        'Temp': {'env': {'prepbufr': 'gdas',
                         'obs_window': '1800',
                         'msg_type': "'ADPUPA, AIRCAR, AIRCFT'",
                         'var1_name': 'HGT',
                         'var1_levels': ("'P1000, P925, P850, "
                                         +"P700, P500, P400, "
                                         +"P300, P250, P200, "
                                         +"P150, P100, P50, "
                                         +"P20, P10, P5, P1'"),
                         'var1_options': '',
                         'met_config_overrides': ''},
                 'commands': [gda_util.metplus_command(
                                  'PointStat_fcstGLOBAL_DET_'
                                  +'obsPrepbufr.conf'
                              )]},
        'Winds': {'env': {'prepbufr': 'gdas',
                          'obs_window': '1800',
                          'msg_type': "'ADPUPA, AIRCAR, AIRCFT'",
                          'var1_name': 'UGRD',
                          'var1_levels': ("'P1000, P925, P850, "
                                          +"P700, P500, P400, "
                                          +"P300, P250, P200, "
                                          +"P150, P100, P50, "
                                          +"P20, P10, P5, P1'"),
                          'var1_options': '',
                          'var2_name': 'VGRD',
                          'var2_levels': ("'P1000, P925, P850, "
                                          +"P700, P500, P400, "
                                          +"P300, P250, P200, "
                                          +"P150, P100, P50, "
                                          +"P20, P10, P5, P1'"),
                          'var2_options': '',
                          'met_config_overrides': ''},
                  'commands': [gda_util.metplus_command(
                                   'PointStat_fcstGLOBAL_DET_'
                                   +'obsPrepbufr_Winds.conf'
                               )]}
    },
    'sfc': {
        'CAPEMixedLayer': {'env': {'prepbufr': 'gdas',
                                   'obs_window': '1800',
                                   'msg_type': "'ADPUPA, AIRCAR, AIRCFT'",
                                   'valid_hr_inc': '6',
                                   'var1_fcst_name': 'CAPE',
                                   'var1_fcst_levels': "'P90-0'",
                                   'var1_fcst_options': ("'cnt_thresh = "
                                                         +"[ >0 ];'"),
                                   'var1_obs_name': 'MLCAPE',
                                   'var1_obs_levels': "'L0-90000'",
                                   'var1_obs_options': ("'cnt_thresh = "
                                                        +"[ >0 ]; "
                                                        +"cnt_logic = "
                                                        +"UNION;'"),
                                   'var1_thresh_list': ("'>500, >1000, "
                                                        +">1500, >2000, "
                                                        +">3000, >4000, "
                                                        +">5000'"),
                                   'met_config_overrides': ''},
                           'commands': [gda_util.metplus_command(
                                            'PointStat_fcstGLOBAL_DET_'
                                            +'obsPrepbufr_Thresh.conf'
                                        )]},
        'CAPESfcBased': {'env': {'prepbufr': 'gdas',
                                 'obs_window': '1800',
                                 'msg_type': "'ADPUPA, AIRCAR, AIRCFT'",
                                 'valid_hr_inc': '6',
                                 'var1_fcst_name': 'CAPE',
                                 'var1_fcst_levels': 'Z0',
                                 'var1_fcst_options': ("'cnt_thresh = "
                                                       +"[ >0 ];'"),
                                 'var1_obs_name': 'CAPE',
                                 'var1_obs_levels': "'L0-100000'",
                                 'var1_obs_options': ("'cnt_thresh = "
                                                      +"[ >0 ]; "
                                                      +"cnt_logic = "
                                                      +"UNION;'"),
                                 'var1_thresh_list': ("'>500, >1000, "
                                                      +">1500, >2000, "
                                                      +">3000, >4000, "
                                                      +">5000'"),
                                 'met_config_overrides': ''},
                         'commands': [gda_util.metplus_command(
                                          'PointStat_fcstGLOBAL_DET_'
                                          +'obsPrepbufr_Thresh.conf'
                                      )]},
        'Ceiling': {'env': {'prepbufr': 'nam',
                            'obs_window': '900',
                            'msg_type': 'ADPSFC',
                            'var1_name': 'HGT',
                            'var1_levels': 'L0',
                            'var1_options': ("'GRIB_lvl_typ = 215;"
                                             +"set_attr_level = "
                                             +'"Ceiling";'+"'"),
                            'met_config_overrides': ''},
                    'commands': [gda_util.metplus_command(
                                     'PointStat_fcstGLOBAL_DET_'
                                     +'obsPrepbufr.conf'
                                 )]},
        'DailyAvg_TempAnom2m': {'env': {'prepbufr': 'nam',
                                        'obs_window': '900',
                                        'msg_type': 'ADPSFC',
                                        'valid_hr_inc': '6',
                                        'var1_name': 'TMP',
                                        'var1_levels': 'Z2',
                                        'var1_options': '',
                                        'met_config_overrides': ("'climo_mean "
                                                                 +"= fcst;'")},
                                'commands': [gda_util.metplus_command(
                                                'PointStat_fcstGLOBAL_DET_'
                                                 +'obsPrepbufr_climoERAI_'
                                                 +'MPR.conf'
                                             ),
                                             gda_util.python_command(
                                                 'global_det_atmos_stats_'
                                                 'grid2obs_create_anomaly.py',
                                                 ['TMP_Z2',
                                                  os.path.join(
                                                      '$DATA',
                                                      '${VERIF_CASE}_${STEP}',
                                                      'METplus_output',
                                                      '${RUN}.'
                                                      +'{valid?fmt=%Y%m%d}',
                                                      '$MODEL', '$VERIF_CASE',
                                                      'point_stat_'
                                                      +'${VERIF_TYPE}.'
                                                      +'${job_name}_'
                                                      +'{lead?fmt=%2H}0000L_'
                                                      +'{valid?fmt=%Y%m%d}_'
                                                      +'{valid?fmt=%H}0000V'
                                                      +'.stat'
                                                )]
                                            ),
                                            gda_util.python_command(
                                                'global_det_atmos_stats_'
                                                'grid2obs_create_daily_avg.py',
                                                ['HGT_ANOM_P500',
                                                  os.path.join(
                                                      '$DATA',
                                                      '${VERIF_CASE}_${STEP}',
                                                      'METplus_output',
                                                      '${RUN}.'
                                                      +'{valid?fmt=%Y%m%d}',
                                                      '$MODEL', '$VERIF_CASE',
                                                      'anomaly_${VERIF_TYPE}.'
                                                      +'${job_name}_init'
                                                      +'{init?fmt=%Y%m%d%H}_'
                                                      +'fhr{lead?fmt=%3H}.stat'
                                                )]
                                            ),
                                            gda_util.metplus_command(
                                                'StatAnalysis_fcstGLOBAL_DET_'
                                                +'obsPrepbufr_MPRtoCNT.conf'
                                            ),
                                            gda_util.metplus_command(
                                                'StatAnalysis_fcstGLOBAL_DET_'
                                                +'obsPrepbufr_MPRtoSL1L2.conf'
                                            )
                                        ]},
        'Dewpoint2m': {'env': {'prepbufr': 'nam',
                               'obs_window': '900',
                               'msg_type': 'ADPSFC',
                               'var1_fcst_name': 'DPT',
                               'var1_fcst_levels': 'Z2',
                               'var1_fcst_options': '',
                               'var1_obs_name': 'DPT',
                               'var1_obs_levels': 'Z2',
                               'var1_obs_options': '',
                               'var1_thresh_list': "'>50, >60, >70'",
                               'met_config_overrides': ''},
                       'commands': [gda_util.metplus_command(
                                        'PointStat_fcstGLOBAL_DET_'
                                        +'obsPrepbufr_Thresh.conf'
                                    )]},
        'PBLHeight': {'env': {'prepbufr': 'gdas',
                              'obs_window': '1800',
                              'msg_type': "'ADPUPA, AIRCAR, AIRCFT'",
                              'valid_hr_inc': '6',
                              'var1_name': 'HPBL',
                              'var1_levels': 'L0',
                              'var1_options': '',
                              'met_config_overrides': ''},
                      'commands': [gda_util.metplus_command(
                                       'PointStat_fcstGLOBAL_DET_'
                                       +'obsPrepbufr.conf'
                                   )]},
        'RelHum2m': {'env': {'prepbufr': 'nam',
                             'obs_window': '900',
                             'msg_type': 'ADPSFC',
                             'var1_name': 'RH',
                             'var1_levels': 'Z2',
                             'var1_options': '',
                             'met_config_overrides': ''},
                     'commands': [gda_util.metplus_command(
                                      'PointStat_fcstGLOBAL_DET_'
                                      +'obsPrepbufr.conf'
                                  )]},
        'SeaLevelPres': {'env': {'prepbufr': 'nam',
                                 'obs_window': '900',
                                 'msg_type': 'ADPSFC',
                                 'var1_name': 'PRMSL',
                                 'var1_levels': 'Z0',
                                 'var1_options': '',
                                 'met_config_overrides': ''},
                         'commands': [gda_util.metplus_command(
                                          'PointStat_fcstGLOBAL_DET_'
                                          +'obsPrepbufr.conf'
                                      )]},
        'Temp2m': {'env': {'prepbufr': 'nam',
                           'obs_window': '900',
                           'msg_type': 'ADPSFC',
                           'var1_name': 'TMP',
                           'var1_levels': 'Z2',
                           'var1_options': '',
                           'met_config_overrides': ''},
                   'commands': [gda_util.metplus_command(
                                    'PointStat_fcstGLOBAL_DET_'
                                    +'obsPrepbufr.conf'
                                )]},
        'TotCloudCover': {'env': {'prepbufr': 'nam',
                                  'obs_window': '900',
                                  'msg_type': 'ADPSFC',
                                  'var1_name': 'TCDC',
                                  'var1_levels': 'L0',
                                  'var1_options': ("'GRIB_lvl_typ = 10;"
                                                   +"set_attr_level = "
                                                   +'"Total";'+"'"),
                                  'met_config_overrides': ''},
                          'commands': [gda_util.metplus_command(
                                           'PointStat_fcstGLOBAL_DET_'
                                           +'obsPrepbufr.conf'
                                       )]},
        'Visibility': {'env': {'prepbufr': 'nam',
                               'obs_window': '900',
                               'msg_type': 'ADPSFC',
                               'var1_name': 'VIS',
                               'var1_levels': 'Z0',
                               'var1_options': '',
                               'met_config_overrides': ''},
                       'commands': [gda_util.metplus_command(
                                        'PointStat_fcstGLOBAL_DET_'
                                        +'obsPrepbufr.conf'
                                    )]},
        'WindGust': {'env': {'prepbufr': 'nam',
                             'obs_window': '900',
                             'msg_type': 'ADPSFC',
                             'var1_name': 'GUST',
                             'var1_levels': 'Z00',
                             'var1_options': '',
                             'met_config_overrides': ''},
                     'commands': [gda_util.metplus_command(
                                      'PointStat_fcstGLOBAL_DET_'
                                       +'obsPrepbufr.conf'
                                  )]},
        'Winds10m': {'env': {'prepbufr': 'nam',
                             'obs_window': '900',
                             'msg_type': 'ADPSFC',
                             'var1_name': 'UGRD',
                             'var1_levels': 'Z10',
                             'var1_options': '',
                             'var2_name': 'VGRD',
                             'var2_levels': 'Z10',
                             'var2_options': '',
                             'met_config_overrides': ''},
                     'commands': [gda_util.metplus_command(
                                      'PointStat_fcstGLOBAL_DET_'
                                       +'obsPrepbufr_Winds.conf'
                                  )]},
    },
    'sea_ice': {}
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
        FIXevs = job_env_dict['FIXevs']
        if verif_type == 'pres_levs':
            job_env_dict['grid'] = 'G004'
            job_env_dict['mask_list'] = (
                "'"+FIXevs+"/masks/G004_GLOBAL.nc, "
                +FIXevs+"/masks/G004_NHEM.nc, "
                +FIXevs+"/masks/G004_SHEM.nc, "
                +FIXevs+"/masks/G004_TROPICS.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_CONUS.nc'"
            )
        elif verif_type == 'sfc':
            job_env_dict['grid'] = 'G104'
            job_env_dict['mask_list'] = (
                "'/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_CONUS.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_CONUS_East.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_CONUS_West.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_CONUS_South.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_CONUS_Central.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_Appalachia.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_CPlains.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_DeepSouth.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_GreatBasin.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_GreatLakes.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_Mezquital.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_MidAtlantic.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_NorthAtlantic.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_NPlains.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_NRockies.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_PacificNW.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_PacificSW.nc"
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_Prairie.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_Southeast.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_Southwest.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_SPlains.nc, "
                +"/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix/Bukovsky_50m_SRockies.nc'"
            )
        # Loop through and write job script for dates and models
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
            if verif_type == 'sfc' \
                    and verif_type_job == 'DailyAvg_TempAnom2m':
                job_env_dict['MPR_ENDDATE'] = date_dt.strftime('%Y%m%d')
                job_env_dict['MPR_STARTDATE'] = (
                    (date_dt - datetime.timedelta(hours=24))\
                    .strftime('%Y%m%d')
                )
                MPR_fhr_start = int(job_env_dict['fhr_start']) - 18
                if MPR_fhr_start > 0:
                    job_env_dict['MPR_fhr_start'] = str(MPR_fhr_start)
                else:
                    job_env_dict['MPR_fhr_start'] = (
                        job_env_dict['fhr_start']
                    )
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
