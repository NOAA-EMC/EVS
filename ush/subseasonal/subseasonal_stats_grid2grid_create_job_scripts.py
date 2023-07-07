#!/usr/bin/env python3
'''
Program Name: subseasonal_stats_grid2grid_create_job_scripts.py
Contact(s): Shannon Shields
Abstract: This creates multiple independent job scripts. These
          jobs contain all the necessary environment variables
          and commands to needed to run the specific
          use case.
'''

import sys
import os
import glob
import datetime
import numpy as np
import subseasonal_util as sub_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
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
members = os.environ['members']

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')

# Set up job directory
njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                  'METplus_job_scripts', JOB_GROUP)
if not os.path.exists(JOB_GROUP_jobs_dir):
    os.makedirs(JOB_GROUP_jobs_dir)

################################################
#### assemble_data jobs
################################################
assemble_data_obs_jobs_dict = {
    'anom': {},
    'ENSO': {},
    'OLR': {},
    'precip': {
        #'24hrCCPA': {'env': {},
                     #'commands': [sub_util.metplus_command(
                                      #'PCPCombine_obs24hrCCPA.conf'
                                  #)]}
    },
    'pres_lvls': {},
    'seaice': {},
    'sst': {},
}
assemble_data_model_jobs_dict = {
    'anom': {
        'WeeklyAvg_TempAnom2m': {'env': {'var1_name': 'TMP',
                                         'var1_levels': 'Z2'},
                                 'commands': [sub_util.python_command(
                                                  'subseasonal_'
                                                  +'stats_grid2grid'
                                                  +'_create_weekly_avg.py',
                                                  ['TMP_ANOM_Z2',
                                                   os.path.join(
                                                       '$DATA',
                                                       '${VERIF_CASE}_'
                                                       +'${STEP}',
                                                       'METplus_output',
                                                       '${RUN}.'
                                                       +'$DATE',
                                                       '$MODEL',
                                                       '$VERIF_CASE',
                                                       'anomaly_'
                                                       +'${VERIF_TYPE}_'
                                                       +'TempAnom2m_init'
                                                       +'{init?fmt=%Y%m%d%H}_'
                                                       +'fhr{lead?fmt=%3H}.nc'
                                                   ),
                                                   os.path.join(
                                                       '$COMOUT',
                                                       '${RUN}.'
                                                       +'$DATE',
                                                       '$MODEL',
                                                       '$VERIF_CASE',
                                                       'anomaly_'
                                                       +'${VERIF_TYPE}_'
                                                       +'TempAnom2m_init'
                                                       +'{init?fmt=%Y%m%d%H}_'
                                                       +'fhr{lead?fmt=%3H}.nc'
                                                   )]
                                              )]},
        'Days6_10Avg_TempAnom2m': {'env': {'var1_name': 'TMP',
                                           'var1_levels': 'Z2'},
                                   'commands': [sub_util.python_command(
                                                    'subseasonal_'
                                                    +'stats_grid2grid'
                                                    +'_create_days6_10_avg.py',
                                                    ['TMP_ANOM_Z2',
                                                     os.path.join(
                                                         '$DATA',
                                                         '${VERIF_CASE}_'
                                                         +'${STEP}',
                                                         'METplus_output',
                                                         '${RUN}.'
                                                         +'$DATE',
                                                         '$MODEL',
                                                         '$VERIF_CASE',
                                                         'anomaly_'
                                                         +'${VERIF_TYPE}_'
                                                         +'TempAnom2m_init'
                                                         +'{init?fmt=%Y%m%d%H}_'
                                                         +'fhr{lead?fmt=%3H}.nc'
                                                     ),
                                                     os.path.join(
                                                         '$COMOUT',
                                                         '${RUN}.'
                                                         +'$DATE',
                                                         '$MODEL',
                                                         '$VERIF_CASE',
                                                         'anomaly_'
                                                         +'${VERIF_TYPE}_'
                                                         +'TempAnom2m_init'
                                                         +'{init?fmt=%Y%m%d%H}_'
                                                         +'fhr{lead?fmt=%3H}.nc'
                                                     )]
                                                )]},
        'Weeks3_4Avg_TempAnom2m': {'env': {'var1_name': 'TMP',
                                           'var1_levels': 'Z2'},
                                   'commands': [sub_util.python_command(
                                                    'subseasonal_'
                                                    +'stats_grid2grid'
                                                    +'_create_weeks3_4_avg.py',
                                                    ['TMP_ANOM_Z2',
                                                     os.path.join(
                                                         '$DATA',
                                                         '${VERIF_CASE}_'
                                                         +'${STEP}',
                                                         'METplus_output',
                                                         '${RUN}.'
                                                         +'$DATE',
                                                         '$MODEL',
                                                         '$VERIF_CASE',
                                                         'anomaly_'
                                                         +'${VERIF_TYPE}_'
                                                         +'TempAnom2m_init'
                                                         +'{init?fmt=%Y%m%d%H}_'
                                                         +'fhr{lead?fmt=%3H}.nc'
                                                     ),
                                                     os.path.join(
                                                         '$COMOUT',
                                                         '${RUN}.'
                                                         +'$DATE',
                                                         '$MODEL',
                                                         '$VERIF_CASE',
                                                         'anomaly_'
                                                         +'${VERIF_TYPE}_'
                                                         +'TempAnom2m_init'
                                                         +'{init?fmt=%Y%m%d%H}_'
                                                         +'fhr{lead?fmt=%3H}.nc'
                                                     )]
                                                )]},
    },
    'ENSO': {},
    'OLR': {},
    'precip': {
        #'24hrAccum': {'env': {},
                      #'commands': [sub_util.metplus_command(
                                       #'PCPCombine_fcstSUBSEASONAL_'
                                       #+'24hrAccum_precip.conf'
                                   #)]}
    },
    'pres_lvls': {
        'WeeklyAvg_GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                            'var1_levels': 'P500'},
                                    'commands': [sub_util.python_command(
                                                     'subseasonal_'
                                                     +'stats_grid2grid'
                                                     +'_create_weekly_avg.py',
                                                     ['HGT_ANOM_P500',
                                                      os.path.join(
                                                          '$DATA',
                                                          '${VERIF_CASE}_'
                                                          +'${STEP}',
                                                          'METplus_output',
                                                          '${RUN}.'
                                                          +'$DATE',
                                                          '$MODEL',
                                                          '$VERIF_CASE',
                                                          'anomaly_'
                                                          +'${VERIF_TYPE}_'
                                                          +'GeoHeightAnom_init'
                                                          +'{init?fmt=%Y%m%d%H}_'
                                                          +'fhr{lead?fmt=%3H}.nc'
                                                      ),
                                                      os.path.join(
                                                          '$COMOUT',
                                                          '${RUN}.'
                                                          +'$DATE',
                                                          '$MODEL',
                                                          '$VERIF_CASE',
                                                          'anomaly_'
                                                          +'${VERIF_TYPE}_'
                                                          +'GeoHeightAnom_init'
                                                          +'{init?fmt=%Y%m%d%H}_'
                                                          +'fhr{lead?fmt=%3H}.nc'
                                                      )]
                                                 )]},
        'Days6_10Avg_GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                              'var1_levels': 'P500'},
                                      'commands': [sub_util.python_command(
                                                       'subseasonal_'
                                                       +'stats_grid2grid'
                                                       +'_create_days6_10_avg.py',
                                                       ['HGT_ANOM_P500',
                                                        os.path.join(
                                                            '$DATA',
                                                            '${VERIF_CASE}_'
                                                            +'${STEP}',
                                                            'METplus_output',
                                                            '${RUN}.'
                                                            +'$DATE',
                                                            '$MODEL',
                                                            '$VERIF_CASE',
                                                            'anomaly_'
                                                            +'${VERIF_TYPE}_'
                                                            +'GeoHeightAnom_init'
                                                            +'{init?fmt=%Y%m%d%H}_'
                                                            +'fhr{lead?fmt=%3H}.nc'
                                                        ),
                                                        os.path.join(
                                                            '$COMOUT',
                                                            '${RUN}.'
                                                            +'$DATE',
                                                            '$MODEL',
                                                            '$VERIF_CASE',
                                                            'anomaly_'
                                                            +'${VERIF_TYPE}_'
                                                            +'GeoHeightAnom_init'
                                                            +'{init?fmt=%Y%m%d%H}_'
                                                            +'fhr{lead?fmt=%3H}.nc'
                                                        )]
                                                   )]},
        'Weeks3_4Avg_GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                              'var1_levels': 'P500'},
                                      'commands': [sub_util.python_command(
                                                       'subseasonal_'
                                                       +'stats_grid2grid'
                                                       +'_create_weeks3_4_avg.py',
                                                       ['HGT_ANOM_P500',
                                                        os.path.join(
                                                            '$DATA',
                                                            '${VERIF_CASE}_'
                                                            +'${STEP}',
                                                            'METplus_output',
                                                            '${RUN}.'
                                                            +'$DATE',
                                                            '$MODEL',
                                                            '$VERIF_CASE',
                                                            'anomaly_'
                                                            +'${VERIF_TYPE}_'
                                                            +'GeoHeightAnom_init'
                                                            +'{init?fmt=%Y%m%d%H}_'
                                                            +'fhr{lead?fmt=%3H}.nc'
                                                        ),
                                                        os.path.join(
                                                            '$COMOUT',
                                                            '${RUN}.'
                                                            +'$DATE',
                                                            '$MODEL',
                                                            '$VERIF_CASE',
                                                            'anomaly_'
                                                            +'${VERIF_TYPE}_'
                                                            +'GeoHeightAnom_init'
                                                            +'{init?fmt=%Y%m%d%H}_'
                                                            +'fhr{lead?fmt=%3H}.nc'
                                                        )]
                                                   )]},
    },
    'seaice': {
        'WeeklyAvg_Concentration': {'env': {'var1_name': 'ICEC',
                                            'var1_levels': 'Z0',},
                                    'commands': [sub_util.python_command(
                                                     'subseasonal_stats_'
                                                     +'grid2grid_create_'
                                                     +'weekly_avg.py',
                                                     ['ICEC_Z0',
                                                      os.path.join(
                                                          '$DATA',
                                                          '${VERIF_CASE}_'
                                                          +'${STEP}',
                                                          'METplus_output',
                                                          '${RUN}.'
                                                          +'$DATE',
                                                          '$MODEL',
                                                          '$VERIF_CASE',
                                                          'grid_stat_'
                                                          +'${VERIF_TYPE}_'
                                                          +'Concentration_'
                                                          +'{lead?fmt=%2H}0000L_'
                                                          +'{valid?fmt=%Y%m%d}_'
                                                          +'{valid?fmt=%H}0000V_'
                                                          +'pairs.nc'
                                                      ),
                                                      os.path.join(
                                                          '$COMOUT',
                                                          '${RUN}.'
                                                          +'$DATE',
                                                          '$MODEL',
                                                          '$VERIF_CASE',
                                                          'grid_stat_'
                                                          +'${VERIF_TYPE}_'
                                                          +'Concentration_'
                                                          +'{lead?fmt=%2H}0000L_'
                                                          +'{valid?fmt=%H}0000V_'
                                                          +'pairs.nc'
                                                      )])]},
        'MonthlyAvg_Concentration': {'env': {'var1_name': 'ICEC',
                                             'var1_levels': 'Z0',},
                                     'commands': [sub_util.python_command(
                                                      'subseasonal_stats_'
                                                      +'grid2grid_create_'
                                                      +'monthly_avg.py',
                                                      ['ICEC_Z0',
                                                       os.path.join(
                                                           '$DATA',
                                                           '${VERIF_CASE}_'
                                                           +'${STEP}',
                                                           'METplus_output',
                                                           '${RUN}.'
                                                           +'$DATE',
                                                           '$MODEL',
                                                           '$VERIF_CASE',
                                                           'grid_stat_'
                                                           +'${VERIF_TYPE}_'
                                                           +'Concentration_'
                                                           +'{lead?fmt=%2H}0000L_'
                                                           +'{valid?fmt=%Y%m%d}_'
                                                           +'{valid?fmt=%H}0000V_'
                                                           +'pairs.nc'
                                                       ),
                                                       os.path.join(
                                                           '$COMOUT',
                                                           '${RUN}.'
                                                           +'$DATE',
                                                           '$MODEL',
                                                           '$VERIF_CASE',
                                                           'grid_stat_'
                                                           +'${VERIF_TYPE}_'
                                                           +'Concentration_'
                                                           +'{lead?fmt=%2H}0000L_'
                                                           +'{valid?fmt=%H}0000V_'
                                                           +'pairs.nc'
                                                       )])]},
    },
    'sst': {
        'DailyAvg_SST': {'env': {'var1_name': 'TMP',
                                 'var1_levels': 'Z0'},
                         'commands': [sub_util.python_command(
                                          'subseasonal_'
                                          +'stats_grid2grid'
                                          +'_create_daily_avg.py',
                                          ['TMP_Z0',
                                           os.path.join(
                                              '$DATA',
                                              '${VERIF_CASE}_${STEP}',
                                              'METplus_output',
                                              '${RUN}.$DATE',
                                              '$MODEL', '$VERIF_CASE',
                                              'grid_stat_${VERIF_TYPE}_'
                                              +'SST_'
                                              +'{lead?fmt=%2H}0000L_'
                                              +'{valid?fmt=%Y%m%d}_'
                                              +'{valid?fmt=%H}0000V_pairs.nc'
                                          ),
                                          os.path.join(
                                               '$COMOUT',
                                               '${RUN}.$DATE',
                                               '$MODEL', '$VERIF_CASE',
                                               'grid_stat_${VERIF_TYPE}_'
                                               +'SST_'
                                               +'{lead?fmt=%2H}0000L_'
                                               +'{valid?fmt=%Y%m%d}_'
                                               +'{valid?fmt=%H}0000V_pairs.nc'
                                           )])]},
        'WeeklyAvg_SST': {'env': {'var1_name': 'TMP',
                                  'var1_levels': 'Z0',},
                          'commands': [sub_util.python_command(
                                           'subseasonal_stats_'
                                           +'grid2grid_create_'
                                           +'weekly_avg.py',
                                           ['TMP_Z0',
                                            os.path.join(
                                                '$DATA',
                                                '${VERIF_CASE}_'
                                                +'${STEP}',
                                                'METplus_output',
                                                '${RUN}.'
                                                +'$DATE',
                                                '$MODEL',
                                                '$VERIF_CASE',
                                                'grid_stat_'
                                                +'${VERIF_TYPE}_'
                                                +'SST_'
                                                +'{lead?fmt=%2H}0000L_'
                                                +'{valid?fmt=%Y%m%d}_'
                                                +'{valid?fmt=%H}0000V_'
                                                +'pairs.nc'
                                            ),
                                            os.path.join(
                                                '$COMOUT',
                                                '${RUN}.'
                                                +'$DATE',
                                                '$MODEL',
                                                '$VERIF_CASE',
                                                'grid_stat_'
                                                +'${VERIF_TYPE}_'
                                                +'SST_'
                                                +'{lead?fmt=%2H}0000L_'
                                                +'{valid?fmt=%H}0000V_'
                                                +'pairs.nc'
                                            )])]},
        'MonthlyAvg_SST': {'env': {'var1_name': 'TMP',
                                   'var1_levels': 'Z0'},
                           'commands': [sub_util.python_command(
                                            'subseasonal_'
                                            +'stats_grid2grid'
                                            +'_create_monthly_avg.py',
                                            ['TMP_Z0',
                                             os.path.join(
                                                 '$DATA',
                                                 '${VERIF_CASE}_${STEP}',
                                                 'METplus_output',
                                                 '${RUN}.$DATE',
                                                 '$MODEL', '$VERIF_CASE',
                                                 'grid_stat_${VERIF_TYPE}_'
                                                 +'SST_'
                                                 +'{lead?fmt=%2H}0000L_'
                                                 +'{valid?fmt=%Y%m%d}_'
                                                 +'{valid?fmt=%H}0000V_pairs.nc'
                                             ),
                                             os.path.join(
                                                 '$COMOUT',
                                                 '${RUN}.$DATE',
                                                 '$MODEL', '$VERIF_CASE',
                                                 'grid_stat_${VERIF_TYPE}_'
                                                 +'SST_'
                                                 +'{lead?fmt=%2H}0000L_'
                                                 +'{valid?fmt=%Y%m%d}_'
                                                 +'{valid?fmt=%H}0000V_pairs.nc'
                                             )])]}
    },
}

