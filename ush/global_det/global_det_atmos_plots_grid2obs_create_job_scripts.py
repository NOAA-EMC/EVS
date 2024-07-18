#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_grid2obs_create_job_scripts.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This creates multiple independent job scripts. These
          jobs scripts contain all the necessary environment variables
          and commands to needed to run them.
Run By: scripts/plots/global_det/exevs_global_det_atmos_grid2obs_plots.sh
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
    'pres_levs': {
        'GeoHeight': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                   'CONUS'],
                      'fcst_var_dict': {'name': 'HGT',
                                        'levels': ['P1000', 'P925', 'P850',
                                                   'P700', 'P500', 'P300',
                                                   'P250', 'P200', 'P100',
                                                   'P50', 'P20', 'P10', 'P5']},
                      'obs_var_dict': {'name': 'HGT',
                                       'levels': ['P1000', 'P925', 'P850',
                                                  'P700', 'P500', 'P300',
                                                  'P250', 'P200', 'P100',
                                                  'P50', 'P20', 'P10', 'P5']},
                     'obs_name': 'ADPUPA'},
        'RelHum': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS'],
                   'fcst_var_dict': {'name': 'RH',
                                     'levels': ['P1000', 'P925', 'P850',
                                                'P700', 'P500', 'P300', 'P250',
                                                'P200', 'P100', 'P50', 'P20',
                                                'P10', 'P5']},
                   'obs_var_dict': {'name': 'RH',
                                    'levels': ['P1000', 'P925', 'P850',
                                               'P700', 'P500', 'P300', 'P250',
                                               'P200', 'P100', 'P50', 'P20',
                                               'P10', 'P5']},
                   'obs_name': 'ADPUPA'},
        'SpefHum': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS'],
                    'fcst_var_dict': {'name': 'SPFH',
                                      'levels': ['P1000', 'P925', 'P850',
                                                 'P700', 'P500', 'P300',
                                                 'P250', 'P200', 'P100',
                                                 'P50', 'P20', 'P10', 'P5']},
                    'obs_var_dict': {'name': 'SPFH',
                                     'levels': ['P1000', 'P925', 'P850',
                                                'P700', 'P500', 'P300',
                                                'P250', 'P200', 'P100',
                                                'P50', 'P20', 'P10', 'P5']},
                    'obs_name': 'ADPUPA'},
        'Temp': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS'],
                 'fcst_var_dict': {'name': 'TMP',
                                   'levels': ['P1000', 'P925', 'P850', 'P700',
                                              'P500', 'P300', 'P250', 'P200',
                                              'P100', 'P50', 'P20', 'P10',
                                              'P5']},
                 'obs_var_dict': {'name': 'TMP',
                                  'levels': ['P1000', 'P925', 'P850', 'P700',
                                             'P500', 'P300', 'P250', 'P200',
                                             'P100', 'P50', 'P20', 'P10',
                                             'P5']},
                 'obs_name': 'ADPUPA'},
        'UWind': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS'],
                  'fcst_var_dict': {'name': 'UGRD',
                                    'levels': ['P1000', 'P925', 'P850', 'P700',
                                               'P500', 'P300', 'P250', 'P200',
                                               'P100', 'P50', 'P20', 'P10',
                                               'P5']},
                  'obs_var_dict': {'name': 'UGRD',
                                   'levels': ['P1000', 'P925', 'P850', 'P700',
                                              'P500', 'P300', 'P250', 'P200',
                                              'P100', 'P50', 'P20', 'P10',
                                              'P5']},
                  'obs_name': 'ADPUPA'},
        'VWind': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS'],
                  'fcst_var_dict': {'name': 'VGRD',
                                    'levels': ['P1000', 'P925', 'P850', 'P700',
                                               'P500', 'P300', 'P250', 'P200',
                                               'P100', 'P50', 'P20', 'P10',
                                               'P5']},
                  'obs_var_dict': {'name': 'VGRD',
                                   'levels': ['P1000', 'P925', 'P850', 'P700',
                                              'P500', 'P300', 'P250', 'P200',
                                              'P100', 'P50', 'P20', 'P10',
                                              'P5']},
                  'obs_name': 'ADPUPA'},
        'VectorWind': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                    'CONUS'],
                       'fcst_var_dict': {'name': 'UGRD_VGRD',
                                         'levels': ['P1000', 'P925', 'P850',
                                                    'P700', 'P500', 'P300',
                                                    'P250', 'P200', 'P100',
                                                    'P50', 'P20', 'P10',
                                                    'P5']},
                       'obs_var_dict': {'name': 'UGRD_VGRD',
                                        'levels': ['P1000', 'P925', 'P850',
                                                   'P700', 'P500', 'P300',
                                                   'P250', 'P200', 'P100',
                                                   'P50', 'P20', 'P10', 'P5']},
                       'obs_name': 'ADPUPA'}
    },
    'ptype': {
        'Rain': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                              'CONUS_South', 'CONUS_West', 'Alaska'],
                 'fcst_var_dict': {'name': 'CRAIN',
                                   'levels': ['L0']},
                 'obs_var_dict': {'name': 'PRWE',
                                  'levels':['Z0']},
                 'obs_name': 'ADPSFC'},
        'Snow': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                              'CONUS_South', 'CONUS_West', 'Alaska'],
                 'fcst_var_dict': {'name': 'CSNOW',
                                   'levels': ['L0']},
                 'obs_var_dict': {'name': 'PRWE',
                                  'levels':['Z0']},
                 'obs_name': 'ADPSFC'},
        'FrzRain': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                 'CONUS_South', 'CONUS_West', 'Alaska'],
                    'fcst_var_dict': {'name': 'CFRZR',
                                      'levels': ['L0']},
                    'obs_var_dict': {'name': 'PRWE',
                                     'levels':['Z0']},
                    'obs_name': 'ADPSFC'},
        'IcePel': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                'CONUS_South', 'CONUS_West', 'Alaska'],
                   'fcst_var_dict': {'name': 'CICEP',
                                     'levels': ['L0']},
                   'obs_var_dict': {'name': 'PRWE',
                                    'levels':['Z0']},
                   'obs_name': 'ADPSFC'},
    },
    'sfc': {
        'CAPEMixedLayer': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                        'CONUS_South', 'CONUS_West',
                                        'Appalachia', 'CPlains', 'DeepSouth',
                                        'GreatBasin', 'GreatLakes',
                                        'Mezqutial', 'MidAtlantic',
                                        'NorthAtlantic', 'NPlains', 'NRockies',
                                        'PacificNW', 'PacificSW', 'Prairie',
                                        'Southeast', 'Southwest', 'SPlains',
                                        'SRockies'],
                           'fcst_var_dict': {'name': 'CAPE',
                                             'levels': ['P90-0']},
                           'obs_var_dict': {'name': 'MLCAPE',
                                            'levels': ['L90000-0']},
                           'obs_name': 'ADPUPA'},
        'CAPESfcBased': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                      'CONUS_South', 'CONUS_West',
                                      'Appalachia', 'CPlains', 'DeepSouth',
                                      'GreatBasin', 'GreatLakes', 'Mezqutial',
                                      'MidAtlantic', 'NorthAtlantic',
                                      'NPlains', 'NRockies', 'PacificNW',
                                      'PacificSW', 'Prairie', 'Southeast',
                                      'Southwest', 'SPlains', 'SRockies'],
                         'fcst_var_dict': {'name': 'CAPE',
                                           'levels': ['Z0']},
                         'obs_var_dict': {'name': 'CAPE',
                                          'levels': ['L100000-0']},
                         'obs_name': 'ADPUPA'},
        'Ceiling': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                 'CONUS_South', 'CONUS_West', 'Appalachia',
                                 'CPlains', 'DeepSouth', 'GreatBasin',
                                 'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                 'NorthAtlantic', 'NPlains', 'NRockies',
                                 'PacificNW', 'PacificSW', 'Prairie',
                                 'Southeast', 'Southwest', 'SPlains',
                                 'SRockies'],
                    'fcst_var_dict': {'name': 'HGT',
                                      'levels': ['CEILING']},
                    'obs_var_dict': {'name': 'CEILING',
                                     'levels': ['L0']},
                    'obs_name': 'ADPSFC'},
        'DailyAvg_TempAnom2m': {'vx_masks': ['CONUS', 'CONUS_Central',
                                             'CONUS_East', 'CONUS_South',
                                             'CONUS_West', 'Appalachia',
                                             'CPlains', 'DeepSouth',
                                             'GreatBasin', 'GreatLakes',
                                             'Mezqutial', 'MidAtlantic',
                                             'NorthAtlantic', 'NPlains',
                                             'NRockies', 'PacificNW',
                                             'PacificSW', 'Prairie',
                                             'Southeast', 'Southwest',
                                             'SPlains', 'SRockies'],
                                'fcst_var_dict': {'name': 'TMP_ANOM_DAILYAVG',
                                                  'levels': ['Z2']},
                                'obs_var_dict': {'name': 'TMP_ANOM_DAILYAVG',
                                                 'levels': ['Z2']},
                                'obs_name': 'ADPSFC'},
        'Dewpoint2m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                    'CONUS_South', 'CONUS_West', 'Appalachia',
                                    'CPlains', 'DeepSouth', 'GreatBasin',
                                    'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                    'NorthAtlantic', 'NPlains', 'NRockies',
                                    'PacificNW', 'PacificSW', 'Prairie',
                                    'Southeast', 'Southwest', 'SPlains',
                                    'SRockies'],
                       'fcst_var_dict': {'name': 'DPT',
                                         'levels': ['Z2']},
                       'obs_var_dict': {'name': 'DPT',
                                        'levels': ['Z2']},
                       'obs_name': 'ADPSFC'},
        'PBLHeight': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                   'CONUS_South', 'CONUS_West', 'Appalachia',
                                   'CPlains', 'DeepSouth', 'GreatBasin',
                                   'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                   'NorthAtlantic', 'NPlains', 'NRockies',
                                   'PacificNW', 'PacificSW', 'Prairie',
                                   'Southeast', 'Southwest', 'SPlains',
                                   'SRockies'],
                      'fcst_var_dict': {'name': 'HPBL',
                                        'levels': ['L0']},
                      'obs_var_dict': {'name': 'HPBL',
                                       'levels': ['L0']},
                      'obs_name': 'ADPUPA'},
        'RelHum2m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                  'CONUS_South', 'CONUS_West', 'Appalachia',
                                  'CPlains', 'DeepSouth', 'GreatBasin',
                                  'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                  'NorthAtlantic', 'NPlains', 'NRockies',
                                  'PacificNW', 'PacificSW', 'Prairie',
                                  'Southeast', 'Southwest', 'SPlains',
                                  'SRockies'],
                     'fcst_var_dict': {'name': 'RH',
                                       'levels': ['Z2']},
                     'obs_var_dict': {'name': 'RH',
                                      'levels': ['Z2']},
                     'obs_name': 'ADPSFC'},
        'SeaLevelPres': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                      'CONUS_South', 'CONUS_West',
                                      'Appalachia', 'CPlains', 'DeepSouth',
                                      'GreatBasin', 'GreatLakes', 'Mezqutial',
                                      'MidAtlantic', 'NorthAtlantic',
                                      'NPlains', 'NRockies', 'PacificNW',
                                      'PacificSW', 'Prairie', 'Southeast',
                                      'Southwest', 'SPlains', 'SRockies'],
                         'fcst_var_dict': {'name': 'PRMSL',
                                           'levels': ['Z0']},
                         'obs_var_dict': {'name': 'PRMSL',
                                          'levels': ['Z0']},
                         'obs_name': 'ADPSFC'},
        'Temp2m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                'CONUS_South', 'CONUS_West', 'Appalachia',
                                'CPlains', 'DeepSouth', 'GreatBasin',
                                'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                'NorthAtlantic', 'NPlains', 'NRockies',
                                'PacificNW', 'PacificSW', 'Prairie',
                                'Southeast', 'Southwest', 'SPlains',
                                'SRockies'],
                   'fcst_var_dict': {'name': 'TMP',
                                     'levels': ['Z2']},
                   'obs_var_dict': {'name': 'TMP',
                                    'levels': ['Z2']},
                   'obs_name': 'ADPSFC'},
        'TotCloudCover': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                       'CONUS_South', 'CONUS_West',
                                       'Appalachia', 'CPlains', 'DeepSouth',
                                       'GreatBasin', 'GreatLakes', 'Mezqutial',
                                       'MidAtlantic', 'NorthAtlantic',
                                       'NPlains', 'NRockies', 'PacificNW',
                                       'PacificSW', 'Prairie', 'Southeast',
                                       'Southwest', 'SPlains', 'SRockies'],
                          'fcst_var_dict': {'name': 'TCDC',
                                            'levels': ['TOTAL']},
                          'obs_var_dict': {'name': 'TCDC',
                                           'levels': ['L0']},
                          'obs_name': 'ADPSFC'},
        'UWind10m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                  'CONUS_South', 'CONUS_West', 'Appalachia',
                                  'CPlains', 'DeepSouth', 'GreatBasin',
                                  'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                  'NorthAtlantic', 'NPlains', 'NRockies',
                                  'PacificNW', 'PacificSW', 'Prairie',
                                  'Southeast', 'Southwest', 'SPlains',
                                  'SRockies'],
                     'fcst_var_dict': {'name': 'UGRD',
                                       'levels': ['Z10']},
                     'obs_var_dict': {'name': 'UGRD',
                                      'levels': ['Z10']},
                     'obs_name': 'ADPSFC'},
        'Visibility': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                    'CONUS_South', 'CONUS_West', 'Appalachia',
                                    'CPlains', 'DeepSouth', 'GreatBasin',
                                    'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                    'NorthAtlantic', 'NPlains', 'NRockies',
                                    'PacificNW', 'PacificSW', 'Prairie',
                                    'Southeast', 'Southwest', 'SPlains',
                                    'SRockies'],
                       'fcst_var_dict': {'name': 'VIS',
                                         'levels': ['Z0']},
                       'obs_var_dict': {'name': 'VIS',
                                        'levels': ['Z0']},
                       'obs_name': 'ADPSFC'},
        'VWind10m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                  'CONUS_South', 'CONUS_West', 'Appalachia',
                                  'CPlains', 'DeepSouth', 'GreatBasin',
                                  'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                  'NorthAtlantic', 'NPlains', 'NRockies',
                                  'PacificNW', 'PacificSW', 'Prairie',
                                  'Southeast', 'Southwest', 'SPlains',
                                  'SRockies'],
                     'fcst_var_dict': {'name': 'VGRD',
                                       'levels': ['Z10']},
                     'obs_var_dict': {'name': 'VGRD',
                                      'levels': ['Z10']},
                     'obs_name': 'ADPSFC'},
        'WindGust': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                  'CONUS_South', 'CONUS_West', 'Appalachia',
                                  'CPlains', 'DeepSouth', 'GreatBasin',
                                  'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                  'NorthAtlantic', 'NPlains', 'NRockies',
                                  'PacificNW', 'PacificSW', 'Prairie',
                                  'Southeast', 'Southwest', 'SPlains',
                                  'SRockies'],
                     'fcst_var_dict': {'name': 'GUST',
                                       'levels': ['Z0']},
                     'obs_var_dict': {'name': 'GUST',
                                      'levels': ['Z0']},
                     'obs_name': 'ADPSFC'},
        'VectorWind10m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                       'CONUS_South', 'CONUS_West',
                                       'Appalachia', 'CPlains', 'DeepSouth',
                                       'GreatBasin', 'GreatLakes', 'Mezqutial',
                                       'MidAtlantic', 'NorthAtlantic',
                                       'NPlains', 'NRockies', 'PacificNW',
                                       'PacificSW', 'Prairie', 'Southeast',
                                       'Southwest', 'SPlains', 'SRockies'],
                          'fcst_var_dict': {'name': 'UGRD_VGRD',
                                            'levels': ['Z10']},
                          'obs_var_dict': {'name': 'UGRD_VGRD',
                                           'levels': ['Z10']},
                          'obs_name': 'ADPSFC'}
    }
}

