import os
import datetime
import numpy as np
import subprocess
import shutil
import sys
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
    format_opt_list = ['lead', 'lead_shift', 'valid', 'init', 'cycle']
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
                   if format_opt == 'lead_shift':
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
                   elif format_opt in ['init', 'cycle']:
                       replace_format_opt_count = init_time_dt.strftime(
                           format_opt_count_fmt
                       )
                   else:
                       replace_format_opt_count = str_sub_dict[format_opt]
                   if format_opt == 'lead_shift':
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
            convert_grib2_grib1(source_file, working_file1)
        if check_file_exists_size(working_file1):
            source_file_accum_fhr_start = (
                int(forecast_hour) - source_file_accum
            )
            run_shell_command(
                [WGRIB+' '+working_file1+' | grep "'
                 +str(source_file_accum_fhr_start)+'-'
                 +forecast_hour+'hr" | '+WGRIB+' '+working_file1
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
        if 'wgrbbul/jma_' in source_file:
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
    os.environ['MET_TMP_DIR'] = os.path.join(
        os.environ['DATA'], os.environ['VERIF_CASE']+'_'+os.environ['STEP'],
        'METplus_output', 'tmp'
    )
    if not os.path.exists(os.environ['MET_TMP_DIR']):
        os.makedirs(os.environ['MET_TMP_DIR'])
    job_env_var_list = [
        'machine', 'evs_ver', 'HOMEevs', 'FIXevs', 'USHevs', 'METPLUS_PATH',
        'log_met_output_to_metplus', 'metplus_verbosity', 'MET_ROOT',
        'MET_bin_exec', 'met_verbosity', 'DATA', 'MET_TMP_DIR', 'COMROOT',
        'NET', 'RUN', 'VERIF_CASE', 'STEP', 'COMPONENT'
    ]
    job_env_dict = {}
    for env_var in job_env_var_list:
        job_env_dict[env_var] = os.environ[env_var]
    job_env_dict['JOB_GROUP'] = group
    if group in ['reformat', 'generate']:
        job_env_dict['VERIF_TYPE'] = verif_type
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
        if verif_type in ['pres_levs', 'means', 'sfc']:
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
    return job_env_dict
