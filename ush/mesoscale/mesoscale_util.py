#!/usr/bin/env python3
# =============================================================================
#
# NAME: mesoscale_util.py
# CONTRIBUTOR(S): RS, roshan.shrestha@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
#                 Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
#                 Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Various Utilities for EVS MESOSCALE Verification
# 
# =============================================================================

import os
import sys
import datetime
import numpy as np
import glob
import subprocess
from collections.abc import Iterable

def flatten(xs):
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x

def get_data_type(fname):
    data_type_dict = {
        'PrepBUFR': {
            'and':[''],
            'or':['prepbufr'],
            'not':[],
            'type': 'anl'
        },
        'SPC Outlook Area': {
            'and':[''],
            'or':['spc_otlk'],
            'not':[],
            'type': 'gen'
        },
        'NAM': {
            'and':[''],
            'or':['nam'],
            'not':[],
            'type': 'fcst'
        },
        'RAP': {
            'and':[''],
            'or':['rap'],
            'not':[],
            'type': 'fcst'
        },
    }
    for k in data_type_dict:
        if not data_type_dict[k]['and'] or not any(data_type_dict[k]['and']):
            data_type_dict[k]['and'] = ['']
        if not data_type_dict[k]['or'] or not any(data_type_dict[k]['or']):
            data_type_dict[k]['or'] = ['']
        if not data_type_dict[k]['not'] or not any(data_type_dict[k]['not']):
            data_type_dict[k]['not'] = []
    data_names = [
        k for k in data_type_dict
        if (
            all(map(fname.__contains__, data_type_dict[k]['and']))
            and any(map(fname.__contains__, data_type_dict[k]['or']))
            and not any(map(fname.__contains__, data_type_dict[k]['not']))
        )
    ]
    if len(data_names) == 1:
        data_name = data_names[0]
        return data_name, data_type_dict[data_name]['type']
    else:
        data_name = "Unknown"
        return data_name, 'unk'

def get_all_eval_periods(graphics):
    all_eval_periods = []
    for component in graphics:                                                               
        for verif_case in graphics[component]:                                                 
            for verif_type in graphics[component][verif_case]:                                     
                verif_type_dict = graphics[component][verif_case][verif_type]
                for models in verif_type_dict:
                    for plot_type in verif_type_dict[models]:           
                        all_eval_periods.append(
                            verif_type_dict[models][plot_type]['EVAL_PERIODS']
                        )
    return np.unique(np.hstack(all_eval_periods))

def get_fhr_start(vhour, acc, fhr_incr, min_ihour):
    fhr_start = (
        float(vhour) + float(min_ihour)
        + (
            float(fhr_incr)
            * np.ceil(
                (float(acc)-float(vhour)-float(min_ihour))
                / float(fhr_incr)
            )
        )
    )
    return int(fhr_start)

def run_shell_command(command, capture_output=False):
    """! Run shell command

        Args:
            command - list of argument entries (string)

        Returns:

    """
    print("Running "+' '.join(command))
    if any(mark in ' '.join(command) for mark in ['"', "'", '|', '*', '>']):
        run_command = subprocess.run(
            ' '.join(command), shell=True, capture_output=capture_output
        )
    else:
        run_command = subprocess.run(command, capture_output=capture_output)
    if run_command.returncode != 0:
        print("ERROR: "+''.join(run_command.args)+" gave return code "
              + str(run_command.returncode))
    else:
        if capture_output:
            return run_command.stdout.decode('utf-8')

def run_shell_commandc(command, capture_output=True):
    """! Run shell command

        Args:
            command - list of argument entries (string)

        Returns:

    """
    print("Running "+' '.join(command))
    if any(mark in ' '.join(command) for mark in ['"', "'", '|', '*', '>']):
        run_command = subprocess.run(
            ' '.join(command), shell=True, capture_output=capture_output
        )
    else:
        run_command = subprocess.run(command, capture_output=capture_output)
    if run_command.returncode != 0:
        print("ERROR: "+''.join(run_command.args)+" gave return code "
              + str(run_command.returncode))
    else:
        if capture_output:
            return run_command.stdout.decode('utf-8')

