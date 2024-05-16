#!/usr/bin/env python3
'''
Program Name: get_gefs_subseasonal_data_files_prep.py
Contact(s): Shannon Shields
Abstract: This script is run by subseasonal_prep_gefs_create_job_scripts.py
          in ush/subseasonal.
          This gets the necessary GEFS model files for the
          prep step.
'''

import os
import subprocess
import datetime
from time import sleep
import pandas as pd
import glob
import numpy as np
import subseasonal_util as sub_util

print("BEGIN: "+os.path.basename(__file__))

def get_time_info(start_date_str, end_date_str,
                  start_hr_str, end_hr_str, hr_inc_str,
                  fhr_list, date_type):
    """! This creates a list of dictionaries containing information
         on the valid dates and times, the initialization dates
         and times, and forecast hour pairings

         Args:
             start_date_str - string of the verification start
                              date
             end_date_str   - string of the verification end
                              date
             start_hr_str   - string of the verification start
                              hour
             end_hr_str     - string of the verification end
                              hour
             hr_inc_str     - string of the increment between
                              start_hr and end_hr
             fhr_list       - list of strings of the forecast
                              hours to verify
             date_type      - string defining by what type
                              date and times to create prep
                              data

         Returns:
             time_info - list of dictionaries with the valid,
                         initialization, and forecast hour
                         pairings
    """
    sdate = datetime.datetime(int(start_date_str[0:4]),
                              int(start_date_str[4:6]),
                              int(start_date_str[6:]),
                              int(start_hr_str))
    edate = datetime.datetime(int(end_date_str[0:4]),
                              int(end_date_str[4:6]),
                              int(end_date_str[6:]),
                              int(end_hr_str))
    date_inc = datetime.timedelta(seconds=int(hr_inc_str))
    time_info = []
    date = sdate
    while date <= edate:
        if date_type == 'VALID':
            valid_time = date
        elif date_type == 'INIT':
            init_time = date
        for fhr in fhr_list:
            if fhr == 'anl':
                lead = '0'
            else:
                lead = fhr
            if date_type == 'VALID':
                init_time = valid_time - datetime.timedelta(hours=int(lead))
            elif date_type == 'INIT':
                valid_time = init_time + datetime.timedelta(hours=int(lead))
            t = {}
            t['valid_time'] = valid_time
            t['init_time'] = init_time
            t['lead'] = lead
            time_info.append(t)
        date = date + date_inc
    return time_info

def format_filler(unfilled_file_format, dt_valid_time, dt_init_time, str_lead):
    """! This creates a list of objects containing information
         on the valid dates and times, the initialization dates
         and times, and forecast hour pairings

         Args:
             unfilled_file_format   - string of file naming convention
             dt_valid_time          - datetime object of the valid time
             dt_init_time           - datetime object of the
                                      initialization time
             str_lead               - string of the forecast lead

         Returns:
             filled_file_format - string of file_format
                                  filled in with verifying
                                  time information
    """
    filled_file_format = ''
    format_opt_list = ['lead', 'valid', 'init']
    for filled_file_format_chunk in unfilled_file_format.split('/'):
        for format_opt in format_opt_list:
            nformat_opt = (
                filled_file_format_chunk.count('{'+format_opt+'?fmt=')
            )
            if nformat_opt > 0:
               format_opt_count = 1
               while format_opt_count <= nformat_opt:
                   format_opt_count_fmt = (
                       filled_file_format_chunk \
                       .partition('{'+format_opt+'?fmt=')[2] \
                       .partition('}')[0]
                   )
                   if format_opt == 'valid':
                       replace_format_opt_count = dt_valid_time.strftime(
                           format_opt_count_fmt
                       )
                   elif format_opt == 'lead':
                       if format_opt_count_fmt == '%1H':
                           if int(str_lead) < 10:
                               replace_format_opt_count = str_lead[1]
                           else:
                               replace_format_opt_count = str_lead
                       elif format_opt_count_fmt == '%2H':
                           replace_format_opt_count = str_lead.zfill(2)
                       elif format_opt_count_fmt == '%3H':
                           replace_format_opt_count = str_lead.zfill(3)
                       else:
                           replace_format_opt_count = str_lead
                   elif format_opt == 'init':
                       replace_format_opt_count = dt_init_time.strftime(
                           format_opt_count_fmt
                       )
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

def get_source_file(valid_time_dt, init_time_dt, lead_str,
                   name, data_dir, file_format):
    """! This links a model file from its source.

         Args:
             valid_time_dt    - datetime object of the valid time
             init_time_dt     - datetime object of the
                                initialization time
             lead_str         - string of the forecast lead
             name             - string of the model name
             data_dir         - string of the online archive
                                for model
             file_format      - string of the file format the
                                files are saved as in the data_dir

         Returns:
             model_file
    """
    
    model_filename = format_filler(file_format, valid_time_dt,
                                       init_time_dt, lead_str)
    model_file = os.path.join(data_dir, model_filename)
    if os.path.exists(model_file):
        print("SUCCESS: "+model_file+" exists")
    else:
        print("WARNING: "+model_file+" does not exist")
    return model_file
    
