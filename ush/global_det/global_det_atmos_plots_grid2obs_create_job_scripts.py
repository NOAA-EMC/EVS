'''
Program Name: global_det_atmos_plots_grid2obs_create_job_scripts.py
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

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
################################################
#### Plotting jobs
################################################
plot_jobs_dict = {
    'pres_levs': {
        'GeoHeight': {'line_type_stat_list': ['SL1L2/BIAS',
                                              'SL1L2/RMSE'],
                      'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                       'TROPICS', 'CONUS'],
                      'fcst_var_dict': {'name': 'HGT',
                                        'levels': ('P1000, P925, P850, P700, '
                                                   +'P500, P400, P300, P250, '
                                                   +'P200, P150, P100, P50, '
                                                   +'P20, P10, P5, P1'),
                                        'threshs': 'NA'},
                      'obs_var_dict': {'name': 'HGT',
                                       'levels': ('P1000, P925, P850, P700, '
                                                  +'P500, P400, P300, P250, '
                                                  +'P200, P150, P100, P50, '
                                                  +'P20, P10, P5, P1'),
                                       'threshs': 'NA'},
                      'interp_dict': {'method': 'BILIN',
                                      'points': '4'},
                      'grid': 'G004',
                      'obs_name': 'ADPUPA',
                      'plots_list': ('time_series, lead_average, '
                                     +'stat_by_level, lead_level')},
        'RelHum': {'line_type_stat_list': ['SL1L2/BIAS',
                                           'SL1L2/RMSE'],
                   'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                    'TROPICS', 'CONUS'],
                   'fcst_var_dict': {'name': 'RH',
                                     'levels': ('P1000, P925, P850, P700, '
                                                +'P500, P400, P300, P250, '
                                                +'P200, P150, P100, P50, '
                                                +'P20, P10, P5, P1'),
                                     'threshs': 'NA'},
                   'obs_var_dict': {'name': 'RH',
                                    'levels': ('P1000, P925, P850, P700, '
                                               +'P500, P400, P300, P250, '
                                               +'P200, P150, P100, P50, '
                                               +'P20, P10, P5, P1'),
                                    'threshs': 'NA'},
                   'interp_dict': {'method': 'BILIN',
                                   'points': '4'},
                   'grid': 'G004',
                   'obs_name': 'ADPUPA',
                   'plots_list': ('time_series, lead_average, '
                                  +'stat_by_level, lead_level')},
        'SpefHum': {'line_type_stat_list': ['SL1L2/BIAS',
                                            'SL1L2/RMSE'],
                    'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                     'TROPICS', 'CONUS'],
                    'fcst_var_dict': {'name': 'SPFH',
                                      'levels': ('P1000, P925, P850, P700, '
                                                 +'P500, P400, P300, P250, '
                                                 +'P200, P150, P100, P50, '
                                                 +'P20, P10, P5, P1'),
                                      'threshs': 'NA'},
                    'obs_var_dict': {'name': 'SPFH',
                                     'levels': ('P1000, P925, P850, P700, '
                                                +'P500, P400, P300, P250, '
                                                +'P200, P150, P100, P50, '
                                                +'P20, P10, P5, P1'),
                                     'threshs': 'NA'},
                    'interp_dict': {'method': 'BILIN',
                                    'points': '4'},
                    'obs_name': 'ADPUPA',
                    'grid': 'G004',
                    'plots_list': ('time_series, lead_average, '
                                   +'stat_by_level, lead_level')},
        'Temp': {'line_type_stat_list': ['SL1L2/BIAS',
                                         'SL1L2/RMSE'],
                 'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                  'TROPICS', 'CONUS'],
                 'fcst_var_dict': {'name': 'TMP',
                                   'levels': ('P1000, P925, P850, P700, '
                                              +'P500, P400, P300, P250, '
                                              +'P200, P150, P100, P50, '
                                              +'P20, P10, P5, P1'),
                                   'threshs': 'NA'},
                  'obs_var_dict': {'name': 'TMP',
                                   'levels': ('P1000, P925, P850, P700, '
                                              +'P500, P400, P300, P250, '
                                              +'P200, P150, P100, P50, '
                                              +'P20, P10, P5, P1'),
                                   'threshs': 'NA'},
                  'interp_dict': {'method': 'BILIN',
                                  'points': '4'},
                  'grid': 'G004',
                  'obs_name': 'ADPUPA',
                  'plots_list': ('time_series, lead_average, '
                                 +'stat_by_level, lead_level')},
        'UWind': {'line_type_stat_list': ['SL1L2/BIAS',
                                          'SL1L2/RMSE'],
                  'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                   'TROPICS', 'CONUS'],
                  'fcst_var_dict': {'name': 'UGRD',
                                    'levels': ('P1000, P925, P850, P700, '
                                               +'P500, P400, P300, P250, '
                                               +'P200, P150, P100, P50, '
                                               +'P20, P10, P5, P1'),
                                    'threshs': 'NA'},
                  'obs_var_dict': {'name': 'UGRD',
                                   'levels': ('P1000, P925, P850, P700, '
                                              +'P500, P400, P300, P250, '
                                              +'P200, P150, P100, P50, '
                                              +'P20, P10, P5, P1'),
                                   'threshs': 'NA'},
                  'interp_dict': {'method': 'BILIN',
                                  'points': '4'},
                  'grid': 'G004',
                  'obs_name': 'ADPUPA',
                  'plots_list': ('time_series, lead_average, '
                                 +'stat_by_level, lead_level')},
        'VWind': {'line_type_stat_list': ['SL1L2/BIAS',
                                          'SL1L2/RMSE'],
                  'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                   'TROPICS', 'CONUS'],
                  'fcst_var_dict': {'name': 'VGRD',
                                    'levels': ('P1000, P925, P850, P700, '
                                               +'P500, P400, P300, P250, '
                                               +'P200, P150, P100, P50, '
                                               +'P20, P10, P5, P1'),
                                    'threshs': 'NA'},
                  'obs_var_dict': {'name': 'VGRD',
                                   'levels': ('P1000, P925, P850, P700, '
                                              +'P500, P400, P300, P250, '
                                              +'P200, P150, P100, P50, '
                                              +'P20, P10, P5, P1'),
                                   'threshs': 'NA'},
                  'interp_dict': {'method': 'BILIN',
                                  'points': '4'},
                  'grid': 'G004',
                  'obs_name': 'ADPUPA',
                  'plots_list': ('time_series, lead_average, '
                                 +'stat_by_level, lead_level')},
        'VectorWind': {'line_type_stat_list': ['VL1L2/BIAS',
                                               'VL1L2/RMSE'],
                       'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                        'TROPICS', 'CONUS'],
                       'fcst_var_dict': {'name': 'UGRD_VGRD',
                                         'levels': ('P1000, P925, P850, P700, '
                                                    +'P500, P400, P300, P250, '
                                                    +'P200, P150, P100, P50, '
                                                    +'P20, P10, P5, P1'),
                                         'threshs': 'NA'},
                       'obs_var_dict': {'name': 'UGRD_VGRD',
                                        'levels': ('P1000, P925, P850, P700, '
                                                   +'P500, P400, P300, P250, '
                                                   +'P200, P150, P100, P50, '
                                                   +'P20, P10, P5, P1'),
                                        'threshs': 'NA'},
                       'interp_dict': {'method': 'BILIN',
                                       'points': '4'},
                       'grid': 'G004',
                       'obs_name': 'ADPUPA',
                       'plots_list': ('time_series, lead_average, '
                                      +'stat_by_level, lead_level')}
    },
    'sea_ice': {},
    'sfc': {
        'CAPEMixedLayer': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS',
                                                   'SL1L2/FBAR_OBAR'],
                           'vx_mask_list': ['CONUS', 'CONUS_Central',
                                            'CONUS_East', 'CONUS_South',
                                            'CONUS_West', 'Appalachia',
                                            'CPlains', 'DeepSouth',
                                            'GreatBasin', 'GreatLakes',
                                            'Mezqutial', 'MidAtlantic',
                                            'NorthAtlantic', 'NPlains',
                                            'NRockies', 'PacificNW',
                                            'PacificSW', 'Prairie',
                                            'Southeast', 'Southwest', 'SPlains',
                                            'SRockies'],
                           'fcst_var_dict': {'name': 'CAPE',
                                             'levels': 'P90-0',
                                             'threshs': 'gt0||'},
                           'obs_var_dict': {'name': 'MLCAPE',
                                            'levels': 'L90000-0',
                                            'threshs': 'gt0'},
                           'interp_dict': {'method': 'BILIN',
                                           'points': '4'},
                           'grid': 'G104',
                           'obs_name': 'ADPUPA',
                           'plots_list': ('time_series, lead_average, '
                                          +'valid_hour_average')},
        'CAPEMixedLayer_Thresh': {'line_type_stat_list': ['CTC/FBIAS'],
                                  'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                                  'fcst_var_dict': {'name': 'CAPE',
                                                    'levels': 'P90-0',
                                                    'threshs': ('ge500, ge1000, '
                                                               +'ge1500, ge2000, '
                                                               +'ge3000, ge4000, '
                                                               +'ge5000')},
                                  'obs_var_dict': {'name': 'MLCAPE',
                                                   'levels': 'L90000-0',
                                                   'threshs': ('ge500, ge1000, '
                                                              +'ge1500, ge2000, '
                                                              +'ge3000, ge4000, '
                                                              +'ge5000')},
                                  'interp_dict': {'method': 'BILIN',
                                                  'points': '4'},
                                  'grid': 'G104',
                                  'obs_name': 'ADPUPA',
                                  'plots_list': ('time_series, lead_average, '
                                                 'threshold_average')},
        'CAPEMixedLayer_PerfDia': {'line_type_stat_list': ['CTC/PERF_DIA'],
                                   'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                                   'fcst_var_dict': {'name': 'CAPE',
                                                     'levels': 'P90-0',
                                                     'threshs': ('ge500, ge1000, '
                                                                +'ge1500, ge2000, '
                                                                +'ge3000, ge4000, '
                                                                +'ge5000')},
                                   'obs_var_dict': {'name': 'MLCAPE',
                                                    'levels': 'L90000-0',
                                                    'threshs': ('ge500, ge1000, '
                                                               +'ge1500, ge2000, '
                                                               +'ge3000, ge4000, '
                                                               +'ge5000')},
                                   'interp_dict': {'method': 'BILIN',
                                                   'points': '4'},
                                   'grid': 'G104',
                                   'obs_name': 'ADPUPA',
                                   'plots_list': 'performance_diagram'},
        'CAPESfcBased': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS',
                                                 'SL1L2/FBAR_OBAR'],
                         'vx_mask_list': ['CONUS', 'CONUS_Central',
                                          'CONUS_East', 'CONUS_South',
                                          'CONUS_West', 'Appalachia',
                                          'CPlains', 'DeepSouth',
                                          'GreatBasin', 'GreatLakes',
                                          'Mezqutial', 'MidAtlantic',
                                          'NorthAtlantic', 'NPlains',
                                          'NRockies', 'PacificNW',
                                          'PacificSW', 'Prairie',
                                          'Southeast', 'Southwest', 'SPlains',
                                          'SRockies'],
                         'fcst_var_dict': {'name': 'CAPE',
                                           'levels': 'Z0',
                                           'threshs': 'gt0||'},
                         'obs_var_dict': {'name': 'CAPE',
                                          'levels': 'L100000-0',
                                          'threshs': 'gt0'},
                         'interp_dict': {'method': 'BILIN',
                                         'points': '4'},
                         'grid': 'G104',
                         'obs_name': 'ADPUPA',
                         'plots_list': ('time_series, lead_average, '
                                        +'valid_hour_average')},
        'CAPESfcBased_Thresh': {'line_type_stat_list': ['CTC/FBIAS'],
                                'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                                'fcst_var_dict': {'name': 'CAPE',
                                                  'levels': 'Z0',
                                                  'threshs': ('ge500, ge1000, '
                                                             +'ge1500, ge2000, '
                                                             +'ge3000, ge4000, '
                                                             +'ge5000')},
                                'obs_var_dict': {'name': 'CAPE',
                                                 'levels': 'L100000-0',
                                                 'threshs': ('ge500, ge1000, '
                                                            +'ge1500, ge2000, '
                                                            +'ge3000, ge4000, '
                                                            +'ge5000')},
                                'interp_dict': {'method': 'BILIN',
                                                'points': '4'},
                                'grid': 'G104',
                                'obs_name': 'ADPUPA',
                                'plots_list': ('time_series, lead_average, '
                                               'threshold_average')},
        'CAPESfcBased_PerfDia': {'line_type_stat_list': ['CTC/PERF_DIA'],
                                 'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                                 'fcst_var_dict': {'name': 'CAPE',
                                                   'levels': 'Z0',
                                                   'threshs': ('ge500, ge1000, '
                                                              +'ge1500, ge2000, '
                                                              +'ge3000, ge4000, '
                                                              +'ge5000')},
                                 'obs_var_dict': {'name': 'CAPE',
                                                  'levels': 'L100000-0',
                                                  'threshs': ('ge500, ge1000, '
                                                             +'ge1500, ge2000, '
                                                             +'ge3000, ge4000, '
                                                             +'ge5000')},
                                 'interp_dict': {'method': 'BILIN',
                                                 'points': '4'},
                                 'grid': 'G104',
                                 'obs_name': 'ADPUPA',
                                 'plots_list': 'performance_diagram'},
        'Ceiling': {'line_type_stat_list': ['CTC/FBIAS', 'CTC/ETS'],
                    'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                    'fcst_var_dict': {'name': 'HGT',
                                      'levels': 'CEILING',
                                      'threshs': ('lt152.4, lt304.8, '
                                                  +'lt914.4, ge914.4, '
                                                  +'lt1524, lt3048')},
                    'obs_var_dict': {'name': 'CEILING',
                                     'levels': 'L0',
                                     'threshs': ('lt152.4, lt304.8, '
                                                 +'lt914.4, ge914.4, '
                                                 +'lt1524, lt3048')},
                    'interp_dict': {'method': 'BILIN',
                                    'points': '4'},
                    'grid': 'G104',
                    'obs_name': 'ADPSFC',
                    'plots_list': 'time_series, lead_average'},
        'DailyAvg_TempAnom2m': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS'],
                                'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                                                  'levels': 'Z2',
                                                  'threshs': 'NA'},
                                'obs_var_dict': {'name': 'TMP_ANOM_DAILYAVG',
                                                 'levels': 'Z2',
                                                 'threshs': 'NA'},
                                'interp_dict': {'method': 'BILIN',
                                                'points': '4'},
                                'grid': 'G104',
                                'obs_name': 'ADPSFC',
                                'plots_list': 'time_series, lead_average'},
        'Dewpoint2m': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS'],
                       'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                       'fcst_var_dict': {'name': 'DPT',
                                         'levels': 'Z2',
                                         'threshs': 'NA'},
                       'obs_var_dict': {'name': 'DPT',
                                        'levels': 'Z2',
                                        'threshs': 'NA'},
                       'interp_dict': {'method': 'BILIN',
                                       'points': '4'},
                       'grid': 'G104',
                       'obs_name': 'ADPSFC',
                       'plots_list': ('time_series, lead_average, '
                                      'valid_hour_average')},
        'Dewpoint2m_Thresh': {'line_type_stat_list': ['CTC/FBIAS'],
                              'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                              'fcst_var_dict': {'name': 'DPT',
                                                'levels': 'Z2',
                                                'threshs': ('ge277.594, '
                                                            +'ge283.15, '
                                                            +'ge288.706, '
                                                            +'ge294.261')},
                              'obs_var_dict': {'name': 'DPT',
                                               'levels': 'Z2',
                                               'threshs': ('ge277.594, '
                                                           +'ge283.15, '
                                                           +'ge288.706, '
                                                           +'ge294.261')},
                              'interp_dict': {'method': 'BILIN',
                                              'points': '4'},
                              'grid': 'G104',
                              'obs_name': 'ADPSFC',
                              'plots_list': ('time_series, lead_average, '
                                             +'threshold_average')},
        'PBLHeight': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS',
                                              'SL1L2/FBAR_OBAR'],
                      'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                      'fcst_var_dict': {'name': 'HPBL',
                                        'levels': 'L0',
                                        'threshs': 'NA'},
                      'obs_var_dict': {'name': 'HPBL',
                                       'levels': 'L0',
                                       'threshs': 'NA'},
                      'interp_dict': {'method': 'BILIN',
                                      'points': '4'},
                      'grid': 'G104',
                      'obs_name': 'ADPUPA',
                      'plots_list': 'time_series, lead_average'},
        'RelHum2m': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS'],
                     'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                     'fcst_var_dict': {'name': 'RH',
                                       'levels': 'Z2',
                                       'threshs': 'NA'},
                     'obs_var_dict': {'name': 'RH',
                                      'levels': 'Z2',
                                      'threshs': 'NA'},
                     'interp_dict': {'method': 'BILIN',
                                     'points': '4'},
                     'grid': 'G104',
                     'obs_name': 'ADPSFC',
                     'plots_list': 'time_series, lead_average'},
        'SeaLevelPres': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS'],
                         'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                         'fcst_var_dict': {'name': 'PRMSL',
                                           'levels': 'Z0',
                                           'threshs': 'NA'},
                         'obs_var_dict': {'name': 'PRMSL',
                                          'levels': 'Z0',
                                          'threshs': 'NA'},
                         'interp_dict': {'method': 'BILIN',
                                         'points': '4'},
                         'grid': 'G104',
                         'obs_name': 'ADPSFC',
                         'plots_list': ('time_series, lead_average')},
        'Temp2m': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS'],
                   'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                   'fcst_var_dict': {'name': 'TMP',
                                     'levels': 'Z2',
                                     'threshs': 'NA'},
                   'obs_var_dict': {'name': 'TMP',
                                    'levels': 'Z2',
                                    'threshs': 'NA'},
                   'interp_dict': {'method': 'BILIN',
                                   'points': '4'},
                   'grid': 'G104',
                   'obs_name': 'ADPSFC',
                   'plots_list': ('time_series, lead_average, '
                                  'valid_hour_average')},
        'TotCloudCover': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS',
                                                  'SL1L2/FBAR_OBAR'],
                          'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                          'fcst_var_dict': {'name': 'TCDC',
                                            'levels': 'TOTAL',
                                            'threshs': 'NA'},
                          'obs_var_dict': {'name': 'TCDC',
                                           'levels': 'L0',
                                           'threshs': 'NA'},
                          'interp_dict': {'method': 'BILIN',
                                          'points': '4'},
                          'grid': 'G104',
                          'obs_name': 'ADPSFC',
                          'plots_list': 'time_series, lead_average'},
        'UWind10m': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS'],
                     'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                     'fcst_var_dict': {'name': 'UGRD',
                                       'levels': 'Z10',
                                       'threshs': 'NA'},
                     'obs_var_dict': {'name': 'UGRD',
                                      'levels': 'Z10',
                                      'threshs': 'NA'},
                     'interp_dict': {'method': 'BILIN',
                                     'points': '4'},
                     'grid': 'G104',
                     'obs_name': 'ADPSFC',
                     'plots_list': 'time_series, lead_average'},
        'Visibility': {'line_type_stat_list': ['CTC/FBIAS', 'CTC/ETS'],
                       'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                       'fcst_var_dict': {'name': 'VIS',
                                         'levels': 'Z0',
                                         'threshs': ('lt804.672, lt1609.344, '
                                                     +'lt4828.032, lt8046.72, '
                                                     +'ge8046.72, lt16093.44')},
                       'obs_var_dict': {'name': 'VIS',
                                        'levels': 'Z0',
                                        'threshs': ('lt804.672, lt1609.344, '
                                                     +'lt4828.032, lt8046.72, '
                                                     +'ge8046.72, lt16093.44')},
                       'interp_dict': {'method': 'BILIN',
                                       'points': '4'},
                       'grid': 'G104',
                       'obs_name': 'ADPSFC',
                       'plots_list': 'time_series, lead_average'},
        'VWind10m': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS'],
                     'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                     'fcst_var_dict': {'name': 'VGRD',
                                       'levels': 'Z10',
                                       'threshs': 'NA'},
                     'obs_var_dict': {'name': 'VGRD',
                                      'levels': 'Z10',
                                      'threshs': 'NA'},
                     'interp_dict': {'method': 'BILIN',
                                     'points': '4'},
                     'grid': 'G104',
                     'obs_name': 'ADPSFC',
                     'plots_list': 'time_series, lead_average'},
        'WindGust': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS'],
                     'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                     'fcst_var_dict': {'name': 'GUST',
                                       'levels': 'Z0',
                                       'threshs': 'NA'},
                     'obs_var_dict': {'name': 'GUST',
                                      'levels': 'Z0',
                                      'threshs': 'NA'},
                     'interp_dict': {'method': 'BILIN',
                                     'points': '4'},
                     'grid': 'G104',
                     'obs_name': 'ADPSFC',
                     'plots_list': 'time_series, lead_average'},
        'VectorWind10m': {'line_type_stat_list': ['VL1L2/RMSE', 'VL1L2/BIAS'],
                          'vx_mask_list': ['CONUS', 'CONUS_Central',
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
                          'fcst_var_dict': {'name': 'UGRD_VGRD',
                                            'levels': 'Z10',
                                             'threshs': 'NA'},
                          'obs_var_dict': {'name': 'UGRD_VGRD',
                                           'levels': 'Z10',
                                           'threshs': 'NA'},
                          'interp_dict': {'method': 'BILIN',
                                          'points': '4'},
                          'grid': 'G104',
                          'obs_name': 'ADPSFC',
                          'plots_list': 'time_series, lead_average'}
    }
}
njobs = 0
plot_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP, 'plot_job_scripts')
if not os.path.exists(plot_jobs_dir):
    os.makedirs(plot_jobs_dir)
for verif_type in VERIF_CASE_STEP_type_list:
    print("----> Making job scripts for "+VERIF_CASE_STEP+" "
          +verif_type)
    VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                   +verif_type)
    verif_type_plot_jobs_dict = plot_jobs_dict[verif_type]
    for verif_type_job in list(verif_type_plot_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, 'plot',
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        job_env_dict['model_list'] = "'"+os.environ['model_list']+"'"
        job_env_dict['model_plot_name_list'] = (
            "'"+os.environ[VERIF_CASE_STEP_abbrev+'_model_plot_name_list']+"'" 
        )
        job_env_dict['obs_name'] = (
            verif_type_plot_jobs_dict[verif_type_job]['obs_name']
        )
        job_env_dict['event_equalization'] = (
            os.environ[VERIF_CASE_STEP_abbrev+'_event_equalization']
        )
        job_env_dict['start_date'] = start_date
        job_env_dict['end_date'] = end_date
        job_env_dict['date_type'] = 'VALID'
        job_env_dict['plots_list'] = (
            "'"+verif_type_plot_jobs_dict[verif_type_job]\
            ['plots_list']+"'"
        )
        for data_name in ['fcst', 'obs']:
            job_env_dict[data_name+'_var_name'] =  (
                verif_type_plot_jobs_dict[verif_type_job]\
                [data_name+'_var_dict']['name']
            )
            job_env_dict[data_name+'_var_level_list'] =  ("'"+
                verif_type_plot_jobs_dict[verif_type_job]\
                [data_name+'_var_dict']['levels']
            +"'")
            job_env_dict[data_name+'_var_thresh_list'] =  ("'"+
                verif_type_plot_jobs_dict[verif_type_job]\
                [data_name+'_var_dict']['threshs']
            +"'")
        job_env_dict['interp_method'] = (
            verif_type_plot_jobs_dict[verif_type_job]\
            ['interp_dict']['method']
        )
        job_env_dict['interp_points_list'] = ("'"+
            verif_type_plot_jobs_dict[verif_type_job]\
            ['interp_dict']['points']
        +"'")
        job_env_dict['grid'] = (
            verif_type_plot_jobs_dict[verif_type_job]\
            ['grid']
        )
        for line_type_stat \
                in verif_type_plot_jobs_dict[verif_type_job]\
                ['line_type_stat_list']:
            job_env_dict['line_type'] = line_type_stat.split('/')[0]
            job_env_dict['stat'] = line_type_stat.split('/')[1]
            for vx_mask in verif_type_plot_jobs_dict[verif_type_job]\
                    ['vx_mask_list']:
                job_env_dict['vx_mask'] = vx_mask
                job_env_dict['job_name'] = (line_type_stat+'/'
                                            +verif_type_job+'/'
                                            +vx_mask)
                # Write job script
                njobs+=1
                # Create job file
                job_file = os.path.join(plot_jobs_dir, 'job'+str(njobs))
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
                job.write(
                    gda_util.python_command('global_det_atmos_plots.py',[])
                )
                job.close()

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(DATA, VERIF_CASE_STEP,
                                       'plot_job_scripts', 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("WARNING: No job files created in "
              +os.path.join(DATA, VERIF_CASE_STEP, 'plot_job_scripts'))
    poe_files = glob.glob(os.path.join(DATA, VERIF_CASE_STEP,
                                       'plot_job_scripts', 'poe*'))
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
        poe_filename = os.path.join(DATA, VERIF_CASE_STEP,
                                    'plot_job_scripts',
                                    'poe_jobs'+str(node))
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
                str(iproc-1)+' '
                +os.path.join(DATA, VERIF_CASE_STEP, 'plot_job_scripts',
                              job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(DATA, VERIF_CASE_STEP, 'plot_job_scripts',
                             job)+'\n'
            )
        poe_file.close()
        njob+=1
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(DATA, VERIF_CASE_STEP,
                                'plot_job_scripts',
                                'poe_jobs'+str(node))
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
