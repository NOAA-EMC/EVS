#!/usr/bin/env python3
'''
Name: global_ens_chem_plots_grid2obs_create_job_scripts.py
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This creates multiple independent job scripts. These
          jobs scripts contain all the necessary environment variables
          and commands to needed to run them.
Run By: scripts/plots/global_ens/exevs_global_ens_chem_grid2obs_plots.sh
'''

import sys
import os
import glob
import datetime
import itertools
import numpy as np
import subprocess
import copy
import global_ens_chem_util as gda_util

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
    'aeronet': {
        'AOD': {'vx_masks': ['GLOBAL', 'NAMERICA', 'SAMERICA', 'AFRICA',
                             'ASIA', 'CONUS', 'CONUS_Central',
                             'CONUS_East', 'CONUS_South', 'CONUS_West'],
                'fcst_var_dict': {'name': 'AOTK',
                                  'levels': ['L0']},
                'obs_var_dict': {'name': 'AOD',
                                 'levels': ['Z550']},
                'obs_name': 'AERONET_AOD'}
    },
    'airnow': {
        'PM25': {'vx_masks': ['GLOBAL', 'NAMERICA', 'SAMERICA', 'AFRICA',
                              'ASIA', 'CONUS', 'CONUS_Central',
                              'CONUS_East', 'CONUS_South', 'CONUS_West'],
                 'fcst_var_dict': {'name': 'PMTF',
                                   'levels': ['L0']},
                 'obs_var_dict': {'name': 'PM25',
                                  'levels': ['A1']},
                 'obs_name': 'AIRNOW_HOURLY_AQOBS'}
    }
}

################################################
#### condense_stats jobs
################################################
condense_stats_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
#### aeronet
for aeronet_job in list(condense_stats_jobs_dict['aeronet'].keys()):
    if aeronet_job == 'AOD':
        aeronet_job_line_types = ['SL1L2', 'CTC' ]
    else:
        aeronet_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['aeronet'][aeronet_job]['line_types'] = aeronet_job_line_types
#### airnow
for airnow_job in list(condense_stats_jobs_dict['airnow'].keys()):
    if airnow_job == 'PM25':
        airnow_job_line_types = ['SL1L2', 'CTC' ]
    else:
        airnow_job_line_types = ['SL1L2']
    condense_stats_jobs_dict['airnow'][airnow_job]['line_types'] = airnow_job_line_types
if JOB_GROUP == 'condense_stats':
    JOB_GROUP_dict = condense_stats_jobs_dict

################################################
#### filter_stats jobs
################################################
filter_stats_jobs_dict = copy.deepcopy(condense_stats_jobs_dict)
#### aeronet
for aeronet_job in list(filter_stats_jobs_dict['aeronet'].keys()):
    ## column of "DESC" values
    filter_stats_jobs_dict['aeronet'][aeronet_job]['grid'] = 'G004'
    filter_stats_jobs_dict['aeronet'][aeronet_job]['interps'] = ['NEAREST/1']
    aeronet_job_fcst_threshs = ['NA']
    aeronet_job_obs_threshs = ['NA']
    filter_stats_jobs_dict['aeronet'][aeronet_job]['fcst_var_dict']['threshs'] = (
        aeronet_job_fcst_threshs
    )
    filter_stats_jobs_dict['aeronet'][aeronet_job]['obs_var_dict']['threshs'] = (
        aeronet_job_obs_threshs
    )
    if aeronet_job in ['AOD']:
        ## Already defined above, only add line for variables not defined above
        ## filter_stats_jobs_dict['aeronet'][aeronet_job]['line_types'] = ['SL1L2']
        filter_stats_jobs_dict['aeronet'][f"{aeronet_job}_Thresh"] = copy.deepcopy(
            filter_stats_jobs_dict['aeronet'][aeronet_job]
        )
        filter_stats_jobs_dict['aeronet'][f"{aeronet_job}_Thresh"]['line_types'] = [
            'CTC'
        ]
        if aeronet_job == 'AOD':
            (filter_stats_jobs_dict['aeronet'][f"{aeronet_job}_Thresh"]\
             ['fcst_var_dict']['threshs']) = [
                 'ge0.1', 'ge0.2', 'ge0.4', 'ge0.6', 'ge0.8', 'ge1.0',
                 'ge1.5', 'ge2.0'
             ]
            (filter_stats_jobs_dict['aeronet'][f"{aeronet_job}_Thresh"]\
             ['obs_var_dict']['threshs']) = [
                 'ge0.1', 'ge0.2', 'ge0.4', 'ge0.6', 'ge0.8', 'ge1.0',
                 'ge1.5', 'ge2.0'
             ]
