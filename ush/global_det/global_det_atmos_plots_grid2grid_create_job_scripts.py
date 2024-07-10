#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_grid2grid_create_job_scripts.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This creates multiple independent job scripts. These
          jobs scripts contain all the necessary environment variables
          and commands to needed to run them.
Run By: scripts/plots/global_det/exevs_global_det_atmos_grid2grid_plots.sh
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
gda_util.make_dir(JOB_GROUP_jobs_dir)

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
                                     'levels': ['Z0']}},
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
        'DailyAvg_ConcentrationNH': {'vx_masks': ['ARCTIC'],
                                     'fcst_var_dict': {'name': 'ICEC_DAILYAVG',
                                                       'levels': ['Z0']},
                                     'obs_var_dict': {'name': 'ice_conc',
                                                      'levels': ['0,*,*']},
                                     'obs_name': 'osi_saf'},
        'DailyAvg_ConcentrationSH': {'vx_masks': ['ANTARCTIC'],
                                     'fcst_var_dict': {'name': 'ICEC_DAILYAVG',
                                                       'levels': ['Z0']},
                                     'obs_var_dict': {'name': 'ice_conc',
                                                      'levels': ['0,*,*']},
                                     'obs_name': 'osi_saf'},
        'DailyAvg_ExtentNH': {'vx_masks': ['ARCTIC'],
                              'fcst_var_dict': {'name': 'ICEEX_DAILYAVG',
                                                'levels': ['Z0']},
                              'obs_var_dict': {'name': 'ICEEX_DAILYAVG',
                                               'levels': ['Z0']},
                              'obs_name': 'osi_saf'},
        'DailyAvg_ExtentSH': {'vx_masks': ['ANTARCTIC'],
                              'fcst_var_dict': {'name': 'ICEEX_DAILYAVG',
                                                'levels': ['Z0']},
                              'obs_var_dict': {'name': 'ICEEX_DAILYAVG',
                                               'levels': ['Z0']},
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
        pres_job_line_types = ['SL1L2']
    elif pres_levs_job == 'GeoHeight':
        pres_job_line_types = ['SAL1L2', 'GRAD']
    elif pres_levs_job == 'PresSeaLevel':
        pres_job_line_types = ['SAL1L2', 'SL1L2', 'GRAD']
    elif pres_levs_job == 'VectorWind':
        pres_job_line_types = ['VAL1L2']
    else:
        pres_job_line_types = ['SAL1L2']
    condense_stats_jobs_dict['pres_levs'][pres_levs_job]['line_types'] = (
        pres_job_line_types
    )
#### sea_ice
for sea_ice_job in list(condense_stats_jobs_dict['sea_ice'].keys()):
    if 'DailyAvg_Concentration' in sea_ice_job:
        condense_stats_jobs_dict['sea_ice'][sea_ice_job]['line_types'] = [
            'SL1L2', 'CTC'
        ]
    elif 'DailyAvg_Extent' in sea_ice_job:
        condense_stats_jobs_dict['sea_ice'][sea_ice_job]['line_types'] = [
            'SL1L2'
        ]
#### snow
for snow_job in list(condense_stats_jobs_dict['snow'].keys()):
    condense_stats_jobs_dict['snow'][snow_job]['line_types'] = [
        'CTC', 'NBRCNT'
    ]
#### sst
for sst_job in list(condense_stats_jobs_dict['sst'].keys()):
    condense_stats_jobs_dict['sst'][sst_job]['line_types'] = ['SL1L2']
if JOB_GROUP == 'condense_stats':
    JOB_GROUP_dict = condense_stats_jobs_dict

################################################
#### filter_stats jobs
################################################
filter_stats_jobs_dict = copy.deepcopy(condense_stats_jobs_dict)
#### means
for means_job in list(filter_stats_jobs_dict['means'].keys()):
    filter_stats_jobs_dict['means'][means_job]['grid'] = 'G004'
    filter_stats_jobs_dict['means'][means_job]['fcst_var_dict']['threshs'] = [
        'NA'
    ]
    filter_stats_jobs_dict['means'][means_job]['obs_var_dict']['threshs'] = [
        'NA'
    ]
    filter_stats_jobs_dict['means'][means_job]['interps'] = ['NEAREST/1']
#### precip
filter_stats_jobs_dict['precip']['24hrCCPA']['line_types'] = ['CTC']
filter_stats_jobs_dict['precip']['24hrCCPA']['grid'] = 'G211'
filter_stats_jobs_dict['precip']['24hrCCPA']['fcst_var_dict']['threshs'] = [
    'ge0.1', 'ge0.5', 'ge1', 'ge5', 'ge10', 'ge25', 'ge50', 'ge75', 'ge0.254',
    'ge2.54', 'ge6.35', 'ge12.7', 'ge25.4', 'ge50.8', 'ge76.2', 'ge101.6'
]
filter_stats_jobs_dict['precip']['24hrCCPA']['obs_var_dict']['threshs'] = [
    'ge0.1', 'ge0.5', 'ge1', 'ge5', 'ge10', 'ge25', 'ge50', 'ge75', 'ge0.254',
    'ge2.54', 'ge6.35', 'ge12.7', 'ge25.4', 'ge50.8', 'ge76.2', 'ge101.6'
]
filter_stats_jobs_dict['precip']['24hrCCPA']['interps'] = ['NEAREST/1']
filter_stats_jobs_dict['precip']['24hrCCPA_Nbrhd'] = copy.deepcopy(
    filter_stats_jobs_dict['precip']['24hrCCPA']
)
filter_stats_jobs_dict['precip']['24hrCCPA_Nbrhd']['line_types'] = ['NBRCNT']
filter_stats_jobs_dict['precip']['24hrCCPA_Nbrhd']['grid'] = 'G240'
filter_stats_jobs_dict['precip']['24hrCCPA_Nbrhd']['interps'] = [
    'NBRHD_SQUARE/1', 'NBRHD_SQUARE/169', 'NBRHD_SQUARE/529',
    'NBRHD_SQUARE/1089', 'NBRHD_SQUARE/1849', 'NBRHD_SQUARE/2809',
    'NBRHD_SQUARE/3969'
]
#### pres_levs
for pres_levs_job in list(filter_stats_jobs_dict['pres_levs'].keys()):
    filter_stats_jobs_dict['pres_levs'][pres_levs_job]['grid'] = 'G004'
    (filter_stats_jobs_dict['pres_levs'][pres_levs_job]\
     ['fcst_var_dict']['threshs']) = ['NA']
    (filter_stats_jobs_dict['pres_levs'][pres_levs_job]\
     ['obs_var_dict']['threshs']) = ['NA']
    if pres_levs_job == 'GeoHeight_FourierDecomp':
        pres_levs_job_interps = [
            'WV1_0-20/NA', 'WV1_0-3/NA', 'WV1_4-9/NA', 'WV1_10-20/NA'
        ]
    else:
        pres_levs_job_interps = ['NEAREST/1']
    filter_stats_jobs_dict['pres_levs'][pres_levs_job]['interps'] = (
        pres_levs_job_interps
    )
#### sea_ice
for sea_ice_job in list(condense_stats_jobs_dict['sea_ice'].keys()):
    filter_stats_jobs_dict['sea_ice'][sea_ice_job]['line_types'] = ['SL1L2']
    (filter_stats_jobs_dict['sea_ice'][sea_ice_job]['fcst_var_dict']\
     ['threshs']) = ['NA']
    (filter_stats_jobs_dict['sea_ice'][sea_ice_job]['obs_var_dict']\
     ['threshs']) = ['NA']
    filter_stats_jobs_dict['sea_ice'][sea_ice_job]['interps'] = ['NEAREST/1']
    if 'NH' in sea_ice_job:
        filter_stats_jobs_dict['sea_ice'][sea_ice_job]['grid'] = 'G219'
    elif 'SH' in sea_ice_job:
        filter_stats_jobs_dict['sea_ice'][sea_ice_job]['grid'] = 'G220'
for hemisphere in ['NH', 'SH']:
    (filter_stats_jobs_dict['sea_ice']\
     ['DailyAvg_Concentration'+hemisphere+'_Thresh']) = copy.deepcopy(
        filter_stats_jobs_dict['sea_ice']['DailyAvg_Concentration'+hemisphere]
    )
    (filter_stats_jobs_dict['sea_ice']\
     ['DailyAvg_Concentration'+hemisphere+'_Thresh']['line_types']) = ['CTC']
    (filter_stats_jobs_dict['sea_ice']\
     ['DailyAvg_Concentration'+hemisphere+'_Thresh']\
     ['fcst_var_dict']['threshs']) = ['ge15', 'ge40', 'ge80']
    (filter_stats_jobs_dict['sea_ice']\
     ['DailyAvg_Concentration'+hemisphere+'_Thresh']\
     ['obs_var_dict']['threshs']) = ['ge15', 'ge40', 'ge80']
#### snow
for snow_job in list(filter_stats_jobs_dict['snow'].keys()):
    filter_stats_jobs_dict['snow'][snow_job]['line_types'] = ['CTC']
    filter_stats_jobs_dict['snow'][snow_job]['grid'] = 'G211'
    filter_stats_jobs_dict['snow'][snow_job]['fcst_var_dict']['threshs'] = [
        'ge0.0254', 'ge0.0508', 'ge0.1016', 'ge0.2032', 'ge0.3048'
    ]
    filter_stats_jobs_dict['snow'][snow_job]['obs_var_dict']['threshs'] = [
        'ge0.0254', 'ge0.0508', 'ge0.1016', 'ge0.2032', 'ge0.3048'
    ]
    filter_stats_jobs_dict['snow'][snow_job]['interps'] = ['NEAREST/1']
    filter_stats_jobs_dict['snow'][f"{snow_job}_Nbrhd"] = copy.deepcopy(
        filter_stats_jobs_dict['snow'][snow_job]
    )
    filter_stats_jobs_dict['snow'][f"{snow_job}_Nbrhd"]['grid'] = 'G240'
    filter_stats_jobs_dict['snow'][f"{snow_job}_Nbrhd"]['line_types'] = [
        'NBRCNT'
    ]
    filter_stats_jobs_dict['snow'][f"{snow_job}_Nbrhd"]['interps'] = [
        'NBRHD_SQUARE/1', 'NBRHD_SQUARE/169', 'NBRHD_SQUARE/529',
        'NBRHD_SQUARE/1089', 'NBRHD_SQUARE/1849', 'NBRHD_SQUARE/2809',
        'NBRHD_SQUARE/3969'
    ]
#### sst
for sst_job in list(filter_stats_jobs_dict['sst'].keys()):
    filter_stats_jobs_dict['sst'][sst_job]['grid'] = 'G004'
    filter_stats_jobs_dict['sst'][sst_job]['fcst_var_dict']['threshs'] = ['NA']
    filter_stats_jobs_dict['sst'][sst_job]['obs_var_dict']['threshs'] = ['NA']
    filter_stats_jobs_dict['sst'][sst_job]['interps'] = ['NEAREST/1']
if JOB_GROUP == 'filter_stats':
    JOB_GROUP_dict = filter_stats_jobs_dict

################################################
#### make_plots jobs
################################################
make_plots_jobs_dict = copy.deepcopy(filter_stats_jobs_dict)
#### means
for means_job in list(make_plots_jobs_dict['means'].keys()):
    del make_plots_jobs_dict['means'][means_job]['line_types']
    make_plots_jobs_dict['means'][means_job]['line_type_stats'] = [
        'SL1L2/FBAR'
    ]
    make_plots_jobs_dict['means'][means_job]['plots'] = ['time_series']
#### precip
for precip_job in list(make_plots_jobs_dict['precip'].keys()):
    del make_plots_jobs_dict['precip'][precip_job]['line_types']
make_plots_jobs_dict['precip']['24hrCCPA']['line_type_stats'] = [
    'CTC/ETS', 'CTC/FBIAS'
]
make_plots_jobs_dict['precip']['24hrCCPA']['plots'] = [
    'time_series', 'lead_average'
]
for nbrhd in make_plots_jobs_dict['precip']['24hrCCPA_Nbrhd']['interps']:
    make_plots_jobs_dict['precip'][f"24hrCCPA_Nbrhd{nbrhd.split('/')[1]}"] = (
        copy.deepcopy(make_plots_jobs_dict['precip']['24hrCCPA_Nbrhd'])
    )
    (make_plots_jobs_dict['precip'][f"24hrCCPA_Nbrhd{nbrhd.split('/')[1]}"]\
     ['line_type_stats']) = ['NBRCNT/FSS']
    (make_plots_jobs_dict['precip'][f"24hrCCPA_Nbrhd{nbrhd.split('/')[1]}"]\
     ['interps']) = [nbrhd]
    (make_plots_jobs_dict['precip'][f"24hrCCPA_Nbrhd{nbrhd.split('/')[1]}"]\
     ['plots']) = ['time_series', 'lead_average']
del make_plots_jobs_dict['precip']['24hrCCPA_Nbrhd']
make_plots_jobs_dict['precip']['24hrCCPA_PerfDiag'] = copy.deepcopy(
    make_plots_jobs_dict['precip']['24hrCCPA']
)
make_plots_jobs_dict['precip']['24hrCCPA_PerfDiag']['line_type_stats'] = [
    'CTC/PERFDIAG'
]
make_plots_jobs_dict['precip']['24hrCCPA_PerfDiag']['plots'] = [
    'performance_diagram'
]
(make_plots_jobs_dict['precip']['24hrCCPA_PerfDiag']\
 ['fcst_var_dict']['threshs']) = [
    'ge0.1', 'ge0.5', 'ge1', 'ge5', 'ge10', 'ge25', 'ge50', 'ge75'
]
(make_plots_jobs_dict['precip']['24hrCCPA_PerfDiag']\
 ['obs_var_dict']['threshs']) = [
    'ge0.1', 'ge0.5', 'ge1', 'ge5', 'ge10', 'ge25', 'ge50', 'ge75'
]

make_plots_jobs_dict['precip']['24hrAccumMaps'] = {
    'vx_masks': ['conus', 'alaska', 'prico', 'hawaii'],
    'fcst_var_dict': {'name': 'APCP',
                      'levels': ['A24'],
                      'threshs': ['NA']},
    'obs_var_dict': {'name': 'APCP',
                     'levels': ['A24'],
                     'threshs': ['NA']},
    'obs_name': '24hrCCPA',
    'grid': 'G211',
    'line_type_stats': ['SL1L2/FBAR'],
    'interps': ['NEAREST/1'],
    'plots': ['precip_spatial_map']
}
#### pres_levs
for pres_levs_job in list(make_plots_jobs_dict['pres_levs'].keys()):
    del make_plots_jobs_dict['pres_levs'][pres_levs_job]['line_types']
    if pres_levs_job in ['DailyAvg_GeoHeightAnom', 'Ozone', 'WindShear']:
        pres_levs_job_line_type_stats = ['SL1L2/ME', 'SL1L2/RMSE']
    elif pres_levs_job == 'GeoHeight':
        pres_levs_job_line_type_stats = ['SAL1L2/ACC', 'GRAD/S1']
    elif pres_levs_job == 'PresSeaLevel':
        pres_levs_job_line_type_stats = [
            'SAL1L2/ACC', 'SL1L2/ME', 'SL1L2/RMSE', 'GRAD/S1'
        ]
    elif pres_levs_job == 'VectorWind':
        pres_levs_job_line_type_stats = ['VAL1L2/ACC']
    else:
        pres_levs_job_line_type_stats = ['SAL1L2/ACC']
    if pres_levs_job == 'Ozone':
        pres_levs_job_plots = [
            'time_series', 'lead_average', 'stat_by_level', 'lead_by_level'
        ]
    elif pres_levs_job in ['WindShear', 'DailyAvg_GeoHeightAnom']:
        pres_levs_job_plots = ['time_series', 'lead_average']
    else:
        pres_levs_job_plots = ['time_series', 'lead_average', 'lead_by_date']
    make_plots_jobs_dict['pres_levs'][pres_levs_job]['line_type_stats'] = (
        pres_levs_job_line_type_stats
    )
    make_plots_jobs_dict['pres_levs'][pres_levs_job]['plots'] = (
        pres_levs_job_plots
    )
for decomp in (make_plots_jobs_dict['pres_levs']\
               ['GeoHeight_FourierDecomp']['interps']):
    (make_plots_jobs_dict['pres_levs']\
     [f"GeoHeight_FourierDecomp{decomp.split('/')[0]}"]) = (
        copy.deepcopy(make_plots_jobs_dict['pres_levs']\
                      ['GeoHeight_FourierDecomp'])
    )
    (make_plots_jobs_dict['pres_levs']\
     [f"GeoHeight_FourierDecomp{decomp.split('/')[0]}"]['interps']) = [decomp]
del make_plots_jobs_dict['pres_levs']['GeoHeight_FourierDecomp']
#### sea_ice
for sea_ice_job in list(make_plots_jobs_dict['sea_ice'].keys()):
    del make_plots_jobs_dict['sea_ice'][sea_ice_job]['line_types']
    if 'DailyAvg_Concentration' in sea_ice_job:
        if 'Thresh' in sea_ice_job:
            sea_ice_job_line_type_stats = ['CTC/CSI']
        else:
            sea_ice_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
    elif 'DailyAvg_Extent' in sea_ice_job:
        sea_ice_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME',
                                       'SL1L2/STDEV_ERR', 'SL1L2/CORR']
    make_plots_jobs_dict['sea_ice'][sea_ice_job]['line_type_stats'] = (
        sea_ice_job_line_type_stats
    )
    make_plots_jobs_dict['sea_ice'][sea_ice_job]['plots'] = [
        'time_series', 'lead_average'
    ]
