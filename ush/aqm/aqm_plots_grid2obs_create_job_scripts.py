#!/usr/bin/env python3
'''
Name: aqm_plots_grid2obs_create_job_scripts.py
Original Author: Mallory Row (mallory.row@noaa.gov)
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This creates multiple independent job scripts. These
          jobs scripts contain all the necessary environment variables
          and commands to needed to run them.
Run By: scripts/plots/aqm/exevs_aqm_grid2obs_plots.sh
'''

import sys
import os
import glob
import datetime
import itertools
import numpy as np
import subprocess
import copy
import aqm_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMOUT = os.environ['COMOUT']
SENDCOM = os.environ['SENDCOM']
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
fig_name_label = os.environ['fig_name_label']
dir_name_label = fig_name_label
restart_mode = os.environ['restart_mode']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
PBS_NODEFILE = os.environ['PBS_NODEFILE']
VERIF_CASE_STEP = VERIF_CASE+'_'+STEP

njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                  'plot_job_scripts', JOB_GROUP)
gda_util.make_dir(JOB_GROUP_jobs_dir)

# Set environment variables to not write to individual job scripts
# as per request from NCO; these get set higher up in the job
dont_write_env_var_list = [
    'machine', 'evs_ver', 'HOMEevs', 'FIXevs', 'USHevs', 'DATA', 'COMROOT',
    'NET', 'RUN', 'VERIF_CASE', 'STEP', 'COMPONENT', 'COMIN', 'SENDCOM',
    'COMOUT', 'evs_run_mode', 'MET_ROOT', 'met_ver', 'NDAYS'
]

################################################
#### Base/Common Plotting Information
################################################
base_plot_jobs_info_dict = {
    'ozone': {
        'OZONE': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                               'CONUS_South', 'CONUS_West',
                               'Appalachia', 'CPlains', 'DeepSouth',
                               'GreatBasin', 'GreatLakes', 'Mezquital',
                               'MidAtlantic', 'NorthAtlantic',
                               'NPlains', 'NRockies', 'PacificNW',
                               'PacificSW', 'Prairie', 'Southeast',
                               'Southwest', 'SPlains', 'SRockies'],
                'fcst_var_dict': {'name': 'OZCON1',
                                  'levels': ['A1']},
                'obs_var_dict': {'name': 'OZONE',
                                 'levels': ['A1']},
                'obs_name': 'AIRNOW_HOURLY_AQOBS'}
    },
    'pm25': {
        'PM25': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                              'CONUS_South', 'CONUS_West',
                              'Appalachia', 'CPlains', 'DeepSouth',
                              'GreatBasin', 'GreatLakes', 'Mezquital',
                              'MidAtlantic', 'NorthAtlantic',
                              'NPlains', 'NRockies', 'PacificNW',
                              'PacificSW', 'Prairie', 'Southeast',
                              'Southwest', 'SPlains', 'SRockies'],
                 'fcst_var_dict': {'name': 'PMTF',
                                   'levels': ['L1']},
                 'obs_var_dict': {'name': 'PM25',
                                  'levels': ['A1']},
                 'obs_name': 'AIRNOW_HOURLY_AQOBS'}
    },
    'ozmax8': {
        'OZMAX8': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                'CONUS_South', 'CONUS_West',
                                'Appalachia', 'CPlains', 'DeepSouth',
                                'GreatBasin', 'GreatLakes', 'Mezquital',
                                'MidAtlantic', 'NorthAtlantic',
                                'NPlains', 'NRockies', 'PacificNW',
                                'PacificSW', 'Prairie', 'Southeast',
                                'Southwest', 'SPlains', 'SRockies'],
                 'fcst_var_dict': {'name': 'OZMAX8',
                                   'levels': ['L1']},
                 'obs_var_dict': {'name': 'OZONE-8HR',
                                  'levels': ['A8']},
                 'obs_name': 'AIRNOW_DAILY_V2'}
    },
    'pmave': {
        'PMAVE': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                               'CONUS_South', 'CONUS_West',
                               'Appalachia', 'CPlains', 'DeepSouth',
                               'GreatBasin', 'GreatLakes', 'Mezquital',
                               'MidAtlantic', 'NorthAtlantic',
                               'NPlains', 'NRockies', 'PacificNW',
                               'PacificSW', 'Prairie', 'Southeast',
                               'Southwest', 'SPlains', 'SRockies'],
                 'fcst_var_dict': {'name': 'PMAVE',
                                   'levels': ['A23']},
                 'obs_var_dict': {'name': 'PM2.5-24hr',
                                  'levels': ['A24']},
                 'obs_name': 'AIRNOW_DAILY_V2'}
    },
    'ozmax8_headline': {
        'OZMAX8': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                'CONUS_South', 'CONUS_West'],
                 'fcst_var_dict': {'name': 'OZMAX8',
                                   'levels': ['L1']},
                 'obs_var_dict': {'name': 'OZONE-8HR',
                                  'levels': ['A8']},
                 'obs_name': 'AIRNOW_DAILY_V2'}
    },
    'pmave_headline': {
        'PMAVE': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                               'CONUS_South', 'CONUS_West'],
                 'fcst_var_dict': {'name': 'PMAVE',
                                   'levels': ['A23']},
                 'obs_var_dict': {'name': 'PM2.5-24hr',
                                  'levels': ['A24']},
                 'obs_name': 'AIRNOW_DAILY_V2'}
    },
    'aeronetaod': {
        'AOD': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                             'CONUS_South', 'CONUS_West',
                             'Appalachia', 'CPlains', 'DeepSouth',
                             'GreatBasin', 'GreatLakes', 'Mezquital',
                             'MidAtlantic', 'NorthAtlantic',
                             'NPlains', 'NRockies', 'PacificNW',
                             'PacificSW', 'Prairie', 'Southeast',
                             'Southwest', 'SPlains', 'SRockies'],
                'fcst_var_dict': {'name': 'AOTK',
                                  'levels': ['L0']},
                'obs_var_dict': {'name': 'AOD',
                                 'levels': ['Z550']},
                'obs_name': 'AERONET_AOD'}
    }
}