def format_thresh(thresh):
   """! Format threshold with letter and symbol options

      Args:
         thresh         - the threshold (string)

      Return:
         thresh_symbol  - threshold with symbols (string)
         thresh_letters - treshold with letters (string)
   """
   thresh_symbol = (
       thresh.replace('ge', '>=').replace('gt', '>')\
       .replace('eq', '==').replace('ne', '!=')\
       .replace('le', '<=').replace('lt', '<')
   )
   thresh_letter = (
       thresh.replace('>=', 'ge').replace('>', 'gt')\
       .replace('==', 'eq').replace('!=', 'ne')\
       .replace('<=', 'le').replace('<', 'lt')
   )
   return thresh_symbol, thresh_letter

def check_file(file_path):
    """! Check file exists and not zero size
         Args:
             file_path - full path to file (string)
         Returns:
             file_good - full call to METplus (boolean)
    """
    if os.path.exists(file_path):
        if os.path.getsize(file_path) > 0:
            file_good = True
        else:
            file_good = False
    else:
        file_good = False
    return file_good

def check_stat_files(job_dict):
    """! Check for MET .stat files

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             stat_files_exist - if .stat files
                                exist or not (boolean)
    """
    model_stat_file_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE']+'_'+job_dict['STEP'],
        'METplus_output', job_dict['RUN']+'.'+job_dict['DATE'],
        job_dict['MODEL'], job_dict['VERIF_CASE']
    )
    stat_file_list = glob.glob(os.path.join(model_stat_file_dir, '*.stat'))
    if len(stat_file_list) != 0:
        stat_files_exist = True
    else:
        stat_files_exist = False
    return stat_files_exist


def check_pstat_files(job_dict):
    """! Check for MET point_stat files

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             pstat_files_exist - if point_stat files
                                exist or not (boolean)
    """
    FHR_START = os.environ ['FHR_START']
    FHR_START2= str(FHR_START).zfill(2)
    model_stat_file_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE'],
        'METplus_output', job_dict['VERIF_TYPE'],'point_stat',
        job_dict['MODEL']+'.'+job_dict['VDATE']
    )

    pstat_file = os.path.join(
            model_stat_file_dir, 'point_stat_'+job_dict['MODEL']+
            '_'+job_dict['NEST']+'_'+job_dict['VAR_NAME']+
            '_OBS_*0000L_'+job_dict['VDATE']+'_'+job_dict['VHOUR']+'0000V.stat'
            )

    stat_file_list = glob.glob(pstat_file) 

    if len(stat_file_list) != 0:
        pstat_files_exist = True
    else:
        pstat_files_exist = False
    return pstat_files_exist



