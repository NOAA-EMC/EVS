#!/usr/bin/env python3
'''
Name: subseasonal_util.py
Contact(s): Shannon Shields
Abstract: This contains many functions used across subseasonal.
'''

import os
import datetime
import numpy as np
import subprocess
import shutil
import sys
import netCDF4 as netcdf
import numpy as np
import glob
import pandas as pd
import logging
import copy
from time import sleep

def run_shell_command(command):
    """! Run shell command

         Args:
             command - list of argument entries (string)

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
    if os.environ['STEP'] == 'prep':
        conf_file = os.path.join(os.environ['PARMevs'], 'metplus_config',
                                 os.environ['STEP'],
                                 os.environ['COMPONENT'],
                                 'grid2grid',
                                 conf_file_name)
    else:
        conf_file = os.path.join(os.environ['PARMevs'], 'metplus_config',
                                 os.environ['STEP'],
                                 os.environ['COMPONENT'],
                                 os.environ['VERIF_CASE'],
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
            lmf.write(f'export subject="F{fhr} {model.upper()} Forecast '
                      +'Data Missing for EVS subseasonal"\n')
            lmf.write(f'echo "Warning: No {model.upper()} forecast was '
                      +f'available for {init_dt:%Y%m%d%H}f{fhr}" '
                      +'> mailmsg\n')
            lmf.write(f'echo "Missing file is {missing_file}" >> mailmsg\n')
            lmf.write(f'echo "Job ID: $jobid" >> mailmsg\n')
            lmf.write(f'cat mailmsg | mail -s "$subject" $MAILTO\n')
        os.chmod(log_missing_file, 0o755)

def log_missing_file_obs(log_missing_file, missing_file, obs, valid_dt):
    """! This writes a missing obs file to a log

         Args:
             log_missing_file - log of missing file (string)
             missing_file     - missing file path (string)
             obs              - observation name (string)
             valid_dt         - initialization date (datetime)
    """
    if not os.path.exists(log_missing_file):
        with open(log_missing_file, "w") as lmf:
            lmf.write("#!/bin/bash\n")
            if obs == 'nam':
                lmf.write(f'export subject="{obs.upper()} prepbufr Data '
                          +'Missing for '
                          +'EVS subseasonal"\n')
                lmf.write(f'echo "Warning: No {obs.upper()} prepbufr data '
                          +f'was available for '
                          +f'valid date {valid_dt:%Y%m%d%H}" > mailmsg\n')
            else:
                lmf.write(f'export subject="{obs.upper()} Analysis Data '
                          +'Missing for '
                          +'EVS subseasonal"\n')
                lmf.write(f'echo "Warning: No {obs.upper()} Analysis data '
                          +f'was available for '
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
        shutil.copy2(source_file, dest_file)

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
             init_hour    - init hour (integer)
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

def prep_prod_gefs_file(source_afile, source_bfile, prepped_file, dest_file, 
                        init_dt, forecast_hour, prep_method,
                        log_missing_file):
    """! Do prep work for GEFS production files

         Args:
             source_afile       - source a file format (string)
             source_bfile       - source b file format (string)
             prepped_file       - prepped file (string)
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
    WGRIB2 = os.environ['WGRIB2']
    EXECevs = os.environ['EXECevs']
    # Working file names
    working_file1 = prepped_file+'.tmp1'
    # Prep file
    if prep_method == 'full': 
        if forecast_hour == 0:
            wgrib_fhr = 'anl'
        else:
            wgrib_fhr = forecast_hour
        thin_var_level_list = [
            'HGT:500 mb',
            'ULWRF:top of atmosphere',
            'APCP:surface',
            'ICETK:surface',
            'ICEC:surface',
            'TMP:surface',
            'TMP:2 m above ground',
            'TMAX:2 m above ground',
            'TMIN:2 m above ground',
            'UGRD:850 mb',
            'UGRD:200 mb',
            'UGRD:10 m above ground',
            'VGRD:850 mb', 
            'VGRD:200 mb', 
            'VGRD:10 m above ground'
        ]
        
        if check_file_exists_size(source_afile) \
                and check_file_exists_size(source_bfile):
            run_shell_command(['>', prepped_file])
            for thin_var_level in thin_var_level_list:
                run_shell_command([WGRIB2, '-match', '"'+thin_var_level+'"',
                                   source_afile+'|'+WGRIB2, '-i', 
                                   source_afile,
                                   '-grib', working_file1])
                run_shell_command(['cat', working_file1, '>>', prepped_file])
                run_shell_command([WGRIB2, '-match', '"'+thin_var_level+'"',
                                   source_bfile+'|'+WGRIB2, '-i',
                                   source_bfile,
                                   '-grib', working_file1])
                run_shell_command(['cat', working_file1, '>>', prepped_file])
                os.remove(working_file1)
        else:
            log_missing_file_model(log_missing_file, source_afile,
                                   'gefs', init_dt,
                                   str(forecast_hour).zfill(3))

def prep_prod_cfs_pfile(source_pfile, prepped_pfile, dest_pfile,
                        init_dt, forecast_hour, prep_method, 
                        log_missing_pfile):
    """! Do prep work for CFS production pgbf files

         Args:
             source_pfile       - source pgbf file format (string)
             prepped_pfile      - prepped pgbf file (string)
             dest_pfile         - destination pgbf file (string)
             init_dt            - initialization date (datetime)
             forecast_hour      - forecast hour (string)
             prep_method        - name of prep method to do
                                  (string)
             log_missing_pfile  - text file path to write that
                                  production file is missing (string)

         Returns:
    """
    # Environment variables and executables
    WGRIB2 = os.environ['WGRIB2']
    EXECevs = os.environ['EXECevs']
    # Working file names
    working_file1 = prepped_pfile+'.tmp1'
    # Prep file
    if prep_method == 'full':
        if forecast_hour == 0:
            wgrib_fhr = 'anl'
        else:
            wgrib_fhr = forecast_hour
        thin_var_level_list = [
            'HGT:500 mb',
            'APCP:surface',
            'UGRD:850 mb',
            'UGRD:200 mb',
            'VGRD:850 mb',
            'VGRD:200 mb'
        ]

        if check_file_exists_size(source_pfile):
            run_shell_command(['>', prepped_pfile])
            for thin_var_level in thin_var_level_list:
                run_shell_command([WGRIB2, '-match', '"'+thin_var_level+'"',
                                   source_pfile+'|'+WGRIB2, '-i',
                                   source_pfile,
                                   '-grib', working_file1])
                run_shell_command(['cat', working_file1, '>>', prepped_pfile])
                os.remove(working_file1)
        else:
            log_missing_file_model(log_missing_pfile, source_pfile,
                                   'cfs', init_dt,
                                   str(forecast_hour).zfill(3))

def prep_prod_cfs_ffile(source_ffile, prepped_ffile, dest_ffile,
                        init_dt, forecast_hour, prep_method,
                        log_missing_ffile):
    """! Do prep work for CFS production flxf files

         Args:
             source_ffile       - source flxf file format (string)
             prepped_ffile      - prepped flxf file (string)
             dest_ffile         - destination flxf file (string)
             init_dt            - initialization date (datetime)
             forecast_hour      - forecast hour (string)
             prep_method        - name of prep method to do
                                  (string)
             log_missing_ffile  - text file path to write that
                                  production file is missing (string)

         Returns:
    """
    # Environment variables and executables
    WGRIB2 = os.environ['WGRIB2']
    EXECevs = os.environ['EXECevs']
    # Working file names
    working_file1 = prepped_ffile+'.tmp1'
    # Prep file
    if prep_method == 'full':
        if forecast_hour == 0:
            wgrib_fhr = 'anl'
        else:
            wgrib_fhr = forecast_hour
        thin_var_level_list = [
            'ULWRF:top of atmosphere',
            'ICETK:surface',
            'ICEC:surface',
            'TMP:surface',
            'TMP:2 m above ground',
            'TMAX:2 m above ground',
            'TMIN:2 m above ground',
            'UGRD:10 m above ground',
            'VGRD:10 m above ground'
        ]

        if check_file_exists_size(source_ffile):
            run_shell_command(['>', prepped_ffile])
            for thin_var_level in thin_var_level_list:
                run_shell_command([WGRIB2, '-match', '"'+thin_var_level+'"',
                                   source_ffile+'|'+WGRIB2, '-i',
                                   source_ffile,
                                   '-grib', working_file1])
                run_shell_command(['cat', working_file1, '>>', prepped_ffile])
                os.remove(working_file1)
        else:
            log_missing_file_model(log_missing_ffile, source_ffile,
                                   'cfs', init_dt,
                                   str(forecast_hour).zfill(3))

def prep_prod_gfs_file(source_file, dest_file, date_dt, log_missing_file):
    """! Do prep work for GFS analysis production files

         Args:
             source_file       - source file format (string)
             dest_file         - destination file (string)
             date_dt           - date (datetime object)
             log_missing_file  - text file path to write that
                                 production file is missing (string)

         Returns:
    """
    # Environment variables and executables
    WGRIB2 = os.environ['WGRIB2']
    EXECevs = os.environ['EXECevs']
    # Working file names
    prepped_file = os.path.join(os.getcwd(),
                                'atmos.'+dest_file.rpartition('/')[2])
    working_file1 = prepped_file+'.tmp1'
    # Prep file
    thin_var_level_list = [
        'HGT:500 mb',
        'UGRD:850 mb',
        'UGRD:200 mb',
        'VGRD:850 mb',
        'VGRD:200 mb'
    ]
    if check_file_exists_size(source_file):
        run_shell_command(['>', prepped_file])
        for thin_var_level in thin_var_level_list:
            run_shell_command([WGRIB2, '-match', '"'+thin_var_level+'"',
                               source_file+'|'+WGRIB2, '-i', source_file,
                               '-grib', working_file1])
            run_shell_command(['cat', working_file1, '>>', prepped_file])
            os.remove(working_file1)
    else:
        log_missing_file_obs(log_missing_file, source_file,
                             'GFS', date_dt)
    copy_file(prepped_file, dest_file)

def prep_prod_osi_saf_file(daily_source_file_format, daily_dest_file,
                           date_dt, log_missing_file):
    """! Do prep work for OSI-SAF production files

         Args:
             daily_source_file_format - daily source file format (string)
             daily_dest_file          - daily destination file (string)
             date_dt                  - date (datetime object)
             log_missing_file         - text file path to write that
                                        production file is missing (string)
         Returns:
    """
    # Environment variables and executables
    FIXevs = os.environ['FIXevs']
    CDO_ROOT = os.environ['CDO_ROOT']
    # Temporary file name
    daily_prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                      +daily_dest_file.rpartition('/')[2])
    # Prep daily file
    for hem in ['nh', 'sh']:
        hem_source_file = daily_source_file_format.replace('{hem?fmt=str}',
                                                           hem)
        hem_dest_file = daily_dest_file.replace('multi.', 'multi.'+hem+'.')
        hem_prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                        +hem_dest_file.rpartition('/')[2])
        if check_file_exists_size(hem_source_file):
            run_shell_command(
                [os.path.join(CDO_ROOT, 'bin', 'cdo'),
                'remapbil,'
                +os.path.join(FIXevs, 'cdo_grids', 'G003.grid'),
                hem_source_file, hem_prepped_file]
            )
        else:
            log_missing_file_obs(log_missing_file, hem_source_file,
                                 f"OSI-SAF {hem.upper()}", date_dt)
        if hem == 'nh':
            nh_prepped_file = hem_prepped_file
        elif hem == 'sh':
            sh_prepped_file = hem_prepped_file
    if check_file_exists_size(nh_prepped_file) \
            and check_file_exists_size(sh_prepped_file):
        nh_data = netcdf.Dataset(nh_prepped_file)
        sh_data = netcdf.Dataset(sh_prepped_file)
        merged_data = netcdf.Dataset(daily_prepped_file, 'w',
                                     format='NETCDF3_CLASSIC')
        for attr in nh_data.ncattrs():
            if attr == 'history':
                merged_data.setncattr(
                    attr, nh_data.getncattr(attr)+' '
                    +sh_data.getncattr(attr)
                )
            elif attr == 'southernmost_latitude':
                merged_data.setncattr(attr, '-90')
            elif attr == 'area':
                merged_data.setncattr(attr, 'Global')
            else:
                merged_data.setncattr(attr, nh_data.getncattr(attr))
        for dim in list(nh_data.dimensions.keys()):
            merged_data.createDimension(dim, len(nh_data.dimensions[dim]))
        for var in ['time', 'time_bnds', 'lat', 'lon']:
            merged_var = merged_data.createVariable(
                var, nh_data.variables[var].datatype,
                nh_data.variables[var].dimensions
            )
            for k in nh_data.variables[var].ncattrs():
                merged_var.setncatts(
                    {k: nh_data.variables[var].getncattr(k)}
                )
            if var == 'time':
                merged_var[:] = nh_data.variables[var][:] + 43200
            else:
                merged_var[:] = nh_data.variables[var][:]
        for var in ['ice_conc', 'raw_ice_conc_values',
                    'status_flag', 'total_uncertainty',
                    'smearing_uncertainty', 'algorithm_uncertainty']:
            merged_var = merged_data.createVariable(
                var, nh_data.variables[var].datatype,
                ('lat', 'lon')
            )
            for k in nh_data.variables[var].ncattrs():
                if k == 'long_name':
                    merged_var.setncatts(
                        {k: nh_data.variables[var].getncattr(k)\
                        .replace('northern hemisphere', 'globe')}
                    )
                else:
                    merged_var.setncatts(
                        {k: nh_data.variables[var].getncattr(k)}
                    )
            merged_var_vals = np.ma.masked_equal(
                np.vstack((sh_data.variables[var][0,:90,:],
                           nh_data.variables[var][0,90:,:]))
               ,nh_data.variables[var]._FillValue)
            merged_var[:] = merged_var_vals
        merged_data.close()
    copy_file(daily_prepped_file, daily_dest_file)

