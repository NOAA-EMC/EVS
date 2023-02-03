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
        print("ERROR: "+' '.join(run_command.args)+" gave return code "
              +str(run_command.returncode))

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
                             os.environ['COMPONENT'],
                             os.environ['RUN']+'_'+os.environ['VERIF_CASE'],
                             os.environ['STEP'], conf_file_name)
    if not os.path.exists(conf_file):
        print("ERROR: "+conf_file+" DOES NOT EXIST")
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
        print("ERROR: "+python_script+" DOES NOT EXIST")
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
    if os.path.exists(file_name):
        if os.path.getsize(file_name) > 0:
            file_good = True
        else:
            print("WARNING: "+file_name+" empty, 0 sized")
            file_good = False
    else:
        print("WARNING: "+file_name+" does not exist")
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
    """! Get a initialization hour/cycle

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

def prep_prod_gfs_file(source_file, dest_file, forecast_hour, prep_method):
    """! Do prep work for GFS production files

         Args:
             source_file_format - source file format (string)
             dest_file          - destination file (string)
             forecast_hour      - forecast hour (string)
             prep_method        - name of prep method to do
                                  (string)

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
    if prep_method == 'full': 
        if forecast_hour == 0:
            wgrib_fhr = 'anl'
        else:
            wgrib_fhr = forecast_hour
        thin_var_level_list = [
            'CAPE:surface',
            'CAPE:90-0 mb above ground',
            'CWAT:entire atmosphere (considered as a single layer)',
            'DPT:2 m above ground',
            'GUST:surface',
            'HGT:1000 mb', 'HGT:925 mb', 'HGT:850 mb', 'HGT:700 mb',
            'HGT:500 mb', 'HGT:400 mb', 'HGT:300 mb', 'HGT:250 mb',
            'HGT:200 mb', 'HGT:150 mb', 'HGT:100 mb', 'HGT:50 mb','HGT:20 mb',
            'HGT:10 mb', 'HGT:5 mb', 'HGT:1 mb', 'HGT:cloud ceiling',
            'HGT:tropopause',
            'HPBL:surface',
            'ICEC:surface',
            'ICETK:surface',
            'LHTFL:surface',
            'O3MR:925 mb', 'O3MR:100 mb', 'O3MR:70 mb', 'O3MR:50 mb',
            'O3MR:30 mb', 'O3MR:20 mb', 'O3MR:10 mb', 'O3MR:5 mb', 'O3MR:1 mb',
            'PRES:surface', 'PRES:tropopause',
            'PRMSL:mean sea level',
            'PWAT:entire atmosphere (considered as a single layer)',
            'RH:1000 mb', 'RH:925 mb', 'RH:850 mb', 'RH:700 mb', 'RH:500 mb',
            'RH:400 mb', 'RH:300 mb', 'RH:250 mb', 'RH:200 mb', 'RH:150 mb',
            'RH:100 mb', 'RH:50 mb','RH:20 mb', 'RH:10 mb', 'RH:5 mb',
            'RH:1 mb', 'RH:2 m above ground',
            'SHTFL:surface',
            'SNOD:surface',
            'SPFH:1000 mb', 'SPFH:925 mb', 'SPFH:850 mb', 'SPFH:700 mb',
            'SPFH:500 mb', 'SPFH:400 mb', 'SPFH:300 mb', 'SPFH:250 mb',
            'SPFH:200 mb', 'SPFH:150 mb', 'SPFH:100 mb', 'SPFH:50 mb',
            'SPFH:20 mb', 'SPFH:10 mb', 'SPFH:5 mb', 'SPFH:1 mb',
            'SPFH:2 m above ground',
            'SOILW:0-0.1 m below ground',
            'TCDC:entire atmosphere:'+wgrib_fhr,
            'TMP:1000 mb', 'TMP:925 mb', 'TMP:850 mb', 'TMP:700 mb',
            'TMP:500 mb', 'TMP:400 mb', 'TMP:300 mb', 'TMP:250 mb',
            'TMP:200 mb', 'TMP:150 mb', 'TMP:100 mb', 'TMP:50 mb',
            'TMP:20 mb', 'TMP:10 mb', 'TMP:5 mb', 'TMP:1 mb',
            'TMP:2 m above ground', 'TMP:surface', 'TMP:tropopause',
            'TOZNE:entire atmosphere (considered as a single layer)',
            'TSOIL:0-0.1 m below ground',
            'UGRD:1000 mb', 'UGRD:925 mb', 'UGRD:850 mb', 'UGRD:700 mb',
            'UGRD:500 mb', 'UGRD:400 mb', 'UGRD:300 mb', 'UGRD:250 mb',
            'UGRD:200 mb', 'UGRD:150 mb', 'UGRD:100 mb', 'UGRD:50 mb',
            'UGRD:20 mb', 'UGRD:10 mb', 'UGRD:5 mb', 'UGRD:1 mb',
            'UGRD:10 m above ground',
            'VGRD:1000 mb', 'VGRD:925 mb', 'VGRD:850 mb', 'VGRD:700 mb',
            'VGRD:500 mb', 'VGRD:400 mb', 'VGRD:300 mb', 'VGRD:250 mb',
            'VGRD:200 mb', 'VGRD:150 mb', 'VGRD:100 mb', 'VGRD:50 mb',
            'VGRD:20 mb', 'VGRD:10 mb', 'VGRD:5 mb', 'VGRD:1 mb',
            'VGRD:10 m above ground',
            'VIS:surface',
            'WEASD:surface'
        ]
        # Missing in GFS files: Sea Ice Drift (Velocity) - SICED??
        #                       Sea Ice Extent - Derived from ICEC?
        #                       Sea Ice Volume
        if check_file_exists_size(source_file):
            run_shell_command(['>', prepped_file])
            for thin_var_level in thin_var_level_list:
                run_shell_command([WGRIB2, '-match', '"'+thin_var_level+'"',
                                   source_file+'|'+WGRIB2, '-i', source_file,
                                   '-grib', working_file1])
                run_shell_command(['cat', working_file1, '>>', prepped_file])
                os.remove(working_file1)
    elif 'precip' in prep_method:
        if int(forecast_hour) % 24 == 0:
            thin_var_level = ('APCP:surface:0-'
                              +str(int(int(forecast_hour)/24)))
        else:
            thin_var_level = ('APCP:surface:0-'+forecast_hour)
        if check_file_exists_size(source_file):
            run_shell_command([WGRIB2, '-match', '"'+thin_var_level+'"',
                               source_file+'|'+WGRIB2, '-i', source_file,
                               '-grib', prepped_file])
    copy_file(prepped_file, dest_file)

