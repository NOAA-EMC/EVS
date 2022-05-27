'''
Program Name: global_det_atmos_stats_grid2grid_create_job_scripts.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This creates multiple independent job scripts. These
          jobs contain all the necessary environment variables
          and METplus commands to needed to run the specific
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
METPLUS_PATH = os.environ['METPLUS_PATH']
MET_ROOT = os.environ['MET_ROOT']
MET_bin_exec = os.environ['MET_bin_exec']
PARMevs = os.environ['PARMevs']
model_list = os.environ['model_list'].split(' ')
precip_file_accum_list = (os.environ \
                          [VERIF_CASE_STEP_abbrev+'_precip_file_accum_list'] \
                          .split(' '))
precip_var_list = (os.environ \
                   [VERIF_CASE_STEP_abbrev+'_precip_var_list'] \
                    .split(' '))

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
################################################
#### Reformat jobs
################################################
reformat_obs_jobs_dict = {
    'flux': {},
    'pres_levs': {},
    'means': {},
    'ozone': {},
    'precip': {'24hrCCPA': {'env': {},
                            'commands': [gda_util.metplus_command(
                                             'PCPCombine_obs24hrCCPA.conf'
                                         )]}},
    'sea_ice': {},
    'snow': {},
    'sst': {},
}
reformat_model_jobs_dict = {
    'flux': {},
    'pres_levs': {},
    'means': {},
    'ozone': {},
    'precip': {'24hrAccum': {'env': {'valid_hr': '12',
                                     'MODEL_template': ('{MODEL}.precip.'
                                                        +'{init?fmt=%Y%m%d%H}.'
                                                        +'f{lead?fmt=%HHH}')
                             },
                             'commands': [gda_util.metplus_command(
                                              'PCPCombine_fcstGLOBAL_DET_'
                                              +'24hrAccum_precip.conf'
                                          )]}},
    'sea_ice': {},
    'snow': {'24hrAccum_WaterEqv': {'env': {'valid_hr': '12',
                                            'MODEL_var': 'WEASD'},
                                    'commands': [gda_util.metplus_command(
                                                     'PCPCombine_fcstGLOBAL_'
                                                     +'DET_24hrAccum_snow.conf'
                                                 )]},
             '24hrAccum_Depth': {'env': {'valid_hr': '12',
                                         'MODEL_var': 'SNOD'},
                                 'commands': [gda_util.metplus_command(
                                                  'PCPCombine_fcstGLOBAL_'
                                                  +'DET_24hrAccum_snow.conf'
                                              )]}},
    'sst': {},
}

# Create reformat jobs directory
njobs = 0
reformat_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                 'reformat')
if not os.path.exists(reformat_jobs_dir):
    os.makedirs(reformat_jobs_dir)
for verif_type in VERIF_CASE_STEP_type_list:
    VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                   +verif_type)
    verif_type_reformat_obs_jobs_dict = (
        reformat_obs_jobs_dict[verif_type]
    )
    verif_type_reformat_model_jobs_dict = (
        reformat_model_jobs_dict[verif_type]
    )
    # Reformat obs jobs
    for verif_type_job in list(verif_type_reformat_obs_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, 'reformat',
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        # Add job specific environment variables
        for verif_type_job_env_var in \
                list(verif_type_reformat_obs_jobs_dict\
                     [verif_type_job]['env'].keys()):
            job_env_dict[verif_type_job_env_var] = (
                verif_type_reformat_obs_jobs_dict\
                [verif_type_job]['env'][verif_type_job_env_var]
            )
        verif_type_job_commands_list = (
            verif_type_reformat_obs_jobs_dict\
            [verif_type_job]['commands']
        )
        # Loop through and write job script for dates
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
            njobs+=1
            # Create job file
            job_file = os.path.join(reformat_jobs_dir, 'job'+str(njobs))
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
            for cmd in verif_type_job_commands_list:
                job.write(cmd+'\n')
            job.close()
            date_dt = date_dt + datetime.timedelta(days=1)
    # Reformat model jobs
    for verif_type_job in list(verif_type_reformat_model_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, 'reformat',
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        # Add job specific environment variables
        for verif_type_job_env_var in \
                list(verif_type_reformat_model_jobs_dict\
                     [verif_type_job]['env'].keys()):
            job_env_dict[verif_type_job_env_var] = (
                verif_type_reformat_model_jobs_dict\
                [verif_type_job]['env'][verif_type_job_env_var]
            )
        verif_type_job_commands_list = (
            verif_type_reformat_model_jobs_dict\
            [verif_type_job]['commands']
        )
        # Loop through and write job script for dates and models
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
            for model_idx in range(len(model_list)):
                job_env_dict['MODEL'] = model_list[model_idx]
                njobs+=1
                # Create job file
                job_file = os.path.join(reformat_jobs_dir, 'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/sh\n')
                job.write('set -x\n')
                job.write('\n')
                # Set any environment variables for special cases
                if verif_type == 'precip':
                    job_env_dict['MODEL_var'] = precip_var_list[model_idx]
                    if precip_file_accum_list[model_idx] == 'continuous':
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
                # Write environment variables
                for name, value in job_env_dict.items():
                    job.write('export '+name+'='+value+'\n')
                job.write('\n')
                # Write job commands
                for cmd in verif_type_job_commands_list:
                    job.write(cmd+'\n')
                job.close()
            date_dt = date_dt + datetime.timedelta(days=1)

################################################
#### Generate jobs
################################################
# Generate jobs information dictionary
generate_jobs_dict = {
    'flux': {},
    'pres_levs': {
        'GeoHeight': {'env': {'var1_name': 'HGT',
                              'var1_levels': "'P1000, P700, P500, P250'",
                              'fourier_beg': "'0, 0, 10, 4'",
                              'fourier_end': "'20, 3, 20, 9'",
                              'met_config_overrides': "'climo_mean = fcst;'"},
                      'commands': [gda_util.metplus_command(
                                       'GridStat_fcstGLOBAL_DET_'
                                       +'obsModelAnalysis_climoERAI_'
                                       +'StatOutput.conf'
                                   )]},
        'GeoHeightAnom': {'env': {'var1_name': 'HGT',
                                  'var1_levels': 'P500',
                                  'met_config_overrides': "'climo_mean = fcst;'"},
                          'commands': [gda_util.metplus_command(
                                           'GridStat_fcstGLOBAL_DET_'
                                           +'obsModelAnalysis_climoERAI_'
                                           +'NetCDFOutput.conf'
                                       ),
                                       gda_util.python_command(
                                           'global_det_atmos_stats_grid2grid'
                                           '_create_daily_avg_anomaly.py',
                                           ['HGT_P500']
                                       ),
                                       gda_util.metplus_command(
                                           'GridStat_fcstGLOBAL_DET_'
                                           +'obsModelAnalysis_DailyAvgAnom_'
                                           +'StatOutput.conf'
                                       )]},
        'PresSeaLevel': {'env': {'var1_name': 'PRMSL',
                                 'var1_levels': 'Z0',
                                 'fourier_beg': '',
                                 'fourier_end': '',
                                 'met_config_overrides': "'climo_mean = fcst;'"},
                         'commands': [gda_util.metplus_command(
                                          'GridStat_fcstGLOBAL_DET_'
                                          +'obsModelAnalysis_climoERAI_'
                                          +'StatOutput.conf'
                                      )]},
        'Temp': {'env': {'var1_name': 'TMP',
                         'var1_levels': ''"P850, P500, P250"'',
                         'fourier_beg': '',
                         'fourier_end': '',
                         'met_config_overrides': "'climo_mean = fcst;'"},
                 'commands': [gda_util.metplus_command(
                                  'GridStat_fcstGLOBAL_DET_'
                                  +'obsModelAnalysis_climoERAI_'
                                  +'StatOutput.conf'
                              )]},
        'Winds': {'env': {'var1_name': 'UGRD',
                          'var1_levels': ''"P850, P500, P250"'',
                          'var2_name': 'VGRD',
                          'var2_levels': ''"P850, P500, P250"'',
                          'fourier_beg': '',
                          'fourier_end': '',
                          'met_config_overrides': "'climo_mean = fcst;'"},
                  'commands': [gda_util.metplus_command(
                                   'GridStat_fcstGLOBAL_DET_'
                                   +'obsModelAnalysis_climoERAI_'
                                   +'WindsStatOutput.conf'
                               )]},
    },
    'means': {
        'CAPESfcBased': {'env': {},
                         'commands': []},
        'CloudWater': {'env': {},
                       'commands': []},
        'GeoHeightTropopause': {'env': {},
                                'commands': []},
        'PBLHeight': {'env': {},
                      'commands': []},
        'PrecipWater': {'env': {},
                        'commands': []},
        'PresSeaLevel': {'env': {},
                         'commands': []},
        'PresSfc': {'env': {},
                    'commands': []},
        'PresTropopause': {'env': {},
                           'commands': []},
        'RelHum2m': {'env': {},
                     'commands': []},
        'SnowWaterEqv': {'env': {},
                         'commands': []},
        'SpefHum2m': {'env': {},
                      'commands': []},
        'Temp2m': {'env': {},
                   'commands': []},
        'TempTropopause': {'env': {},
                           'commands': []},
        'TempSoilTopLayer': {'env': {},
                             'commands': []},
        'TotalOzone': {'env': {},
                      'commands': []},
        'UWind10m': {'env': {},
                     'commands': []},
        'VolSoilMoistTopLayer': {'env': {},
                                 'commands': []},
        'VWind10m': {'env': {},
                     'commands': []},
    },
    'ozone': {
        'Ozone': {'env': {},
                  'commands': []},
    },
    'precip': {
        '24hrCCPA_G211_mm': {'env': {},
                             'commands': []},
        '24hrCCPA_G211_in': {'env': {},
                             'commands': []},
        '24hrCCPA_G212_mm': {'env': {},
                             'commands': []},
        '24hrCCPA_G212_in': {'env': {},
                             'commands': []},
        '24hrCCPA_G218_mm': {'env': {},
                             'commands': []},
        '24hrCCPA_G218_in': {'env': {},
                             'commands': []},
        '24hrCCPA_Nbrhd_mm': {'env': {},
                              'commands': []},
        '24hrCCPA_Nbrhd_in': {'env': {},
                              'commands': []},
    },
    'sea_ice': {
        'Concentration': {'env': {},
                          'commands': []},
        'Thickness': {'env': {},
                      'commands': []},
        'Extent': {'env': {},
                   'commands': []},
        'Volume': {'env': {},
                   'commands': []},
    },
    'snow': {
        '24hrNOHRSC_WaterEqv_G211': {'env': {},
                                     'commands': []},
        '24hrNOHRSC_Depth_G211': {'env': {},
                                  'commands': []},
        '24hrNOHRSC_WaterEqv_G212': {'env': {},
                                     'commands': []},
        '24hrNOHRSC_Depth_G212': {'env': {},
                                  'commands': []},
        '24hrNOHRSC_WaterEqv_G218': {'env': {},
                                     'commands': []},
        '24hrNOHRSC_Depth_G218': {'env': {},
                                  'commands': []},
        '24hrNOHRSC_WaterEqv_Nbrhd': {'env': {},
                                      'commands': []},
        '24hrNOHRSC_Depth_Nbrhd': {'env': {},
                                   'commands': []},
    },
    'sst': {
        'TempSeaSfc': {'env': {},
                       'commands': []},
    },
}
# Create generate jobs directory
njobs = 0
generate_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                 'generate')
if not os.path.exists(generate_jobs_dir):
    os.makedirs(generate_jobs_dir)
for verif_type in VERIF_CASE_STEP_type_list:
    VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                   +verif_type)
    verif_type_generate_jobs_dict = generate_jobs_dict[verif_type]
    # Generate model jobs
    for verif_type_job in list(verif_type_generate_jobs_dict.keys()):
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, 'generate',
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        # Add job specific environment variables
        for verif_type_job_env_var in \
                list(verif_type_generate_jobs_dict\
                     [verif_type_job]['env'].keys()):
            job_env_dict[verif_type_job_env_var] = (
                verif_type_generate_jobs_dict\
                [verif_type_job]['env'][verif_type_job_env_var]
            )
        verif_type_job_commands_list = (
            verif_type_generate_jobs_dict\
            [verif_type_job]['commands']
        )
        # Loop through and write job script for dates and models
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
            for model_idx in range(len(model_list)):
                job_env_dict['MODEL'] = model_list[model_idx]
                njobs+=1
                # Create job file
                job_file = os.path.join(generate_jobs_dir, 'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/sh\n')
                job.write('set -x\n')
                job.write('\n')
                # Set any environment variables for special cases
                if verif_type == 'pres_levs':
                    job_env_dict['TRUTH'] = os.environ[
                        VERIF_CASE_STEP_abbrev_type+'_truth_name_list' 
                    ].split(' ')[model_idx]
                if verif_type == 'pres_levs' \
                        and verif_type_job == 'GeoHeightAnom':
                    job_env_dict['netCDF_ENDDATE'] = date_dt.strftime('%Y%m%d')
                    job_env_dict['netCDF_STARTDATE'] = (
                        (date_dt - datetime.timedelta(days=1))\
                        .strftime('%Y%m%d')
                    )
                # Write environment variables
                for name, value in job_env_dict.items():
                    job.write('export '+name+'='+value+'\n')
                job.write('\n')
                # Write job commands
                for cmd in verif_type_job_commands_list:
                    job.write(cmd+'\n')
                job.close()
            date_dt = date_dt + datetime.timedelta(days=1)

################################################
#### Gather jobs
################################################
# Gather jobs information dictionary
gather_jobs_dict = {'env': {},
                    'commands': [gda_util.metplus_command(
                                     'StatAnalysis_fcstGLOBAL_DET.conf'
                                 )]}
njobs = 0
gather_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                               'gather')
if not os.path.exists(gather_jobs_dir):
    os.makedirs(gather_jobs_dir)
# Initialize job environment dictionary
job_env_dict = gda_util.initalize_job_env_dict(
    verif_type, 'gather',
    VERIF_CASE_STEP_abbrev_type, verif_type_job
)
# Loop through and write job script for dates and models
date_dt = start_date_dt
while date_dt <= end_date_dt:
    job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
    for model_idx in range(len(model_list)):
        job_env_dict['MODEL'] = model_list[model_idx]
        njobs+=1
        # Create job file
        job_file = os.path.join(gather_jobs_dir, 'job'+str(njobs))
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
        for cmd in gather_jobs_dict['commands']:
            job.write(cmd+'\n')
            job.close()
    date_dt = date_dt + datetime.timedelta(days=1)

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    for group in ['reformat', 'generate', 'gather']:
        job_files = glob.glob(os.path.join(DATA, VERIF_CASE_STEP,
                                           'METplus_job_scripts', group,
                                           'job*'))
        njob_files = len(job_files)
        if njob_files == 0:
            print("ERROR: No job files created in "
                  +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                group))
        njob, iproc, node = 1, 0, 1
        while njob <= njob_files:
            job = 'job'+str(njob)
            if machine in ['HERA', 'ORION', 'S4', 'JET']:
                if iproc >= int(nproc):
                    poe_file.close()
                    iproc = 0
                    node+=1
            poe_filename = os.path.join(DATA, VERIF_CASE_STEP,
                                        'METplus_job_scripts',
                                        group, 'poe_jobs'+str(node))
            if iproc == 0:
                poe_file = open(poe_filename, 'w')
            iproc+=1
            if machine in ['HERA', 'ORION', 'S4', 'JET']:
                poe_file.write(
                    str(iproc-1)+' '
                    +os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                  group, job)+'\n'
                )
            else:
                poe_file.write(
                    os.path.join(DATA, VERIF_CASE_STEP, 'METplus_job_scripts',
                                 group, job)+'\n'
                )
            njob+=1
        poe_file.close()
        # If at final record and have not reached the
        # final processor then write echo's to
        # poe script for remaining processors
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