def prep_prod_ghrsst_ospo_file(daily_source_file, daily_dest_file,
                               date_dt, log_missing_file):
    """! Do prep work for GHRSST OSPO production files

         Args:
             daily_source_file - daily source file (string)
             daily_dest_file   - daily destination file (string)
             date_dt           - date (datetime object)
             log_missing_file  - text file path to write that
                                 production file is missing (string)
         Returns:
    """
    # Temporary file name
    daily_prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                      +daily_source_file.rpartition('/')[2])
    # Prep daily file
    if check_file_exists_size(daily_source_file):
        copy_file(daily_source_file, daily_prepped_file)
    else:
        log_missing_file_obs(log_missing_file, daily_source_file,
                               'GHRSST OSPO', date_dt)
    if check_file_exists_size(daily_prepped_file):
        dly_prepped_data = netcdf.Dataset(daily_prepped_file, 'a',
                                          format='NETCDF3_CLASSIC')
        ghrsst_ospo_date_since_dt = datetime.datetime.strptime(
            '1981-01-01 00:00:00','%Y-%m-%d %H:%M:%S'
        )
        dly_prepped_data['time'][:] = dly_prepped_data['time'][:][0] + 43200
        dly_prepped_data.close()
    copy_file(daily_prepped_file, daily_dest_file)

def weekly_osi_saf_file(weekly_source_file_list, weekly_dest_file,
                        weekly_dates):
    """! Gather weekly OSI-SAF production files

         Args:
             weekly_source_file_list  - list of daily files to make up
                                        weekly average file
             weekly_dest_file         - weekly destination file (string)
             weekly_dates             - date span for weekly period (tuple
                                        of datetimes)
         Returns:
    """
    # Temporary file name
    weekly_prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                       +weekly_dest_file.rpartition('/')[2])
    # Prep weekly file
    for weekly_source_file in weekly_source_file_list:
        if not os.path.exists(weekly_source_file):
            print(f"WARNING: {weekly_source_file} does not exist, "
                  +"not using in weekly average file")
            weekly_source_file_list.remove(weekly_source_file)
    # 80% file check from expected 7
    if len(weekly_source_file_list) >= 6:
        ncea_cmd_list = ['ncea']
        for weekly_source_file in weekly_source_file_list:
            ncea_cmd_list.append(weekly_source_file)
        ncea_cmd_list.append('-o')
        ncea_cmd_list.append(weekly_prepped_file)
        run_shell_command(ncea_cmd_list)
        if check_file_exists_size(weekly_prepped_file):
            weekly_data = netcdf.Dataset(weekly_prepped_file, 'a',
                                         format='NETCDF3_CLASSIC')
            weekly_data.setncattr(
                'start_date', weekly_dates[0].strftime('%Y-%m-%d %H:%M:%S')
            )
            osi_saf_date_since_dt = datetime.datetime.strptime(
                '1978-01-01 00:00:00','%Y-%m-%d %H:%M:%S'
            )
            weekly_data.variables['time_bnds'][:] = [
                (weekly_dates[0] - osi_saf_date_since_dt).total_seconds(),
                weekly_data.variables['time_bnds'][:][0][1]
            ]
            weekly_data.close()
    else:
        print("WARNING: Not enough files to make "+weekly_prepped_file
              +": "+' '.join(weekly_source_file_list))
    print("Linking "+weekly_prepped_file+" to "+weekly_dest_file)
    os.symlink(weekly_prepped_file, weekly_dest_file)

def monthly_osi_saf_file(monthly_source_file_list,
                         monthly_dest_file,
                         monthly_dates):
    """! Gather monthly OSI-SAF production files

         Args:
             monthly_source_file_list - list of daily files to make up
                                        monthly average file
             monthly_dest_file        - monthly destination file (string)
             monthly_dates            - date span for monthly period (tuple)
         Returns:
    """
    # Temporary file name
    monthly_prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                        +monthly_dest_file.rpartition('/')[2])
    # Prep monthly file
    for monthly_source_file in monthly_source_file_list:
        if not os.path.exists(monthly_source_file):
            print(f"WARNING: {monthly_source_file} does not exist, "
                  +"not using in monthly average file")
            monthly_source_file_list.remove(monthly_source_file)
    # 80% file check from expected 30
    if len(monthly_source_file_list) >= 24:
        ncea_cmd_list = ['ncea']
        for monthly_source_file in monthly_source_file_list:
            ncea_cmd_list.append(monthly_source_file)
        ncea_cmd_list.append('-o')
        ncea_cmd_list.append(monthly_prepped_file)
        run_shell_command(ncea_cmd_list)
        if check_file_exists_size(monthly_prepped_file):
            monthly_data = netcdf.Dataset(monthly_prepped_file, 'a',
                                          format='NETCDF3_CLASSIC')
            monthly_data.setncattr(
                'start_date', monthly_dates[0].strftime('%Y-%m-%d %H:%M:%S')
            )
            osi_saf_date_since_dt = datetime.datetime.strptime(
                '1978-01-01 00:00:00','%Y-%m-%d %H:%M:%S'
            )
            monthly_data.variables['time_bnds'][:] = [
                (monthly_dates[0] - osi_saf_date_since_dt).total_seconds(),
                monthly_data.variables['time_bnds'][:][0][1]
            ]
            monthly_data.close()
    else:
        print("WARNING: Not enough files to make "+monthly_prepped_file
              +": "+' '.join(monthly_source_file_list))
    print("Linking "+monthly_prepped_file+" to "+monthly_dest_file)
    os.symlink(monthly_prepped_file, monthly_dest_file)

def weekly_ghrsst_ospo_file(weekly_source_file_list, weekly_dest_file,
                            weekly_dates):
    """! Gather weekly GHRSST OSPO production files

         Args:
             weekly_source_file_list  - list of daily files to make up
                                        weekly average file
             weekly_dest_file         - weekly destination file (string)
             weekly_dates             - date span for weekly period (tuple
                                        of datetimes)
         Returns:
    """
    # Temporary file name
    weekly_prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                       +weekly_dest_file.rpartition('/')[2])
    # Prep weekly file
    for weekly_source_file in weekly_source_file_list:
        if not os.path.exists(weekly_source_file):
            print(f"WARNING: {weekly_source_file} does not exist, "
                  +"not using in weekly average file")
            weekly_source_file_list.remove(weekly_source_file)
    # 80% file check from expected 7
    if len(weekly_source_file_list) >= 6:
        ncea_cmd_list = ['ncea']
        for weekly_source_file in weekly_source_file_list:
            ncea_cmd_list.append(weekly_source_file)
        ncea_cmd_list.append('-o')
        ncea_cmd_list.append(weekly_prepped_file)
        run_shell_command(ncea_cmd_list)
        if check_file_exists_size(weekly_prepped_file):
            weekly_data = netcdf.Dataset(weekly_prepped_file, 'a',
                                         format='NETCDF3_CLASSIC')
            weekly_data.setncattr(
                'start_time', weekly_dates[0].strftime('%Y-%m-%d %H:%M:%S')
            )
            weekly_data.setncattr(
                'time_coverage_start',
                weekly_dates[0].strftime('%Y-%m-%d %H:%M:%S')
            )
            weekly_data.setncattr(
                'stop_time', weekly_dates[1].strftime('%Y-%m-%d %H:%M:%S')
            )
            weekly_data.setncattr(
                'time_coverage_end',
                weekly_dates[1].strftime('%Y-%m-%d %H:%M:%S')
            )
            weekly_data['time'][:] = weekly_data['time'][:][-1]
            weekly_data.close()
    else:
        print("WARNING: Not enough files to make "+weekly_prepped_file
              +": "+' '.join(weekly_source_file_list))
    print("Linking "+weekly_prepped_file+" to "+weekly_dest_file)
    os.symlink(weekly_prepped_file, weekly_dest_file)

def monthly_ghrsst_ospo_file(monthly_source_file_list,
                             monthly_dest_file,
                             monthly_dates):
    """! Gather monthly GHRSST OSPO production files

         Args:
             monthly_source_file_list - list of daily files to make up
                                        monthly average file
             monthly_dest_file        - monthly destination file (string)
             monthly_dates            - date span for monthly period (tuple)
         Returns:
    """
    # Temporary file name
    monthly_prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                        +monthly_dest_file.rpartition('/')[2])
    # Prep monthly file
    for monthly_source_file in monthly_source_file_list:
        if not os.path.exists(monthly_source_file):
            print(f"WARNING: {monthly_source_file} does not exist, "
                  +"not using in monthly average file")
            monthly_source_file_list.remove(monthly_source_file)
    # 80% file check from expected 30
    if len(monthly_source_file_list) >= 24:
        ncea_cmd_list = ['ncea']
        for monthly_source_file in monthly_source_file_list:
            ncea_cmd_list.append(monthly_source_file)
        ncea_cmd_list.append('-o')
        ncea_cmd_list.append(monthly_prepped_file)
        run_shell_command(ncea_cmd_list)
        if check_file_exists_size(monthly_prepped_file):
            monthly_data = netcdf.Dataset(monthly_prepped_file, 'a',
                                          format='NETCDF3_CLASSIC')
            monthly_data.setncattr(
                'start_time', monthly_dates[0].strftime('%Y-%m-%d %H:%M:%S')
            )
            monthly_data.setncattr(
                'time_coverage_start',
                monthly_dates[0].strftime('%Y-%m-%d %H:%M:%S')
            )
            monthly_data.setncattr(
                'stop_time', monthly_dates[1].strftime('%Y-%m-%d %H:%M:%S')
            )
            monthly_data.setncattr(
                'time_coverage_end',
                monthly_dates[1].strftime('%Y-%m-%d %H:%M:%S')
            )
            monthly_data['time'][:] = monthly_data['time'][:][-1]
            monthly_data.close()
    else:
        print("WARNING: Not enough files to make "+monthly_prepped_file
              +": "+' '.join(monthly_source_file_list))
    print("Linking "+monthly_prepped_file+" to "+monthly_dest_file)
    os.symlink(monthly_prepped_file, monthly_dest_file)