def get_dest_file(valid_time_dt, init_time_dt, lead_str,
                  name, dest_data_dir, dest_file_format):
    """! This creates the model destination file to save in prep.

         Args:
             valid_time_dt    - datetime object of the valid time
             init_time_dt     - datetime object of the
                                initialization time
             lead_str         - string of the forecast lead
             name             - string of the model name
             dest_data_dir    - string of the directory to link
                                model data to
             dest_file_format - string of the linked file name
         Returns:
             dest_model_file
    """

    dest_filename = format_filler(dest_file_format, valid_time_dt,
                                  init_time_dt, lead_str)
    dest_model_file = os.path.join(dest_data_dir, dest_filename)
    return dest_model_file

# Read in common environment variables
RUN = os.environ['RUN']
STEP = os.environ['STEP']
DATA = os.environ['DATA']
SENDCOM = os.environ['SENDCOM']
model_list = os.environ['model_list'].split(' ')
model_dir_list = os.environ['model_dir_list'].split(' ')
model_prep_dir_list = os.environ['model_prep_dir_list'].split(' ')
model_file_format_list = os.environ['model_file_format_list'].split(' ')
gefs_file_type = os.environ['gefs_file_type']
gefs_members = os.environ['gefs_members']
INITDATE = os.environ['INITDATE']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
make_prep_data_by = os.environ['make_prep_data_by']
machine = os.environ['machine']

# Set some common variables
cwd = os.getcwd()
if cwd != DATA:
    os.chdir(DATA)

if STEP == 'prep':
    # Read in environment variables
    # Get model forecast files
    inithour_list = os.environ['inithour_list'
    ].split(' ')
    vhr_list = os.environ['vhr_list'
    ].split(' ')
    start_hr = os.environ[make_prep_data_by.lower()+'_hr_beg']
    end_hr = os.environ[make_prep_data_by.lower()+'_hr_end']
    hr_inc = os.environ[make_prep_data_by.lower()+'_hr_inc']
    fhr_list = os.environ['fhr_list'
    ].split(',')
    # Get date and time information
    time_info_dict = get_time_info(
        start_date, end_date, start_hr,
        end_hr, hr_inc,
        fhr_list, make_prep_data_by
    )
    # Get GEFS forecast files
    for model in model_list:
        model_idx = model_list.index(model)
        model_dir = model_dir_list[model_idx]
        model_prep_dir = model_prep_dir_list[model_idx]
        model_file_form = model_file_format_list[model_idx]
        # Get model forecast files
        for time in time_info_dict:
            valid_time = time['valid_time']
            init_time = time['init_time']
            lead = time['lead']
            if init_time.strftime('%H') \
                    not in inithour_list:
                continue
            elif valid_time.strftime('%H') \
                    not in vhr_list:
                continue
            else:
                work_model_dir = os.path.join(cwd, 'data', 'gefs')
                if not os.path.exists(work_model_dir):
                    os.makedirs(work_model_dir)
                dest_model_dir = os.path.join(model_prep_dir, 'gefs')
                if not os.path.exists(dest_model_dir):
                    os.makedirs(dest_model_dir)
                if model == 'gefs':
                    mbr = 1
                    total = int(gefs_members)
                    while mbr <= total:
                        mb = str(mbr).zfill(2)
                        model_afile_format = os.path.join(
                            model_file_form, 'pgrb2ap5', 
                            'gep'+mb
                            +'.t{init?fmt=%2H}z.pgrb2a.0p50.'
                            +'f{lead?fmt=%3H}'
                        )
                        model_bfile_format = os.path.join(
                            model_file_form, 'pgrb2bp5',
                            'gep'+mb
                            +'.t{init?fmt=%2H}z.pgrb2b.0p50.'
                            +'f{lead?fmt=%3H}'
                        )
                        model_afile = get_source_file(
                            valid_time, init_time, lead,
                            model, model_dir,
                            model_afile_format
                        )
                        model_bfile = get_source_file(
                            valid_time, init_time, lead,
                            model, model_dir,
                            model_bfile_format
                        )
                        prep_file = get_dest_file(
                            valid_time, init_time, lead,
                            model,
                            work_model_dir, 'getgefs.'
                            +mb+'.{init?fmt=%2H}z'
                            +'.f{lead?fmt=%3H}'
                        )
                        dest_model_file = get_dest_file(
                            valid_time, init_time, lead,
                            model,
                            dest_model_dir, model+'.'
                            +'ens'+mb+'.t{init?fmt=%2H}z'
                            +'.pgrb2.0p50.'
                            +'f{lead?fmt=%3H}'
                        )
                        log_missing_file = os.path.join(
                            DATA, 'mail_missing_'+model+'_'
                            +'member'+mb+'_fhr'
                            +lead.zfill(3)+'_init'
                            +init_time.strftime('%Y%m%d%H')+'.sh'
                        )
                        sub_util.prep_prod_gefs_file(model_afile,
                                                     model_bfile,
                                                     prep_file,
                                                     dest_model_file,
                                                     init_time,
                                                     lead,
                                                     'full',
                                                     log_missing_file)
                        if SENDCOM == 'YES':
                            sub_util.copy_file(prep_file,
                                               dest_model_file)
                        del model_afile_format
                        del model_bfile_format
                        mbr = mbr+1

print("END: "+os.path.basename(__file__))