def format_filler(unfilled_file_format, valid_time_dt, init_time_dt,
                  forecast_hour, str_sub_dict):
    """! Creates a filled file path from a format
         Args:
             unfilled_file_format - file naming convention (string)
             valid_time_dt        - valid time (datetime)
             init_time_dt         - initialization time (datetime)
             forecast_hour        - forecast hour (string)
             str_sub_dict         - other strings to substitue (dictionary)
         Returns:
             filled_file_format - file_format filled in with verifying
                                  time information (string)
    """
    filled_file_format = '/'
    format_opt_list = ['lead', 'lead_shift', 'valid', 'valid_shift',
                       'init', 'init_shift', 'cycle']
    if len(list(str_sub_dict.keys())) != 0:
        format_opt_list = format_opt_list+list(str_sub_dict.keys())
    for filled_file_format_chunk in unfilled_file_format.split('/'):
        for format_opt in format_opt_list:
            nformat_opt = (
                filled_file_format_chunk.count('{'+format_opt+'?fmt=')
            )
            if nformat_opt > 0:
               format_opt_count = 1
               while format_opt_count <= nformat_opt:
                   if format_opt in ['lead_shift', 'valid_shift',
                                     'init_shift']:
                       shift = (filled_file_format_chunk \
                                .partition('shift=')[2] \
                                .partition('}')[0])
                       format_opt_count_fmt = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .rpartition('?')[0]
                       )
                   else:
                       format_opt_count_fmt = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0]
                       )
                   if format_opt == 'valid':
                       replace_format_opt_count = valid_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'lead':
                       if format_opt_count_fmt == '%1H':
                           if int(forecast_hour) < 10:
                               replace_format_opt_count = forecast_hour[1]
                           else:
                               replace_format_opt_count = forecast_hour
                       elif format_opt_count_fmt == '%2H':
                           replace_format_opt_count = forecast_hour.zfill(2)
                       elif format_opt_count_fmt == '%3H':
                           replace_format_opt_count = forecast_hour.zfill(3)
                       else:
                           replace_format_opt_count = forecast_hour
                   elif format_opt == 'init':
                       replace_format_opt_count = init_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'cycle':
                       replace_format_opt_count = init_time_dt.strftime(
                           format_opt_count_fmt
                       ) 
                   elif format_opt == 'lead_shift':
                       shift = (filled_file_format_chunk.partition('shift=')[2]\
                                .partition('}')[0])
                       forecast_hour_shift = str(int(forecast_hour)
                                                 + int(shift))
                       if format_opt_count_fmt == '%1H':
                           if int(forecast_hour_shift) < 10:
                               replace_format_opt_count = (
                                   forecast_hour_shift[1]
                               )
                           else:
                               replace_format_opt_count = forecast_hour_shift
                       elif format_opt_count_fmt == '%2H':
                           replace_format_opt_count = (
                               forecast_hour_shift.zfill(2)
                           )
                       elif format_opt_count_fmt == '%3H':
                           replace_format_opt_count = (
                               forecast_hour_shift.zfill(3)
                           )
                       else:
                           replace_format_opt_count = forecast_hour_shift
                   elif format_opt == 'init_shift':
                       shift = (filled_file_format_chunk.partition('shift=')[2]\
                                .partition('}')[0])
                       init_shift_time_dt = (
                           init_time_dt + datetime.timedelta(hours=int(shift))
                       )
                       replace_format_opt_count = init_shift_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'valid_shift':
                       shift = (filled_file_format_chunk.partition('shift=')[2]\
                                .partition('}')[0])
                       valid_shift_time_dt = (
                           valid_time_dt + datetime.timedelta(hours=int(shift))
                       )
                       replace_format_opt_count = valid_shift_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   else:
                       replace_format_opt_count = str_sub_dict[format_opt]
                   if format_opt in ['lead_shift', 'valid_shift', 'init_shift']:
                       filled_file_format_chunk = (
                           filled_file_format_chunk.replace(
                               '{'+format_opt+'?fmt='
                               +format_opt_count_fmt
                               +'?shift='+shift+'}',
                               replace_format_opt_count
                           )
                       )
                   else:
                       filled_file_format_chunk = (
                           filled_file_format_chunk.replace(
                               '{'+format_opt+'?fmt='
                               +format_opt_count_fmt+'}',
                               replace_format_opt_count
                           )
                       )
                   format_opt_count+=1
        filled_file_format = os.path.join(filled_file_format,
                                          filled_file_format_chunk)
    return filled_file_format

