#!/usr/bin/env python3
'''
Program Name: global_det_atmos_stats_grid2grid_create_job_scripts.py
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
#### reformat_data jobs
################################################
reformat_data_obs_jobs_dict = {
    'flux': {},
    'means': {},
    'ozone': {},
    'precip_accum24hr': {},
    'precip_accum3hr': {},
    'pres_levs': {},
    'sea_ice': {},
    'snow': {},
    'sst': {},
}
reformat_data_model_jobs_dict = {
    'flux': {},
    'means': {},
    'ozone': {},
    'precip_accum24hr': {},
    'precip_accum3hr': {},
    'pres_levs': {
        'GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                  'var1_levels': 'P500',
                                  'met_config_overrides': (
                                      "'climo_mean = fcst;'"
                                  )},
                          'commands': [gda_util.metplus_command(
                                           'GridStat_fcstGLOBAL_DET_'
                                            +'obsModelAnalysis_climoERA5_'
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
                                                'grid_stat_${VERIF_TYPE}_'
                                                +'${job_name}_'
                                                +'{lead?fmt=%2H}0000L_'
                                                +'{valid?fmt=%Y%m%d}_'
                                                +'{valid?fmt=%H}0000V_pairs.nc'
                                             )]
                                       )]},
        'WindShear': {'env': {'var1_name': 'UGRD',
                              'var1_levels': '"P850, P200"',
                              'var2_name': 'VGRD',
                              'var2_levels': '"P850, P200"',
                              'met_config_overrides': ''},
                      'commands': [gda_util.metplus_command(
                                       'GridStat_fcstGLOBAL_DET_'
                                       +'obsModelAnalysis_WindsNetCDF.conf'
                                   ),
                                   gda_util.python_command(
                                       'global_det_atmos_stats_grid2grid_'
                                       +'create_wind_shear.py',
                                       [os.path.join(
                                            '$DATA', '${VERIF_CASE}_${STEP}',
                                            'METplus_output',
                                            '${RUN}.{valid?fmt=%Y%m%d}',
                                            '$MODEL', '$VERIF_CASE',
                                            'grid_stat_${VERIF_TYPE}_'
                                            +'${job_name}_'
                                            +'{lead?fmt=%2H}0000L_'
                                            +'{valid?fmt=%Y%m%d}_'
                                            +'{valid?fmt=%H}0000V_pairs.nc'
                                        )]
                                   )]}
    },
    'sea_ice': {
        'Concentration': {'env': {'var1_name': 'ICEC',
                                  'var1_levels': 'Z0',},
                          'commands': [gda_util.metplus_command(
                                           'GridStat_fcstGLOBAL_DET_'
                                            +'NetCDF.conf'
                                       )]},
    },
    'snow': {},
    'sst': {
        'SST': {'env': {'var1_name': 'TMP',
                        'var1_levels': 'Z0'},
                'commands': [gda_util.metplus_command(
                                 'GridStat_fcstGLOBAL_DET_'
                                 +'NetCDF.conf'
                             )]}
    },
}
################################################
#### assemble_data jobs
################################################
assemble_data_obs_jobs_dict = {
    'flux': {},
    'means': {},
    'ozone': {},
    'precip_accum24hr': {
        '24hrCCPA': {'env': {},
                     'commands': [gda_util.metplus_command(
                                      'PCPCombine_obs24hrCCPA.conf'
                                  )]}
    },
    'precip_accum3hr': {},
    'pres_levs': {},
    'sea_ice': {},
    'snow': {},
    'sst': {},
}
assemble_data_model_jobs_dict = {
    'flux': {},
    'means': {},
    'ozone': {},
    'precip_accum24hr': {
        '24hrAccum': {'env': {'accum': '24'},
                      'commands': [gda_util.metplus_command(
                                       'PCPCombine_fcstGLOBAL_DET_precip.conf'
                                   )]}
    },
    'precip_accum3hr': {
        '3hrAccum': {'env': {'accum': '3'},
                      'commands': [gda_util.metplus_command(
                                       'PCPCombine_fcstGLOBAL_DET_precip.conf'
                                   )]}
    },
    'pres_levs': {
        'DailyAvg_GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                           'var1_levels': 'P500',},
                                   'commands': [gda_util.python_command(
                                                    'global_det_atmos_'
                                                    +'stats_grid2grid'
                                                    +'_create_daily_avg.py',
                                                    ['HGT_ANOM_P500',
                                                     os.path.join(
                                                         '$DATA',
                                                         '${VERIF_CASE}_'
                                                         +'${STEP}',
                                                         'METplus_output',
                                                         '${RUN}.'
                                                         +'{valid?fmt=%Y%m%d}',
                                                         '$MODEL',
                                                         '$VERIF_CASE',
                                                         'anomaly_'
                                                         +'${VERIF_TYPE}_'
                                                         +'GeoHeightAnom_init'
                                                         +'{init?fmt=%Y%m%d%H}_'
                                                         +'fhr{lead?fmt=%3H}.nc'
                                                     ),
                                                     os.path.join(
                                                         '$COMIN', 'stats',
                                                         '$COMPONENT',
                                                         '${RUN}.'
                                                         +'{valid?fmt=%Y%m%d}',
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
    'sea_ice': {
        'DailyAvg_Concentration': {'env': {'var1_name': 'ICEC',
                                           'var1_levels': 'Z0',},
                                   'commands': [gda_util.python_command(
                                                    'global_det_atmos_stats_'
                                                    +'grid2grid_create_'
                                                    +'daily_avg.py',
                                                    ['ICEC_Z0',
                                                     os.path.join(
                                                         '$DATA',
                                                         '${VERIF_CASE}_'
                                                         +'${STEP}',
                                                         'METplus_output',
                                                         '${RUN}.'
                                                         +'{valid?fmt=%Y%m%d}',
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
                                                         '$COMIN', 'stats',
                                                         '$COMPONENT',
                                                         '${RUN}.'
                                                         +'{valid?fmt=%Y%m%d}',
                                                         '$MODEL',
                                                         '$VERIF_CASE',
                                                         'grid_stat_'
                                                         +'${VERIF_TYPE}_'
                                                         +'Concentration_'
                                                         +'{lead?fmt=%2H}0000L_'
                                                         +'{valid?fmt=%Y%m%d}_'
                                                         +'{valid?fmt=%H}0000V_'
                                                         +'pairs.nc'
                                                     )])]},
    },
    'snow': {
        '24hrAccum_WaterEqv': {'env': {'MODEL_var': 'WEASD'},
                               'commands': [gda_util.metplus_command(
                                                'PCPCombine_fcstGLOBAL_'
                                                +'DET_24hrAccum_snow.conf'
                                            )]}, 
        '24hrAccum_Depth': {'env': {'MODEL_var': 'SNOD'},
                            'commands': [gda_util.metplus_command(
                                             'PCPCombine_fcstGLOBAL_'
                                             +'DET_24hrAccum_snow.conf'
                                         )]}
    },
    'sst': {
        'DailyAvg_SST': {'env': {'var1_name': 'TMP',
                                 'var1_levels': 'Z0'},
                         'commands': [gda_util.python_command(
                                          'global_det_atmos_'
                                          +'stats_grid2grid'
                                          +'_create_daily_avg.py',
                                          ['TMP_Z0',
                                           os.path.join(
                                              '$DATA',
                                              '${VERIF_CASE}_${STEP}',
                                              'METplus_output',
                                              '${RUN}.{valid?fmt=%Y%m%d}',
                                              '$MODEL', '$VERIF_CASE',
                                              'grid_stat_${VERIF_TYPE}_SST_'
                                              +'{lead?fmt=%2H}0000L_'
                                              +'{valid?fmt=%Y%m%d}_'
                                              +'{valid?fmt=%H}0000V_pairs.nc'
                                          ),
                                          os.path.join(
                                               '$COMIN', 'stats',
                                               '$COMPONENT',
                                               '${RUN}.{valid?fmt=%Y%m%d}',
                                               '$MODEL', '$VERIF_CASE',
                                               'grid_stat_${VERIF_TYPE}_SST_'
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
    'flux': {},
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
                                                         +'"TROPOPAUSE";'+"'")},
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
                                 'var1_options': ("'set_attr_units = "
                                                  +'"hPa"; convert(p)='
                                                  +'PA_to_HPA(p)'
                                                  +"'")},
                         'commands': [gda_util.metplus_command(
                                          'GridStat_fcstGLOBAL_DET.conf'
                                      )]},
        'PresSfc': {'env': {'var1_name': 'PRES',
                            'var1_level': 'Z0',
                            'var1_options': ("'set_attr_units = "
                                             +'"hPa"; convert(p)=PA_to_HPA(p)'
                                             +"'")},
                    'commands': [gda_util.metplus_command(
                                     'GridStat_fcstGLOBAL_DET.conf'
                                 )]},
        'PresTropopause': {'env': {'var1_name': 'PRES',
                                   'var1_level': 'L0',
                                   'var1_options': ("'GRIB_lvl_typ = 7; "
                                                    +'set_attr_level = '
                                                    +'"TROPOPAUSE";'
                                                    +'set_attr_units = "hPa"; '
                                                    +'convert(p)=PA_to_HPA(p)'
                                                    +"'")},
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
                                 'var1_options': ("'set_attr_units = "
                                                  +'"mm";'+"'")},
                         'commands': [gda_util.metplus_command(
                                          'GridStat_fcstGLOBAL_DET.conf'
                                      )]},
        'SpefHum2m': {'env': {'var1_name': 'SPFH',
                              'var1_level': 'Z2',
                              'var1_options': ("'set_attr_units = "
                                               +'"g/kg"; convert(x)=x*1000'
                                               +"'")},
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
                                                    +'"TROPOPAUSE";'+"'")},
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
    'precip_accum24hr': {
        '24hrCCPA_G211': {'env': {'grid': 'G211',
                                  'met_config_overrides': ''},
                          'commands': [gda_util.metplus_command(
                                           'GridStat_fcstGLOBAL_DET_'
                                           +'obs24hrCCPA.conf'
                                       )]},
        '24hrCCPA_G212': {'env': {'grid': 'G212',
                                  'met_config_overrides': ''},
                          'commands': [gda_util.metplus_command(
                                           'GridStat_fcstGLOBAL_DET_'
                                           +'obs24hrCCPA.conf'
                                       )]},
        '24hrCCPA_G218': {'env': {'grid': 'G218',
                                  'met_config_overrides': ''},
                          'commands': [gda_util.metplus_command(
                                           'GridStat_fcstGLOBAL_DET_'
                                           +'obs24hrCCPA.conf'
                                       )]},
        '24hrCCPA_Nbrhd1': {'env': {'nbhrd_list': ("'1,3,5,7,9,11,13,"
                                                   +"15,17,19'"),
                                    'met_config_overrides': ''},
                            'commands': [gda_util.metplus_command(
                                             'GridStat_fcstGLOBAL_DET_'
                                             +'obs24hrCCPA_Nbrhd.conf'
                                         )]},
        '24hrCCPA_Nbrhd2': {'env': {'nbhrd_list': "'21,23,25,27,29'",
                                    'met_config_overrides': ''},
                            'commands': [gda_util.metplus_command(
                                             'GridStat_fcstGLOBAL_DET_'
                                             +'obs24hrCCPA_Nbrhd.conf'
                                         )]},
        '24hrCCPA_Nbrhd3': {'env': {'nbhrd_list': "'31,33,35,37'",
                                    'met_config_overrides': ''},
                            'commands': [gda_util.metplus_command(
                                             'GridStat_fcstGLOBAL_DET_'
                                             +'obs24hrCCPA_Nbrhd.conf'
                                         )]},
        '24hrCCPA_Nbrhd4': {'env': {'nbhrd_list': "'39,41,43'",
                                    'met_config_overrides': ''},
                            'commands': [gda_util.metplus_command(
                                             'GridStat_fcstGLOBAL_DET_'
                                             +'obs24hrCCPA_Nbrhd.conf'
                                         )]},
        '24hrCCPA_Nbrhd5': {'env': {'nbhrd_list': "'45,47,49'",
                                    'met_config_overrides': ''},
                            'commands': [gda_util.metplus_command(
                                             'GridStat_fcstGLOBAL_DET_'
                                             +'obs24hrCCPA_Nbrhd.conf'
                                         )]},
        '24hrCCPA_Nbrhd6': {'env': {'nbhrd_list': "'51,53,55'",
                                    'met_config_overrides': ''},
                            'commands': [gda_util.metplus_command(
                                             'GridStat_fcstGLOBAL_DET_'
                                             +'obs24hrCCPA_Nbrhd.conf'
                                         )]},
        '24hrCCPA_Nbrhd7': {'env': {'nbhrd_list': "'57,59'",
                                    'met_config_overrides': ''},
                            'commands': [gda_util.metplus_command(
                                             'GridStat_fcstGLOBAL_DET_'
                                             +'obs24hrCCPA_Nbrhd.conf'
                                         )]},
        '24hrCCPA_Nbrhd8': {'env': {'nbhrd_list': "'61,63'",
                                    'met_config_overrides': ''},
                            'commands': [gda_util.metplus_command(
                                             'GridStat_fcstGLOBAL_DET_'
                                             +'obs24hrCCPA_Nbrhd.conf'
                                         )]}
    },
    'precip_accum3hr': {
        '3hrCCPA_G212': {'env': {'grid': 'G212',
                                 'met_config_overrides': ''},
                         'commands': [gda_util.metplus_command(
                                          'GridStat_fcstGLOBAL_DET_'
                                          +'obs3hrCCPA.conf'
                                      )]},
        '3hrCCPA_Nbrhd1': {'env': {'nbhrd_list': ("'1,3,5,7,9,11,13,"
                                                  +"15,17,19'"),
                                   'met_config_overrides': ''},
                           'commands': [gda_util.metplus_command(
                                            'GridStat_fcstGLOBAL_DET_'
                                            +'obs3hrCCPA_Nbrhd.conf'
                                        )]},
        '3hrCCPA_Nbrhd2': {'env': {'nbhrd_list': "'21,23,25,27,29'",
                                   'met_config_overrides': ''},
                           'commands': [gda_util.metplus_command(
                                            'GridStat_fcstGLOBAL_DET_'
                                            +'obs3hrCCPA_Nbrhd.conf'
                                        )]},
        '3hrCCPA_Nbrhd3': {'env': {'nbhrd_list': "'31,33,35,37'",
                                   'met_config_overrides': ''},
                           'commands': [gda_util.metplus_command(
                                            'GridStat_fcstGLOBAL_DET_'
                                            +'obs3hrCCPA_Nbrhd.conf'
                                        )]},
        '3hrCCPA_Nbrhd4': {'env': {'nbhrd_list': "'39,41,43'",
                                   'met_config_overrides': ''},
                           'commands': [gda_util.metplus_command(
                                            'GridStat_fcstGLOBAL_DET_'
                                            +'obs3hrCCPA_Nbrhd.conf'
                                        )]},
        '3hrCCPA_Nbrhd5': {'env': {'nbhrd_list': "'45,47,49'",
                                   'met_config_overrides': ''},
                           'commands': [gda_util.metplus_command(
                                            'GridStat_fcstGLOBAL_DET_'
                                            +'obs3hrCCPA_Nbrhd.conf'
                                        )]},
        '3hrCCPA_Nbrhd6': {'env': {'nbhrd_list': "'51,53,55'",
                                   'met_config_overrides': ''},
                           'commands': [gda_util.metplus_command(
                                            'GridStat_fcstGLOBAL_DET_'
                                            +'obs3hrCCPA_Nbrhd.conf'
                                        )]},
        '3hrCCPA_Nbrhd7': {'env': {'nbhrd_list': "'57,59'",
                                   'met_config_overrides': ''},
                           'commands': [gda_util.metplus_command(
                                            'GridStat_fcstGLOBAL_DET_'
                                            +'obs3hrCCPA_Nbrhd.conf'
                                        )]},
        '3hrCCPA_Nbrhd8': {'env': {'nbhrd_list': "'61,63'",
                                   'met_config_overrides': ''},
                           'commands': [gda_util.metplus_command(
                                            'GridStat_fcstGLOBAL_DET_'
                                            +'obs3hrCCPA_Nbrhd.conf'
                                        )]}
    },
    'pres_levs': {
        'GeoHeight': {'env': {'var1_name': 'HGT',
                              'var1_levels': "'P1000, P700, P500, P250'",
                              'var1_options': '',
                              'met_config_overrides': "'climo_mean = fcst;'"},
                      'commands': [gda_util.metplus_command(
                                       'GridStat_fcstGLOBAL_DET_'
                                       +'obsModelAnalysis_climoERA5.conf'
                                   )]},
        'GeoHeight_FourierDecomp': {'env': {'var1_name': 'HGT',
                                            'var1_levels': 'P500',
                                            'met_config_overrides': ("'climo_"
                                                                     +"mean = "
                                                                     +"fcst;'")},
                                    'commands': [gda_util.metplus_command(
                                                     'GridStat_fcstGLOBAL_DET_'
                                                     +'obsModelAnalysis_'
                                                     +'climoERA5_FourierDecomp'
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
        'Ozone': {'env': {'var1_name': 'O3MR',
                          'var1_levels': ("'P925, P100, P70, P50, P30, P20, "
                                          +"P10, P5, P1'"),
                          'var1_options': ("'set_attr_units = "
                                           +'"ppm"; convert(x)=x*1000000'
                                           +"'"),
                          'met_config_overrides': "'climo_mean = fcst;'"},
                  'commands': [gda_util.metplus_command(
                                   'GridStat_fcstGLOBAL_DET_'
                                   +'obsModelAnalysis_climoERA5.conf'
                               )]},
        'PresSeaLevel': {'env': {'var1_name': 'PRMSL',
                                 'var1_levels': 'Z0',
                                 'var1_options': ("'set_attr_units = "
                                                  +'"hPa"; convert(p)=PA_to_HPA(p)'
                                                  +"'"),
                                 'met_config_overrides': "'climo_mean = fcst;'"},
                         'commands': [gda_util.metplus_command(
                                          'GridStat_fcstGLOBAL_DET_'
                                          +'obsModelAnalysis_climoERA5.conf'
                                      )]},
        'Temp': {'env': {'var1_name': 'TMP',
                         'var1_levels': "'P850, P500, P250'",
                         'var1_options': '',
                         'met_config_overrides': "'climo_mean = fcst;'"},
                 'commands': [gda_util.metplus_command(
                                  'GridStat_fcstGLOBAL_DET_'
                                  +'obsModelAnalysis_climoERA5.conf'
                              )]},
        'UWind': {'env': {'var1_name': 'UGRD',
                          'var1_levels': "'P850, P500, P250'",
                          'var1_options': '',
                          'met_config_overrides': "'climo_mean = fcst;'"},
                  'commands': [gda_util.metplus_command(
                                   'GridStat_fcstGLOBAL_DET_'
                                   +'obsModelAnalysis_climoERA5.conf'
                               )]},
        'VWind': {'env': {'var1_name': 'VGRD',
                          'var1_levels': "'P850, P500, P250'",
                          'var1_options': '',
                          'met_config_overrides': "'climo_mean = fcst;'"},
                  'commands': [gda_util.metplus_command(
                                   'GridStat_fcstGLOBAL_DET_'
                                   +'obsModelAnalysis_climoERA5.conf'
                               )]},
        'VectorWind': {'env': {'var1_name': 'UGRD',
                               'var1_levels': "'P850, P500, P250'",
                               'var2_name': 'VGRD',
                               'var2_levels': "'P850, P500, P250'",
                               'met_config_overrides': "'climo_mean = fcst;'"},
                       'commands': [gda_util.metplus_command(
                                        'GridStat_fcstGLOBAL_DET_'
                                        +'obsModelAnalysis_climoERA5_'
                                        +'VectorWind.conf'
                                    )]},
        'WindShear': {'env': {},
                      'commands': [gda_util.metplus_command(
                                       'GridStat_fcstGLOBAL_DET_'
                                       +'obsModelAnalysis_WindShear.conf'
                                   )]}
    },
    'sea_ice': {
        'DailyAvg_Concentration': {'env': {},
                                   'commands': [gda_util.metplus_command(
                                                   'GridStat_fcstGLOBAL_DET_'
                                                   +'obsOSI-SAF_DailyAvg.conf'
                                                )]},
    },
    'snow': {
        '24hrNOHRSC_WaterEqv_G211': {'env': {'grid': 'G211',
                                             'file_name_var': 'WaterEqv',
                                             'var1_name': 'WEASD',
                                             'var1_convert': '0.01'},
                                     'commands': [gda_util.metplus_command(
                                                      'GridStat_fcstGLOBAL_DET_'
                                                      +'obs24hrNOHRSC.conf'
                                                  )]},
        '24hrNOHRSC_Depth_G211': {'env': {'grid': 'G211',
                                          'file_name_var': 'Depth',
                                          'var1_name': 'SNOD',
                                          'var1_convert': '1'},
                                  'commands': [gda_util.metplus_command(
                                                   'GridStat_fcstGLOBAL_DET_'
                                                   +'obs24hrNOHRSC.conf'
                                               )]},
        '24hrNOHRSC_WaterEqv_G212': {'env': {'grid': 'G212',
                                             'file_name_var': 'WaterEqv',
                                             'var1_name': 'WEASD',
                                             'var1_convert': '0.01'},
                                     'commands': [gda_util.metplus_command(
                                                      'GridStat_fcstGLOBAL_DET_'
                                                      +'obs24hrNOHRSC.conf'
                                                  )]},
        '24hrNOHRSC_Depth_G212': {'env': {'grid': 'G212',
                                          'file_name_var': 'Depth',
                                          'var1_name': 'SNOD',
                                          'var1_convert': '1'},
                                  'commands': [gda_util.metplus_command(
                                                   'GridStat_fcstGLOBAL_DET_'
                                                   +'obs24hrNOHRSC.conf'
                                               )]},
        '24hrNOHRSC_WaterEqv_G218': {'env': {'grid': 'G218',
                                             'file_name_var': 'WaterEqv',
                                             'var1_name': 'WEASD',
                                             'var1_convert': '0.01'},
                                     'commands': [gda_util.metplus_command(
                                                      'GridStat_fcstGLOBAL_DET_'
                                                      +'obs24hrNOHRSC.conf'
                                                  )]},
        '24hrNOHRSC_Depth_G218': {'env': {'grid': 'G218',
                                          'file_name_var': 'Depth',
                                          'var1_name': 'SNOD',
                                          'var1_convert': '1'},
                                  'commands': [gda_util.metplus_command(
                                                   'GridStat_fcstGLOBAL_DET_'
                                                   +'obs24hrNOHRSC.conf'
                                               )]},
        '24hrNOHRSC_WaterEqv_Nbrhd1': {'env': {'file_name_var': 'WaterEqv',
                                               'nbhrd_list': ("'1,3,5,7,9,11,"
                                                              +"13,15,17,19'"),
                                               'var1_name': 'WEASD',
                                               'var1_convert': '0.01'},
                                       'commands': [gda_util.metplus_command(
                                                       'GridStat_fcstGLOBAL_DET_'
                                                       +'obs24hrNOHRSC_Nbrhd.conf'
                                                   )]},
        '24hrNOHRSC_WaterEqv_Nbrhd2': {'env': {'file_name_var': 'WaterEqv',
                                               'nbhrd_list': ("'21,23,25,27,"
                                                              +"29'"),
                                               'var1_name': 'WEASD',
                                               'var1_convert': '0.01'},
                                       'commands': [gda_util.metplus_command(
                                                       'GridStat_fcstGLOBAL_DET_'
                                                       +'obs24hrNOHRSC_Nbrhd.conf'
                                                   )]},
        '24hrNOHRSC_WaterEqv_Nbrhd3': {'env': {'file_name_var': 'WaterEqv',
                                               'nbhrd_list': "'31,33,35,37'",
                                               'var1_name': 'WEASD',
                                               'var1_convert': '0.01'},
                                       'commands': [gda_util.metplus_command(
                                                       'GridStat_fcstGLOBAL_DET_'
                                                       +'obs24hrNOHRSC_Nbrhd.conf'
                                                   )]},
        '24hrNOHRSC_WaterEqv_Nbrhd4': {'env': {'file_name_var': 'WaterEqv',
                                               'nbhrd_list': "'39,41,43'",
                                               'var1_name': 'WEASD',
                                               'var1_convert': '0.01'},
                                       'commands': [gda_util.metplus_command(
                                                       'GridStat_fcstGLOBAL_DET_'
                                                       +'obs24hrNOHRSC_Nbrhd.conf'
                                                   )]},
        '24hrNOHRSC_WaterEqv_Nbrhd5': {'env': {'file_name_var': 'WaterEqv',
                                               'nbhrd_list': "'45,47,49'",
                                               'var1_name': 'WEASD',
                                               'var1_convert': '0.01'},
                                       'commands': [gda_util.metplus_command(
                                                       'GridStat_fcstGLOBAL_DET_'
                                                       +'obs24hrNOHRSC_Nbrhd.conf'
                                                   )]},
        '24hrNOHRSC_WaterEqv_Nbrhd6': {'env': {'file_name_var': 'WaterEqv',
                                               'nbhrd_list': "'51,53,55'",
                                               'var1_name': 'WEASD',
                                               'var1_convert': '0.01'},
                                       'commands': [gda_util.metplus_command(
                                                       'GridStat_fcstGLOBAL_DET_'
                                                       +'obs24hrNOHRSC_Nbrhd.conf'
                                                   )]},
        '24hrNOHRSC_WaterEqv_Nbrhd7': {'env': {'file_name_var': 'WaterEqv',
                                               'nbhrd_list': "'57,59'",
                                               'var1_name': 'WEASD',
                                               'var1_convert': '0.01'},
                                       'commands': [gda_util.metplus_command(
                                                       'GridStat_fcstGLOBAL_DET_'
                                                       +'obs24hrNOHRSC_Nbrhd.conf'
                                                   )]},
        '24hrNOHRSC_WaterEqv_Nbrhd8': {'env': {'file_name_var': 'WaterEqv',
                                               'nbhrd_list': "'61,63'",
                                               'var1_name': 'WEASD',
                                               'var1_convert': '0.01'},
                                       'commands': [gda_util.metplus_command(
                                                       'GridStat_fcstGLOBAL_DET_'
                                                       +'obs24hrNOHRSC_Nbrhd.conf'
                                                   )]},
        '24hrNOHRSC_Depth_Nbrhd1': {'env': {'file_name_var': 'Depth',
                                            'nbhrd_list': ("'1,3,5,7,9,11,13,"
                                                           +"15,17,19'"),
                                            'var1_name': 'SNOD',
                                            'var1_convert': '1'},
                                    'commands': [gda_util.metplus_command(
                                                     'GridStat_fcstGLOBAL_DET_'
                                                     +'obs24hrNOHRSC_Nbrhd.conf'
                                                 )]},
        '24hrNOHRSC_Depth_Nbrhd2': {'env': {'file_name_var': 'Depth',
                                            'nbhrd_list': "'21,23,25,27,29'",
                                            'var1_name': 'SNOD',
                                            'var1_convert': '1'},
                                    'commands': [gda_util.metplus_command(
                                                     'GridStat_fcstGLOBAL_DET_'
                                                     +'obs24hrNOHRSC_Nbrhd.conf'
                                                 )]},
        '24hrNOHRSC_Depth_Nbrhd3': {'env': {'file_name_var': 'Depth',
                                            'nbhrd_list': "'31,33,35,37'",
                                            'var1_name': 'SNOD',
                                            'var1_convert': '1'},
                                    'commands': [gda_util.metplus_command(
                                                     'GridStat_fcstGLOBAL_DET_'
                                                     +'obs24hrNOHRSC_Nbrhd.conf'
                                                 )]},
        '24hrNOHRSC_Depth_Nbrhd4': {'env': {'file_name_var': 'Depth',
                                            'nbhrd_list': "'39,41,43'",
                                            'var1_name': 'SNOD',
                                            'var1_convert': '1'},
                                    'commands': [gda_util.metplus_command(
                                                     'GridStat_fcstGLOBAL_DET_'
                                                     +'obs24hrNOHRSC_Nbrhd.conf'
                                                 )]},
        '24hrNOHRSC_Depth_Nbrhd5': {'env': {'file_name_var': 'Depth',
                                            'nbhrd_list': "'45,47,49'",
                                            'var1_name': 'SNOD',
                                            'var1_convert': '1'},
                                    'commands': [gda_util.metplus_command(
                                                     'GridStat_fcstGLOBAL_DET_'
                                                     +'obs24hrNOHRSC_Nbrhd.conf'
                                                 )]},
        '24hrNOHRSC_Depth_Nbrhd6': {'env': {'file_name_var': 'Depth',
                                            'nbhrd_list': "'51,53,55'",
                                            'var1_name': 'SNOD',
                                            'var1_convert': '1'},
                                    'commands': [gda_util.metplus_command(
                                                     'GridStat_fcstGLOBAL_DET_'
                                                     +'obs24hrNOHRSC_Nbrhd.conf'
                                                 )]},
        '24hrNOHRSC_Depth_Nbrhd7': {'env': {'file_name_var': 'Depth',
                                            'nbhrd_list': "'57,59'",
                                            'var1_name': 'SNOD',
                                            'var1_convert': '1'},
                                    'commands': [gda_util.metplus_command(
                                                     'GridStat_fcstGLOBAL_DET_'
                                                     +'obs24hrNOHRSC_Nbrhd.conf'
                                                 )]},
        '24hrNOHRSC_Depth_Nbrhd8': {'env': {'file_name_var': 'Depth',
                                            'nbhrd_list': "'61,63'",
                                            'var1_name': 'SNOD',
                                            'var1_convert': '1'},
                                    'commands': [gda_util.metplus_command(
                                                     'GridStat_fcstGLOBAL_DET_'
                                                     +'obs24hrNOHRSC_Nbrhd.conf'
                                                 )]},
    },
    'sst': {
        'DailyAvg_SST': {'env': {},
                         'commands': [gda_util.metplus_command(
                                          'GridStat_fcstGLOBAL_DET_'
                                          +'obsGHRSST_OSPO_DailyAvg.conf'
                                      )]},
    },
}

################################################
#### gather_stats jobs
################################################
gather_stats_jobs_dict = {'env': {},
                    'commands': [gda_util.metplus_command(
                                     'StatAnalysis_fcstGLOBAL_DET.conf'
                                 )]}

# Create job scripts
if JOB_GROUP in ['reformat_data', 'assemble_data', 'generate_stats']:
    if JOB_GROUP == 'reformat_data':
        JOB_GROUP_jobs_dict = reformat_data_model_jobs_dict
    elif JOB_GROUP == 'assemble_data':
        JOB_GROUP_jobs_dict = assemble_data_model_jobs_dict
    elif JOB_GROUP == 'generate_stats':
        JOB_GROUP_jobs_dict = generate_stats_jobs_dict
    for verif_type in VERIF_CASE_STEP_type_list:
        print("----> Making job scripts for "+VERIF_CASE_STEP+" "
              +verif_type+" for job group "+JOB_GROUP)
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +verif_type)
        # Read in environment variables for verif_type
        if JOB_GROUP == 'assemble_data' and verif_type in ['precip_accum24hr',
                                                           'precip_accum3hr']:
            precip_file_accum_list = (os.environ \
                [VERIF_CASE_STEP_abbrev+'_'+verif_type+'_file_accum_list'] \
                .split(' '))
            precip_var_list = (os.environ \
                [VERIF_CASE_STEP_abbrev+'_'+verif_type+'_var_list'] \
                .split(' '))
        for verif_type_job in list(JOB_GROUP_jobs_dict[verif_type].keys()):
            # Initialize job environment dictionary
            job_env_dict = gda_util.initalize_job_env_dict(
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
            if JOB_GROUP == 'reformat_data':
                if verif_type in ['sst', 'sea_ice']:
                    job_env_dict['valid_hr_start'] = '00'
                    job_env_dict['valid_hr_end'] = '12'
                    job_env_dict['valid_hr_inc'] = '12'
                if verif_type == 'pres_levs' \
                        and verif_type_job == 'GeoHeightAnom':
                    if int(job_env_dict['valid_hr_start']) - 12 > 0:
                        job_env_dict['valid_hr_start'] = str(
                            int(job_env_dict['valid_hr_start']) - 12
                        )
                        job_env_dict['valid_hr_inc'] = '12'
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
                for model_idx in range(len(model_list)):
                    job_env_dict['MODEL'] = model_list[model_idx]
                    njobs+=1
                    job_env_dict['job_num'] = str(njobs)
                    # Create job file
                    job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
                    print("Creating job script: "+job_file)
                    job = open(job_file, 'w')
                    job.write('#!/bin/bash\n')
                    job.write('set -x\n')
                    job.write('\n')
                    # Set any environment variables for special cases
                    if JOB_GROUP == 'reformat_data':
                        if verif_type == 'pres_levs':
                            job_env_dict['TRUTH'] = os.environ[
                                VERIF_CASE_STEP_abbrev_type+'_truth_name_list'
                            ].split(' ')[model_idx]
                    if JOB_GROUP == 'assemble_data':
                        if verif_type in ['precip_accum24hr',
                                          'precip_accum3hr']:
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
                        if verif_type == 'pres_levs' \
                                and verif_type_job == 'DailyAvg_GeoHeightAnom':
                            if int(job_env_dict['fhr_inc']) < 24:
                                job_env_dict['fhr_inc'] = '24'
                            if int(job_env_dict['fhr_start']) < 24:
                                job_env_dict['fhr_start'] = str(
                                    int(job_env_dict['fhr_start']) + 24
                                )
                    elif JOB_GROUP == 'generate_stats':
                        if verif_type == 'pres_levs':
                            job_env_dict['TRUTH'] = os.environ[
                                VERIF_CASE_STEP_abbrev_type+'_truth_name_list'
                            ].split(' ')[model_idx]
                            if verif_type_job == 'DailyAvg_GeoHeightAnom':
                                if int(job_env_dict['fhr_inc']) < 24:
                                    job_env_dict['fhr_inc'] = '24'
                                if int(job_env_dict['fhr_start']) < 24:
                                    job_env_dict['fhr_start'] = str(
                                        int(job_env_dict['fhr_start']) + 24
                                    )
                    # Do file checks
                    all_truth_file_exist = False
                    model_files_exist = False
                    write_job_cmds = False
                    check_model_files = True
                    if check_model_files:
                        model_files_exist, valid_date_fhr_list = (
                            gda_util.check_model_files(job_env_dict)
                        )
                        job_env_dict['fhr_list'] = (
                            '"'+','.join(valid_date_fhr_list)+'"'
                        )
                        job_env_dict.pop('fhr_start')
                        job_env_dict.pop('fhr_end')
                        job_env_dict.pop('fhr_inc')
                    if JOB_GROUP == 'reformat_data':
                        if verif_type == 'pres_levs' \
                                and verif_type_job in ['GeoHeightAnom',
                                                       'WindShear']:
                            check_truth_files = True
                        else:
                            check_truth_files = False
                    elif JOB_GROUP == 'assemble_data':
                        check_truth_files = False
                    elif JOB_GROUP == 'generate_stats':
                        if verif_type == 'pres_levs' \
                                and verif_type_job in [
                                    'DailyAvg_GeoHeightAnom',
                                    'WindShear'
                                ]:
                            check_truth_files = False
                        elif verif_type == 'means':
                            check_truth_files = False
                        else:
                            check_truth_files = True
                    if check_truth_files:
                        all_truth_file_exist = gda_util.check_truth_files(
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
                    # Check job and model being run
                    if job_env_dict['MODEL'] \
                            in ['cmc', 'cmc_regional', 'dwd', 'ecmwf',
                                'fnmoc', 'jma', 'metfra', 'ukmet'] \
                            and verif_type_job == 'Ozone':
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
                job_env_dict = gda_util.initalize_job_env_dict(
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
                    all_truth_file_exist = gda_util.check_truth_files(
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
    job_env_dict = gda_util.initalize_job_env_dict(
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
            stat_files_exist = gda_util.check_stat_files(job_env_dict)
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