################################################
#### condense_stats jobs
################################################
condense_stats_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
#### pres_levs
for pres_levs_job in list(condense_stats_jobs_dict['pres_levs'].keys()):
    if pres_levs_job == 'VectorWind':
        pres_levs_job_line_types = ['VL1L2']
    else:
        pres_levs_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['pres_levs'][pres_levs_job]['line_types'] = (
        pres_levs_job_line_types
    )
#### ptype
for ptype_job in list(condense_stats_jobs_dict['ptype'].keys()):
    condense_stats_jobs_dict['ptype'][ptype_job]['line_types'] = ['CTC']
#### sfc
for sfc_job in list(condense_stats_jobs_dict['sfc'].keys()):
    if sfc_job == 'VectorWind10m':
        sfc_job_line_types = ['VL1L2']
    elif sfc_job in ['Dewpoint2m', 'CAPESfcBased', 'CAPEMixedLayer']:
        sfc_job_line_types = ['SL1L2', 'CTC']
    elif sfc_job in ['Visibility', 'Ceiling']:
        sfc_job_line_types = ['CTC']
    else:
        sfc_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['sfc'][sfc_job]['line_types'] = sfc_job_line_types
if JOB_GROUP == 'condense_stats':
    JOB_GROUP_dict = condense_stats_jobs_dict

