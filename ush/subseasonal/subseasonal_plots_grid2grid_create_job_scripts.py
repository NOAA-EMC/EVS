#!/usr/bin/env python3
'''                           
Program Name: subseasonal_plots_grid2grid_create_job_scripts.py
Contact(s): Shannon Shields
Abstract: This script is run by exevs_subseasonal_grid2grid_plots.sh
          in scripts/plots/subseasonal.
          This creates multiple independent job scripts. These
          jobs contain all the necessary environment variables
          and commands needed to run the specific
          use case.
'''

import sys
import os
import glob
import datetime
import itertools
import numpy as np              
import subprocess               
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
PBS_NODEFILE = os.environ['PBS_NODEFILE']
VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
model_list = os.environ['model_list'].split(' ')

njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                  'plot_job_scripts', JOB_GROUP)
if not os.path.exists(JOB_GROUP_jobs_dir):
    os.makedirs(JOB_GROUP_jobs_dir)

################################################
#### Plotting jobs
################################################
plot_jobs_dict = {
    'temp': {
        'WeeklyAvg_TempAnom2m': {'line_type_stat_list': ['SL1L2/RMSE',
                                                         'SL1L2/ME'],
                                 'vx_mask_list': ['GLOBAL', 'CONUS',
                                                  'Alaska', 'Hawaii'],
                                 'fcst_var_dict': {'name': 'TMP_ANOM_WEEKLYAVG',
                                                   'levels': 'Z2',
                                                   'threshs': 'NA'},
                                 'obs_var_dict': {'name': 'TMP_ANOM_WEEKLYAVG',
                                                  'levels': 'Z2',
                                                  'threshs': 'NA'},
                                 'interp_dict': {'method': 'NEAREST',
                                                 'points': '1'},
                                 'fhr_start': '168',
                                 'fhr_end': '840',
                                 'fhr_inc': '168',
                                 'grid': 'G003',
                                 'obs_name': 'ecmwf',
                                 'plots_list': 'time_series, lead_average'},
        'Days6_10Avg_TempAnom2m': {'line_type_stat_list': ['SL1L2/RMSE',
                                                           'SL1L2/ME'],
                                   'vx_mask_list': ['GLOBAL', 'CONUS',
                                                    'Alaska', 'Hawaii'],
                                   'fcst_var_dict': {'name': 'TMP_ANOM_DAYS6_10AVG',
                                                     'levels': 'Z2',
                                                     'threshs': 'NA'},
                                   'obs_var_dict': {'name': 'TMP_ANOM_DAYS6_10AVG',
                                                    'levels': 'Z2',
                                                    'threshs': 'NA'},
                                   'interp_dict': {'method': 'NEAREST',
                                                   'points': '1'},
                                   'fhr_start': '240',
                                   'fhr_end': '240',
                                   'fhr_inc': '24',
                                   'grid': 'G003',
                                   'obs_name': 'ecmwf',
                                   'plots_list': 'time_series'},
        'Weeks3_4Avg_TempAnom2m': {'line_type_stat_list': ['SL1L2/RMSE',
                                                           'SL1L2/ME'],
                                   'vx_mask_list': ['GLOBAL', 'CONUS',
                                                    'Alaska', 'Hawaii'],
                                   'fcst_var_dict': {'name': 'TMP_ANOM_WEEKS3_4AVG',
                                                     'levels': 'Z2',
                                                     'threshs': 'NA'},
                                   'obs_var_dict': {'name': 'TMP_ANOM_WEEKS3_4AVG',
                                                    'levels': 'Z2',
                                                    'threshs': 'NA'},
                                   'interp_dict': {'method': 'NEAREST',
                                                   'points': '1'},
                                   'fhr_start': '672',
                                   'fhr_end': '672',
                                   'fhr_inc': '24',
                                   'grid': 'G003',
                                   'obs_name': 'ecmwf',
                                   'plots_list': 'time_series'},
        'WeeklyAvg_Temp2m': {'line_type_stat_list': ['SL1L2/RMSE',
                                                     'SL1L2/ME',
                                                     'SAL1L2/ACC'],
                             'vx_mask_list': ['GLOBAL', 'CONUS',
                                              'Alaska', 'Hawaii'],
                             'fcst_var_dict': {'name': 'TMP_WEEKLYAVG',
                                               'levels': 'Z2',
                                               'threshs': 'NA'},
                             'obs_var_dict': {'name': 'TMP_WEEKLYAVG',
                                              'levels': 'Z2',
                                              'threshs': 'NA'},
                             'interp_dict': {'method': 'NEAREST',
                                             'points': '1'},
                             'fhr_start': '168',
                             'fhr_end': '840',
                             'fhr_inc': '168',
                             'grid': 'G003',
                             'obs_name': 'ecmwf',
                             'plots_list': 'time_series, lead_average'},
        'Days6_10Avg_Temp2m': {'line_type_stat_list': ['SL1L2/RMSE',
                                                       'SL1L2/ME',
                                                       'SAL1L2/ACC'],
                               'vx_mask_list': ['GLOBAL', 'CONUS',
                                                'Alaska', 'Hawaii'],
                               'fcst_var_dict': {'name': 'TMP_DAYS6_10AVG',
                                                 'levels': 'Z2',
                                                 'threshs': 'NA'},
                               'obs_var_dict': {'name': 'TMP_DAYS6_10AVG',
                                                'levels': 'Z2',
                                                'threshs': 'NA'},
                               'interp_dict': {'method': 'NEAREST',
                                               'points': '1'},
                               'fhr_start': '240',
                               'fhr_end': '240',
                               'fhr_inc': '24',
                               'grid': 'G003',
                               'obs_name': 'ecmwf',
                               'plots_list': 'time_series'},
        'Weeks3_4Avg_Temp2m': {'line_type_stat_list': ['SL1L2/RMSE',
                                                       'SL1L2/ME',
                                                       'SAL1L2/ACC'],
                               'vx_mask_list': ['GLOBAL', 'CONUS',
                                                'Alaska', 'Hawaii'],
                               'fcst_var_dict': {'name': 'TMP_WEEKS3_4AVG',
                                                 'levels': 'Z2',
                                                 'threshs': 'NA'},
                               'obs_var_dict': {'name': 'TMP_WEEKS3_4AVG',
                                                'levels': 'Z2',
                                                'threshs': 'NA'},
                               'interp_dict': {'method': 'NEAREST',
                                               'points': '1'},
                               'fhr_start': '672',
                               'fhr_end': '672',
                               'fhr_inc': '24',
                               'grid': 'G003',
                               'obs_name': 'ecmwf',
                               'plots_list': 'time_series'},
    },
    'pres_lvls': {
        'WeeklyAvg_GeoHeightAnom': {'line_type_stat_list': ['SL1L2/RMSE',
                                                            'SL1L2/ME'],
                                    'vx_mask_list': ['NHEM', 'SHEM', 
                                                     'TROPICS', 'CONUS',
                                                     'Alaska', 'Hawaii'],
                                    'fcst_var_dict': {'name': 'HGT_ANOM_WEEKLYAVG',
                                                      'levels': 'P500',
                                                      'threshs': 'NA'},
                                    'obs_var_dict': {'name': 'HGT_ANOM_WEEKLYAVG',
                                                     'levels': 'P500',
                                                     'threshs': 'NA'},
                                    'interp_dict': {'method': 'NEAREST',
                                                    'points': '1'},
                                    'fhr_start': '168',
                                    'fhr_end': '840',
                                    'fhr_inc': '168',
                                    'grid': 'G003',
                                    'obs_name': 'gfs',
                                    'plots_list': 'time_series, lead_average'},
        'Days6_10Avg_GeoHeightAnom': {'line_type_stat_list': ['SL1L2/RMSE',
                                                              'SL1L2/ME'],
                                      'vx_mask_list': ['NHEM', 'SHEM',
                                                       'TROPICS', 'CONUS',
                                                       'Alaska', 'Hawaii'],
                                      'fcst_var_dict': {'name': 'HGT_ANOM_DAYS6_10AVG',
                                                        'levels': 'P500',
                                                        'threshs': 'NA'},
                                      'obs_var_dict': {'name': 'HGT_ANOM_DAYS6_10AVG',
                                                       'levels': 'P500',
                                                       'threshs': 'NA'},
                                      'interp_dict': {'method': 'NEAREST',
                                                      'points': '1'},
                                      'fhr_start': '240',
                                      'fhr_end': '240',
                                      'fhr_inc': '24',
                                      'grid': 'G003',
                                      'obs_name': 'gfs',
                                      'plots_list': 'time_series'},
        'Weeks3_4Avg_GeoHeightAnom': {'line_type_stat_list': ['SL1L2/RMSE',
                                                              'SL1L2/ME'],
                                      'vx_mask_list': ['NHEM', 'SHEM',
                                                       'TROPICS', 'CONUS',
                                                       'Alaska', 'Hawaii'],
                                      'fcst_var_dict': {'name': 'HGT_ANOM_WEEKS3_4AVG',
                                                        'levels': 'P500',
                                                        'threshs': 'NA'},
                                      'obs_var_dict': {'name': 'HGT_ANOM_WEEKS3_4AVG',
                                                       'levels': 'P500',
                                                       'threshs': 'NA'},
                                      'interp_dict': {'method': 'NEAREST',
                                                      'points': '1'},
                                      'fhr_start': '672',
                                      'fhr_end': '672',
                                      'fhr_inc': '24',
                                      'grid': 'G003',
                                      'obs_name': 'gfs',
                                      'plots_list': 'time_series'},
        'WeeklyAvg_GeoHeight': {'line_type_stat_list': ['SL1L2/RMSE',
                                                        'SL1L2/ME',
                                                        'SAL1L2/ACC'],
                                'vx_mask_list': ['NHEM', 'SHEM',
                                                 'TROPICS', 'CONUS',
                                                 'Alaska', 'Hawaii'],
                                'fcst_var_dict': {'name': 'HGT_WEEKLYAVG',
                                                  'levels': 'P500',
                                                  'threshs': 'NA'},
                                'obs_var_dict': {'name': 'HGT_WEEKLYAVG',
                                                 'levels': 'P500',
                                                 'threshs': 'NA'},
                                'interp_dict': {'method': 'NEAREST',
                                                'points': '1'},
                                'fhr_start': '168',
                                'fhr_end': '840',
                                'fhr_inc': '168',
                                'grid': 'G003',
                                'obs_name': 'gfs',
                                'plots_list': 'time_series, lead_average'},
        'Days6_10Avg_GeoHeight': {'line_type_stat_list': ['SL1L2/RMSE',
                                                          'SL1L2/ME',
                                                          'SAL1L2/ACC'],
                                  'vx_mask_list': ['NHEM', 'SHEM',
                                                   'TROPICS', 'CONUS',
                                                   'Alaska', 'Hawaii'],
                                  'fcst_var_dict': {'name': 'HGT_DAYS6_10AVG',
                                                    'levels': 'P500',
                                                    'threshs': 'NA'},
                                  'obs_var_dict': {'name': 'HGT_DAYS6_10AVG',
                                                   'levels': 'P500',
                                                   'threshs': 'NA'},
                                  'interp_dict': {'method': 'NEAREST',
                                                  'points': '1'},
                                  'fhr_start': '240',
                                  'fhr_end': '240',
                                  'fhr_inc': '24',
                                  'grid': 'G003',
                                  'obs_name': 'gfs',
                                  'plots_list': 'time_series'},
        'Weeks3_4Avg_GeoHeight': {'line_type_stat_list': ['SL1L2/RMSE',
                                                          'SL1L2/ME',
                                                          'SAL1L2/ACC'],
                                  'vx_mask_list': ['NHEM', 'SHEM',
                                                   'TROPICS', 'CONUS',
                                                   'Alaska', 'Hawaii'],
                                  'fcst_var_dict': {'name': 'HGT_WEEKS3_4AVG',
                                                    'levels': 'P500',
                                                    'threshs': 'NA'},
                                  'obs_var_dict': {'name': 'HGT_WEEKS3_4AVG',
                                                   'levels': 'P500',
                                                   'threshs': 'NA'},
                                  'interp_dict': {'method': 'NEAREST',
                                                  'points': '1'},
                                  'fhr_start': '672',
                                  'fhr_end': '672',
                                  'fhr_inc': '24',
                                  'grid': 'G003',
                                  'obs_name': 'gfs',
                                  'plots_list': 'time_series'},
    },
    'sea_ice': {
        'WeeklyAvg_Concentration': {'line_type_stat_list': ['SL1L2/RMSE',
                                                            'SL1L2/ME'],
                                    'vx_mask_list': ['ARCTIC', 'ANTARCTIC'],
                                    'fcst_var_dict': {'name': 'ICEC_WEEKLYAVG',
                                                      'levels': 'Z0',
                                                      'threshs': 'NA'},
                                    'obs_var_dict': {'name': 'ice_conc',
                                                     'levels': "'*,*'",
                                                     'threshs': 'NA'},
                                    'interp_dict': {'method': 'NEAREST',
                                                    'points': '1'},
                                    'fhr_start': '168',
                                    'fhr_end': '840',
                                    'fhr_inc': '168',
                                    'grid': 'G003',
                                    'obs_name': 'osi_saf',
                                    'plots_list': 'time_series, lead_average'},
        'WeeklyAvg_Concentration_Thresh': {'line_type_stat_list': ['CTC/CSI'],
                                           'vx_mask_list': ['ARCTIC',
                                                            'ANTARCTIC'],
                                           'fcst_var_dict': {'name': (
                                                                 'ICEC_WEEKLYAVG'
                                                             ),
                                                             'levels': 'Z0',
                                                             'threshs': ('ge15, '
                                                                         +'ge40, '
                                                                         +'ge80')},
                                           'obs_var_dict': {'name': 'ice_conc',
                                                            'levels': "'*,*'",
                                                            'threshs': ('ge15, '
                                                                        +'ge40, '
                                                                        +'ge80')},
                                           'interp_dict': {'method': 'NEAREST',
                                                           'points': '1'},
                                           'fhr_start': '168',
                                           'fhr_end': '840',
                                           'fhr_inc': '168',
                                           'grid': 'G003',
                                           'obs_name': 'osi_saf',
                                           'plots_list': ('time_series, '
                                                          +'lead_average')},
        'WeeklyAvg_Concentration_PerfDia': {'line_type_stat_list': \
                                                ['CTC/PERF_DIA'],
                                            'vx_mask_list': \
                                                ['ARCTIC', 'ANTARCTIC'],
                                            'fcst_var_dict': \
                                                {'name': 'ICEC_WEEKLYAVG',
                                                 'levels': 'Z0',
                                                 'threshs': ('ge15, ge40, '
                                                             +'ge80')},
                                            'obs_var_dict': \
                                                {'name': 'ice_conc',
                                                 'levels': "'*,*'",
                                                 'threshs': ('ge15, ge40, '
                                                             +'ge80')},
                                            'interp_dict': {'method': 'NEAREST',
                                                            'points': '1'},
                                            'fhr_start': '168',
                                            'fhr_end': '840',
                                            'fhr_inc': '168',
                                            'grid': 'G003',
                                            'obs_name': 'osi_saf',
                                            'plots_list': 'performance_diagram'},
        'MonthlyAvg_Concentration': {'line_type_stat_list': ['SL1L2/RMSE',
                                                             'SL1L2/ME'],
                                     'vx_mask_list': ['ARCTIC', 'ANTARCTIC'],
                                     'fcst_var_dict': {'name': 'ICEC_MONTHLYAVG',
                                                       'levels': 'Z0',
                                                       'threshs': 'NA'},
                                     'obs_var_dict': {'name': 'ice_conc',
                                                      'levels': "'*,*'",
                                                      'threshs': 'NA'},
                                     'interp_dict': {'method': 'NEAREST',
                                                     'points': '1'},
                                     'fhr_start': '720',
                                     'fhr_end': '720',
                                     'fhr_inc': '24',
                                     'grid': 'G003',
                                     'obs_name': 'osi_saf',
                                     'plots_list': 'time_series'},
        'MonthlyAvg_Concentration_Thresh': {'line_type_stat_list': ['CTC/CSI'],
                                            'vx_mask_list': ['ARCTIC',
                                                             'ANTARCTIC'],
                                            'fcst_var_dict': {'name': (
                                                                  'ICEC_MONTHLYAVG'
                                                              ),
                                                              'levels': 'Z0',
                                                              'threshs': ('ge15, '
                                                                          +'ge40, '
                                                                          +'ge80')},
                                            'obs_var_dict': {'name': 'ice_conc',
                                                             'levels': "'*,*'",
                                                             'threshs': ('ge15, '
                                                                         +'ge40, '
                                                                         +'ge80')},
                                            'interp_dict': {'method': 'NEAREST',
                                                            'points': '1'},
                                            'fhr_start': '720',
                                            'fhr_end': '720',
                                            'fhr_inc': '24',
                                            'grid': 'G003',
                                            'obs_name': 'osi_saf',
                                            'plots_list': 'time_series'},
        'MonthlyAvg_Concentration_PerfDia': {'line_type_stat_list': \
                                                 ['CTC/PERF_DIA'],
                                             'vx_mask_list': \
                                                 ['ARCTIC', 'ANTARCTIC'],
                                             'fcst_var_dict': \
                                                 {'name': 'ICEC_MONTHLYAVG',
                                                  'levels': 'Z0',
                                                  'threshs': ('ge15, ge40, '
                                                              +'ge80')},
                                             'obs_var_dict': \
                                                 {'name': 'ice_conc',
                                                  'levels': "'*,*'",
                                                  'threshs': ('ge15, ge40, '
                                                              +'ge80')},
                                             'interp_dict': {'method': 'NEAREST',
                                                             'points': '1'},
                                             'fhr_start': '720',
                                             'fhr_end': '720',
                                             'fhr_inc': '24',
                                             'grid': 'G003',
                                             'obs_name': 'osi_saf',
                                             'plots_list': 'performance_diagram'},
    },
    'sst': {
        'DailyAvg_SST': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/ME'],
                         'vx_mask_list': ['NHEM', 'SHEM', 'TROPICS'],
                         'fcst_var_dict': {'name': 'SST_DAILYAVG',
                                           'levels': 'Z0',
                                           'threshs': 'NA'},
                         'obs_var_dict': {'name': 'analysed_sst',
                                          'levels': "'0,*,*'",
                                          'threshs': 'NA'},
                         'interp_dict': {'method': 'NEAREST',
                                         'points': '1'},
                         'fhr_start': '24',
                         'fhr_end': '840',
                         'fhr_inc': '24',
                         'grid': 'G003',
                         'obs_name': 'ghrsst_ospo',
                         'plots_list': 'time_series, lead_average'},
        'WeeklyAvg_SST': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/ME'],
                          'vx_mask_list': ['NHEM', 'SHEM', 'TROPICS'],
                          'fcst_var_dict': {'name': 'SST_WEEKLYAVG',
                                            'levels': 'Z0',
                                            'threshs': 'NA'},
                          'obs_var_dict': {'name': 'analysed_sst',
                                           'levels': "'0,*,*'",
                                           'threshs': 'NA'},
                          'interp_dict': {'method': 'NEAREST',
                                          'points': '1'},
                          'fhr_start': '168',
                          'fhr_end': '840',
                          'fhr_inc': '168',
                          'grid': 'G003',
                          'obs_name': 'ghrsst_ospo',
                          'plots_list': 'time_series, lead_average'},
        'MonthlyAvg_SST': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/ME'],
                           'vx_mask_list': ['NHEM', 'SHEM', 'TROPICS'],
                           'fcst_var_dict': {'name': 'SST_MONTHLYAVG',
                                             'levels': 'Z0',
                                             'threshs': 'NA'},
                           'obs_var_dict': {'name': 'analysed_sst',
                                            'levels': "'0,*,*'",
                                            'threshs': 'NA'},
                           'interp_dict': {'method': 'NEAREST',
                                           'points': '1'},
                           'fhr_start': '720',
                           'fhr_end': '720',
                           'fhr_inc': '24',
                           'grid': 'G003',
                           'obs_name': 'ghrsst_ospo',
                           'plots_list': 'time_series'},
    }
}
for verif_type in VERIF_CASE_STEP_type_list:
    print("----> Making job scripts for "+VERIF_CASE_STEP+" "
          +verif_type+" for job group "+JOB_GROUP)
    VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                   +verif_type)
    model_plot_name_list = (
        os.environ[VERIF_CASE_STEP_abbrev+'_model_plot_name_list'].split(' ')
    )
    verif_type_plot_jobs_dict = plot_jobs_dict[verif_type]
    for verif_type_job in list(verif_type_plot_jobs_dict.keys()):
        obs_list = [
            verif_type_plot_jobs_dict[verif_type_job]['obs_name']
            for m in model_list
        ]
        fcst_var_levels = (verif_type_plot_jobs_dict[verif_type_job]\
                           ['fcst_var_dict']['levels'].split(', '))
        fcst_var_threshs = (verif_type_plot_jobs_dict[verif_type_job]\
                            ['fcst_var_dict']['threshs'].split(', '))
        obs_var_levels = (verif_type_plot_jobs_dict[verif_type_job]\
                          ['obs_var_dict']['levels'].split(', '))
        obs_var_threshs = (verif_type_plot_jobs_dict[verif_type_job]\
                           ['obs_var_dict']['threshs'].split(', '))
        # Initialize job environment dictionary
        job_env_dict = sub_util.initialize_job_env_dict(
            verif_type, JOB_GROUP,
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        job_env_dict['event_equalization'] = (
            os.environ[VERIF_CASE_STEP_abbrev+'_event_eq']
        )
        job_env_dict['fhr_start'] = (
            verif_type_plot_jobs_dict[verif_type_job]['fhr_start']
        )
        job_env_dict['fhr_end'] = (
            verif_type_plot_jobs_dict[verif_type_job]['fhr_end']
        )
        job_env_dict['fhr_inc'] = (
            verif_type_plot_jobs_dict[verif_type_job]['fhr_inc']
        )
        job_env_dict['start_date'] = start_date
        job_env_dict['end_date'] = end_date
        job_env_dict['date_type'] = 'VALID'
        job_env_dict['grid'] = (
            verif_type_plot_jobs_dict[verif_type_job]['grid']
        )
        job_env_dict['interp_method'] = (
            verif_type_plot_jobs_dict[verif_type_job]\
            ['interp_dict']['method']
        )
        job_env_dict['interp_points_list'] = ("'"+
            verif_type_plot_jobs_dict[verif_type_job]\
            ['interp_dict']['points']
        +"'")
        valid_hr_start = int(job_env_dict['valid_hr_start'])
        valid_hr_end = int(job_env_dict['valid_hr_end'])
        valid_hr_inc = int(job_env_dict['valid_hr_inc'])
        valid_hrs = list(range(valid_hr_start,
                               valid_hr_end+valid_hr_inc,
                               valid_hr_inc))
        for data_name in ['fcst', 'obs']:
            job_env_dict[data_name+'_var_name'] =  (
                verif_type_plot_jobs_dict[verif_type_job]\
                [data_name+'_var_dict']['name']
            )
        verif_type_job_loop_list = []
        for line_type_stat \
                in verif_type_plot_jobs_dict[verif_type_job]\
                ['line_type_stat_list']:
            if JOB_GROUP in ['condense_stats', 'filter_stats', 'tar_images']:
                if line_type_stat.split('/')[0] not in verif_type_job_loop_list:
                    verif_type_job_loop_list.append(line_type_stat.split('/')[0])
            else:
                verif_type_job_loop_list.append(line_type_stat)
        for verif_type_job_loop in list(
                itertools.product(verif_type_job_loop_list,
                                  verif_type_plot_jobs_dict[verif_type_job]\
                                  ['vx_mask_list'])
        ):
            if '/' in verif_type_job_loop[0]:
                job_env_dict['line_type'] = (
                    verif_type_job_loop[0].split('/')[0]
                )
                job_env_dict['stat'] = (
                    verif_type_job_loop[0].split('/')[1]
                )
            else:
                job_env_dict['line_type'] = verif_type_job_loop[0]
            job_env_dict['vx_mask'] = verif_type_job_loop[1]
            job_env_dict['job_name'] = (
                job_env_dict['line_type']+'/'
                +verif_type_job+'/'
                +job_env_dict['vx_mask']
            )
            job_output_dir = os.path.join(
                DATA, VERIF_CASE+'_'+STEP, 'plot_output',
                RUN+'.'+end_date, verif_type,
                job_env_dict['job_name'].replace('/','_')
            )
            if not os.path.exists(job_output_dir):
                os.makedirs(job_output_dir)
            if JOB_GROUP == 'condense_stats':
                for JOB_GROUP_loop in list(
                    itertools.product(model_list, [fcst_var_levels],
                                      [fcst_var_threshs])
                ):
                    job_env_dict['model_list'] = "'"+f"{JOB_GROUP_loop[0]}"+"'"
                    job_env_dict['model_plot_name_list'] = (
                        "'"+f"{model_plot_name_list[model_list.index(JOB_GROUP_loop[0])]}"+"'"
                    )
                    job_env_dict['obs_list'] = (
                        "'"+f"{obs_list[model_list.index(JOB_GROUP_loop[0])]}"+"'"
                    )
                    job_env_dict['fcst_var_level_list'] = (
                        "'"+f"{', '.join(JOB_GROUP_loop[1])}"+"'"
                    )
                    job_env_dict['fcst_var_thresh_list'] = (
                        "'"+f"{', '.join(JOB_GROUP_loop[2])}"+"'"
                    )
                    job_env_dict['obs_var_level_list'] = (
                        "'"+f"{', '.join(obs_var_levels)}"+"'"
                    )
                    job_env_dict['obs_var_thresh_list'] = (
                        "'"+f"{', '.join(obs_var_threshs)}"+"'"
                    )
                    job_env_dict['valid_hr_inc'] = '24'
                    # Create job file
                    njobs+=1
                    job_file = os.path.join(JOB_GROUP_jobs_dir, 
                                            'job'+str(njobs))
                    print("Creating job script: "+job_file)
                    job = open(job_file, 'w')
                    job.write('#!/bin/bash\n')
                    job.write('set -x\n')
                    job.write('\n')
                    # Set any environment variables for special cases
                    # Write environment variables
                    job_env_dict['job_id'] = 'job'+str(njobs)
                    for name, value in job_env_dict.items():
                        job.write('export '+name+'='+value+'\n')
                    job.write('\n')
                    # Write job commands
                    job.write(
                        sub_util.python_command('subseasonal_plots.py',[])
                        +'\n'
                    )
                    job.write('export err=$?; err_chk'+'\n')
                    job.close()
            elif JOB_GROUP == 'filter_stats':
                for JOB_GROUP_loop in list(
                    itertools.product(model_list, fcst_var_levels,
                                      fcst_var_threshs, valid_hrs)
                ):
                    job_env_dict['model_list'] = "'"+f"{JOB_GROUP_loop[0]}"+"'"
                    job_env_dict['model_plot_name_list'] = (
                        "'"+f"{model_plot_name_list[model_list.index(JOB_GROUP_loop[0])]}"+"'"
                    )
                    job_env_dict['obs_list'] = (
                        "'"+f"{obs_list[model_list.index(JOB_GROUP_loop[0])]}"+"'"
                    )
                    job_env_dict['fcst_var_level_list'] = (
                        "'"+f"{JOB_GROUP_loop[1]}"+"'"
                    )
                    job_env_dict['fcst_var_thresh_list'] = (
                        "'"+f"{JOB_GROUP_loop[2]}"+"'"
                    )
                    job_env_dict['obs_var_level_list'] = (
                        "'"+f"{obs_var_levels[fcst_var_levels.index(JOB_GROUP_loop[1])]}"+"'"
                    )
                    job_env_dict['obs_var_thresh_list'] = (
                        "'"+f"{obs_var_threshs[fcst_var_threshs.index(JOB_GROUP_loop[2])]}"+"'"
                    )
                    job_env_dict['valid_hr_start'] = (
                        str(JOB_GROUP_loop[3]).zfill(2)
                    )
                    job_env_dict['valid_hr_end'] = (
                        job_env_dict['valid_hr_start']
                    )
                    job_env_dict['valid_hr_inc'] = '24'
                    # Create job file
                    njobs+=1
                    job_file = os.path.join(JOB_GROUP_jobs_dir,
                                            'job'+str(njobs))
                    print("Creating job script: "+job_file)
                    job = open(job_file, 'w')
                    job.write('#!/bin/bash\n')
                    job.write('set -x\n')
                    job.write('\n')
                    # Write environment variables
                    job_env_dict['job_id'] = 'job'+str(njobs)
                    for name, value in job_env_dict.items():
                        job.write('export '+name+'='+value+'\n')
                    job.write('\n')
                    job.write(
                        sub_util.python_command('subseasonal_plots.py',[])
                        +'\n'
                    )
                    job.write('export err=$?; err_chk'+'\n')
                    job.close()
            elif JOB_GROUP == 'make_plots':
                job_output_images_dir = os.path.join(
                    DATA, VERIF_CASE+'_'+STEP, 'plot_output',
                    RUN+'.'+end_date, verif_type,
                    job_env_dict['job_name'].replace('/','_'), 'images'
                )
                if not os.path.exists(job_output_images_dir):
                    os.makedirs(job_output_images_dir)
                job_env_dict['model_list'] = "'"+f"{', '.join(model_list)}"+"'"
                job_env_dict['model_plot_name_list'] = (
                    "'"+f"{', '.join(model_plot_name_list)}"+"'"
                )
                job_env_dict['obs_list'] = (
                    "'"+f"{', '.join(obs_list)}"+"'"
                )
                for plot in verif_type_plot_jobs_dict\
                        [verif_type_job]['plots_list'].split(', '):
                    job_env_dict['plot'] = plot
                    if plot == 'valid_hour_average':
                        plot_valid_hrs_loop = [valid_hrs]
                    else:
                        plot_valid_hrs_loop = valid_hrs
                    if plot in ['threshold_average', 'performance_diagram']:
                        plot_fcst_threshs_loop = [fcst_var_threshs]
                    else:
                        plot_fcst_threshs_loop = fcst_var_threshs
                    if plot in ['stat_by_level', 'lead_by_level']:
                        plot_fcst_levels_loop = ['all', 'trop', 'strat',
                                                 'ltrop', 'utrop']
                    else:
                        plot_fcst_levels_loop = fcst_var_levels
                    for JOB_GROUP_loop in list(
                        itertools.product(plot_valid_hrs_loop,
                                          plot_fcst_threshs_loop,
                                          plot_fcst_levels_loop)
                    ):
                        if plot == 'valid_hour_average':
                            job_env_dict['valid_hr_start'] = str(
                                JOB_GROUP_loop[0][0]
                            ).zfill(2)
                            job_env_dict['valid_hr_end'] = str(
                                JOB_GROUP_loop[0][-1]
                            ).zfill(2)
                            job_env_dict['valid_hr_inc'] = str(valid_hr_inc)
                        else:
                            job_env_dict['valid_hr_start'] = str(
                                JOB_GROUP_loop[0]
                            ).zfill(2)
                            job_env_dict['valid_hr_end'] = str(
                                JOB_GROUP_loop[0]
                            ).zfill(2)
                            job_env_dict['valid_hr_inc'] = '24'
                        if plot in ['threshold_average',
                                    'performance_diagram']:
                            job_env_dict['fcst_var_thresh_list'] = (
                                "'"+f"{', '.join(JOB_GROUP_loop[1])}"+"'"
                            )
                            job_env_dict['obs_var_thresh_list'] = (
                                "'"+f"{', '.join(obs_var_threshs)}"+"'"
                            )
                        else:
                            job_env_dict['fcst_var_thresh_list'] = (
                                "'"+f"{JOB_GROUP_loop[1]}"+"'"
                            )
                            job_env_dict['obs_var_thresh_list'] = (
                                "'"+f"{obs_var_threshs[fcst_var_threshs.index(JOB_GROUP_loop[1])]}"+"'"
                            )
                        if plot in ['stat_by_level', 'lead_by_level']:
                            job_env_dict['vert_profile'] = (
                                "'"+f"{JOB_GROUP_loop[2]}"+"'"
                            )
                            job_env_dict['fcst_var_level_list'] = (
                                "'"+f"{', '.join(fcst_var_levels)}"+"'"
                            )
                            job_env_dict['obs_var_level_list'] = (
                                "'"+f"{', '.join(obs_var_levels)}"+"'"
                            )
                        else:
                            job_env_dict['fcst_var_level_list'] = (
                                "'"+f"{JOB_GROUP_loop[2]}"+"'"
                            )
                            job_env_dict['obs_var_level_list'] = (
                                "'"+f"{obs_var_levels[fcst_var_levels.index(JOB_GROUP_loop[2])]}"+"'"
                            )
                        run_subseasonal_plots = ['subseasonal_plots.py']
                        for run_subseasonal_plot in run_subseasonal_plots:
                            # Create job file
                            njobs+=1
                            job_file = os.path.join(JOB_GROUP_jobs_dir,
                                                    'job'+str(njobs))
                            print("Creating job script: "+job_file)
                            job = open(job_file, 'w')
                            job.write('#!/bin/bash\n')
                            job.write('set -x\n')
                            job.write('\n')
                            # Write environment variables
                            job_env_dict['job_id'] = 'job'+str(njobs)
                            for name, value in job_env_dict.items():
                                job.write('export '+name+'='+value+'\n')
                            job.write('\n')
                            job.write(
                                sub_util.python_command(run_subseasonal_plot,
                                                        [])+'\n'
                            )
                            job.write('export err=$?; err_chk'+'\n')
                            job.close()
            elif JOB_GROUP == 'tar_images':
                job_env_dict['model_list'] = "'"+f"{', '.join(model_list)}"+"'"
                job_env_dict['model_plot_name_list'] = (
                    "'"+f"{', '.join(model_plot_name_list)}"+"'"
                )
                job_env_dict['obs_list'] = (
                    "'"+f"{', '.join(obs_list)}"+"'"
                )
                job_env_dict['fcst_var_level_list'] = (
                    "'"+f"{', '.join(fcst_var_levels)}"+"'"
                )
                job_env_dict['fcst_var_thresh_list'] = (
                    "'"+f"{', '.join(fcst_var_threshs)}"+"'"
                )
                job_env_dict['obs_var_level_list'] = (
                    "'"+f"{', '.join(obs_var_levels)}"+"'"
                )
                job_env_dict['obs_var_thresh_list'] = (
                    "'"+f"{', '.join(obs_var_threshs)}"+"'"
                )
                job_env_dict['valid_hr_inc'] = '24'
                # Create job file
                njobs+=1
                job_file = os.path.join(JOB_GROUP_jobs_dir,
                                        'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/bash\n')
                job.write('set -x\n')
                job.write('\n')
                # Write environment variables
                job_env_dict['job_id'] = 'job'+str(njobs)
                for name, value in job_env_dict.items():
                    job.write('export '+name+'='+value+'\n')
                job.write('\n')
                job.write(
                    sub_util.python_command('subseasonal_plots.py',[])
                    +'\n'
                )
                job.write('export err=$?; err_chk'+'\n')
                job.close()

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("FATAL ERROR: No job files created in "+JOB_GROUP_jobs_dir)
        sys.exit(1)
    poe_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'poe*'))
    npoe_files = len(poe_files)
    if npoe_files > 0:
        for poe_file in poe_files:
            os.remove(poe_file)
    njob, iproc, node = 1, 0, 1
    while njob <= njob_files:
        job = 'job'+str(njob)
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            if iproc >= int(nproc):
                poe_file.close()
                iproc = 0
                node+=1
        poe_filename = os.path.join(JOB_GROUP_jobs_dir,
                                    'poe_jobs'+str(node))
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
                str(iproc-1)+' '
                +os.path.join(JOB_GROUP_jobs_dir, job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(JOB_GROUP_jobs_dir, job)+'\n'
            )
        poe_file.close()
        njob+=1
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(JOB_GROUP_jobs_dir,
                                'poe_jobs'+str(node))
    poe_file = open(poe_filename, 'a')
    if machine == 'WCOSS2':
        nselect = subprocess.check_output(
            'cat '+PBS_NODEFILE+'| wc -l', shell=True, encoding='UTF-8'
        ).replace('\n', '')
        nnp = int(nselect) * int(nproc)
    else:
        nnp = nproc
    iproc+=1
    while iproc <= int(nnp):
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

