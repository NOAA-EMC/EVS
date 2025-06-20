#!/usr/bin/env python3
'''
Name: global_chem_atmos_util.py
Original Author: Mallory Row (mallory.row@noaa.gov)
Contact(s): Ho-Chun Huang (ho-chun.huang@noaa.gov)
Abstract: This contains many functions used across global_chem.
'''

import os
import datetime
import numpy as np
import subprocess
import shutil
import sys
import netCDF4 as netcdf
import glob
import pandas as pd
import logging
import copy
import itertools
from time import sleep

def run_shell_command(command):
    """! Run shell command

         Args:
             command - list of agrument entries (string)

         Returns:

    """
    print("Running  "+' '.join(command))
    if any(mark in ' '.join(command) for mark in ['"', "'", '|', '*', '>',
                                                  '-']):
        run_command = subprocess.run(
            ' '.join(command), shell=True
        )
    else:
        run_command = subprocess.run(command)
    if run_command.returncode != 0:
        print("FATAL ERROR: "+' '.join(run_command.args)+" gave return code "
              +str(run_command.returncode))
        sys.exit(run_command.returncode)

def make_dir(dir_path):
    """! Make a directory

         Args:
             dir_path - path of the directory (string)

         Returns:

    """
    if not os.path.exists(dir_path):
        print(f"Making directory {dir_path}")
        os.makedirs(dir_path, mode=0o755, exist_ok=True)


def python_command(python_script_name, script_arg_list):
    """! Write out full call to python

         Args:
             python_script_name - python script name (string)
             script_arg_list    - list of script agruments (strings)

         Returns:
             python_cmd - full call to python (string)

    """
    python_script = os.path.join(os.environ['USHevs'], os.environ['COMPONENT'],
                                 python_script_name)
    if not os.path.exists(python_script):
        print("FATAL ERROR: "+python_script+" DOES NOT EXIST")
        sys.exit(1)
    python_cmd = 'python '+python_script
    for script_arg in script_arg_list:
        python_cmd = python_cmd+' '+script_arg
    return python_cmd

def check_file_exists_size(file_name):
    """! Checks to see if file exists and has size greater than 0

         Args:
             file_name - file path (string)

         Returns:
             file_good - boolean
                       - True: file exists,file size >0
                       - False: file doesn't exist
                                OR file size = 0
    """
    if '/com/' in file_name or '/dcom/' in file_name:
        alert_word = 'WARNING'
    else:
        alert_word = 'NOTE'
    if os.path.exists(file_name):
        if os.path.getsize(file_name) > 0:
            file_good = True
        else:
            print(f"{alert_word}: {file_name} empty, 0 sized")
            file_good = False
    else:
        print(f"{alert_word}: {file_name} does not exist")
        file_good = False
    return file_good

def copy_file(source_file, dest_file):
    """! This copies a file from one location to another

         Args:
             source_file - source file path (string)
             dest_file   - destination file path (string)

         Returns:
    """
    if check_file_exists_size(source_file):
        print("Copying "+source_file+" to "+dest_file)
        shutil.copy(source_file, dest_file)


def get_time_info(date_start, date_end, date_type, init_hr_list, valid_hr_list,
                  fhr_list):
    """! Creates a list of dictionaries containing information
         on the valid dates and times, the initialization dates
         and times, and forecast hour pairings

         Args:
             date_start     - verification start date
                              (string, format:YYYYmmdd)
             date_end       - verification end_date
                              (string, format:YYYYmmdd)
             date_type      - how to treat date_start and
                              date_end (string, values:VALID or INIT)
             init_hr_list   - list of initialization hours
                              (string)
             valid_hr_list  - list of valid hours (string)
             fhr_list       - list of forecasts hours (string)

         Returns:
             time_info - list of dictionaries with the valid,
                         initialization, and forecast hour
                         pairings
    """
    valid_hr_zfill2_list = [hr.zfill(2) for hr in valid_hr_list]
    init_hr_zfill2_list = [hr.zfill(2) for hr in init_hr_list]
    if date_type == 'VALID':
        date_type_hr_list = valid_hr_zfill2_list
    elif date_type == 'INIT':
        date_type_hr_list = init_hr_zfill2_list
    date_type_hr_start = date_type_hr_list[0]
    date_type_hr_end = date_type_hr_list[-1]
    if len(date_type_hr_list) > 1:
        date_type_hr_inc = np.min(
            np.diff(np.array(date_type_hr_list, dtype=int))
        )
    else:
        date_type_hr_inc = 24
    date_start_dt = datetime.datetime.strptime(date_start+date_type_hr_start,
                                               '%Y%m%d%H')
    date_end_dt = datetime.datetime.strptime(date_end+date_type_hr_end,
                                             '%Y%m%d%H')
    time_info = []
    date_dt = date_start_dt
    while date_dt <= date_end_dt:
        if date_type == 'VALID':
            valid_time_dt = date_dt
        elif date_type == 'INIT':
            init_time_dt = date_dt
        for fhr in fhr_list:
            if fhr == 'anl':
                forecast_hour = 0
            else:
                forecast_hour = int(fhr)
            if date_type == 'VALID':
                init_time_dt = (valid_time_dt
                                - datetime.timedelta(hours=forecast_hour))
            elif date_type == 'INIT':
                valid_time_dt = (init_time_dt
                                 + datetime.timedelta(hours=forecast_hour))
            if valid_time_dt.strftime('%H') in valid_hr_zfill2_list \
                    and init_time_dt.strftime('%H') in init_hr_zfill2_list:
                t = {}
                t['valid_time'] = valid_time_dt
                t['init_time'] = init_time_dt
                t['forecast_hour'] = str(forecast_hour)
                time_info.append(t)
        date_dt = date_dt + datetime.timedelta(hours=int(date_type_hr_inc))
    return time_info

def get_init_hour(valid_hour, forecast_hour):
    """! Get a initialization hour

         Args:
             valid_hour    - valid hour (integer)
             forecast_hour - forecast hour (integer)
    """
    init_hour = 24 + (valid_hour - (forecast_hour%24))
    if forecast_hour % 24 == 0:
        init_hour = valid_hour
    else:
        init_hour = 24 + (valid_hour - (forecast_hour%24))
    if init_hour >= 24:
        init_hour = init_hour - 24
    return init_hour

def get_valid_hour(init_hour, forecast_hour):
    """! Get a valid hour

         Args:
             init_hour    - intit hour (integer)
             forecast_hour - forecast hour (integer)
    """
    valid_hour = (init_hour + (forecast_hour%24))
    if forecast_hour % 24 == 0:
        valid_hour = init_hour
    else:
        valid_hour = (init_hour + (forecast_hour%24))
    if valid_hour >= 24:
        valid_hour = valid_hour - 24
    return valid_hour


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
                       'init', 'init_shift']
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
                       shift = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0].partition('shift=')[2]
                       )
                       format_opt_count_fmt = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0].partition('?')[0]
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
                   elif format_opt == 'lead_shift':
                       shift = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0].partition('shift=')[2]
                       )
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
                       shift = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0].partition('shift=')[2]
                       )
                       init_shift_time_dt = (
                           init_time_dt + datetime.timedelta(hours=int(shift))
                       )
                       replace_format_opt_count = init_shift_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'valid_shift':
                       shift = (
                           filled_file_format_chunk \
                           .partition('{'+format_opt+'?fmt=')[2] \
                           .partition('}')[0].partition('shift=')[2]
                       )
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