################################################
#### filter_stats jobs
################################################
filter_stats_jobs_dict = copy.deepcopy(condense_stats_jobs_dict)
#### pres_levs
for pres_levs_job in list(filter_stats_jobs_dict['pres_levs'].keys()):
    filter_stats_jobs_dict['pres_levs'][pres_levs_job]['grid'] = 'G004'
    (filter_stats_jobs_dict['pres_levs'][pres_levs_job]\
     ['fcst_var_dict']['threshs']) = ['NA']
    (filter_stats_jobs_dict['pres_levs'][pres_levs_job]\
     ['obs_var_dict']['threshs']) = ['NA']
    filter_stats_jobs_dict['pres_levs'][pres_levs_job]['interps'] = [
        'BILIN/4'
    ]
#### ptype
for ptype_job in list(filter_stats_jobs_dict['ptype'].keys()):
    filter_stats_jobs_dict['ptype'][ptype_job]['grid'] = 'G104'
    filter_stats_jobs_dict['ptype'][ptype_job]['interps'] = ['NEAREST/1']
    filter_stats_jobs_dict['ptype'][ptype_job]['fcst_var_dict']['threshs'] = [
        'ge1.0'
    ]
    if ptype_job == 'Rain':
        ptype_job_obs_threshs = ['ge161&&le163']
    elif ptype_job == 'Snow':
        ptype_job_obs_threshs = ['ge171&&le173']
    elif ptype_job == 'FrzRain':
        ptype_job_obs_threshs = ['ge164&&le166']
    elif ptype_job == 'IcePel':
        ptype_job_obs_threshs = ['ge174&&le176']
    filter_stats_jobs_dict['ptype'][ptype_job]['obs_var_dict']['threshs'] = (
        ptype_job_obs_threshs
    )