################################################
#### condense_stats jobs
################################################
condense_stats_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
#### ozone
for ozone_job in list(condense_stats_jobs_dict['ozone'].keys()):
    if ozone_job == 'OZONE':
        ## ozone_job_line_types = ['SL1L2', 'CTC' ]
        ozone_job_line_types = ['SL1L2' ]
    else:
        ozone_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['ozone'][ozone_job]['line_types'] = ozone_job_line_types
#### pm25
for pm25_job in list(condense_stats_jobs_dict['pm25'].keys()):
    if pm25_job == 'PM25':
        ## pm25_job_line_types = ['SL1L2', 'CTC' ]
        pm25_job_line_types = ['SL1L2']
    else:
        pm25_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['pm25'][pm25_job]['line_types'] = pm25_job_line_types
#### ozmax8
for ozmax8_job in list(condense_stats_jobs_dict['ozmax8'].keys()):
    if ozmax8_job == 'OZMAX8':
        ozmax8_job_line_types = ['SL1L2', 'CTC' ]
    else:
        ozmax8_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['ozmax8'][ozmax8_job]['line_types'] = ozmax8_job_line_types
#### pmave
for pmave_job in list(condense_stats_jobs_dict['pmave'].keys()):
    if pmave_job == 'PMAVE':
        pmave_job_line_types = ['SL1L2', 'CTC' ]
    else:
        pmave_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['pmave'][pmave_job]['line_types'] = pmave_job_line_types
#### ozmax8_headline
for ozmax8_job in list(condense_stats_jobs_dict['ozmax8_headline'].keys()):
    if ozmax8_job == 'OZMAX8':
        ozmax8_job_line_types = [ 'CTC' ]
    else:
        ozmax8_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['ozmax8_headline'][ozmax8_job]['line_types'] = ozmax8_job_line_types
#### pmave_headline
for pmave_job in list(condense_stats_jobs_dict['pmave_headline'].keys()):
    if pmave_job == 'PMAVE':
        pmave_job_line_types = [ 'CTC' ]
    else:
        pmave_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['pmave_headline'][pmave_job]['line_types'] = pmave_job_line_types
#### aeronetaod
for aeronetaod_job in list(condense_stats_jobs_dict['aeronetaod'].keys()):
    if aeronetaod_job == 'AOD':
        ## aeronetaod_job_line_types = ['SL1L2', 'CTC' ]
        aeronetaod_job_line_types = ['SL1L2']
    else:
        aeronetaod_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['aeronetaod'][aeronetaod_job]['line_types'] = aeronetaod_job_line_types
if JOB_GROUP == 'condense_stats':
    JOB_GROUP_dict = condense_stats_jobs_dict

################################################
#### filter_stats jobs
################################################
filter_stats_jobs_dict = copy.deepcopy(condense_stats_jobs_dict)
#### ozone
for ozone_job in list(filter_stats_jobs_dict['ozone'].keys()):
    filter_stats_jobs_dict['ozone'][ozone_job]['grid'] = 'NA'
    filter_stats_jobs_dict['ozone'][ozone_job]['interps'] = ['BILIN/4']
    ozone_job_fcst_threshs = ['NA']
    ozone_job_obs_threshs = ['NA']
    filter_stats_jobs_dict['ozone'][ozone_job]['fcst_var_dict']['threshs'] = (
        ozone_job_fcst_threshs
    )
    filter_stats_jobs_dict['ozone'][ozone_job]['obs_var_dict']['threshs'] = (
        ozone_job_obs_threshs
    )
#### pm25
for pm25_job in list(filter_stats_jobs_dict['pm25'].keys()):
    filter_stats_jobs_dict['pm25'][pm25_job]['grid'] = 'NA'
    filter_stats_jobs_dict['pm25'][pm25_job]['interps'] = ['BILIN/4']
    pm25_job_fcst_threshs = ['NA']
    pm25_job_obs_threshs = ['NA']
    filter_stats_jobs_dict['pm25'][pm25_job]['fcst_var_dict']['threshs'] = (
        pm25_job_fcst_threshs
    )
    filter_stats_jobs_dict['pm25'][pm25_job]['obs_var_dict']['threshs'] = (
        pm25_job_obs_threshs
    )
#### ozmax8
for ozmax8_job in list(filter_stats_jobs_dict['ozmax8'].keys()):
    filter_stats_jobs_dict['ozmax8'][ozmax8_job]['grid'] = 'NA'
    filter_stats_jobs_dict['ozmax8'][ozmax8_job]['interps'] = ['BILIN/4']
    ozmax8_job_fcst_threshs = ['NA']
    ozmax8_job_obs_threshs = ['NA']
    filter_stats_jobs_dict['ozmax8'][ozmax8_job]['fcst_var_dict']['threshs'] = (
        ozmax8_job_fcst_threshs
    )
    filter_stats_jobs_dict['ozmax8'][ozmax8_job]['obs_var_dict']['threshs'] = (
        ozmax8_job_obs_threshs
    )
    if ozmax8_job in ['OZMAX8']:
        ## Already defined above, only add line for variables not defined above
        ## filter_stats_jobs_dict['ozmax8'][ozmax8_job]['line_types'] = ['SL1L2']
        filter_stats_jobs_dict['ozmax8'][f"{ozmax8_job}_Thresh"] = copy.deepcopy(
            filter_stats_jobs_dict['ozmax8'][ozmax8_job]
        )
        filter_stats_jobs_dict['ozmax8'][f"{ozmax8_job}_Thresh"]['line_types'] = [
            'CTC'
        ]
        if ozmax8_job == 'OZMAX8':
            (filter_stats_jobs_dict['ozmax8'][f"{ozmax8_job}_Thresh"]\
             ['fcst_var_dict']['threshs']) = [
                 'gt50',  'gt60', 'gt65', 'gt70', 'gt75', 'gt85'
             ]
            (filter_stats_jobs_dict['ozmax8'][f"{ozmax8_job}_Thresh"]\
             ['obs_var_dict']['threshs']) = [
                 'gt50',  'gt60', 'gt65', 'gt70', 'gt75', 'gt85'
             ]