def check_stat_files(job_dict):
    """! Check for MET .stat files

         Args:
             job_dict         - dictionary containing settings
                                job is running with (strings)
             copy_output_list - list of file to copy from

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
    # Check inputs
    if len(stat_file_list) != 0:
        stat_files_exist = True
    else:
        stat_files_exist = False
    copy_output_list = []
    # Set outputs
    file_JOB = os.path.join(
        job_dict['job_num_work_dir'],
        f"{job_dict['MODEL']}.{job_dict['DATE']}",
        f"evs.{job_dict['STEP']}.{job_dict['MODEL']}.{job_dict['RUN']}."
        +f"{job_dict['VERIF_CASE']}.v{job_dict['DATE']}.stat"
    )
    file_COMOUT = os.path.join(
        job_dict['COMOUT'], f"{job_dict['MODEL']}.{job_dict['DATE']}",
        file_JOB.rpartition('/')[2]
    )
    file_EVS_DATA = os.path.join(
        job_dict['MODEL_EVS_DATA_DIR'],
        file_JOB.rpartition('/')[2]
    )
    file_output_list = [file_EVS_DATA]
    if job_dict['SENDCOM'] == 'YES':
        file_output_list.append(file_COMOUT)
    for file_output in file_output_list:
        output_tuple = (file_JOB, file_output)
        if output_tuple not in copy_output_list:
            copy_output_list.append(output_tuple)
    return stat_files_exist, copy_output_list

def check_plot_files(job_dict):
    """! Check what plot files or don't exist

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             plot_files_exist - if non-zero number of  model files
                                exist or not (boolean)
    """
    if job_dict['JOB_GROUP'] != 'tar_images':
        model_list = job_dict['model_list'].split(', ')
        obs_list = job_dict['obs_list'].split(', ')
    if job_dict['JOB_GROUP'] in ['filter_stats', 'make_plots']:
        valid_hrs = list(
            range(int(job_dict['valid_hr_start']),
                  int(job_dict['valid_hr_end'])+int(job_dict['valid_hr_inc']),
                  int(job_dict['valid_hr_inc']))
        )
        init_hrs = list(
            range(int(job_dict['init_hr_start']),
                  int(job_dict['init_hr_end'])+int(job_dict['init_hr_inc']),
                  int(job_dict['init_hr_inc']))
        )
        fhrs = [int(i) for i in job_dict['fhr_list'].split(', ')]
    if job_dict['JOB_GROUP'] == 'make_plots':
        from global_chem_atmos_plots_specs import PlotSpecs
        plot_specs = PlotSpecs('NA', job_dict['plot'])
        fcst_var_prod = list(
            itertools.product([job_dict['fcst_var_name']],
                              job_dict['fcst_var_level_list'].split(', '),
                              job_dict['fcst_var_thresh_list'].split(', '))
        )
        obs_var_prod = list(
            itertools.product([job_dict['obs_var_name']],
                              job_dict['obs_var_level_list'].split(', '),
                              job_dict['obs_var_thresh_list'].split(', '))
        )
        if len(fcst_var_prod) == len(obs_var_prod):
            var_info = []
            for v in range(len(fcst_var_prod)):
                var_info.append((fcst_var_prod[v], obs_var_prod[v]))
        else:
            print("ERROR: Forecast and observation variable information not "
                  +"the same length")
            sys.exit(1)
    # Check files
    plot_files_exist = True
    if job_dict['JOB_GROUP'] == 'condense_stats':
        job_COMOUT_file_exist_list = []
        for model in model_list:
            job_COMOUT_model_file = os.path.join(
                os.path.join(job_dict['job_COMOUT_dir'],
                f"condensed_stats_{model.lower()}_"
                +f"{job_dict['line_type'].lower()}_"
                +f"{job_dict['fcst_var_name'].lower()}_"
                +(job_dict['fcst_var_level'].lower()\
                  .replace('.','p').replace('-', '_'))
                +f"_{job_dict['vx_mask'].lower()}.stat")
            )
            if os.path.exists(job_COMOUT_model_file):
                job_COMOUT_file_exist_list.append(
                    job_COMOUT_model_file
                )
        if len(job_COMOUT_file_exist_list) == len(model_list):
            plot_files_exist = True
        else:
            plot_files_exist = False
    elif job_dict['JOB_GROUP'] == 'filter_stats':
        for filter_info in list(itertools.product(valid_hrs, fhrs)):
            init_hr = get_init_hour(
                int(filter_info[0]), int(filter_info[1])
            )
            if init_hr in init_hrs:
                job_COMOUT_file_exist_list = []
                for model_idx in range(len(model_list)):
                    model = model_list[model_idx]
                    obs = obs_list[model_idx]
                    filename = (
                        f"fcst{model}_{job_dict['fcst_var_name']}"
                        +f"{job_dict['fcst_var_level']}"
                        +f"{job_dict['fcst_var_thresh']}_"
                        +f"obs{obs}_{job_dict['obs_var_name']}"
                        +f"{job_dict['obs_var_level']}"
                        +f"{job_dict['obs_var_thresh']}_"
                        +f"linetype{job_dict['line_type']}_"
                        +f"grid{job_dict['grid']}_"
                        +f"vxmask{job_dict['vx_mask']}_"
                        +f"interp{job_dict['interp_method']}"
                        +f"{job_dict['interp_points']}_"
                        +f"{job_dict['date_type'].lower()}"
                        +f"{job_dict['start_date']}"
                        +f"{str(filter_info[0]).zfill(2)}0000to"
                        +f"{job_dict['end_date']}"
                        +f"{str(filter_info[0]).zfill(2)}0000_"
                        +f"fhr{str(filter_info[1]).zfill(3)}"
                    ).lower().replace('.','p').replace('-', '_')\
                    .replace('&&', 'and').replace('||', 'or')\
                    .replace('0,*,*', '').replace('*,*', '')+'.stat'
                    job_COMOUT_model_file = os.path.join(job_dict['job_COMOUT_dir'],
                                                          filename)
                    if os.path.exists(job_COMOUT_model_file):
                        job_COMOUT_file_exist_list.append(
                            job_COMOUT_model_file
                        )
                if len(job_COMOUT_file_exist_list) == len(model_list):
                    plot_files_exist = True
                else:
                    plot_files_exist = False
    elif job_dict['JOB_GROUP'] == 'make_plots':
        plot_files_exist = True
        if job_dict['plot'] == 'time_series':
            plot_info_list = list(itertools.product(valid_hrs, fhrs, var_info))
        elif job_dict['plot'] in ['lead_average']:
            plot_info_list = list(itertools.product(valid_hrs, var_info))
        elif job_dict['plot'] == 'valid_hour_average':
            plot_info_list = list(itertools.product(var_info))
        elif job_dict['plot'] in ['performance_diagram','threshold_average']:
            plot_info_list = list(itertools.product(valid_hrs, fhrs))
        if job_dict['plot'] in ['performance_diagram', 'threshold_average']:
            fcst_var_thresh_list = (job_dict['fcst_var_thresh_list']\
                                    .split(', '))
            obs_var_thresh_list = (job_dict['obs_var_thresh_list']\
                                    .split(', '))
            if job_dict['plot'] == 'threshold_average':
                fcst_var_level_list = (job_dict['fcst_var_level_list']\
                                       .split(', '))
                obs_var_level_list = (job_dict['obs_var_level_list']\
                                      .split(', '))
        plots_files_exist_check_list = []
        for plot_info in plot_info_list:
            # Set up plot_dict
            plot_dict = copy.deepcopy(job_dict)
            if plot_dict['plot'] != 'valid_hour_average':
                plot_dict['valid_hr_start'] = str(plot_info[0])
                plot_dict['valid_hr_end'] = str(plot_info[0])
                plot_dict['valid_hr_inc'] = '24'
            if plot_dict['plot'] in ['time_series', 'performance_diagram',
                                     'threshold_average']:
                plot_dict['forecast_hour'] = str(plot_info[1])
            else:
                plot_dict['forecast_hours'] = fhrs
            if plot_dict['plot'] == 'time_series':
                plot_dict['fcst_var_name'] = plot_info[2][0][0]
                plot_dict['fcst_var_level'] = plot_info[2][0][1]
                plot_dict['fcst_var_thresh'] = plot_info[2][0][2]
                plot_dict['obs_var_name'] = plot_info[2][1][0]
                plot_dict['obs_var_level'] = plot_info[2][1][1]
                plot_dict['obs_var_thresh'] = plot_info[2][1][2]
            elif plot_dict['plot'] in ['lead_average']:
                plot_dict['fcst_var_name'] = plot_info[1][0][0]
                plot_dict['fcst_var_level'] = plot_info[1][0][1]
                plot_dict['fcst_var_thresh'] = plot_info[1][0][2]
                plot_dict['obs_var_name'] = plot_info[1][1][0]
                plot_dict['obs_var_level'] = plot_info[1][1][1]
                plot_dict['obs_var_thresh'] = plot_info[1][1][2]
            elif plot_dict['plot'] == 'valid_hour_average':
                plot_dict['fcst_var_name'] = plot_info[0][0][0]
                plot_dict['fcst_var_level'] = plot_info[0][0][1]
                plot_dict['fcst_var_thresh'] = plot_info[0][0][2]
                plot_dict['obs_var_name'] = plot_info[0][1][0]
                plot_dict['obs_var_level'] = plot_info[0][1][1]
                plot_dict['obs_var_thresh'] = plot_info[0][1][2]
            if plot_dict['plot'] in ['time_series', 'performance_diagram',
                                     'threshold_average']:
                init_hr = get_init_hour(
                    int(plot_dict['valid_hr_start']),
                    int(plot_dict['forecast_hour'])
                )
            # Check for plots
            if plot_dict['plot'] == 'time_series':
                if plot_dict['stat'] == 'FBAR_OBAR' \
                        and str(plot_dict['forecast_hour']) not in \
                        ['24', '48', '72', '96', '120']:
                    continue
                if init_hr not in init_hrs:
                    continue
                plot_check = plot_specs.get_savefig_name(
                    plot_dict['job_COMOUT_dir'], plot_dict, plot_dict
                )
                plots_files_exist_check_list.append(
                    os.path.exists(plot_check)
                )
            elif plot_dict['plot'] in ['lead_average']:
                if plot_dict['stat'] != 'FBAR_OBAR' \
                        and len(fhrs) > 1:
                    plot_check = plot_specs.get_savefig_name(
                        plot_dict['job_COMOUT_dir'], plot_dict, plot_dict
                    )
                    plots_files_exist_check_list.append(
                        os.path.exists(plot_check)
                    )
            elif plot_dict['plot'] == 'valid_hour_average':
                 if plot_dict['stat'] != 'FBAR_OBAR':
                     if plot_dict['valid_hr_start'] \
                             != plot_dict['valid_hr_end']:
                         plot_check = plot_specs.get_savefig_name(
                             plot_dict['job_COMOUT_dir'], plot_dict, plot_dict
                         )
                         plots_files_exist_check_list.append(
                             os.path.exists(plot_check)
                         )
            elif plot_dict['plot'] == 'threshold_average':
                if init_hr not in init_hrs \
                        or plot_dict['stat'] == 'FBAR_OBAR':
                    continue
                plot_dict['fcst_var_threshs'] = fcst_var_thresh_list
                plot_dict['obs_var_threshs'] = obs_var_thresh_list
                if len(plot_dict['fcst_var_threshs']) <= 1:
                    continue
                for l in range(len(fcst_var_level_list)):
                    plot_dict['fcst_var_level'] = fcst_var_level_list[l]
                    plot_dict['obs_var_level'] = obs_var_level_list[l]
                    plot_check = plot_specs.get_savefig_name(
                        plot_dict['job_COMOUT_dir'], plot_dict, plot_dict
                    )
                    plots_files_exist_check_list.append(
                        os.path.exists(plot_check)
                    )
            elif plot_dict['plot'] == 'performance_diagram':
                if init_hr not in init_hrs \
                        or plot_dict['stat'] != 'PERFDIAG':
                    continue
                plot_dict['fcst_var_threshs'] = fcst_var_thresh_list
                plot_dict['obs_var_threshs'] = obs_var_thresh_list
                for l in range(
                        len(plot_dict['fcst_var_level_list'].split(', '))
                ):
                    plot_dict['fcst_var_level'] = (
                        plot_dict['fcst_var_level_list'].split(', ')[l]
                    )
                    plot_dict['obs_var_level'] = (
                        plot_dict['obs_var_level_list'].split(', ')[l]
                    )
                    plot_check = plot_specs.get_savefig_name(
                        plot_dict['job_COMOUT_dir'], plot_dict, plot_dict
                    )
                    plots_files_exist_check_list.append(
                        os.path.exists(plot_check)
                    )
            if all(x == True for x in plots_files_exist_check_list) \
                    and len(plots_files_exist_check_list) > 0:
                plot_files_exist = True
            else:
                plot_files_exist = False
    elif job_dict['JOB_GROUP'] == 'tar_images':
        tar_file_name = (
            f"{job_dict['VERIF_CASE']}_{job_dict['VERIF_TYPE']}_"
            +job_dict['job_COMOUT_dir'].replace(
                os.path.join(job_dict['COMOUT'],
                             f"{job_dict['VERIF_CASE']}_"
                             +f"{job_dict['VERIF_TYPE']}",
                             f"last{job_dict['NDAYS']}days/"),
                ''
            ).replace('/', '_')+'.tar'
        )
        job_COMOUT_tar_file = os.path.join(
            job_dict['job_COMOUT_dir'], tar_file_name
        )
        job_DATA_tar_file = os.path.join(
            job_dict['DATA'], f"{job_dict['VERIF_CASE']}_{job_dict['STEP']}",
            'plot_output', 'tar_files', tar_file_name
        )
        if os.path.exists(job_COMOUT_tar_file):
            copy_file(job_COMOUT_tar_file, job_DATA_tar_file)
            plot_files_exist = True
        else:
            plot_files_exist = False
    return plot_files_exist


def initialize_job_env_dict(verif_type, group,
                           verif_case_step_abbrev_type, job):
    """! This initializes a dictionary of environment variables and their
         values to be set for the job pulling from environment variables
         already set previously
         Args:
             verif_type                  - string of the use case name
             group                       - string of the group name
             verif_case_step_abbrev_type - string of reference name in config
                                           and environment variables
             job                         - string of job name
         Returns:
             job_env_dict - dictionary of job settings
    """
    job_env_var_list = [
        'machine', 'evs_ver', 'HOMEevs', 'FIXevs', 'USHevs', 'DATA', 'COMROOT',
        'NET', 'RUN', 'VERIF_CASE', 'STEP', 'COMPONENT', 'COMIN', 'SENDCOM',
        'COMOUT', 'evs_run_mode'
    ]
    if group in ['reformat_data', 'assemble_data', 'generate_stats',
                 'gather_stats', 'summarize_stats', 'write_reports',
                 'concatenate_reports']:
        if os.environ['VERIF_CASE'] == 'wmo':
           job_env_var_list.extend(['met_ver'])
        job_env_var_list.extend(
            ['METPLUS_PATH', 'MET_ROOT']
        )
    elif group in ['condense_stats', 'filter_stats', 'make_plots',
                   'tar_images']:
        job_env_var_list.extend(['MET_ROOT', 'met_ver'])
        if group == 'tar_images':
            job_env_var_list.extend(['KEEPDATA'])
    job_env_dict = {}
    for env_var in job_env_var_list:
        job_env_dict[env_var] = os.environ[env_var]
    if os.environ['VERIF_CASE'] == 'wmo':
        for env_var in ['MODELNAME', 'COMINgfs', 'JOB_GROUP']:
            job_env_dict[env_var] = os.environ[env_var]
        return job_env_dict
    if group in ['condense_stats', 'filter_stats', 'make_plots',
                 'tar_images']:
        job_env_dict['plot_verbosity'] = 'DEBUG'
    job_env_dict['VERIF_TYPE'] = verif_type
    job_env_dict['JOB_GROUP'] = group
    job_env_dict['job_name'] = job
    job_env_dict['fig_name_label'] = os.environ['fig_name_label']
    if group in ['reformat_data', 'assemble_data', 'generate_stats',
                 'filter_stats', 'make_plots']:
        if verif_case_step_abbrev_type+'_fhr_list' in list(os.environ.keys()):
            fhr_list = (
                os.environ[verif_case_step_abbrev_type+'_fhr_list'].split(' ')
            )
        else:
            fhr_range = range(
                int(os.environ[verif_case_step_abbrev_type+'_fhr_min']),
                int(os.environ[verif_case_step_abbrev_type+'_fhr_max'])
                +int(os.environ[verif_case_step_abbrev_type+'_fhr_inc']),
                int(os.environ[verif_case_step_abbrev_type+'_fhr_inc'])
            )
            fhr_list = [str(i) for i in fhr_range]
        job_env_dict['fhr_list'] = ', '.join(fhr_list)
        if verif_type in ['pres_levs', 'means', 'sfc', 'ptype', 'abi', 'viirs', 'aeronet', 'airnow']:
            verif_type_valid_hr_list = (
                os.environ[verif_case_step_abbrev_type+'_valid_hr_list']\
                .split(' ')
            )
            if os.environ['VERIF_CASE'] == 'grid2obs' \
                    and verif_type == 'sfc':
                if 'CAPE' in job or job in ['PBLHeight',
                                            'DailyAvg_TempAnom2m']:
                    for vh in verif_type_valid_hr_list:
                        if int(vh) % 6 != 0:
                            verif_type_valid_hr_list.remove(vh)
            job_env_dict['valid_hr_start'] = (
                verif_type_valid_hr_list[0].zfill(2)
            )
            job_env_dict['valid_hr_end'] = (
                verif_type_valid_hr_list[-1].zfill(2)
            )
            if len(verif_type_valid_hr_list) > 1:
                verif_type_valid_hr_inc = np.min(
                    np.diff(np.array(verif_type_valid_hr_list, dtype=int))
                )
            else:
                verif_type_valid_hr_inc = 24
            job_env_dict['valid_hr_inc'] = str(verif_type_valid_hr_inc)
        else:
            if verif_type == 'precip_accum24hr':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('24hrCCPA')
                )
            elif verif_type == 'precip_accum3hr':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('3hrCCPA')
                )
            elif verif_type == 'snow':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('24hrNOHRSC')
                )
            elif verif_type == 'sea_ice':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('OSI-SAF')
                )
            elif verif_type == 'sst':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('GHRSST-OSPO')
                )
            else:
                 valid_hr_start, valid_hr_end, valid_hr_inc = 12, 12, 23
            job_env_dict['valid_hr_start'] = str(valid_hr_start).zfill(2)
            job_env_dict['valid_hr_end'] = str(valid_hr_end).zfill(2)
            job_env_dict['valid_hr_inc'] = str(valid_hr_inc)
        verif_type_init_hr_list = (
            os.environ[verif_case_step_abbrev_type+'_init_hr_list']\
            .split(' ')
        )
        job_env_dict['init_hr_start'] = (
            verif_type_init_hr_list[0].zfill(2)
        )
        job_env_dict['init_hr_end'] = (
            verif_type_init_hr_list[-1].zfill(2)
        )
        if len(verif_type_init_hr_list) > 1:
            verif_type_init_hr_inc = np.min(
                np.diff(np.array(verif_type_init_hr_list, dtype=int))
            )
        else:
            verif_type_init_hr_inc = 24
        job_env_dict['init_hr_inc'] = str(verif_type_init_hr_inc)
    return job_env_dict

def get_logger(log_file):
    """! Get logger
         Args:
             log_file - full path to log file (string)
         Returns:
             logger - logger object
    """
    log_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
        + '%(message)s',
        '%m/%d %H:%M:%S'
    )
    logger = logging.getLogger(log_file)
    logger.setLevel('DEBUG')
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    logger_info = f"Log file: {log_file}"
    print(logger_info)
    logger.info(logger_info)
    return logger

def get_plot_dates(logger, date_type, start_date, end_date,
                   valid_hr_start, valid_hr_end, valid_hr_inc,
                   init_hr_start, init_hr_end, init_hr_inc,
                   forecast_hour):
    """! This builds the dates to include in plotting based on user
         configurations
         Args:
             logger         - logger object
             date_type      - type of date to plot (string: VALID or INIT)
             start_date     - plotting start date (string, format: YYYYmmdd)
             end_date       - plotting end date (string, format: YYYYmmdd)
             valid_hr_start - starting valid hour (string)
             valid_hr_end   - ending valid hour (string)
             valid_hr_inc   - valid hour increment (string)
             init_hr_start  - starting initialization hour (string)
             init_hr_end    - ending initialization hour (string)
             init_hr_inc    - initialization hour incrrement (string)
             forecast_hour  - forecast hour (string)
         Returns:
             valid_dates - array of valid dates (datetime)
             init_dates  - array of initialization dates (datetime)
    """
    # Build date_type date array
    if date_type == 'VALID':
        start_date_dt = datetime.datetime.strptime(start_date+valid_hr_start,
                                                   '%Y%m%d%H')
        end_date_dt = datetime.datetime.strptime(end_date+valid_hr_end,
                                                 '%Y%m%d%H')
        dt_inc = datetime.timedelta(hours=int(valid_hr_inc))
    elif date_type == 'INIT':
        start_date_dt = datetime.datetime.strptime(start_date+init_hr_start,
                                                   '%Y%m%d%H')
        end_date_dt = datetime.datetime.strptime(end_date+init_hr_end,
                                                 '%Y%m%d%H')
        dt_inc = datetime.timedelta(hours=int(init_hr_inc))
    date_type_dates = (np.arange(start_date_dt, end_date_dt+dt_inc, dt_inc)\
                       .astype(datetime.datetime))
    # Build valid and init date arrays
    if date_type == 'VALID':
        valid_dates = date_type_dates
        init_dates = (valid_dates
                      - datetime.timedelta(hours=(int(forecast_hour))))
    elif date_type == 'INIT':
        init_dates = date_type_dates
        valid_dates = (init_dates
                      + datetime.timedelta(hours=(int(forecast_hour))))
    # Check if unrequested hours exist in arrays, and remove
    valid_remove_idx_list = []
    valid_hr_list = [
        str(hr).zfill(2) for hr in range(int(valid_hr_start),
                                         int(valid_hr_end)+int(valid_hr_inc),
                                         int(valid_hr_inc))
    ]
    for d in range(len(valid_dates)):
        if valid_dates[d].strftime('%H') \
                not in valid_hr_list:
            valid_remove_idx_list.append(d)
    valid_dates = np.delete(valid_dates, valid_remove_idx_list)
    init_dates = np.delete(init_dates, valid_remove_idx_list)
    init_remove_idx_list = []
    init_hr_list = [
        str(hr).zfill(2) for hr in range(int(init_hr_start),
                                         int(init_hr_end)+int(init_hr_inc),
                                         int(init_hr_inc))
    ]
    for d in range(len(init_dates)):
        if init_dates[d].strftime('%H') \
                not in init_hr_list:
            init_remove_idx_list.append(d)
    valid_dates = np.delete(valid_dates, init_remove_idx_list)
    init_dates = np.delete(init_dates, init_remove_idx_list)
    return valid_dates, init_dates

def get_met_line_type_cols(logger, met_root, met_version, met_line_type):
    """! Get the MET columns for a specific line type and MET
         verison

         Args:
             logger        - logger object
             met_root      - path to MET (string)
             met_version   - MET version number (string)
             met_line_type - MET line type (string)
         Returns:
             met_version_line_type_col_list - list of MET versoin
                                              line type colums (strings)
    """
    if met_version.count('.') == 2:
        met_minor_version = met_version.rpartition('.')[0]
    elif met_version.count('.') == 1:
        met_minor_version = met_version
    met_minor_version_col_file = os.path.join(
        met_root, 'share', 'met', 'table_files',
        'met_header_columns_V'+met_minor_version+'.txt'
    )
    if os.path.exists(met_minor_version_col_file):
        with open(met_minor_version_col_file) as f:
            for line in f:
                if met_line_type in line:
                    line_type_cols = line.split(' : ')[-1]
                    break
    else:
        logger.error(f"{met_minor_version_col_file} does not exist, "
                     +"cannot determine MET data column structure")
        sys.exit(1)
    met_version_line_type_col_list = (
        line_type_cols.replace('\n', '').split(' ')
    )
    return met_version_line_type_col_list

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

def get_plot_job_dirs(DATA_base_dir, COMOUT_base_dir, job_group,
                      plot_job_env_dict):
    """! Get directories for the plotting job
         Args:
             DATA_base_dir     - path to DATA directory
                                 (string)
             COMOUT_base_dir   - path to COMOUT directory
                                 (string)
             job_group         - plotting job group:
                                 condense_stats, filter_stats,
                                 make_plots (string)
             plot_job_env_dict - dictionary with plotting job
                                 environment variables to be
                                 set

         Returns:
             job_work_dir    - path to plotting job's
                               working directory
             job_DATA_dir    - path to plotting job's
                               DATA directory
             job_COMOUT_dir  - path to plotting job's
                               COMOUT directory
    """
    region_savefig_dict = {
        'Africa': 'africa',
        'AFRICA': 'africa',
        'Alaska': 'alaska',
        'alaska': 'alaska',
        'Appalachia': 'buk_apl',
        'ANTARCTIC': 'antarctic',
        'ARCTIC': 'arctic',
        'Asia': 'asia',
        'ASIA': 'asia',
        'ATL_MDR': 'al_mdr',
        'Conus': 'conus',
        'conus': 'conus',
        'CONUS': 'buk_conus',
        'CONUS_East': 'buk_conus_e',
        'CONUS_Central': 'buk_conus_c',
        'CONUS_South': 'buk_conus_s',
        'CONUS_West': 'buk_conus_w',
        'CPlains': 'buk_cpl',
        'DeepSouth': 'buk_ds',
        'EPAC_MDR': 'ep_mdr',
        'GLOBAL': 'glb',
        'GreatBasin': 'buk_grb',
        'GreatLakes': 'buk_grlk',
        'hawaii': 'hawaii',
        'Mezquital': 'buk_mez',
        'MidAtlantic': 'buk_matl',
        'N60N90': 'n60',
        'NAMERICA': 'namer',
        'NAO': 'nao',
        'NHEM': 'nhem',
        'NorthAtlantic': 'buk_ne',
        'NPlains': 'buk_npl',
        'NPO': 'npo',
        'NRockies': 'buk_nrk',
        'PacificNW': 'buk_npw',
        'PacificSW': 'buk_psw',
        'Prairie': 'buk_pra',
        'prico': 'prico',
        'S60S90': 's60',
        'SAO': 'sao',
        'SAMERICA': 'samer',
        'SHEM': 'shem',
        'Southeast': 'buk_se',
        'Southwest': 'buk_sw',
        'SPlains': 'buk_spl',
        'SPO': 'spo',
        'SRockies': 'buk_srk',
        'TROPICS': 'tropics'
    }
    dir_step = plot_job_env_dict['STEP'].lower()
    dir_verif_case = plot_job_env_dict['VERIF_CASE'].lower()
    dir_verif_type = plot_job_env_dict['VERIF_TYPE'].lower()
    dir_name_label = plot_job_env_dict['fig_name_label'].lower()
    dir_line_type = plot_job_env_dict['line_type'].lower()
    dir_parameter = plot_job_env_dict['fcst_var_name'].lower()
    if job_group == 'make_plots':
        if plot_job_env_dict['plot'] in ['stat_by_level', 'lead_by_level']:
            dir_level = plot_job_env_dict['vert_profile'].lower()
        else:
            dir_level = (plot_job_env_dict['fcst_var_level_list'].lower()\
                         .replace('.','p').replace('-', '_'))
    else:
        dir_level = (plot_job_env_dict['fcst_var_level'].lower()\
                     .replace('.','p').replace('-', '_'))
    if plot_job_env_dict['fcst_var_name'] == 'CAPE':
        dir_level = dir_level.replace('z0', 'l0').replace('p90_0', 'l90')
    dir_region = region_savefig_dict[plot_job_env_dict['vx_mask']]
    if job_group in ['condense_stats', 'filter_stats']:
        job_work_dir = os.path.join(
            DATA_base_dir, f"{dir_verif_case}_{dir_step}", 'plot_output',
            'job_work_dir', job_group, f"{plot_job_env_dict['job_id']}",
            f"{plot_job_env_dict['RUN']}.{plot_job_env_dict['end_date']}",
            f"{dir_verif_case}_{dir_verif_type}",
            dir_name_label, dir_line_type,
            f"{dir_parameter}_{dir_level}",
            dir_region
        )
    elif job_group == 'make_plots':
        dir_stat = plot_job_env_dict['stat'].lower()
        job_work_dir = os.path.join(
            DATA_base_dir, f"{dir_verif_case}_{dir_step}", 'plot_output',
            'job_work_dir', job_group, f"{plot_job_env_dict['job_id']}",
            f"{plot_job_env_dict['RUN']}.{plot_job_env_dict['end_date']}",
            f"{dir_verif_case}_{dir_verif_type}",
            dir_name_label, dir_line_type,
            f"{dir_parameter}_{dir_level}",
            dir_region, dir_stat
        )
    job_COMOUT_dir = job_work_dir.replace(
        os.path.join(DATA_base_dir,
                     f"{dir_verif_case}_{dir_step}",
                     'plot_output', 'job_work_dir', job_group,
                     f"{plot_job_env_dict['job_id']}",
                     f"{plot_job_env_dict['RUN']}."
                     +f"{plot_job_env_dict['end_date']}"),
        COMOUT_base_dir
    )
    job_DATA_dir = job_COMOUT_dir.replace(
        COMOUT_base_dir,
        os.path.join(DATA_base_dir, f"{dir_verif_case}_{dir_step}",
                     'plot_output', f"{plot_job_env_dict['RUN']}."
                     +f"{plot_job_env_dict['end_date']}")
    )
    return job_work_dir, job_DATA_dir, job_COMOUT_dir

def get_daily_stat_file(model_name, source_stats_base_dir,
                        dest_model_name_stats_dir,
                        verif_case, start_date_dt, end_date_dt):
    """! Link model daily stat files
         Args:
             model_name                - name of model (string)
             source_stats_base_dir     - full path to stats/global_chem_atmos
                                         source directory (string)
             dest_model_name_stats_dir - full path to model
                                         destintion directory (string)
             verif_case                - grid2grid or grid2obs (string)
             start_date_dt             - month start date (datetime obj)
             end_date_dt               - month end date (datetime obj)
         Returns:
    """
    date_dt = start_date_dt
    while date_dt <= end_date_dt:
        source_model_date_stat_file = os.path.join(
            source_stats_base_dir,
            model_name+'.'+date_dt.strftime('%Y%m%d'),
            'evs.stats.'+model_name+'.atmos.'+verif_case+'.'
            +'v'+date_dt.strftime('%Y%m%d')+'.stat'
        )
        dest_model_date_stat_file = os.path.join(
            dest_model_name_stats_dir,
            model_name+'_atmos_'+verif_case+'_v'
            +date_dt.strftime('%Y%m%d')+'.stat'
        )
        if not os.path.exists(dest_model_date_stat_file):
            if check_file_exists_size(source_model_date_stat_file):
                print(f"Linking {source_model_date_stat_file} to "
                      +f"{dest_model_date_stat_file}")
                os.symlink(source_model_date_stat_file,
                           dest_model_date_stat_file)
        date_dt = date_dt + datetime.timedelta(days=1)

def condense_model_stat_files(logger, input_dir, output_dir, model, obs,
                              vx_mask, fcst_var_name, fcst_var_level,
                              obs_var_name, obs_var_level, line_type):
    """! Condense the individual date model stat file and
         thin out unneeded data

         Args:
             logger         - logger object
             input_dir      - path to input directory (string)
             output_dir     - path to output directory (string)
             model          - model name (string)
             obs            - observation name (string)
             vx_mask        - verification masking region (string)
             fcst_var_name  - forecast variable name (string)
             fcst_var_level - forecast variable level (string)
             obs_var_name   - observation variable name (string)
             obs_var_leve   - observation variable level (string)
             line_type      - MET line type (string)

         Returns:
    """
    model_stat_files_wildcard = os.path.join(input_dir, model, model+'_*.stat')
    model_stat_files = glob.glob(model_stat_files_wildcard, recursive=True)
    make_dir(output_dir)
    output_file = os.path.join(
        output_dir, f"condensed_stats_{model.lower()}_{line_type.lower()}_"
        +f"{fcst_var_name.lower()}_"
        +f"{fcst_var_level.lower().replace('.','p').replace('-', '_')}_"
        +f"{vx_mask.lower()}.stat"
    )
    if len(model_stat_files) == 0:
        logger.debug(f"No stat files matching "
                     +f"{model_stat_files_wildcard}")
    else:
        if not os.path.exists(output_file):
            logger.info(f"Condensing down stat files matching "
                        +f"{model_stat_files_wildcard}")
            with open(model_stat_files[0]) as msf:
                met_header_cols = msf.readline()
            additional_grep_list = [obs, vx_mask, fcst_var_name,
                                    fcst_var_level, obs_var_name,
                                    line_type]
            additional_grep = ''
            for item in additional_grep_list:
                additional_grep = (additional_grep
                                   +f' | grep "{item} "')
            all_grep_output = ''
            for model_stat_file in model_stat_files:
                logger.info(f"Grep'ing {model_stat_file} for "
                            +f"{model}, {', '.join(additional_grep_list)}")
                grep = subprocess.run(
                    'grep -R "'+model+' " '+model_stat_file+additional_grep,
                    shell=True, capture_output=True, encoding="utf8"
                )
                logger.debug(f"Ran {grep.args}")
                all_grep_output = all_grep_output+grep.stdout
            logger.info(f"Condensed {model} stat files at "
                        +f"{output_file}")
            with open(output_file, 'w') as f:
                f.write(met_header_cols+all_grep_output)
        else:
            logger.info(f"{output_file} exists")

def build_df(job_group, logger, input_dir, output_dir, model_info_dict,
             met_info_dict, fcst_var_name, fcst_var_level, fcst_var_thresh,
             obs_var_name, obs_var_level, obs_var_thresh, line_type,
             grid, vx_mask, interp_method, interp_points, date_type, dates,
             met_format_valid_dates, fhr):
    """! Build the data frame for all model stats,
         Read the model's filtered file, and if doesn't exist
         filter the model file for need information and write file

         Args:
             job_group              - either filter_stats or make_plots
                                      (string)
             logger                 - logger object
             input_dir              - path to input directory (string)
             output_dir             - path to output directory (string)
             model_info_dict        - model infomation dictionary (strings)
             met_info_dict          - MET information dictionary (strings)
             fcst_var_name          - forecast variable name (string)
             fcst_var_level         - forecast variable level (string)
             fcst_var_tresh         - forecast variable treshold (string)
             obs_var_name           - observation variable name (string)
             obs_var_level          - observation variable level (string)
             obs_var_tresh          - observation variable treshold (string)
             line_type              - MET line type (string)
             grid                   - verification grid (string)
             vx_mask                - verification masking region (string)
             interp_method          - interpolation method (string)
             interp_points          - interpolation points (string)
             date_type              - type of date (string, VALID or INIT)
             dates                  - array of dates (datetime)
             met_format_valid_dates - list of valid dates formatted
                                      like they are in MET stat files
             fhr                    - forecast hour (string)

         Returns:
             all_model_df                - dataframe of all the information
    """
    met_version_line_type_col_list = get_met_line_type_cols(
        logger, met_info_dict['root'], met_info_dict['version'], line_type
    )
    for model_num in list(model_info_dict.keys()):
        model_num_name = (
            model_num+'/'+model_info_dict[model_num]['name']
            +'/'+model_info_dict[model_num]['plot_name']
        )
        model_num_df_index = pd.MultiIndex.from_product(
            [[model_num_name], met_format_valid_dates],
            names=['model', 'valid_dates']
        )
        model_dict = model_info_dict[model_num]
        condensed_model_file = os.path.join(
            input_dir, 'condensed_stats_'
            +f"{model_info_dict[model_num]['name'].lower()}_"
            +f"{line_type.lower()}_"
            +f"{fcst_var_name.lower()}_"
            +f"{fcst_var_level.lower().replace('.','p').replace('-', '_')}_"
            +f"{vx_mask.lower()}.stat"
        )
        if len(dates) != 0:
            filtered_model_stat_file_name = (
                'fcst'+model_dict['name']+'_'
                +fcst_var_name+fcst_var_level+fcst_var_thresh+'_'
                +'obs'+model_dict['obs_name']+'_'
                +obs_var_name+obs_var_level+obs_var_thresh+'_'
                +'linetype'+line_type+'_'
                +'grid'+grid+'_'+'vxmask'+vx_mask+'_'
                +'interp'+interp_method+interp_points+'_'
                +date_type.lower()
                +dates[0].strftime('%Y%m%d%H%M%S')+'to'
                +dates[-1].strftime('%Y%m%d%H%M%S')+'_'
                +'fhr'+fhr.zfill(3)
            ).lower().replace('.','p').replace('-', '_')\
            .replace('&&', 'and').replace('||', 'or')\
            .replace('0,*,*', '').replace('*,*', '')+'.stat'
            input_filtered_model_stat_file = os.path.join(
                input_dir, filtered_model_stat_file_name
            )
            output_filtered_model_stat_file = os.path.join(
                output_dir, filtered_model_stat_file_name
            )
            if os.path.exists(input_filtered_model_stat_file):
                filtered_model_stat_file = input_filtered_model_stat_file
            else:
                filtered_model_stat_file = output_filtered_model_stat_file
            if not os.path.exists(filtered_model_stat_file):
                write_filtered_stat_file = True
                read_filtered_stat_file = True
            else:
                write_filtered_stat_file = False
                read_filtered_stat_file = True
            if job_group == 'filter_stats':
                read_filtered_stat_file = False
        else:
            write_filtered_stat_file = False
            read_filtered_stat_file = False
        if os.path.exists(condensed_model_file) and line_type == 'MCTC':
            tmp_df = pd.read_csv(
                condensed_model_file, sep=" ", skiprows=1,
                skipinitialspace=True,
                keep_default_na=False, dtype='str', header=None
            )
            if len(tmp_df) > 0:
                ncat = int(tmp_df[25][0])
                new_met_version_line_type_col_list = []
                for col in met_version_line_type_col_list:
                    if col == '(N_CAT)':
                        new_met_version_line_type_col_list.append('N_CAT')
                    elif col == 'F[0-9]*_O[0-9]*':
                        fcount = 1
                        ocount = 1
                        totcount = 1
                        while totcount <= ncat*ncat:
                            new_met_version_line_type_col_list.append(
                                'F'+str(fcount)+'_'+'O'+str(ocount)
                            )
                            if ocount < ncat:
                                ocount+=1
                            elif ocount == ncat:
                                ocount = 1
                                fcount+=1
                            totcount+=1
                    else:
                        new_met_version_line_type_col_list.append(col)
                met_version_line_type_col_list = (
                    new_met_version_line_type_col_list
                )
        if write_filtered_stat_file:
            if fcst_var_thresh != 'NA':
                fcst_var_thresh_symbol, fcst_var_thresh_letter = (
                    format_thresh(fcst_var_thresh)
                )
            else:
                fcst_var_thresh_symbol = fcst_var_thresh
                fcst_vat_thresh_letter = fcst_var_thresh
            if obs_var_thresh != 'NA':
                obs_var_thresh_symbol, obs_var_thresh_letter = (
                    format_thresh(obs_var_thresh)
                )
            else:
                obs_var_thresh_symbol = obs_var_thresh
                obs_vat_thresh_letter = obs_var_thresh
            if os.path.exists(condensed_model_file):
                condensed_model_df = pd.read_csv(
                    condensed_model_file, sep=" ", skiprows=1,
                    skipinitialspace=True, names=met_version_line_type_col_list,
                    keep_default_na=False, dtype='str', header=None
                )
                filtered_model_df = condensed_model_df[
                    (condensed_model_df['MODEL'] == model_dict['name'])
                     & (condensed_model_df['DESC'] == grid)
                     & (condensed_model_df['FCST_LEAD'] \
                        == fhr.zfill(2)+'0000')
                     & (condensed_model_df['FCST_VAR'] \
                        == fcst_var_name)
                     & (condensed_model_df['FCST_LEV'] \
                        == fcst_var_level)
                     & (condensed_model_df['OBS_VAR'] \
                        == obs_var_name)
                     & (condensed_model_df['OBS_LEV'] \
                        == obs_var_level)
                     & (condensed_model_df['OBTYPE'] == model_dict['obs_name'])
                     & (condensed_model_df['VX_MASK'] \
                        == vx_mask)
                     & (condensed_model_df['INTERP_MTHD'] \
                        == interp_method)
                     & (condensed_model_df['INTERP_PNTS'] \
                        == interp_points)
                     & (condensed_model_df['FCST_THRESH'] \
                        == fcst_var_thresh_symbol)
                     & (condensed_model_df['OBS_THRESH'] \
                        == obs_var_thresh_symbol)
                     & (condensed_model_df['LINE_TYPE'] \
                        == line_type)
                ]
                filtered_model_df = filtered_model_df[
                    filtered_model_df['FCST_VALID_BEG'].isin(met_format_valid_dates)
                ]
                filtered_model_df['FCST_VALID_BEG'] = pd.to_datetime(
                    filtered_model_df['FCST_VALID_BEG'], format='%Y%m%d_%H%M%S'
                )
                filtered_model_df = filtered_model_df.sort_values(by='FCST_VALID_BEG')
                filtered_model_df['FCST_VALID_BEG'] = (
                    filtered_model_df['FCST_VALID_BEG'].dt.strftime('%Y%m%d_%H%M%S')
                )
                filtered_model_df.to_csv(
                    filtered_model_stat_file, header=met_version_line_type_col_list,
                    index=None, sep=' ', mode='w'
                )
            else:
                logger.debug(f"{condensed_model_file} does not exist")
            if os.path.exists(filtered_model_stat_file):
                logger.info(f"Filtered {model_dict['name']} file "
                            +f"at {filtered_model_stat_file}")
            else:
                logger.debug(f"Could not create {filtered_model_stat_file}")
        model_num_df = pd.DataFrame(np.nan, index=model_num_df_index,
                                    columns=met_version_line_type_col_list)
        if read_filtered_stat_file:
            if os.path.exists(filtered_model_stat_file):
                logger.info(f"Reading {filtered_model_stat_file} for "
                            +f"{model_dict['name']}")
                model_stat_file_df = pd.read_csv(
                    filtered_model_stat_file, sep=" ", skiprows=1,
                    skipinitialspace=True, names=met_version_line_type_col_list,
                    na_values=['NA'], header=None
                )
                df_dtype_dict = {}
                float_idx = met_version_line_type_col_list.index('TOTAL')
                for col in met_version_line_type_col_list:
                    col_idx = met_version_line_type_col_list.index(col)
                    if col_idx < float_idx:
                        df_dtype_dict[col] = str
                    else:
                        df_dtype_dict[col] = np.float64
                model_stat_file_df = model_stat_file_df.astype(df_dtype_dict)
                for valid_date in met_format_valid_dates:
                    model_stat_file_df_valid_date_idx_list = (
                        model_stat_file_df.index[
                            model_stat_file_df['FCST_VALID_BEG'] == valid_date
                        ]
                    ).tolist()
                    if len(model_stat_file_df_valid_date_idx_list) == 0:
                        continue
                    model_num_df.loc[(model_num_name, valid_date)] = (
                        model_stat_file_df.loc\
                        [model_stat_file_df_valid_date_idx_list[0]]\
                        [:]
                    )
                # Do conversions if needed
                #### K to F
                if fcst_var_name in ['TMP', 'DPT', 'TMP_ANOM_DAILYAVG',
                                     'SST_DAILYAVG', 'TSOIL'] \
                        and fcst_var_level in ['Z0', 'Z2', 'Z0.1-0'] \
                        and line_type in ['SL1L2', 'SAL1L2']:
                    coef = np.divide(9., 5.)
                    if fcst_var_name == 'TMP_ANOM_DAILYAVG':
                        const = 0
                    elif line_type == 'SAL1L2':
                        const = 0
                    else:
                        const = ((-273.15)*9./5.)+32.
                    convert = True
                    units_old = 'K'
                    units_new = 'F'
                #### m/s to knots
                elif fcst_var_name in ['UGRD', 'VGRD', 'UGRD_VGRD',
                                       'WNDSHR', 'GUST'] \
                        and line_type in ['SL1L2', 'SAL1L2',
                                          'VL1L2', 'VAL1L2']:
                    coef = 1.94384449412
                    const = 0
                    convert = True
                    units_old = 'm/s'
                    units_new = 'kt'
                else:
                    convert = False
                if convert:
                    if line_type == 'SL1L2':
                        fcst_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'FBAR'
                        ]
                        obs_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'OBAR'
                        ]
                        col1_list = ['FBAR', 'OBAR']
                        col2_list = ['FOBAR', 'FFBAR', 'OOBAR']
                    elif line_type == 'SAL1L2':
                        fcst_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'FABAR'
                        ]
                        obs_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'OABAR'
                        ]
                        col1_list = ['FABAR', 'OABAR']
                        col2_list = ['FOABAR', 'FFABAR', 'OOABAR']
                    elif line_type == 'VL1L2':
                        uf_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'UFBAR'
                        ]
                        vf_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'VFBAR'
                        ]
                        uo_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'UOBAR'
                        ]
                        vo_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'VOBAR'
                        ]
                        col1_list = ['UFBAR', 'VFBAR', 'UOBAR', 'VOBAR']
                        col2_list = ['UVFOBAR', 'UVFFBAR', 'UVOOBAR']
                    elif line_type == 'VAL1L2':
                        uf_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'UFABAR'
                        ]
                        vf_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'VFABAR'
                        ]
                        uo_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'UOABAR'
                        ]
                        vo_avg_old = model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, 'VOABAR'
                        ]
                        col1_list = ['UFABAR', 'VFABAR', 'UOABAR', 'VOABAR']
                        col2_list = ['UVFOABAR', 'UVFFABAR', 'UVOOABAR']
                    for col in col1_list:
                        model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, col
                        ] = (coef
                             * model_num_df.loc[model_num_df['FCST_UNITS'] \
                                               == units_old, col]) \
                            + const
                    for col in col2_list:
                        if col in ['FOBAR', 'FOABAR']:
                            const2 =  ((coef * const * fcst_avg_old)
                                       + (coef * const * obs_avg_old))
                        elif col in ['FFBAR', 'FFABAR']:
                            const2 = 2 * (coef * const * fcst_avg_old)
                        elif col in ['OOBAR', 'OOABAR']:
                            const2 = 2 * (coef * const * obs_avg_old)
                        elif col in ['UVFOBAR', 'UVFOABAR']:
                            const2 = (coef * const \
                                      * (uf_avg_old+vf_avg_old
                                         +uo_avg_old+vo_avg_old))
                        elif col in ['UVFFBAR', 'UVFFABAR']:
                            const2 = 2 * (coef * const * \
                                          (uf_avg_old+vf_avg_old))
                        elif col in ['UVOOBAR', 'UVOOABAR']:
                            const2 = 2 * (coef * const * \
                                          (uo_avg_old+vo_avg_old))
                        model_num_df.loc[
                            model_num_df['FCST_UNITS'] == units_old, col
                        ] = (coef**2
                             *model_num_df.loc[model_num_df['FCST_UNITS'] \
                                               == units_old, col]) \
                             + const2 + const**2
                    model_num_df.loc[
                        model_num_df['FCST_UNITS'] == units_old, 'FCST_UNITS'
                    ] = units_new
            else:
                logger.debug(f"{filtered_model_stat_file} does not exist")
        if model_num == 'model1':
            all_model_df = model_num_df
        else:
            all_model_df = pd.concat([all_model_df, model_num_df])
    return all_model_df

def calculate_stat(logger, data_df, line_type, stat):
   """! Calculate the statistic from the data from the
        read in MET .stat file(s)
        Args:
           data_df        - dataframe containing the model(s)
                            information from the MET .stat
                            files
           line_type      - MET line type (string)
           stat           - statistic to calculate (string)

        Returns:
           stat_df       - dataframe of the statistic
           stat_array    - array of the statistic
   """
   if line_type == 'SL1L2':
       FBAR = data_df.loc[:]['FBAR']
       OBAR = data_df.loc[:]['OBAR']
       FOBAR = data_df.loc[:]['FOBAR']
       FFBAR = data_df.loc[:]['FFBAR']
       OOBAR = data_df.loc[:]['OOBAR']
   elif line_type == 'SAL1L2':
       FABAR = data_df.loc[:]['FABAR']
       OABAR = data_df.loc[:]['OABAR']
       FOABAR = data_df.loc[:]['FOABAR']
       FFABAR = data_df.loc[:]['FFABAR']
       OOABAR = data_df.loc[:]['OOABAR']
   elif line_type == 'CNT':
       FBAR = data_df.loc[:]['FBAR']
       FBAR_NCL = data_df.loc[:]['FBAR_NCL']
       FBAR_NCU = data_df.loc[:]['FBAR_NCU']
       FBAR_BCL = data_df.loc[:]['FBAR_BCL']
       FBAR_BCU = data_df.loc[:]['FBAR_BCU']
       FSTDEV = data_df.loc[:]['FSTDEV']
       FSTDEV_NCL = data_df.loc[:]['FSTDEV_NCL']
       FSTDEV_NCU = data_df.loc[:]['FSTDEV_NCU']
       FSTDEV_BCL = data_df.loc[:]['FSTDEV_BCL']
       FSTDEV_BCU = data_df.loc[:]['FSTDEV_BCU']
       OBAR = data_df.loc[:]['OBAR']
       OBAR_NCL = data_df.loc[:]['OBAR_NCL']
       OBAR_NCU = data_df.loc[:]['OBAR_NCU']
       OBAR_BCL = data_df.loc[:]['OBAR_BCL']
       OBAR_BCU = data_df.loc[:]['OBAR_BCU']
       OSTDEV = data_df.loc[:]['OSTDEV']
       OSTDEV_NCL = data_df.loc[:]['OSTDEV_NCL']
       OSTDEV_NCU = data_df.loc[:]['OSTDEV_NCU']
       OSTDEV_BCL = data_df.loc[:]['OSTDEV_BCL']
       OSTDEV_BCU = data_df.loc[:]['OSTDEV_BCU']
       PR_CORR = data_df.loc[:]['PR_CORR']
       PR_CORR_NCL = data_df.loc[:]['PR_CORR_NCL']
       PR_CORR_NCU = data_df.loc[:]['PR_CORR_NCU']
       PR_CORR_BCL = data_df.loc[:]['PR_CORR_BCL']
       PR_CORR_BCU = data_df.loc[:]['PR_CORR_BCU']
       SP_CORR = data_df.loc[:]['SP_CORR']
       KT_CORR = data_df.loc[:]['KT_CORR']
       RANKS = data_df.loc[:]['RANKS']
       FRANKS_TIES = data_df.loc[:]['FRANKS_TIES']
       ORANKS_TIES = data_df.loc[:]['ORANKS_TIES']
       ME = data_df.loc[:]['ME']
       ME_NCL = data_df.loc[:]['ME_NCL']
       ME_NCU = data_df.loc[:]['ME_NCU']
       ME_BCL = data_df.loc[:]['ME_BCL']
       ME_BCU = data_df.loc[:]['ME_BCU']
       ESTDEV = data_df.loc[:]['ESTDEV']
       ESTDEV_NCL = data_df.loc[:]['ESTDEV_NCL']
       ESTDEV_NCU = data_df.loc[:]['ESTDEV_NCU']
       ESTDEV_BCL = data_df.loc[:]['ESTDEV_BCL']
       ESTDEV_BCU = data_df.loc[:]['ESTDEV_BCU']
       MBIAS = data_df.loc[:]['MBIAS']
       MBIAS_BCL = data_df.loc[:]['MBIAS_BCL']
       MBIAS_BCU = data_df.loc[:]['MBIAS_BCU']
       MAE = data_df.loc[:]['MAE']
       MAE_BCL = data_df.loc[:]['MAE_BCL']
       MAE_BCU = data_df.loc[:]['MAE_BCU']
       MSE = data_df.loc[:]['MSE']
       MSE_BCL = data_df.loc[:]['MSE_BCL']
       MSE_BCU = data_df.loc[:]['MSE_BCU']
       BCRMSE = data_df.loc[:]['BCRMSE']
       BCRMSE_BCL = data_df.loc[:]['BCRMSE_BCL']
       BCRMSE_BCU = data_df.loc[:]['BCRMSE_BCU']
       RMSE = data_df.loc[:]['RMSE']
       RMSE_BCL = data_df.loc[:]['RMSE_BCL']
       RMSE_BCU = data_df.loc[:]['RMSE_BCU']
       E10 = data_df.loc[:]['E10']
       E10_BCL = data_df.loc[:]['E10_BCL']
       E10_BCU = data_df.loc[:]['E10_BCU']
       E25 = data_df.loc[:]['E25']
       E25_BCL = data_df.loc[:]['E25_BCL']
       E25_BCU = data_df.loc[:]['E25_BCU']
       E50 = data_df.loc[:]['E50']
       E50_BCL = data_df.loc[:]['E50_BCL']
       E50_BCU = data_df.loc[:]['E50_BCU']
       E75 = data_df.loc[:]['E75']
       E75_BCL = data_df.loc[:]['E75_BCL']
       E75_BCU = data_df.loc[:]['E75_BCU']
       E90 = data_df.loc[:]['E90']
       E90_BCL = data_df.loc[:]['E90_BCL']
       E90_BCU = data_df.loc[:]['E90_BCU']
       IQR = data_df.loc[:]['IQR']
       IQR_BCL = data_df.loc[:]['IQR_BCL']
       IQR_BCU = data_df.loc[:]['IQR_BCU']
       MAD = data_df.loc[:]['MAD']
       MAD_BCL = data_df.loc[:]['MAD_BCL']
       MAD_BCU = data_df.loc[:]['MAD_BCU']
       ANOM_CORR_NCL = data_df.loc[:]['ANOM_CORR_NCL']
       ANOM_CORR_NCU = data_df.loc[:]['ANOM_CORR_NCU']
       ANOM_CORR_BCL = data_df.loc[:]['ANOM_CORR_BCL']
       ANOM_CORR_BCU = data_df.loc[:]['ANOM_CORR_BCU']
       ME2 = data_df.loc[:]['ME2']
       ME2_BCL = data_df.loc[:]['ME2_BCL']
       ME2_BCU = data_df.loc[:]['ME2_BCU']
       MSESS = data_df.loc[:]['MSESS']
       MSESS_BCL = data_df.loc[:]['MSESS_BCL']
       MSESS_BCU = data_df.loc[:]['MSESS_BCU']
       RMSFA = data_df.loc[:]['RMSFA']
       RMSFA_BCL = data_df.loc[:]['RMSFA_BCL']
       RMSFA_BCU = data_df.loc[:]['RMSFA_BCU']
       RMSOA = data_df.loc[:]['RMSOA']
       RMSOA_BCL = data_df.loc[:]['RMSOA_BCL']
       RMSOA_BCU = data_df.loc[:]['RMSOA_BCU']
       ANOM_CORR_UNCNTR = data_df.loc[:]['ANOM_CORR_UNCNTR']
       ANOM_CORR_UNCNTR_BCL = data_df.loc[:]['ANOM_CORR_UNCNTR_BCL']
       ANOM_CORR_UNCNTR_BCU = data_df.loc[:]['ANOM_CORR_UNCNTR_BCU']
       SI = data_df.loc[:]['SI']
       SI_BCL = data_df.loc[:]['SI_BCL']
       SI_BCU = data_df.loc[:]['SI_BCU']
   elif line_type == 'GRAD':
       FGBAR = data_df.loc[:]['FGBAR']
       OGBAR = data_df.loc[:]['OGBAR']
       MGBAR = data_df.loc[:]['MGBAR']
       EGBAR = data_df.loc[:]['EGBAR']
       S1 = data_df.loc[:]['S1']
       S1_OG = data_df.loc[:]['S1_OG']
       FGOG_RATIO = data_df.loc[:]['FGOG_RATIO']
       DX = data_df.loc[:]['DX']
       DY = data_df.loc[:]['DY']
   elif line_type == 'FHO':
       F_RATE = data_df.loc[:]['F_RATE']
       H_RATE = data_df.loc[:]['H_RATE']
       O_RATE = data_df.loc[:]['O_RATE']
   elif line_type in ['CTC', 'NBRCTC']:
       FY_OY = data_df.loc[:]['FY_OY']
       FY_ON = data_df.loc[:]['FY_ON']
       FN_OY = data_df.loc[:]['FN_OY']
       FN_ON = data_df.loc[:]['FN_ON']
       if line_type == 'CTC':
           EC_VALUE = data_df.loc[:]['EC_VALUE']
   elif line_type in ['CTS', 'NBRCTS']:
       BASER = data_df.loc[:]['BASER']
       BASER_NCL = data_df.loc[:]['BASER_NCL']
       BASER_NCU = data_df.loc[:]['BASER_NCU']
       BASER_BCL = data_df.loc[:]['BASER_BCL']
       BASER_BCU = data_df.loc[:]['BASER_BCU']
       FMEAN = data_df.loc[:]['FMEAN']
       FMEAN_NCL = data_df.loc[:]['FMEAN_NCL']
       FMEAN_NCU = data_df.loc[:]['FMEAN_NCU']
       FMEAN_BCL = data_df.loc[:]['FMEAN_BCL']
       FMEAN_BCU = data_df.loc[:]['FMEAN_BCU']
       ACC = data_df.loc[:]['ACC']
       ACC_NCL = data_df.loc[:]['ACC_NCL']
       ACC_NCU = data_df.loc[:]['ACC_NCU']
       ACC_BCL = data_df.loc[:]['ACC_BCL']
       ACC_BCU = data_df.loc[:]['ACC_BCU']
       FBIAS = data_df.loc[:]['FBIAS']
       FBIAS_BCL = data_df.loc[:]['FBIAS_BCL']
       FBIAS_BCU = data_df.loc[:]['FBIAS_BCU']
       PODY = data_df.loc[:]['PODY']
       PODY_NCL = data_df.loc[:]['PODY_NCL']
       PODY_NCU = data_df.loc[:]['PODY_NCU']
       PODY_BCL = data_df.loc[:]['PODY_BCL']
       PODY_BCU = data_df.loc[:]['PODY_BCU']
       PODN = data_df.loc[:]['PODN']
       PODN_NCL = data_df.loc[:]['PODN_NCL']
       PODN_NCU = data_df.loc[:]['PODN_NCU']
       PODN_BCL = data_df.loc[:]['PODN_BCL']
       PODN_BCU = data_df.loc[:]['PODN_BCU']
       POFD = data_df.loc[:]['POFD']
       POFD_NCL = data_df.loc[:]['POFD_NCL']
       POFD_NCU = data_df.loc[:]['POFD_NCU']
       POFD_BCL = data_df.loc[:]['POFD_BCL']
       POFD_BCU = data_df.loc[:]['POFD_BCU']
       FAR = data_df.loc[:]['FAR']
       FAR_NCL = data_df.loc[:]['FAR_NCL']
       FAR_NCU = data_df.loc[:]['FAR_NCU']
       FAR_BCL = data_df.loc[:]['FAR_BCL']
       FAR_BCU = data_df.loc[:]['FAR_BCU']
       CSI = data_df.loc[:]['CSI']
       CSI_NCL = data_df.loc[:]['CSI_NCL']
       CSI_NCU = data_df.loc[:]['CSI_NCU']
       CSI_BCL = data_df.loc[:]['CSI_BCL']
       CSI_BCU = data_df.loc[:]['CSI_BCU']
       GSS = data_df.loc[:]['GSS']
       GSS_BCL = data_df.loc[:]['GSS_BCL']
       GSS_BCU = data_df.loc[:]['GSS_BCU']
       HK = data_df.loc[:]['HK']
       HK_NCL = data_df.loc[:]['HK_NCL']
       HK_NCU = data_df.loc[:]['HK_NCU']
       HK_BCL = data_df.loc[:]['HK_BCL']
       HK_BCU = data_df.loc[:]['HK_BCU']
       HSS = data_df.loc[:]['HSS']
       HSS_BCL = data_df.loc[:]['HSS_BCL']
       HSS_BCU = data_df.loc[:]['HSS_BCU']
       ODDS = data_df.loc[:]['ODDS']
       ODDS_NCL = data_df.loc[:]['ODDS_NCL']
       ODDS_NCU = data_df.loc[:]['ODDS_NCU']
       ODDS_BCL = data_df.loc[:]['ODDS_BCL']
       ODDS_BCU = data_df.loc[:]['ODDS_BCU']
       LODDS = data_df.loc[:]['LODDS']
       LODDS_NCL = data_df.loc[:]['LODDS_NCL']
       LODDS_NCU = data_df.loc[:]['LODDS_NCU']
       LODDS_BCL = data_df.loc[:]['LODDS_BCL']
       LODDS_BCU = data_df.loc[:]['LODDS_BCU']
       ORSS = data_df.loc[:]['ORSS']
       ORSS_NCL = data_df.loc[:]['ORSS_NCL']
       ORSS_NCU = data_df.loc[:]['ORSS_NCU']
       ORSS_BCL = data_df.loc[:]['ORSS_BCL']
       ORSS_BCU = data_df.loc[:]['ORSS_BCU']
       EDS = data_df.loc[:]['EDS']
       EDS_NCL = data_df.loc[:]['EDS_NCL']
       EDS_NCU = data_df.loc[:]['EDS_NCU']
       EDS_BCL = data_df.loc[:]['EDS_BCL']
       EDS_BCU = data_df.loc[:]['EDS_BCU']
       SEDS = data_df.loc[:]['SEDS']
       SEDS_NCL = data_df.loc[:]['SEDS_NCL']
       SEDS_NCU = data_df.loc[:]['SEDS_NCU']
       SEDS_BCL = data_df.loc[:]['SEDS_BCL']
       SEDS_BCU = data_df.loc[:]['SEDS_BCU']
       EDI = data_df.loc[:]['EDI']
       EDI_NCL = data_df.loc[:]['EDI_NCL']
       EDI_NCU = data_df.loc[:]['EDI_NCU']
       EDI_BCL = data_df.loc[:]['EDI_BCL']
       EDI_BCU = data_df.loc[:]['EDI_BCU']
       SEDI = data_df.loc[:]['SEDI']
       SEDI_NCL = data_df.loc[:]['SEDI_NCL']
       SEDI_NCU = data_df.loc[:]['SEDI_NCU']
       SEDI_BCL = data_df.loc[:]['SEDI_BCL']
       SEDI_BCU = data_df.loc[:]['SEDI_BCU']
       BAGSS = data_df.loc[:]['BAGSS']
       BAGSS_BCL = data_df.loc[:]['BAGSS_BCL']
       BAGSS_BCU = data_df.loc[:]['BAGSS_BCU']
       if line_type == 'CTS':
           EC_VALUE = data_df.loc[:]['EC_VALUE']
   elif line_type == 'MCTC':
       F1_O1 = data_df.loc[:]['F1_O1']
   elif line_type == 'NBRCNT':
       FBS = data_df.loc[:]['FBS']
       FBS_BCL = data_df.loc[:]['FBS_BCL']
       FBS_BCU = data_df.loc[:]['FBS_BCU']
       FSS = data_df.loc[:]['FSS']
       FSS_BCL = data_df.loc[:]['FSS_BCL']
       FSS_BCU = data_df.loc[:]['FSS_BCU']
       AFSS = data_df.loc[:]['AFSS']
       AFSS_BCL = data_df.loc[:]['AFSS_BCL']
       AFSS_BCU = data_df.loc[:]['AFSS_BCU']
       UFSS = data_df.loc[:]['UFSS']
       UFSS_BCL = data_df.loc[:]['UFSS_BCL']
       UFSS_BCU = data_df.loc[:]['UFSS_BCU']
       F_RATE = data_df.loc[:]['F_RATE']
       F_RATE_BCL = data_df.loc[:]['F_RATE_BCL']
       F_RATE_BCU = data_df.loc[:]['F_RATE_BCU']
       O_RATE = data_df.loc[:]['O_RATE']
       O_RATE_BCL = data_df.loc[:]['O_RATE_BCL']
       O_RATE_BCU = data_df.loc[:]['O_RATE_BCU']
   elif line_type == 'VL1L2':
       UFBAR = data_df.loc[:]['UFBAR']
       VFBAR = data_df.loc[:]['VFBAR']
       UOBAR = data_df.loc[:]['UOBAR']
       VOBAR = data_df.loc[:]['VOBAR']
       UVFOBAR = data_df.loc[:]['UVFOBAR']
       UVFFBAR = data_df.loc[:]['UVFFBAR']
       UVOOBAR = data_df.loc[:]['UVOOBAR']
       F_SPEED_BAR = data_df.loc[:]['F_SPEED_BAR']
       O_SPEED_BAR = data_df.loc[:]['O_SPEED_BAR']
       TOTAL_DIR = data_df.loc[:]['TOTAL_DIR']
       DIR_ME = data_df.loc[:]['DIR_ME']
       DIR_MAE = data_df.loc[:]['DIR_MAE']
       DIR_MSE = data_df.loc[:]['DIR_MSE']
   elif line_type == 'VAL1L2':
       UFABAR = data_df.loc[:]['UFABAR']
       VFABAR = data_df.loc[:]['VFABAR']
       UOABAR = data_df.loc[:]['UOABAR']
       VOABAR = data_df.loc[:]['VOABAR']
       UVFOABAR = data_df.loc[:]['UVFOABAR']
       UVFFABAR = data_df.loc[:]['UVFFABAR']
       UVOOABAR = data_df.loc[:]['UVOOABAR']
       FA_SPEED_BAR = data_df.loc[:]['FA_SPEED_BAR']
       OA_SPEED_BAR = data_df.loc[:]['OA_SPEED_BAR']
       TOTAL_DIR = data_df.loc[:]['TOTAL_DIR']
       DIRA_ME = data_df.loc[:]['DIRA_ME']
       DIRA_MAE = data_df.loc[:]['DIRA_MAE']
       DIRA_MSE = data_df.loc[:]['DIRA_MSE']
   elif line_type == 'VCNT':
       FBAR = data_df.loc[:]['FBAR']
       OBAR = data_df.loc[:]['OBAR']
       FS_RMS = data_df.loc[:]['FS_RMS']
       OS_RMS = data_df.loc[:]['OS_RMS']
       MSVE = data_df.loc[:]['MSVE']
       RMSVE = data_df.loc[:]['RMSVE']
       FSTDEV = data_df.loc[:]['FSTDEV']
       OSTDEV = data_df.loc[:]['OSTDEV']
       FDIR = data_df.loc[:]['FDIR']
       ORDIR = data_df.loc[:]['ODIR']
       FBAR_SPEED = data_df.loc[:]['FBAR_SPEED']
       OBAR_SPEED = data_df.loc[:]['OBAR_SPEED']
       VDIFF_SPEED = data_df.loc[:]['VDIFF_SPEED']
       VDIFF_DIR = data_df.loc[:]['VDIFF_DIR']
       SPEED_ERR = data_df.loc[:]['SPEED_ERR']
       SPEED_ABSERR = data_df.loc[:]['SPEED_ABSERR']
       DIR_ERR = data_df.loc[:]['DIR_ERR']
       DIR_ABSERR = data_df.loc[:]['DIR_ABSERR']
       ANOM_CORR = data_df.loc[:]['ANOM_CORR']
       ANOM_CORR_NCL = data_df.loc[:]['ANOM_CORR_NCL']
       ANOM_CORR_NCU = data_df.loc[:]['ANOM_CORR_NCU']
       ANOM_CORR_BCL = data_df.loc[:]['ANOM_CORR_BCL']
       ANOM_CORR_BCU = data_df.loc[:]['ANOM_CORR_BCU']
       ANOM_CORR_UNCNTR = data_df.loc[:]['ANOM_CORR_UNCNTR']
       ANOM_CORR_UNCNTR_BCL = data_df.loc[:]['ANOM_CORR_UNCNTR_BCL']
       ANOM_CORR_UNCNTR_BCU = data_df.loc[:]['ANOM_CORR_UNCNTR_BCU']
       TOTAL_DIR = data_df.loc[:]['TOTAL_DIR']
       DIR_ME = data_df.loc[:]['DIR_ME']
       DIR_ME_BCL = data_df.loc[:]['DIR_ME_BCL']
       DIR_ME_BCU = data_df.loc[:]['DIR_ME_BCU']
       DIR_MAE = data_df.loc[:]['DIR_MAE']
       DIR_MAE_BCL = data_df.loc[:]['DIR_MAE_BCL']
       DIR_MAE_BCU = data_df.loc[:]['DIR_MAE_BCU']
       DIR_MSE = data_df.loc[:]['DIR_MSE']
       DIR_MSE_BCL = data_df.loc[:]['DIR_MSE_BCL']
       DIR_MSE_BCU = data_df.loc[:]['DIR_MSE_BCU']
       DIR_RMSE = data_df.loc[:]['DIR_RMSE']
       DIR_RMSE_BCL = data_df.loc[:]['DIR_RMSE_BCL']
       DIR_RMSE_BCU = data_df.loc[:]['DIR_RMSE_BCU']
   if stat == 'ACC': # Anomaly Correlation Coefficient
       if line_type == 'SAL1L2':
           radicand = (FFABAR - FABAR*FABAR)*(OOABAR - OABAR*OABAR)
           radicand[radicand<0] = np.nan
           stat_df = (FOABAR - FABAR*OABAR) \
                     /np.sqrt(radicand)
       elif line_type in ['CNT', 'VCNT']:
           stat_df = ANOM_CORR
       elif line_type == 'VAL1L2':
           radicand = UVFFABAR*UVOOABAR
           radicand[radicand<0] = np.nan
           stat_df = UVFOABAR/np.sqrt(radicand)
   elif stat in ['BIAS', 'ME']: # Bias/Mean Error
       if line_type == 'SL1L2':
           stat_df = FBAR - OBAR
       elif line_type == 'CNT':
           stat_df = ME
       elif line_type == 'VL1L2':
           radicand1 = UVFFBAR
           radicand1[radicand1<0] = np.nan
           radicand2 = UVOOBAR
           radicand2[radicand2<0] = np.nan
           stat_df = np.sqrt(radicand1) - np.sqrt(radicand2)
   elif stat == 'CORR': # Pearson Correlation Coefficient
       if line_type == 'SL1L2':
           var_f = FFBAR - FBAR*FBAR
           var_o = OOBAR - OBAR*OBAR
           radicand = var_f*var_o
           radicand[radicand<0] = np.nan
           stat_df = (FOBAR - (FBAR*OBAR))/np.sqrt(radicand)
   elif stat == 'CSI': # Critical Success Index'
       if line_type == 'CTC':
           stat_df = FY_OY/(FY_OY + FY_ON + FN_OY)
   elif stat == 'F1_O1': # Count of forecast category 1 and observation category 1
       if line_type == 'MCTC':
           stat_df = F1_O1
   elif stat in ['ETS', 'GSS']: # Equitable Threat Score/Gilbert Skill Score
       if line_type == 'CTC':
           TOTAL = FY_OY + FY_ON + FN_OY + FN_ON
           C = ((FY_OY + FY_ON)*(FY_OY + FN_OY))/TOTAL
           stat_df = (FY_OY - C)/(FY_OY + FY_ON + FN_OY - C)
       elif line_type == 'CTS':
           stat_df = GSS
   elif stat == 'FBAR': # Forecast Mean
       if line_type == 'SL1L2':
           stat_df = FBAR
   elif stat == 'FBIAS': # Frequency Bias
       if line_type == 'CTC':
           stat_df = (FY_OY + FY_ON)/(FY_OY + FN_OY)
       elif line_type == 'CTS':
           stat_df = FBIAS
   elif stat == 'FSS': # Fraction Skill Score
       if line_type == 'NBRCNT':
           stat_df = FSS
   elif stat == 'FY_OY': # Forecast Yes/Obs Yes
       if line_type == 'CTC':
           stat_df = FY_OY
   elif stat == 'HSS': # Heidke Skill Score
       if line_type == 'CTC':
           TOTAL = FY_OY + FY_ON + FN_OY + FN_ON
           CA = (FY_OY+FY_ON)*(FY_OY+FN_OY)
           CB = (FN_OY+FN_ON)*(FY_ON+FN_ON)
           C = (CA + CB)/TOTAL
           stat_df = (FY_OY + FN_ON - C)/(TOTAL - C)
   elif stat == 'OBAR': # Observation Mean
       if line_type == 'SL1L2':
           stat_df = OBAR
   elif stat == 'POD': # Probability of Detection
       if line_type == 'CTC':
           stat_df = FY_OY/(FY_OY + FN_OY)
   elif stat == 'RMSE': # Root Mean Square Error
       if line_type == 'SL1L2':
           radicand = FFBAR + OOBAR - 2*FOBAR
           radicand[radicand<0] = np.nan
           stat_df = np.sqrt(radicand)
       elif line_type == 'CNT':
           stat_df = RMSE
       elif line_type == 'VL1L2':
           radicand = UVFFBAR + UVOOBAR - 2*UVFOBAR
           radicand[radicand<0] = np.nan
           stat_df = np.sqrt(radicand)
   elif stat == 'S1': # S1
       if line_type == 'GRAD':
           stat_df = S1
   elif stat == 'SRATIO': # Success Ratio
       if line_type == 'CTC':
           stat_df = 1 - (FY_ON/(FY_ON + FY_OY))
   elif stat == 'STDEV_ERR': # Standard Deviation of Error
       if line_type == 'SL1L2':
           radicand = (
               FFBAR + OOBAR - FBAR*FBAR - OBAR*OBAR - 2*FOBAR + 2*FBAR*OBAR
           )
           radicand[radicand<0] = np.nan
           stat_df = np.sqrt(radicand)
   else:
        logger.error(stat+" is not an option")
        sys.exit(1)
   idx = 0
   idx_dict = {}
   while idx < stat_df.index.nlevels:
       idx_dict['index'+str(idx)] = len(
           stat_df.index.get_level_values(idx).unique()
       )
       idx+=1
   if stat_df.index.nlevels == 1:
       stat_array = stat_df.values.reshape(
           idx_dict['index0']
       )
   elif stat_df.index.nlevels == 2:
       stat_array = stat_df.values.reshape(
           idx_dict['index0'], idx_dict['index1']
       )
   return stat_df, stat_array

def calculate_average(logger, average_method, line_type, stat, df):
    """! Calculate average of dataset

         Args:
             logger                 - logger object
             average_method         - method to use to
                                      calculate the
                                      average (string:
                                      mean, aggregation)
             line_type              - line type to calculate
                                      stat from
             stat                   - statistic to calculate
                                      (string)
             df                     - dataframe of values
         Returns:
    """
    average_value = np.nan
    if average_method == 'mean':
        average_value = np.ma.masked_invalid(df).mean()
    elif average_method == 'aggregation':
        if not df.isnull().values.all():
            ndays = (
                len(df.loc[:,'TOTAL'])
                -np.ma.count_masked(np.ma.masked_invalid(df.loc[:,'TOTAL']))
            )
            avg_df, avg_array = calculate_stat(
                logger, df.loc[:,'TOTAL':].agg(['sum'])/ndays,
                line_type, stat
            )
            average_value = avg_array[0]
    else:
        logger.warning(f"{average_method} not recongnized..."
                       +"use mean, or aggregation...returning NaN")
    return average_value