for hemisphere in ['NH', 'SH']:
    (make_plots_jobs_dict['sea_ice']\
     ['DailyAvg_Concentration'+hemisphere+'_PerfDiag']) = copy.deepcopy(
         make_plots_jobs_dict['sea_ice']\
         ['DailyAvg_Concentration'+hemisphere+'_Thresh']
    )
    (make_plots_jobs_dict['sea_ice']\
     ['DailyAvg_Concentration'+hemisphere+'_PerfDiag']['line_type_stats']) = [
        'CTC/PERFDIAG'
    ]
    (make_plots_jobs_dict['sea_ice']\
     ['DailyAvg_Concentration'+hemisphere+'_PerfDiag']['plots']) = [
        'performance_diagram'
    ]
#### snow
for snow_job in list(make_plots_jobs_dict['snow'].keys()):
    del make_plots_jobs_dict['snow'][snow_job]['line_types']
for snow_var in ['Depth', 'WaterEqv']:
    (make_plots_jobs_dict['snow'][f"24hrNOHRSC_{snow_var}"]\
     ['line_type_stats']) = ['CTC/ETS', 'CTC/FBIAS']
    (make_plots_jobs_dict['snow'][f"24hrNOHRSC_{snow_var}"]\
     ['plots']) = ['time_series', 'lead_average']
    for nbrhd in (make_plots_jobs_dict['snow']\
            [f"24hrNOHRSC_{snow_var}_Nbrhd"]['interps']):
        (make_plots_jobs_dict['snow']\
         [f"24hrNOHRSC_{snow_var}_Nbrhd{nbrhd.split('/')[1]}"]) = (
            copy.deepcopy(make_plots_jobs_dict['snow']\
            [f"24hrNOHRSC_{snow_var}_Nbrhd"])
        )
        (make_plots_jobs_dict['snow']\
         [f"24hrNOHRSC_{snow_var}_Nbrhd{nbrhd.split('/')[1]}"]\
         ['line_type_stats']) = ['NBRCNT/FSS']
        (make_plots_jobs_dict['snow']\
         [f"24hrNOHRSC_{snow_var}_Nbrhd{nbrhd.split('/')[1]}"]\
         ['interps']) = [nbrhd]
        (make_plots_jobs_dict['snow']\
         [f"24hrNOHRSC_{snow_var}_Nbrhd{nbrhd.split('/')[1]}"]\
         ['plots']) = ['time_series', 'lead_average']
    del make_plots_jobs_dict['snow'][f"24hrNOHRSC_{snow_var}_Nbrhd"]