#### pmave
for pmave_job in list(filter_stats_jobs_dict['pmave'].keys()):
    filter_stats_jobs_dict['pmave'][pmave_job]['grid'] = 'NA'
    filter_stats_jobs_dict['pmave'][pmave_job]['interps'] = ['BILIN/4']
    pmave_job_fcst_threshs = ['NA']
    pmave_job_obs_threshs = ['NA']
    filter_stats_jobs_dict['pmave'][pmave_job]['fcst_var_dict']['threshs'] = (
        pmave_job_fcst_threshs
    )
    filter_stats_jobs_dict['pmave'][pmave_job]['obs_var_dict']['threshs'] = (
        pmave_job_obs_threshs
    )
    if pmave_job in ['PMAVE']:
        ## Already defined above, only add line for variables not defined above
        ## filter_stats_jobs_dict['pmave'][pmave_job]['line_types'] = ['SL1L2']
        filter_stats_jobs_dict['pmave'][f"{pmave_job}_Thresh"] = copy.deepcopy(
            filter_stats_jobs_dict['pmave'][pmave_job]
        )
        filter_stats_jobs_dict['pmave'][f"{pmave_job}_Thresh"]['line_types'] = [
            'CTC'
        ]
        if pmave_job == 'PMAVE':
            (filter_stats_jobs_dict['pmave'][f"{pmave_job}_Thresh"]\
             ['fcst_var_dict']['threshs']) = [
                 'gt5',  'gt10', 'gt15', 'gt20', 'gt25', 'gt35',
                 'gt40', 'gt50', 'gt60'
             ]
            (filter_stats_jobs_dict['pmave'][f"{pmave_job}_Thresh"]\
             ['obs_var_dict']['threshs']) = [
                 'gt5',  'gt10', 'gt15', 'gt20', 'gt25', 'gt35',
                 'gt40', 'gt50', 'gt60'
             ]
#### ozmax8_headline
for ozmax8_job in list(filter_stats_jobs_dict['ozmax8_headline'].keys()):
    filter_stats_jobs_dict['ozmax8_headline'][ozmax8_job]['grid'] = 'NA'
    filter_stats_jobs_dict['ozmax8_headline'][ozmax8_job]['interps'] = ['BILIN/4']
    ozmax8_job_fcst_threshs = ['NA']
    ozmax8_job_obs_threshs = ['NA']
    filter_stats_jobs_dict['ozmax8_headline'][ozmax8_job]['fcst_var_dict']['threshs'] = (
        ozmax8_job_fcst_threshs
    )
    filter_stats_jobs_dict['ozmax8_headline'][ozmax8_job]['obs_var_dict']['threshs'] = (
        ozmax8_job_obs_threshs
    )
    if ozmax8_job in ['OZMAX8']:
        ## Already defined above, only add line for variables not defined above
        ## filter_stats_jobs_dict['ozmax8_headline'][ozmax8_job]['line_types'] = ['SL1L2']
        filter_stats_jobs_dict['ozmax8_headline'][f"{ozmax8_job}_Thresh"] = copy.deepcopy(
            filter_stats_jobs_dict['ozmax8_headline'][ozmax8_job]
        )
        filter_stats_jobs_dict['ozmax8_headline'][f"{ozmax8_job}_Thresh"]['line_types'] = [
            'CTC'
        ]
        if ozmax8_job == 'OZMAX8':
            (filter_stats_jobs_dict['ozmax8_headline'][f"{ozmax8_job}_Thresh"]\
             ['fcst_var_dict']['threshs']) = [ 'gt70' ]
            (filter_stats_jobs_dict['ozmax8_headline'][f"{ozmax8_job}_Thresh"]\
             ['obs_var_dict']['threshs']) = [ 'gt70' ]
#### pmave_headline
for pmave_job in list(filter_stats_jobs_dict['pmave'].keys()):
    filter_stats_jobs_dict['pmave_headline'][pmave_job]['grid'] = 'NA'
    filter_stats_jobs_dict['pmave_headline'][pmave_job]['interps'] = ['BILIN/4']
    pmave_job_fcst_threshs = ['NA']
    pmave_job_obs_threshs = ['NA']
    filter_stats_jobs_dict['pmave_headline'][pmave_job]['fcst_var_dict']['threshs'] = (
        pmave_job_fcst_threshs
    )
    filter_stats_jobs_dict['pmave_headline'][pmave_job]['obs_var_dict']['threshs'] = (
        pmave_job_obs_threshs
    )
    if pmave_job in ['PMAVE']:
        ## Already defined above, only add line for variables not defined above
        ## filter_stats_jobs_dict['pmave_headline'][pmave_job]['line_types'] = ['SL1L2']
        filter_stats_jobs_dict['pmave_headline'][f"{pmave_job}_Thresh"] = copy.deepcopy(
            filter_stats_jobs_dict['pmave_headline'][pmave_job]
        )
        filter_stats_jobs_dict['pmave_headline'][f"{pmave_job}_Thresh"]['line_types'] = [
            'CTC'
        ]
        if pmave_job == 'PMAVE':
            (filter_stats_jobs_dict['pmave_headline'][f"{pmave_job}_Thresh"]\
             ['fcst_var_dict']['threshs']) = [ 'gt35' ]
            (filter_stats_jobs_dict['pmave_headline'][f"{pmave_job}_Thresh"]\
             ['obs_var_dict']['threshs']) = [ 'gt35' ]