################################################
#### generate_stats jobs
################################################
generate_stats_jobs_dict = {
    'ENSO': {},
    'OLR': {},
    'anom': {
        'WeeklyAvg_TempAnom2m': {'env': {'var1_name': 'TMP',
                                         'var1_levels': 'Z2',
                                         'met_config_overrides': (
                                             "'climo_mean = fcst;'"
                                         )},
                                 'commands': [sub_util.metplus_command(
                                                  'GridStat_fcstSUBSEASONAL_'
                                                  +'obsECMWF_WeeklyAvgAnom'
                                                  +'.conf'
                                              )]},
        'Days6_10Avg_TempAnom2m': {'env': {'var1_name': 'TMP',
                                           'var1_levels': 'Z2',
                                           'met_config_overrides': (
                                               "'climo_mean = fcst;'"
                                           )},
                                   'commands': [sub_util.metplus_command(
                                                    'GridStat_fcstSUBSEASONAL_'
                                                    +'obsECMWF_Days6_10AvgAnom'
                                                    +'.conf'
                                                )]},
        'Weeks3_4Avg_TempAnom2m': {'env': {'var1_name': 'TMP',
                                           'var1_levels': 'Z2',
                                           'met_config_overrides': (
                                               "'climo_mean = fcst;'"
                                           )},
                                   'commands': [sub_util.metplus_command(
                                                    'GridStat_fcstSUBSEASONAL_'
                                                    +'obsECMWF_Weeks3_4AvgAnom'
                                                    +'.conf'
                                                )]},
    },
    'precip': {
        #'24hrCCPA': {'env': {'met_config_overrides': ''},
                          #'commands': [sub_util.metplus_command(
                                           #'GridStat_fcstSUBSEASONAL_'
                                           #+'obs24hrCCPA.conf'
                                       #)]},
        #'24hrCCPA_Nbrhd1': {'env': {'nbhrd_list': ("'1,3,5,7,9,11,13,"
                                                   #+"15,17,19'"),
                                    #'met_config_overrides': ''},
                            #'commands': [sub_util.metplus_command(
                                             #'GridStat_fcstSUBSEASONAL_'
                                             #+'obs24hrCCPA_Nbrhd.conf'
                                         #)]},
        #'24hrCCPA_Nbrhd2': {'env': {'nbhrd_list': "'21,23,25,27,29'",
                                    #'met_config_overrides': ''},
                            #'commands': [sub_util.metplus_command(
                                             #'GridStat_fcstSUBSEASONAL_'
                                             #+'obs24hrCCPA_Nbrhd.conf'
                                         #)]},
        #'24hrCCPA_Nbrhd3': {'env': {'nbhrd_list': "'31,33,35,37'",
                                    #'met_config_overrides': ''},
                            #'commands': [sub_util.metplus_command(
                                             #'GridStat_fcstSUBSEASONAL_'
                                             #+'obs24hrCCPA_Nbrhd.conf'
                                         #)]},
        #'24hrCCPA_Nbrhd4': {'env': {'nbhrd_list': "'39,41,43'",
                                    #'met_config_overrides': ''},
                            #'commands': [sub_util.metplus_command(
                                             #'GridStat_fcstSUBSEASONAL_'
                                             #+'obs24hrCCPA_Nbrhd.conf'
                                         #)]},
        #'24hrCCPA_Nbrhd5': {'env': {'nbhrd_list': "'45,47,49'",
                                    #'met_config_overrides': ''},
                           #'commands': [sub_util.metplus_command(
                                            #'GridStat_fcstSUBSEASONAL_'
                                            #+'obs24hrCCPA_Nbrhd.conf'
                                        #)]},
        #'24hrCCPA_Nbrhd6': {'env': {'nbhrd_list': "'51,53,55'",
                                    #'met_config_overrides': ''},
                           #'commands': [sub_util.metplus_command(
                                            #'GridStat_fcstSUBSEASONAL_'
                                            #+'obs24hrCCPA_Nbrhd.conf'
                                        #)]},
        #'24hrCCPA_Nbrhd7': {'env': {'nbhrd_list': "'57,59'",
                                    #'met_config_overrides': ''},
                           #'commands': [sub_util.metplus_command(
                                            #'GridStat_fcstSUBSEASONAL_'
                                            #+'obs24hrCCPA_Nbrhd.conf'
                                        #)]},
        #'24hrCCPA_Nbrhd8': {'env': {'nbhrd_list': "'61,63'",
                                    #'met_config_overrides': ''},
                           #'commands': [sub_util.metplus_command(
                                            #'GridStat_fcstSUBSEASONAL_'
                                            #+'obs24hrCCPA_Nbrhd.conf'
                                        #)]}
    },
    'pres_lvls': {
        #'GeoHeight': {'env': {'var1_name': 'HGT',
                              #'var1_levels': 'P500',
                              #'var1_options': '',
                              #'met_config_overrides': "'climo_mean = fcst;'"}#,
                      #'commands': [sub_util.metplus_command(
                                       #'GridStat_fcstSUBSEASONAL_'
                                       #+'obsGFS_climoERA5.conf'
                                   #)]}
        'WeeklyAvg_GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                            'var1_levels': 'P500',
                                            'met_config_overrides': (
                                                "'climo_mean = fcst;'"
                                            )},
                                    'commands': [sub_util.metplus_command(
                                                     'GridStat_fcstSUBSEASONAL_'
                                                     +'obsGFS_WeeklyAvgAnom'
                                                     +'.conf'
                                                 )]},
        'Days6_10Avg_GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                              'var1_levels': 'P500',
                                              'met_config_overrides': (
                                                  "'climo_mean = fcst;'"
                                              )},
                                      'commands': [sub_util.metplus_command(
                                                       'GridStat_fcstSUBSEASONAL_'
                                                       +'obsGFS_Days6_10AvgAnom'
                                                       +'.conf'
                                                   )]},
        'Weeks3_4Avg_GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                              'var1_levels': 'P500',
                                              'met_config_overrides': (
                                                  "'climo_mean = fcst;'"
                                              )},
                                      'commands': [sub_util.metplus_command(
                                                       'GridStat_fcstSUBSEASONAL_'
                                                       +'obsGFS_Weeks3_4AvgAnom'
                                                       +'.conf'
                                                   )]},
        #'Temp': {'env': {'var1_name': 'TMP',
                         #'var1_levels': "'P850, P500'",
                         #'var1_options': '',
                         #'met_config_overrides': "'climo_mean = fcst;'"},
                 #'commands': [sub_util.metplus_command(
                                  #'GridStat_fcstSUBSEASONAL_'
                                  #+'obsGFS_climoERA5.conf'
                              #)]},
        #'UWind': {'env': {'var1_name': 'UGRD',
                          #'var1_levels': "'P850, P500, P250'",
                          #'var1_options': '',
                          #'met_config_overrides': "'climo_mean = fcst;'"},
                  #'commands': [sub_util.metplus_command(
                                   #'GridStat_fcstSUBSEASONAL_'
                                   #+'obsGFS_climoERA5.conf'
                               #)]},
        #'VWind': {'env': {'var1_name': 'VGRD',
                          #'var1_levels': "'P850, P500, P250'",
                          #'var1_options': '',
                          #'met_config_overrides': "'climo_mean = fcst;'"},
                  #'commands': [sub_util.metplus_command(
                                   #'GridStat_fcstSUBSEASONAL_'
                                   #+'obsGFS_climoERA5.conf'
                               #)]},
        #'VectorWind': {'env': {'var1_name': 'UGRD',
                               #'var1_levels': "'P850, P500, P250'",
                               #'var2_name': 'VGRD',
                               #'var2_levels': "'P850, P500, P250'",
                               #'met_config_overrides': "'climo_mean = fcst;'"#},
                       #'commands': [sub_util.metplus_command(
                                        #'GridStat_fcstSUBSEASONAL_'
                                        #+'obsGFS_climoERA5_'
                                        #+'VectorWind.conf'
                                    #)]},
    },
    'seaice': {
        'WeeklyAvg_Concentration': {'env': {},
                                    'commands': [sub_util.metplus_command(
                                                    'GridStat_fcstSUBSEASONAL_'
                                                    +'obsOSI-SAF_WeeklyAvg.conf'
                                                 )]},
        'MonthlyAvg_Concentration': {'env': {},
                                     'commands': [sub_util.metplus_command(
                                                      'GridStat_fcstSUBSEASONAL_'
                                                      +'obsOSI-SAF_MonthlyAvg.conf'
                                                   )]},
    },
    'sst': {
        'DailyAvg_SST': {'env': {},
                         'commands': [sub_util.metplus_command(
                                          'GridStat_fcstSUBSEASONAL_'
                                          +'obsGHRSST_OSPO_DailyAvg.conf'
                                      )]},
        'WeeklyAvg_SST': {'env': {},
                          'commands': [sub_util.metplus_command(
                                           'GridStat_fcstSUBSEASONAL_'
                                           +'obsGHRSST_OSPO_WeeklyAvg.conf'
                                       )]},
        'MonthlyAvg_SST': {'env': {},
                           'commands': [sub_util.metplus_command(
                                            'GridStat_fcstSUBSEASONAL_'
                                            +'obsGHRSST_OSPO_MonthlyAvg.conf'
                                        )]},
    },
}