def initalize_job_env_dict():
    """! This initializes a dictionary of environment variables and their
         values to be set for the job pulling from environment variables
         already set previously
         Args:

         Returns:
             job_env_dict - dictionary of job settings
    """
    os.environ['MET_TMP_DIR'] = os.path.join(os.environ['DATA'], 'tmp')
    job_env_var_list = [
        'machine', 'evs_ver', 'HOMEevs', 'FIXevs', 'USHevs', 'DATA',
        'NET', 'RUN', 'VERIF_CASE', 'STEP', 'COMPONENT', 'evs_run_mode',
        'COMROOT', 'COMIN', 'COMOUT', 'COMOUTsmall', 'COMOUTfinal',
        'METPLUS_PATH','LOG_MET_OUTPUT_TO_METPLUS', 'METPLUS_VERBOSITY',
        'MET_ROOT', 'MET_bin_exec', 'MET_VERBOSITY',
        'MET_TMP_DIR', 'MODELNAME', 'JOB_GROUP'
    ]
    job_env_dict = {}
    for env_var in job_env_var_list:
        job_env_dict[env_var] = os.environ[env_var]
        if env_var in ['LOG_MET_OUTPUT_TO_METPLUS',
                       'METPLUS_VERBOSITY', 'MET_VERBOSITY']:
            job_env_dict[env_var.lower()] = os.environ[env_var]
    return job_env_dict

def metplus_command(conf_file_name):
    """! Write out full call to METplus
         Args:
             conf_file_name - METplus conf file name (string)
         Returns:
             metplus_cmd - full call to METplus (string)
    """
    run_metplus = os.path.join(os.environ['METPLUS_PATH'], 'ush',
                               'run_metplus.py')
    machine_conf = os.path.join(os.environ['PARMevs'], 'metplus_config',
                                'machine.conf')
    conf_file = os.path.join(os.environ['PARMevs'], 'metplus_config',
                             os.environ['COMPONENT'], os.environ['VERIF_CASE'],
                             os.environ['STEP'], conf_file_name)
    if not os.path.exists(conf_file):
        print("ERROR: "+conf_file+" DOES NOT EXIST")
        sys.exit(1)
    metplus_cmd = run_metplus+' -c '+machine_conf+' -c '+conf_file
    return metplus_cmd

