'''
Program Name: global_det_atmos_plots_grid2grid_create_job_scripts.py
Contact(s): Mallory Row
Abstract: This creates multiple independent job scripts. These
          jobs contain all the necessary environment variables
          and commands to needed to run the specific
          use case.
'''

import sys
import os
import glob
import datetime
import itertools
import numpy as np
import subprocess
import copy
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMOUT = os.environ['COMOUT']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
evs_run_mode = os.environ['evs_run_mode']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
NDAYS = str(os.environ['NDAYS'])
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
PBS_NODEFILE = os.environ['PBS_NODEFILE']
VERIF_CASE_STEP = VERIF_CASE+'_'+STEP

njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                  'plot_job_scripts', JOB_GROUP)
if not os.path.exists(JOB_GROUP_jobs_dir):
    os.makedirs(JOB_GROUP_jobs_dir)

################################################
#### Base/Common Plotting Information
################################################
base_plot_jobs_info_dict = {
    'flux': {},
    'means': {
        'CAPESfcBased': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                      'CONUS', 'N60N90', 'S60S90', 'NAO',
                                      'SAO', 'NPO', 'SPO'],
                         'fcst_var_dict': {'name': 'CAPE',
                                           'levels': ['Z0']},
                         'obs_var_dict': {'name': 'CAPE',
                                          'levels': ['Z0']}},
        'CloudWater': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                    'CONUS', 'N60N90', 'S60S90', 'NAO', 'SAO',
                                    'NPO', 'SPO'],
                       'fcst_var_dict': {'name': 'CWAT',
                                         'levels': ['L0']},
                       'obs_var_dict': {'name': 'CWAT',
                                        'levels': ['L0']}},
        'GeoHeightTropopause': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM',
                                             'TROPICS', 'CONUS', 'N60N90',
                                             'S60S90', 'NAO', 'SAO', 'NPO',
                                             'SPO'],
                                'fcst_var_dict': {'name': 'HGT',
                                                  'levels': ['TROPOPAUSE']},
                                'obs_var_dict': {'name': 'HGT',
                                                 'levels': ['TROPOPAUSE']}},
        'PBLHeight': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                   'CONUS', 'N60N90', 'S60S90', 'NAO', 'SAO',
                                   'NPO', 'SPO'],
                      'fcst_var_dict': {'name': 'HPBL',
                                        'levels': ['L0']},
                      'obs_var_dict': {'name': 'HPBL',
                                       'levels': ['L0']}},
        'PrecipWater': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                     'CONUS', 'N60N90', 'S60S90', 'NAO', 'SAO',
                                     'NPO', 'SPO'],
                        'fcst_var_dict': {'name': 'PWAT',
                                          'levels': ['L0']},
                        'obs_var_dict': {'name': 'PWAT',
                                         'levels': ['L0']}},
        'PresSeaLevel': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                      'CONUS', 'N60N90', 'S60S90', 'NAO',
                                      'SAO', 'NPO', 'SPO'],
                         'fcst_var_dict': {'name': 'PRMSL',
                                           'levels': ['Z0']},
                         'obs_var_dict': {'name': 'PRMSL',
                                          'levels': ['Z0']}},
        'PresSfc': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS',
                                 'N60N90', 'S60S90', 'NAO', 'SAO', 'NPO',
                                 'SPO'],
                    'fcst_var_dict': {'name': 'PRES',
                                      'levels': ['Z0']},
                    'obs_var_dict': {'name': 'PRES',
                                     'levels': 'Z0'}},
        'PresTropopause': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                        'CONUS', 'N60N90', 'S60S90', 'NAO',
                                        'SAO', 'NPO', 'SPO'],
                           'fcst_var_dict': {'name': 'PRES',
                                             'levels': ['TROPOPAUSE']},
                           'obs_var_dict': {'name': 'PRES',
                                            'levels': ['TROPOPAUSE']}},
        'RelHum2m': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS',
                                  'N60N90', 'S60S90', 'NAO', 'SAO', 'NPO',
                                  'SPO'],
                     'fcst_var_dict': {'name': 'RH',
                                       'levels': ['Z2']},
                     'obs_var_dict': {'name': 'RH',
                                      'levels': ['Z2']}},
        'SnowWaterEqv': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                      'CONUS', 'N60N90', 'S60S90', 'NAO',
                                      'SAO', 'NPO', 'SPO'],
                         'fcst_var_dict': {'name': 'WEASD',
                                           'levels': ['Z0']},
                         'obs_var_dict': {'name': 'WEASD',
                                          'levels': ['Z0']}},
        'SpefHum2m': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                   'CONUS', 'N60N90', 'S60S90', 'NAO', 'SAO',
                                   'NPO', 'SPO'],
                      'fcst_var_dict': {'name': 'SPFH',
                                        'levels': ['Z2']},
                      'obs_var_dict': {'name': 'SPFH',
                                       'levels': ['Z2']}},
        'Temp2m': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS',
                                'N60N90', 'S60S90', 'NAO', 'SAO', 'NPO',
                                'SPO'],
                   'fcst_var_dict': {'name': 'TMP',
                                     'levels': ['Z2']},
                   'obs_var_dict': {'name': 'TMP',
                                    'levels': ['Z2']}},
        'TempTropopause': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                        'CONUS', 'N60N90', 'S60S90', 'NAO',
                                        'SAO', 'NPO', 'SPO'],
                           'fcst_var_dict': {'name': 'TMP',
                                             'levels': ['TROPOPAUSE']},
                           'obs_var_dict': {'name': 'TMP',
                                            'levels': ['TROPOPAUSE']}},
        'TempSoilTopLayer': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                          'CONUS', 'N60N90', 'S60S90', 'NAO',
                                          'SAO', 'NPO', 'SPO'],
                             'fcst_var_dict': {'name': 'TSOIL',
                                               'levels': ['Z0.1-0']},
                             'obs_var_dict': {'name': 'TSOIL',
                                              'levels': ['Z0.1-0']}},
        'TotalOzone': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                    'CONUS', 'N60N90', 'S60S90', 'NAO', 'SAO',
                                    'NPO', 'SPO'],
                       'fcst_var_dict': {'name': 'TOZNE',
                                         'levels': ['L0']},
                       'obs_var_dict': {'name': 'TOZNE',
                                        'levels': ['L0']}},
        'UWind10m': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS',
                                  'N60N90', 'S60S90', 'NAO', 'SAO', 'NPO',
                                  'SPO'],
                     'fcst_var_dict': {'name': 'UGRD',
                                       'levels': ['Z10']},
                     'obs_var_dict': {'name': 'UGRD',
                                      'levels': ['Z10']}},
        'VolSoilMoistTopLayer': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM',
                                              'TROPICS', 'CONUS', 'N60N90',
                                              'S60S90', 'NAO', 'SAO', 'NPO',
                                              'SPO'],
                                 'fcst_var_dict': {'name': 'SOILW',
                                                   'levels': ['Z0.1-0']},
                                 'obs_var_dict': {'name': 'SOILW',
                                                  'levels': ['Z0.1-0']}},
        'VWind10m': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS',
                                  'N60N90', 'S60S90', 'NAO', 'SAO', 'NPO',
                                  'SPO'],
                     'fcst_var_dict': {'name': 'VGRD',
                                       'levels': ['Z10']},
                     'obs_var_dict': {'name': 'VGRD',
                                      'levels': ['Z10']}},
    },
    'ozone': {},
    'precip': {
        '24hrCCPA': {'vx_masks': ['CONUS', 'CONUS_East', 'CONUS_West',
                                  'CONUS_Central', 'CONUS_South'],
                     'fcst_var_dict': {'name': 'APCP',
                                       'levels': ['A24']},
                     'obs_var_dict': {'name': 'APCP',
                                     'levels': ['A24']},
                     'obs_name': '24hrCCPA'},
    },
    'pres_levs': {
        'GeoHeight': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS'],
                      'fcst_var_dict': {'name': 'HGT',
                                        'levels': ['P1000', 'P700',
                                                   'P500', 'P250']},
                      'obs_var_dict': {'name': 'HGT',
                                       'levels': ['P1000', 'P700',
                                                  'P500', 'P250']}},
        'GeoHeight_FourierDecomp': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM',
                                                 'TROPICS'],
                                    'fcst_var_dict': {'name': 'HGT_DECOMP',
                                                      'levels': ['P500']},
                                    'obs_var_dict': {'name': 'HGT_DECOMP',
                                                     'levels': ['P500']}},
        'DailyAvg_GeoHeightAnom': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM',
                                               'TROPICS'],
                                   'fcst_var_dict': {'name': 'HGT_ANOM_DAILYAVG',
                                                     'levels': ['P500']},
                                   'obs_var_dict': {'name': 'HGT_ANOM_DAILYAVG',
                                                    'levels': ['P500']}},
        'Ozone': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS'],
                  'fcst_var_dict': {'name': 'O3MR',
                                    'levels': ['P925', 'P100', 'P70', 'P50',
                                               'P30', 'P20', 'P10', 'P5',
                                               'P1']},
                  'obs_var_dict': {'name': 'O3MR',
                                   'levels': ['P925', 'P100', 'P70', 'P50',
                                              'P30', 'P20', 'P10', 'P5',
                                              'P1']}},
        'PresSeaLevel': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS'],
                         'fcst_var_dict': {'name': 'PRMSL',
                                           'levels': ['Z0']},
                         'obs_var_dict': {'name': 'PRMSL',
                                          'levels': ['Z0']}},
        'Temp': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS'],
                 'fcst_var_dict': {'name': 'TMP',
                                   'levels': ['P850', 'P500', 'P250']},
                 'obs_var_dict': {'name': 'TMP',
                                  'levels': ['P850', 'P500', 'P250']}},
        'UWind': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS'],
                  'fcst_var_dict': {'name': 'UGRD',
                                    'levels': ['P850', 'P500', 'P250']},
                  'obs_var_dict': {'name': 'UGRD',
                                   'levels': ['P850', 'P500', 'P250']}},
        'VWind': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS'],
                  'fcst_var_dict': {'name': 'VGRD',
                                    'levels': ['P850', 'P500', 'P250']},
                  'obs_var_dict': {'name': 'VGRD',
                                   'levels': ['P850', 'P500', 'P250']}},
        'VectorWind': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS'],
                       'fcst_var_dict': {'name': 'UGRD_VGRD',
                                         'levels': ['P850', 'P500', 'P250']},
                       'obs_var_dict': {'name': 'UGRD_VGRD',
                                        'levels': ['P850', 'P500', 'P250']}},
        'WindShear': {'vx_masks': ['ATL_MDR', 'EPAC_MDR'],
                      'fcst_var_dict': {'name': 'WNDSHR',
                                        'levels': ['P850-P200']},
                      'obs_var_dict': {'name': 'WNDSHR',
                                       'levels': ['P850-P200']}},
    },
    'sea_ice': {
        'DailyAvg_Concentration': {'vx_masks': ['ARCTIC', 'ANTARCTIC'],
                                   'fcst_var_dict': {'name': 'ICEC_DAILYAVG',
                                                     'levels': ['Z0']},
                                   'obs_var_dict': {'name': 'ice_conc',
                                                    'levels': ['*,*']},
                                   'obs_name': 'osi_saf'}
    },
    'snow': {
        '24hrNOHRSC_Depth': {'vx_masks': ['CONUS', 'CONUS_East', 'CONUS_West',
                                          'CONUS_Central', 'CONUS_South'],
                             'fcst_var_dict': {'name': 'SNOD_A24',
                                               'levels': ['Z0']},
                             'obs_var_dict': {'name': 'ASNOW',
                                              'levels': ['A24']},
                             'obs_name': '24hrNOHRSC'},
        '24hrNOHRSC_WaterEqv': {'vx_masks': ['CONUS', 'CONUS_East',
                                             'CONUS_West', 'CONUS_Central',
                                             'CONUS_South'],
                             'fcst_var_dict': {'name': 'WEASD_A24',
                                               'levels': ['Z0']},
                             'obs_var_dict': {'name': 'ASNOW',
                                              'levels': ['A24']},
                             'obs_name': '24hrNOHRSC'},
    },
    'sst': {
        'DailyAvg_SST': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS'],
                         'fcst_var_dict': {'name': 'SST_DAILYAVG',
                                           'levels': ['Z0']},
                         'obs_var_dict': {'name': 'analysed_sst',
                                          'levels': ['0,*,*']},
                         'obs_name': 'ghrsst_ospo'},
    }
}