#### aeronetaod
for aeronetaod_job in list(filter_stats_jobs_dict['aeronetaod'].keys()):
    ## column of "DESC" values
    filter_stats_jobs_dict['aeronetaod'][aeronetaod_job]['grid'] = 'NA'
    filter_stats_jobs_dict['aeronetaod'][aeronetaod_job]['interps'] = ['NEAREST/1']
    aeronetaod_job_fcst_threshs = ['NA']
    aeronetaod_job_obs_threshs = ['NA']
    filter_stats_jobs_dict['aeronetaod'][aeronetaod_job]['fcst_var_dict']['threshs'] = (
        aeronetaod_job_fcst_threshs
    )
    filter_stats_jobs_dict['aeronetaod'][aeronetaod_job]['obs_var_dict']['threshs'] = (
        aeronetaod_job_obs_threshs
    )
    if aeronetaod_job in ['AOD']:
        ## Already defined above, only add line for variables not defined above
        ## filter_stats_jobs_dict['aeronetaod'][aeronetaod_job]['line_types'] = ['SL1L2']
        filter_stats_jobs_dict['aeronetaod'][f"{aeronetaod_job}_Thresh"] = copy.deepcopy(
            filter_stats_jobs_dict['aeronetaod'][aeronetaod_job]
        )
        filter_stats_jobs_dict['aeronetaod'][f"{aeronetaod_job}_Thresh"]['line_types'] = [
            'CTC'
        ]
        if aeronetaod_job == 'AOD':
            (filter_stats_jobs_dict['aeronetaod'][f"{aeronetaod_job}_Thresh"]\
             ['fcst_var_dict']['threshs']) = [
                 'ge0.2', 'ge0.4', 'ge0.6', 'ge0.8', 'ge1.0',
                 'ge1.5', 'ge2.0'
             ]
            (filter_stats_jobs_dict['aeronetaod'][f"{aeronetaod_job}_Thresh"]\
             ['obs_var_dict']['threshs']) = [
                 'ge0.2', 'ge0.4', 'ge0.6', 'ge0.8', 'ge1.0',
                 'ge1.5', 'ge2.0'
             ]
if JOB_GROUP == 'filter_stats':
    JOB_GROUP_dict = filter_stats_jobs_dict

################################################
#### make_plots jobs
################################################
make_plots_jobs_dict = copy.deepcopy(filter_stats_jobs_dict)
#### ozone
for ozone_job in list(make_plots_jobs_dict['ozone'].keys()):
    del make_plots_jobs_dict['ozone'][ozone_job]['line_types']
    if ozone_job in ['OZONE']:
        ozone_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
        make_plots_jobs_dict['ozone'][ozone_job+'_FBAR_OBAR'] = copy.deepcopy(
            make_plots_jobs_dict['ozone'][ozone_job]
        )
        make_plots_jobs_dict['ozone'][ozone_job+'_FBAR_OBAR']['line_type_stats']=[
            'SL1L2/FBAR_OBAR'
        ]
        make_plots_jobs_dict['ozone'][ozone_job+'_FBAR_OBAR']['vx_masks']=[
            'CONUS', 'CONUS_Central', 'CONUS_East', 'CONUS_South', 'CONUS_West',
            'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 'Mezquital',
            'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies', 'PacificNW',
            'PacificSW', 'Prairie', 'Southeast', 'Southwest', 'SPlains', 'SRockies'
        ]
        make_plots_jobs_dict['ozone'][ozone_job+'_FBAR_OBAR']['plots'] = [
            'time_series_fhr_mean'
        ]
    ## elif ozone_job in ['OZONE_Thresh']:
    ##     ozone_job_line_type_stats = ['CTC/CSI']
    else:
        ozone_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
    make_plots_jobs_dict['ozone'][ozone_job]['line_type_stats'] = (
        ozone_job_line_type_stats
    )

    if ozone_job in ['OZONE']:
        ozone_job_plots = ['time_series_fhr_mean', 'lead_average_vhr_mean', 'valid_hour_average_fhr_mean']
    ## elif ozone_job in ['OZONE_Thresh']:
    ##     ozone_job_plots = ['time_series', 'lead_average', 'threshold_average']
    else:
        ozone_job_plots = ['time_series', 'lead_average']
    make_plots_jobs_dict['ozone'][ozone_job]['plots'] = ozone_job_plots

#### pm25
for pm25_job in list(make_plots_jobs_dict['pm25'].keys()):
    del make_plots_jobs_dict['pm25'][pm25_job]['line_types']
    if pm25_job in ['PM25']:
        pm25_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
        make_plots_jobs_dict['pm25'][pm25_job+'_FBAR_OBAR'] = copy.deepcopy(
            make_plots_jobs_dict['pm25'][pm25_job]
        )
        make_plots_jobs_dict['pm25'][pm25_job+'_FBAR_OBAR']['line_type_stats']=[
            'SL1L2/FBAR_OBAR'
        ]
        make_plots_jobs_dict['pm25'][pm25_job+'_FBAR_OBAR']['vx_masks']=[
            'CONUS', 'CONUS_Central', 'CONUS_East', 'CONUS_South', 'CONUS_West',
            'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 'Mezquital',
            'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies', 'PacificNW',
            'PacificSW', 'Prairie', 'Southeast', 'Southwest', 'SPlains', 'SRockies'
        ]
        make_plots_jobs_dict['pm25'][pm25_job+'_FBAR_OBAR']['plots'] = [
            'time_series_fhr_mean'
        ]
    ## elif pm25_job in ['PM25_Thresh']:
    ##     pm25_job_line_type_stats = ['CTC/CSI']
    else:
        pm25_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
    make_plots_jobs_dict['pm25'][pm25_job]['line_type_stats'] = (
        pm25_job_line_type_stats
    )

    if pm25_job in ['PM25']:
        pm25_job_plots = ['time_series_fhr_mean', 'lead_average_vhr_mean', 'valid_hour_average_fhr_mean']
    ## elif pm25_job in ['PM25_Thresh']:
    ##     pm25_job_plots = ['time_series', 'lead_average', 'threshold_average']
    else:
        pm25_job_plots = ['time_series', 'lead_average']
    make_plots_jobs_dict['pm25'][pm25_job]['plots'] = pm25_job_plots