def prep_prod_fnmoc_file(source_file, dest_file, forecast_hour,
                         prep_method):
    """! Do prep work for FNMOC production files

         Args:
             source_file   - source file format (string)
             dest_file     - destination file (string)
             forecast_hour - forecast hour (string)
             prep_method   - name of prep method to do
                             (string)

         Returns:
    """
    # Environment variables and executables
    # Working file names
    prepped_file = os.path.join(os.getcwd(),
                                'atmos.'+dest_file.rpartition('/')[2])
    # Prep file
    if check_file_exists_size(source_file):
        convert_grib2_grib2(source_file, prepped_file)
    copy_file(prepped_file, dest_file)


def prep_prod_jma_file(source_file_format, dest_file, forecast_hour,
                       prep_method):
    """! Do prep work for JMA production files
         
         Args:
             source_file_format - source file format (string)
             dest_file          - destination file (string)
             forecast_hour      - forecast hour (string)
             prep_method        - name of prep method to do
                                  (string)

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
    copy_file(prepped_file, dest_file)

def prep_prod_ecmwf_file(source_file, dest_file, forecast_hour, prep_method):
    """! Do prep work for ECMWF production files

         Args:
             source_file   - source file format (string)
             dest_file     - destination file (string)
             forecast_hour - forecast hour (string)
             prep_method   - name of prep method to do
                             (string)

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
        if check_file_exists_size(working_file1):
            run_shell_command(['chmod', '750', working_file1])
            run_shell_command(['chgrp', 'rstprod', working_file1])
            run_shell_command(
                [ECMGFSLOOKALIKENEW, working_file1, prepped_file]
            )
    elif 'precip' in prep_method:
        if check_file_exists_size(source_file):
            run_shell_command(
                [PCPCONFORM, 'ecmwf', source_file, prepped_file]
            )
    if os.path.exists(prepped_file):
        run_shell_command(['chmod', '750', prepped_file])
        run_shell_command(['chgrp', 'rstprod', prepped_file])
    copy_file(prepped_file, dest_file)