def get_model_file(valid_time_dt, init_time_dt, forecast_hour,
                   source_file_format, dest_file_format):
    """! This gets a model file and saves it in the specified
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
    if not os.path.exists(dest_file):
        source_file = format_filler(source_file_format, valid_time_dt,
                                    init_time_dt, forecast_hour, {})
        if 'wgrbbul/ecmwf' in source_file:
            prep_prod_ecmwf_file(source_file, dest_file, forecast_hour, 'full')
        else:
            if os.path.exists(source_file):
                print("Linking "+source_file+" to "+dest_file)
                os.symlink(source_file, dest_file)   
            else:
                print("WARNING: "+source_file+" DOES NOT EXIST")

def get_truth_file(valid_time_dt, source_file_format, dest_file_format):
    """! This gets a truth/obs file and saves it in the specified
         destination
         
         Args:
             valid_time_dt      - valid time (datetime)
             source_file_format - source file format (string)
             dest_file_format   - destination file format (string)
         

         Returns:
    """
    dest_file = format_filler(dest_file_format, valid_time_dt,
                              valid_time_dt, ['anl'], {})
    if not os.path.exists(dest_file):
        source_file = format_filler(source_file_format, valid_time_dt,
                                    valid_time_dt, ['anl'], {})
        if os.path.exists(source_file):
            print("Linking "+source_file+" to "+dest_file)
            os.symlink(source_file, dest_file)
        else:
            print("WARNING: "+source_file+" DOES NOT EXIST")


def check_gefs_prep_files(job_dict):
    """! Check if COMOUT GEFS prep files exist and adjust fhr_list

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             fhr_list - adjusted list of forecast hours that are
                        needed for prep (string)
    """
    init_date_dt = datetime.datetime.strptime(
        job_dict['INITDATE']+job_dict['init_hr_start'],
        '%Y%m%d%H'
    )
    model = job_dict['MODEL']
    inithr = job_dict['init_hr_start']
    fhr_min = int(job_dict['fhr_start'])
    fhr_max = int(job_dict['fhr_end'])
    fhr_inc = 6
    fhr = fhr_min
    fhr_list = []
    fhr_check_output_dict = {}
    while fhr <= fhr_max:
        fhr_check_output_dict[str(fhr)] = {}
        if job_dict['JOB_GROUP'] == 'retrieve_data':
            # Check by last GEFS member file
            # If that exists, then all other member files exist
            # for the specific fhr
            output_COMOUT_file_format = os.path.join(
                job_dict['COMOUT']+'.'+job_dict['INITDATE'],
                model, model+'.'
                +'ens30.t'+inithr+'z'
                +'.pgrb2.0p50.'
                +'f{lead?fmt=%3H}'
            )
            # Use this file format to state all member files exist
            # for a specific fhr
            restart_COMOUT_file_format = os.path.join(
                job_dict['COMOUT']+'.'+job_dict['INITDATE'],
                model, model+'.'
                +'ens*.t'+inithr+'z'
                +'.pgrb2.0p50.'
                +'f{lead?fmt=%3H}'
            )
            fhr_check_output_dict[str(fhr)]['file1'] = {
                'valid_date': init_date_dt,
                'init_date': init_date_dt,
                'forecast_hour': str(fhr)
            }
        fhr+=fhr_inc
    # Check output files
    for fhr_key in list(fhr_check_output_dict.keys()):
        fhr_key_output_files_exist_list = []
        for fhr_fileN_key in list(fhr_check_output_dict[fhr_key].keys()):
            fhr_fileN_COMOUT = format_filler(
                output_COMOUT_file_format,
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['valid_date'],
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['init_date'],
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['forecast_hour'],
                {}
            )
            fhr_fileN_restart = format_filler(
                restart_COMOUT_file_format,
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['valid_date'],
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['init_date'],
                fhr_check_output_dict[fhr_key][fhr_fileN_key]['forecast_hour'],
                {}
            )
            if os.path.exists(fhr_fileN_COMOUT):
                fhr_key_output_files_exist_list.append(True)
                print("COMOUT files "+fhr_fileN_restart+" exist and will not"
                      +" be generated in prep restart")
            else:
                fhr_key_output_files_exist_list.append(False)
                fhr_list.append(
                    fhr_check_output_dict[fhr_key][fhr_fileN_key]\
                    ['forecast_hour']
                )
    fhr_list = list(
        np.asarray(np.unique(np.asarray(fhr_list, dtype=int)),dtype=str)
    )
    return fhr_list


def check_ccpa_prep_files(DATA, STEP, INITDATE):
    """!
        Args:
            DATA     - Temporary working directory (string)
            STEP     - Step (string)
            INITDATE - Initialization date (string, format: YYYYmmdd)

        Returns:
            all_ccpa_file_exist - if all needed ccpa files
                                  exist or not (boolean)
    """
    cdate_dt = datetime.datetime.strptime(
        INITDATE+'12',
        '%Y%m%d%H'
    )
    temp_dir = os.path.join(
        DATA, STEP
    )
    ccpa_file_list = []
    ccpa_file_format = os.path.join(
        temp_dir, 'data', 'ccpa',
        'ccpa.6H.{init?fmt=%Y%m%d%H}'
    )
    nf = 0
    while nf <= 3:
        ccpa_file = format_filler(
            ccpa_file_format,
            (cdate_dt-datetime.timedelta(hours=6*nf)),
            (cdate_dt-datetime.timedelta(hours=6*nf)),
            ['anl'], {}
        )
        ccpa_file_list.append(ccpa_file)
        nf+=1
    ccpa_files_exist_list = []
    for ccpa_file in ccpa_file_list:
        if os.path.exists(ccpa_file):
            ccpa_files_exist_list.append(True)
        else:
            ccpa_files_exist_list.append(False)
    if all(x == True for x in ccpa_files_exist_list) \
            and len(ccpa_files_exist_list) > 0:
        all_ccpa_file_exist = True
    else:
        all_ccpa_file_exist = False
    return all_ccpa_file_exist


def check_daily_model_files(job_dict):
    """! Check if model files exist for daily reformat step

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             model_files_exist - if correct number of model files
                                 exist or not (boolean)
             fhr_list          - list of forecast hours that model
                                 files exist for (string)
             model_copy_output_DATA2COMOUT_list - list of files to copy from
                                                  DATA to COMOUT
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hr_start'],
        '%Y%m%d%H'
    )
    init_date_dt = datetime.datetime.strptime(
        job_dict['CORRECT_INIT_DATE']+job_dict['init_hr_start'],
        '%Y%m%d%H'
    )
    verif_case_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE']+'_'+job_dict['STEP']
    )
    model = job_dict['MODEL']
    members = job_dict['members']
    fhr_list = []
    fhr_check_input_dict = {}
    fhr_check_output_dict = {}
    for fhr in [int(i) for i in job_dict['CORRECT_LEAD_SEQ'].split(',')]:
        fhr_check_input_dict[str(fhr)] = {}
        fhr_check_output_dict[str(fhr)] = {}
        valid_date_dt = init_date_dt + datetime.timedelta(hours=fhr)
        if job_dict['JOB_GROUP'] == 'reformat_data':
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] == 'sst' \
                      and job_dict['job_name'] == 'SST':
                    mb = str(members).zfill(2)
                    input_file_format = os.path.join(verif_case_dir, 'data',
                                                     model,
                                                     model+'.ens'+mb
                                                     +'.{init?fmt=%Y%m%d%H}.'
                                                     +'f{lead?fmt=%3H}')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        job_dict['MODEL'], job_dict['VERIF_CASE'],
                        'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        job_dict['MODEL'], job_dict['VERIF_CASE'],
                        'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
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
                        and job_dict['job_name'] == 'SST':
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
                # Copy restart files from COMOUT to DATA dir
                # to be used in restart and remove from fhr_list
                copy_file(fhr_fileN_COMOUT,fhr_fileN_DATA)
                print("COMOUT restart file "+fhr_fileN_COMOUT+" exists"
                      +" and will be used in stats restart")
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
    if len(input_fhr_list) == 3:
        model_files_exist = True
    else:
        model_files_exist = False
    return model_files_exist, fhr_list, model_copy_output_DATA2COMOUT_list


def check_weekly_model_files(job_dict):
    """! Check if model files exist for weekly reformat and assemble step

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             model_files_exist - if 80% of model files
                                 exist or not (boolean)
             fhr_list          - list of forecast hours that model
                                 files exist for (string)
             model_copy_output_DATA2COMOUT_list - list of files to copy from
                                                  DATA to COMOUT
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hr_start'],
        '%Y%m%d%H'
    )
    init_date_dt = datetime.datetime.strptime(
        job_dict['CORRECT_INIT_DATE']+job_dict['init_hr_start'],
        '%Y%m%d%H'
    )
    verif_case_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE']+'_'+job_dict['STEP']
    )
    model = job_dict['MODEL']
    members = job_dict['members']
    fhr_list = []
    fhr_check_input_dict = {}
    fhr_check_output_dict = {}
    for fhr in [int(i) for i in job_dict['CORRECT_LEAD_SEQ'].split(',')]:
        fhr_check_input_dict[str(fhr)] = {}
        fhr_check_output_dict[str(fhr)] = {}
        valid_date_dt = init_date_dt + datetime.timedelta(hours=fhr)
        if job_dict['JOB_GROUP'] == 'reformat_data':
            if job_dict['VERIF_CASE'] in ['grid2grid', 'grid2obs']:
                if job_dict['VERIF_TYPE'] in ['seaice', 'sst', 
                                              'temp', 'prepbufr',
                                              'pres_lvls'] \
                      and job_dict['job_name'] in ['Concentration',
                                                   'SST',
                                                   'TempAnom2m',
                                                   'GenEnsProd',
                                                   'GeoHeightAnom']:
                    mb = str(members).zfill(2)
                    if job_dict['VERIF_TYPE'] == 'pres_lvls' \
                          and job_dict['MODEL'] == 'cfs':
                        input_file_format = os.path.join(verif_case_dir, 
                                                         'data',
                                                         model,
                                                         model+'.pgbf.ens'+mb
                                                         +'.{init?fmt=%Y%m%d%H}.'
                                                         +'f{lead?fmt=%3H}')
                    else:
                        input_file_format = os.path.join(verif_case_dir, 
                                                         'data',
                                                         model,
                                                         model+'.ens'+mb
                                                         +'.{init?fmt=%Y%m%d%H}.'
                                                         +'f{lead?fmt=%3H}')
                    if job_dict['VERIF_CASE'] == 'grid2grid':
                        output_DATA_file_format = os.path.join(
                            verif_case_dir, 'METplus_output',
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                            +job_dict['job_name']+'_{lead?fmt=%2H}'
                            '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
                        )
                        output_COMOUT_file_format = os.path.join(
                            job_dict['COMOUT'],
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                            +job_dict['job_name']+'_{lead?fmt=%2H}'
                            '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
                        )
                    if job_dict['VERIF_CASE'] == 'grid2obs':
                        output_DATA_file_format = os.path.join(
                            verif_case_dir, 'METplus_output',
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'gen_ens_prod_'+job_dict['VERIF_TYPE']+'_'
                            +'GenEnsProd_FHR{lead?fmt=%3H}'
                            +'_{valid?fmt=%Y%m%d}'
                            +'_{valid?fmt=%H}0000V_ens.nc'
                        )
                        output_COMOUT_file_format = os.path.join(
                            job_dict['COMOUT'],
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'gen_ens_prod_'+job_dict['VERIF_TYPE']+'_'
                            +'GenEnsProd_FHR{lead?fmt=%3H}'
                            +'_{valid?fmt=%Y%m%d}'
                            +'_{valid?fmt=%H}0000V_ens.nc'
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
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] == 'temp':
                    truth_file_format = os.path.join(
                        verif_case_dir, 'data', 'ecmwf',
                        'ecmwf.{valid?fmt=%Y%m%d%H}.anl'
                    )
                elif job_dict['VERIF_TYPE'] == 'pres_lvls':
                    truth_file_format = os.path.join(
                        verif_case_dir, 'data', 'gfs',
                        'gfs.{valid?fmt=%Y%m%d%H}.anl'
                    )
        elif job_dict['JOB_GROUP'] == 'assemble_data':
            if job_dict['VERIF_CASE'] == 'grid2obs':
                if job_dict['VERIF_TYPE'] == 'prepbufr' \
                      and job_dict['job_name'] == 'TempAnom2m':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'gen_ens_prod_'
                                                     +job_dict['VERIF_TYPE']
                                                     +'_GenEnsProd'
                                                     +'_FHR{lead?fmt=%3H}'
                                                     +'_{valid?fmt=%Y%m%d}'
                                                     +'_{valid?fmt=%H}0000V'
                                                     +'_ens.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        job_dict['MODEL'], job_dict['VERIF_CASE'],
                        'point_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        job_dict['MODEL'], job_dict['VERIF_CASE'],
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
            if job_dict['JOB_GROUP'] == 'reformat_data' \
                    and job_dict['job_name'] in ['TempAnom2m',
                                                 'GeoHeightAnom']:
                truth_file = format_filler(
                    truth_file_format,
                    fhr_check_input_dict[fhr_key][fhr_fileN_key]['valid_date'],
                    fhr_check_input_dict[fhr_key][fhr_fileN_key]['valid_date'],
                    ['anl'],
                    {}
                )
                if os.path.exists(fhr_fileN) \
                        and os.path.exists(truth_file):
                    fhr_key_input_files_exist_list.append(True)
                    fhr_list.append(
                        fhr_check_input_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
                else:
                    fhr_key_input_files_exist_list.append(False)
            elif job_dict['JOB_GROUP'] == 'reformat_data' \
                    and job_dict['job_name'] in ['Concentration',
                                                 'SST',
                                                 'GenEnsProd']:
                if os.path.exists(fhr_fileN):
                    fhr_key_input_files_exist_list.append(True)
                    fhr_list.append(
                        fhr_check_input_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
                else:
                    fhr_key_input_files_exist_list.append(False)
            elif job_dict['JOB_GROUP'] == 'assemble_data' \
                    and job_dict['job_name'] == 'TempAnom2m':
                if os.path.exists(fhr_fileN):
                    fhr_key_input_files_exist_list.append(True)
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
                # Copy restart files from COMOUT to DATA dir
                # to be used in restart and remove from fhr_list
                copy_file(fhr_fileN_COMOUT,fhr_fileN_DATA)
                print("COMOUT restart file "+fhr_fileN_COMOUT+" exists"
                      +" and will be used in stats restart")
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
    if len(input_fhr_list) >= 12:
        model_files_exist = True
    else:
        model_files_exist = False
    if len(fhr_list) == 0:
        model_files_exist = False
    return model_files_exist, fhr_list, model_copy_output_DATA2COMOUT_list


def check_monthly_model_files(job_dict):
    """! Check if model files exist for monthly reformat step

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             model_files_exist - if 80% of model files
                                 exist or not (boolean)
             fhr_list          - list of forecast hours that model
                                 files exist for (string)
             model_copy_output_DATA2COMOUT_list - list of files to copy from
                                                  DATA to COMOUT
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hr_start'],
        '%Y%m%d%H'
    )
    init_date_dt = datetime.datetime.strptime(
        job_dict['CORRECT_INIT_DATE']+job_dict['init_hr_start'],
        '%Y%m%d%H'
    )
    verif_case_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE']+'_'+job_dict['STEP']
    )
    model = job_dict['MODEL']
    members = job_dict['members']
    fhr_list = []
    fhr_check_input_dict = {}
    fhr_check_output_dict = {}
    for fhr in [int(i) for i in job_dict['CORRECT_LEAD_SEQ'].split(',')]:
        fhr_check_input_dict[str(fhr)] = {}
        fhr_check_output_dict[str(fhr)] = {}
        valid_date_dt = init_date_dt + datetime.timedelta(hours=fhr)
        if job_dict['JOB_GROUP'] == 'reformat_data':
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] in ['seaice', 'sst'] \
                      and job_dict['job_name'] in ['Concentration',
                                                   'SST']:
                    mb = str(members).zfill(2)
                    input_file_format = os.path.join(verif_case_dir, 'data',
                                                     model,
                                                     model+'.ens'+mb
                                                     +'.{init?fmt=%Y%m%d%H}.'
                                                     +'f{lead?fmt=%3H}')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        job_dict['MODEL'], job_dict['VERIF_CASE'],
                        'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        job_dict['MODEL'], job_dict['VERIF_CASE'],
                        'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
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
                        and job_dict['job_name'] in ['Concentration',
                                                     'SST']:
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
                # Copy restart files from COMOUT to DATA dir
                # to be used in restart and remove from fhr_list
                copy_file(fhr_fileN_COMOUT,fhr_fileN_DATA)
                print("COMOUT restart file "+fhr_fileN_COMOUT+" exists"
                      +" and will be used in stats restart")
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
    if len(input_fhr_list) >= 49:
        model_files_exist = True
    else:
        model_files_exist = False
    return model_files_exist, fhr_list, model_copy_output_DATA2COMOUT_list