#### airnow
for airnow_job in list(filter_stats_jobs_dict['airnow'].keys()):
    filter_stats_jobs_dict['airnow'][airnow_job]['grid'] = 'G004'
    filter_stats_jobs_dict['airnow'][airnow_job]['interps'] = ['BILIN/4']
    airnow_job_fcst_threshs = ['NA']
    airnow_job_obs_threshs = ['NA']
    filter_stats_jobs_dict['airnow'][airnow_job]['fcst_var_dict']['threshs'] = (
        airnow_job_fcst_threshs
    )
    filter_stats_jobs_dict['airnow'][airnow_job]['obs_var_dict']['threshs'] = (
        airnow_job_obs_threshs
    )
    if airnow_job in ['PM25']:
        ## Already defined above, only add line for variables not defined above
        ## filter_stats_jobs_dict['airnow'][airnow_job]['line_types'] = ['SL1L2']
        filter_stats_jobs_dict['airnow'][f"{airnow_job}_Thresh"] = copy.deepcopy(
            filter_stats_jobs_dict['airnow'][airnow_job]
        )
        filter_stats_jobs_dict['airnow'][f"{airnow_job}_Thresh"]['line_types'] = [
            'CTC'
        ]
        if airnow_job == 'PM25':
            (filter_stats_jobs_dict['airnow'][f"{airnow_job}_Thresh"]\
             ['fcst_var_dict']['threshs']) = [
                 'gt5',  'gt10', 'gt15', 'gt20', 'gt25', 'gt30', 'gt35',
                 'gt40', 'gt45', 'gt50', 'gt55', 'gt60', 'gt65'
             ]
            (filter_stats_jobs_dict['airnow'][f"{airnow_job}_Thresh"]\
             ['obs_var_dict']['threshs']) = [
                 'gt5',  'gt10', 'gt15', 'gt20', 'gt25', 'gt30', 'gt35',
                 'gt40', 'gt45', 'gt50', 'gt55', 'gt60', 'gt65'
             ]
if JOB_GROUP == 'filter_stats':
    JOB_GROUP_dict = filter_stats_jobs_dict

################################################
#### make_plots jobs
################################################
make_plots_jobs_dict = copy.deepcopy(filter_stats_jobs_dict)
#### aeronet
for aeronet_job in list(make_plots_jobs_dict['aeronet'].keys()):
    del make_plots_jobs_dict['aeronet'][aeronet_job]['line_types']
    if aeronet_job in ['AOD']:
        aeronet_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
        make_plots_jobs_dict['aeronet'][aeronet_job+'_FBAR_OBAR'] = copy.deepcopy(
            make_plots_jobs_dict['aeronet'][aeronet_job]
        )
        make_plots_jobs_dict['aeronet'][aeronet_job+'_FBAR_OBAR']['line_type_stats']=[
            'SL1L2/FBAR_OBAR'
        ]
        make_plots_jobs_dict['aeronet'][aeronet_job+'_FBAR_OBAR']['vx_masks']=[
            'GLOBAL', 'NAMERICA', 'SAMERICA', 'AFRICA', 'ASIA',
            'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 'CONUS_South'
        ]
        make_plots_jobs_dict['aeronet'][aeronet_job+'_FBAR_OBAR']['plots'] = [
            'time_series', 'lead_average', 'threshold_average'
        ]
    elif aeronet_job in ['AOD_Thresh']:
        aeronet_job_line_type_stats = ['CTC/CSI']
    else:
        aeronet_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']

    make_plots_jobs_dict['aeronet'][aeronet_job]['line_type_stats'] = (
        aeronet_job_line_type_stats
    )

    if aeronet_job in ['AOD']:
        aeronet_job_plots = ['time_series', 'lead_average', 'valid_hour_average']
    elif aeronet_job in ['AOD_Thresh']:
        aeronet_job_plots = ['time_series', 'lead_average', 'threshold_average']
    else:
        aeronet_job_plots = ['time_series', 'lead_average']
    make_plots_jobs_dict['aeronet'][aeronet_job]['plots'] = aeronet_job_plots