def prep_prod_ukmet_file(source_file_format, dest_file, forecast_hour,
                         prep_method):
    """! Do prep work for UKMET production files

         Args:
             source_file_format - source file format (string)
             dest_file          - destination file (string)
             forecast_hour      - forecast hour (string)
             prep_method        - name of prep method to do
                                  (string)

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

def prep_prod_dwd_file(source_file, dest_file, forecast_hour, prep_method):
    """! Do prep work for DWD production files

         Args:
             source_file_format - source file format (string)
             dest_file          - destination file (string)
             forecast_hour      - forecast hour (string)
             prep_method        - name of prep method to do
                                  (string)

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
        if check_file_exists_size(working_file1):
            run_shell_command(
               [PCPCONFORM, 'dwd', working_file1,
                prepped_file]
            )
    copy_file(prepped_file, dest_file)

def prep_prod_metfra_file(source_file, dest_file, forecast_hour, prep_method):
    """! Do prep work for METRFRA production files

         Args:
             source_file   - source file(string)
             dest_file     - destination file (string)
             forecast_hour - forecast hour (string)
             prep_method   - name of prep method to do
                             (string)

         Returns:
    """
    # Environment variables and executables
    EXECevs = os.environ['EXECevs']
    WGRIB = os.environ['WGRIB']
    # Temporary file names
    prepped_file = os.path.join(os.getcwd(),
                                'atmos.'+dest_file.rpartition('/')[2])
    # Prep file
    if 'precip' in prep_method:
        file_accum = 24
        fhr_accum_start = int(forecast_hour)-file_accum
        if check_file_exists_size(source_file):
            run_shell_command(
                [WGRIB+' '+source_file+' | grep "'
                 +str(fhr_accum_start)+'-'
                 +forecast_hour+'hr" | '+WGRIB+' '+source_file
                 +' -i -grib -o '+prepped_file]
            )
    copy_file(prepped_file, dest_file)

def prep_prod_osi_saf_file(daily_source_file_format, daily_dest_file,
                           weekly_source_file_list, weekly_dest_file,
                           weekly_dates):
    """! Do prep work for OSI-SAF production files

         Args:
             daily_source_file_format - daily source file format (string)
             daily_dest_file          - daily destination file (string)
             weekly_source_file_list  - list of daily files to make up
                                        weekly average file
             weekly_dest_file         - weekly destination file (string)
             weekly_dates             - date span for weekly dates (tuple
                                        of datetimes)
         Returns:
    """
    # Environment variables and executables
    FIXevs = os.environ['FIXevs']
    CDO_ROOT = os.environ['CDO_ROOT']
    # Temporary file names
    daily_prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                      +daily_dest_file.rpartition('/')[2])
    weekly_prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                       +weekly_dest_file.rpartition('/')[2])
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
                +os.path.join(FIXevs, 'cdo_grids', 'G004.grid'),
                hem_source_file, hem_prepped_file]
            )
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
        for var in ['ice_conc', 'ice_conc_unfiltered', 'masks',
                    'confidence_level', 'status_flag', 'total_uncertainty',
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
                np.vstack((sh_data.variables[var][0,:180,:],
                           nh_data.variables[var][0,180:,:]))
               ,nh_data.variables[var]._FillValue)
            merged_var[:] = merged_var_vals
        merged_data.close()
    copy_file(daily_prepped_file, daily_dest_file)
    # Prep weekly file
    #for weekly_source_file in weekly_source_file_list:
    #    if not os.path.exists(weekly_source_file):
    #        print(f"WARNING: {weekly_source_file} does not exist, "
    #              +"not using in weekly average file")
    #        weekly_source_file_list.remove(weekly_source_file)
    #if len(weekly_source_file_list) == 7:
    #    ncea_cmd_list = ['ncea']
    #    for weekly_source_file in weekly_source_file_list:
    #        ncea_cmd_list.append(weekly_source_file)
    #    ncea_cmd_list.append('-o')
    #    ncea_cmd_list.append(weekly_prepped_file)
    #    run_shell_command(ncea_cmd_list)
    #    if check_file_exists_size(weekly_prepped_file):
    #        weekly_data = netcdf.Dataset(weekly_prepped_file, 'a',
    #                                     format='NETCDF3_CLASSIC')
    #        weekly_data.setncattr(
    #            'start_date', weekly_dates[0].strftime('%Y-%m-%d %H:%M:%S')
    #        )
    #        osi_saf_date_since_dt = datetime.datetime.strptime(
    #            '1978-01-01 00:00:00','%Y-%m-%d %H:%M:%S'
    #        )
    #        weekly_data.variables['time_bnds'][:] = [
    #            (weekly_dates[0] - osi_saf_date_since_dt).total_seconds(),
    #            weekly_data.variables['time_bnds'][:][0][1]
    #        ]
    #        weekly_data.close()
    #else:
    #    print("Not enough files to make "+weekly_prepped_file
    #          +": "+' '.join(weekly_source_file_list))
    #copy_file(weekly_prepped_file, weekly_dest_file)

