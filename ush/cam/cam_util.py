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
import glob
from datetime import datetime, timedelta as td

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
        print("FATAL ERROR: "+''.join(run_command.args)+" gave return code "
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

def get_completed_jobs(completed_jobs_file):
    completed_jobs = set()
    if os.path.exists(completed_jobs_file):
        with open(completed_jobs_file, 'r') as f:
            completed_jobs = set(f.read().splitlines())
    return completed_jobs

def mark_job_completed(completed_jobs_file, job_name, job_type=""):
    with open(completed_jobs_file, 'a') as f:
        if job_type:
            f.write(job_type + "_" + job_name + "\n")
        else:
            f.write(job_name + "\n")

def copy_data_to_restart(data_dir, restart_dir, met_tool=None, net=None, 
                         run=None, step=None, model=None, vdate=None, vhr=None, 
                         verif_case=None, verif_type=None, vx_mask=None, 
                         job_type=None, var_name=None, vhour=None, 
                         fhr_start=None, fhr_end=None, fhr_incr=None, 
                         njob=None, acc=None, nbrhd=None):
    sub_dirs = []
    copy_files = []
    if met_tool == "ascii2nc":
        check_if_none = [
            data_dir, restart_dir, verif_case, verif_type, vx_mask, met_tool, 
            vdate, vhour
        ]
        if any([var is None for var in check_if_none]):
            e = (f"FATAL ERROR: None encountered as an argument while copying"
                 + f" {met_tool} METplus output to COMOUT directory.")
            raise TypeError(e)
        sub_dirs.append(os.path.join(
            'METplus_output',
            verif_type, 
            vx_mask, 
            met_tool, 
        ))
        copy_files.append(f'{verif_type}.{vdate}{vhour}.nc')
    elif met_tool == 'genvxmask':
        check_if_none = [
            data_dir, restart_dir, verif_case, verif_type, vx_mask, met_tool, 
            vdate, vhour, fhr_start, fhr_end, fhr_incr
        ]
        if any([var is None for var in check_if_none]):
            e = (f"FATAL ERROR: None encountered as an argument while copying"
                 + f" {met_tool} METplus output to COMOUT directory.")
            raise TypeError(e)
        sub_dirs.append(os.path.join(
            'METplus_output',
            verif_type,
            met_tool,
            f'{vx_mask}.{vdate}',
        ))
        for fhr in np.arange(int(fhr_start), int(fhr_end), int(fhr_incr)):
            copy_files.append(f'{vx_mask}_t{vhour}z_f{str(fhr).zfill(2)}.nc')
    elif met_tool == 'grid_stat':
        if verif_case == "snowfall":
            check_if_none = [
                data_dir, restart_dir, verif_case, verif_type, met_tool, 
                vdate, vhour, fhr_start, fhr_end, fhr_incr, model, var_name, 
                acc, nbrhd
            ]
            if any([var is None for var in check_if_none]):
                e = (f"FATAL ERROR: None encountered as an argument while copying"
                     + f" {met_tool} METplus output to COMOUT directory.")
                raise TypeError(e)
            sub_dirs.append(os.path.join(
                'METplus_output',
                verif_type,
                met_tool,
                f'{model}.{vdate}'
            ))
            for fhr in np.arange(int(fhr_start), int(fhr_end), int(fhr_incr)):
                copy_files.append(
                    f'{met_tool}_{model}_{var_name}*{acc}H_{str(verif_type).upper()}_NBRHD{nbrhd}*_'
                    + f'{str(fhr).zfill(2)}0000L_{vdate}_{vhour}0000V.stat'
                )
        else:
            check_if_none = [
                data_dir, restart_dir, verif_case, verif_type, met_tool, 
                vdate, vhour, fhr_start, fhr_end, fhr_incr, model, acc, nbrhd
            ]
            if any([var is None for var in check_if_none]):
                e = (f"FATAL ERROR: None encountered as an argument while copying"
                     + f" {met_tool} METplus output to COMOUT directory.")
                raise TypeError(e)
            sub_dirs.append(os.path.join(
                'METplus_output',
                verif_type,
                met_tool,
                f'{model}.{vdate}'
            ))
            for fhr in np.arange(int(fhr_start), int(fhr_end), int(fhr_incr)):
                copy_files.append(
                    f'{met_tool}_{model}_*_{acc}H_{str(verif_type).upper()}_NBRHD{nbrhd}*_'
                    + f'{str(fhr).zfill(2)}0000L_{vdate}_{vhour}0000V.stat'
                )
    elif met_tool == 'merged_ptype':
        check_if_none = [
            data_dir, restart_dir, verif_case, verif_type, vx_mask, met_tool, 
            vdate, vhour, fhr_start, fhr_end, fhr_incr, model, njob
        ]
        if any([var is None for var in check_if_none]):
            e = (f"FATAL ERROR: None encountered as an argument while copying"
                 + f" {met_tool} output to COMOUT directory.")
            raise TypeError(e)
        sub_dirs.append(os.path.join(
            'data',
            model,
            met_tool,
        ))
        for fhr in np.arange(int(fhr_start), int(fhr_end), int(fhr_incr)):
            vdt = datetime.strptime(f'{vdate}{vhour}', '%Y%m%d%H')
            idt = vdt - td(hours=int(fhr))
            idate = idt.strftime('%Y%m%d')
            ihour = idt.strftime('%H')
            copy_files.append(
                f'{met_tool}_{verif_type}_{vx_mask}_job{njob}_'
                + f'init{idate}{ihour}_fhr{str(fhr).zfill(2)}.nc'
            )
    elif met_tool == 'pb2nc':
        check_if_none = [
            data_dir, restart_dir, verif_case, verif_type, vx_mask, met_tool, 
            vdate, vhour
        ]
        if any([var is None for var in check_if_none]):
            e = (f"FATAL ERROR: None encountered as an argument while copying"
                 + f" {met_tool} METplus output to COMOUT directory.")
            raise TypeError(e)
        sub_dirs.append(os.path.join(
            'METplus_output',
            verif_type,
            vx_mask,
            met_tool,
        ))
        copy_files.append(f'prepbufr.*.{vdate}{vhour}.nc')
    elif met_tool == 'pcp_combine':
        if verif_case == "snowfall":
            check_if_none = [
                data_dir, restart_dir, verif_case, verif_type, vx_mask, met_tool, 
                vdate, vhour, fhr_start, fhr_end, fhr_incr, model, var_name, acc
            ]
            if any([var is None for var in check_if_none]):
                e = (f"FATAL ERROR: None encountered as an argument while copying"
                     + f" {met_tool} METplus output to COMOUT directory.")
                raise TypeError(e)
            for fhr in np.arange(int(fhr_start), int(fhr_end), int(fhr_incr)):
                vdt = datetime.strptime(f'{vdate}{vhour}', '%Y%m%d%H')
                idt = vdt - td(hours=int(fhr))
                idate = idt.strftime('%Y%m%d')
                ihour = idt.strftime('%H')
                sub_dirs.append(os.path.join(
                    'METplus_output',
                    verif_type,
                    met_tool,
                ))
                copy_files.append(
                    f'{model}.{var_name}.init{idate}.t{ihour}z.f{str(fhr).zfill(3)}.a{acc}h.{vx_mask}.nc'
                )
        else:
            check_if_none = [
                data_dir, restart_dir, verif_case, verif_type, vx_mask, met_tool, 
                vdate, vhour, fhr_start, fhr_end, fhr_incr, model, acc
            ]
            if any([var is None for var in check_if_none]):
                e = (f"FATAL ERROR: None encountered as an argument while copying"
                     + f" {met_tool} METplus output to COMOUT directory.")
                raise TypeError(e)
            for fhr in np.arange(int(fhr_start), int(fhr_end), int(fhr_incr)):
                vdt = datetime.strptime(f'{vdate}{vhour}', '%Y%m%d%H')
                idt = vdt - td(hours=int(fhr))
                idate = idt.strftime('%Y%m%d')
                ihour = idt.strftime('%H')
                sub_dirs.append(os.path.join(
                    'METplus_output',
                    verif_type,
                    met_tool,
                ))
                copy_files.append(
                    f'{model}.init{idate}.t{ihour}z.f{str(fhr).zfill(3)}.a{acc}h.{vx_mask}.nc'
                )
    elif met_tool == 'point_stat':
        check_if_none = [
            data_dir, restart_dir, verif_case, verif_type, vx_mask, met_tool, 
            vdate, vhour, fhr_start, fhr_end, fhr_incr, model, var_name
        ]
        if any([var is None for var in check_if_none]):
            e = (f"FATAL ERROR: None encountered as an argument while copying"
                 + f" {met_tool} METplus output to COMOUT directory.")
            raise TypeError(e)
        sub_dirs.append(os.path.join(
            'METplus_output',
            verif_type,
            met_tool,
            f'{model}.{vdate}'
        ))
        for fhr in np.arange(int(fhr_start), int(fhr_end), int(fhr_incr)):
            copy_files.append(
                f'{met_tool}_{model}_{vx_mask}_{var_name}_OBS*_{str(fhr).zfill(2)}0000L_{vdate}_'
                + f'{vhour}0000V.stat'
            )
    elif met_tool == 'regrid_data_plane':
        check_if_none = [
            data_dir, restart_dir, verif_case, verif_type, vx_mask, met_tool, 
            vdate, vhour, fhr_start, fhr_end, fhr_incr, model, njob
        ]
        if any([var is None for var in check_if_none]):
            e = (f"FATAL ERROR: None encountered as an argument while copying"
                 + f" {met_tool} METplus output to COMOUT directory.")
            raise TypeError(e)
        sub_dirs.append(os.path.join(
            'METplus_output',
            verif_type,
            met_tool,
            f'{model}.{vdate}'
        ))
        for fhr in np.arange(int(fhr_start), int(fhr_end), int(fhr_incr)):
            copy_files.append(
                f'{met_tool}_{model}_t{vhour}z_{verif_type}_{vx_mask}_job{njob}_'
                + f'fhr{str(fhr).zfill(2)}.nc'
            )
    elif met_tool == 'stat_analysis':
        if job_type == 'gather':
            check_if_none = [
                data_dir, restart_dir, verif_case, verif_type, met_tool, vdate, 
                net, step, model, run 
            ]
            if any([var is None for var in check_if_none]):
                e = (f"FATAL ERROR: None encountered as an argument while copying"
                     + f" {met_tool} METplus output to COMOUT directory.")
                raise TypeError(e)
            sub_dirs.append(os.path.join(
                'METplus_output',
                'gather_small',
                met_tool,
                f'{model}.{vdate}'
            ))
            copy_files.append(
                f'{net}.{step}.{model}.{run}.{verif_case}.{verif_type}'
                + f'.v{vdate}.stat'
            )
        elif job_type == 'gather2':
            check_if_none = [
                data_dir, restart_dir, verif_case, met_tool, vdate, net, step, 
                model, run, vhr
            ]
            if any([var is None for var in check_if_none]):
                e = (f"FATAL ERROR: None encountered as an argument while copying"
                     + f" {met_tool} METplus output to COMOUT directory.")
                raise TypeError(e)
            sub_dirs.append(os.path.join(
                'METplus_output',
                met_tool,
                f'{model}.{vdate}'
            ))
            copy_files.append(
                f'{net}.{step}.{model}.{run}.{verif_case}.v{vdate}.c{vhr}z.stat'
            )
    for sub_dir in sub_dirs:
        for copy_file in copy_files:
            origin_path = os.path.join(
                data_dir, verif_case, sub_dir, copy_file
            )
            dest_path = os.path.join(restart_dir, sub_dir)
            if not glob.glob(origin_path):
                continue
            if not os.path.exists(dest_path):
                print(f"FATAL ERROR: Could not copy METplus output to COMOUT directory"
                      + f" {dest_path} because the path does not already exist.")
                continue
            if len(glob.glob(origin_path)) == len(glob.glob(os.path.join(dest_path, copy_file))):
                print(f"Not copying restart files to restart_directory"
                      + f" {dest_path} because they already exist.")
            else:
                run_shell_command(
                    ['cpreq', '-rpv', origin_path, os.path.join(dest_path,'.')]
                )