################################################
#### condense_stats jobs 
################################################
condense_stats_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
#### means
for means_job in list(condense_stats_jobs_dict['means'].keys()):
    condense_stats_jobs_dict['means'][means_job]['line_types'] = ['SL1L2']
#### precip
condense_stats_jobs_dict['precip']['24hrCCPA']['line_types'] = (
    ['CTC', 'NBRCNT']
)
#### pres_levs
for pres_levs_job in list(condense_stats_jobs_dict['pres_levs'].keys()):
    if pres_levs_job in ['DailyAvg_GeoHeightAnom', 'Ozone', 'WindShear']:
        (condense_stats_jobs_dict['pres_levs'][pres_levs_job]\
         ['line_types']) = ['SL1L2']
    elif pres_levs_job == 'GeoHeight':
        (condense_stats_jobs_dict['pres_levs'][pres_levs_job]\
             ['line_types']) = ['SAL1L2', 'GRAD']
    elif pres_levs_job == 'PresSeaLevel':
        (condense_stats_jobs_dict['pres_levs'][pres_levs_job]\
             ['line_types']) = ['SAL1L2', 'SL1L2', 'GRAD']
    elif pres_levs_job == 'VectorWind':
        (condense_stats_jobs_dict['pres_levs'][pres_levs_job]\
         ['line_types']) = ['VAL1L2']
    else:
        (condense_stats_jobs_dict['pres_levs'][pres_levs_job]\
         ['line_types']) = ['SAL1L2']
