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
    'flux': {},
    'means': {
        'CAPESfcBased': {'line_type_stat_list': ['SL1L2/FBAR'],
                         'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                          'TROPICS', 'CONUS', 'N60N90',
                                          'S60S90', 'NAO', 'SAO',
                                          'NPO', 'SPO'],
                         'fcst_var_dict': {'name': 'CAPE',
                                           'levels': 'Z0',
                                           'threshs': 'NA'},
                         'obs_var_dict': {'name': 'CAPE',
                                          'levels': 'Z0',
                                          'threshs': 'NA'},
                         'interp_dict': {'method': 'NEAREST',
                                         'points': '1'},
                         'grid': 'G004',
                         'plots_list': 'time_series'},
        'CloudWater': {'line_type_stat_list': ['SL1L2/FBAR'],
                       'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                        'TROPICS', 'CONUS', 'N60N90',
                                        'S60S90', 'NAO', 'SAO',
                                        'NPO', 'SPO'],
                       'fcst_var_dict': {'name': 'CWAT',
                                         'levels': 'L0',
                                         'threshs': 'NA'},
                       'obs_var_dict': {'name': 'CWAT',
                                        'levels': 'L0',
                                        'threshs': 'NA'},
                       'interp_dict': {'method': 'NEAREST',
                                       'points': '1'},
                       'grid': 'G004',
                       'plots_list': 'time_series'},
        'GeoHeightTropopause': {'line_type_stat_list': ['SL1L2/FBAR'],
                                'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                                 'TROPICS', 'CONUS', 'N60N90',
                                                 'S60S90', 'NAO', 'SAO',
                                                 'NPO', 'SPO'],
                                'fcst_var_dict': {'name': 'HGT',
                                                  'levels': 'TROPOPAUSE',
                                                  'threshs': 'NA'},
                                'obs_var_dict': {'name': 'HGT',
                                                 'levels': 'TROPOPAUSE',
                                                 'threshs': 'NA'},
                                'interp_dict': {'method': 'NEAREST',
                                                'points': '1'},
                                'grid': 'G004',
                                'plots_list': 'time_series'},
        'PBLHeight': {'line_type_stat_list': ['SL1L2/FBAR'],
                      'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                       'TROPICS', 'CONUS', 'N60N90',
                                       'S60S90', 'NAO', 'SAO',
                                       'NPO', 'SPO'],
                      'fcst_var_dict': {'name': 'HPBL',
                                        'levels': 'L0',
                                        'threshs': 'NA'},
                      'obs_var_dict': {'name': 'HPBL',
                                       'levels': 'L0',
                                       'threshs': 'NA'},
                      'interp_dict': {'method': 'NEAREST',
                                      'points': '1'},
                      'grid': 'G004',
                      'plots_list': 'time_series'},
        'PrecipWater': {'line_type_stat_list': ['SL1L2/FBAR'],
                        'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                         'TROPICS', 'CONUS', 'N60N90',
                                         'S60S90', 'NAO', 'SAO',
                                         'NPO', 'SPO'],
                        'fcst_var_dict': {'name': 'PWAT',
                                          'levels': 'L0',
                                          'threshs': 'NA'},
                        'obs_var_dict': {'name': 'PWAT',
                                         'levels': 'L0',
                                         'threshs': 'NA'},
                        'interp_dict': {'method': 'NEAREST',
                                        'points': '1'},
                        'grid': 'G004',
                        'plots_list': 'time_series'},
        'PresSeaLevel': {'line_type_stat_list': ['SL1L2/FBAR'],
                         'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                          'TROPICS', 'CONUS', 'N60N90',
                                          'S60S90', 'NAO', 'SAO',
                                          'NPO', 'SPO'],
                         'fcst_var_dict': {'name': 'PRMSL',
                                           'levels': 'Z0',
                                           'threshs': 'NA'},
                         'obs_var_dict': {'name': 'PRMSL',
                                          'levels': 'Z0',
                                          'threshs': 'NA'},
                         'interp_dict': {'method': 'NEAREST',
                                         'points': '1'},
                         'grid': 'G004',
                         'plots_list': 'time_series'},
        'PresSfc': {'line_type_stat_list': ['SL1L2/FBAR'],
                    'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                     'TROPICS', 'CONUS', 'N60N90',
                                     'S60S90', 'NAO', 'SAO',
                                     'NPO', 'SPO'],
                    'fcst_var_dict': {'name': 'PRES',
                                      'levels': 'Z0',
                                      'threshs': 'NA'},
                    'obs_var_dict': {'name': 'PRES',
                                     'levels': 'Z0',
                                     'threshs': 'NA'},
                    'interp_dict': {'method': 'NEAREST',
                                    'points': '1'},
                    'grid': 'G004',
                    'plots_list': 'time_series'},
        'PresTropopause': {'line_type_stat_list': ['SL1L2/FBAR'],
                           'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                            'TROPICS', 'CONUS', 'N60N90',
                                            'S60S90', 'NAO', 'SAO',
                                            'NPO', 'SPO'],
                           'fcst_var_dict': {'name': 'PRES',
                                             'levels': 'TROPOPAUSE',
                                             'threshs': 'NA'},
                           'obs_var_dict': {'name': 'PRES',
                                            'levels': 'TROPOPAUSE',
                                            'threshs': 'NA'},
                           'interp_dict': {'method': 'NEAREST',
                                           'points': '1'},
                           'grid': 'G004',
                           'plots_list': 'time_series'},
        'RelHum2m': {'line_type_stat_list': ['SL1L2/FBAR'],
                     'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                      'TROPICS', 'CONUS', 'N60N90',
                                      'S60S90', 'NAO', 'SAO',
                                      'NPO', 'SPO'],
                     'fcst_var_dict': {'name': 'RH',
                                       'levels': 'Z2',
                                       'threshs': 'NA'},
                     'obs_var_dict': {'name': 'RH',
                                      'levels': 'Z2',
                                      'threshs': 'NA'},
                     'interp_dict': {'method': 'NEAREST',
                                     'points': '1'},
                     'grid': 'G004',
                     'plots_list': 'time_series'},
        'SnowWaterEqv': {'line_type_stat_list': ['SL1L2/FBAR'],
                         'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                          'TROPICS', 'CONUS', 'N60N90',
                                          'S60S90', 'NAO', 'SAO',
                                          'NPO', 'SPO'],
                         'fcst_var_dict': {'name': 'WEASD',
                                           'levels': 'Z0',
                                           'threshs': 'NA'},
                         'obs_var_dict': {'name': 'WEASD',
                                          'levels': 'Z0',
                                          'threshs': 'NA'},
                         'interp_dict': {'method': 'NEAREST',
                                         'points': '1'},
                         'grid': 'G004',
                         'plots_list': 'time_series'},
        'SpefHum2m': {'line_type_stat_list': ['SL1L2/FBAR'],
                      'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                       'TROPICS', 'CONUS', 'N60N90',
                                       'S60S90', 'NAO', 'SAO',
                                       'NPO', 'SPO'],
                      'fcst_var_dict': {'name': 'SPFH',
                                        'levels': 'Z2',
                                        'threshs': 'NA'},
                      'obs_var_dict': {'name': 'SPFH',
                                       'levels': 'Z2',
                                       'threshs': 'NA'},
                      'interp_dict': {'method': 'NEAREST',
                                      'points': '1'},
                      'grid': 'G004',
                      'plots_list': 'time_series'},
        'Temp2m': {'line_type_stat_list': ['SL1L2/FBAR'],
                   'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                    'TROPICS', 'CONUS', 'N60N90',
                                    'S60S90', 'NAO', 'SAO',
                                    'NPO', 'SPO'],
                   'fcst_var_dict': {'name': 'TMP',
                                     'levels': 'Z2',
                                     'threshs': 'NA'},
                   'obs_var_dict': {'name': 'TMP',
                                    'levels': 'Z2',
                                    'threshs': 'NA'},
                   'interp_dict': {'method': 'NEAREST',
                                   'points': '1'},
                   'grid': 'G004',
                   'plots_list': 'time_series'},
        'TempTropopause': {'line_type_stat_list': ['SL1L2/FBAR'],
                           'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                            'TROPICS', 'CONUS', 'N60N90',
                                            'S60S90', 'NAO', 'SAO',
                                            'NPO', 'SPO'],
                           'fcst_var_dict': {'name': 'TMP',
                                             'levels': 'TROPOPAUSE',
                                             'threshs': 'NA'},
                           'obs_var_dict': {'name': 'TMP',
                                            'levels': 'TROPOPAUSE',
                                            'threshs': 'NA'},
                           'interp_dict': {'method': 'NEAREST',
                                           'points': '1'},
                           'grid': 'G004',
                           'plots_list': 'time_series'},
        'TempSoilTopLayer': {'line_type_stat_list': ['SL1L2/FBAR'],
                             'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                              'TROPICS', 'CONUS', 'N60N90',
                                              'S60S90', 'NAO', 'SAO',
                                              'NPO', 'SPO'],
                             'fcst_var_dict': {'name': 'TSOIL',
                                               'levels': 'Z0.1-0',
                                               'threshs': 'NA'},
                             'obs_var_dict': {'name': 'TSOIL',
                                              'levels': 'Z0.1-0',
                                              'threshs': 'NA'},
                             'interp_dict': {'method': 'NEAREST',
                                             'points': '1'},
                             'grid': 'G004',
                             'plots_list': 'time_series'},
        'TotalOzone': {'line_type_stat_list': ['SL1L2/FBAR'],
                       'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                        'TROPICS', 'CONUS', 'N60N90',
                                        'S60S90', 'NAO', 'SAO',
                                        'NPO', 'SPO'],
                       'fcst_var_dict': {'name': 'TOZNE',
                                         'levels': 'L0',
                                         'threshs': 'NA'},
                       'obs_var_dict': {'name': 'TOZNE',
                                        'levels': 'L0',
                                        'threshs': 'NA'},
                       'interp_dict': {'method': 'NEAREST',
                                       'points': '1'},
                       'grid': 'G004',
                       'plots_list': 'time_series'},
        'UWind10m': {'line_type_stat_list': ['SL1L2/FBAR'],
                     'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                      'TROPICS', 'CONUS', 'N60N90',
                                      'S60S90', 'NAO', 'SAO',
                                      'NPO', 'SPO'],
                     'fcst_var_dict': {'name': 'UGRD',
                                       'levels': 'Z10',
                                       'threshs': 'NA'},
                     'obs_var_dict': {'name': 'UGRD',
                                      'levels': 'Z10',
                                      'threshs': 'NA'},
                     'interp_dict': {'method': 'NEAREST',
                                     'points': '1'},
                     'grid': 'G004',
                     'plots_list': 'time_series'},
        'VolSoilMoistTopLayer': {'line_type_stat_list': ['SL1L2/FBAR'],
                                 'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                                  'TROPICS', 'CONUS', 'N60N90',
                                                  'S60S90', 'NAO', 'SAO',
                                                  'NPO', 'SPO'],
                                 'fcst_var_dict': {'name': 'SOILW',
                                                   'levels': 'Z0.1-0',
                                                   'threshs': 'NA'},
                                 'obs_var_dict': {'name': 'SOILW',
                                                  'levels': 'Z0.1-0',
                                                  'threshs': 'NA'},
                                 'interp_dict': {'method': 'NEAREST',
                                                 'points': '1'},
                                 'grid': 'G004',
                                 'plots_list': 'time_series'},
        'VWind10m': {'line_type_stat_list': ['SL1L2/FBAR'],
                     'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                      'TROPICS', 'CONUS', 'N60N90',
                                      'S60S90', 'NAO', 'SAO',
                                      'NPO', 'SPO'],
                     'fcst_var_dict': {'name': 'VGRD',
                                       'levels': 'Z10',
                                       'threshs': 'NA'},
                     'obs_var_dict': {'name': 'VGRD',
                                      'levels': 'Z10',
                                      'threshs': 'NA'},
                     'interp_dict': {'method': 'NEAREST',
                                     'points': '1'},
                     'grid': 'G004',
                     'plots_list': 'time_series'},
    },
    'ozone': {},
    'precip': {
        '24hrCCPA': {'line_type_stat_list': ['CTC/ETS', 'CTC/FBIAS',
                                             'CTC/FY_OY'],
                     'vx_mask_list': ['CONUS', 'CONUS_East',
                                      'CONUS_West', 'CONUS_Central',
                                      'CONUS_South'],
                     'fcst_var_dict': {'name': 'APCP_A24',
                                       'levels': 'A24',
                                       'threshs': ('ge0.1, ge0.5, ge1, ge5, '
                                                   +'ge10, ge25, ge50, ge75, '
                                                   +'ge0.254, ge2.54, ge6.35, '
                                                   +'ge12.7, ge25.4, ge50.8, '
                                                   +'ge76.2, ge101.6')},
                     'obs_var_dict': {'name': 'APCP_A24',
                                     'levels': 'A24',
                                     'threshs': ('ge0.1, ge0.5, ge1, ge5, '
                                                 +'ge10, ge25, ge50, ge75, '
                                                 +'ge0.254, ge2.54, ge6.35, '
                                                 +'ge12.7, ge25.4, ge50.8, '
                                                 +'ge76.2, ge101.6')},
                     'interp_dict': {'method': 'NEAREST',
                                     'points': '1'},
                     'grid': 'G211',
                     'obs_name': '24hrCCPA',
                     'plots_list': 'time_series, lead_average'},
        '24hrCCPA_Nbrhd': {'line_type_stat_list': ['NBRCNT/FSS'],
                           'vx_mask_list': ['CONUS', 'CONUS_East',
                                            'CONUS_West', 'CONUS_Central',
                                            'CONUS_South'],
                           'fcst_var_dict': {'name': 'APCP_A24',
                                             'levels': 'A24',
                                             'threshs': ('ge0.1, ge0.5, ge1, '
                                                         +'ge5, ge10, ge25, '
                                                         +'ge50, ge75, '
                                                         +'ge0.254, ge2.54, '
                                                         +'ge6.35, ge12.7, '
                                                         +'ge25.4, ge50.8, '
                                                         +'ge76.2, ge101.6')},
                           'obs_var_dict': {'name': 'APCP_A24',
                                            'levels': 'A24',
                                            'threshs': ('ge0.1, ge0.5, ge1, '
                                                        +'ge5, ge10, ge25, '
                                                        +'ge50, ge75, '
                                                        +'ge0.254, ge2.54, '
                                                        +'ge6.35, ge12.7, '
                                                        +'ge25.4, ge50.8, '
                                                        +'ge76.2, ge101.6')},
                          'interp_dict': {'method': 'NBRHD_SQUARE',
                                          'points': ('1, 169, 529, 1089, '
                                                     +'1849, 2809, 3969')},
                          'grid': 'G240',
                          'obs_name': '24hrCCPA',
                          'plots_list': 'time_series, lead_average'},
        '24hrCCPAPerfDia': {'line_type_stat_list': ['CTC/PERF_DIA'],
                            'vx_mask_list': ['CONUS', 'CONUS_East',
                                             'CONUS_West', 'CONUS_Central',
                                             'CONUS_South'],
                            'fcst_var_dict': {'name': 'APCP_A24',
                                              'levels': 'A24',
                                              'threshs': ('ge0.1, ge0.5, '
                                                          +'ge1, ge5, '
                                                          +'ge10, ge25, '
                                                          +'ge50, ge75')},
                            'obs_var_dict': {'name': 'APCP_A24',
                                             'levels': 'A24',
                                             'threshs': ('ge0.1, ge0.5, '
                                                         +'ge1, ge5, '
                                                         +'ge10, ge25, '
                                                         +'ge50, ge75')},
                            'interp_dict': {'method': 'NEAREST',
                                            'points': '1'},
                            'grid': 'G211',
                            'obs_name': '24hrCCPA',
                            'plots_list': 'performance_diagram'},
        '24hrAccumMaps': {'line_type_stat_list': ['SL1L2/FBAR'],
                          'vx_mask_list': ['CONUS', 'AK', 'PR', 'HI'],
                          'fcst_var_dict': {'name': 'APCP_A24',
                                            'levels': 'A24',
                                            'threshs': 'NA'},
                          'obs_var_dict': {'name': 'APCP_A24',
                                           'levels': 'A24',
                                           'threshs': 'NA'},
                          'interp_dict': {'method': 'NEAREST',
                                          'points': '1'},
                          'grid': 'G211',
                          'obs_name': '24hrCCPA',
                          'plots_list': 'precip_spatial_map'}
    },
    'pres_levs': {
        'GeoHeight': {'line_type_stat_list': ['SAL1L2/ACC', 'GRAD/S1'],
                      'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                       'TROPICS'],
                      'fcst_var_dict': {'name': 'HGT',
                                        'levels': 'P1000, P700, P500, P250',
                                        'threshs': 'NA'},
                      'obs_var_dict': {'name': 'HGT',
                                      'levels': 'P1000, P700, P500, P250',
                                      'threshs': 'NA'},
                      'interp_dict': {'method': 'NEAREST',
                                      'points': '1'},
                      'grid': 'G004',
                      'plots_list': 'time_series, lead_average, lead_by_date'},
        'GeoHeight_FourierDecom0-20': {'line_type_stat_list': ['SAL1L2/ACC'],
                                       'vx_mask_list': ['GLOBAL', 'NHEM',
                                                        'SHEM', 'TROPICS'],
                                       'fcst_var_dict': {'name': 'HGT_DECOMP',
                                                         'levels': 'P500',
                                                         'threshs': 'NA'},
                                       'obs_var_dict': {'name': 'HGT_DECOMP',
                                                        'levels': 'P500',
                                                        'threshs': 'NA'},
                                       'interp_dict': {'method': 'WV1_0-20',
                                                       'points': 'NA'},
                                       'grid': 'G004',
                                       'plots_list': ('time_series, '
                                                      +'lead_average, '
                                                      +'lead_by_date')},
        'GeoHeight_FourierDecom0-3': {'line_type_stat_list': ['SAL1L2/ACC'],
                                      'vx_mask_list': ['GLOBAL', 'NHEM',
                                                       'SHEM', 'TROPICS'],
                                      'fcst_var_dict': {'name': 'HGT_DECOMP',
                                                        'levels': 'P500',
                                                        'threshs': 'NA'},
                                      'obs_var_dict': {'name': 'HGT_DECOMP',
                                                       'levels': 'P500',
                                                       'threshs': 'NA'},
                                      'interp_dict': {'method': 'WV1_0-3',
                                                      'points': 'NA'},
                                      'grid': 'G004',
                                      'plots_list': ('time_series, '
                                                     +'lead_average, '
                                                     +'lead_by_date')},
        'GeoHeight_FourierDecom4-9': {'line_type_stat_list': ['SAL1L2/ACC'],
                                      'vx_mask_list': ['GLOBAL', 'NHEM',
                                                       'SHEM', 'TROPICS'],
                                      'fcst_var_dict': {'name': 'HGT_DECOMP',
                                                        'levels': 'P500',
                                                        'threshs': 'NA'},
                                      'obs_var_dict': {'name': 'HGT_DECOMP',
                                                       'levels': 'P500',
                                                       'threshs': 'NA'},
                                      'interp_dict': {'method': 'WV1_4-9',
                                                      'points': 'NA'},
                                      'grid': 'G004',
                                      'plots_list': ('time_series, '
                                                     +'lead_average, '
                                                     +'lead_by_date')},
        'GeoHeight_FourierDecom10-20': {'line_type_stat_list': ['SAL1L2/ACC'],
                                        'vx_mask_list': ['GLOBAL', 'NHEM',
                                                         'SHEM', 'TROPICS'],
                                        'fcst_var_dict': {'name': 'HGT_DECOMP',
                                                          'levels': 'P500',
                                                          'threshs': 'NA'},
                                        'obs_var_dict': {'name': 'HGT_DECOMP',
                                                         'levels': 'P500',
                                                         'threshs': 'NA'},
                                        'interp_dict': {'method': 'WV1_10-20',
                                                        'points': 'NA'},
                                        'grid': 'G004',
                                        'plots_list': ('time_series, '
                                                       +'lead_average, '
                                                       +'lead_by_date')},
        'DailyAvg_GeoHeightAnom': {'line_type_stat_list': ['SL1L2/BIAS',
                                                           'SL1L2/RMSE'],
                                   'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                                    'TROPICS'],
                                   'fcst_var_dict': {'name': 'HGT_ANOM_DAILYAVG',
                                                     'levels': 'P500',
                                                     'threshs': 'NA'},
                                   'obs_var_dict': {'name': 'HGT_ANOM_DAILYAVG',
                                                    'levels': 'P500',
                                                    'threshs': 'NA'},
                                   'interp_dict': {'method': 'NEAREST',
                                                   'points': '1'},
                                   'grid': 'G004',
                                   'plots_list': 'time_series, lead_average'},
        'Ozone': {'line_type_stat_list': ['SL1L2/BIAS', 'SL1L2/RMSE'],
                  'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                   'TROPICS'],
                  'fcst_var_dict': {'name': 'O3MR',
                                    'levels': ('P100, P70, P50, P30, '
                                               +'P20, P10, P5, P1'),
                                    'threshs': 'NA'},
                  'obs_var_dict': {'name': 'O3MR',
                                   'levels': ('P100, P70, P50, P30, '
                                              +'P20, P10, P5, P1'),
                                   'threshs': 'NA'},
                  'interp_dict': {'method': 'NEAREST',
                                  'points': '1'},
                  'grid': 'G004',
                  'plots_list': ('time_series, lead_average, '
                                 +'stat_by_level, lead_by_level')},
        'PresSeaLevel': {'line_type_stat_list': ['SAL1L2/ACC', 'SL1L2/BIAS',
                                                 'SL1L2/RMSE', 'GRAD/S1'],
                         'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                          'TROPICS'],
                         'fcst_var_dict': {'name': 'PRMSL',
                                           'levels': 'Z0',
                                           'threshs': 'NA'},
                         'obs_var_dict': {'name': 'PRMSL',
                                          'levels': 'Z0',
                                          'threshs': 'NA'},
                         'interp_dict': {'method': 'NEAREST',
                                         'points': '1'},
                         'grid': 'G004',
                         'plots_list': ('time_series, lead_average, '
                                        +'lead_by_date')},
        'Temp': {'line_type_stat_list': ['SAL1L2/ACC'],
                 'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                  'TROPICS'],
                 'fcst_var_dict': {'name': 'TMP',
                                   'levels': 'P850, P500, P250',
                                   'threshs': 'NA'},
                 'obs_var_dict': {'name': 'TMP',
                                  'levels': 'P850, P500, P250',
                                  'threshs': 'NA'},
                 'interp_dict': {'method': 'NEAREST',
                                 'points': '1'},
                 'grid': 'G004',
                 'plots_list': 'time_series, lead_average, lead_by_date'},
        'UWind': {'line_type_stat_list': ['SAL1L2/ACC'],
                  'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                   'TROPICS'],
                  'fcst_var_dict': {'name': 'UGRD',
                                    'levels': 'P850, P500, P250',
                                    'threshs': 'NA'},
                  'obs_var_dict': {'name': 'UGRD',
                                   'levels': 'P850, P500, P250',
                                   'threshs': 'NA'},
                  'interp_dict': {'method': 'NEAREST',
                                  'points': '1'},
                  'grid': 'G004',
                  'plots_list': 'time_series, lead_average, lead_by_date'},
        'VWind': {'line_type_stat_list': ['SAL1L2/ACC'],
                  'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                   'TROPICS'],
                  'fcst_var_dict': {'name': 'VGRD',
                                    'levels': 'P850, P500, P250',
                                    'threshs': 'NA'},
                  'obs_var_dict': {'name': 'VGRD',
                                   'levels': 'P850, P500, P250',
                                   'threshs': 'NA'},
                  'interp_dict': {'method': 'NEAREST',
                                  'points': '1'},
                  'grid': 'G004',
                  'plots_list': 'time_series, lead_average, lead_by_date'},
        'VectorWind': {'line_type_stat_list': ['VAL1L2/ACC'],
                       'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                        'TROPICS'],
                       'fcst_var_dict': {'name': 'UGRD_VGRD',
                                         'levels': 'P850, P500, P250',
                                         'threshs': 'NA'},
                       'obs_var_dict': {'name': 'UGRD_VGRD',
                                        'levels': 'P850, P500, P250',
                                        'threshs': 'NA'},
                       'interp_dict': {'method': 'NEAREST',
                                       'points': '1'},
                       'grid': 'G004',
                       'plots_list': 'time_series, lead_average, lead_by_date'},
        'WindShear': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS'],
                      'vx_mask_list': ['ATL_MDR', 'EPAC_MDR'],
                      'fcst_var_dict': {'name': 'WNDSHR',
                                        'levels': 'P850-P200',
                                        'threshs': 'NA'},
                      'obs_var_dict': {'name': 'WNDSHR',
                                       'levels': 'P850-P200',
                                       'threshs': 'NA'},
                      'interp_dict': {'method': 'NEAREST',
                                      'points': '1'},
                      'grid': 'G004',
                      'plots_list': 'time_series, lead_average'},
    },
    'sea_ice': {
        'DailyAvg_Concentration': {'line_type_stat_list': ['SL1L2/RMSE',
                                                           'SL1L2/BIAS'],
                                   'vx_mask_list': ['ARCTIC', 'ANTARCTIC'],
                                   'fcst_var_dict': {'name': 'ICEC_DAILYAVG',
                                                     'levels': 'Z0',
                                                     'threshs': ''},
                                   'obs_var_dict': {'name': 'ice_conc',
                                                    'levels': "'*,*'",
                                                    'threshs': ''},
                                   'interp_dict': {'method': 'NEAREST',
                                                   'points': '1'},
                                   'grid': 'G004',
                                   'obs_name': 'osi_saf',
                                   'plots_list': 'time_series, lead_average'}, 
        'DailyAvg_Concentration_Thresh': {'line_type_stat_list': ['CTC/CSI'],
                                          'vx_mask_list': ['ARCTIC',
                                                           'ANTARCTIC'],
                                          'fcst_var_dict': {'name': (
                                                                'ICEC_DAILYAVG'
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
                                          'grid': 'G004',
                                          'obs_name': 'osi_saf',
                                          'plots_list': ('time_series, '
                                                         +'lead_average')},
        'DailyAvg_Concentration_PerfDia': {'line_type_stat_list': \
                                               ['CTC/PERF_DIA'],
                                           'vx_mask_list': \
                                               ['ARCTIC', 'ANTARCTIC'],
                                           'fcst_var_dict': \
                                               {'name': 'ICEC_DAILYAVG',
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
                                           'grid': 'G004',
                                           'obs_name': 'osi_saf',
                                           'plots_list': 'performance_diagram'},
    },
    'snow': {
        '24hrNOHRSC_Depth': {'line_type_stat_list': ['CTC/ETS', 'CTC/FBIAS'],
                             'vx_mask_list': ['CONUS', 'CONUS_East',
                                              'CONUS_West', 'CONUS_Central',
                                              'CONUS_South'],
                             'fcst_var_dict': {'name': 'SNOD_A24',
                                               'levels': 'Z0',
                                               'threshs': ('ge0.0254, '
                                                           +'ge0.0508, '
                                                           +'ge0.1016, '
                                                           +'ge0.2032, '
                                                           +'ge0.3048')},
                             'obs_var_dict': {'name': 'ASNOW',
                                              'levels': 'A24',
                                              'threshs': ('ge0.0254, '
                                                          +'ge0.0508, '
                                                          +'ge0.1016, '
                                                          +'ge0.2032, '
                                                          +'ge0.3048')},
                             'interp_dict': {'method': 'NEAREST',
                                             'points': '1'},
                             'grid': 'G211',
                             'obs_name': '24hrNOHRSC',
                             'plots_list': 'time_series, lead_average'},
        '24hrNOHRSC_WaterEqv': {'line_type_stat_list': ['CTC/ETS', 'CTC/FBIAS'],
                                'vx_mask_list': ['CONUS', 'CONUS_East',
                                                 'CONUS_West', 'CONUS_Central',
                                                 'CONUS_South'],
                                'fcst_var_dict': {'name': 'WEASD_A24',
                                                  'levels': 'Z0',
                                                  'threshs': ('ge0.0254, '
                                                              +'ge0.0508, '
                                                              +'ge0.1016, '
                                                              +'ge0.2032, '
                                                              +'ge0.3048')},
                                'obs_var_dict': {'name': 'ASNOW',
                                                 'levels': 'A24',
                                                 'threshs': ('ge0.0254, '
                                                             +'ge0.0508, '
                                                             +'ge0.1016, '
                                                             +'ge0.2032, '
                                                             +'ge0.3048')},
                                'interp_dict': {'method': 'NEAREST',
                                                'points': '1'},
                                'grid': 'G211',
                                'obs_name': '24hrNOHRSC',
                                'plots_list': 'time_series, lead_average'},
        '24hrNOHRSC_Depth_Nbrhd': {'line_type_stat_list': ['NBRCNT/FSS'],
                                   'vx_mask_list': ['CONUS', 'CONUS_East',
                                                    'CONUS_West',
                                                    'CONUS_Central',
                                                    'CONUS_South'],
                                   'fcst_var_dict': {'name': 'SNOD_A24',
                                                     'levels': 'Z0',
                                                     'threshs': ('ge0.0254, '
                                                                 +'ge0.0508, '
                                                                 +'ge0.1016, '
                                                                 +'ge0.2032, '
                                                                 +'ge0.3048')},
                                   'obs_var_dict': {'name': 'ASNOW',
                                                    'levels': 'A24',
                                                    'threshs': ('ge0.0254, '
                                                                +'ge0.0508, '
                                                                +'ge0.1016, '
                                                                +'ge0.2032, '
                                                                +'ge0.3048')},
                                   'interp_dict': {'method': 'NBRHD_SQUARE',
                                                   'points': ('1, 169, '
                                                              +'529, 1089, '
                                                              +'1849, 2809, '
                                                              +'3969')},
                                   'grid': 'G240',
                                   'obs_name': '24hrNOHRSC',
                                   'plots_list': 'time_series, lead_average'},
        '24hrNOHRSC_WaterEqv_Nbrhd': {'line_type_stat_list': ['NBRCNT/FSS'],
                                      'vx_mask_list': ['CONUS', 'CONUS_East',
                                                       'CONUS_West',
                                                       'CONUS_Central',
                                                       'CONUS_South'],
                                      'fcst_var_dict': {'name': 'WEASD_A24',
                                                        'levels': 'Z0',
                                                        'threshs': ('ge0.0254, '
                                                                    +'ge0.0508, '
                                                                    +'ge0.1016, '
                                                                    +'ge0.2032, '
                                                                    +'ge0.3048')},
                                      'obs_var_dict': {'name': 'ASNOW',
                                                       'levels': 'A24',
                                                       'threshs': ('ge0.0254, '
                                                                   +'ge0.0508, '
                                                                   +'ge0.1016, '
                                                                   +'ge0.2032, '
                                                                   +'ge0.3048')},
                                      'interp_dict': {'method': 'NBRHD_SQUARE',
                                                      'points': ('1, 169, '
                                                                 +'529, 1089, '
                                                                 +'1849, 2809, '
                                                                 +'3969')},
                                      'grid': 'G240',
                                      'obs_name': '24hrNOHRSC',
                                      'plots_list': 'time_series, lead_average'},
    },
    'sst': {
        'DailyAvg_SST': {'line_type_stat_list': ['SL1L2/RMSE', 'SL1L2/BIAS'],
                         'vx_mask_list': ['GLOBAL', 'NHEM', 'SHEM',
                                          'TROPICS'],
                         'fcst_var_dict': {'name': 'SST_DAILYAVG',
                                           'levels': 'Z0',
                                           'threshs': 'NA'},
                         'obs_var_dict': {'name': 'analysed_sst',
                                          'levels': "'0,*,*'",
                                          'threshs': 'NA'},
                         'interp_dict': {'method': 'NEAREST',
                                         'points': '1'},
                         'grid': 'G004',
                         'obs_name': 'ghrsst_median',
                         'plots_list': 'time_series, lead_average'},
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
        if verif_type == 'pres_levs':
            job_env_dict['truth_name_list'] =  "'"+os.environ[
                VERIF_CASE_STEP_abbrev_type+'_truth_name_list'
            ]+"'"
        elif verif_type == 'means':
            job_env_dict['obs_name'] = "'"+os.environ['model_list']+"'"
        else:
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
        job_env_dict['grid'] = (
            verif_type_plot_jobs_dict[verif_type_job]['grid']
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
