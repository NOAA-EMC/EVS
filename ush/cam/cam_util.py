#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_util.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Various Utilities for EVS CAM Verification
# 
# =============================================================================

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
