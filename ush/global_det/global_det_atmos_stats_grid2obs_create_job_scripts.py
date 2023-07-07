#!/usr/bin/env python3
'''
Program Name: global_det_atmos_stats_grid2obs_create_job_scripts.py
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
    'ptype': {
        'PrepbufrNAM': {'env': {'prepbufr': 'nam',
                                'obs_window': '900',
                                'msg_type': 'ADPSFC',
                                'obs_bufr_var_list': "'PRWE'"},
                        'commands': [gda_util.metplus_command(
                                         'PB2NC_obsPrepbufr.conf'
                                     )]},
        'PrepbufrRAP': {'env': {'prepbufr': 'rap',
                                'obs_window': '900',
                                'msg_type': 'ADPSFC',
                                'obs_bufr_var_list': "'PRWE'"},
                        'commands': [gda_util.metplus_command(
                                         'PB2NC_obsPrepbufr.conf'
                                     )]},
    },
    'sfc': {
        'PrepbufrGDAS': {'env': {'prepbufr': 'gdas',
                                 'obs_window': '1800',
                                 'msg_type': "'ADPUPA, AIRCAR, AIRCFT'",
                                 'obs_bufr_var_list': ("'D_CAPE, D_MLCAPE, "
                                                       +"D_PBL'")},
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
        'PrepbufrRAP': {'env': {'prepbufr': 'rap',
                                'obs_window': '900',
                                'msg_type': 'ADPSFC',
                                'obs_bufr_var_list': ("'PMO, UOB, VOB, MXGS, "
                                                      +"TOB, TDO, D_RH, QOB, "
                                                      +"HOVI, CEILING, TOCC'")},
                        'commands': [gda_util.metplus_command(
                                         'PB2NC_obsPrepbufr.conf'
                                     )]},
    }
}
reformat_data_model_jobs_dict = {
    'pres_levs': {},
    'ptype': {
        'Rain': {'env': {'var1_name': 'CRAIN',
                         'var1_level': 'L0',
                         'grid': 'G104'},
                 'commands': [gda_util.metplus_command(
                                  'RegridDataPlane_fcstGLOBAL_DET.conf'
                              )]},
        'Snow': {'env': {'var1_name': 'CSNOW',
                         'var1_level': 'L0',
                         'grid': 'G104'},
                 'commands': [gda_util.metplus_command(
                                  'RegridDataPlane_fcstGLOBAL_DET.conf'
                              )]},
        'FrzRain': {'env': {'var1_name': 'CFRZR',
                            'var1_level': 'L0',
                            'grid': 'G104'},
                    'commands': [gda_util.metplus_command(
                                     'RegridDataPlane_fcstGLOBAL_DET.conf'
                                 )]},
        'IcePel': {'env': {'var1_name': 'CICEP',
                           'var1_level': 'L0',
                           'grid': 'G104'},
                   'commands': [gda_util.metplus_command(
                                    'RegridDataPlane_fcstGLOBAL_DET.conf'
                                )]},
    },
    'sfc': {}
}

################################################
#### assemble_data jobs
################################################
assemble_data_obs_jobs_dict = {
    'pres_levs': {},
    'ptype': {},
    'sfc': {}
}
assemble_data_model_jobs_dict = {
    'pres_levs': {},
    'ptype': {
        'Ptype': {'env': {},
                  'commands': [
                      gda_util.python_command(
                          'global_det_atmos_stats_grid2obs_'
                          'create_merged_ptype.py',
                          [os.path.join(
                               '$DATA', '${VERIF_CASE}_${STEP}',
                               'METplus_output',
                               '${RUN}.{valid?fmt=%Y%m%d}',
                               '$MODEL', '$VERIF_CASE',
                               'regrid_data_plane_${VERIF_TYPE}_Rain_'
                               +'init{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                           ),
                           os.path.join(
                               '$DATA', '${VERIF_CASE}_${STEP}',
                               'METplus_output',
                               '${RUN}.{valid?fmt=%Y%m%d}',
                               '$MODEL', '$VERIF_CASE',
                               'regrid_data_plane_${VERIF_TYPE}_Snow_'
                               +'init{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                           ),
                           os.path.join(
                               '$DATA', '${VERIF_CASE}_${STEP}',
                               'METplus_output',
                               '${RUN}.{valid?fmt=%Y%m%d}',
                               '$MODEL', '$VERIF_CASE',
                               'regrid_data_plane_${VERIF_TYPE}_FrzRain_'
                               +'init{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                           ),
                           os.path.join(
                               '$DATA', '${VERIF_CASE}_${STEP}',
                               'METplus_output',
                               '${RUN}.{valid?fmt=%Y%m%d}',
                               '$MODEL', '$VERIF_CASE',
                               'regrid_data_plane_${VERIF_TYPE}_IcePel_'
                               +'init{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                           )]
                      )
                  ]}
    },
    'sfc': {
        'TempAnom2m': {'env': {'prepbufr': 'nam',
                               'obs_window': '900',
                               'msg_type': 'ADPSFC',
                               'var1_fcst_name': 'TMP',
                               'var1_fcst_levels': 'Z2',
                               'var1_fcst_options': '',
                               'var1_obs_name': 'TMP',
                               'var1_obs_levels': 'Z2',
                               'var1_obs_options': '',
                               'met_config_overrides': ("'climo_mean "
                                                        +"= fcst;'")},
                       'commands': [gda_util.metplus_command(
                                        'PointStat_fcstGLOBAL_DET_'
                                        +'obsPrepbufr_climoERA5_'
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
                                             +'${VERIF_TYPE}_'
                                             +'${job_name}_'
                                             +'{lead?fmt=%2H}0000L_'
                                             +'{valid?fmt=%Y%m%d}_'
                                             +'{valid?fmt=%H}0000V'
                                             +'.stat'
                                         )]
                                    )]},
    }
}

################################################
#### generate_stats jobs
################################################
generate_stats_jobs_dict = {
    'pres_levs': {
        'GeoHeight': {'env': {'prepbufr': 'gdas',
                              'obs_window': '1800',
                              'msg_type': "'AIRUPA, ADPUPA, ANYAIR'",
                              'var1_fcst_name': 'HGT',
                              'var1_fcst_levels': ("'P1000, P925, P850, "
                                                   +"P700, P500, P400, "
                                                   +"P300, P250, P200, "
                                                   +"P150, P100, P50, "
                                                   +"P20, P10, P5, P1'"),
                              'var1_fcst_options': '',
                              'var1_obs_name': 'HGT',
                              'var1_obs_levels': ("'P1000, P925, P850, "
                                                  +"P700, P500, P400, "
                                                  +"P300, P250, P200, "
                                                  +"P150, P100, P50, "
                                                  +"P20, P10, P5, P1'"),
                              'var1_obs_options': '',
                              'met_config_overrides': ''},
                      'commands': [gda_util.metplus_command(
                                       'PointStat_fcstGLOBAL_DET_'
                                       +'obsPrepbufr.conf'
                                   )]},
        'RelHum': {'env': {'prepbufr': 'gdas',
                           'obs_window': '1800',
                           'msg_type': "'AIRUPA, ADPUPA, ANYAIR'",
                           'var1_fcst_name': 'RH',
                           'var1_fcst_levels': ("'P1000, P925, P850, "
                                                +"P700, P500, P400, "
                                                +"P300, P250, P200, "
                                                +"P150, P100, P50, "
                                                +"P20, P10, P5, P1'"),
                           'var1_fcst_options': '',
                           'var1_obs_name': 'RH',
                           'var1_obs_levels': ("'P1000, P925, P850, "
                                               +"P700, P500, P400, "
                                               +"P300, P250, P200, "
                                               +"P150, P100, P50, "
                                               +"P20, P10, P5, P1'"),
                           'var1_obs_options': '',
                           'met_config_overrides': ''},
                   'commands': [gda_util.metplus_command(
                                    'PointStat_fcstGLOBAL_DET_'
                                    +'obsPrepbufr.conf'
                                )]},
        'SpefHum': {'env': {'prepbufr': 'gdas',
                            'obs_window': '1800',
                            'msg_type': "'AIRUPA, ADPUPA, ANYAIR'",
                            'var1_fcst_name': 'SPFH',
                            'var1_fcst_levels': ("'P1000, P925, P850, "
                                                 +"P700, P500, P400, "
                                                 +"P300, P250, P200, "
                                                 +"P150, P100, P50, "
                                                 +"P20, P10, P5, P1'"),
                            'var1_fcst_options': ("'set_attr_units = "
                                                  +'"g/kg"; convert(x)=x*1000'
                                                  +"'"),
                            'var1_obs_name': 'SPFH',
                            'var1_obs_levels': ("'P1000, P925, P850, "
                                                +"P700, P500, P400, "
                                                +"P300, P250, P200, "
                                                +"P150, P100, P50, "
                                                +"P20, P10, P5, P1'"),
                            'var1_obs_options': ("'set_attr_units = "
                                                 +'"g/kg"; convert(x)=x*1000'
                                                 +"'"),
                            'met_config_overrides': ''},
                    'commands': [gda_util.metplus_command(
                                     'PointStat_fcstGLOBAL_DET_'
                                     +'obsPrepbufr.conf'
                                 )]},
        'Temp': {'env': {'prepbufr': 'gdas',
                         'obs_window': '1800',
                         'msg_type': "'AIRUPA, ADPUPA, ANYAIR'",
                         'var1_fcst_name': 'TMP',
                         'var1_fcst_levels': ("'P1000, P925, P850, "
                                              +"P700, P500, P400, "
                                              +"P300, P250, P200, "
                                              +"P150, P100, P50, "
                                              +"P20, P10, P5, P1'"),
                         'var1_fcst_options': '',
                         'var1_obs_name': 'TMP',
                         'var1_obs_levels': ("'P1000, P925, P850, "
                                             +"P700, P500, P400, "
                                             +"P300, P250, P200, "
                                             +"P150, P100, P50, "
                                             +"P20, P10, P5, P1'"),
                         'var1_obs_options': '',
                         'met_config_overrides': ''},
                 'commands': [gda_util.metplus_command(
                                  'PointStat_fcstGLOBAL_DET_'
                                  +'obsPrepbufr.conf'
                              )]},
        'UWind': {'env': {'prepbufr': 'gdas',
                          'obs_window': '1800',
                          'msg_type': "'AIRUPA, ADPUPA, ANYAIR'",
                          'var1_fcst_name': 'UGRD',
                          'var1_fcst_levels': ("'P1000, P925, P850, "
                                               +"P700, P500, P400, "
                                               +"P300, P250, P200, "
                                               +"P150, P100, P50, "
                                               +"P20, P10, P5, P1'"),
                          'var1_fcst_options': '',
                          'var1_obs_name': 'UGRD',
                          'var1_obs_levels': ("'P1000, P925, P850, "
                                              +"P700, P500, P400, "
                                              +"P300, P250, P200, "
                                              +"P150, P100, P50, "
                                              +"P20, P10, P5, P1'"),
                          'var1_obs_options': '',
                          'met_config_overrides': ''},
                  'commands': [gda_util.metplus_command(
                                   'PointStat_fcstGLOBAL_DET_'
                                   +'obsPrepbufr.conf'
                               )]},
        'VWind': {'env': {'prepbufr': 'gdas',
                          'obs_window': '1800',
                          'msg_type': "'AIRUPA, ADPUPA, ANYAIR'",
                          'var1_fcst_name': 'VGRD',
                          'var1_fcst_levels': ("'P1000, P925, P850, "
                                               +"P700, P500, P400, "
                                               +"P300, P250, P200, "
                                               +"P150, P100, P50, "
                                               +"P20, P10, P5, P1'"),
                          'var1_fcst_options': '',
                          'var1_obs_name': 'VGRD',
                          'var1_obs_levels': ("'P1000, P925, P850, "
                                              +"P700, P500, P400, "
                                              +"P300, P250, P200, "
                                              +"P150, P100, P50, "
                                              +"P20, P10, P5, P1'"),
                          'var1_obs_options': '',
                          'met_config_overrides': ''},
                  'commands': [gda_util.metplus_command(
                                   'PointStat_fcstGLOBAL_DET_'
                                   +'obsPrepbufr.conf'
                               )]},
        'VectorWind': {'env': {'prepbufr': 'gdas',
                               'obs_window': '1800',
                               'msg_type': "'AIRUPA, ADPUPA, ANYAIR'",
                               'var1_fcst_name': 'UGRD',
                               'var1_fcst_levels': ("'P1000, P925, P850, "
                                                    +"P700, P500, P400, "
                                                    +"P300, P250, P200, "
                                                    +"P150, P100, P50, "
                                                    +"P20, P10, P5, P1'"),
                               'var1_fcst_options': '',
                               'var1_obs_name': 'UGRD',
                               'var1_obs_levels': ("'P1000, P925, P850, "
                                                   +"P700, P500, P400, "
                                                   +"P300, P250, P200, "
                                                   +"P150, P100, P50, "
                                                   +"P20, P10, P5, P1'"),
                               'var1_obs_options': '',
                               'var2_fcst_name': 'VGRD',
                               'var2_fcst_levels': ("'P1000, P925, P850, "
                                                    +"P700, P500, P400, "
                                                    +"P300, P250, P200, "
                                                    +"P150, P100, P50, "
                                                    +"P20, P10, P5, P1'"),
                               'var2_fcst_options': '',
                               'var2_obs_name': 'VGRD',
                               'var2_obs_levels': ("'P1000, P925, P850, "
                                                   +"P700, P500, P400, "
                                                   +"P300, P250, P200, "
                                                   +"P150, P100, P50, "
                                                   +"P20, P10, P5, P1'"),
                               'var2_obs_options': '',
                               'met_config_overrides': ''},
                       'commands': [gda_util.metplus_command(
                                        'PointStat_fcstGLOBAL_DET_'
                                        +'obsPrepbufr_VectorWind.conf'
                                    )]}
    },
    'ptype': {
        'Rain': {'env': {'prepbufr': 'nam',
                         'obs_window': '900',
                         'msg_type': "'ADPSFC'",
                         'var1_fcst_name': 'CRAIN',
                         'var1_fcst_levels': 'L0',
                         'var1_fcst_options': ("'set_attr_units = "
                                               +'"unitless";'+"'"),
                         'var1_fcst_threshs': "'ge1.0'",
                         'var1_obs_name': 'PRWE',
                         'var1_obs_levels': 'Z0',
                         'var1_obs_options': '',
                         'var1_obs_threshs': "'ge161&&le163'",
                         'met_config_overrides': ''},
                 'commands': [gda_util.metplus_command(
                                  'PointStat_fcstGLOBAL_DET_'
                                  +'obsPrepbufr_Thresh_Ptype.conf'
                              )]},
        'Snow': {'env': {'prepbufr': 'nam',
                         'obs_window': '900',
                         'msg_type': "'ADPSFC'",
                         'var1_fcst_name': 'CSNOW',
                         'var1_fcst_levels': 'L0',
                         'var1_fcst_options': ("'set_attr_units = "
                                               +'"unitless";'+"'"),
                         'var1_fcst_threshs': "'ge1.0'",
                         'var1_obs_name': 'PRWE',
                         'var1_obs_levels': 'Z0',
                         'var1_obs_options': '',
                         'var1_obs_threshs': "'ge171&&le173'",
                         'met_config_overrides': ''},
                 'commands': [gda_util.metplus_command(
                                  'PointStat_fcstGLOBAL_DET_'
                                  +'obsPrepbufr_Thresh_Ptype.conf'
                              )]},
        'FrzRain': {'env': {'prepbufr': 'nam',
                            'obs_window': '900',
                            'msg_type': "'ADPSFC'",
                            'var1_fcst_name': 'CFRZR',
                            'var1_fcst_levels': 'L0',
                            'var1_fcst_options': ("'set_attr_units = "
                                                  +'"unitless";'+"'"),
                            'var1_fcst_threshs': "'ge1.0'",
                            'var1_obs_name': 'PRWE',
                            'var1_obs_levels': 'Z0',
                            'var1_obs_options': '',
                            'var1_obs_threshs': "'ge164&&le166'",
                            'met_config_overrides': ''},
                    'commands': [gda_util.metplus_command(
                                     'PointStat_fcstGLOBAL_DET_'
                                     +'obsPrepbufr_Thresh_Ptype.conf'
                                 )]},
        'IcePel': {'env': {'prepbufr': 'nam',
                           'obs_window': '900',
                           'msg_type': "'ADPSFC'",
                           'var1_fcst_name': 'CICEP',
                           'var1_fcst_levels': 'L0',
                           'var1_fcst_options': ("'set_attr_units = "
                                                 +'"unitless";'+"'"),
                           'var1_fcst_threshs': "'ge1.0'",
                           'var1_obs_name': 'PRWE',
                           'var1_obs_levels': 'Z0',
                           'var1_obs_options': '',
                           'var1_obs_threshs': "'ge174&&le176'",
                           'met_config_overrides': ''},
                   'commands': [gda_util.metplus_command(
                                    'PointStat_fcstGLOBAL_DET_'
                                    +'obsPrepbufr_Thresh_Ptype.conf'
                                )]},
        'Ptype': {'env': {'prepbufr': 'nam',
                          'obs_window': '900',
                          'msg_type': "'ADPSFC'",
                          'met_config_overrides': ''},
                  'commands': [gda_util.metplus_command(
                                   'PointStat_fcstGLOBAL_DET_'
                                   +'obsPrepbufr_Ptype_MCTC.conf'
                               )]},
    },
    'sfc': {
        'CAPEMixedLayer': {'env': {'prepbufr': 'gdas',
                                   'obs_window': '1800',
                                   'msg_type': "'AIRUPA, ADPUPA, ANYAIR'",
                                   'var1_fcst_name': 'CAPE',
                                   'var1_fcst_levels': "'P90-0'",
                                   'var1_fcst_options': ("'cnt_thresh = "
                                                         +"[ >0 ];'"),
                                   'var1_fcst_threshs': ("'ge500, ge1000, "
                                                         +"ge1500, ge2000, "
                                                         +"ge3000, ge4000, "
                                                         +"ge5000'"),
                                   'var1_obs_name': 'MLCAPE',
                                   'var1_obs_levels': "'L0-90000'",
                                   'var1_obs_options': ("'cnt_thresh = "
                                                        +"[ >0 ]; "
                                                        +"cnt_logic = "
                                                        +"UNION;'"),
                                   'var1_obs_threshs': ("'ge500, ge1000, "
                                                        +"ge1500, ge2000, "
                                                        +"ge3000, ge4000, "
                                                        +"ge5000'"),
                                   'met_config_overrides': ''},
                           'commands': [gda_util.metplus_command(
                                            'PointStat_fcstGLOBAL_DET_'
                                            +'obsPrepbufr_Thresh.conf'
                                        )]},
        'CAPESfcBased': {'env': {'prepbufr': 'gdas',
                                 'obs_window': '1800',
                                 'msg_type': "'AIRUPA, ADPUPA, ANYAIR'",
                                 'var1_fcst_name': 'CAPE',
                                 'var1_fcst_levels': 'Z0',
                                 'var1_fcst_options': ("'cnt_thresh = "
                                                       +"[ >0 ];'"),
                                 'var1_fcst_threshs': ("'ge500, ge1000, "
                                                       +"ge1500, ge2000, "
                                                       +"ge3000, ge4000, "
                                                       +"ge5000'"),
                                 'var1_obs_name': 'CAPE',
                                 'var1_obs_levels': "'L0-100000'",
                                 'var1_obs_options': ("'cnt_thresh = "
                                                      +"[ >0 ]; "
                                                      +"cnt_logic = "
                                                      +"UNION;'"),
                                 'var1_obs_threshs': ("'ge500, ge1000, "
                                                      +"ge1500, ge2000, "
                                                      +"ge3000, ge4000, "
                                                      +"ge5000'"),
                                 'met_config_overrides': ''},
                         'commands': [gda_util.metplus_command(
                                          'PointStat_fcstGLOBAL_DET_'
                                          +'obsPrepbufr_Thresh.conf'
                                      )]},
        'Ceiling': {'env': {'prepbufr': 'nam',
                            'obs_window': '900',
                            'msg_type': 'ADPSFC',
                            'var1_fcst_name': 'HGT',
                            'var1_fcst_levels': 'L0',
                            'var1_fcst_options': ("'GRIB_lvl_typ = 215;"
                                                  +"set_attr_level = "
                                                  +'"CEILING";'+"'"),
                            'var1_fcst_threshs': ("'lt152, lt305, "
                                                  +"lt914, ge914, "
                                                  +"lt1524, lt3048'"),
                            'var1_obs_name': 'CEILING',
                            'var1_obs_levels': 'L0',
                            'var1_obs_options': '',
                            'var1_obs_threshs': ("'lt152, lt305, "
                                                 +"lt914, ge914, "
                                                 +"lt1524, lt3048'"),
                            'met_config_overrides': ''},
                    'commands': [gda_util.metplus_command(
                                     'PointStat_fcstGLOBAL_DET_'
                                     +'obsPrepbufr_Thresh.conf'
                                 )]},
        'DailyAvg_TempAnom2m': {'env': {'prepbufr': 'nam',
                                        'obs_window': '900',
                                        'msg_type': 'ADPSFC',
                                        'var1_fcst_name': 'TMP',
                                        'var1_fcst_levels': 'Z2',
                                        'var1_fcst_options': '',
                                        'var1_obs_name': 'TMP',
                                        'var1_obs_levels': 'Z2',
                                        'var1_obs_options': '',
                                        'met_config_overrides': ("'climo_mean "
                                                                 +"= fcst;'")},
                                'commands': [gda_util.python_command(
                                                'global_det_atmos_stats_'
                                                'grid2obs_create_daily_avg.py',
                                                ['TMP_ANOM_Z2',
                                                  os.path.join(
                                                      '$DATA',
                                                      '${VERIF_CASE}_${STEP}',
                                                      'METplus_output',
                                                      '${RUN}.'
                                                      +'{valid?fmt=%Y%m%d}',
                                                      '$MODEL', '$VERIF_CASE',
                                                      'anomaly_${VERIF_TYPE}_'
                                                      +'TempAnom2m_init'
                                                      +'{init?fmt=%Y%m%d%H}_'
                                                      +'fhr{lead?fmt=%3H}.stat'
                                                ),
                                                os.path.join(
                                                    '$COMIN', 'stats',
                                                    '$COMPONENT',
                                                    '${RUN}.{valid?fmt=%Y%m%d}',
                                                    '$MODEL', '$VERIF_CASE',
                                                    'anomaly_${VERIF_TYPE}_'
                                                    +'TempAnom2m_init'
                                                    +'{init?fmt=%Y%m%d%H}_'
                                                    +'fhr{lead?fmt=%3H}.stat'
                                                )]
                                            ),
                                            'ndaily_avg_stat_files='
                                            +'$(ls '+os.path.join(
                                                '$DATA',
                                                '${VERIF_CASE}_${STEP}',
                                                'METplus_output',
                                                '${RUN}.${DATE}',
                                                '$MODEL', '$VERIF_CASE',
                                                'daily_avg_*.stat'
                                            )+'|wc -l)',
                                            ('if [ $ndaily_avg_stat_files '
                                            +'-ne 0 ]; then'),
                                            gda_util.metplus_command(
                                                'StatAnalysis_fcstGLOBAL_DET_'
                                                +'obsPrepbufr_MPRtoSL1L2.conf'
                                            ),
                                            'fi']},
        'Dewpoint2m': {'env': {'prepbufr': 'nam',
                               'obs_window': '900',
                               'msg_type': 'ADPSFC',
                               'var1_fcst_name': 'DPT',
                               'var1_fcst_levels': 'Z2',
                               'var1_fcst_options': '',
                               'var1_fcst_threshs': ("'ge277.594, ge283.15, "
                                                     +"ge288.706, ge294.261'"),
                               'var1_obs_name': 'DPT',
                               'var1_obs_levels': 'Z2',
                               'var1_obs_options': '',
                               'var1_obs_threshs': ("'ge277.594, ge283.15, "
                                                    +"ge288.706, ge294.261'"),
                               'met_config_overrides': ''},
                       'commands': [gda_util.metplus_command(
                                        'PointStat_fcstGLOBAL_DET_'
                                        +'obsPrepbufr_Thresh.conf'
                                    )]},
        'PBLHeight': {'env': {'prepbufr': 'gdas',
                              'obs_window': '1800',
                              'msg_type': "'AIRUPA, ADPUPA, ANYAIR'",
                              'var1_fcst_name': 'HPBL',
                              'var1_fcst_levels': 'L0',
                              'var1_fcst_options': '',
                              'var1_obs_name': 'HPBL',
                              'var1_obs_levels': 'L0',
                              'var1_obs_options': '',
                              'met_config_overrides': ''},
                      'commands': [gda_util.metplus_command(
                                       'PointStat_fcstGLOBAL_DET_'
                                       +'obsPrepbufr.conf'
                                   )]},
        'RelHum2m': {'env': {'prepbufr': 'nam',
                             'obs_window': '900',
                             'msg_type': 'ADPSFC',
                             'var1_fcst_name': 'RH',
                             'var1_fcst_levels': 'Z2',
                             'var1_fcst_options': '',
                             'var1_fcst_threshs': "'le15, le20, le25, le30'",
                             'var1_obs_name': 'RH',
                             'var1_obs_levels': 'Z2',
                             'var1_obs_options': '',
                             'var1_obs_threshs': "'le15, le20, le25, le30'",
                             'met_config_overrides': ''},
                     'commands': [gda_util.metplus_command(
                                      'PointStat_fcstGLOBAL_DET_'
                                      +'obsPrepbufr_Thresh.conf'
                                  )]},
        'SeaLevelPres': {'env': {'prepbufr': 'nam',
                                 'obs_window': '900',
                                 'msg_type': 'ADPSFC',
                                 'var1_fcst_name': 'PRMSL',
                                 'var1_fcst_levels': 'Z0',
                                 'var1_fcst_options': ("'set_attr_units = "
                                                       +'"hPa"; convert(p)='
                                                       +'PA_to_HPA(p)'
                                                       +"'"),
                                 'var1_obs_name': 'PRMSL',
                                 'var1_obs_levels': 'Z0',
                                 'var1_obs_options': ("'set_attr_units = "
                                                      +'"hPa"; convert(p)='
                                                      +'PA_to_HPA(p)'
                                                      +"'"),
                                 'met_config_overrides': ''},
                         'commands': [gda_util.metplus_command(
                                          'PointStat_fcstGLOBAL_DET_'
                                          +'obsPrepbufr.conf'
                                      )]},
        'Temp2m': {'env': {'prepbufr': 'nam',
                           'obs_window': '900',
                           'msg_type': 'ADPSFC',
                           'var1_fcst_name': 'TMP',
                           'var1_fcst_levels': 'Z2',
                           'var1_fcst_options': '',
                           'var1_obs_name': 'TMP',
                           'var1_obs_levels': 'Z2',
                           'var1_obs_options': '',
                           'met_config_overrides': ''},
                   'commands': [gda_util.metplus_command(
                                    'PointStat_fcstGLOBAL_DET_'
                                    +'obsPrepbufr.conf'
                                )]},
        'TotCloudCover': {'env': {'prepbufr': 'nam',
                                  'obs_window': '900',
                                  'msg_type': 'ADPSFC',
                                  'var1_fcst_name': 'TCDC',
                                  'var1_fcst_levels': 'L0',
                                  'var1_fcst_options': ("'GRIB_lvl_typ = 10;"
                                                        +"set_attr_level = "
                                                        +'"TOTAL";'+"'"),
                                  'var1_fcst_threshs': "'lt10, gt10, gt50, gt90'",
                                  'var1_obs_name': 'TCDC',
                                  'var1_obs_levels': 'L0',
                                  'var1_obs_options': '',
                                  'var1_obs_threshs': "'lt10, gt10, gt50, gt90'",
                                  'met_config_overrides': ''},
                          'commands': [gda_util.metplus_command(
                                           'PointStat_fcstGLOBAL_DET_'
                                           +'obsPrepbufr_Thresh.conf'
                                       )]},
        'UWind10m': {'env': {'prepbufr': 'nam',
                             'obs_window': '900',
                             'msg_type': 'ADPSFC',
                             'var1_fcst_name': 'UGRD',
                             'var1_fcst_levels': 'Z10',
                             'var1_fcst_options': '',
                             'var1_obs_name': 'UGRD',
                             'var1_obs_levels': 'Z10',
                             'var1_obs_options': '',
                             'met_config_overrides': ''},
                     'commands': [gda_util.metplus_command(
                                      'PointStat_fcstGLOBAL_DET_'
                                       +'obsPrepbufr.conf'
                                  )]},
        'Visibility': {'env': {'prepbufr': 'nam',
                               'obs_window': '900',
                               'msg_type': 'ADPSFC',
                               'var1_fcst_name': 'VIS',
                               'var1_fcst_levels': 'Z0',
                               'var1_fcst_options': ("'censor_thresh = gt16090;"
                                                     +"censor_val = 16090;'"),
                               'var1_fcst_threshs': ("'lt805, lt1609, "
                                                     +"lt4828, lt8045, "
                                                     +"ge8045, "
                                                     +"lt16090'"),
                               'var1_obs_name': 'VIS',
                               'var1_obs_levels': 'Z0',
                               'var1_obs_options': '',
                               'var1_obs_threshs': ("'lt805, lt1609, "
                                                    +"lt4828, lt8045, "
                                                    +"ge8045, "
                                                    +"lt16090'"),
                               'met_config_overrides': ''},
                       'commands': [gda_util.metplus_command(
                                        'PointStat_fcstGLOBAL_DET_'
                                        +'obsPrepbufr_Thresh.conf'
                                    )]},
        'VWind10m': {'env': {'prepbufr': 'nam',
                             'obs_window': '900',
                             'msg_type': 'ADPSFC',
                             'var1_fcst_name': 'VGRD',
                             'var1_fcst_levels': 'Z10',
                             'var1_fcst_options': '',
                             'var1_obs_name': 'VGRD',
                             'var1_obs_levels': 'Z10',
                             'var1_obs_options': '',
                             'met_config_overrides': ''},
                     'commands': [gda_util.metplus_command(
                                      'PointStat_fcstGLOBAL_DET_'
                                       +'obsPrepbufr.conf'
                                  )]},
        'WindGust': {'env': {'prepbufr': 'nam',
                             'obs_window': '900',
                             'msg_type': 'ADPSFC',
                             'var1_fcst_name': 'GUST',
                             'var1_fcst_levels': 'Z0',
                             'var1_fcst_options': '',
                             'var1_obs_name': 'GUST',
                             'var1_obs_levels': 'Z0',
                             'var1_obs_options': '',
                             'met_config_overrides': ''},
                     'commands': [gda_util.metplus_command(
                                      'PointStat_fcstGLOBAL_DET_'
                                       +'obsPrepbufr.conf'
                                  )]},
        'VectorWind10m': {'env': {'prepbufr': 'nam',
                                  'obs_window': '900',
                                  'msg_type': 'ADPSFC',
                                  'var1_fcst_name': 'UGRD',
                                  'var1_fcst_levels': 'Z10',
                                  'var1_fcst_options': '',
                                  'var2_fcst_name': 'VGRD',
                                  'var2_fcst_levels': 'Z10',
                                  'var2_fcst_options': '',
                                  'var1_obs_name': 'UGRD',
                                  'var1_obs_levels': 'Z10',
                                  'var1_obs_options': '',
                                  'var2_obs_name': 'VGRD',
                                  'var2_obs_levels': 'Z10',
                                  'var2_obs_options': '',
                                  'met_config_overrides': ''},
                          'commands': [gda_util.metplus_command(
                                          'PointStat_fcstGLOBAL_DET_'
                                          +'obsPrepbufr_VectorWind.conf'
                                       )]},
    }
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
            fhr_list = job_env_dict['fhr_list']
            verif_type_job_commands_list = (
                JOB_GROUP_jobs_dict[verif_type]\
                [verif_type_job]['commands']
            ) 
            # Loop through and write job script for dates and models
            if JOB_GROUP == 'assemble_data':
                if verif_type == 'sfc' \
                        and verif_type_job == 'TempAnom2m':
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
                job_env_dict['fhr_list'] = fhr_list
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
                    if JOB_GROUP in ['assemble_data', 'generate_stats']:
                        if verif_type == 'pres_levs':
                            job_env_dict['grid'] = 'G004'
                            mask_list = [
                                'G004_GLOBAL', 'G004_NHEM', 'G004_SHEM',
                                'G004_TROPICS', 'Bukovsky_G004_CONUS',
                                'Alaska_G004'
                            ]
                        elif verif_type in ['sfc', 'ptype']:
                            job_env_dict['grid'] = 'G104'
                            mask_list = [
                                'Bukovsky_G104_CONUS', 'Bukovsky_G104_CONUS_East',
                                'Bukovsky_G104_CONUS_West',
                                'Bukovsky_G104_CONUS_South',
                                'Bukovsky_G104_CONUS_Central',
                                'Bukovsky_G104_Appalachia',
                                'Bukovsky_G104_CPlains',
                                'Bukovsky_G104_DeepSouth',
                                'Bukovsky_G104_GreatBasin',
                                'Bukovsky_G104_GreatLakes',
                                'Bukovsky_G104_Mezquital',
                                'Bukovsky_G104_MidAtlantic',
                                'Bukovsky_G104_NorthAtlantic',
                                'Bukovsky_G104_NPlains',
                                'Bukovsky_G104_NRockies',
                                'Bukovsky_G104_PacificNW',
                                'Bukovsky_G104_PacificSW',
                                'Bukovsky_G104_Prairie',
                                'Bukovsky_G104_Southeast',
                                'Bukovsky_G104_Southwest',
                                'Bukovsky_G104_SPlains',
                                'Bukovsky_G104_SRockies',
                                'Alaska_G104'
                            ]
                        for mask in mask_list:
                            if mask == mask_list[0]:
                                env_var_mask_list = ("'"+job_env_dict['FIXevs']
                                                     +"/masks/"+mask+".nc, ")
                            elif mask == mask_list[-1]:
                                env_var_mask_list = (env_var_mask_list
                                                     +job_env_dict['FIXevs']
                                                     +"/masks/"+mask+".nc'")
                            else:
                                env_var_mask_list = (env_var_mask_list
                                                     +job_env_dict['FIXevs']
                                                     +"/masks/"+mask+".nc, ")
                        job_env_dict['mask_list'] = env_var_mask_list
                    if JOB_GROUP == 'generate_stats':
                        if verif_type_job == 'DailyAvg_TempAnom2m':
                            job_fhr_list = fhr_list.split(',')
                            for fhr in job_fhr_list:
                                if int(fhr) % 24 != 0:
                                    job_fhr_list.remove(fhr)
                                job_env_dict['fhr_list'] = ','.join(
                                    job_fhr_list
                                )
                    # Do file checks
                    check_model_files = True
                    if check_model_files:
                        model_files_exist, valid_date_fhr_list = (
                            gda_util.check_model_files(job_env_dict)
                        )
                        job_env_dict['fhr_list'] = (
                            '"'+','.join(valid_date_fhr_list)+'"'
                        )
                    if JOB_GROUP == 'assemble_data':
                        check_truth_files = False
                    elif JOB_GROUP in ['reformat_data', 'generate_stats']:
                        if verif_type == 'ptype' \
                                and JOB_GROUP == 'reformat_data':
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
                            in ['cmc', 'ecmwf', 'fnmoc',
                                'imd', 'jma', 'ukmet'] \
                            and verif_type_job == 'SpefHum':
                        write_job_cmds = False
                    elif job_env_dict['MODEL'] \
                            in ['jma'] \
                            and verif_type_job == 'RelHum':
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