#### sea_ice
for sea_ice_job in list(condense_stats_jobs_dict['sea_ice'].keys()):
    condense_stats_jobs_dict['sea_ice'][sea_ice_job]['line_types'] = (
        ['SL1L2', 'CTC']
    )
#### snow
for snow_job in list(condense_stats_jobs_dict['snow'].keys()):
    condense_stats_jobs_dict['snow'][snow_job]['line_types'] = (
        ['CTC', 'NBRCNT']
    )
#### sst
for sst_job in list(condense_stats_jobs_dict['sst'].keys()):
    condense_stats_jobs_dict['sst'][sst_job]['line_types'] = ['SL1L2']
if JOB_GROUP == 'condense_stats':
    JOB_GROUP_dict = condense_stats_jobs_dict

################################################
#### filter_stats jobs
################################################
filter_stats_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
if JOB_GROUP == 'filter_stats':
    JOB_GROUP_dict = filter_stats_jobs_dict

################################################
#### make_plots jobs
################################################
make_plots_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
if JOB_GROUP == 'make_plots':
    JOB_GROUP_dict = make_plots_jobs_dict

################################################
#### tar_images jobs
################################################
tar_images_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
if JOB_GROUP == 'tar_images':
    JOB_GROUP_dict = tar_images_jobs_dict