#### sfc
for sfc_job in list(filter_stats_jobs_dict['sfc'].keys()):
    filter_stats_jobs_dict['sfc'][sfc_job]['grid'] = 'G104'
    filter_stats_jobs_dict['sfc'][sfc_job]['interps'] = ['BILIN/4']
    if 'CAPE' in sfc_job:
        sfc_job_fcst_threshs = ['gt0||']
        sfc_job_obs_threshs = ['gt0']
    elif sfc_job == 'Ceiling':
        sfc_job_fcst_threshs = [
            'lt152', 'lt305', 'lt914', 'ge914', 'lt1524', 'lt3048'
        ]
        sfc_job_obs_threshs = [
            'lt152', 'lt305', 'lt914', 'ge914', 'lt1524', 'lt3048'
        ]
    elif sfc_job == 'Visibility':
        sfc_job_fcst_threshs = [
            'lt805', 'lt1609', 'lt4828', 'lt8045', 'ge8045', 'lt16090'
        ]
        sfc_job_obs_threshs = [
            'lt805', 'lt1609', 'lt4828', 'lt8045', 'ge8045', 'lt16090'
        ]
    else:
        sfc_job_fcst_threshs = ['NA']
        sfc_job_obs_threshs = ['NA']
    filter_stats_jobs_dict['sfc'][sfc_job]['fcst_var_dict']['threshs'] = (
        sfc_job_fcst_threshs
    )
    filter_stats_jobs_dict['sfc'][sfc_job]['obs_var_dict']['threshs'] = (
        sfc_job_obs_threshs
    )
    if sfc_job in ['Dewpoint2m', 'CAPESfcBased', 'CAPEMixedLayer']:
        filter_stats_jobs_dict['sfc'][sfc_job]['line_types'] = ['SL1L2']
        filter_stats_jobs_dict['sfc'][f"{sfc_job}_Thresh"] = copy.deepcopy(
            filter_stats_jobs_dict['sfc'][sfc_job]
        )
        filter_stats_jobs_dict['sfc'][f"{sfc_job}_Thresh"]['line_types'] = [
            'CTC'
        ]
        if 'CAPE' in sfc_job:
            (filter_stats_jobs_dict['sfc'][f"{sfc_job}_Thresh"]\
             ['fcst_var_dict']['threshs']) = [
                'ge500', 'ge1000', 'ge1500', 'ge2000', 'ge3000', 'ge4000',
                'ge5000'
             ]
            (filter_stats_jobs_dict['sfc'][f"{sfc_job}_Thresh"]\
             ['obs_var_dict']['threshs']) = [
                'ge500', 'ge1000', 'ge1500', 'ge2000', 'ge3000', 'ge4000',
                'ge5000'
             ]
        elif sfc_job == 'Dewpoint2m':
            (filter_stats_jobs_dict['sfc'][f"{sfc_job}_Thresh"]\
             ['fcst_var_dict']['threshs']) = [
                 'ge277.594', 'ge283.15', 'ge288.706', 'ge294.261'
             ]
            (filter_stats_jobs_dict['sfc'][f"{sfc_job}_Thresh"]\
             ['obs_var_dict']['threshs']) = [
                 'ge277.594', 'ge283.15', 'ge288.706', 'ge294.261'
             ]