def prep_prod_ghrsst_ospo_file(source_file, dest_file, date_dt):
    """! Do prep work for GHRSST OSPO production files

         Args:
             source_file - source file (string)
             dest_file   - destination file (string)
             date_dt     - date (datetime object)
         Returns:
    """
    # Environment variables and executables
    # Temporary file names
    prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                +source_file.rpartition('/')[2])
    # Prep file
    copy_file(source_file, prepped_file)
    if check_file_exists_size(prepped_file):
        prepped_data = netcdf.Dataset(prepped_file, 'a',
                                      format='NETCDF3_CLASSIC')
        ghrsst_ospo_date_since_dt = datetime.datetime.strptime(
            '1981-01-01 00:00:00','%Y-%m-%d %H:%M:%S'
        )
        prepped_data['time'][:] = prepped_data['time'][:][0] + 43200
        prepped_data.close()
    copy_file(prepped_file, dest_file)

def prep_prod_get_d_file(source_file, dest_file, date_dt):
    """! Do prep work for ALEXI GET-D production files

         Args:
             source_file - source file (string)
             dest_file   - destination file (string)
             date_dt     - date (datetime object)
         Returns:
    """
    # Environment variables and executables
    # Temporary file names
    prepped_file = os.path.join(os.getcwd(), 'atmos.'
                                +source_file.rpartition('/')[2])
    # Prep file
    #copy_file(prod_file, prepped_file)
    ##########################################################################
    # Temporary until NCO brings in data feed
    ftp_file = ('ftp://ftp.star.nesdis.noaa.gov/'
                +'pub/smcd/emb/lfang/GET-D_ET_H_updated/'
                +date_dt.strftime('%Y')+'/'
                +'GETDL3_DAL_CONUS_'+date_dt.strftime('%Y%j')+'_1.0.nc')
    run_shell_command(
        ['wget', ftp_file]
    )
    copy_file(os.path.join(os.getcwd(),ftp_file.rpartition('/')[2]), prepped_file)
    ##########################################################################
    copy_file(prepped_file, dest_file)

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
    if not os.path.exists(dest_file):
        source_file = format_filler(source_file_format, valid_time_dt,
                                    init_time_dt, forecast_hour, {})
        if 'dcom/navgem' in source_file:
            prep_prod_fnmoc_file(source_file, dest_file, forecast_hour, 'full')
        elif 'wgrbbul/jma_' in source_file:
            prep_prod_jma_file(source_file, dest_file, forecast_hour, 'full')
        elif 'wgrbbul/ecmwf' in source_file:
            prep_prod_ecmwf_file(source_file, dest_file, forecast_hour, 'full')
        elif 'wgrbbul/ukmet_hires' in source_file:
            prep_prod_ukmet_file(source_file, dest_file, forecast_hour, 'full')
        elif 'qpf_verif/jma' in source_file:
            prep_prod_jma_file(source_file, dest_file, forecast_hour,
                               'precip')
        elif 'qpf_verif/UWD' in source_file:
            prep_prod_ecmwf_file(source_file, dest_file, forecast_hour,
                                 'precip')
        elif 'qpf_verif/ukmo' in source_file:
            prep_prod_ukmet_file(source_file, dest_file, forecast_hour,
                                 'precip')
        elif 'qpf_verif/dwd' in source_file:
            prep_prod_dwd_file(source_file, dest_file, forecast_hour,
                               'precip')
        elif 'qpf_verif/METFRA' in source_file:
            prep_prod_metfra_file(source_file, dest_file, forecast_hour,
                                  'precip')
        else:
            if os.path.exists(source_file):
                print("Linking "+source_file+" to "+dest_file)
                os.symlink(source_file, dest_file)   
            else:
                print("WARNING: "+source_file+" DOES NOT EXIST")