for aeronet_job in list(make_plots_jobs_dict['aeronet'].keys()):
    if aeronet_job in ['AOD']:
        make_plots_jobs_dict['aeronet'][f"{aeronet_job}_PerfDiag"] = copy.deepcopy(
             make_plots_jobs_dict['aeronet'][f"{aeronet_job}_Thresh"]
            )
        (make_plots_jobs_dict['aeronet'][f"{aeronet_job}_PerfDiag"]\
         ['line_type_stats']) = ['CTC/PERFDIAG']
        make_plots_jobs_dict['aeronet'][f"{aeronet_job}_PerfDiag"]['plots'] = [
            'performance_diagram'
        ]
#### airnow
for airnow_job in list(make_plots_jobs_dict['airnow'].keys()):
    del make_plots_jobs_dict['airnow'][airnow_job]['line_types']
    if airnow_job in ['PM25']:
        airnow_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
        make_plots_jobs_dict['airnow'][airnow_job+'_FBAR_OBAR'] = copy.deepcopy(
            make_plots_jobs_dict['airnow'][airnow_job]
        )
        make_plots_jobs_dict['airnow'][airnow_job+'_FBAR_OBAR']['line_type_stats']=[
            'SL1L2/FBAR_OBAR'
        ]
        make_plots_jobs_dict['airnow'][airnow_job+'_FBAR_OBAR']['vx_masks']=[
            'GLOBAL', 'NAMERICA', 'SAMERICA', 'AFRICA', 'ASIA',
            'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 'CONUS_South'
        ]
        make_plots_jobs_dict['airnow'][airnow_job+'_FBAR_OBAR']['plots'] = [
            'time_series', 'lead_average', 'threshold_average'
        ]
    elif airnow_job in ['PM25_Thresh']:
        airnow_job_line_type_stats = ['CTC/CSI']
    else:
        airnow_job_line_type_stats = ['SL1L2/RMSE', 'SL1L2/ME']
    make_plots_jobs_dict['airnow'][airnow_job]['line_type_stats'] = (
        airnow_job_line_type_stats
    )

    if airnow_job in ['PM25']:
        airnow_job_plots = ['time_series', 'lead_average', 'valid_hour_average']
    elif airnow_job in ['PM25_Thresh']:
        airnow_job_plots = ['time_series', 'lead_average', 'threshold_average']
    else:
        airnow_job_plots = ['time_series', 'lead_average']
    make_plots_jobs_dict['airnow'][airnow_job]['plots'] = airnow_job_plots

for airnow_job in list(make_plots_jobs_dict['airnow'].keys()):
    if airnow_job in ['PM25']:
        make_plots_jobs_dict['airnow'][f"{airnow_job}_PerfDiag"] = copy.deepcopy(
            make_plots_jobs_dict['airnow'][f"{airnow_job}_Thresh"]
        )
        (make_plots_jobs_dict['airnow'][f"{airnow_job}_PerfDiag"]\
         ['line_type_stats']) = ['CTC/PERFDIAG']
        make_plots_jobs_dict['airnow'][f"{airnow_job}_PerfDiag"]['plots'] = [
            'performance_diagram'
        ]
if JOB_GROUP == 'make_plots':
    JOB_GROUP_dict = make_plots_jobs_dict

################################################
#### tar_images jobs
################################################
tar_images_jobs_dict = {
    'aeronet': {
        'search_base_dir': os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'plot_output', f"{RUN}.{end_date}",
                                        f"{VERIF_CASE}_aeronet",
                                        f"last{NDAYS}days")
    },
    'airnow': {
        'search_base_dir': os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                        'plot_output', f"{RUN}.{end_date}",
                                        f"{VERIF_CASE}_airnow",
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
                    gda_util.python_command('global_ens_chem_plots.py',[])
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
                    run_global_ens_chem_plots = ['global_ens_chem_plots.py']
                    if evs_run_mode == 'production' and \
                            verif_type in ['aeronet', 'airnow'] and \
                            job_env_dict['plot'] in \
                            ['lead_average', 'lead_by_level',
                             'lead_by_date']:
                        run_global_ens_chem_plots.append(
                            'global_ens_chem_plots_production_tof120.py'
                        )
                    for run_global_ens_chem_plot in run_global_ens_chem_plots:
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
                            gda_util.python_command(run_global_ens_chem_plot,
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
                    gda_util.python_command('global_ens_chem_plots.py', [])
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