################################################
#### gather_stats jobs
################################################
gather_stats_jobs_dict = {'env': {},
                    'commands': [sub_util.metplus_command(
                                     'StatAnalysis_fcstSUBSEASONAL.conf'
                                 )]}

# Create job scripts
if JOB_GROUP in ['assemble_data', 'generate_stats']:
    if JOB_GROUP == 'assemble_data':
        JOB_GROUP_jobs_dict = assemble_data_model_jobs_dict
    elif JOB_GROUP == 'generate_stats':
        JOB_GROUP_jobs_dict = generate_stats_jobs_dict
    for verif_type in VERIF_CASE_STEP_type_list:
        print("----> Making job scripts for "+VERIF_CASE_STEP+" "
              +verif_type+" for job group "+JOB_GROUP)
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +verif_type)
        # Read in environment variables for verif_type
        if JOB_GROUP == 'assemble_data' and verif_type == 'precip':
            precip_file_accum_list = (os.environ \
                [VERIF_CASE_STEP_abbrev+'_precip_file_accum_list'] \
                .split(' '))
            precip_var_list = (os.environ \
                [VERIF_CASE_STEP_abbrev+'_precip_var_list'] \
                .split(' '))
        for verif_type_job in list(JOB_GROUP_jobs_dict[verif_type].keys()):
            # Initialize job environment dictionary
            job_env_dict = sub_util.initalize_job_env_dict(
                verif_type, JOB_GROUP, VERIF_CASE_STEP_abbrev_type,
                verif_type_job
            )
            # Add job specific environment variables
            for verif_type_job_env_var in \
                    list(JOB_GROUP_jobs_dict[verif_type]\
                         [verif_type_job]['env'].keys()):
                job_env_dict[verif_type_job_env_var] = (
                    JOB_GROUP_jobs_dict[verif_type]\
                    [verif_type_job]['env'][verif_type_job_env_var]
                )
            fhr_start = job_env_dict['fhr_start']
            fhr_end = job_env_dict['fhr_end']
            fhr_inc = job_env_dict['fhr_inc']
            verif_type_job_commands_list = (
                JOB_GROUP_jobs_dict[verif_type]\
                [verif_type_job]['commands']
            ) 
            # Loop through and write job script for dates and models
            valid_start_date_dt = datetime.datetime.strptime(
                start_date+job_env_dict['valid_hr_start'],
                '%Y%m%d%H'
            )
            valid_end_date_dt = datetime.datetime.strptime(
                end_date+job_env_dict['valid_hr_end'],
                '%Y%m%d%H'
            )
            valid_date_inc = int(job_env_dict['valid_hr_inc'])
            date_dt = valid_start_date_dt
            while date_dt <= valid_end_date_dt:
                ddate_dt = date_dt - datetime.timedelta(days=1)
                job_env_dict['DAILYSTART'] = ddate_dt.strftime('%Y%m%d')
                wdate_dt = date_dt - datetime.timedelta(days=7)
                job_env_dict['WEEKLYSTART'] = wdate_dt.strftime('%Y%m%d')
                mdate_dt = date_dt - datetime.timedelta(days=30)
                job_env_dict['MONTHLYSTART'] = mdate_dt.strftime('%Y%m%d')
                dys6_10date_dt = date_dt - datetime.timedelta(days=5)
                job_env_dict['D6_10START'] = dys6_10date_dt.strftime('%Y%m%d')
                w3_4date_dt = date_dt - datetime.timedelta(days=14)
                job_env_dict['W3_4START'] = w3_4date_dt.strftime('%Y%m%d')
                job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                job_env_dict['valid_hr_start'] = date_dt.strftime('%H')
                job_env_dict['valid_hr_end'] = date_dt.strftime('%H')
                for model_idx in range(len(model_list)):
                    job_env_dict['MODEL'] = model_list[model_idx]
                    njobs+=1
                    # Create job file
                    job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
                    print("Creating job script: "+job_file)
                    job = open(job_file, 'w')
                    job.write('#!/bin/bash\n')
                    job.write('set -x\n')
                    job.write('\n')
                    # Set any environment variables for special cases
                    if JOB_GROUP == 'assemble_data':
                        if verif_type == 'precip':
                            job_env_dict['MODEL_var'] = (
                                precip_var_list[model_idx]
                            )
                            if precip_file_accum_list[model_idx] \
                                    == 'continuous':
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
                    # Do file checks
                    all_truth_file_exist = False
                    model_files_exist = False
                    write_job_cmds = False
                    check_model_files = True
                    if check_model_files:
                        model_files_exist, valid_date_fhr_list = (
                            sub_util.check_model_files(job_env_dict)
                        )
                        job_env_dict['fhr_list'] = (
                            '"'+','.join(valid_date_fhr_list)+'"'
                        )
                        job_env_dict.pop('fhr_start')
                        job_env_dict.pop('fhr_end')
                        job_env_dict.pop('fhr_inc')
                    if JOB_GROUP == 'assemble_data':
                        check_truth_files = False
                    elif JOB_GROUP == 'generate_stats':
                        if verif_type in ['pres_lvls', 'anom'] \
                                and verif_type_job in [
                                    'WeeklyAvg_GeoHeightAnom',
                                    'Days6_10Avg_GeoHeightAnom',
                                    'Weeks3_4Avg_GeoHeightAnom',
                                    'WeeklyAvg_TempAnom2m',
                                    'Days6_10Avg_TempAnom2m',
                                    'Weeks3_4Avg_TempAnom2m']:
                            check_truth_files = False
                        else:
                            check_truth_files = True
                    if check_truth_files:
                        all_truth_file_exist = sub_util.check_truth_files(
                            job_env_dict
                        )
                        if model_files_exist and all_truth_file_exist:
                            write_job_cmds = True
                        else:
                            write_job_cmds = False
                    else:
                        if model_files_exist:
                            write_job_cmds = True
                        else:
                            write_job_cmds = False
                    # Write environment variables
                    for name, value in job_env_dict.items():
                        job.write('export '+name+'='+value+'\n')
                    job.write('\n')
                    # Write job commands
                    if write_job_cmds:
                        for cmd in verif_type_job_commands_list:
                            job.write(cmd+'\n')
                    job.close()
                    job_env_dict.pop('fhr_list')
                    job_env_dict['fhr_start'] = fhr_start
                    job_env_dict['fhr_end'] = fhr_end
                    job_env_dict['fhr_inc'] = fhr_inc
                date_dt = date_dt + datetime.timedelta(hours=valid_date_inc)
        # Do reformat_data and assemble_data observation jobs
        if JOB_GROUP in ['reformat_data', 'assemble_data']:
            if JOB_GROUP == 'reformat_data':
                JOB_GROUP_obs_jobs_dict = reformat_data_obs_jobs_dict
            elif JOB_GROUP == 'assemble_data':
                JOB_GROUP_obs_jobs_dict = assemble_data_obs_jobs_dict
            for verif_type_job in list(JOB_GROUP_obs_jobs_dict[verif_type]\
                                       .keys()):
                # Initialize job environment dictionary
                job_env_dict = sub_util.initalize_job_env_dict(
                    verif_type, JOB_GROUP, VERIF_CASE_STEP_abbrev_type,
                    verif_type_job
                )
                job_env_dict.pop('fhr_start')
                job_env_dict.pop('fhr_end')
                job_env_dict.pop('fhr_inc')
                # Add job specific environment variables
                for verif_type_job_env_var in \
                        list(JOB_GROUP_obs_jobs_dict[verif_type]\
                             [verif_type_job]['env'].keys()):
                    job_env_dict[verif_type_job_env_var] = (
                        JOB_GROUP_obs_jobs_dict[verif_type]\
                        [verif_type_job]['env'][verif_type_job_env_var]
                    )
                verif_type_job_commands_list = (
                    JOB_GROUP_obs_jobs_dict[verif_type]\
                    [verif_type_job]['commands']
                )
                # Loop through and write job script for dates and models
                valid_start_date_dt = datetime.datetime.strptime(
                    start_date+job_env_dict['valid_hr_start'],
                    '%Y%m%d%H'
                )
                valid_end_date_dt = datetime.datetime.strptime(
                    end_date+job_env_dict['valid_hr_end'],
                    '%Y%m%d%H'
                )
                valid_date_inc = int(job_env_dict['valid_hr_inc'])
                date_dt = valid_start_date_dt
                while date_dt <= valid_end_date_dt:
                    job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                    job_env_dict['valid_hr_start'] = date_dt.strftime('%H')
                    job_env_dict['valid_hr_end'] = date_dt.strftime('%H')
                    njobs+=1
                    # Create job file
                    job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
                    print("Creating job script: "+job_file)
                    job = open(job_file, 'w')
                    job.write('#!/bin/bash\n')
                    job.write('set -x\n')
                    job.write('\n')
                    # Set any environment variables for special cases
                    # Do file checks
                    all_truth_file_exist = sub_util.check_truth_files(
                        job_env_dict
                    )
                    if all_truth_file_exist:
                        write_job_cmds = True
                    else:
                        write_job_cmds = False
                    # Write environment variables
                    for name, value in job_env_dict.items():
                        job.write('export '+name+'='+value+'\n')
                    job.write('\n')
                    # Write job commands
                    if write_job_cmds:
                        for cmd in verif_type_job_commands_list:
                            job.write(cmd+'\n')
                    job.close()
                    date_dt = date_dt + datetime.timedelta(hours=valid_date_inc)