#### ozmax8
for ozmax8_job in list(make_plots_jobs_dict['ozmax8'].keys()):
    del make_plots_jobs_dict['ozmax8'][ozmax8_job]['line_types']
    if ozmax8_job in ['OZMAX8']:
        ozmax8_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
        make_plots_jobs_dict['ozmax8'][ozmax8_job+'_FBAR_OBAR'] = copy.deepcopy(
            make_plots_jobs_dict['ozmax8'][ozmax8_job]
        )
        make_plots_jobs_dict['ozmax8'][ozmax8_job+'_FBAR_OBAR']['line_type_stats']=[
            'SL1L2/FBAR_OBAR'
        ]
        make_plots_jobs_dict['ozmax8'][ozmax8_job+'_FBAR_OBAR']['vx_masks']=[
            'CONUS', 'CONUS_Central', 'CONUS_East', 'CONUS_South', 'CONUS_West',
            'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 'Mezquital',
            'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies', 'PacificNW',
            'PacificSW', 'Prairie', 'Southeast', 'Southwest', 'SPlains', 'SRockies'
        ]
        make_plots_jobs_dict['ozmax8'][ozmax8_job+'_FBAR_OBAR']['plots'] = [
            'time_series'
        ]
    elif ozmax8_job in ['OZMAX8_Thresh']:
        ozmax8_job_line_type_stats = ['CTC/CSI']
    else:
        ozmax8_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
    make_plots_jobs_dict['ozmax8'][ozmax8_job]['line_type_stats'] = (
        ozmax8_job_line_type_stats
    )

    if ozmax8_job in ['OZMAX8']:
        ozmax8_job_plots = ['time_series', 'lead_average']
    elif ozmax8_job in ['OZMAX8_Thresh']:
        ozmax8_job_plots = ['time_series', 'lead_average', 'threshold_average']
    else:
        ozmax8_job_plots = ['time_series', 'lead_average']
    make_plots_jobs_dict['ozmax8'][ozmax8_job]['plots'] = ozmax8_job_plots

for ozmax8_job in list(make_plots_jobs_dict['ozmax8'].keys()):
    if ozmax8_job in ['OZMAX8']:
        make_plots_jobs_dict['ozmax8'][f"{ozmax8_job}_PerfDiag"] = copy.deepcopy(
            make_plots_jobs_dict['ozmax8'][f"{ozmax8_job}_Thresh"]
        )
        (make_plots_jobs_dict['ozmax8'][f"{ozmax8_job}_PerfDiag"]\
         ['line_type_stats']) = ['CTC/PERFDIAG']
        make_plots_jobs_dict['ozmax8'][f"{ozmax8_job}_PerfDiag"]['plots'] = [
            'performance_diagram'
        ]
#### pmave
for pmave_job in list(make_plots_jobs_dict['pmave'].keys()):
    del make_plots_jobs_dict['pmave'][pmave_job]['line_types']
    if pmave_job in ['PMAVE']:
        pmave_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
        make_plots_jobs_dict['pmave'][pmave_job+'_FBAR_OBAR'] = copy.deepcopy(
            make_plots_jobs_dict['pmave'][pmave_job]
        )
        make_plots_jobs_dict['pmave'][pmave_job+'_FBAR_OBAR']['line_type_stats']=[
            'SL1L2/FBAR_OBAR'
        ]
        make_plots_jobs_dict['pmave'][pmave_job+'_FBAR_OBAR']['vx_masks']=[
            'CONUS', 'CONUS_Central', 'CONUS_East', 'CONUS_South', 'CONUS_West',
            'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 'Mezquital',
            'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies', 'PacificNW',
            'PacificSW', 'Prairie', 'Southeast', 'Southwest', 'SPlains', 'SRockies'
        ]
        make_plots_jobs_dict['pmave'][pmave_job+'_FBAR_OBAR']['plots'] = [
            'time_series'
        ]
    elif pmave_job in ['PMAVE_Thresh']:
        pmave_job_line_type_stats = ['CTC/CSI']
    else:
        pmave_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
    make_plots_jobs_dict['pmave'][pmave_job]['line_type_stats'] = (
        pmave_job_line_type_stats
    )

    if pmave_job in ['PMAVE']:
        pmave_job_plots = ['time_series', 'lead_average']
    elif pmave_job in ['PMAVE_Thresh']:
        pmave_job_plots = ['time_series', 'lead_average', 'threshold_average']
    else:
        pmave_job_plots = ['time_series', 'lead_average']
    make_plots_jobs_dict['pmave'][pmave_job]['plots'] = pmave_job_plots

for pmave_job in list(make_plots_jobs_dict['pmave'].keys()):
    if pmave_job in ['PMAVE']:
        make_plots_jobs_dict['pmave'][f"{pmave_job}_PerfDiag"] = copy.deepcopy(
            make_plots_jobs_dict['pmave'][f"{pmave_job}_Thresh"]
        )
        (make_plots_jobs_dict['pmave'][f"{pmave_job}_PerfDiag"]\
         ['line_type_stats']) = ['CTC/PERFDIAG']
        make_plots_jobs_dict['pmave'][f"{pmave_job}_PerfDiag"]['plots'] = [
            'performance_diagram'
        ]
#### ozmax8_headline
for ozmax8_job in list(make_plots_jobs_dict['ozmax8_headline'].keys()):
    del make_plots_jobs_dict['ozmax8_headline'][ozmax8_job]['line_types']
    if ozmax8_job in ['OZMAX8_Thresh']:
        ozmax8_job_line_type_stats = ['CTC/CSI']
    else:
        ozmax8_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
    make_plots_jobs_dict['ozmax8_headline'][ozmax8_job]['line_type_stats'] = (
        ozmax8_job_line_type_stats
    )

    if ozmax8_job in ['OZMAX8_Thresh']:
        ozmax8_job_plots = ['time_series']
    else:
        ozmax8_job_plots = ['time_series_fhr_mean']
    make_plots_jobs_dict['ozmax8_headline'][ozmax8_job]['plots'] = ozmax8_job_plots

#### pmave
for pmave_job in list(make_plots_jobs_dict['pmave_headline'].keys()):
    del make_plots_jobs_dict['pmave_headline'][pmave_job]['line_types']
    if pmave_job in ['PMAVE_Thresh']:
        pmave_job_line_type_stats = ['CTC/CSI']
    else:
        pmave_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
    make_plots_jobs_dict['pmave_headline'][pmave_job]['line_type_stats'] = (
        pmave_job_line_type_stats
    )

    if pmave_job in ['PMAVE_Thresh']:
        pmave_job_plots = ['time_series']
    else:
        pmave_job_plots = ['time_series_fhr_mean']
    make_plots_jobs_dict['pmave_headline'][pmave_job]['plots'] = pmave_job_plots