make_plots_jobs_dict['snow']['24hrNOHRSC_24hrAccumMaps'] = {
    'vx_masks': ['conus'],
    'fcst_var_dict': {'name': 'ASNOW',
                      'levels': ['Z0'],
                      'threshs': ['NA']},
    'obs_var_dict': {'name': 'ASNOW',
                     'levels': ['Z0'],
                     'threshs': ['NA']},
    'obs_name': '24hrNOHRSC',
    'grid': 'G211',
    'line_type_stats': ['SL1L2/FBAR'],
    'interps': ['NEAREST/1'],
    'plots': ['nohrsc_spatial_map']
}
#### sst
for sst_job in list(make_plots_jobs_dict['sst'].keys()):
    del make_plots_jobs_dict['sst'][sst_job]['line_types']
    make_plots_jobs_dict['sst'][sst_job]['line_type_stats'] = [
        'SL1L2/RMSE', 'SL1L2/ME'
    ]
    make_plots_jobs_dict['sst'][sst_job]['plots'] = [
        'time_series', 'lead_average'
    ]
if JOB_GROUP == 'make_plots':
    JOB_GROUP_dict = make_plots_jobs_dict

################################################
#### tar_images jobs
################################################
tar_images_jobs_dict = {
    'flux': {},
    'means': {
        'search_base_dir': os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'plot_output', f"{RUN}.{end_date}",
                                        f"{VERIF_CASE}_means",
                                        f"last{NDAYS}days")
    },
    'ozone': {},
    'precip': {
        'search_base_dir': os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'plot_output', f"{RUN}.{end_date}",
                                        f"{VERIF_CASE}_precip",
                                        f"last{NDAYS}days")
    },
    'pres_levs': {
        'search_base_dir': os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'plot_output', f"{RUN}.{end_date}",
                                        f"{VERIF_CASE}_pres_levs",
                                        f"last{NDAYS}days")
    },
    'sea_ice': {
        'search_base_dir': os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'plot_output', f"{RUN}.{end_date}",
                                        f"{VERIF_CASE}_sea_ice",
                                        f"last{NDAYS}days")
    },
    'snow': {
        'search_base_dir': os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'plot_output', f"{RUN}.{end_date}",
                                        f"{VERIF_CASE}_snow",
                                        f"last{NDAYS}days")
    },
    'sst': {
        'search_base_dir': os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'plot_output', f"{RUN}.{end_date}",
                                        f"{VERIF_CASE}_sst",
                                        f"last{NDAYS}days")
    },
}
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
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, JOB_GROUP,
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        job_env_dict['start_date'] = start_date
        job_env_dict['end_date'] = end_date
        job_env_dict['NDAYS'] = NDAYS
        job_env_dict['date_type'] = 'VALID'
        if JOB_GROUP in ['filter_stats', 'make_plots']:
            valid_hr_start = int(job_env_dict['valid_hr_start'])
            valid_hr_end = int(job_env_dict['valid_hr_end'])
            valid_hr_inc = int(job_env_dict['valid_hr_inc'])
            valid_hrs = list(range(valid_hr_start,
                                   valid_hr_end+valid_hr_inc,
                                   valid_hr_inc))
            if 'Daily' in verif_type_job:
                daily_fhr_list = []
                for fhr in job_env_dict['fhr_list'].split(', '):
                    if int(fhr) >= 24 and int(fhr) % 24 == 0:
                        daily_fhr_list.append(str(fhr))
                    job_env_dict['fhr_list'] = ', '.join(daily_fhr_list)
        if JOB_GROUP in ['condense_stats', 'filter_stats', 'make_plots']:
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
        elif JOB_GROUP == 'filter_stats':
            job_env_dict['grid'] = (
                verif_type_plot_jobs_dict[verif_type_job]['grid']
            )
            JOB_GROUP_verif_type_job_product_loops = list(itertools.product(
                verif_type_plot_jobs_dict[verif_type_job]['line_types'],
                verif_type_plot_jobs_dict[verif_type_job]['fcst_var_dict']['levels'],
                verif_type_plot_jobs_dict[verif_type_job]['vx_masks'],
                model_list,
                verif_type_plot_jobs_dict[verif_type_job]['fcst_var_dict']['threshs'],
                verif_type_plot_jobs_dict[verif_type_job]['interps'],
                valid_hrs
            ))
        elif JOB_GROUP == 'make_plots':
            job_env_dict['grid'] = (
                verif_type_plot_jobs_dict[verif_type_job]['grid']
            )
            JOB_GROUP_verif_type_job_product_loops = list(itertools.product(
                verif_type_plot_jobs_dict[verif_type_job]['line_type_stats'],
                verif_type_plot_jobs_dict[verif_type_job]['plots'],
                verif_type_plot_jobs_dict[verif_type_job]['vx_masks'],
                verif_type_plot_jobs_dict[verif_type_job]['interps']
            ))
        elif JOB_GROUP == 'tar_images':
            JOB_GROUP_verif_type_job_product_loops = []
            for root, dirs, files in os.walk(
                verif_type_plot_jobs_dict['search_base_dir']
            ):
                if not dirs \
                        and root not in JOB_GROUP_verif_type_job_product_loops:
                    JOB_GROUP_verif_type_job_product_loops.append(root)
        for loop_info in JOB_GROUP_verif_type_job_product_loops:
            if JOB_GROUP in ['condense_stats', 'filter_stats']:
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
                if JOB_GROUP == 'filter_stats':
                    job_env_dict['event_equalization'] = (
                        os.environ[VERIF_CASE_STEP_abbrev
                                   +'_event_equalization']
                    )
                    job_env_dict['fcst_var_thresh'] = loop_info[4]
                    job_env_dict['obs_var_thresh'] = (
                        verif_type_plot_jobs_dict[verif_type_job]\
                        ['obs_var_dict']['threshs'][
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['fcst_var_dict']['threshs'].index(loop_info[4])
                        ]
                    )
                    job_env_dict['interp_method'] = loop_info[5].split('/')[0]
                    job_env_dict['interp_points'] = loop_info[5].split('/')[1]
                    job_env_dict['valid_hr_start'] = (
                        str(loop_info[6]).zfill(2)
                    )
                    job_env_dict['valid_hr_end'] = (
                        job_env_dict['valid_hr_start']
                    )
                    job_env_dict['valid_hr_inc'] = '24'
                DATAjob, COMOUTjob = gda_util.get_plot_job_dirs(
                    DATA, COMOUT, JOB_GROUP, job_env_dict
                )
                job_env_dict['DATAjob'] = DATAjob
                job_env_dict['COMOUTjob'] = COMOUTjob
                for output_dir in [job_env_dict['DATAjob'],
                                   job_env_dict['COMOUTjob']]:
                    gda_util.make_dir(output_dir)
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
                    +'\n'
                )
                job.write('export err=$?; err_chk'+'\n')
                job.close()
            elif JOB_GROUP == 'make_plots':
                job_env_dict['event_equalization'] = os.environ[
                    VERIF_CASE_STEP_abbrev+'_event_equalization'
                ]
                job_env_dict['model_list'] = ', '.join(model_list)
                job_env_dict['model_plot_name_list'] = (
                    ', '.join(model_plot_name_list)
                )
                job_env_dict['obs_list'] = ', '.join(obs_list)
                job_env_dict['line_type'] = loop_info[0].split('/')[0]
                job_env_dict['stat'] = loop_info[0].split('/')[1]
                job_env_dict['plot'] = loop_info[1]
                job_env_dict['vx_mask'] = loop_info[2]
                job_env_dict['interp_method'] = loop_info[3].split('/')[0]
                job_env_dict['interp_points'] = loop_info[3].split('/')[1]
                if job_env_dict['plot'] == 'valid_hour_average':
                    plot_valid_hrs_loop = [valid_hrs]
                else:
                    plot_valid_hrs_loop = valid_hrs
                if job_env_dict['plot'] in ['threshold_average',
                                            'performance_diagram']:
                    plot_fcst_threshs_loop = [
                        verif_type_plot_jobs_dict[verif_type_job]\
                        ['fcst_var_dict']['threshs']
                    ]
                else:
                    plot_fcst_threshs_loop = (
                        verif_type_plot_jobs_dict[verif_type_job]\
                        ['fcst_var_dict']['threshs']
                    )
                if job_env_dict['plot'] in ['stat_by_level', 'lead_by_level']:
                    if verif_type_plot_jobs_dict[verif_type_job]\
                            ['fcst_var_dict']['name'] == 'O3MR':
                        plot_fcst_levels_loop = ['all', 'strat']
                    else:
                        plot_fcst_levels_loop = ['all', 'trop', 'strat',
                                                 'ltrop', 'utrop']
                else:
                    plot_fcst_levels_loop = (
                        verif_type_plot_jobs_dict[verif_type_job]\
                        ['fcst_var_dict']['levels']
                    )
                for plot_loop_info in list(
                    itertools.product(plot_valid_hrs_loop,
                                      plot_fcst_threshs_loop,
                                      plot_fcst_levels_loop)
                ):
                    if job_env_dict['plot'] == 'valid_hour_average':
                        job_env_dict['valid_hr_start'] = str(
                            plot_loop_info[0][0]
                        ).zfill(2)
                        job_env_dict['valid_hr_end'] = str(
                            plot_loop_info[0][-1]
                        ).zfill(2)
                        job_env_dict['valid_hr_inc'] = str(valid_hr_inc)
                    else:
                        job_env_dict['valid_hr_start'] = str(
                            plot_loop_info[0]
                        ).zfill(2)
                        job_env_dict['valid_hr_end'] = str(
                            plot_loop_info[0]
                        ).zfill(2)
                        job_env_dict['valid_hr_inc'] = '24'
                    if job_env_dict['plot'] in ['threshold_average',
                                                'performance_diagram']:
                        job_env_dict['fcst_var_thresh_list'] = ', '.join(
                            plot_loop_info[1]
                        )
                        job_env_dict['obs_var_thresh_list'] = ', '.join(
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['obs_var_dict']['threshs']
                        )
                    else:
                        job_env_dict['fcst_var_thresh_list'] = (
                            plot_loop_info[1]
                        )
                        job_env_dict['obs_var_thresh_list'] = (
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['obs_var_dict']['threshs']\
                            [verif_type_plot_jobs_dict[verif_type_job]\
                             ['fcst_var_dict']['threshs']\
                             .index(plot_loop_info[1])]
                        )
                    if job_env_dict['plot'] in ['stat_by_level',
                                                'lead_by_level']:
                        job_env_dict['vert_profile'] = plot_loop_info[2]
                        job_env_dict['fcst_var_level_list'] = ', '.join(
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['fcst_var_dict']['levels']
                        )
                        job_env_dict['obs_var_level_list'] = ', '.join(
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['obs_var_dict']['levels']
                        )
                    else:
                        job_env_dict['fcst_var_level_list'] = plot_loop_info[2]
                        job_env_dict['obs_var_level_list'] = (
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['obs_var_dict']['levels']\
                            [verif_type_plot_jobs_dict[verif_type_job]\
                             ['fcst_var_dict']['levels']\
                             .index(plot_loop_info[2])]
                        )
                    DATAjob, COMOUTjob = gda_util.get_plot_job_dirs(
                        DATA, COMOUT, JOB_GROUP, job_env_dict
                    )
                    job_env_dict['DATAjob'] = DATAjob
                    job_env_dict['COMOUTjob'] = COMOUTjob
                    for output_dir in [job_env_dict['DATAjob'],
                                       job_env_dict['COMOUTjob']]:
                        gda_util.make_dir(output_dir)
                    run_global_det_atmos_plots = ['global_det_atmos_plots.py']
                    if evs_run_mode == 'production' and \
                            verif_type in ['pres_levs', 'sfc'] and \
                            job_env_dict['plot'] in \
                            ['lead_average', 'lead_by_level', 'lead_by_date']:
                        run_global_det_atmos_plots.append(
                            'global_det_atmos_plots_production_tof240.py'
                        )
                    for run_global_det_atmos_plot in run_global_det_atmos_plots:
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
                            gda_util.python_command(run_global_det_atmos_plot,
                                                    [])+'\n'
                        )
                        job.write('export err=$?; err_chk'+'\n')
                        job.close()
            elif JOB_GROUP == 'tar_images':
                job_env_dict['DATAjob'] = loop_info
                job_env_dict['COMOUTjob'] = loop_info.replace(
                    os.path.join(DATA,f"{VERIF_CASE}_{STEP}", 'plot_output',
                                 f"{RUN}.{end_date}"),
                    COMOUT
                )
                # Create job file
                njobs+=1
                job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
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
                    gda_util.python_command('global_det_atmos_plots.py', [])
                    +'\n'
                )
                job.write('export err=$?; err_chk'+'\n')
                job.close()

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("NOTE: No job files created in "+JOB_GROUP_jobs_dir)
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
                                f"poe_jobs{str(node)}")
    poe_file = open(poe_filename, 'a')
    if machine == 'WCOSS2':
        nselect = subprocess.run(
            f"cat {PBS_NODEFILE} | wc -l",
            shell=True, capture_output=True, encoding="utf8"
        ).stdout.replace('\n', '')
        nnp = int(nselect) * int(nproc)
    else:
        nnp = nproc
    iproc+=1
    while iproc <= int(nnp):
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
                f"{str(iproc-1)} /bin/echo {str(iproc)}'\n'"
            )
        else:
            poe_file.write(
                f"/bin/echo {str(iproc)}\n"
            )
        iproc+=1
    poe_file.close()

print("END: "+os.path.basename(__file__))
