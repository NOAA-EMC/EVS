#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_util.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Various Utilities for EVS CAM Verification
# 
# =============================================================================

import os
from collections.abc import Iterable
import numpy as np
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
        'NOHRSC': {
            'and':[''],
            'or':['sfav2'],
            'not':[],
            'type': 'gen'
        },
        'mPING': {
            'and':[''],
            'or':['mPING', 'mping'],
            'not':[],
            'type': 'gen'
        },
        'FireWX Nest': {
            'and':[''],
            'or':['firewx'],
            'not':[],
            'type': 'anl'
        },
        'SPC Outlook Area': {
            'and':[''],
            'or':['spc_otlk'],
            'not':[],
            'type': 'gen'
        },
        'CCPA': {
            'and':[''],
            'or':['ccpa'],
            'not':[],
            'type': 'gen'
        },
        'MRMS': {
            'and':[''],
            'or':['mrms'],
            'not':[],
            'type': 'gen'
        },
        'NAM Nest Forecast': {
            'and':['nam', 'nest'],
            'or':[''],
            'not':[],
            'type': 'fcst'
        },
        'HRRR Forecast': {
            'and':['hrrr'],
            'or':[''],
            'not':[],
            'type': 'fcst'
        },
        'HiRes Window ARW Forecast': {
            'and':['hiresw','arw'],
            'or':[''],
            'not':['mem2'],
            'type': 'fcst'
        },
        'HiRes Window ARW2 Forecast': {
            'and':['hiresw','arw','mem2'],
            'or':[''],
            'not':[],
            'type': 'fcst'
        },
        'HiRes Window FV3 Forecast': {
            'and':['hiresw','fv3'],
            'or':[''],
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
        'NOHRSC': {
            'and':[''],
            'or':['sfav2'],
            'not':[],
            'type': 'gen'
        },
        'mPING': {
            'and':[''],
            'or':['mPING', 'mping'],
            'not':[],
            'type': 'gen'
        },
        'FireWX Nest': {
            'and':[''],
            'or':['firewx'],
            'not':[],
            'type': 'anl'
        },
        'SPC Outlook Area': {
            'and':[''],
            'or':['spc_otlk'],
            'not':[],
            'type': 'gen'
        },
        'CCPA': {
            'and':[''],
            'or':['ccpa'],
            'not':[],
            'type': 'gen'
        },
        'MRMS': {
            'and':[''],
            'or':['mrms'],
            'not':[],
            'type': 'gen'
        },
        'NAM Nest Forecast': {
            'and':['nam', 'nest'],
            'or':[''],
            'not':[],
            'type': 'fcst'
        },
        'HRRR Forecast': {
            'and':['hrrr'],
            'or':[''],
            'not':[],
            'type': 'fcst'
        },
        'HiRes Window ARW Forecast': {
            'and':['hiresw','arw'],
            'or':[''],
            'not':['mem2'],
            'type': 'fcst'
        },
        'HiRes Window ARW2 Forecast': {
            'and':['hiresw','arw','mem2'],
            'or':[''],
            'not':[],
            'type': 'fcst'
        },
        'HiRes Window FV3 Forecast': {
            'and':['hiresw','fv3'],
            'or':[''],
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