#### aeronetaod
for aeronetaod_job in list(make_plots_jobs_dict['aeronetaod'].keys()):
    del make_plots_jobs_dict['aeronetaod'][aeronetaod_job]['line_types']
    if aeronetaod_job in ['AOD']:
        aeronetaod_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
        make_plots_jobs_dict['aeronetaod'][aeronetaod_job+'_FBAR_OBAR'] = copy.deepcopy(
            make_plots_jobs_dict['aeronetaod'][aeronetaod_job]
        )
        make_plots_jobs_dict['aeronetaod'][aeronetaod_job+'_FBAR_OBAR']['line_type_stats']=[
            'SL1L2/FBAR_OBAR'
        ]
        make_plots_jobs_dict['aeronetaod'][aeronetaod_job+'_FBAR_OBAR']['vx_masks']=[
            'CONUS', 'CONUS_Central', 'CONUS_East', 'CONUS_South', 'CONUS_West',
            'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 'Mezquital',
            'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies', 'PacificNW',
            'PacificSW', 'Prairie', 'Southeast', 'Southwest', 'SPlains', 'SRockies'
        ]
        make_plots_jobs_dict['aeronetaod'][aeronetaod_job+'_FBAR_OBAR']['plots'] = [
            'time_series_fhr_mean'
        ]
    elif aeronetaod_job in ['AOD_Thresh']:
        aeronetaod_job_line_type_stats = ['CTC/CSI']
    else:
        aeronetaod_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']

    make_plots_jobs_dict['aeronetaod'][aeronetaod_job]['line_type_stats'] = (
        aeronetaod_job_line_type_stats
    )

    if aeronetaod_job in ['AOD']:
        aeronetaod_job_plots = ['time_series_fhr_mean', 'lead_average_vhr_mean', 'valid_hour_average_fhr_mean']
    elif aeronetaod_job in ['AOD_Thresh']:
        aeronetaod_job_plots = ['time_series_fhr_mean', 'lead_average_vhr_mean', 'threshold_average']
    else:
        aeronetaod_job_plots = ['time_series', 'lead_average']
    make_plots_jobs_dict['aeronetaod'][aeronetaod_job]['plots'] = aeronetaod_job_plots

for aeronetaod_job in list(make_plots_jobs_dict['aeronetaod'].keys()):
    if aeronetaod_job in ['AOD']:
        make_plots_jobs_dict['aeronetaod'][f"{aeronetaod_job}_PerfDiag"] = copy.deepcopy(
             make_plots_jobs_dict['aeronetaod'][f"{aeronetaod_job}_Thresh"]
            )
        (make_plots_jobs_dict['aeronetaod'][f"{aeronetaod_job}_PerfDiag"]\
         ['line_type_stats']) = ['CTC/PERFDIAG']
        make_plots_jobs_dict['aeronetaod'][f"{aeronetaod_job}_PerfDiag"]['plots'] = [
            'performance_diagram'
        ]
if JOB_GROUP == 'make_plots':
    JOB_GROUP_dict = make_plots_jobs_dict

################################################
#### tar_images jobs
################################################
if SENDCOM == 'YES':
    search_dir = os.path.join(COMOUT, f"{VERIF_CASE}_VERIF_TYPE",
                              f"{dir_name_label}")
else:
    search_dir = os.path.join(DATA, f"{VERIF_CASE}_{STEP}", 'plot_output',
                              f"{RUN}.{end_date}", f"{VERIF_CASE}_VERIF_TYPE",
                              f"{dir_name_label}")
