#!/usr/bin/env python3
'''
Name: global_det_atmos_util.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This contains many functions used across global_det atmos.
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
from time import sleep

def run_shell_command(command):
    """! Run shell command

         Args:
             command - list of agrument entries (string)

         Returns:

    """
    print("Running  "+' '.join(command))
    if any(mark in ' '.join(command) for mark in ['"', "'", '|', '*', '>']):
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
                             os.environ['STEP'],
                             os.environ['COMPONENT'],
                             os.environ['RUN']+'_'+os.environ['VERIF_CASE'],
                             conf_file_name)
    if not os.path.exists(conf_file):
        print("FATAL ERROR: "+conf_file+" DOES NOT EXIST")
        sys.exit(1)
    metplus_cmd = run_metplus+' -c '+machine_conf+' -c '+conf_file
    return metplus_cmd

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

def log_missing_file_model(log_missing_file, missing_file, model, init_dt,
                           fhr):
    """! This writes a missing model file to a log

         Args:
             log_missing_file - log of missing file (string)
             missing_file     - missing file path (string)
             model            - model name (string)
             init_dt          - initialization date (datetime)
             fhr              - forecast hour (string)
    """
    if not os.path.exists(log_missing_file):
        with open(log_missing_file, "w") as lmf:
            lmf.write("#!/bin/bash\n")
            if fhr == 'anl':
                lmf.write(f'export subject="{model.upper()} Analysis '
                          +'Data Missing for EVS global_det"\n')
                lmf.write(f'echo "Warning: No {model.upper()} analysis was '
                          +f'available for valid date {init_dt:%Y%m%d%H}" '
                          +'> mailmsg\n')
            else:
                lmf.write(f'export subject="F{fhr} {model.upper()} Forecast '
                          +'Data Missing for EVS global_det"\n')
                lmf.write(f'echo "Warning: No {model.upper()} forecast was '
                          +f'available for {init_dt:%Y%m%d%H}f{fhr}" '
                          +'> mailmsg\n')
            lmf.write(f'echo "Missing file is {missing_file}" >> mailmsg\n')
            lmf.write(f'echo "Job ID: $jobid" >> mailmsg\n')
            lmf.write(f'cat mailmsg | mail -s "$subject" $MAILTO\n')
        os.chmod(log_missing_file, 0o755)

def log_missing_file_truth(log_missing_file, missing_file, obs, valid_dt):
    """! This writes a missing truth file to a log

         Args:
             log_missing_file - log of missing file (string)
             missing_file     - missing file path (string)
             obs              - observation name (string)
             valid_dt         - initialization date (datetime)
    """
    if not os.path.exists(log_missing_file):
        with open(log_missing_file, "a") as lmf:
            lmf.write("#!/bin/bash\n")
            lmf.write(f'export subject="{obs} Data Missing for EVS '
                      +'global_det"\n')
            lmf.write(f'echo "Warning: No {obs} data was available for '
                      +f'valid date {valid_dt:%Y%m%d%H}" > mailmsg\n')
            lmf.write(f'echo "Missing file is {missing_file}" >> mailmsg\n')
            lmf.write(f'echo "Job ID: $jobid" >> mailmsg\n')
            lmf.write(f'cat mailmsg | mail -s "$subject" $MAILTO\n')
        os.chmod(log_missing_file, 0o755)


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

def convert_grib1_grib2(grib1_file, grib2_file):
    """! Converts GRIB1 data to GRIB2

         Args:
             grib1_file - string of the path to
                          the GRIB1 file to
                          convert (string)
             grib2_file - string of the path to
                          save the converted GRIB2
                          file (string)
         Returns:
    """
    print("Converting GRIB1 file "+grib1_file+" "
          +"to GRIB2 file "+grib2_file)
    cnvgrib = os.environ['CNVGRIB']
    os.system(cnvgrib+' -g12 '+grib1_file+' '
              +grib2_file+' > /dev/null 2>&1')

def convert_grib2_grib1(grib2_file, grib1_file):
    """! Converts GRIB2 data to GRIB1

         Args:
             grib2_file - string of the path to
                          the GRIB2 file to
                          convert
             grib1_file - string of the path to
                          save the converted GRIB1
                          file
         Returns:
    """
    print("Converting GRIB2 file "+grib2_file+" "
          +"to GRIB1 file "+grib1_file)
    cnvgrib = os.environ['CNVGRIB']
    os.system(cnvgrib+' -g21 '+grib2_file+' '
              +grib1_file+' > /dev/null 2>&1')

def convert_grib2_grib2(grib2_fileA, grib2_fileB):
    """! Converts GRIB2 data to GRIB2

         Args:
             grib2_fileA - string of the path to
                           the GRIB2 file to
                           convert
             grib2_fileB - string of the path to
                           save the converted GRIB2
                           file
         Returns:
    """
    print("Converting GRIB2 file "+grib2_fileA+" "
          +"to GRIB2 file "+grib2_fileB)
    cnvgrib = os.environ['CNVGRIB']
    os.system(cnvgrib+' -g22 '+grib2_fileA+' '
              +grib2_fileB+' > /dev/null 2>&1')

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
                         initalization, and forecast hour
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

def prep_prod_fnmoc_file(source_file, dest_file, init_dt, forecast_hour,
                         prep_method, log_missing_file):
    """! Do prep work for FNMOC production files

         Args:
             source_file      - source file format (string)
             dest_file        - destination file (string)
             init_dt          - initialization date (datetime)
             forecast_hour    - forecast hour (string)
             prep_method      - name of prep method to do
                                (string)
             log_missing_file - text file path to write that
                                production file is missing (string)

         Returns:
    """
    # Environment variables and executables
    # Working file names
    prepped_file = os.path.join(os.getcwd(),
                                'atmos.'+dest_file.rpartition('/')[2])
    # Prep file
    if check_file_exists_size(source_file):
        convert_grib2_grib2(source_file, prepped_file)
    else:
        log_missing_file_model(log_missing_file, source_file, 'fnmoc',
                               init_dt, str(forecast_hour).zfill(3))
    copy_file(prepped_file, dest_file)

def prep_prod_imd_file(source_file, dest_file, init_dt, forecast_hour,
                       prep_method, log_missing_file):
    """! Do prep work for IMD production files

         Args:
             source_file      - source file format (string)
             dest_file        - destination file (string)
             init_dt          - initialization date (datetime)
             forecast_hour    - forecast hour (string)
             prep_method      - name of prep method to do
                                (string)
             log_missing_file - text file path to write that
                                production file is missing (string)

         Returns:
    """
    # Environment variables and executables
    WGRIB2 = os.environ['WGRIB2']
    # Working file names
    prepped_file = os.path.join(os.getcwd(),
                                'atmos.'+dest_file.rpartition('/')[2])
    # Prep file
    if check_file_exists_size(source_file):
        chk_corrupt = subprocess.run(
            f"{WGRIB2} {source_file}  1> /dev/null 2>&1", shell=True
        )
        if chk_corrupt.returncode != 0:
            print(f"WARNING: {source_file} is corrupt")
        else:
            copy_file(source_file, prepped_file)
    else:
        log_missing_file_model(log_missing_file, source_file, 'imd',
                               init_dt, str(forecast_hour).zfill(3))
    copy_file(prepped_file, dest_file)

def prep_prod_jma_file(source_file_format, dest_file, init_dt, forecast_hour,
                       prep_method, log_missing_file):
    """! Do prep work for JMA production files

         Args:
             source_file_format - source file format (string)
             dest_file          - destination file (string)
             init_dt            - initialization date (datetime)
             forecast_hour      - forecast hour (string)
             prep_method        - name of prep method to do
                                  (string)
             log_missing_file   - text file path to write that
                                  production file is missing (string)

         Returns:
    """
    # Environment variables and executables
    WGRIB = os.environ['WGRIB']
    EXECevs = os.environ['EXECevs']
    JMAMERGE = os.path.join(EXECevs, 'jma_merge')
    # Working file names
    prepped_file = os.path.join(os.getcwd(),
                                'atmos.'+dest_file.rpartition('/')[2])
    working_file1 = prepped_file+'.tmp1'
    working_file2 = prepped_file+'.tmp2'
    # Prep file
    if prep_method == 'full':
        if forecast_hour == 'anl':
            wgrib_fhr = ':anl'
        elif int(forecast_hour) == 0:
            wgrib_fhr = ':anl'
        else:
            wgrib_fhr = ':'+forecast_hour+'hr'
        for hem in ['n', 's']:
            hem_source_file = source_file_format.replace('{hem?fmt=str}', hem)
            if hem == 'n':
                working_file = working_file1
            elif hem == 's':
                working_file = working_file2
            if check_file_exists_size(hem_source_file):
                run_shell_command(
                    [WGRIB+' '+hem_source_file+' | grep "'+wgrib_fhr+'" | '
                     +WGRIB+' '+hem_source_file+' -i -grib -o '
                     +working_file]
                )
            else:
                log_missing_file_model(log_missing_file, hem_source_file,
                                       'jma', init_dt,
                                       str(forecast_hour).zfill(3))
        if check_file_exists_size(working_file1) \
                and check_file_exists_size(working_file2):
            run_shell_command(
                [JMAMERGE, working_file1, working_file2, prepped_file]
            )
    elif 'precip' in prep_method:
        source_file = source_file_format
        if check_file_exists_size(source_file):
            run_shell_command(
                [WGRIB+' '+source_file+' | grep "0-'
                 +forecast_hour+'hr" | '+WGRIB+' '+source_file
                 +' -i -grib -o '+prepped_file]
            )
        else:
            log_missing_file_model(log_missing_file, source_file, 'jma',
                                   init_dt, str(forecast_hour).zfill(3))
    copy_file(prepped_file, dest_file)

def prep_prod_ecmwf_file(source_file, dest_file, init_dt, forecast_hour, prep_method,
                         log_missing_file):
    """! Do prep work for ECMWF production files

         Args:
             source_file       - source file format (string)
             dest_file         - destination file (string)
             init_dt           - initialzation date (datetime)
             forecast_hour     - forecast hour (string)
             prep_method       - name of prep method to do
                                 (string)
             log_missing_file  - text file path to write that
                                 production file is missing (string)

         Returns:
    """
    # Environment variables and executables
    EXECevs = os.environ['EXECevs']
    ECMGFSLOOKALIKENEW = os.path.join(EXECevs, 'ecm_gfs_look_alike_new')
    PCPCONFORM = os.path.join(EXECevs, 'pcpconform')
    WGRIB = os.environ['WGRIB']
    # Working file names
    prepped_file = os.path.join(os.getcwd(),
                                'atmos.'+dest_file.rpartition('/')[2])
    working_file1 = prepped_file+'.tmp1'
    # Prep file
    if prep_method == 'full':
        if forecast_hour == 'anl':
            wgrib_fhr = ':anl'
        elif int(forecast_hour) == 0:
            wgrib_fhr = ':anl'
        else:
            wgrib_fhr = ':'+forecast_hour+'hr'
        if check_file_exists_size(source_file):
            run_shell_command(
                [WGRIB+' '+source_file+' | grep "'+wgrib_fhr+'" | '
                 +WGRIB+' '+source_file+' -i -grib -o '
                 +working_file1]
            )
        else:
            log_missing_file_model(log_missing_file, source_file, 'ecmwf',
                                   init_dt, str(forecast_hour).zfill(3))
        if check_file_exists_size(working_file1):
            run_shell_command(['chmod', '640', working_file1])
            run_shell_command(['chgrp', 'rstprod', working_file1])
            run_shell_command(
                [ECMGFSLOOKALIKENEW, working_file1, prepped_file]
            )
    elif 'precip' in prep_method:
        if check_file_exists_size(source_file):
            run_shell_command(
                [PCPCONFORM, 'ecmwf', source_file, prepped_file]
            )
        else:
            if int(datetime.datetime.now().strftime('%H')) > 18:
                log_missing_file_model(log_missing_file, source_file, 'ecmwf',
                                       init_dt, str(forecast_hour).zfill(3))
    if os.path.exists(prepped_file):
        run_shell_command(['chmod', '640', prepped_file])
        run_shell_command(['chgrp', 'rstprod', prepped_file])
    copy_file(prepped_file, dest_file)

def prep_prod_ukmet_file(source_file_format, dest_file, init_dt,
                         forecast_hour, prep_method, log_missing_file):
    """! Do prep work for UKMET production files

         Args:
             source_file_format - source file format (string)
             dest_file          - destination file (string)
             init_dt            - initialization date (datetime)
             forecast_hour      - forecast hour (string)
             prep_method        - name of prep method to do
                                  (string)
             log_missing_file   - text file path to write that
                                  production file is missing (string)

         Returns:
    """
    # Environment variables and executables
    EXECevs = os.environ['EXECevs']
    WGRIB = os.environ['WGRIB']
    WGRIB2 = os.environ['WGRIB2']
    UKMHIRESMERGE = os.path.join(EXECevs, 'ukm_hires_merge')
    # Working file names
    prepped_file = os.path.join(os.getcwd(),
                                'atmos.'+dest_file.rpartition('/')[2])
    working_file1 = prepped_file+'.tmp1'
    working_file2 = prepped_file+'.tmp2'
    # Prep file
    if prep_method == 'full':
        ukmet_fhr_id_dict = {
            'anl': 'AAT',
            '0': 'AAT',
            '6': 'BBT',
            '12': 'CCT',
            '18': 'DDT',
            '24': 'EET',
            '30': 'FFT',
            '36': 'GGT',
            '42': 'HHT',
            '48': 'IIT',
            '54': 'JJT',
            '60': 'JJT',
            '66': 'KKT',
            '72': 'KKT',
            '78': 'QQT',
            '84': 'LLT',
            '90': 'TTT',
            '96': 'MMT',
            '102': 'UUT',
            '108': 'NNT',
            '114': 'VVT',
            '120': 'OOT',
            '126': '11T',
            '132': 'PPA',
            '138': '22T',
            '144': 'PPA'
        }
        if forecast_hour in list(ukmet_fhr_id_dict.keys()):
            if forecast_hour == 'anl':
                fhr_id = ukmet_fhr_id_dict['anl']
                fhr_str = '0'
                wgrib_fhr = 'anl'
            else:
                fhr_id = ukmet_fhr_id_dict[forecast_hour]
                fhr_str = forecast_hour
                if forecast_hour == '0':
                    wgrib_fhr = 'anl'
                else:
                    wgrib_fhr = forecast_hour+'hr'
            source_file = source_file_format.replace('{letter?fmt=str}',
                                                     fhr_id)
            if check_file_exists_size(source_file):
                run_shell_command(
                    [WGRIB+' '+source_file+' | grep "'+wgrib_fhr
                     +'" | '+WGRIB+' '+source_file+' -i -grib -o '
                     +working_file1]
                )
            else:
                log_missing_file_model(log_missing_file, source_file, 'ukmet',
                                       init_dt, str(forecast_hour).zfill(3))
            if check_file_exists_size(working_file1):
                run_shell_command([UKMHIRESMERGE, working_file1,
                                   prepped_file, fhr_str])
    elif 'precip' in prep_method:
        source_file = source_file_format
        source_file_accum = 12
        if check_file_exists_size(source_file):
            run_shell_command(
                [WGRIB2+' '+source_file+' -if ":TWATP:" -set_var "APCP" '
                 +'-fi -grib '+working_file1]
            )
        else:
            log_missing_file_model(log_missing_file, source_file, 'ukmet',
                                   init_dt, str(forecast_hour).zfill(3))
        if check_file_exists_size(working_file1):
            convert_grib2_grib1(working_file1, working_file2)
        if check_file_exists_size(working_file2):
            source_file_accum_fhr_start = (
                int(forecast_hour) - source_file_accum
            )
            run_shell_command(
                [WGRIB+' '+working_file2+' | grep "'
                 +str(source_file_accum_fhr_start)+'-'
                 +forecast_hour+'hr" | '+WGRIB+' '+working_file2
                 +' -i -grib -o '+prepped_file]
            )
    copy_file(prepped_file, dest_file)

def prep_prod_dwd_file(source_file, dest_file, init_dt, forecast_hour,
                       prep_method, log_missing_file):
    """! Do prep work for DWD production files

         Args:
             source_file_format - source file format (string)
             dest_file          - destination file (string)
             init_dt            - initialization date (datetime)
             forecast_hour      - forecast hour (string)
             prep_method        - name of prep method to do
                                  (string)
             log_missing_file   - text file path to write that
                                  production file is missing (string)

         Returns:
    """
    # Environment variables and executables
    EXECevs = os.environ['EXECevs']
    PCPCONFORM = os.path.join(EXECevs, 'pcpconform')
    # Working file names
    prepped_file = os.path.join(os.getcwd(),
                                'atmos.'+dest_file.rpartition('/')[2])
    #working_file1 = prepped_file+'.tmp1'
    #### For DWD to run through pcpconform, file name must be
    ####    dwd_YYYYMMDDHH_(hhh)_(hhh).tmp
    working_file1 = os.path.join(os.getcwd(),
                                 source_file.rpartition('/')[2]+'.tmp')
    # Prep file
    if 'precip' in prep_method:
        if check_file_exists_size(source_file):
            convert_grib2_grib1(source_file, working_file1)
        else:
            log_missing_file_model(log_missing_file, source_file, 'dwd',
                                   init_dt, str(forecast_hour).zfill(3))
        if check_file_exists_size(working_file1):
            run_shell_command(
               [PCPCONFORM, 'dwd', working_file1,
                prepped_file]
            )
    copy_file(prepped_file, dest_file)

def prep_prod_metfra_file(source_file, dest_file, init_dt, forecast_hour,
                          prep_method, log_missing_file):
    """! Do prep work for METRFRA production files

         Args:
             source_file       - source file(string)
             dest_file         - destination file (string)
             init_dt           - initialization date (datetime)
             forecast_hour     - forecast hour (string)
             prep_method       - name of prep method to do
                                 (string)
             log_missing_file  - text file path to write that
                                 production file is missing (string)

         Returns:
    """
    # Environment variables and executables
    WGRIB = os.environ['WGRIB']
    # Temporary file names
    prepped_file = os.path.join(os.getcwd(),
                                'atmos.'+dest_file.rpartition('/')[2])
    working_file1 = os.path.join(os.getcwd(),
                                 'atmos.'+source_file.rpartition('/')[2])
    working_file2 = os.path.join(os.getcwd(),
                                 'atmos.'+source_file.rpartition('/')[2]\
                                 .replace('.gz', ''))
    # Prep file
    if 'precip' in prep_method:
        if not check_file_exists_size(working_file2):
            if check_file_exists_size(source_file):
                copy_file(source_file, working_file1)
                if check_file_exists_size(working_file1):
                    run_shell_command(['gunzip', working_file1])
            else:
                log_missing_file_model(log_missing_file, source_file, 'metfra',
                                       init_dt, str(forecast_hour).zfill(3))
        if check_file_exists_size(working_file2):
            file_accum = 24
            fhr_accum_start = int(forecast_hour)-file_accum
            run_shell_command(
                [WGRIB+' '+working_file2+' | grep "'
                 +str(fhr_accum_start)+'-'
                 +forecast_hour+'hr" | '+WGRIB+' '+working_file2
                 +' -i -grib -o '+prepped_file]
            )
            copy_file(prepped_file, dest_file)

def prep_prod_osi_saf_file(daily_source_file, daily_dest_file,
                           date_dt, log_missing_file):
    """! Do prep work for OSI-SAF production files

         Args:
             daily_source_file - daily source file (string)
             daily_dest_file   - daily destination file (string)
             date_dt           - date (datetime object)
             log_missing_file  - text file path to write that
                                 production file is missing (string)
         Returns:
    """
    # Environment variables and executables
    # Temporary file names
    prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                +daily_dest_file.rpartition('/')[2])
    if check_file_exists_size(daily_source_file):
        copy_file(daily_source_file, prepped_file)
        if check_file_exists_size(prepped_file):
            prepped_data = netcdf.Dataset(prepped_file, 'a')
            prepped_data.variables['time'][:] = (
               prepped_data.variables['time'][:] + 43200
            )
            prepped_data.close()
            copy_file(prepped_file, daily_dest_file)
    else:
        if '_nh_' in daily_source_file:
            hem = 'nh'
        elif '_sh_' in daily_source_file:
            hem = 'sh'
        log_missing_file_truth(log_missing_file, daily_source_file,
                               f"OSI-SAF {hem.upper()}", date_dt)

def prep_prod_ghrsst_ospo_file(source_file, dest_file, date_dt,
                               log_missing_file):
    """! Do prep work for GHRSST OSPO production files

         Args:
             source_file      - source file (string)
             dest_file        - destination file (string)
             date_dt          - date (datetime object)
             log_missing_file - text file path to write that
                                production file is missing (string)
         Returns:
    """
    # Environment variables and executables
    # Temporary file names
    prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                +source_file.rpartition('/')[2])
    # Prep file
    if check_file_exists_size(source_file):
        copy_file(source_file, prepped_file)
    else:
        log_missing_file_truth(log_missing_file, source_file,
                               'GHRSST OSPO', date_dt)
    if check_file_exists_size(prepped_file):
        prepped_data = netcdf.Dataset(prepped_file, 'a',
                                      format='NETCDF3_CLASSIC')
        ghrsst_ospo_date_since_dt = datetime.datetime.strptime(
            '1981-01-01 00:00:00','%Y-%m-%d %H:%M:%S'
        )
        prepped_data['time'][:] = prepped_data['time'][:][0] + 43200
        prepped_data.close()
    copy_file(prepped_file, dest_file)

def prep_prod_get_d_file(source_file, dest_file, date_dt,
                         log_missing_files):
    """! Do prep work for ALEXI GET-D production files

         Args:
             source_file       - source file (string)
             dest_file         - destination file (string)
             date_dt           - date (datetime object)
             log_missing_files - text file path to write that
                                 production file is missing (string)
         Returns:
    """
    # Environment variables and executables
    # Temporary file names
    prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                +source_file.rpartition('/')[2])
    # Prep file
    if check_file_exists_size(source_file):
        copy_file(prepped_file, dest_file)
    else:
        log_missing_file_truth(log_missing_file, source_file,
                               'GET-D', date_dt)

def get_model_file(valid_time_dt, init_time_dt, forecast_hour,
                   source_file_format, dest_file_format):
    """! This get a model file and saves it in the specificed
         destination

         Args:
             valid_time_dt      - valid time (datetime)
             init_time_dt       - initialization time (datetime)
             forecast_hour      - forecast hour (string)
             source_file_format - source file format (string)
             dest_file_format   - destination file format (string)

         Returns:
    """
    dest_file = format_filler(dest_file_format, valid_time_dt,
                              init_time_dt, forecast_hour, {})
    log_missing_dir = dest_file.rpartition('/')[0].rpartition('/')[0]
    model = dest_file.rpartition('/')[0].rpartition('/')[2]
    log_missing_file = os.path.join(log_missing_dir, 'mail_missing_'
                                    +dest_file.rpartition('/')[2]\
                                     .replace('.', '_')+'.sh')
    if not os.path.exists(dest_file):
        source_file = format_filler(source_file_format, valid_time_dt,
                                    init_time_dt, forecast_hour, {})
        if 'dcom/navgem' in source_file:
            prep_prod_fnmoc_file(source_file, dest_file, init_time_dt,
                                 forecast_hour, 'full', log_missing_file)
        elif 'wgrbbul/jma_' in source_file:
            prep_prod_jma_file(source_file, dest_file, init_time_dt,
                               forecast_hour, 'full', log_missing_file)
        elif 'wgrbbul/ecmwf' in source_file:
            prep_prod_ecmwf_file(source_file, dest_file, init_time_dt,
                                 forecast_hour, 'full', log_missing_file)
        elif 'wgrbbul/ukmet_hires' in source_file:
            prep_prod_ukmet_file(source_file, dest_file, init_time_dt,
                                 forecast_hour, 'full', log_missing_file)
        elif 'qpf_verif/jma' in source_file:
            prep_prod_jma_file(source_file, dest_file, init_time_dt,
                               forecast_hour, 'precip', log_missing_file)
        elif 'qpf_verif/UWD' in source_file:
            prep_prod_ecmwf_file(source_file, dest_file, init_time_dt,
                                 forecast_hour, 'precip', log_missing_file)
        elif 'qpf_verif/ukmo' in source_file:
            prep_prod_ukmet_file(source_file, dest_file, init_time_dt,
                                 forecast_hour, 'precip', log_missing_file)
        elif 'qpf_verif/dwd' in source_file:
            prep_prod_dwd_file(source_file, dest_file, init_time_dt,
                               forecast_hour, 'precip', log_missing_file)
        elif 'qpf_verif/METFRA' in source_file:
            prep_prod_metfra_file(source_file, dest_file, init_time_dt,
                                  forecast_hour, 'precip', log_missing_file)
        elif '.precip.' in dest_file and 'com/gfs' in source_file \
                and int(forecast_hour) in [3,6]:
            ### Need to prepare special files for GFS precip for
            ### for f003 and f006 as APCP variables in the files
            ### are the same and throw WARNING from MET
            if check_file_exists_size(source_file):
                wgrib2_apcp_grep = subprocess.run(
                    'wgrib2 '+source_file+' | grep "APCP"',
                    shell=True, capture_output=True, encoding="utf8"
                )
                if wgrib2_apcp_grep.returncode == 0:
                    first_apcp_rec = wgrib2_apcp_grep.stdout.split(':')[0]
                    wgrib2_apcp_match = subprocess.run(
                        "wgrib2 "+source_file
                        +" -match '^("+first_apcp_rec+"):' "
                        +"-grib "+dest_file, shell=True
                    )
                else:
                    print("Could not get APCP record number(s) "
                          +"linking files insted")
                    print(f"Linking {source_file} to {dest_file}")
                    os.symlink(source_file, dest_file)
            else:
                log_missing_file_model(log_missing_file, source_file,
                                       model, init_time_dt,
                                       forecast_hour.zfill(3))
        else:
            link_file = True
            write_missing_file = True
            if model == 'jma' and forecast_hour.isnumeric():
                if f"{init_time_dt:%H}" == '00' \
                        and int(forecast_hour) > 72:
                    write_missing_file = False
                    link_file = False
                elif int(forecast_hour) % 24 != 0:
                    write_missing_file = False
                    link_file = False
            if link_file:
                if check_file_exists_size(source_file):
                    print("Linking "+source_file+" to "+dest_file)
                    os.symlink(source_file, dest_file)
                else:
                    if write_missing_file:
                        log_missing_file_model(log_missing_file, source_file,
                                               model, init_time_dt,
                                               forecast_hour.zfill(3))

def get_truth_file(valid_time_dt, obs, source_prod_file_format,
                   source_arch_file_format, evs_run_mode,
                   dest_file_format):
    """! This get a truth/observation file and saves it in the specificed
         destination

         Args:
             valid_time_dt           - valid time (datetime)
             obs                     - observation name (string)
             source_prod_file_format - source productoin file format (string)
             source_arch_file_format - source archive file format (string)
             evs_run_mode            - mode EVS is running in (string)
             dest_file_format        - destination file format (string)
         Returns:
    """
    dest_file = format_filler(dest_file_format, valid_time_dt,
                              valid_time_dt, ['anl'], {})
    log_missing_dir = dest_file.rpartition('/')[0].rpartition('/')[0]
    source_loc_list = ['prod']
    if evs_run_mode != 'production':
        source_loc_list.append('arch')
    for source_loc in source_loc_list:
        if source_loc == 'prod':
            source_file_format = source_prod_file_format
        elif source_loc == 'arch':
            source_file_format = source_arch_file_format
        log_missing_file = os.path.join(log_missing_dir, 'mail_missing_'
                                        +source_loc+'_'
                                        +dest_file.rpartition('/')[2]\
                                        .replace('.', '_')+'.sh')
        source_file = format_filler(source_file_format, valid_time_dt,
                                    valid_time_dt, ['anl'], {})
        if not os.path.exists(dest_file):
            if check_file_exists_size(source_file):
                print("Linking "+source_file+" to "+dest_file)
                os.symlink(source_file, dest_file)
            else:
                log_missing_file_truth(log_missing_file, source_file,
                                       obs, valid_time_dt)

def check_model_files(job_dict):
    """! Check what model files or don't exist

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             model_files_exist - if non-zero number of  model files
                                 exist or not (boolean)
             fhr_list          - list of forecast hours that model
                                 files exist for (string)
             model_copy_output_DATA2COMOUT_list - list of file to copy from
                                                  DATA to COMOUT
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hr_start'],
        '%Y%m%d%H'
    )
    verif_case_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE']+'_'+job_dict['STEP']
    )
    model = job_dict['MODEL']
    fhr_list = []
    fhr_check_input_dict = {}
    fhr_check_output_dict = {}
    job_dict_fhr_list = job_dict['fhr_list'].replace("'",'').split(', ')
    for fhr in [int(i) for i in job_dict_fhr_list]:
        fhr_check_input_dict[str(fhr)] = {}
        fhr_check_output_dict[str(fhr)] = {}
        init_date_dt = valid_date_dt - datetime.timedelta(hours=fhr)
        if job_dict['JOB_GROUP'] == 'reformat_data':
            input_file_format = os.path.join(verif_case_dir, 'data', model,
                                             model+'.{init?fmt=%Y%m%d%H}.'
                                             +'f{lead?fmt=%3H}')
            if job_dict['VERIF_CASE'] == 'grid2grid':
                output_DATA_file_format = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+'{valid?fmt=%Y%m%d}',
                    job_dict['MODEL'], job_dict['VERIF_CASE'],
                    'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                    +job_dict['job_name']+'_{lead?fmt=%2H}'
                    '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
                )
                output_COMOUT_file_format = os.path.join(
                    job_dict['COMOUT'],
                    job_dict['RUN']+'.'+'{valid?fmt=%Y%m%d}',
                    job_dict['MODEL'], job_dict['VERIF_CASE'],
                    'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                    +job_dict['job_name']+'_{lead?fmt=%2H}'
                    '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
                )
                if job_dict['VERIF_TYPE'] == 'pres_levs' \
                        and job_dict['job_name'] == 'GeoHeightAnom':
                    if init_date_dt.strftime('%H') in ['00', '12'] \
                            and fhr % 24 == 0:
                        fhr_check_input_dict[str(fhr)]['file1'] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr)
                        }
                        fhr_check_input_dict[str(fhr)]['file2'] = {
                            'valid_date': valid_date_dt,
                            'init_date': (valid_date_dt
                                          -datetime.timedelta(hours=fhr-12)),
                            'forecast_hour': str(fhr-12)
                        }
                        fhr_check_output_dict[str(fhr)]['file1'] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr)
                        }
                        fhr_check_output_dict[str(fhr)]['file2'] = {
                            'valid_date': valid_date_dt,
                            'init_date': (valid_date_dt
                                          -datetime.timedelta(hours=fhr-12)),
                            'forecast_hour': str(fhr-12)
                        }
                elif job_dict['VERIF_TYPE'] in ['sea_ice', 'sst']:
                    fhr_avg_end = fhr
                    fhr_avg_start = fhr-24
                    fhr_in_avg = fhr_avg_start
                    nf = 0
                    while fhr_in_avg <= fhr_avg_end:
                        fhr_check_input_dict[str(fhr)]['file'+str(nf+1)] = {
                            'valid_date': valid_date_dt,
                            'init_date': valid_date_dt-datetime.timedelta(
                                             hours=fhr_in_avg
                            ),
                            'forecast_hour': str(fhr_in_avg)
                        }
                        fhr_check_output_dict[str(fhr)]['file'+str(nf+1)] = {
                            'valid_date': valid_date_dt,
                            'init_date': valid_date_dt-datetime.timedelta(
                                             hours=fhr_in_avg
                            ),
                            'forecast_hour': str(fhr_in_avg)
                        }
                        nf+=1
                        fhr_in_avg+=12
                else:
                    fhr_check_input_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
                    fhr_check_output_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
            if job_dict['VERIF_CASE'] == 'grid2obs':
                if job_dict['VERIF_TYPE'] == 'ptype':
                    fhr_check_input_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'regrid_data_plane_'
                        +job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_init'
                        +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'regrid_data_plane_'
                        +job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_init'
                        +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                    fhr_check_output_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
        elif job_dict['JOB_GROUP'] == 'assemble_data':
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] in ['precip_accum24hr',
                                              'precip_accum3hr']:
                    input_file_format = os.path.join(verif_case_dir, 'data',
                                                     model, model+'.precip.'
                                                     +'{init?fmt=%Y%m%d%H}.'
                                                     +'f{lead?fmt=%3H}')
                    precip_accum = (job_dict['VERIF_TYPE']\
                                    .replace('precip_accum',''))
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'pcp_combine_'
                        +job_dict['VERIF_TYPE']+'_'+precip_accum+'Accum_init'
                        +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'pcp_combine_'
                        +job_dict['VERIF_TYPE']+'_'+precip_accum+'Accum_init'
                        +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'pres_levs' \
                        and job_dict['job_name'] == 'DailyAvg_GeoHeightAnom':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +'{valid?fmt=%Y%m%d}',
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'anomaly_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('DailyAvg_', '')
                                                     +'_init'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'fhr{lead?fmt=%3H}.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'daily_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-12}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'daily_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-12}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] in ['sea_ice', 'sst']:
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +'{valid?fmt=%Y%m%d}',
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'grid_stat_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('DailyAvg_', '')
                                                     +'_{lead?fmt=%2H}0000L_'
                                                     +'{valid?fmt=%Y%m%d}_'
                                                     +'{valid?fmt=%H}0000V_'
                                                     +'pairs.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'daily_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-24}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'daily_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-24}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                else:
                    input_file_format = os.path.join(verif_case_dir, 'data',
                                                     model, model
                                                     +'.{init?fmt=%Y%m%d%H}.'
                                                     +'f{lead?fmt=%3H}')
                    if job_dict['VERIF_TYPE'] == 'snow':
                        output_DATA_file_format = os.path.join(
                            verif_case_dir, 'METplus_output',
                            job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                            model, job_dict['VERIF_CASE'], 'pcp_combine_'
                            +job_dict['VERIF_TYPE']+'_'
                            +job_dict['job_name']+'_init'
                            +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                        )
                        output_COMOUT_file_format = os.path.join(
                            job_dict['COMOUT'],
                            job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                            model, job_dict['VERIF_CASE'], 'pcp_combine_'
                            +job_dict['VERIF_TYPE']+'_'
                            +job_dict['job_name']+'_init'
                            +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                        )
                if job_dict['VERIF_TYPE'] in ['precip_accum24hr',
                                              'precip_accum3hr']:
                    precip_accum = int(
                        job_dict['VERIF_TYPE'].replace('precip_accum','')\
                        .replace('hr','')
                    )
                    fhr_in_accum_list = [str(fhr)]
                    if job_dict['MODEL_accum'][0] == '{': #continuous
                        if fhr-precip_accum > 0:
                            fhr_in_accum_list.append(str(fhr-precip_accum))
                    elif int(job_dict['MODEL_accum']) < precip_accum:
                        nfiles_in_accum = int(
                            precip_accum/int(job_dict['MODEL_accum'])
                        )
                        nf = 1
                        while nf <= nfiles_in_accum:
                            fhr_nf = fhr - ((nf-1)*int(job_dict['MODEL_accum']))
                            if fhr_nf > 0:
                                fhr_in_accum_list.append(str(fhr_nf))
                            nf+=1
                    for fhr_in_accum in fhr_in_accum_list:
                        file_num = fhr_in_accum_list.index(fhr_in_accum)+1
                        fhr_check_input_dict[str(fhr)]['file'+str(file_num)] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr_in_accum)
                        }
                elif job_dict['VERIF_TYPE'] == 'snow':
                    fhr_check_input_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
                    fhr_check_input_dict[str(fhr)]['file2'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr-24)
                    }
                elif job_dict['VERIF_TYPE'] == 'pres_levs' \
                        and job_dict['job_name'] == 'DailyAvg_GeoHeightAnom':
                    if init_date_dt.strftime('%H') in ['00', '12'] \
                            and fhr % 24 == 0:
                        fhr_check_input_dict[str(fhr)]['file1'] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr)
                        }
                else:
                    fhr_check_input_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
                fhr_check_output_dict[str(fhr)]['file1'] = {
                    'valid_date': valid_date_dt,
                    'init_date': init_date_dt,
                    'forecast_hour': str(fhr)
                }
            elif job_dict['VERIF_CASE'] == 'grid2obs':
                input_file_format = os.path.join(verif_case_dir, 'data',
                                                 model, model
                                                 +'.{init?fmt=%Y%m%d%H}.'
                                                 +'f{lead?fmt=%3H}')
                if job_dict['VERIF_TYPE'] == 'sfc' \
                        and job_dict['job_name'] == 'TempAnom2m':
                    fhr_check_input_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
                    fhr_check_input_dict[str(fhr)]['file2'] = {
                        'valid_date': valid_date_dt,
                        'init_date': (valid_date_dt
                                      -datetime.timedelta(hours=fhr-12)),
                        'forecast_hour': str(fhr-12)
                    }
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'],
                        'point_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'],
                        'point_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
                    )
                    fhr_check_output_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
                    fhr_check_output_dict[str(fhr)]['file2'] = {
                        'valid_date': valid_date_dt,
                        'init_date': (valid_date_dt
                                      -datetime.timedelta(hours=fhr-12)),
                        'forecast_hour': str(fhr-12)
                    }
                elif job_dict['VERIF_TYPE'] == 'ptype':
                    fhr_check_input_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'merged_ptype_'
                        +job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_init'
                        +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'merged_ptype_'
                        +job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_init'
                        +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                    fhr_check_output_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
        elif job_dict['JOB_GROUP'] == 'generate_stats':
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] == 'sea_ice' \
                        and 'DailyAvg_Extent' in job_dict['job_name']:
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'],
                        'stat_analysis_fcst'+model+'_obsosi_saf_'
                        +job_dict['job_name']+'_SL1L2_'
                        '{valid?fmt=%Y%m%d%H}.stat'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'],
                        'stat_analysis_fcst'+model+'_obsosi_saf_'
                        +job_dict['job_name']+'_SL1L2_'
                        '{valid?fmt=%Y%m%d%H}.stat'
                    )
                else:
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'],
                        'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'],
                        'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
                    )
                fhr_check_output_dict[str(fhr)]['file1'] = {
                    'valid_date': valid_date_dt,
                    'init_date': init_date_dt,
                    'forecast_hour': str(fhr)
                }
                if job_dict['VERIF_TYPE'] == 'pres_levs' \
                        and job_dict['job_name'] == 'DailyAvg_GeoHeightAnom':
                    input_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'daily_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-12}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'pres_levs' \
                        and job_dict['job_name'] == 'WindShear':
                    input_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'wind_shear_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] in ['precip_accum24hr',
                                                'precip_accum3hr']:
                    precip_accum = (job_dict['VERIF_TYPE']\
                                    .replace('precip_accum',''))
                    input_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'pcp_combine_'
                        +job_dict['VERIF_TYPE']+'_'+precip_accum+'Accum_init'
                        +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'sea_ice':
                    input_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'daily_avg_'
                        +job_dict['VERIF_TYPE']+'_DailyAvg_Concentration'
                        +job_dict['hemisphere'].upper()+'_'
                        +'init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-24}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'snow':
                    input_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'pcp_combine_'
                        +job_dict['VERIF_TYPE']+'_24hrAccum_'
                        +job_dict['file_name_var']+'_init'
                        +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                elif  job_dict['VERIF_TYPE'] == 'sst':
                    input_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'daily_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-24}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                else:
                    input_file_format = os.path.join(
                        verif_case_dir, 'data', model,
                        model+'.{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}'
                    )
            elif job_dict['VERIF_CASE'] == 'grid2obs':
                if job_dict['VERIF_TYPE'] == 'ptype' \
                        and job_dict['job_name'] == 'Ptype':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +'{valid?fmt=%Y%m%d}',
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'merged_ptype_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']+'_'
                                                     +'init{init?fmt=%Y%m%d%H}_'
                                                     +'fhr{lead?fmt=%3H}.nc')
                elif job_dict['VERIF_TYPE'] == 'sfc' \
                        and job_dict['job_name'] == 'DailyAvg_TempAnom2m':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +'{valid?fmt=%Y%m%d}',
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'anomaly_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('DailyAvg_', '')
                                                     +'_init'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'fhr{lead?fmt=%3H}.stat')
                else:
                    input_file_format = os.path.join(
                        verif_case_dir, 'data', model,
                        model+'.{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}'
                    )
                if job_dict['VERIF_TYPE'] == 'sfc' \
                        and job_dict['job_name'] == 'DailyAvg_TempAnom2m':
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'],
                        'stat_analysis_fcst'+job_dict['MODEL']+'_obsprepbufr_'
                        +job_dict['prepbufr']+'_'+job_dict['job_name']
                        +'_SL1L2_{valid?fmt=%Y%m%d%H}.stat'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'],
                        'stat_analysis_fcst'+job_dict['MODEL']+'_obsprepbufr_'
                        +job_dict['prepbufr']+'_'+job_dict['job_name']
                        +'_SL1L2_{valid?fmt=%Y%m%d%H}.stat'
                    )
                else:
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'],
                        'point_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'],
                        'point_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
                    )
            fhr_check_input_dict[str(fhr)]['file1'] = {
                'valid_date': valid_date_dt,
                'init_date': init_date_dt,
                'forecast_hour': str(fhr)
            }
            fhr_check_output_dict[str(fhr)]['file1'] = {
                'valid_date': valid_date_dt,
                'init_date': init_date_dt,
                'forecast_hour': str(fhr)
            }
    # Check input files
    for fhr_key in list(fhr_check_input_dict.keys()):
        fhr_key_input_files_exist_list = []
        for fhr_fileN_key in list(fhr_check_input_dict[fhr_key].keys()):
            fhr_fileN = format_filler(
                input_file_format,
                fhr_check_input_dict[fhr_key][fhr_fileN_key]['valid_date'],
                fhr_check_input_dict[fhr_key][fhr_fileN_key]['init_date'],
                fhr_check_input_dict[fhr_key][fhr_fileN_key]['forecast_hour'],
                {}
            )
            if os.path.exists(fhr_fileN):
                fhr_key_input_files_exist_list.append(True)
                if job_dict['JOB_GROUP'] == 'reformat_data' \
                        and job_dict['job_name'] in ['GeoHeightAnom',
                                                     'ConcentrationNH',
                                                     'ConcentrationSH',
                                                     'SST']:
                    fhr_list.append(
                        fhr_check_input_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
                elif job_dict['JOB_GROUP'] == 'assemble_data' \
                        and job_dict['job_name'] in ['TempAnom2m']:
                    fhr_list.append(
                        fhr_check_input_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
            else:
                fhr_key_input_files_exist_list.append(False)
        if all(x == True for x in fhr_key_input_files_exist_list) \
                and len(fhr_key_input_files_exist_list) > 0:
            fhr_list.append(fhr_key)
    fhr_list = list(
        np.asarray(np.unique(np.asarray(fhr_list, dtype=int)),dtype=str)
    )
    input_fhr_list = copy.deepcopy(fhr_list)
    # Check output files
    model_copy_output_DATA2COMOUT_list = []
    for fhr_key in list(fhr_check_output_dict.keys()):
        for fhr_fileN_key in list(fhr_check_output_dict[fhr_key].keys()):
            fhr_fileN_DATA = format_filler(
                output_DATA_file_format,
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['valid_date'],
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['init_date'],
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['forecast_hour'],
                {}
            )
            fhr_fileN_COMOUT = format_filler(
                output_COMOUT_file_format,
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['valid_date'],
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['init_date'],
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['forecast_hour'],
                {}
            )
            if os.path.exists(fhr_fileN_COMOUT):
                copy_file(fhr_fileN_COMOUT,fhr_fileN_DATA)
                if fhr_check_output_dict[fhr_key]\
                        [fhr_fileN_key]['forecast_hour'] \
                        in fhr_list:
                    fhr_list.remove(
                        fhr_check_output_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
            else:
                if fhr_check_output_dict[fhr_key]\
                        [fhr_fileN_key]['forecast_hour'] \
                        in fhr_list:
                    if (fhr_fileN_DATA, fhr_fileN_COMOUT) \
                            not in model_copy_output_DATA2COMOUT_list:
                        model_copy_output_DATA2COMOUT_list.append(
                            (fhr_fileN_DATA, fhr_fileN_COMOUT)
                        )
    if len(fhr_list) != 0:
        model_files_exist = True
    else:
        model_files_exist = False
    if job_dict['JOB_GROUP'] == 'reformat_data' \
            and job_dict['VERIF_CASE'] == 'grid2grid':
        if (job_dict['job_name'] == 'GeoHeightAnom' \
                and int(job_dict['valid_hr_start']) % 12 == 0)\
               or job_dict['job_name'] == 'WindShear':
            fhr_list = input_fhr_list
    if job_dict['JOB_GROUP'] == 'assemble_data' \
            and job_dict['VERIF_CASE'] == 'grid2obs':
        if job_dict['job_name'] == 'TempAnom2m':
            fhr_list = input_fhr_list
    return model_files_exist, fhr_list, model_copy_output_DATA2COMOUT_list

def check_truth_files(job_dict):
    """!
         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             all_truth_file_exist - if all needed truth files
                                    exist or not (boolean)
             truth_copy_output_DATA2COMOUT_list - list of files to copy
                                                  from DATA to COMOUT
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hr_start'],
        '%Y%m%d%H'
    )
    verif_case_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE']+'_'+job_dict['STEP']
    )
    truth_input_file_list = []
    truth_output_file_list = []
    if job_dict['JOB_GROUP'] == 'reformat_data':
        if job_dict['VERIF_CASE'] == 'grid2grid':
            if job_dict['VERIF_TYPE'] == 'pres_levs':
                model_truth_file = os.path.join(
                    verif_case_dir, 'data', job_dict['MODEL'],
                    job_dict['MODEL']+'.'+valid_date_dt.strftime('%Y%m%d%H')
                    +'.truth'
                )
                truth_input_file_list.append(model_truth_file)
            elif job_dict['VERIF_TYPE'] == 'sea_ice':
                osi_saf_file = os.path.join(
                    verif_case_dir, 'data', 'osi_saf',
                    'osi_saf.multi.'+job_dict['hemisphere']+'.'
                    +(valid_date_dt-datetime.timedelta(hours=24))\
                    .strftime('%Y%m%d%H')
                    +'to'+valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                truth_input_file_list.append(osi_saf_file)
                osi_saf_DATA_output = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'osi_saf', job_dict['VERIF_CASE'], 'regrid_data_plane_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']+'_valid'
                    +(valid_date_dt-datetime.timedelta(hours=24))\
                    .strftime('%Y%m%d%H')
                    +'to'+valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                osi_saf_COMOUT_output = os.path.join(
                    job_dict['COMOUT'],
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'osi_saf', job_dict['VERIF_CASE'], 'regrid_data_plane_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']+'_valid'
                    +(valid_date_dt-datetime.timedelta(hours=24))\
                    .strftime('%Y%m%d%H')
                    +'to'+valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                truth_output_file_list.append((osi_saf_DATA_output,
                                               osi_saf_COMOUT_output))
        elif job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] in ['pres_levs', 'sfc', 'ptype'] \
                    and 'Prepbufr' in job_dict['job_name']:
                prepbufr_name = (job_dict['job_name'].replace('Prepbufr', '')\
                                 .lower())
                prepbufr_file = os.path.join(
                    verif_case_dir, 'data', 'prepbufr_'+prepbufr_name,
                    'prepbufr.'+prepbufr_name+'.'
                    +valid_date_dt.strftime('%Y%m%d%H')
                )
                truth_input_file_list.append(prepbufr_file)
                pb2nc_DATA_output = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                pb2nc_COMOUT_output = os.path.join(
                    job_dict['COMOUT'],
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                truth_output_file_list.append((pb2nc_DATA_output,
                                               pb2nc_COMOUT_output))
    elif job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['VERIF_CASE'] == 'grid2grid':
            if job_dict['VERIF_TYPE'] == 'precip_accum24hr' \
                    and job_dict['job_name'] == '24hrCCPA':
                nccpa_files = 4
                n = 1
                while n <= 4:
                    nccpa_file = os.path.join(
                        verif_case_dir, 'data', 'ccpa', 'ccpa.6H.'
                        +(valid_date_dt-datetime.timedelta(hours=(n-1)*6))\
                        .strftime('%Y%m%d%H')
                    )
                    truth_input_file_list.append(nccpa_file)
                    n+=1
                ccpa_DATA_output = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'ccpa', job_dict['VERIF_CASE'],
                    'pcp_combine_precip_accum24hr_24hrCCPA_valid'
                    +valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                ccpa_COMOUT_output = os.path.join(
                    job_dict['COMOUT'],
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'ccpa', job_dict['VERIF_CASE'],
                    'pcp_combine_precip_accum24hr_24hrCCPA_valid'
                    +valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                truth_output_file_list.append((ccpa_DATA_output,
                                               ccpa_COMOUT_output))
        elif job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] in ['pres_levs', 'sfc', 'ptype']:
                pb2nc_file = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                truth_input_file_list.append(pb2nc_file)
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        if job_dict['VERIF_CASE'] == 'grid2grid':
            if job_dict['VERIF_TYPE'] == 'pres_levs':
                model_truth_file = os.path.join(
                    verif_case_dir, 'data', job_dict['MODEL'],
                    job_dict['MODEL']+'.'+valid_date_dt.strftime('%Y%m%d%H')
                    +'.truth'
                )
                truth_input_file_list.append(model_truth_file)
            elif job_dict['VERIF_TYPE'] == 'precip_accum24hr':
                ccpa_file = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'ccpa', job_dict['VERIF_CASE'], 'pcp_combine_'
                    +job_dict['VERIF_TYPE']+'_24hrCCPA_valid'
                    +valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                truth_input_file_list.append(ccpa_file)
            elif job_dict['VERIF_TYPE'] == 'precip_accum3hr':
                ccpa_file = os.path.join(
                    verif_case_dir, 'data', 'ccpa', 'ccpa.3H.'
                    +valid_date_dt.strftime('%Y%m%d%H')
                )
                truth_input_file_list.append(ccpa_file)
            elif job_dict['VERIF_TYPE'] == 'sea_ice':
                if 'DailyAvg_Concentration' in job_dict['job_name']:
                    osi_saf_file = os.path.join(
                        verif_case_dir, 'data', 'osi_saf',
                        'osi_saf.multi.'+job_dict['hemisphere']+'.'
                        +(valid_date_dt-datetime.timedelta(hours=24))\
                        .strftime('%Y%m%d%H')
                        +'to'+valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                    )
                elif 'DailyAvg_Extent' in job_dict['job_name']:
                    osi_saf_file = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                        'osi_saf', job_dict['VERIF_CASE'],
                        'regrid_data_plane_sea_ice_'
                        +'DailyAvg_Concentration'
                        +job_dict['hemisphere'].upper()+'_valid'
                        +(valid_date_dt-datetime.timedelta(hours=24))\
                        .strftime('%Y%m%d%H')
                        +'to'+valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                    )
                truth_input_file_list.append(osi_saf_file)
            elif job_dict['VERIF_TYPE'] == 'snow':
                nohrsc_file = os.path.join(
                    verif_case_dir, 'data', 'nohrsc',
                    'nohrsc.24H.'+valid_date_dt.strftime('%Y%m%d%H')
                )
                truth_input_file_list.append(nohrsc_file)
            elif job_dict['VERIF_TYPE'] == 'sst':
                ghrsst_ospo_file = os.path.join(
                    verif_case_dir, 'data', 'ghrsst_ospo',
                    'ghrsst_ospo.'
                    +(valid_date_dt-datetime.timedelta(hours=24))\
                    .strftime('%Y%m%d%H')
                    +'to'+valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                truth_input_file_list.append(ghrsst_ospo_file)
        elif job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] in ['pres_levs', 'sfc', 'ptype']:
                pb2nc_file = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                truth_input_file_list.append(pb2nc_file)
    truth_output_files_exist_list = []
    truth_copy_output_DATA2COMOUT_list = truth_output_file_list
    for truth_file_tuple in truth_output_file_list:
        if os.path.exists(truth_file_tuple[1]):
            truth_output_files_exist_list.append(True)
            copy_file(truth_file_tuple[1], truth_file_tuple[0])
            if job_dict['JOB_GROUP'] == 'reformat_data' \
                    and job_dict['VERIF_CASE'] == 'grid2obs' \
                    and job_dict['VERIF_TYPE'] in ['pres_levs', 'sfc', 'ptype'] \
                    and 'Prepbufr' in job_dict['job_name']:
                if os.path.exists(truth_file_tuple[0]):
                    run_shell_command(['chmod', '640',
                                       truth_file_tuple[0]])
                    run_shell_command(['chgrp', 'rstprod',
                                       truth_file_tuple[0]])
            truth_copy_output_DATA2COMOUT_list.remove(truth_file_tuple)
        else:
            truth_output_files_exist_list.append(False)
    if all(x == True for x in truth_output_files_exist_list) \
            and len(truth_output_files_exist_list) > 0:
        all_truth_file_exist = False
    else:
        truth_input_files_exist_list = []
        for truth_file in truth_input_file_list:
            if os.path.exists(truth_file):
                truth_input_files_exist_list.append(True)
            else:
                truth_input_files_exist_list.append(False)
        if all(x == True for x in truth_input_files_exist_list) \
                and len(truth_input_files_exist_list) > 0:
            all_truth_file_exist = True
        else:
            all_truth_file_exist = False
    return all_truth_file_exist, truth_copy_output_DATA2COMOUT_list

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

def get_obs_valid_hrs(obs):
    """! This returns the valid hour start, end, and increment
         information for a given observation

         Args:
             obs - observation name (string)

         Returns:
             valid_hr_start - starting valid hour (integer)
             valid_hr_end   - ending valid hour (integer)
             valid_hr_inc   - valid hour increment (integer)
    """
    obs_valid_hr_dict = {
        '24hrCCPA': {'valid_hr_start': 12,
                     'valid_hr_end': 12,
                     'valid_hr_inc': 24},
        '3hrCCPA': {'valid_hr_start': 0,
                     'valid_hr_end': 21,
                     'valid_hr_inc': 3},
        '24hrNOHRSC': {'valid_hr_start': 12,
                       'valid_hr_end': 12,
                       'valid_hr_inc': 24},
        'OSI-SAF': {'valid_hr_start': 00,
                    'valid_hr_end': 00,
                    'valid_hr_inc': 24},
        'GHRSST-OSPO': {'valid_hr_start': 00,
                        'valid_hr_end': 00,
                        'valid_hr_inc': 24},
        'GET_D': {'valid_hr_start': 00,
                  'valid_hr_end': 00,
                  'valid_hr_inc': 24},
    }
    if obs in list(obs_valid_hr_dict.keys()):
        valid_hr_start = obs_valid_hr_dict[obs]['valid_hr_start']
        valid_hr_end = obs_valid_hr_dict[obs]['valid_hr_end']
        valid_hr_inc = obs_valid_hr_dict[obs]['valid_hr_inc']
    else:
        print(f"FATAL ERROR: Cannot get {obs} valid hour information")
        sys.exit(1)
    return valid_hr_start, valid_hr_end, valid_hr_inc

def get_off_machine_data(job_file, job_name, job_output, machine, user, queue,
                         account):
    """! This submits a job to the transfer queue
         to get data that does not reside on current machine
         Args:
             job_file   - path to job submission file (string)
             job_name   - job submission name (string)
             job_output - path to write job output (string)
             machine    - machine name (string)
             user       - user name (string)
             queue      - submission queue name (string)
             account    - submission account name (string)
         Returns:
    """
    # Set up job wall time information
    walltime = '60'
    walltime_seconds = (
        datetime.timedelta(minutes=int(walltime)).total_seconds()
    )
    walltime = (datetime.datetime.min
                + datetime.timedelta(minutes=int(walltime))).time()
    # Submit job
    print("Submitting "+job_file+" to "+queue)
    print("Output sent to "+job_output)
    os.chmod(job_file, 0o755)
    if machine == 'WCOSS2':
        os.system('qsub -V -l walltime='+walltime.strftime('%H:%M:%S')+' '
                  +'-q '+queue+' -A '+account+' -o '+job_output+' '
                  +'-e '+job_output+' -N '+job_name+' '
                  +'-l select=1:ncpus=1 '+job_file)
        job_check_cmd = ('qselect -s QR -u '+user+' '+'-N '
                         +job_name+' | wc -l')
    elif machine in ['HERA', 'ORION', 'S4', 'JET']:
        os.system('sbatch --ntasks=1 --time='
                  +walltime.strftime('%H:%M:%S')+' --partition='+queue+' '
                  +'--account='+account+' --output='+job_output+' '
                  +'--job-name='+job_name+' '+job_file)
        job_check_cmd = ('squeue -u '+user+' -n '+job_name+' '
                         +'-t R,PD -h | wc -l')
    sleep_counter, sleep_checker = 1, 10
    while (sleep_counter*sleep_checker) <= walltime_seconds:
        sleep(sleep_checker)
        print("Walltime checker: "+str(sleep_counter*sleep_checker)+" "
              +"out of "+str(int(walltime_seconds))+" seconds")
        check_job = subprocess.check_output(job_check_cmd, shell=True,
                                            encoding='UTF-8')
        if check_job[0] == '0':
            break
        sleep_counter+=1

def initalize_job_env_dict(verif_type, group,
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
        'NET', 'RUN', 'VERIF_CASE', 'STEP', 'COMPONENT', 'COMIN', 'SENDCOM', 'COMOUT',
        'evs_run_mode'
    ]
    if group in ['reformat_data', 'assemble_data', 'generate_stats', 'gather_stats']:
        os.environ['MET_TMP_DIR'] = os.path.join(
            os.environ['DATA'],
            os.environ['VERIF_CASE']+'_'+os.environ['STEP'],
            'METplus_output', 'tmp'
        )
        make_dir(os.environ['MET_TMP_DIR'])
        job_env_var_list.extend(
            ['METPLUS_PATH', 'MET_ROOT', 'MET_TMP_DIR', 'COMROOT']
        )
    elif group in ['condense_stats', 'filter_stats', 'make_plots',
                   'tar_images']:
        job_env_var_list.extend(['MET_ROOT', 'met_ver'])
        if group == 'tar_images':
            job_env_var_list.extend(['KEEPDATA'])
    job_env_dict = {}
    for env_var in job_env_var_list:
        job_env_dict[env_var] = os.environ[env_var]
    if group in ['condense_stats', 'filter_stats', 'make_plots',
                 'tar_images']:
        job_env_dict['plot_verbosity'] = 'DEBUG'
    job_env_dict['VERIF_TYPE'] = verif_type
    job_env_dict['JOB_GROUP'] = group
    job_env_dict['job_name'] = job
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
        if group in ['filter_stats', 'make_plots']:
            job_env_dict['fhr_list'] = ', '.join(fhr_list)
        else:
            job_env_dict['fhr_list'] = "'"+', '.join(fhr_list)+"'"
        if verif_type in ['pres_levs', 'means', 'sfc', 'ptype']:
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
             init_dates  - array of initalization dates (datetime)
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
        logger.error(f"{met_minor_version_col_file} DOES NOT EXISTS, "
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
             DATAjob_dir    - path to plotting job's
                              DATA directory
             COMOUTjob_dir  - path to plotting job's
                              COMOUT directory
    """
    region_savefig_dict = {
        'Alaska': 'alaska',
        'alaska': 'alaska',
        'Appalachia': 'buk_apl',
        'ANTARCTIC': 'antarctic',
        'ARCTIC': 'arctic',
        'ATL_MDR': 'al_mdr',
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
        'Mezqutial': 'buk_mez',
        'MidAtlantic': 'buk_matl',
        'N60N90': 'n60',
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
    dir_ndays = ('last'+plot_job_env_dict['NDAYS']+'days').lower()
    dir_line_type = plot_job_env_dict['line_type'].lower()
    dir_parameter = plot_job_env_dict['fcst_var_name'].lower()
    #if plot_job_env_dict['fcst_var_name'] == 'HGT_DECOMP':
    #    dir_parameter = (
    #        dir_parameter+'_'
    #        +(plot_job_env_dict['interp_method']\
    #          .replace('WV1_', '').replace('-', '_'))
    #    )
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
        DATAjob_dir = os.path.join(
            DATA_base_dir, f"{dir_verif_case}_{dir_step}", 'plot_output',
            f"{plot_job_env_dict['RUN']}.{plot_job_env_dict['end_date']}",
            f"{dir_verif_case}_{dir_verif_type}",
            dir_ndays, dir_line_type,
            f"{dir_parameter}_{dir_level}",
            dir_region
        )
    elif job_group == 'make_plots':
        dir_stat = plot_job_env_dict['stat'].lower()
        DATAjob_dir = os.path.join(
            DATA_base_dir, f"{dir_verif_case}_{dir_step}", 'plot_output',
            f"{plot_job_env_dict['RUN']}.{plot_job_env_dict['end_date']}",
            f"{dir_verif_case}_{dir_verif_type}",
            dir_ndays, dir_line_type,
            f"{dir_parameter}_{dir_level}",
            dir_region, dir_stat
        )
    COMOUTjob_dir = DATAjob_dir.replace(
        os.path.join(DATA_base_dir,
                     f"{dir_verif_case}_{dir_step}",
                     'plot_output', f"{plot_job_env_dict['RUN']}."
                     +f"{plot_job_env_dict['end_date']}"),
        COMOUT_base_dir
    )
    return DATAjob_dir, COMOUTjob_dir

def get_daily_stat_file(model_name, source_stats_base_dir,
                        dest_model_name_stats_dir,
                        verif_case, start_date_dt, end_date_dt):
    """! Link model daily stat files
         Args:
             model_name                - name of model (string)
             source_stats_base_dir     - full path to stats/global_det
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
    output_file = os.path.join(
        output_dir, f"condensed_stats_{model.lower()}_{line_type.lower()}_"
        +f"{fcst_var_name.lower()}_"
        +f"{fcst_var_level.lower().replace('.','p').replace('-', '_')}_"
        +f"{vx_mask.lower()}.stat"
    )
    if len(model_stat_files) == 0:
        logger.warning(f"NO STAT FILES IN MATCHING "
                       +f"{model_stat_files_wildcard}")
    else:
        if not os.path.exists(output_file):
            logger.info(f"Condensing down stat files matching "
                        +f"{model_stat_files_wildcard}")
            with open(model_stat_files[0]) as msf:
                met_header_cols = msf.readline()
            all_grep_output = ''
            grep_opts = (
                ' | grep "'+obs+' "'
                +' | grep "'+vx_mask+' "'
                +' | grep "'+fcst_var_name+' "'
                +' | grep "'+fcst_var_level+' "'
                +' | grep "'+obs_var_name+' "'
                +' | grep "'+line_type+' "'
            )
            for model_stat_file in model_stat_files:
                logger.debug(f"Getting data from {model_stat_file}")
                ps = subprocess.Popen(
                    'grep -R "'+model+' " '+model_stat_file+grep_opts,
                    shell=True, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, encoding='UTF-8'
                )
                logger.debug(f"Ran {ps.args}")
                all_grep_output = all_grep_output+ps.communicate()[0]
            logger.debug(f"Condensed {model} .stat file at "
                         +f"{output_file}")
            with open(output_file, 'w') as f:
                f.write(met_header_cols+all_grep_output)
        else:
            logger.info(f"{output_file} exists")

def build_df(logger, input_dir, output_dir, model_info_dict,
             met_info_dict, fcst_var_name, fcst_var_level, fcst_var_thresh,
             obs_var_name, obs_var_level, obs_var_thresh, line_type,
             grid, vx_mask, interp_method, interp_points, date_type, dates,
             met_format_valid_dates, fhr):
    """! Build the data frame for all model stats,
         Read the model parse file, if doesn't exist
         parse the model file for need information, and write file

         Args:
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
            parsed_model_stat_file_name = (
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
            input_parsed_model_stat_file = os.path.join(
                input_dir, parsed_model_stat_file_name
            )
            output_parsed_model_stat_file = os.path.join(
                output_dir, parsed_model_stat_file_name
            )
            if os.path.exists(input_parsed_model_stat_file):
                parsed_model_stat_file = input_parsed_model_stat_file
            else:
                parsed_model_stat_file = output_parsed_model_stat_file
            if not os.path.exists(parsed_model_stat_file):
                write_parse_stat_file = True
                read_parse_stat_file = True
            else:
                write_parse_stat_file = False
                read_parse_stat_file = True
        else:
            write_parse_stat_file = False
            read_parse_stat_file = False
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
        if write_parse_stat_file:
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
                logger.debug(f"Parsing file {condensed_model_file}")
                condensed_model_df = pd.read_csv(
                    condensed_model_file, sep=" ", skiprows=1,
                    skipinitialspace=True, names=met_version_line_type_col_list,
                    keep_default_na=False, dtype='str', header=None
                )
                parsed_model_df = condensed_model_df[
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
                parsed_model_df = parsed_model_df[
                    parsed_model_df['FCST_VALID_BEG'].isin(met_format_valid_dates)
                ]
                parsed_model_df['FCST_VALID_BEG'] = pd.to_datetime(
                    parsed_model_df['FCST_VALID_BEG'], format='%Y%m%d_%H%M%S'
                )
                parsed_model_df = parsed_model_df.sort_values(by='FCST_VALID_BEG')
                parsed_model_df['FCST_VALID_BEG'] = (
                    parsed_model_df['FCST_VALID_BEG'].dt.strftime('%Y%m%d_%H%M%S')
                )
                parsed_model_df.to_csv(
                    parsed_model_stat_file, header=met_version_line_type_col_list,
                    index=None, sep=' ', mode='w'
                )
            else:
                logger.debug(f"{condensed_model_file} does not exist")
            if os.path.exists(parsed_model_stat_file):
                logger.debug(f"Parsed {model_dict['name']} file "
                             +f"at {parsed_model_stat_file}")
            else:
                logger.debug(f"Could not create {parsed_model_stat_file}")
        model_num_df = pd.DataFrame(np.nan, index=model_num_df_index,
                                    columns=met_version_line_type_col_list)
        if read_parse_stat_file:
            if os.path.exists(parsed_model_stat_file):
                logger.debug(f"Reading {parsed_model_stat_file} for "
                             +f"{model_dict['name']}")
                model_stat_file_df = pd.read_csv(
                    parsed_model_stat_file, sep=" ", skiprows=1,
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
                        logger.debug("No data matching valid date "
                                     +f"{valid_date} in"
                                     +f"{parsed_model_stat_file}")
                        continue
                    elif len(model_stat_file_df_valid_date_idx_list) > 1:
                        logger.debug(f"Multiple lines matching valid date "
                                     +f"{valid_date} in "
                                     +f"{parsed_model_stat_file} "
                                     +f"using first one")
                    else:
                        logger.debug(f"One line matching valid date "
                                     +f"{valid_date} in "
                                     +f"{parsed_model_stat_file}")
                    model_num_df.loc[(model_num_name, valid_date)] = (
                        model_stat_file_df.loc\
                        [model_stat_file_df_valid_date_idx_list[0]]\
                        [:]
                    )
            else:
                logger.debug(f"{parsed_model_stat_file} does not exist")
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
   if stat == 'ACC': # Anomaly Correlation Coefficient
       if line_type == 'SAL1L2':
           stat_df = (FOABAR - FABAR*OABAR) \
                     /np.sqrt((FFABAR - FABAR*FABAR)*
                              (OOABAR - OABAR*OABAR))
       elif line_type in ['CNT', 'VCNT']:
           stat_df = ANOM_CORR
       elif line_type == 'VAL1L2':
           stat_df = UVFOABAR/np.sqrt(UVFFABAR*UVOOABAR)
   elif stat in ['BIAS', 'ME']: # Bias/Mean Error
       if line_type == 'SL1L2':
           stat_df = FBAR - OBAR
       elif line_type == 'CNT':
           stat_df = ME
       elif line_type == 'VL1L2':
           stat_df = np.sqrt(UVFFBAR) - np.sqrt(UVOOBAR)
   elif stat == 'CORR': # Pearson Correlation Coefficient
       if line_type == 'SL1L2':
           var_f = FFBAR - FBAR*FBAR
           var_o = OOBAR - OBAR*OBAR
           stat_df = (FOBAR - (FBAR*OBAR))/np.sqrt(var_f*var_o)
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
           stat_df = np.sqrt(FFBAR + OOBAR - 2*FOBAR)
       elif line_type == 'CNT':
           stat_df = RMSE
       elif line_type == 'VL1L2':
           stat_df = np.sqrt(UVFFBAR + UVOOBAR - 2*UVFOBAR)
   elif stat == 'S1': # S1
       if line_type == 'GRAD':
           stat_df = S1
   elif stat == 'SRATIO': # Success Ratio
       if line_type == 'CTC':
           stat_df = 1 - (FY_ON/(FY_ON + FY_OY))
   elif stat == 'STDEV_ERR': # Standard Deviation of Error
       if line_type == 'SL1L2':
           stat_df = np.sqrt(
               FFBAR + OOBAR - FBAR*FBAR - OBAR*OBAR - 2*FOBAR + 2*FBAR*OBAR
           )
   else:
        logger.error(stat+" IS NOT AN OPTION")
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