if JOB_GROUP == 'filter_stats':
    JOB_GROUP_dict = filter_stats_jobs_dict

################################################
#### make_plots jobs
################################################
make_plots_jobs_dict = copy.deepcopy(filter_stats_jobs_dict)
#### pres_levs
for pres_levs_job in list(make_plots_jobs_dict['pres_levs'].keys()):
    del make_plots_jobs_dict['pres_levs'][pres_levs_job]['line_types']
    if pres_levs_job == 'VectorWind':
        pres_levs_job_line_type_stats = ['VL1L2/ME', 'VL1L2/RMSE']
    else:
        pres_levs_job_line_type_stats = ['SL1L2/ME', 'SL1L2/RMSE']
    make_plots_jobs_dict['pres_levs'][pres_levs_job]['line_type_stats'] = (
        pres_levs_job_line_type_stats
    )
    make_plots_jobs_dict['pres_levs'][pres_levs_job]['plots'] = [
        'time_series', 'lead_average', 'stat_by_level', 'lead_by_level'
    ]
#### ptype
for ptype_job in list(make_plots_jobs_dict['ptype'].keys()):
    del make_plots_jobs_dict['ptype'][ptype_job]['line_types']
    make_plots_jobs_dict['ptype'][ptype_job]['line_type_stats'] = ['CTC/FBIAS']
    make_plots_jobs_dict['ptype'][ptype_job]['plots'] = [
        'time_series', 'lead_average'
    ]