tar_images_jobs_dict = {
    'ozone': {'search_base_dir': search_dir},
    'pm25': {'search_base_dir': search_dir},
    'ozmax8': {'search_base_dir': search_dir},
    'pmave': {'search_base_dir': search_dir},
    'ozmax8_headline': {'search_base_dir': search_dir},
    'pmave_headline': {'search_base_dir': search_dir},
    'aeronetaod': {'search_base_dir': search_dir}
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
        job_env_dict = gda_util.initialize_job_env_dict(
            verif_type, JOB_GROUP,
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        job_env_dict['start_date'] = start_date
        job_env_dict['end_date'] = end_date
        job_env_dict['NDAYS'] = NDAYS
        job_env_dict['fig_name_label'] = fig_name_label
        job_env_dict['restart_mode'] = restart_mode
        job_env_dict['date_type'] = 'VALID'
        if JOB_GROUP in ['make_plots']:
            init_hr_start = int(job_env_dict['init_hr_start'])
            init_hr_end = int(job_env_dict['init_hr_end'])
            init_hr_inc = int(job_env_dict['init_hr_inc'])
            init_hrs = list(range(init_hr_start,
                                   init_hr_end+init_hr_inc,
                                   init_hr_inc))
        if JOB_GROUP in ['filter_stats', 'make_plots']:
            valid_hr_start = int(job_env_dict['valid_hr_start'])
            valid_hr_end = int(job_env_dict['valid_hr_end'])
            valid_hr_inc = int(job_env_dict['valid_hr_inc'])
            valid_hrs = list(range(valid_hr_start,
                                   valid_hr_end+valid_hr_inc,
                                   valid_hr_inc))
            fday_start = int(job_env_dict['fday_start'])
            fday_end = int(job_env_dict['fday_end'])
            fday_inc = int(job_env_dict['fday_inc'])
            fdays = list(range(fday_start,
                                   fday_end+fday_inc,
                                   fday_inc))
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
                verif_type_plot_jobs_dict['search_base_dir'].replace(
                    'VERIF_TYPE', verif_type
                    )    
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
                # Set up output directories
                njobs+=1
                job_env_dict['job_id'] = 'job'+str(njobs)
                job_work_dir, job_DATA_dir, job_COMOUT_dir = (
                    gda_util.get_plot_job_dirs(DATA, COMOUT, JOB_GROUP,
                                               job_env_dict)
                )
                job_env_dict['job_work_dir'] = job_work_dir
                job_env_dict['job_DATA_dir'] = job_DATA_dir
                job_env_dict['job_COMOUT_dir'] = job_COMOUT_dir
                if SENDCOM == 'YES':
                    gda_util.make_dir(job_env_dict['job_COMOUT_dir'])
                else:
                    gda_util.make_dir(job_env_dict['job_DATA_dir'])
                write_job_cmds = True
                if restart_mode == 'YES':    # Check plot files
                    plot_files_exist = gda_util.check_plot_files(
                        job_env_dict
                    )
                    if plot_files_exist:
                        write_job_cmds = False
                # Create job file
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
                    if name not in dont_write_env_var_list:
                        job.write('export '+name+'="'+value+'"\n')
                job.write('\n')
                if write_job_cmds:
                    gda_util.make_dir(job_env_dict['job_work_dir'])
                    job.write(
                        gda_util.python_command('aqm_plots.py',[])
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

                plot_fdays_loop = fdays

                plot_init_hrs_loop = init_hrs

                if job_env_dict['plot'] in  [ 'valid_hour_average',
                                              'valid_hour_average_fhr_mean',
                                              'lead_average_vhr_mean',
                                              'time_series_fhr_mean' ]:
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
                plot_fcst_levels_loop = (
                    verif_type_plot_jobs_dict[verif_type_job]\
                    ['fcst_var_dict']['levels']
                )
                if job_env_dict['plot'] in  [ 'valid_hour_average_fhr_mean',
                                              'time_series_fhr_mean' ]:
                    for plot_loop_info in list(
                        itertools.product(plot_valid_hrs_loop,
                                          plot_fcst_threshs_loop,
                                          plot_fcst_levels_loop,
                                          plot_fdays_loop,
                                          plot_init_hrs_loop)
                    ):
                        job_env_dict['fday_start'] = str(plot_loop_info[3])
                        job_env_dict['fday_end']   = str(plot_loop_info[3])
                        job_env_dict['fday_inc']   = str(fday_inc)
    
                        job_env_dict['init_hr_start'] = str(plot_loop_info[4]).zfill(2)
                        job_env_dict['init_hr_end']   = str(plot_loop_info[4]).zfill(2)
                        job_env_dict['init_hr_inc']   = str(init_hr_inc)
    
                        if job_env_dict['plot'] in  [ 'valid_hour_average_fhr_mean',
                                                      'time_series_fhr_mean' ]:
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
                        job_env_dict['fcst_var_level_list'] = plot_loop_info[2]
                        job_env_dict['obs_var_level_list'] = (
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['obs_var_dict']['levels']\
                            [verif_type_plot_jobs_dict[verif_type_job]\
                            ['fcst_var_dict']['levels']\
                            .index(plot_loop_info[2])]
                        )
                        run_aqm_plots = ['plots']
                        ##
                        for run_aqm_plot in run_aqm_plots:
                            # Set up output directories
                            njobs+=1
                            job_env_dict['job_id'] = 'job'+str(njobs)
                            job_work_dir, job_DATA_dir, job_COMOUT_dir = (
                                gda_util.get_plot_job_dirs(DATA, COMOUT, JOB_GROUP,
                                                           job_env_dict)
                            )
                            job_env_dict['job_work_dir'] = job_work_dir
                            job_env_dict['job_DATA_dir'] = job_DATA_dir
                            job_env_dict['job_COMOUT_dir'] = job_COMOUT_dir
                            if SENDCOM == 'YES':
                                gda_util.make_dir(job_env_dict['job_COMOUT_dir'])
                            else:
                                gda_util.make_dir(job_env_dict['job_DATA_dir'])
                            write_job_cmds = True
                            if restart_mode == 'YES':    # Check plot files
                                plot_files_exist = gda_util.check_plot_files(
                                    job_env_dict
                                )
                                if plot_files_exist:
                                    write_job_cmds = False
                            # Create job file
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
                                if name not in dont_write_env_var_list:
                                    job.write('export '+name+'="'+value+'"\n')
                            job.write('\n')
                            if run_aqm_plot == 'plots_tof72':
                                fhrs_tof72= []
                                for fhr in job_env_dict['fhr_list'].split(', '):
                                    if int(fhr) <= 72:
                                        fhrs_tof72.append(str(fhr))
                                job.write(
                                    'export fhr_list="'
                                    +', '.join(fhrs_tof72)+'"\n'
                                )
                            if write_job_cmds:
                                job.write(
                                    gda_util.python_command('aqm_plots.py',
                                                            [])+'\n'
                                )
                                job.write('export err=$?; err_chk'+'\n')
                            job.close()
    
                elif job_env_dict['plot'] in  [ 'lead_average', 'lead_average_vhr_mean' ]:
                    for plot_loop_info in list(
                        itertools.product(plot_valid_hrs_loop,
                                          plot_fcst_threshs_loop,
                                          plot_fcst_levels_loop,
                                          plot_init_hrs_loop)
                    ):
                        job_env_dict['init_hr_start'] = str(plot_loop_info[3]).zfill(2)
                        job_env_dict['init_hr_end'] = str(plot_loop_info[3]).zfill(2)
                        job_env_dict['init_hr_inc'] = str(init_hr_inc)
    
                        if job_env_dict['plot'] == 'lead_average_vhr_mean':
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
                        job_env_dict['fcst_var_level_list'] = plot_loop_info[2]
                        job_env_dict['obs_var_level_list'] = (
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['obs_var_dict']['levels']\
                            [verif_type_plot_jobs_dict[verif_type_job]\
                            ['fcst_var_dict']['levels']\
                            .index(plot_loop_info[2])]
                        )
                        run_aqm_plots = ['plots']
                        for run_aqm_plot in run_aqm_plots:
                            # Set up output directories
                            njobs+=1
                            job_env_dict['job_id'] = 'job'+str(njobs)
                            job_work_dir, job_DATA_dir, job_COMOUT_dir = (
                                gda_util.get_plot_job_dirs(DATA, COMOUT, JOB_GROUP,
                                                           job_env_dict)
                            )
                            job_env_dict['job_work_dir'] = job_work_dir
                            job_env_dict['job_DATA_dir'] = job_DATA_dir
                            job_env_dict['job_COMOUT_dir'] = job_COMOUT_dir
                            if SENDCOM == 'YES':
                                gda_util.make_dir(job_env_dict['job_COMOUT_dir'])
                            else:
                                gda_util.make_dir(job_env_dict['job_DATA_dir'])
                            write_job_cmds = True
                            if restart_mode == 'YES':    # Check plot files
                                plot_files_exist = gda_util.check_plot_files(
                                    job_env_dict
                                )
                                if plot_files_exist:
                                    write_job_cmds = False
                            # Create job file
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
                                if name not in dont_write_env_var_list:
                                    job.write('export '+name+'="'+value+'"\n')
                            job.write('\n')
                            if run_aqm_plot == 'plots_tof72':
                                fhrs_tof72 = []
                                for fhr in job_env_dict['fhr_list'].split(', '):
                                    if int(fhr) <= 72:
                                        fhrs_tof72.append(str(fhr))
                                job.write(
                                    'export fhr_list="'
                                    +', '.join(fhrs_tof72)+'"\n'
                                )
                            if write_job_cmds:
                                job.write(
                                    gda_util.python_command('aqm_plots.py',
                                                            [])+'\n'
                                )
                                job.write('export err=$?; err_chk'+'\n')
                            job.close()
                else:
                    for plot_loop_info in list(
                        itertools.product(plot_valid_hrs_loop,
                                          plot_fcst_threshs_loop,
                                          plot_fcst_levels_loop,
                                          plot_fdays_loop,
                                          plot_init_hrs_loop)
                    ):
                        job_env_dict['fday_start'] = str(plot_loop_info[3])
                        job_env_dict['fday_end'] = str(plot_loop_info[3])
                        job_env_dict['fday_inc'] = str(fday_inc)
    
                        job_env_dict['init_hr_start'] = str(plot_loop_info[4]).zfill(2)
                        job_env_dict['init_hr_end'] = str(plot_loop_info[4]).zfill(2)
                        job_env_dict['init_hr_inc'] = str(init_hr_inc)
    
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
                        job_env_dict['fcst_var_level_list'] = plot_loop_info[2]
                        job_env_dict['obs_var_level_list'] = (
                            verif_type_plot_jobs_dict[verif_type_job]\
                            ['obs_var_dict']['levels']\
                            [verif_type_plot_jobs_dict[verif_type_job]\
                            ['fcst_var_dict']['levels']\
                            .index(plot_loop_info[2])]
                        )
                        run_aqm_plots = ['plots']
                        ##
                        for run_aqm_plot in run_aqm_plots:
                            # Set up output directories
                            njobs+=1
                            job_env_dict['job_id'] = 'job'+str(njobs)
                            job_work_dir, job_DATA_dir, job_COMOUT_dir = (
                                gda_util.get_plot_job_dirs(DATA, COMOUT, JOB_GROUP,
                                                           job_env_dict)
                            )
                            job_env_dict['job_work_dir'] = job_work_dir
                            job_env_dict['job_DATA_dir'] = job_DATA_dir
                            job_env_dict['job_COMOUT_dir'] = job_COMOUT_dir
                            if SENDCOM == 'YES':
                                gda_util.make_dir(job_env_dict['job_COMOUT_dir'])
                            else:
                                gda_util.make_dir(job_env_dict['job_DATA_dir'])
                            write_job_cmds = True
                            if restart_mode == 'YES':    # Check plot files
                                plot_files_exist = gda_util.check_plot_files(
                                    job_env_dict
                                )
                                if plot_files_exist:
                                    write_job_cmds = False
                            # Create job file
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
                                if name not in dont_write_env_var_list:
                                    job.write('export '+name+'="'+value+'"\n')
                            job.write('\n')
                            if run_aqm_plot == 'plots_tof72':
                                fhrs_tof72 = []
                                for fhr in job_env_dict['fhr_list'].split(', '):
                                    if int(fhr) <= 72:
                                        fhrs_tof72.append(str(fhr))
                                job.write(
                                    'export fhr_list="'
                                    +', '.join(fhrs_tof72)+'"\n'
                                )
                            if write_job_cmds:
                                job.write(
                                    gda_util.python_command('aqm_plots.py',
                                                            [])+'\n'
                                )
                                job.write('export err=$?; err_chk'+'\n')
                            job.close()
            elif JOB_GROUP == 'tar_images':
                # Set up output directories
                njobs+=1
                job_env_dict['job_id'] = 'job'+str(njobs)
                if SENDCOM == 'YES':
                   job_env_dict['job_COMOUT_dir'] = loop_info
                   job_env_dict['job_DATA_dir'] = loop_info.replace(
                       COMOUT,
                       os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                    'plot_output', f"{RUN}.{end_date}")
                   )
                else:
                   job_env_dict['job_DATA_dir'] = loop_info
                   job_env_dict['job_COMOUT_dir'] = loop_info.replace(
                       os.path.join(DATA, f"{VERIF_CASE}_{STEP}", 'plot_output',
                                    f"{RUN}.{end_date}"),
                       COMOUT
                   )
                job_env_dict['job_work_dir'] = (
                    job_env_dict['job_DATA_dir'].replace(
                        f"{RUN}.{end_date}",
                        f"job_work_dir/{job_env_dict['JOB_GROUP']}/"
                        +f"{job_env_dict['job_id']}/{RUN}.{end_date}"
                    )
                )
                if SENDCOM == 'YES':
                    gda_util.make_dir(job_env_dict['job_COMOUT_dir'])
                else:
                    gda_util.make_dir(job_env_dict['job_DATA_dir'])
                write_job_cmds = True
                if restart_mode == 'YES':    # Check plot files
                    plot_files_exist = gda_util.check_plot_files(
                        job_env_dict
                    )
                    if plot_files_exist:
                        write_job_cmds = False
                # Create job files
                job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/bash\n')
                job.write('set -x\n')
                job.write('\n')
                # Set any environment variables for special cases
                # Write environment variables
                for name, value in job_env_dict.items():
                    if name not in dont_write_env_var_list:
                        job.write('export '+name+'="'+value+'"\n')
                job.write('\n')
                if write_job_cmds:
                    job.write(
                        gda_util.python_command('aqm_plots.py', [])
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