model_list = os.environ['model_list'].split(' ')
for verif_type in VERIF_CASE_STEP_type_list:
    print("----> Making job scripts for "+VERIF_CASE_STEP+" "
          +verif_type+" for job group "+JOB_GROUP)
    VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                   +verif_type)
    model_plot_name_list = (
        os.environ[VERIF_CASE_STEP_abbrev+'_model_plot_name_list'].split(' ')
    )
    verif_type_plot_jobs_dict = JOB_GROUP_dict[verif_type]
    for verif_type_job in list(verif_type_plot_jobs_dict.keys()):
        if verif_type == 'pres_levs':
            obs_list = (
                os.environ[VERIF_CASE_STEP_abbrev_type+'_truth_name_list']\
                .split(' ')
            )
        elif verif_type == 'means':
            obs_list = model_list
        else:   
            obs_list = [
                verif_type_plot_jobs_dict[verif_type_job]['obs_name']
                for m in model_list
            ]
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, JOB_GROUP,
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        job_env_dict['start_date'] = start_date
        job_env_dict['end_date'] = end_date
        job_env_dict['date_type'] = 'VALID'
        #valid_hr_start = int(job_env_dict['valid_hr_start'])
        #valid_hr_end = int(job_env_dict['valid_hr_end'])
        #valid_hr_inc = int(job_env_dict['valid_hr_inc'])
        #valid_hrs = list(range(valid_hr_start,
        #                       valid_hr_end+valid_hr_inc,
        #                       valid_hr_inc))
        #if 'Daily' in verif_type_job:
        #    if job_env_dict['fhr_inc'] != '24':
        #        job_env_dict['fhr_inc'] = '24'
        #    if int(job_env_dict['fhr_end'])%24 != 0:
        #        job_env_dict['fhr_end'] = str(
        #            int(job_env_dict['fhr_end'])
        #             -(int(job_env_dict['fhr_end'])%24)
        #        )
        #    if int(job_env_dict['fhr_start'])%24 != 0:
        #        job_env_dict['fhr_start'] = str(
        #            int(job_env_dict['fhr_start'])
        #            -(int(job_env_dict['fhr_start'])%24)
        #        )
        #    if int(job_env_dict['fhr_start']) < 24:
        #        job_env_dict['fhr_start'] = '24'
        for data_name in ['fcst', 'obs']:
            job_env_dict[data_name+'_var_name'] =  (
                verif_type_plot_jobs_dict[verif_type_job]\
                [data_name+'_var_dict']['name']
            )
        if JOB_GROUP == 'condense_stats':
            JOB_GROUP_verif_type_job_product_loops = list(itertools.product(
                verif_type_plot_jobs_dict[verif_type_job]['line_types'],
                verif_type_plot_jobs_dict[verif_type_job]['fcst_var_dict']['levels'],
                verif_type_plot_jobs_dict[verif_type_job]['vx_masks'],
                model_list
            ))
        for loop_info in JOB_GROUP_verif_type_job_product_loops:
            if JOB_GROUP == 'condense_stats':
                job_env_dict['fcst_var_level'] = loop_info[1]
                job_env_dict['obs_var_level'] = (
                    verif_type_plot_jobs_dict[verif_type_job]\
                    ['obs_var_dict']['levels'][
                        verif_type_plot_jobs_dict[verif_type_job]\
                        ['fcst_var_dict']['levels'].index(loop_info[1])
                    ]
                )
                job_env_dict['model_list'] = loop_info[3]
                job_env_dict['model_plot_name_list'] = (
                    model_plot_name_list[model_list.index(loop_info[3])]
                )
                job_env_dict['obs_list'] = (
                    obs_list[model_list.index(loop_info[3])]
                )
                job_env_dict['line_type'] = loop_info[0]
                job_env_dict['vx_mask'] = loop_info[2]
                job_env_dict['DATAjob'] = os.path.join(
                    DATA, f"{VERIF_CASE}_{STEP}", 'plot_output',
                    f"{RUN}.{end_date}", f"{VERIF_CASE}_{verif_type}",
                    f"last{NDAYS}days", job_env_dict['line_type'].lower(),
                    f"{job_env_dict['fcst_var_name'].lower()}_"
                    +(job_env_dict['fcst_var_level'].lower()\
                      .replace('.','p').replace('-', '_')),
                    job_env_dict['vx_mask'].lower()
                )
                job_env_dict['COMOUTjob'] = os.path.join(
                    COMOUT, f"{VERIF_CASE}_{verif_type}",
                    f"last{NDAYS}days", job_env_dict['line_type'].lower(),
                    f"{job_env_dict['fcst_var_name'].lower()}_"
                    +(job_env_dict['fcst_var_level'].lower()\
                      .replace('.','p').replace('-', '_')),
                    job_env_dict['vx_mask'].lower()
                )
                for output_dir in [job_env_dict['DATAjob'],
                                   job_env_dict['COMOUTjob']]:
                    if not os.path.exists(output_dir):
                        print(f"Creating output directory: {output_dir}")
                        os.makedirs(output_dir)
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
                    job.write('export '+name+'="'+value+'"\n')
                job.write('\n')
                job.write(
                    gda_util.python_command('global_det_atmos_plots.py',[])
                )
                job.close()

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("WARNING: No job files created in "+JOB_GROUP_jobs_dir)
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
                iproc = 0
                node+=1
        poe_filename = os.path.join(JOB_GROUP_jobs_dir,
                                    'poe_jobs'+str(node))
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
                str(iproc-1)+' '
                +os.path.join(JOB_GROUP_jobs_dir,job)+'\n'
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