#### sfc
for sfc_job in list(make_plots_jobs_dict['sfc'].keys()):
    del make_plots_jobs_dict['sfc'][sfc_job]['line_types']
    if sfc_job in ['CAPEMixedLayer', 'CAPESfcBased', 'PBLHeight',
                   'TotCloudCover']:
        sfc_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
        make_plots_jobs_dict['sfc'][sfc_job+'_FBAR_OBAR'] = copy.deepcopy(
            make_plots_jobs_dict['sfc'][sfc_job]
        )
        make_plots_jobs_dict['sfc'][sfc_job+'_FBAR_OBAR']['line_type_stats']=[
            'SL1L2/FBAR_OBAR'
        ]
        make_plots_jobs_dict['sfc'][sfc_job+'_FBAR_OBAR']['vx_masks']=[
            'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 'CONUS_South'
        ]
        make_plots_jobs_dict['sfc'][sfc_job+'_FBAR_OBAR']['plots'] = [
            'time_series'
        ]
    elif sfc_job in ['CAPEMixedLayer_Thresh', 'CAPESfcBased_Thresh',
                     'Dewpoint2m_Thresh']:
        sfc_job_line_type_stats = ['CTC/FBIAS']
    elif sfc_job in ['Ceiling', 'Visibility']:
        sfc_job_line_type_stats = ['CTC/FBIAS', 'CTC/ETS']
    elif sfc_job == 'VectorWind10m':
        sfc_job_line_type_stats = ['VL1L2/RMSE', 'VL1L2/ME']
    else:
        sfc_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
    if sfc_job in ['CAPEMixedLayer', 'CAPESfcBased', 'Dewpoint2m', 'Temp2m']:
        sfc_job_plots = ['time_series', 'lead_average', 'valid_hour_average']
    elif sfc_job in ['CAPEMixedLayer_Thresh', 'CAPESfcBased_Thresh',
                     'Dewpoint2m_Thresh']:
        sfc_job_plots = ['time_series', 'lead_average', 'threshold_average']
    else:
        sfc_job_plots = ['time_series', 'lead_average']
    make_plots_jobs_dict['sfc'][sfc_job]['line_type_stats'] = (
        sfc_job_line_type_stats
    )
    make_plots_jobs_dict['sfc'][sfc_job]['plots'] = sfc_job_plots
