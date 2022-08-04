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
                                              'SL1L2/RMSE',],
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
                      'obs_name': 'ADPUPA',
                      'plots_list': 'time_series'},
    },
    'sea_ice': {},
    'sfc': {}
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
        print("ERROR: No job files created in "
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
