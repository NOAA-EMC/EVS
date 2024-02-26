import os
import numpy as np
import datetime

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
            lmf.write("set -x\n")
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
            lmf.write("set -x\n")
            lmf.write(f'export subject="{obs} Data Missing for EVS '
                      +'global_det"\n')
            lmf.write(f'echo "Warning: No {obs} data was available for '
                      +f'valid date {valid_dt:%Y%m%d%H}" > mailmsg\n')
            lmf.write(f'echo "Missing file is {missing_file}" >> mailmsg\n')
            lmf.write(f'echo "Job ID: $jobid" >> mailmsg\n')
            lmf.write(f'cat mailmsg | mail -s "$subject" $MAILTO\n')
        os.chmod(log_missing_file, 0o755)

def initalize_job_env_dict():
    """! This initializes a dictionary of environment variables and their
         values to be set for the job pulling from environment variables
         already set previously
         Args:
         Returns:
             job_env_dict - dictionary of job settings
    """
    job_env_var_list = [
        'machine', 'evs_ver', 'HOMEevs', 'FIXevs', 'USHevs', 'DATA', 'COMROOT',
        'NET', 'RUN', 'VERIF_CASE', 'STEP', 'COMPONENT', 'MODELNAME', 'COMIN',
        'COMINgfs', 'SENDCOM', 'COMOUT', 'METPLUS_PATH', 'MET_ROOT', 'JOB_GROUP'
    ]
    job_env_dict = {}
    for env_var in job_env_var_list:
        job_env_dict[env_var] = os.environ[env_var]
    job_env_dict['MET_TMP_DIR'] = os.path.join(os.environ['DATA'], 'tmp')
    return job_env_dict