for cape_level in ['MixedLayer', 'SfcBased']:
    make_plots_jobs_dict['sfc'][f"CAPE{cape_level}_PerfDiag"] = copy.deepcopy(
        make_plots_jobs_dict['sfc'][f"CAPE{cape_level}_Thresh"]
    )
    (make_plots_jobs_dict['sfc'][f"CAPE{cape_level}_PerfDiag"]\
     ['line_type_stats']) = ['CTC/PERFDIAG']
    make_plots_jobs_dict['sfc'][f"CAPE{cape_level}_PerfDiag"]['plots'] = [
        'performance_diagram'
    ]
if JOB_GROUP == 'make_plots':
    JOB_GROUP_dict = make_plots_jobs_dict

################################################
#### tar_images jobs
################################################
tar_images_jobs_dict = {
    'pres_levs': {
        'search_base_dir': os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'plot_output', f"{RUN}.{end_date}",
                                        f"{VERIF_CASE}_pres_levs",
                                        f"last{NDAYS}days")
    },
    'ptype': {
        'search_base_dir': os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'plot_output', f"{RUN}.{end_date}",
                                        f"{VERIF_CASE}_ptype",
                                        f"last{NDAYS}days")
    },
    'sfc': {
        'search_base_dir': os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'plot_output', f"{RUN}.{end_date}",
                                        f"{VERIF_CASE}_sfc",
                                        f"last{NDAYS}days")
    }
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
                            ['lead_average', 'lead_by_level',
                             'lead_by_date']:
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
                f"{str(iproc-1)} /bin/echo {str(iproc)}\n"
            )
        else:
            poe_file.write(
                f"/bin/echo {str(iproc)}\n"
            )
        iproc+=1
    poe_file.close()

print("END: "+os.path.basename(__file__))