def check_days6_10_model_files(job_dict):
    """! Check if model files exist for days 6-10 reformat and assemble step

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             model_files_exist - if 80% of model files
                                 exist or not (boolean)
             fhr_list          - list of forecast hours that model
                                 files exist for (string)
             model_copy_output_DATA2COMOUT_list - list of files to copy from
                                                  DATA to COMOUT
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hr_start'],
        '%Y%m%d%H'
    )
    init_date_dt = datetime.datetime.strptime(
        job_dict['CORRECT_INIT_DATE']+job_dict['init_hr_start'],
        '%Y%m%d%H'
    )
    verif_case_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE']+'_'+job_dict['STEP']
    )
    model = job_dict['MODEL']
    members = job_dict['members']
    fhr_list = []
    fhr_check_input_dict = {}
    fhr_check_output_dict = {}
    for fhr in [int(i) for i in job_dict['CORRECT_LEAD_SEQ'].split(',')]:
        fhr_check_input_dict[str(fhr)] = {}
        fhr_check_output_dict[str(fhr)] = {}
        valid_date_dt = init_date_dt + datetime.timedelta(hours=fhr)
        if job_dict['JOB_GROUP'] == 'reformat_data':
            if job_dict['VERIF_CASE'] in ['grid2grid', 'grid2obs']:
                if job_dict['VERIF_TYPE'] in ['temp', 'prepbufr',
                                              'pres_lvls'] \
                      and job_dict['job_name'] in ['TempAnom2m',
                                                   'GenEnsProd',
                                                   'GeoHeightAnom']:
                    mb = str(members).zfill(2)
                    if job_dict['VERIF_TYPE'] == 'pres_lvls' \
                          and job_dict['MODEL'] == 'cfs':
                        input_file_format = os.path.join(verif_case_dir,
                                                         'data',
                                                         model,
                                                         model+'.pgbf.ens'+mb
                                                         +'.{init?fmt=%Y%m%d%H}.'
                                                         +'f{lead?fmt=%3H}')
                    else:
                        input_file_format = os.path.join(verif_case_dir, 
                                                         'data',
                                                         model,
                                                         model+'.ens'+mb
                                                         +'.{init?fmt=%Y%m%d%H}.'
                                                         +'f{lead?fmt=%3H}')
                    if job_dict['VERIF_CASE'] == 'grid2grid':
                        output_DATA_file_format = os.path.join(
                            verif_case_dir, 'METplus_output',
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                            +job_dict['job_name']+'_{lead?fmt=%2H}'
                            '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
                        )
                        output_COMOUT_file_format = os.path.join(
                            job_dict['COMOUT'],
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                            +job_dict['job_name']+'_{lead?fmt=%2H}'
                            '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
                        )
                    if job_dict['VERIF_CASE'] == 'grid2obs':
                        output_DATA_file_format = os.path.join(
                            verif_case_dir, 'METplus_output',
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'gen_ens_prod_'+job_dict['VERIF_TYPE']+'_'
                            +'GenEnsProd_FHR{lead?fmt=%3H}'
                            +'_{valid?fmt=%Y%m%d}'
                            +'_{valid?fmt=%H}0000V_ens.nc'
                        )
                        output_COMOUT_file_format = os.path.join(
                            job_dict['COMOUT'],
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'gen_ens_prod_'+job_dict['VERIF_TYPE']+'_'
                            +'GenEnsProd_FHR{lead?fmt=%3H}'
                            +'_{valid?fmt=%Y%m%d}'
                            +'_{valid?fmt=%H}0000V_ens.nc'
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
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] == 'temp':
                    truth_file_format = os.path.join(
                        verif_case_dir, 'data', 'ecmwf',
                        'ecmwf.{valid?fmt=%Y%m%d%H}.anl'
                    )
                elif job_dict['VERIF_TYPE'] == 'pres_lvls':
                    truth_file_format = os.path.join(
                        verif_case_dir, 'data', 'gfs',
                        'gfs.{valid?fmt=%Y%m%d%H}.anl'
                    )
        elif job_dict['JOB_GROUP'] == 'assemble_data':
            if job_dict['VERIF_CASE'] == 'grid2obs':
                if job_dict['VERIF_TYPE'] == 'prepbufr' \
                      and job_dict['job_name'] == 'TempAnom2m':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'gen_ens_prod_'
                                                     +job_dict['VERIF_TYPE']
                                                     +'_GenEnsProd'
                                                     +'_FHR{lead?fmt=%3H}'
                                                     +'_{valid?fmt=%Y%m%d}'
                                                     +'_{valid?fmt=%H}0000V'
                                                     +'_ens.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        job_dict['MODEL'], job_dict['VERIF_CASE'],
                        'point_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        job_dict['MODEL'], job_dict['VERIF_CASE'],
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
            if job_dict['JOB_GROUP'] == 'reformat_data' \
                    and job_dict['job_name'] in ['TempAnom2m',
                                                 'GeoHeightAnom']:
                truth_file = format_filler(
                    truth_file_format,
                    fhr_check_input_dict[fhr_key][fhr_fileN_key]['valid_date'],
                    fhr_check_input_dict[fhr_key][fhr_fileN_key]['valid_date'],
                    ['anl'],
                    {}
                )
                if os.path.exists(fhr_fileN) \
                        and os.path.exists(truth_file):
                    fhr_key_input_files_exist_list.append(True)
                    fhr_list.append(
                        fhr_check_input_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
                else:
                    fhr_key_input_files_exist_list.append(False)
            elif job_dict['JOB_GROUP'] == 'reformat_data' \
                    and job_dict['job_name'] == 'GenEnsProd':
                if os.path.exists(fhr_fileN):
                    fhr_key_input_files_exist_list.append(True)
                    fhr_list.append(
                        fhr_check_input_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
                else:
                    fhr_key_input_files_exist_list.append(False)
            elif job_dict['JOB_GROUP'] == 'assemble_data' \
                    and job_dict['job_name'] == 'TempAnom2m':
                if os.path.exists(fhr_fileN):
                    fhr_key_input_files_exist_list.append(True)
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
                # Copy restart files from COMOUT to DATA dir
                # to be used in restart and remove from fhr_list
                copy_file(fhr_fileN_COMOUT,fhr_fileN_DATA)
                print("COMOUT restart file "+fhr_fileN_COMOUT+" exists"
                      +" and will be used in stats restart")
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
    if len(input_fhr_list) >= 9:
        model_files_exist = True
    else:
        model_files_exist = False
    if len(fhr_list) == 0:
        model_files_exist = False
    return model_files_exist, fhr_list, model_copy_output_DATA2COMOUT_list


def check_weeks3_4_model_files(job_dict):
    """! Check if model files exist for weeks 3-4 reformat and assemble step

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             model_files_exist - if 80% of model files
                                 exist or not (boolean)
             fhr_list          - list of forecast hours that model
                                 files exist for (string)
             model_copy_output_DATA2COMOUT_list - list of files to copy from
                                                  DATA to COMOUT
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hr_start'],
        '%Y%m%d%H'
    )
    init_date_dt = datetime.datetime.strptime(
        job_dict['CORRECT_INIT_DATE']+job_dict['init_hr_start'],
        '%Y%m%d%H'
    )
    verif_case_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE']+'_'+job_dict['STEP']
    )
    model = job_dict['MODEL']
    members = job_dict['members']
    fhr_list = []
    fhr_check_input_dict = {}
    fhr_check_output_dict = {}
    for fhr in [int(i) for i in job_dict['CORRECT_LEAD_SEQ'].split(',')]:
        fhr_check_input_dict[str(fhr)] = {}
        fhr_check_output_dict[str(fhr)] = {}
        valid_date_dt = init_date_dt + datetime.timedelta(hours=fhr)
        if job_dict['JOB_GROUP'] == 'reformat_data':
            if job_dict['VERIF_CASE'] in ['grid2grid', 'grid2obs']:
                if job_dict['VERIF_TYPE'] in ['temp', 'prepbufr',
                                              'pres_lvls'] \
                      and job_dict['job_name'] in ['TempAnom2m',
                                                   'GenEnsProd',
                                                   'GeoHeightAnom']:
                    mb = str(members).zfill(2)
                    if job_dict['VERIF_TYPE'] == 'pres_lvls' \
                          and job_dict['MODEL'] == 'cfs':
                        input_file_format = os.path.join(verif_case_dir,
                                                         'data',
                                                         model,
                                                         model+'.pgbf.ens'+mb
                                                         +'.{init?fmt=%Y%m%d%H}.'
                                                         +'f{lead?fmt=%3H}')
                    else:
                        input_file_format = os.path.join(verif_case_dir, 
                                                         'data',
                                                         model,
                                                         model+'.ens'+mb
                                                         +'.{init?fmt=%Y%m%d%H}.'
                                                         +'f{lead?fmt=%3H}')
                    if job_dict['VERIF_CASE'] == 'grid2grid':
                        output_DATA_file_format = os.path.join(
                            verif_case_dir, 'METplus_output',
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                            +job_dict['job_name']+'_{lead?fmt=%2H}'
                            '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
                        )
                        output_COMOUT_file_format = os.path.join(
                            job_dict['COMOUT'],
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                            +job_dict['job_name']+'_{lead?fmt=%2H}'
                            '0000L_{valid?fmt=%Y%m%d_%H%M%S}V_pairs.nc'
                        )
                    if job_dict['VERIF_CASE'] == 'grid2obs':
                        output_DATA_file_format = os.path.join(
                            verif_case_dir, 'METplus_output',
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'gen_ens_prod_'+job_dict['VERIF_TYPE']+'_'
                            +'GenEnsProd_FHR{lead?fmt=%3H}'
                            +'_{valid?fmt=%Y%m%d}'
                            +'_{valid?fmt=%H}0000V_ens.nc'
                        )
                        output_COMOUT_file_format = os.path.join(
                            job_dict['COMOUT'],
                            job_dict['RUN']+'.'+job_dict['DATE'],
                            job_dict['MODEL'], job_dict['VERIF_CASE'],
                            'gen_ens_prod_'+job_dict['VERIF_TYPE']+'_'
                            +'GenEnsProd_FHR{lead?fmt=%3H}'
                            +'_{valid?fmt=%Y%m%d}'
                            +'_{valid?fmt=%H}0000V_ens.nc'
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
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] == 'temp':
                    truth_file_format = os.path.join(
                        verif_case_dir, 'data', 'ecmwf',
                        'ecmwf.{valid?fmt=%Y%m%d%H}.anl'
                    )
                elif job_dict['VERIF_TYPE'] == 'pres_lvls':
                    truth_file_format = os.path.join(
                        verif_case_dir, 'data', 'gfs',
                        'gfs.{valid?fmt=%Y%m%d%H}.anl'
                    )
        elif job_dict['JOB_GROUP'] == 'assemble_data':
            if job_dict['VERIF_CASE'] == 'grid2obs':
                if job_dict['VERIF_TYPE'] == 'prepbufr' \
                      and job_dict['job_name'] == 'TempAnom2m':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'gen_ens_prod_'
                                                     +job_dict['VERIF_TYPE']
                                                     +'_GenEnsProd'
                                                     +'_FHR{lead?fmt=%3H}'
                                                     +'_{valid?fmt=%Y%m%d}'
                                                     +'_{valid?fmt=%H}0000V'
                                                     +'_ens.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        job_dict['MODEL'], job_dict['VERIF_CASE'],
                        'point_stat_'+job_dict['VERIF_TYPE']+'_'
                        +job_dict['job_name']+'_{lead?fmt=%2H}'
                        '0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        job_dict['MODEL'], job_dict['VERIF_CASE'],
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
            if job_dict['JOB_GROUP'] == 'reformat_data' \
                    and job_dict['job_name'] in ['TempAnom2m',
                                                 'GeoHeightAnom']:
                truth_file = format_filler(
                    truth_file_format,
                    fhr_check_input_dict[fhr_key][fhr_fileN_key]['valid_date'],
                    fhr_check_input_dict[fhr_key][fhr_fileN_key]['valid_date'],
                    ['anl'],
                    {}
                )
                if os.path.exists(fhr_fileN) \
                        and os.path.exists(truth_file):
                    fhr_key_input_files_exist_list.append(True)
                    fhr_list.append(
                        fhr_check_input_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
                else:
                    fhr_key_input_files_exist_list.append(False)
            elif job_dict['JOB_GROUP'] == 'reformat_data' \
                    and job_dict['job_name'] == 'GenEnsProd':
                if os.path.exists(fhr_fileN):
                    fhr_key_input_files_exist_list.append(True)
                    fhr_list.append(
                        fhr_check_input_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
                else:
                    fhr_key_input_files_exist_list.append(False)
            elif job_dict['JOB_GROUP'] == 'assemble_data' \
                    and job_dict['job_name'] == 'TempAnom2m':
                if os.path.exists(fhr_fileN):
                    fhr_key_input_files_exist_list.append(True)
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
                # Copy restart files from COMOUT to DATA dir
                # to be used in restart and remove from fhr_list
                copy_file(fhr_fileN_COMOUT,fhr_fileN_DATA)
                print("COMOUT restart file "+fhr_fileN_COMOUT+" exists"
                      +" and will be used in stats restart")
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
    if len(input_fhr_list) >= 23:
        model_files_exist = True
    else:
        model_files_exist = False
    if len(fhr_list) == 0:
        model_files_exist = False
    return model_files_exist, fhr_list, model_copy_output_DATA2COMOUT_list


def check_model_files(job_dict):
    """! Check if model files exist

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             model_files_exist - if non-zero number of  model files
                                 exist or not (boolean)
             fhr_list          - list of forecast hours that model
                                 files exist for (string)
             model_copy_output_DATA2COMOUT_list - list of files to copy from
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
    members = job_dict['members']
    fhr_min = int(job_dict['fhr_start'])
    fhr_max = int(job_dict['fhr_end'])
    fhr_inc = 24
    fhr = fhr_min
    fhr_list = []
    fhr_check_input_dict = {}
    fhr_check_output_dict = {}
    while fhr <= fhr_max:
        fhr_check_input_dict[str(fhr)] = {}
        fhr_check_output_dict[str(fhr)] = {}
        init_date_dt = valid_date_dt - datetime.timedelta(hours=fhr)
        if job_dict['JOB_GROUP'] == 'reformat_data':
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] in ['seaice', 'sst'] \
                      and job_dict['job_name'] in ['Concentration',
                                                   'SST']:
                    mb = str(members).zfill(2)
                    model_file_format = os.path.join(verif_case_dir, 'data',
                                                     model,
                                                     model+'.ens'+mb
                                                     +'.{init?fmt=%Y%m%d%H}.'
                                                     +'f{lead?fmt=%3H}')
                    nf = 0
                    while nf <= 2:
                        if fhr-(12*nf) >= 0:
                            fhr_check_dict[str(fhr)]['file'+str(nf+1)] = {
                                'valid_date': (valid_date_dt
                                               -datetime.timedelta(hours=12*nf)),
                                'init_date': init_date_dt,
                                'forecast_hour': str(fhr-(12*nf))
                            }
                            nf+=1
                else:
                    fhr_check_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
        elif job_dict['JOB_GROUP'] == 'assemble_data':
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] in ['pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['WeeklyAvg_GeoHeightAnom',
                                                     'WeeklyAvg_TempAnom2m']:
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'anomaly_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('WeeklyAvg_', '')
                                                     +'_init'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'fhr{lead?fmt=%3H}.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weekly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weekly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] in ['pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['Days6_10Avg_GeoHeightAnom',
                                                     'Days6_10Avg_TempAnom2m']:
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'anomaly_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('Days6_10Avg_',
                                                              '')
                                                     +'_init'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'fhr{lead?fmt=%3H}.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'days6_10_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-120}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'days6_10_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-120}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] in ['pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['Weeks3_4Avg_GeoHeightAnom',
                                                     'Weeks3_4Avg_TempAnom2m']:
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'anomaly_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('Weeks3_4Avg_',
                                                              '')
                                                     +'_init'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'fhr{lead?fmt=%3H}.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weeks3_4_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-336}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weeks3_4_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-336}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'sst' \
                        and job_dict['job_name'] == 'DailyAvg_SST':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'grid_stat_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('DailyAvg_', 
                                                              '')
                                                     +'_{lead?fmt=%2H}0000L_'
                                                     +'{valid?fmt=%Y%m%d}_'
                                                     +'{valid?fmt=%H}0000V_'
                                                     +'pairs.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'daily_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-24}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'daily_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-24}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] in ['seaice', 'sst'] \
                        and job_dict['job_name'] in ['WeeklyAvg_Concentration',
                                                     'WeeklyAvg_SST']:
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'grid_stat_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('WeeklyAvg_', 
                                                              '')
                                                     +'_{lead?fmt=%2H}0000L_'
                                                     +'{valid?fmt=%Y%m%d}_'
                                                     +'{valid?fmt=%H}0000V_'
                                                     +'pairs.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weekly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weekly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] in ['seaice', 'sst'] \
                        and job_dict['job_name'] in ['MonthlyAvg_Concentration',
                                                     'MonthlyAvg_SST']:
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'grid_stat_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('MonthlyAvg_', 
                                                              '')
                                                     +'_{lead?fmt=%2H}0000L_'
                                                     +'{valid?fmt=%Y%m%d}_'
                                                     +'{valid?fmt=%H}0000V_'
                                                     +'pairs.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'monthly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-720}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'monthly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-720}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'pres_lvls' \
                        and job_dict['job_name'] == 'WeeklyAvg_GeoHeight':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'grid_stat_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +'GeoHeightAnom'
                                                     +'_{lead?fmt=%2H}0000L_'
                                                     +'{valid?fmt=%Y%m%d}_'
                                                     +'{valid?fmt=%H}0000V_'
                                                     +'pairs.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weekly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weekly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'temp' \
                        and job_dict['job_name'] == 'WeeklyAvg_Temp2m':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'grid_stat_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +'TempAnom2m'
                                                     +'_{lead?fmt=%2H}0000L_'
                                                     +'{valid?fmt=%Y%m%d}_'
                                                     +'{valid?fmt=%H}0000V_'
                                                     +'pairs.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weekly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weekly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'pres_lvls' \
                        and job_dict['job_name'] == 'Days6_10Avg_GeoHeight':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'grid_stat_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +'GeoHeightAnom'
                                                     +'_{lead?fmt=%2H}0000L_'
                                                     +'{valid?fmt=%Y%m%d}_'
                                                     +'{valid?fmt=%H}0000V_'
                                                     +'pairs.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'days6_10_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-120}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'days6_10_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-120}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'temp' \
                        and job_dict['job_name'] == 'Days6_10Avg_Temp2m':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'grid_stat_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +'TempAnom2m'
                                                     +'_{lead?fmt=%2H}0000L_'
                                                     +'{valid?fmt=%Y%m%d}_'
                                                     +'{valid?fmt=%H}0000V_'
                                                     +'pairs.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'days6_10_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-120}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'days6_10_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-120}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'pres_lvls' \
                        and job_dict['job_name'] == 'Weeks3_4Avg_GeoHeight':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'grid_stat_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +'GeoHeightAnom'
                                                     +'_{lead?fmt=%2H}0000L_'
                                                     +'{valid?fmt=%Y%m%d}_'
                                                     +'{valid?fmt=%H}0000V_'
                                                     +'pairs.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weeks3_4_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-336}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weeks3_4_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-336}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'temp' \
                        and job_dict['job_name'] == 'Weeks3_4Avg_Temp2m':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'grid_stat_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +'TempAnom2m'
                                                     +'_{lead?fmt=%2H}0000L_'
                                                     +'{valid?fmt=%Y%m%d}_'
                                                     +'{valid?fmt=%H}0000V_'
                                                     +'pairs.nc')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weeks3_4_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-336}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weeks3_4_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-336}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                else:
                    input_file_format = os.path.join(verif_case_dir, 'data',
                                                     model, model
                                                     +'.{init?fmt=%Y%m%d%H}.'
                                                     +'f{lead?fmt=%3H}')
                if job_dict['VERIF_TYPE'] == 'sst' \
                        and job_dict['job_name'] == 'DailyAvg_SST':
                    nf = 0
                    while nf <= 2:
                        if fhr-(12*nf) >= 0:
                            fhr_check_input_dict[str(fhr)]['file'+str(nf+1)] = {
                                'valid_date': (valid_date_dt
                                               -datetime.timedelta(hours=12*nf)),
                                'init_date': init_date_dt,
                                'forecast_hour': str(fhr-(12*nf))
                            }
                            nf+=1
                    fhr_check_output_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
                elif job_dict['VERIF_TYPE'] in ['seaice', 'sst', 
                                                'pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['WeeklyAvg_Concentration',
                                                     'WeeklyAvg_SST',
                                                     'WeeklyAvg_GeoHeightAnom',
                                                     'WeeklyAvg_GeoHeight',
                                                     'WeeklyAvg_TempAnom2m',
                                                     'WeeklyAvg_Temp2m']:
                    if str(fhr) in ['168', '336', '504', '672', '840']:
                        nf = 0
                        while nf <= 14:
                            fhr_check_input_dict[str(fhr)]['file'+str(nf+1)] = {
                                'valid_date': (valid_date_dt
                                               -datetime.timedelta(hours=12*nf)),
                                'init_date': init_date_dt,
                                'forecast_hour': str(fhr-(12*nf))
                            }
                            nf+=1
                        fhr_check_output_dict[str(fhr)]['file1'] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr)
                        }
                elif job_dict['VERIF_TYPE'] in ['seaice', 'sst'] \
                        and job_dict['job_name'] in ['MonthlyAvg_Concentration',
                                                     'MonthlyAvg_SST']:
                    if fhr == 720:
                        nf = 0
                        while nf <= 60:
                            fhr_check_input_dict[str(fhr)]['file'+str(nf+1)] = {
                                'valid_date': (valid_date_dt
                                               -datetime.timedelta(hours=12*nf)),
                                'init_date': init_date_dt,
                                'forecast_hour': str(fhr-(12*nf))
                            }
                            nf+=1
                        fhr_check_output_dict[str(fhr)]['file1'] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr)
                        }
                elif job_dict['VERIF_TYPE'] in ['pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['Days6_10Avg_GeoHeightAnom',
                                                     'Days6_10Avg_GeoHeight',
                                                     'Days6_10Avg_TempAnom2m',
                                                     'Days6_10Avg_Temp2m']:
                    if fhr == 240:
                        nf = 0
                        while nf <= 10:
                            fhr_check_input_dict[str(fhr)]['file'+str(nf+1)] = {
                                'valid_date': (valid_date_dt
                                               -datetime.timedelta(hours=12*nf)),
                                'init_date': init_date_dt,
                                'forecast_hour': str(fhr-(12*nf))
                            }
                            nf+=1
                        fhr_check_output_dict[str(fhr)]['file1'] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr)
                        }
                elif job_dict['VERIF_TYPE'] in ['pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['Weeks3_4Avg_GeoHeightAnom',
                                                     'Weeks3_4Avg_GeoHeight',
                                                     'Weeks3_4Avg_TempAnom2m',
                                                     'Weeks3_4Avg_Temp2m']:
                    if fhr == 672:
                        nf = 0
                        while nf <= 28:
                            fhr_check_input_dict[str(fhr)]['file'+str(nf+1)] = {
                                'valid_date': (valid_date_dt
                                               -datetime.timedelta(hours=12*nf)),
                                'init_date': init_date_dt,
                                'forecast_hour': str(fhr-(12*nf))
                            }
                            nf+=1
                        fhr_check_output_dict[str(fhr)]['file1'] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr)
                        }
                else:
                    fhr_check_output_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
        elif job_dict['JOB_GROUP'] == 'generate_stats':
            if job_dict['VERIF_CASE'] == 'grid2grid':
                output_DATA_file_format = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+job_dict['DATE'],
                    model, job_dict['VERIF_CASE'],
                    'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                    +job_dict['job_name']+'_{lead?fmt=%2H}'
                    '0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
                )
                output_COMOUT_file_format = os.path.join(
                    job_dict['COMOUT'],
                    job_dict['RUN']+'.'+job_dict['DATE'],
                    model, job_dict['VERIF_CASE'],
                    'grid_stat_'+job_dict['VERIF_TYPE']+'_'
                    +job_dict['job_name']+'_{lead?fmt=%2H}'
                    '0000L_{valid?fmt=%Y%m%d_%H%M%S}V.stat'
                )
                if job_dict['VERIF_TYPE'] in ['sst', 'seaice',
                                              'pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['WeeklyAvg_SST',
                                                     'WeeklyAvg_Concentration',
                                                     'WeeklyAvg_GeoHeightAnom',
                                                     'WeeklyAvg_GeoHeight',
                                                     'WeeklyAvg_TempAnom2m',
                                                     'WeeklyAvg_Temp2m']:
                    input_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weekly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] in ['pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['Days6_10Avg_GeoHeightAnom',
                                                     'Days6_10Avg_GeoHeight',
                                                     'Days6_10Avg_TempAnom2m',
                                                     'Days6_10Avg_Temp2m']:
                    input_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'days6_10_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-120}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] in ['pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['Weeks3_4Avg_GeoHeightAnom',
                                                     'Weeks3_4Avg_GeoHeight',
                                                     'Weeks3_4Avg_TempAnom2m',
                                                     'Weeks3_4Avg_Temp2m']:
                    input_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'weeks3_4_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-336}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                #elif job_dict['VERIF_TYPE'] in ['sst', 'seaice'] \
                        #and job_dict['job_name'] in ['WeeklyAvg_SST',
                                                     #'WeeklyAvg_Concentration']:
                    #input_file_format = os.path.join(
                        #verif_case_dir, 'METplus_output',
                        #job_dict['RUN']+'.'+job_dict['DATE'],
                        #model, job_dict['VERIF_CASE'], 'weekly_avg_'
                        #+job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        #+'_init{init?fmt=%Y%m%d%H}_'
                        #+'valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        #+'to{valid?fmt=%Y%m%d%H}.nc'
                    #)
                elif job_dict['VERIF_TYPE'] in ['sst', 'seaice'] \
                        and job_dict['job_name'] in ['MonthlyAvg_SST',
                                                     'MonthlyAvg_Concentration']:
                    input_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'], 'monthly_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-720}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'sst' \
                        and job_dict['job_name'] == 'DailyAvg_SST':
                    input_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
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
                if job_dict['VERIF_TYPE'] == 'sst' \
                      and job_dict['job_name'] == 'DailyAvg_SST':
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
                elif job_dict['VERIF_TYPE'] in ['seaice', 'sst',
                                                'pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['WeeklyAvg_Concentration',
                                                     'WeeklyAvg_SST',
                                                     'WeeklyAvg_GeoHeightAnom',
                                                     'WeeklyAvg_GeoHeight',
                                                     'WeeklyAvg_TempAnom2m',
                                                     'WeeklyAvg_Temp2m']:
                    if str(fhr) in ['168', '336', '504', '672', '840']:
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
                elif job_dict['VERIF_TYPE'] in ['seaice', 'sst'] \
                        and job_dict['job_name'] in ['MonthlyAvg_Concentration',
                                                     'MonthlyAvg_SST']:
                    if fhr == 720:
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
                elif job_dict['VERIF_TYPE'] in ['pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['Days6_10Avg_GeoHeightAnom',
                                                     'Days6_10Avg_GeoHeight',
                                                     'Days6_10Avg_TempAnom2m',
                                                     'Days6_10Avg_Temp2m']:
                    if fhr == 240:
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
                elif job_dict['VERIF_TYPE'] in ['pres_lvls', 'temp'] \
                        and job_dict['job_name'] in ['Weeks3_4Avg_GeoHeightAnom',
                                                     'Weeks3_4Avg_GeoHeight',
                                                     'Weeks3_4Avg_TempAnom2m',
                                                     'Weeks3_4Avg_Temp2m']:
                    if fhr == 672:
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
                if job_dict['VERIF_TYPE'] == 'prepbufr' \
                        and job_dict['job_name'] == 'WeeklyAvg_TempAnom2m':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'anomaly_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('WeeklyAvg_', '')
                                                     +'_init'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'fhr{lead?fmt=%3H}.stat')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'],
                        'stat_analysis_fcst'+job_dict['MODEL']+'_obsprepbufr_'
                        +job_dict['prepbufr']+'_'+job_dict['job_name']
                        +'_SL1L2_valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        +'to{valid?fmt=%Y%m%d%H}.stat'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'],
                        'stat_analysis_fcst'+job_dict['MODEL']+'_obsprepbufr_'
                        +job_dict['prepbufr']+'_'+job_dict['job_name']
                        +'_SL1L2_valid{valid_shift?fmt=%Y%m%d%H?shift=-168}'
                        +'to{valid?fmt=%Y%m%d%H}.stat'
                    )
                elif job_dict['VERIF_TYPE'] == 'prepbufr' \
                        and job_dict['job_name'] == 'Days6_10Avg_TempAnom2m':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'anomaly_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('Days6_10Avg_',
                                                              '')
                                                     +'_init'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'fhr{lead?fmt=%3H}.stat')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'],
                        'stat_analysis_fcst'+job_dict['MODEL']+'_obsprepbufr_'
                        +job_dict['prepbufr']+'_'+job_dict['job_name']
                        +'_SL1L2_valid{valid_shift?fmt=%Y%m%d%H?shift=-120}'
                        +'to{valid?fmt=%Y%m%d%H}.stat'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'],
                        'stat_analysis_fcst'+job_dict['MODEL']+'_obsprepbufr_'
                        +job_dict['prepbufr']+'_'+job_dict['job_name']
                        +'_SL1L2_valid{valid_shift?fmt=%Y%m%d%H?shift=-120}'
                        +'to{valid?fmt=%Y%m%d%H}.stat'
                    )
                elif job_dict['VERIF_TYPE'] == 'prepbufr' \
                        and job_dict['job_name'] == 'Weeks3_4Avg_TempAnom2m':
                    input_file_format = os.path.join(verif_case_dir,
                                                     'METplus_output',
                                                     job_dict['RUN']+'.'
                                                     +job_dict['DATE'],
                                                     job_dict['MODEL'],
                                                     job_dict['VERIF_CASE'],
                                                     'anomaly_'
                                                     +job_dict['VERIF_TYPE']+'_'
                                                     +job_dict['job_name']\
                                                     .replace('Weeks3_4Avg_', 
                                                              '')
                                                     +'_init'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'fhr{lead?fmt=%3H}.stat')
                    output_DATA_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'],
                        'stat_analysis_fcst'+job_dict['MODEL']+'_obsprepbufr_'
                        +job_dict['prepbufr']+'_'+job_dict['job_name']
                        +'_SL1L2_valid{valid_shift?fmt=%Y%m%d%H?shift=-336}'
                        +'to{valid?fmt=%Y%m%d%H}.stat'
                    )
                    output_COMOUT_file_format = os.path.join(
                        job_dict['COMOUT'],
                        job_dict['RUN']+'.'+job_dict['DATE'],
                        model, job_dict['VERIF_CASE'],
                        'stat_analysis_fcst'+job_dict['MODEL']+'_obsprepbufr_'
                        +job_dict['prepbufr']+'_'+job_dict['job_name']
                        +'_SL1L2_valid{valid_shift?fmt=%Y%m%d%H?shift=-336}'
                        +'to{valid?fmt=%Y%m%d%H}.stat'
                    )
                else:
                    input_file_format = os.path.join(
                        verif_case_dir, 'data', model,
                        model+'.{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}'
                    )
                if job_dict['VERIF_TYPE'] == 'prepbufr' \
                        and job_dict['job_name'] == 'WeeklyAvg_TempAnom2m':
                    if str(fhr) in ['168', '336', '504', '672', '840']:
                        nf = 0
                        while nf <= 14:
                            fhr_check_input_dict[str(fhr)]['file'+str(nf+1)] = {
                                'valid_date': (valid_date_dt
                                               -datetime.timedelta(hours=12*nf)),
                                'init_date': init_date_dt,
                                'forecast_hour': str(fhr-(12*nf))
                            }
                            nf+=1
                        fhr_check_output_dict[str(fhr)]['file1'] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr)
                        }
                elif job_dict['VERIF_TYPE'] == 'prepbufr' \
                        and job_dict['job_name'] == 'Days6_10Avg_TempAnom2m':
                    if fhr == 240:
                        nf = 0
                        while nf <= 10:
                            fhr_check_input_dict[str(fhr)]['file'+str(nf+1)] = {
                                'valid_date': (valid_date_dt
                                               -datetime.timedelta(hours=12*nf)),
                                'init_date': init_date_dt,
                                'forecast_hour': str(fhr-(12*nf))
                            }
                            nf+=1
                        fhr_check_output_dict[str(fhr)]['file1'] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr)
                        }
                elif job_dict['VERIF_TYPE'] == 'prepbufr' \
                        and job_dict['job_name'] == 'Weeks3_4Avg_TempAnom2m':
                    if fhr == 672:
                        nf = 0
                        while nf <= 28:
                            fhr_check_input_dict[str(fhr)]['file'+str(nf+1)] = {
                                'valid_date': (valid_date_dt
                                               -datetime.timedelta(hours=12*nf)),
                                'init_date': init_date_dt,
                                'forecast_hour': str(fhr-(12*nf))
                            }
                            nf+=1
                        fhr_check_output_dict[str(fhr)]['file1'] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr)
                        }
        fhr+=fhr_inc
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
                                                     'Concentration',
                                                     'SST']:
                    fhr_list.append(
                        fhr_check_input_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
                elif job_dict['JOB_GROUP'] == 'assemble_data' \
                        and job_dict['job_name'] in ['TempAnom2m',
                                                     'Temp2m',
                                                     'GeoHeightAnom',
                                                     'GeoHeight']:
                    fhr_list.append(
                        fhr_check_input_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
                elif job_dict['JOB_GROUP'] == 'generate_stats':
                    fhr_list.append(
                        fhr_check_input_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
            else:
                fhr_key_input_files_exist_list.append(False)
        if any(x == True for x in fhr_key_input_files_exist_list) \
                and fhr_key_input_files_exist_list.count(True) > 0:
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
                # Copy restart files from COMOUT to DATA dir
                copy_file(fhr_fileN_COMOUT,fhr_fileN_DATA)
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
    return model_files_exist, fhr_list, model_copy_output_DATA2COMOUT_list

def check_weekly_truth_files(job_dict):
    """! Check if obs files exist for weekly reformat and assemble step

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             truth_files_exist - if 80% of truth files
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
            if job_dict['VERIF_TYPE'] == 'temp':
                truth_file_format = os.path.join(
                    verif_case_dir, 'data', 'ecmwf',
                    'ecmwf.{valid?fmt=%Y%m%d%H}.anl'
                )
                nf = 0
                while nf <= 14:
                    truth_file = format_filler(
                        truth_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(truth_file)
                    nf+=1
            elif job_dict['VERIF_TYPE'] == 'pres_lvls':
                truth_file_format = os.path.join(
                    verif_case_dir, 'data', 'gfs',
                    'gfs.{valid?fmt=%Y%m%d%H}.anl'
                )
                nf = 0
                while nf <= 14:
                    truth_file = format_filler(
                        truth_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(truth_file)
                    nf+=1
        elif job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] == 'prepbufr':
                prepbufr_file_format = os.path.join(
                    verif_case_dir, 'data', 'prepbufr_nam',
                    'prepbufr.nam.'
                    +'{valid?fmt=%Y%m%d%H}'
                )
                nf = 0
                while nf <= 14:
                    prepbufr_file = format_filler(
                        prepbufr_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(prepbufr_file)
                    nf+=1
                pb2nc_DATA_output_file_format = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_nam_valid'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                pb2nc_COMOUT_output_file_format = os.path.join(
                    job_dict['COMOUT'],
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_nam_valid'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                nf = 0
                while nf <= 14:
                    pb2nc_DATA_output = format_filler(
                        pb2nc_DATA_output_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    pb2nc_COMOUT_output = format_filler(
                        pb2nc_COMOUT_output_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_output_file_list.append((pb2nc_DATA_output,
                                                   pb2nc_COMOUT_output))
                    nf+=1
    elif job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] == 'prepbufr' \
                    and job_dict['job_name'] == 'TempAnom2m':
                pb2nc_file_format = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                nf = 0
                while nf <= 14:
                    pb2nc_file = format_filler(
                        pb2nc_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(pb2nc_file)
                    nf+=1
    truth_output_files_exist_list = []
    truth_copy_output_DATA2COMOUT_list = truth_output_file_list
    for truth_file_tuple in truth_output_file_list:
        if os.path.exists(truth_file_tuple[1]):
            truth_output_files_exist_list.append(True)
            truth_copy_output_DATA2COMOUT_list.remove(truth_file_tuple)
        else:
            truth_output_files_exist_list.append(False)
    if all(x == True for x in truth_output_files_exist_list) \
            and len(truth_output_files_exist_list) > 0:
        truth_files_exist = True
    else:
        truth_input_files_exist_list = []
        for truth_file in truth_input_file_list:
            if os.path.exists(truth_file):
                truth_input_files_exist_list.append(True)
            else:
                truth_input_files_exist_list.append(False)
        if any(x == True for x in truth_input_files_exist_list) \
                and truth_input_files_exist_list.count(True) >= 12:
            truth_files_exist = True
        else:
            truth_files_exist = False
    return truth_files_exist, truth_copy_output_DATA2COMOUT_list

def check_days6_10_truth_files(job_dict):
    """! Check if obs files exist for Days 6-10 reformat and assemble step

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             truth_files_exist - if 80% of truth files
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
            if job_dict['VERIF_TYPE'] == 'temp':
                truth_file_format = os.path.join(
                    verif_case_dir, 'data', 'ecmwf',
                    'ecmwf.{valid?fmt=%Y%m%d%H}.anl'
                )
                nf = 0
                while nf <= 10:
                    truth_file = format_filler(
                        truth_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(truth_file)
                    nf+=1
            elif job_dict['VERIF_TYPE'] == 'pres_lvls':
                truth_file_format = os.path.join(
                    verif_case_dir, 'data', 'gfs',
                    'gfs.{valid?fmt=%Y%m%d%H}.anl'
                )
                nf = 0
                while nf <= 10:
                    truth_file = format_filler(
                        truth_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(truth_file)
                    nf+=1
        elif job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] == 'prepbufr':
                prepbufr_file_format = os.path.join(
                    verif_case_dir, 'data', 'prepbufr_nam',
                    'prepbufr.nam.'
                    +'{valid?fmt=%Y%m%d%H}'
                )
                nf = 0
                while nf <= 10:
                    prepbufr_file = format_filler(
                        prepbufr_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(prepbufr_file)
                    nf+=1
                pb2nc_DATA_output_file_format = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_nam_valid'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                pb2nc_COMOUT_output_file_format = os.path.join(
                    job_dict['COMOUT'],
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_nam_valid'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                nf = 0
                while nf <= 10:
                    pb2nc_DATA_output = format_filler(
                        pb2nc_DATA_output_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    pb2nc_COMOUT_output = format_filler(
                        pb2nc_COMOUT_output_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_output_file_list.append((pb2nc_DATA_output,
                                                   pb2nc_COMOUT_output))
                    nf+=1
    elif job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] == 'prepbufr' \
                    and job_dict['job_name'] == 'TempAnom2m':
                pb2nc_file_format = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                nf = 0
                while nf <= 10:
                    pb2nc_file = format_filler(
                        pb2nc_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(pb2nc_file)
                    nf+=1
    truth_output_files_exist_list = []
    truth_copy_output_DATA2COMOUT_list = truth_output_file_list
    for truth_file_tuple in truth_output_file_list:
        if os.path.exists(truth_file_tuple[1]):
            truth_output_files_exist_list.append(True)
            truth_copy_output_DATA2COMOUT_list.remove(truth_file_tuple)
        else:
            truth_output_files_exist_list.append(False)
    if all(x == True for x in truth_output_files_exist_list) \
            and len(truth_output_files_exist_list) > 0:
        truth_files_exist = True
    else:
        truth_input_files_exist_list = []
        for truth_file in truth_input_file_list:
            if os.path.exists(truth_file):
                truth_input_files_exist_list.append(True)
            else:
                truth_input_files_exist_list.append(False)
        if any(x == True for x in truth_input_files_exist_list) \
                and truth_input_files_exist_list.count(True) >= 9:
            truth_files_exist = True
        else:
            truth_files_exist = False
    return truth_files_exist, truth_copy_output_DATA2COMOUT_list

def check_weeks3_4_truth_files(job_dict):
    """! Check if obs files exist for Weeks 3-4 reformat and assemble step

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             truth_files_exist - if 80% of truth files
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
            if job_dict['VERIF_TYPE'] == 'temp':
                truth_file_format = os.path.join(
                    verif_case_dir, 'data', 'ecmwf',
                    'ecmwf.{valid?fmt=%Y%m%d%H}.anl'
                )
                nf = 0
                while nf <= 28:
                    truth_file = format_filler(
                        truth_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(truth_file)
                    nf+=1
            elif job_dict['VERIF_TYPE'] == 'pres_lvls':
                truth_file_format = os.path.join(
                    verif_case_dir, 'data', 'gfs',
                    'gfs.{valid?fmt=%Y%m%d%H}.anl'
                )
                nf = 0
                while nf <= 28:
                    truth_file = format_filler(
                        truth_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(truth_file)
                    nf+=1
        elif job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] == 'prepbufr' \
                    and 'Prepbufr' in job_dict['job_name']:
                prepbufr_name = (job_dict['job_name'].replace('Prepbufr', '')\
                                 .lower())
                prepbufr_file_format = os.path.join(
                    verif_case_dir, 'data', 'prepbufr_'+prepbufr_name,
                    'prepbufr.'+prepbufr_name+'.'
                    +'{valid?fmt=%Y%m%d%H}'
                )
                nf = 0
                while nf <= 28:
                    prepbufr_file = format_filler(
                        prepbufr_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(prepbufr_file)
                    nf+=1
                pb2nc_DATA_output_file_format = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                pb2nc_COMOUT_output_file_format = os.path.join(
                    job_dict['COMOUT'],
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                nf = 0
                while nf <= 28:
                    pb2nc_DATA_output = format_filler(
                        pb2nc_DATA_output_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    pb2nc_COMOUT_output = format_filler(
                        pb2nc_COMOUT_output_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_output_file_list.append((pb2nc_DATA_output,
                                                   pb2nc_COMOUT_output))
                    nf+=1
    elif job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] == 'prepbufr' \
                    and job_dict['job_name'] == 'TempAnom2m':
                pb2nc_file_format = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                nf = 0
                while nf <= 28:
                    pb2nc_file = format_filler(
                        pb2nc_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_input_file_list.append(pb2nc_file)
                    nf+=1
    truth_output_files_exist_list = []
    truth_copy_output_DATA2COMOUT_list = truth_output_file_list
    for truth_file_tuple in truth_output_file_list:
        if os.path.exists(truth_file_tuple[1]):
            truth_output_files_exist_list.append(True)
            # Copy restart files from COMOUT to DATA dir
            copy_file(truth_file_tuple[1], truth_file_tuple[0])
            truth_copy_output_DATA2COMOUT_list.remove(truth_file_tuple)
        else:
            truth_output_files_exist_list.append(False)
    if all(x == True for x in truth_output_files_exist_list) \
            and len(truth_output_files_exist_list) > 0:
        truth_files_exist = True
    else:
        truth_input_files_exist_list = []
        for truth_file in truth_input_file_list:
            if os.path.exists(truth_file):
                truth_input_files_exist_list.append(True)
            else:
                truth_input_files_exist_list.append(False)
        if job_dict['JOB_GROUP'] == 'reformat_data' \
                and job_dict['VERIF_CASE'] == 'grid2obs':
            if all(x == True for x in truth_input_files_exist_list) \
                    and len(truth_input_files_exist_list) > 0:
                truth_files_exist = True
            else:
                truth_files_exist = False
        else:
            if any(x == True for x in truth_input_files_exist_list) \
                    and truth_input_files_exist_list.count(True) >= 23:
                truth_files_exist = True
            else:
                truth_files_exist = False
    return truth_files_exist, truth_copy_output_DATA2COMOUT_list

def check_truth_files(job_dict):
    """!
         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             all_truth_file_exist - if all needed truth files
                                    exist or not (boolean)
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hr_start'],
        '%Y%m%d%H'
    )
    verif_case_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE']+'_'+job_dict['STEP']
    )
    truth_file_list = []
    if job_dict['JOB_GROUP'] == 'reformat_data':
        if job_dict['VERIF_CASE'] == 'grid2grid':
            if job_dict['VERIF_TYPE'] == 'temp':
                truth_file_format = os.path.join(
                    verif_case_dir, 'data', 'ecmwf',
                    'ecmwf.{valid?fmt=%Y%m%d%H}.anl'
                )
                nf = 0
                while nf <= 28:
                    truth_file = format_filler(
                        truth_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_file_list.append(truth_file)
                    nf+=1
            elif job_dict['VERIF_TYPE'] == 'pres_lvls':
                truth_file_format = os.path.join(
                    verif_case_dir, 'data', 'gfs',
                    'gfs.{valid?fmt=%Y%m%d%H}.anl'
                )
                nf = 0
                while nf <= 28:
                    truth_file = format_filler(
                        truth_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_file_list.append(truth_file)
                    nf+=1
        elif job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] == 'prepbufr' \
                    and 'Prepbufr' in job_dict['job_name']:
                prepbufr_name = (job_dict['job_name'].replace('Prepbufr', '')\
                                 .lower())
                prepbufr_file_format = os.path.join(
                    verif_case_dir, 'data', 'prepbufr_'+prepbufr_name,
                    'prepbufr.'+prepbufr_name+'.'
                    +'{valid?fmt=%Y%m%d%H}'
                )
                nf = 0
                while nf <= 28:
                    prepbufr_file = format_filler(
                        prepbufr_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_file_list.append(prepbufr_file)
                    nf+=1
    elif job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] == 'prepbufr' \
                    and job_dict['job_name'] == 'TempAnom2m':
                pb2nc_file_format = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                nf = 0
                while nf <= 28:
                    pb2nc_file = format_filler(
                        pb2nc_file_format,
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        (valid_date_dt-datetime.timedelta(hours=12*nf)),
                        ['anl'], {}
                    )
                    truth_file_list.append(pb2nc_file)
                    nf+=1
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        if job_dict['VERIF_CASE'] == 'grid2grid':
            if job_dict['VERIF_TYPE'] == 'seaice' \
                    and job_dict['job_name'] == 'WeeklyAvg_Concentration':
                osi_saf_file_format = os.path.join(
                    verif_case_dir, 'data', 'osi_saf',
                    'osi_saf.multi.'
                    +'{valid_shift?fmt=%Y%m%d%H?shift=-168}to'
                    +'{valid?fmt=%Y%m%d%H}_G003.nc'
                )
                osi_saf_file = format_filler(
                    osi_saf_file_format,
                    valid_date_dt,
                    valid_date_dt,
                    ['anl'], {}
                )
                truth_file_list.append(osi_saf_file)
            elif job_dict['VERIF_TYPE'] == 'seaice' \
                    and job_dict['job_name'] == 'MonthlyAvg_Concentration':
                osi_saf_file_format = os.path.join(
                    verif_case_dir, 'data', 'osi_saf',
                    'osi_saf.multi.'
                    +'{valid_shift?fmt=%Y%m%d%H?shift=-720}to'
                    +'{valid?fmt=%Y%m%d%H}_G003.nc'
                )
                osi_saf_file = format_filler(
                    osi_saf_file_format,
                    valid_date_dt,
                    valid_date_dt,
                    ['anl'], {}
                )
                truth_file_list.append(osi_saf_file)
            elif job_dict['VERIF_TYPE'] == 'sst' \
                    and job_dict['job_name'] == 'DailyAvg_SST':
                ghrsst_ospo_file_format = os.path.join(
                    verif_case_dir, 'data', 'ghrsst_ospo',
                    'ghrsst_ospo.'
                    +'{valid_shift?fmt=%Y%m%d%H?shift=-24}to'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                ghrsst_ospo_file = format_filler(
                    ghrsst_ospo_file_format,
                    valid_date_dt,
                    valid_date_dt,
                    ['anl'], {}
                )
                truth_file_list.append(ghrsst_ospo_file)
            elif job_dict['VERIF_TYPE'] == 'sst' \
                    and job_dict['job_name'] == 'WeeklyAvg_SST':
                ghrsst_ospo_file_format = os.path.join(
                    verif_case_dir, 'data', 'ghrsst_ospo',
                    'ghrsst_ospo.'
                    +'{valid_shift?fmt=%Y%m%d%H?shift=-168}to'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                ghrsst_ospo_file = format_filler(
                    ghrsst_ospo_file_format,
                    valid_date_dt,
                    valid_date_dt,
                    ['anl'], {}
                )
                truth_file_list.append(ghrsst_ospo_file)
            elif job_dict['VERIF_TYPE'] == 'sst' \
                    and job_dict['job_name'] == 'MonthlyAvg_SST':
                ghrsst_ospo_file_format = os.path.join(
                    verif_case_dir, 'data', 'ghrsst_ospo',
                    'ghrsst_ospo.'
                    +'{valid_shift?fmt=%Y%m%d%H?shift=-720}to'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                ghrsst_ospo_file = format_filler(
                    ghrsst_ospo_file_format,
                    valid_date_dt,
                    valid_date_dt,
                    ['anl'], {}
                )
                truth_file_list.append(ghrsst_ospo_file)
        elif job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] == 'prepbufr':
                pb2nc_file = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                truth_file_list.append(pb2nc_file)
    truth_files_exist_list = []
    for truth_file in truth_file_list:
        if os.path.exists(truth_file):
            truth_files_exist_list.append(True)
        else:
            truth_files_exist_list.append(False)
    if all(x == True for x in truth_files_exist_list) \
            and len(truth_files_exist_list) > 0:
        all_truth_file_exist = True
    else:
        all_truth_file_exist = False
    return all_truth_file_exist

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
        'OSI-SAF': {'valid_hr_start': 00,
                    'valid_hr_end': 00,
                    'valid_hr_inc': 24},
        'GHRSST-OSPO': {'valid_hr_start': 00,
                        'valid_hr_end': 00,
                        'valid_hr_inc': 24},
        'ECMWF': {'valid_hr_start': 00,
                  'valid_hr_end': 00,
                  'valid_hr_inc': 12},
        'GFS': {'valid_hr_start': 00,
                'valid_hr_end': 00,
                'valid_hr_inc': 12},
        'BUFR': {'valid_hr_start': 00,
                 'valid_hr_end': 00,
                 'valid_hr_inc': 12},
    }
    if obs in list(obs_valid_hr_dict.keys()):
        valid_hr_start = obs_valid_hr_dict[obs]['valid_hr_start']
        valid_hr_end = obs_valid_hr_dict[obs]['valid_hr_end']
        valid_hr_inc = obs_valid_hr_dict[obs]['valid_hr_inc']
    else:
        print(f"FATAL ERROR: Cannot get {obs} valid hour information")
        sys.exit(1)
    return valid_hr_start, valid_hr_end, valid_hr_inc

def initialize_prep_job_env_dict(verif_type, group,
                                 job):
    """! This initializes a dictionary of environment variables and their
         values to be set for the job pulling from environment variables
         already set previously
         Args:
             verif_type                  - string of the use case name
             group                       - string of the group name
             job                         - string of job name
         Returns:
             job_env_dict - dictionary of job settings
    """
    job_env_var_list = [
        'machine', 'evs_ver', 'HOMEevs', 'FIXevs', 'USHevs', 'DATA',
        'NET', 'RUN', 'STEP', 'COMPONENT', 'COMINgefs', 'COMOUT',
        'SENDCOM', 'gefs_members'
    ]
    job_env_dict = {}
    for env_var in job_env_var_list:
        job_env_dict[env_var] = os.environ[env_var]
    job_env_dict['JOB_GROUP'] = group
    job_env_dict['fhr_start'] = os.environ['fhr_min']
    job_env_dict['fhr_end'] = os.environ['fhr_max']
    valid_hr_list = (
        os.environ['vhr_list']\
        .split(' ')
    )
    job_env_dict['valid_hr_start'] = (valid_hr_list[0].zfill(2))
    job_env_dict['valid_hr_end'] = (valid_hr_list[-1].zfill(2))
    init_hr_list = (
        os.environ['inithour_list']\
        .split(' ')
    )
    job_env_dict['init_hr_start'] = (init_hr_list[0].zfill(2))
    job_env_dict['init_hr_end'] = (init_hr_list[-1].zfill(2))
    return job_env_dict

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
        'COMOUT', 'members'
    ]
    if group in ['reformat_data', 'assemble_data', 'generate_stats', 'gather_stats']:
        os.environ['MET_TMP_DIR'] = os.path.join(
            os.environ['DATA'],
            os.environ['VERIF_CASE']+'_'+os.environ['STEP'],
            'METplus_output', 'tmp'
        )
        if not os.path.exists(os.environ['MET_TMP_DIR']):
            os.makedirs(os.environ['MET_TMP_DIR'])
        job_env_var_list.extend(
            ['METPLUS_PATH', 'MET_ROOT', 'MET_TMP_DIR',
             'COMROOT']
        )
    elif group in ['condense_stats', 'filter_stats', 'make_plots',
                   'tar_images']:
        job_env_var_list.extend(['MET_ROOT', 'met_ver'])
    job_env_dict = {}
    for env_var in job_env_var_list:
        job_env_dict[env_var] = os.environ[env_var]
    if group in ['condense_stats', 'filter_stats', 'make_plots',
                 'tar_images']:
        job_env_dict['plot_verbosity'] = ('INFO')
    job_env_dict['JOB_GROUP'] = group
    if group in ['reformat_data', 'assemble_data', 'generate_stats',
                 'condense_stats', 'filter_stats', 'make_plots',
                 'tar_images']:
        job_env_dict['VERIF_TYPE'] = verif_type
        if group in ['condense_stats', 'filter_stats', 'make_plots',
                     'tar_images']:
            job_env_dict['job_var'] = job
        else:
            job_env_dict['job_name'] = job
        job_env_dict['fhr_start'] = os.environ[
            verif_case_step_abbrev_type+'_fhr_min'
        ]
        job_env_dict['fhr_end'] = os.environ[
            verif_case_step_abbrev_type+'_fhr_max'
        ]
        job_env_dict['fhr_inc'] = os.environ[
            verif_case_step_abbrev_type+'_fhr_inc'
        ]
        if verif_type in ['means', 'sfc']:
            verif_type_valid_hr_list = (
                os.environ[verif_case_step_abbrev_type+'_vhr_list']\
                .split(' ')
            )
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
            if verif_type in ['seaice', 'sea_ice']:
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('OSI-SAF')
                )
            elif verif_type == 'sst':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('GHRSST-OSPO')
                )
            elif verif_type == 'temp':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('ECMWF')
                )
            elif verif_type == 'pres_lvls':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('GFS')
                )
            elif verif_type == 'prepbufr':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('BUFR')
                )
            else:
                 valid_hr_start, valid_hr_end, valid_hr_inc = 00, 00, 12
            job_env_dict['valid_hr_start'] = str(valid_hr_start).zfill(2)
            job_env_dict['valid_hr_end'] = str(valid_hr_end).zfill(2)
            job_env_dict['valid_hr_inc'] = str(valid_hr_inc)
        verif_type_init_hr_list = (
            os.environ[verif_case_step_abbrev_type+'_inithour_list']\
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
         version

         Args:
             logger        - logger object
             met_root      - path to MET (string)
             met_version   - MET version number (string)
             met_line_type - MET line type (string)
         Returns:
             met_version_line_type_col_list - list of MET version
                                              line type columns (strings)
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
        logger.error(f"FATAL ERROR {met_minor_version_col_file} "
                     +"DOES NOT EXIST, "
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

def condense_model_stat_files(logger, input_dir, output_file, model, obs,
                              grid, vx_mask, fcst_var_name, obs_var_name,
                              line_type):
    """! Condense the individual date model stat file and
         thin out unneeded data

         Args:
             logger        - logger object
             input_dir     - path to input directory (string)
             output_file   - path to output file (string)
             model         - model name (string)
             obs           - observation name (string)
             grid          - verification grid (string)
             vx_mask       - verification masking region (string)
             fcst_var_name - forecast variable name (string)
             obs_var_name  - observation variable name (string)
             line_type     - MET line type (string)

         Returns:
    """
    model_stat_files_wildcard = os.path.join(input_dir, model, model+'_*.stat')
    model_stat_files = glob.glob(model_stat_files_wildcard, recursive=True)
    if len(model_stat_files) == 0:
        logger.warning(f"NO STAT FILES IN MATCHING "
                       +f"{model_stat_files_wildcard}")
    else:
        if not os.path.exists(output_file):
            logger.debug(f"Condensing down stat files matching "
                         +f"{model_stat_files_wildcard}")
            with open(model_stat_files[0]) as msf:
                met_header_cols = msf.readline()
            all_grep_output = ''
            grep_opts = (
                ' | grep "'+obs+' "'
                +' | grep "'+grid+' "'
                +' | grep "'+vx_mask+' "'
                +' | grep "'+fcst_var_name+' "'
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
            input_dir, model_num+'_'+model_dict['name']+'.stat'
        )
        if len(dates) != 0:
            input_parsed_model_stat_file = os.path.join(
                input_dir,
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
                +'.stat'
            )
            output_parsed_model_stat_file = os.path.join(
                output_dir,
                input_parsed_model_stat_file.rpartition('/')[2]
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
                fcst_var_thresh_symbol, fcst_vat_thresh_letter = (
                    format_thresh(fcst_var_thresh)
                )
            else:
                fcst_var_thresh_symbol = fcst_var_thresh
                fcst_vat_thresh_letter = fcst_var_thresh
            if obs_var_thresh != 'NA':
                obs_var_thresh_symbol, obs_vat_thresh_letter = (
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
                logger.warning(f"{parsed_model_stat_file} does not exist")
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
   else:
        logger.error("FATAL ERROR, "+stat+" IS NOT AN OPTION")
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
        logger.warning(f"{average_method} not recognized..."
                       +"use mean, or aggregation...returning NaN")
    return average_value