def get_truth_file(valid_time_dt, source_file_format, dest_file_format):
    """! This get a model file and saves it in the specificed
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
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hr_start'],
        '%Y%m%d%H'
    )
    verif_case_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE']+'_'+job_dict['STEP']
    )
    model = job_dict['MODEL']
    fhr_min = int(job_dict['fhr_start'])
    fhr_max = int(job_dict['fhr_end'])
    fhr_inc = int(job_dict['fhr_inc'])
    fhr = fhr_min
    fhr_list = []
    fhr_check_dict = {}
    while fhr <= fhr_max:
        fhr_check_dict[str(fhr)] = {}
        init_date_dt = valid_date_dt - datetime.timedelta(hours=fhr)
        if job_dict['JOB_GROUP'] == 'reformat_data':
            model_file_format = os.path.join(verif_case_dir, 'data', model,
                                             model+'.{init?fmt=%Y%m%d%H}.'
                                             +'f{lead?fmt=%3H}')
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] == 'pres_levs' \
                        and job_dict['job_name'] == 'GeoHeightAnom':
                    if init_date_dt.strftime('%H') in ['00', '12'] \
                            and fhr % 24 == 0:
                        fhr_check_dict[str(fhr)]['file1'] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr)
                        }
                        fhr_check_dict[str(fhr)]['file2'] = {
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
                        fhr_check_dict[str(fhr)]['file'+str(nf+1)] = {
                            'valid_date': valid_date_dt,
                            'init_date': valid_date_dt-datetime.timedelta(
                                             hours=fhr_in_avg
                            ),
                            'forecast_hour': str(fhr_in_avg)
                        }
                        nf+=1
                        fhr_in_avg+=int(job_dict['fhr_inc'])
                else:
                    fhr_check_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
            if job_dict['VERIF_CASE'] == 'grid2obs':
                if job_dict['VERIF_TYPE'] == 'ptype':
                    fhr_check_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
        elif job_dict['JOB_GROUP'] == 'assemble_data':
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] == 'precip':
                    model_file_format = os.path.join(verif_case_dir, 'data',
                                                     model, model+'.precip.'
                                                     +'{init?fmt=%Y%m%d%H}.'
                                                     +'f{lead?fmt=%3H}')
                elif job_dict['VERIF_TYPE'] == 'pres_levs' \
                        and job_dict['job_name'] == 'DailyAvg_GeoHeightAnom':
                    model_file_format = os.path.join(verif_case_dir,
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
                elif job_dict['VERIF_TYPE'] in ['sea_ice', 'sst']:
                    model_file_format = os.path.join(verif_case_dir,
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
                else:
                    model_file_format = os.path.join(verif_case_dir, 'data',
                                                     model, model
                                                     +'.{init?fmt=%Y%m%d%H}.'
                                                     +'f{lead?fmt=%3H}')
                if job_dict['VERIF_TYPE'] == 'precip' \
                        and job_dict['job_name'] == '24hrAccum':
                    fhr_in_accum_list = [str(fhr)]
                    if job_dict['MODEL_accum'][0] == '{': #continuous
                        if fhr-24 > 0:
                            fhr_in_accum_list.append(str(fhr-24))
                    elif int(job_dict['MODEL_accum']) < 24:
                        nfiles_in_accum = int(24/int(job_dict['MODEL_accum']))
                        nf = 1
                        while nf <= nfiles_in_accum:
                            fhr_nf = fhr - ((nf-1)*int(job_dict['MODEL_accum']))
                            if fhr_nf > 0:
                                fhr_in_accum_list.append(str(fhr_nf))
                            nf+=1
                    for fhr_in_accum in fhr_in_accum_list:
                        file_num = fhr_in_accum_list.index(fhr_in_accum)+1
                        fhr_check_dict[str(fhr)]['file'+str(file_num)] = {
                            'valid_date': valid_date_dt,
                            'init_date': init_date_dt,
                            'forecast_hour': str(fhr_in_accum)
                        }
                elif job_dict['VERIF_TYPE'] == 'snow':
                    fhr_check_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
                    fhr_check_dict[str(fhr)]['file2'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr-24)
                    }
                else:
                    fhr_check_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
            elif job_dict['VERIF_CASE'] == 'grid2obs':
                model_file_format = os.path.join(verif_case_dir, 'data',
                                                 model, model
                                                 +'.{init?fmt=%Y%m%d%H}.'
                                                 +'f{lead?fmt=%3H}')
                if job_dict['VERIF_TYPE'] == 'sfc' \
                        and job_dict['job_name'] == 'TempAnom2m':
                    fhr_check_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
                    fhr_check_dict[str(fhr)]['file2'] = {
                        'valid_date': valid_date_dt,
                        'init_date': (valid_date_dt
                                      -datetime.timedelta(hours=fhr-12)),
                        'forecast_hour': str(fhr-12)
                    }
                elif job_dict['VERIF_TYPE'] == 'ptype':
                    fhr_check_dict[str(fhr)]['file1'] = {
                        'valid_date': valid_date_dt,
                        'init_date': init_date_dt,
                        'forecast_hour': str(fhr)
                    }
        elif job_dict['JOB_GROUP'] == 'generate_stats':
            if job_dict['VERIF_CASE'] == 'grid2grid':
                if job_dict['VERIF_TYPE'] == 'pres_levs' \
                        and job_dict['job_name'] == 'DailyAvg_GeoHeightAnom':
                    model_file_format = os.path.join(
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
                    model_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'wind_shear_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'precip':
                    model_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'pcp_combine_'
                        +job_dict['VERIF_TYPE']+'_24hrAccum_init'
                        +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'sea_ice':
                    model_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'daily_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-24}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                elif job_dict['VERIF_TYPE'] == 'snow':
                    model_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'pcp_combine_'
                        +job_dict['VERIF_TYPE']+'_24hrAccum_'
                        +job_dict['file_name_var']+'_init'
                        +'{init?fmt=%Y%m%d%H}_fhr{lead?fmt=%3H}.nc'
                    )
                elif  job_dict['VERIF_TYPE'] == 'sst':
                    model_file_format = os.path.join(
                        verif_case_dir, 'METplus_output',
                        job_dict['RUN']+'.{valid?fmt=%Y%m%d}',
                        model, job_dict['VERIF_CASE'], 'daily_avg_'
                        +job_dict['VERIF_TYPE']+'_'+job_dict['job_name']
                        +'_init{init?fmt=%Y%m%d%H}_'
                        +'valid{valid_shift?fmt=%Y%m%d%H?shift=-24}'
                        +'to{valid?fmt=%Y%m%d%H}.nc'
                    )
                else:
                    model_file_format = os.path.join(
                        verif_case_dir, 'data', model,
                        model+'.{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}'
                    )
            elif job_dict['VERIF_CASE'] == 'grid2obs':
                if job_dict['VERIF_TYPE'] == 'ptype' \
                        and job_dict['job_name'] == 'Ptype':
                    model_file_format = os.path.join(verif_case_dir,
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
                    model_file_format = os.path.join(verif_case_dir,
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
                    model_file_format = os.path.join(
                        verif_case_dir, 'data', model,
                        model+'.{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}'
                    )
            fhr_check_dict[str(fhr)]['file1'] = {
                'valid_date': valid_date_dt,
                'init_date': init_date_dt,
                'forecast_hour': str(fhr)
            }
        fhr+=fhr_inc
    for fhr_key in list(fhr_check_dict.keys()):
        fhr_key_files_exist_list = []
        for fhr_fileN_key in list(fhr_check_dict[fhr_key].keys()):
            fhr_fileN = format_filler(
                model_file_format,
                fhr_check_dict[fhr_key][fhr_fileN_key]['valid_date'],
                fhr_check_dict[fhr_key][fhr_fileN_key]['init_date'],
                fhr_check_dict[fhr_key][fhr_fileN_key]['forecast_hour'],
                {}
            )
            if os.path.exists(fhr_fileN):
                fhr_key_files_exist_list.append(True)
                if job_dict['JOB_GROUP'] == 'reformat_data' \
                        and job_dict['job_name'] in ['GeoHeightAnom',
                                                     'Concentration',
                                                     'SST']:
                    fhr_list.append(
                        fhr_check_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
                elif job_dict['JOB_GROUP'] == 'assemble_data' \
                        and job_dict['job_name'] in ['TempAnom2m']:
                    fhr_list.append(
                        fhr_check_dict[fhr_key][fhr_fileN_key]\
                        ['forecast_hour']
                    )
            else:
                fhr_key_files_exist_list.append(False)
        if all(x == True for x in fhr_key_files_exist_list) \
                and len(fhr_key_files_exist_list) > 0:
            fhr_list.append(fhr_key)
    fhr_list = list(
        np.asarray(np.unique(np.asarray(fhr_list, dtype=int)),dtype=str)
    )
    # UKMET data doesn't have RH for fhr 132 or 144
    if job_dict['MODEL'] == 'ukmet' \
            and job_dict['VERIF_CASE'] == 'grid2obs' \
            and job_dict['VERIF_TYPE'] == 'pres_levs' \
            and job_dict['job_name'] == 'RelHum':
        for fhr_rm in ['132', '144']:
            if fhr_rm in fhr_list:
                fhr_list.remove(fhr_rm)
    if len(fhr_list) != 0:
        model_files_exist = True
    else:
        model_files_exist = False
    return model_files_exist, fhr_list

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
            if job_dict['VERIF_TYPE'] == 'pres_levs':
                model_truth_file = os.path.join(
                    verif_case_dir, 'data', job_dict['MODEL'],
                    job_dict['MODEL']+'.'+valid_date_dt.strftime('%Y%m%d%H')
                    +'.truth'
                )
                truth_file_list.append(model_truth_file)
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
                truth_file_list.append(prepbufr_file)
    elif job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['VERIF_CASE'] == 'grid2grid':
            if job_dict['VERIF_TYPE'] == 'precip' \
                    and job_dict['job_name'] == '24hrCCPA':
                ccpa_dir = os.path.join(verif_case_dir, 'data', 'ccpa')
                nccpa_files = 4
                n = 1
                while n <= 4:
                    nccpa_file = os.path.join(
                        ccpa_dir, 'ccpa.6H.'
                        +(valid_date_dt-datetime.timedelta(hours=(n-1)*6))\
                        .strftime('%Y%m%d%H')
                    )
                    truth_file_list.append(nccpa_file)
                    n+=1
        elif job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] in ['pres_levs', 'sfc', 'ptype']:
                pb2nc_file = os.path.join(
                    verif_case_dir, 'METplus_output',
                    job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                    'prepbufr', job_dict['VERIF_CASE'], 'pb2nc_'
                    +job_dict['VERIF_TYPE']+'_'+job_dict['prepbufr']+'_valid'
                    +valid_date_dt.strftime('%Y%m%d%H')+'.nc'
                )
                truth_file_list.append(pb2nc_file)
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        if job_dict['VERIF_CASE'] == 'grid2grid':
            if job_dict['VERIF_TYPE'] == 'pres_levs':
                model_truth_file = os.path.join(
                    verif_case_dir, 'data', job_dict['MODEL'],
                    job_dict['MODEL']+'.'+valid_date_dt.strftime('%Y%m%d%H')
                    +'.truth'
                )
                truth_file_list.append(model_truth_file)
            elif job_dict['VERIF_TYPE'] == 'precip':
               ccpa_file = os.path.join(
                   verif_case_dir, 'METplus_output',
                   job_dict['RUN']+'.'+valid_date_dt.strftime('%Y%m%d'),
                   'ccpa', job_dict['VERIF_CASE'], 'pcp_combine_'
                   +job_dict['VERIF_TYPE']+'_24hrCCPA_valid'
                   +valid_date_dt.strftime('%Y%m%d%H')+'.nc'
               )
               truth_file_list.append(ccpa_file)
            elif job_dict['VERIF_TYPE'] == 'sea_ice':
                osi_saf_file = os.path.join(
                    verif_case_dir, 'data', 'osi_saf',
                    'osi_saf.multi.'
                    +(valid_date_dt-datetime.timedelta(hours=24))\
                    .strftime('%Y%m%d%H')
                    +'to'+valid_date_dt.strftime('%Y%m%d%H')+'_G004.nc'
                )
                truth_file_list.append(osi_saf_file)
            elif job_dict['VERIF_TYPE'] == 'snow':
               nohrsc_file = os.path.join(
                   verif_case_dir, 'data', 'nohrsc',
                   'nohrsc.24H.'+valid_date_dt.strftime('%Y%m%d%H')
               )
               truth_file_list.append(nohrsc_file)
            elif job_dict['VERIF_TYPE'] == 'sst':
               ghrsst_ospo_file = os.path.join(
                   verif_case_dir, 'data', 'ghrsst_ospo',
                   'ghrsst_ospo.'
                   +(valid_date_dt-datetime.timedelta(hours=24))\
                   .strftime('%Y%m%d%H')
                   +'to'+valid_date_dt.strftime('%Y%m%d%H')+'.nc'
               )
               truth_file_list.append(ghrsst_ospo_file)
        elif job_dict['VERIF_CASE'] == 'grid2obs':
            if job_dict['VERIF_TYPE'] in ['pres_levs', 'sfc', 'ptype']:
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
        '24hrCCPA': {'valid_hr_start': 12,
                     'valid_hr_end': 12,
                     'valid_hr_inc': 24},
        '24hrNOHRSC': {'valid_hr_start': 12,
                       'valid_hr_end': 12,
                       'valid_hr_inc': 24},
        'OSI-SAF': {'valid_hr_start': 00,
                    'valid_hr_end': 00,
                    'valid_hr_inc': 24},
        'GHRSST-MEDIAN': {'valid_hr_start': 00,
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
        print(f"ERROR: Cannot get {obs} valid hour information")
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
        'NET', 'RUN', 'VERIF_CASE', 'STEP', 'COMPONENT', 'COMIN', 'evs_run_mode'
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
            ['METPLUS_PATH','log_met_output_to_metplus', 'metplus_verbosity',
             'MET_ROOT', 'MET_bin_exec', 'met_verbosity', 'MET_TMP_DIR',
             'COMROOT']
        )
    elif group == 'plot':
        job_env_var_list.extend(['MET_ROOT', 'met_ver'])
    job_env_dict = {}
    for env_var in job_env_var_list:
        job_env_dict[env_var] = os.environ[env_var]
    if group == 'plot':
        job_env_dict['plot_verbosity'] = (
            os.environ['metplus_verbosity']
        )
    job_env_dict['JOB_GROUP'] = group
    if group in ['reformat_data', 'assemble_data', 'generate_stats', 'plot']:
        job_env_dict['VERIF_TYPE'] = verif_type
        if group == 'plot':
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
        if verif_type in ['pres_levs', 'means', 'sfc', 'ptype']:
            verif_type_valid_hr_list = (
                os.environ[verif_case_step_abbrev_type+'_valid_hr_list']\
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
            if verif_type == 'precip':
                valid_hr_start, valid_hr_end, valid_hr_inc = (
                    get_obs_valid_hrs('24hrCCPA')
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
                    get_obs_valid_hrs('GHRSST-MEDIAN')
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
            if not os.path.exists(condensed_model_file):
                write_condensed_stat_file = True
            else:
                write_condensed_stat_file = False
            if write_condensed_stat_file:
                condense_model_stat_files(
                    logger, input_dir, condensed_model_file, model_dict['name'],
                    model_dict['obs_name'], grid, vx_mask,
                    fcst_var_name, obs_var_name, line_type
                )
            parsed_model_stat_file = os.path.join(
                output_dir,
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
   if stat == 'ACC': # Anomaly Correlation Coefficient
       if line_type == 'SAL1L2':
           stat_df = (FOABAR - FABAR*OABAR) \
                     /np.sqrt((FFABAR - FABAR*FABAR)*
                              (OOABAR - OABAR*OABAR))
       elif line_type == 'CNT':
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