elif JOB_GROUP == 'gather_stats':
    print("----> Making job scripts for "+VERIF_CASE_STEP+" "
      +"for job group "+JOB_GROUP)
    # Initialize job environment dictionary
    job_env_dict = sub_util.initalize_job_env_dict(
        JOB_GROUP, JOB_GROUP,
        VERIF_CASE_STEP_abbrev, JOB_GROUP
    )
    # Loop through and write job script for dates and models
    date_dt = start_date_dt
    while date_dt <= end_date_dt:
        job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
        for model_idx in range(len(model_list)):
            job_env_dict['MODEL'] = model_list[model_idx]
            njobs+=1
            # Create job file
            job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
            print("Creating job script: "+job_file)
            job = open(job_file, 'w')
            job.write('#!/bin/bash\n')
            job.write('set -x\n')
            job.write('\n')
            # Set any environment variables for special cases
            # Write environment variables
            for name, value in job_env_dict.items():
                job.write('export '+name+'='+value+'\n')
            job.write('\n')
            # Do file checks
            stat_files_exist = sub_util.check_stat_files(job_env_dict)
            if stat_files_exist:
                write_job_cmds = True
            else:
                write_job_cmds = False
            # Write job commands
            if write_job_cmds:
                for cmd in gather_stats_jobs_dict['commands']:
                    job.write(cmd+'\n')
            job.close()
        date_dt = date_dt + datetime.timedelta(days=1)

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(DATA, VERIF_CASE_STEP,
                                       'METplus_job_scripts', JOB_GROUP,
                                       'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("WARNING: No job files created in "
              +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                            JOB_GROUP))
    poe_files = glob.glob(os.path.join(DATA, VERIF_CASE_STEP,
                                       'METplus_job_scripts', JOB_GROUP,
                                       'poe*'))
    npoe_files = len(poe_files)
    if npoe_files > 0:
        for poe_file in poe_files:
            os.remove(poe_file)
    njob, iproc, node = 1, 0, 1
    while njob <= njob_files:
        job = 'job'+str(njob)
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            if iproc >= int(nproc):
                iproc = 0
                node+=1
        poe_filename = os.path.join(DATA, VERIF_CASE_STEP,
                                    'METplus_job_scripts',
                                    JOB_GROUP, 'poe_jobs'+str(node))
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
               str(iproc-1)+' '
               +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                             JOB_GROUP, job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                             JOB_GROUP, job)+'\n'
            )
        poe_file.close()
        njob+=1
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(DATA, VERIF_CASE_STEP,
                                'METplus_job_scripts',
                                JOB_GROUP, 'poe_jobs'+str(node))
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