def precip_check_obs_input_output_files(job_dict):
    """! Check precip observation input and output files
         in COMOUT and DATA
         Args:
             job_dict - job dictionary
         Returns:
             all_input_file_exist  - if all expected
                                     input files exist
                                     (boolean)
             input_files_list      - list of input files
                                     (strings)
             all_COMOUT_file_exist - if all expected
                                     output COMOUT files
                                     exist (boolean)
             COMOUT_files_list     - list of output COMOUT
                                     files (strings)
             DATA_files_list       - list of output DATA
                                     files (strings)
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hour_start'],
        '%Y%m%d%H'
    )
    # Expected input file
    input_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['job_name'] in ['24hrCCPA', '03hrCCPA', '01hrCCPA']:
            nccpa_files = (
                int(job_dict['accum'])
                /int(job_dict['ccpa_file_accum'])
            )
            n = 1
            while n <= nccpa_files:
                nccpa_file = os.path.join(
                    job_dict['DATA'], 'data', 'ccpa', 
                    f"ccpa.accum{job_dict['ccpa_file_accum'].zfill(2)}hr.v"
                    +(valid_date_dt
                      -datetime.timedelta(hours=(n-1)
                                                 *int(job_dict['ccpa_file_accum'])))\
                    .strftime('%Y%m%d%H')
                )
                input_files_list.append(nccpa_file)
                n+=1
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        if job_dict['obs'] == 'ccpa':
            input_files_list.append(
                os.path.join(job_dict['COMOUT'],
                             f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                             job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                             "pcp_combine_ccpa_accum"
                             +f"{job_dict['accum']}hr_valid"
                             +f"{valid_date_dt:%Y%m%d%H}.nc")
            )
        elif job_dict['obs'] == 'mrms':
            input_files_list.append(
                os.path.join(job_dict['DATA'], 'data', job_dict['obs'],
                             f"{job_dict['area']}_MultiSensor_QPE_"
                             +f"{job_dict['accum']}H_Pass2_00.00_"
                             +f"{valid_date_dt:%Y%m%d}-"
                             +f"{valid_date_dt:%H%M%S}.grib2")
            )
    input_files_exist_list = []
    for input_file in input_files_list:
        if check_file(input_file):
            input_files_exist_list.append(True)
        else:
            input_files_exist_list.append(False)
    if all(x == True for x in input_files_exist_list) \
            and len(input_files_exist_list) > 0:
        all_input_file_exist = True
    else:
        all_input_file_exist = False
    # Expected output files (in COMOUT and DATA)
    COMOUT_files_list = []
    DATA_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['job_name'] in ['24hrCCPA', '03hrCCPA', '01hrCCPA']:
            file_name = ("pcp_combine_ccpa_accum"
                         +f"{job_dict['accum']}hr_valid"
                         +f"{valid_date_dt:%Y%m%d%H}.nc")
            COMOUT_files_list.append(
                os.path.join(job_dict['COMOUT'],
                             f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                             job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                             file_name)
            )
            DATA_files_list.append(
                os.path.join(job_dict['DATA'],
                             f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                             job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                             file_name)
            ) 
    COMOUT_files_exist_list = []
    for COMOUT_file in COMOUT_files_list:
        if check_file(COMOUT_file):
            COMOUT_files_exist_list.append(True)
        else:
            COMOUT_files_exist_list.append(False)
    if all(x == True for x in COMOUT_files_exist_list) \
            and len(COMOUT_files_exist_list) > 0:
        all_COMOUT_file_exist = True
    else:
        all_COMOUT_file_exist = False
    return (all_input_file_exist, input_files_list, \
            all_COMOUT_file_exist, COMOUT_files_list,
            DATA_files_list)


def precip_check_model_input_output_files(job_dict):
    """! Check precip model input and output files
         in COMOUT and DATA
         Args:
             job_dict - job dictionary
         Returns:
             all_input_file_exist  - if all expected
                                     input files exist
                                     (boolean)
             input_files_list      - list of input files
                                     (strings)
             all_COMOUT_file_exist - if all expected
                                     output COMOUT files
                                     exist (boolean)
             COMOUT_files_list     - list of output COMOUT
                                     files (strings)
             DATA_files_list       - list of output DATA
                                     files (strings)
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hour_start'],
        '%Y%m%d%H'
    )
    init_date_dt = (valid_date_dt
                    - datetime.timedelta(hours=int(job_dict['fcst_hour'])))
    # Expected input file
    input_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['pcp_combine_method'] == 'SUBTRACT':
            for fhr in [job_dict['fcst_hour'],
                        str(int(job_dict['fcst_hour'])
                            - int(job_dict['accum']))]:
                input_files_list.append(
                    os.path.join(job_dict['DATA'], 'data',
                                 job_dict['MODELNAME'],
                                 f"{job_dict['MODELNAME']}."
                                 +f"{job_dict['area']}."
                                 +f"init{init_date_dt:%Y%m%d%H}."
                                 +f"f{fhr.zfill(3)}")
                )
        elif job_dict['pcp_combine_method'] == 'SUM':
            naccum_files = int(job_dict['accum'])/int(job_dict['input_accum'])
            n = 1 
            while n <= naccum_files:
                naccum_file = os.path.join(
                    job_dict['DATA'], 'data', job_dict['MODELNAME'],
                    f"{job_dict['MODELNAME']}.{job_dict['area']}."
                    +f"init{init_date_dt:%Y%m%d%H}.f"
                    +str(int(job_dict['fcst_hour'])
                         -((n-1)*int(job_dict['input_accum']))).zfill(3)
                )
                input_files_list.append(naccum_file)
                n+=1
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        input_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         f"pcp_combine_{job_dict['MODELNAME']}_"
                         +f"accum{job_dict['accum']}hr_"
                         +f"{job_dict['area']}_"
                         +f"init{init_date_dt:%Y%m%d%H}_"
                         +f"fhr{job_dict['fcst_hour'].zfill(3)}.nc")
        )
    input_files_exist_list = []
    for input_file in input_files_list:
        if check_file(input_file):
            input_files_exist_list.append(True)
        else:
            input_files_exist_list.append(False)
    if all(x == True for x in input_files_exist_list) \
            and len(input_files_exist_list) > 0:
        all_input_file_exist = True
    else:
        all_input_file_exist = False
    # Expected output files (in COMOUT and DATA)
    COMOUT_files_list = []
    DATA_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        file_name = (f"pcp_combine_{job_dict['MODELNAME']}_"
                     +f"accum{job_dict['accum']}hr_"
                     +f"{job_dict['area']}_"
                     +f"init{init_date_dt:%Y%m%d%H}_"
                     +f"fhr{job_dict['fcst_hour'].zfill(3)}.nc")
        COMOUT_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
        DATA_files_list.append(
            os.path.join(job_dict['DATA'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        file_name = (f"grid_stat_{job_dict['job_name']}_"
                     f"{job_dict['fcst_hour'].zfill(2)}0000L_"
                     +f"{valid_date_dt:%Y%m%d_%H%M%S}V.stat")
        COMOUT_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
        DATA_files_list.append(
            os.path.join(job_dict['DATA'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
    COMOUT_files_exist_list = []
    for COMOUT_file in COMOUT_files_list:
        if check_file(COMOUT_file):
            COMOUT_files_exist_list.append(True)
        else:
            COMOUT_files_exist_list.append(False)
    if all(x == True for x in COMOUT_files_exist_list) \
            and len(COMOUT_files_exist_list) > 0:
        all_COMOUT_file_exist = True
    else:
        all_COMOUT_file_exist = False
    return (all_input_file_exist, input_files_list, \
            all_COMOUT_file_exist, COMOUT_files_list,
            DATA_files_list)

def snowfall_check_obs_input_output_files(job_dict):
    """! Check snowfall observation input and output files
         in COMOUT and DATA
         Args:
             job_dict - job dictionary
         Returns:
             all_input_file_exist  - if all expected
                                     input files exist
                                     (boolean)
             input_files_list      - list of input files
                                     (strings)
             all_COMOUT_file_exist - if all expected
                                     output COMOUT files
                                     exist (boolean)
             COMOUT_files_list     - list of output COMOUT
                                     files (strings)
             DATA_files_list       - list of output DATA
                                     files (strings)
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hour_start'],
        '%Y%m%d%H'
    )
    # Expected input file
    input_files_list = []
    if job_dict['JOB_GROUP'] == 'generate_stats':
        if job_dict['obs'] == 'nohrsc':
            input_files_list.append(
                os.path.join(job_dict['DATA'], 'data', 'nohrsc',
                             f"nohrsc.accum{job_dict['accum']}hr."
                             +f"v{valid_date_dt:%Y%m%d%H}")
            )
    input_files_exist_list = []
    for input_file in input_files_list:
        if check_file(input_file):
            input_files_exist_list.append(True)
        else:
            input_files_exist_list.append(False)
    if all(x == True for x in input_files_exist_list) \
            and len(input_files_exist_list) > 0:
        all_input_file_exist = True
    else:
        all_input_file_exist = False
    # Expected output files (in COMOUT and DATA)
    COMOUT_files_list = []
    DATA_files_list = []
    #
    COMOUT_files_exist_list = []
    for COMOUT_file in COMOUT_files_list:
        if check_file(COMOUT_file):
            COMOUT_files_exist_list.append(True)
        else:
            COMOUT_files_exist_list.append(False)
    if all(x == True for x in COMOUT_files_exist_list) \
            and len(COMOUT_files_exist_list) > 0:
        all_COMOUT_file_exist = True
    else:
        all_COMOUT_file_exist = False
    return (all_input_file_exist, input_files_list, \
            all_COMOUT_file_exist, COMOUT_files_list,
            DATA_files_list)

def snowfall_check_model_input_output_files(job_dict):
    """! Check snowfall model input and output files
         in COMOUT and DATA
         Args:
             job_dict - job dictionary
         Returns:
             all_input_file_exist  - if all expected
                                     input files exist
                                     (boolean)
             input_files_list      - list of input files
                                     (strings)
             all_COMOUT_file_exist - if all expected
                                     output COMOUT files
                                     exist (boolean)
             COMOUT_files_list     - list of output COMOUT
                                     files (strings)
             DATA_files_list       - list of output DATA
                                     files (strings)
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hour_start'],
        '%Y%m%d%H'
    )
    init_date_dt = (valid_date_dt
                    - datetime.timedelta(hours=int(job_dict['fcst_hour'])))
    # Expected input file
    input_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['pcp_combine_method'] in ['SUBTRACT', 'USER_DEFINED']:
            for fhr in [job_dict['fcst_hour'],
                        str(int(job_dict['fcst_hour'])
                            - int(job_dict['accum']))]:
                input_files_list.append(
                    os.path.join(job_dict['DATA'], 'data',
                                 job_dict['MODELNAME'],
                                 f"{job_dict['MODELNAME']}."
                                 +f"init{init_date_dt:%Y%m%d%H}."
                                 +f"f{fhr.zfill(3)}")
                )
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        input_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         f"pcp_combine_{job_dict['MODELNAME']}_"
                         +f"accum{job_dict['accum']}hr_"
                         +f"{job_dict['snow_var']}_"
                         +f"init{init_date_dt:%Y%m%d%H}_"
                         +f"fhr{job_dict['fcst_hour'].zfill(3)}.nc")
        )
    input_files_exist_list = []
    for input_file in input_files_list:
        if check_file(input_file):
            input_files_exist_list.append(True)
        else:
            input_files_exist_list.append(False)
    if all(x == True for x in input_files_exist_list) \
            and len(input_files_exist_list) > 0:
        all_input_file_exist = True
    else:
        all_input_file_exist = False
    # Expected output files (in COMOUT and DATA)
    COMOUT_files_list = []
    DATA_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        file_name = (f"pcp_combine_{job_dict['MODELNAME']}_"
                     +f"accum{job_dict['accum']}hr_"
                     +f"{job_dict['snow_var']}_"
                     +f"init{init_date_dt:%Y%m%d%H}_"
                     +f"fhr{job_dict['fcst_hour'].zfill(3)}.nc")
        COMOUT_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
        DATA_files_list.append(
            os.path.join(job_dict['DATA'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        file_name = (f"grid_stat_{job_dict['job_name']}_"
                     f"{job_dict['fcst_hour'].zfill(2)}0000L_"
                     +f"{valid_date_dt:%Y%m%d_%H%M%S}V.stat")
        COMOUT_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
        DATA_files_list.append(
            os.path.join(job_dict['DATA'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
    COMOUT_files_exist_list = []
    for COMOUT_file in COMOUT_files_list:
        if check_file(COMOUT_file):
            COMOUT_files_exist_list.append(True)
        else:
            COMOUT_files_exist_list.append(False)
    if all(x == True for x in COMOUT_files_exist_list) \
            and len(COMOUT_files_exist_list) > 0:
        all_COMOUT_file_exist = True
    else:
        all_COMOUT_file_exist = False
    return (all_input_file_exist, input_files_list, \
            all_COMOUT_file_exist, COMOUT_files_list,
            DATA_files_list)

def get_completed_jobs(completed_jobs_file):
    completed_jobs = set()
    if os.path.exists(completed_jobs_file):
        with open(completed_jobs_file, 'r') as f:
            completed_jobs = set(f.read().splitlines())
    return completed_jobs

def mark_job_completed(completed_jobs_file, job_name):
    with open(completed_jobs_file, 'a') as f:
        f.write(job_name + "\n")
