#!/usr/bin/env python3
# =============================================================================
#
# NAME: mesoscale_util.py
# CONTRIBUTOR(S): RS, roshan.shrestha@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
#                 Mallory Row, mallory.row@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
#                 Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Various Utilities for EVS MESOSCALE Verification
# 
# =============================================================================

import os
import sys
from datetime import datetime, timedelta as td
import numpy as np
import glob
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
        'SPC Outlook Area': {
            'and':[''],
            'or':['spc_otlk'],
            'not':[],
            'type': 'gen'
        },
        'NAM': {
            'and':[''],
            'or':['nam'],
            'not':[],
            'type': 'fcst'
        },
        'RAP': {
            'and':[''],
            'or':['rap'],
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

def run_shell_commandc(command, capture_output=True):
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

def check_file(file_path):
    """! Check file exists and not zero size
         Args:
             file_path - full path to file (string)
         Returns:
             file_good - full call to METplus (boolean)
    """
    if os.path.exists(file_path):
        if os.path.getsize(file_path) > 0:
            file_good = True
        else:
            file_good = False
    else:
        file_good = False
    return file_good

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


def check_pstat_files(job_dict):
    """! Check for MET point_stat files

         Args:
             job_dict - dictionary containing settings
                        job is running with (strings)

         Returns:
             pstat_files_exist - if point_stat files
                                exist or not (boolean)
    """
    FHR_START = os.environ ['FHR_START']
    FHR_START2= str(FHR_START).zfill(2)
    model_stat_file_dir = os.path.join(
        job_dict['DATA'], job_dict['VERIF_CASE'],
        'METplus_output', job_dict['VERIF_TYPE'],'point_stat',
        job_dict['MODEL']+'.'+job_dict['VDATE']
    )

    pstat_file = os.path.join(
            model_stat_file_dir, 'point_stat_'+job_dict['MODEL']+
            '_'+job_dict['NEST']+'_'+job_dict['VAR_NAME']+
            '_OBS_*0000L_'+job_dict['VDATE']+'_'+job_dict['VHOUR']+'0000V.stat'
            )

    stat_file_list = glob.glob(pstat_file) 

    if len(stat_file_list) != 0:
        pstat_files_exist = True
    else:
        pstat_files_exist = False
    return pstat_files_exist



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
                    ['cp', '-rpv', origin_path, os.path.join(dest_path,'.')]
                )

def initalize_job_env_dict():
    """! This initializes a dictionary of environment variables and their
         values to be set for the job pulling from environment variables
         already set previously
         Args:

         Returns:
             job_env_dict - dictionary of job settings
    """
    os.environ['MET_TMP_DIR'] = os.path.join(os.environ['DATA'], 'tmp')
    job_env_var_list = [
        'machine', 'evs_ver', 'HOMEevs', 'FIXevs', 'USHevs', 'DATA',
        'NET', 'RUN', 'VERIF_CASE', 'STEP', 'COMPONENT', 'evs_run_mode',
        'COMROOT', 'COMIN', 'COMOUT', 'COMOUTsmall', 'COMOUTfinal', 'EVSIN',
        'METPLUS_PATH','LOG_MET_OUTPUT_TO_METPLUS', 'METPLUS_VERBOSITY',
        'MET_ROOT', 'MET_VERBOSITY',
        'MET_TMP_DIR', 'MODELNAME', 'JOB_GROUP'
    ]
    job_env_dict = {}
    for env_var in job_env_var_list:
        job_env_dict[env_var] = os.environ[env_var]
        if env_var in ['LOG_MET_OUTPUT_TO_METPLUS',
                       'METPLUS_VERBOSITY', 'MET_VERBOSITY']:
            job_env_dict[env_var.lower()] = os.environ[env_var]
    return job_env_dict

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
    conf_file = os.path.join(os.environ['PARMevs'], 'metplus_config', os.environ['STEP'],
                             os.environ['COMPONENT'], os.environ['VERIF_CASE'],
                             conf_file_name)
    if not os.path.exists(conf_file):
        print("ERROR: "+conf_file+" DOES NOT EXIST")
        sys.exit(1)
    metplus_cmd = run_metplus+' -c '+machine_conf+' -c '+conf_file
    return metplus_cmd

def precip_check_obs_input_output_files(job_dict):
    """! Check precip observation input and output files
         in COMOUT and DATA
         Args:
             job_dict - job dictionary
         Returns:
             all_input_file_exist  - if all expected
                                     input files exist
                                     (boolean)
             input_files_list      - list of input files
                                     (strings)
             all_COMOUT_file_exist - if all expected
                                     output COMOUT files
                                     exist (boolean)
             COMOUT_files_list     - list of output COMOUT
                                     files (strings)
             DATA_files_list       - list of output DATA
                                     files (strings)
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hour_start'],
        '%Y%m%d%H'
    )
    # Expected input file
    input_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['job_name'] in ['24hrCCPA', '03hrCCPA', '01hrCCPA']:
            nccpa_files = (
                int(job_dict['accum'])
                /int(job_dict['ccpa_file_accum'])
            )
            n = 1
            while n <= nccpa_files:
                nccpa_file = os.path.join(
                    job_dict['DATA'], 'data', 'ccpa', 
                    f"ccpa.accum{job_dict['ccpa_file_accum'].zfill(2)}hr.v"
                    +(valid_date_dt
                      -datetime.timedelta(hours=(n-1)
                                                 *int(job_dict['ccpa_file_accum'])))\
                    .strftime('%Y%m%d%H')
                )
                input_files_list.append(nccpa_file)
                n+=1
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        if job_dict['obs'] == 'ccpa':
            input_files_list.append(
                os.path.join(job_dict['COMOUT'],
                             f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                             job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                             "pcp_combine_ccpa_accum"
                             +f"{job_dict['accum']}hr_valid"
                             +f"{valid_date_dt:%Y%m%d%H}.nc")
            )
        elif job_dict['obs'] == 'mrms':
            input_files_list.append(
                os.path.join(job_dict['DATA'], 'data', job_dict['obs'],
                             f"{job_dict['area']}_MultiSensor_QPE_"
                             +f"{job_dict['accum']}H_Pass2_00.00_"
                             +f"{valid_date_dt:%Y%m%d}-"
                             +f"{valid_date_dt:%H%M%S}.grib2")
            )
    input_files_exist_list = []
    for input_file in input_files_list:
        if check_file(input_file):
            input_files_exist_list.append(True)
        else:
            input_files_exist_list.append(False)
    if all(x == True for x in input_files_exist_list) \
            and len(input_files_exist_list) > 0:
        all_input_file_exist = True
    else:
        all_input_file_exist = False
    # Expected output files (in COMOUT and DATA)
    COMOUT_files_list = []
    DATA_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['job_name'] in ['24hrCCPA', '03hrCCPA', '01hrCCPA']:
            file_name = ("pcp_combine_ccpa_accum"
                         +f"{job_dict['accum']}hr_valid"
                         +f"{valid_date_dt:%Y%m%d%H}.nc")
            COMOUT_files_list.append(
                os.path.join(job_dict['COMOUT'],
                             f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                             job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                             file_name)
            )
            DATA_files_list.append(
                os.path.join(job_dict['DATA'],
                             f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                             job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                             file_name)
            ) 
    COMOUT_files_exist_list = []
    for COMOUT_file in COMOUT_files_list:
        if check_file(COMOUT_file):
            COMOUT_files_exist_list.append(True)
        else:
            COMOUT_files_exist_list.append(False)
    if all(x == True for x in COMOUT_files_exist_list) \
            and len(COMOUT_files_exist_list) > 0:
        all_COMOUT_file_exist = True
    else:
        all_COMOUT_file_exist = False
    return (all_input_file_exist, input_files_list, \
            all_COMOUT_file_exist, COMOUT_files_list,
            DATA_files_list)


def precip_check_model_input_output_files(job_dict):
    """! Check precip model input and output files
         in COMOUT and DATA
         Args:
             job_dict - job dictionary
         Returns:
             all_input_file_exist  - if all expected
                                     input files exist
                                     (boolean)
             input_files_list      - list of input files
                                     (strings)
             all_COMOUT_file_exist - if all expected
                                     output COMOUT files
                                     exist (boolean)
             COMOUT_files_list     - list of output COMOUT
                                     files (strings)
             DATA_files_list       - list of output DATA
                                     files (strings)
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hour_start'],
        '%Y%m%d%H'
    )
    init_date_dt = (valid_date_dt
                    - datetime.timedelta(hours=int(job_dict['fcst_hour'])))
    # Expected input file
    input_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['pcp_combine_method'] == 'SUBTRACT':
            for fhr in [job_dict['fcst_hour'],
                        str(int(job_dict['fcst_hour'])
                            - int(job_dict['accum']))]:
                input_files_list.append(
                    os.path.join(job_dict['DATA'], 'data',
                                 job_dict['MODELNAME'],
                                 f"{job_dict['MODELNAME']}."
                                 +f"{job_dict['area']}."
                                 +f"init{init_date_dt:%Y%m%d%H}."
                                 +f"f{fhr.zfill(3)}")
                )
        elif job_dict['pcp_combine_method'] == 'SUM':
            naccum_files = int(job_dict['accum'])/int(job_dict['input_accum'])
            n = 1 
            while n <= naccum_files:
                naccum_file = os.path.join(
                    job_dict['DATA'], 'data', job_dict['MODELNAME'],
                    f"{job_dict['MODELNAME']}.{job_dict['area']}."
                    +f"init{init_date_dt:%Y%m%d%H}.f"
                    +str(int(job_dict['fcst_hour'])
                         -((n-1)*int(job_dict['input_accum']))).zfill(3)
                )
                input_files_list.append(naccum_file)
                n+=1
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        input_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         f"pcp_combine_{job_dict['MODELNAME']}_"
                         +f"accum{job_dict['accum']}hr_"
                         +f"{job_dict['area']}_"
                         +f"init{init_date_dt:%Y%m%d%H}_"
                         +f"fhr{job_dict['fcst_hour'].zfill(3)}.nc")
        )
    input_files_exist_list = []
    for input_file in input_files_list:
        if check_file(input_file):
            input_files_exist_list.append(True)
        else:
            input_files_exist_list.append(False)
    if all(x == True for x in input_files_exist_list) \
            and len(input_files_exist_list) > 0:
        all_input_file_exist = True
    else:
        all_input_file_exist = False
    # Expected output files (in COMOUT and DATA)
    COMOUT_files_list = []
    DATA_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        file_name = (f"pcp_combine_{job_dict['MODELNAME']}_"
                     +f"accum{job_dict['accum']}hr_"
                     +f"{job_dict['area']}_"
                     +f"init{init_date_dt:%Y%m%d%H}_"
                     +f"fhr{job_dict['fcst_hour'].zfill(3)}.nc")
        COMOUT_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
        DATA_files_list.append(
            os.path.join(job_dict['DATA'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        file_name = (f"grid_stat_{job_dict['job_name']}_"
                     f"{job_dict['fcst_hour'].zfill(2)}0000L_"
                     +f"{valid_date_dt:%Y%m%d_%H%M%S}V.stat")
        COMOUT_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
        DATA_files_list.append(
            os.path.join(job_dict['DATA'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
    COMOUT_files_exist_list = []
    for COMOUT_file in COMOUT_files_list:
        if check_file(COMOUT_file):
            COMOUT_files_exist_list.append(True)
        else:
            COMOUT_files_exist_list.append(False)
    if all(x == True for x in COMOUT_files_exist_list) \
            and len(COMOUT_files_exist_list) > 0:
        all_COMOUT_file_exist = True
    else:
        all_COMOUT_file_exist = False
    return (all_input_file_exist, input_files_list, \
            all_COMOUT_file_exist, COMOUT_files_list,
            DATA_files_list)

def snowfall_check_obs_input_output_files(job_dict):
    """! Check snowfall observation input and output files
         in COMOUT and DATA
         Args:
             job_dict - job dictionary
         Returns:
             all_input_file_exist  - if all expected
                                     input files exist
                                     (boolean)
             input_files_list      - list of input files
                                     (strings)
             all_COMOUT_file_exist - if all expected
                                     output COMOUT files
                                     exist (boolean)
             COMOUT_files_list     - list of output COMOUT
                                     files (strings)
             DATA_files_list       - list of output DATA
                                     files (strings)
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hour_start'],
        '%Y%m%d%H'
    )
    # Expected input file
    input_files_list = []
    if job_dict['JOB_GROUP'] == 'generate_stats':
        if job_dict['obs'] == 'nohrsc':
            input_files_list.append(
                os.path.join(job_dict['DATA'], 'data', 'nohrsc',
                             f"nohrsc.accum{job_dict['accum']}hr."
                             +f"v{valid_date_dt:%Y%m%d%H}")
            )
    input_files_exist_list = []
    for input_file in input_files_list:
        if check_file(input_file):
            input_files_exist_list.append(True)
        else:
            input_files_exist_list.append(False)
    if all(x == True for x in input_files_exist_list) \
            and len(input_files_exist_list) > 0:
        all_input_file_exist = True
    else:
        all_input_file_exist = False
    # Expected output files (in COMOUT and DATA)
    COMOUT_files_list = []
    DATA_files_list = []
    #
    COMOUT_files_exist_list = []
    for COMOUT_file in COMOUT_files_list:
        if check_file(COMOUT_file):
            COMOUT_files_exist_list.append(True)
        else:
            COMOUT_files_exist_list.append(False)
    if all(x == True for x in COMOUT_files_exist_list) \
            and len(COMOUT_files_exist_list) > 0:
        all_COMOUT_file_exist = True
    else:
        all_COMOUT_file_exist = False
    return (all_input_file_exist, input_files_list, \
            all_COMOUT_file_exist, COMOUT_files_list,
            DATA_files_list)

def snowfall_check_model_input_output_files(job_dict):
    """! Check snowfall model input and output files
         in COMOUT and DATA
         Args:
             job_dict - job dictionary
         Returns:
             all_input_file_exist  - if all expected
                                     input files exist
                                     (boolean)
             input_files_list      - list of input files
                                     (strings)
             all_COMOUT_file_exist - if all expected
                                     output COMOUT files
                                     exist (boolean)
             COMOUT_files_list     - list of output COMOUT
                                     files (strings)
             DATA_files_list       - list of output DATA
                                     files (strings)
    """
    valid_date_dt = datetime.datetime.strptime(
        job_dict['DATE']+job_dict['valid_hour_start'],
        '%Y%m%d%H'
    )
    init_date_dt = (valid_date_dt
                    - datetime.timedelta(hours=int(job_dict['fcst_hour'])))
    # Expected input file
    input_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        if job_dict['pcp_combine_method'] in ['SUBTRACT', 'USER_DEFINED']:
            for fhr in [job_dict['fcst_hour'],
                        str(int(job_dict['fcst_hour'])
                            - int(job_dict['accum']))]:
                input_files_list.append(
                    os.path.join(job_dict['DATA'], 'data',
                                 job_dict['MODELNAME'],
                                 f"{job_dict['MODELNAME']}."
                                 +f"init{init_date_dt:%Y%m%d%H}."
                                 +f"f{fhr.zfill(3)}")
                )
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        input_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         f"pcp_combine_{job_dict['MODELNAME']}_"
                         +f"accum{job_dict['accum']}hr_"
                         +f"{job_dict['snow_var']}_"
                         +f"init{init_date_dt:%Y%m%d%H}_"
                         +f"fhr{job_dict['fcst_hour'].zfill(3)}.nc")
        )
    input_files_exist_list = []
    for input_file in input_files_list:
        if check_file(input_file):
            input_files_exist_list.append(True)
        else:
            input_files_exist_list.append(False)
    if all(x == True for x in input_files_exist_list) \
            and len(input_files_exist_list) > 0:
        all_input_file_exist = True
    else:
        all_input_file_exist = False
    # Expected output files (in COMOUT and DATA)
    COMOUT_files_list = []
    DATA_files_list = []
    if job_dict['JOB_GROUP'] == 'assemble_data':
        file_name = (f"pcp_combine_{job_dict['MODELNAME']}_"
                     +f"accum{job_dict['accum']}hr_"
                     +f"{job_dict['snow_var']}_"
                     +f"init{init_date_dt:%Y%m%d%H}_"
                     +f"fhr{job_dict['fcst_hour'].zfill(3)}.nc")
        COMOUT_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
        DATA_files_list.append(
            os.path.join(job_dict['DATA'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
    elif job_dict['JOB_GROUP'] == 'generate_stats':
        file_name = (f"grid_stat_{job_dict['job_name']}_"
                     f"{job_dict['fcst_hour'].zfill(2)}0000L_"
                     +f"{valid_date_dt:%Y%m%d_%H%M%S}V.stat")
        COMOUT_files_list.append(
            os.path.join(job_dict['COMOUT'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
        DATA_files_list.append(
            os.path.join(job_dict['DATA'],
                         f"{job_dict['RUN']}.{valid_date_dt:%Y%m%d}",
                         job_dict['MODELNAME'], job_dict['VERIF_CASE'],
                         file_name)
        )
    COMOUT_files_exist_list = []
    for COMOUT_file in COMOUT_files_list:
        if check_file(COMOUT_file):
            COMOUT_files_exist_list.append(True)
        else:
            COMOUT_files_exist_list.append(False)
    if all(x == True for x in COMOUT_files_exist_list) \
            and len(COMOUT_files_exist_list) > 0:
        all_COMOUT_file_exist = True
    else:
        all_COMOUT_file_exist = False
    return (all_input_file_exist, input_files_list, \
            all_COMOUT_file_exist, COMOUT_files_list,
            DATA_files_list)
# Construct a file name given a template
def fname_constructor(template_str, IDATE="YYYYmmdd", IHOUR="HH",
                      VDATE="YYYYmmdd", VHOUR="HH", VDATEHOUR="YYYYmmddHH",
                      VDATEm1H="YYYYmmdd", VDATEHOURm1H="YYYYmmddHH",
                      FHR="HH", LVL="0", OFFSET="HH"):
    template_str = template_str.replace('{IDATE}', IDATE)
    template_str = template_str.replace('{IHOUR}', IHOUR)
    template_str = template_str.replace('{VDATE}', VDATE)
    template_str = template_str.replace('{VHOUR}', VHOUR)
    template_str = template_str.replace('{VDATEHOUR}', VDATEHOUR)
    template_str = template_str.replace('{VDATEm1H}', VDATEm1H)
    template_str = template_str.replace('{VDATEHOURm1H}', VDATEHOURm1H)
    template_str = template_str.replace('{FHR}', FHR)
    template_str = template_str.replace('{LVL}', LVL)
    template_str = template_str.replace('{OFFSET}', OFFSET)
    return template_str

# Create a list of prepbufr file paths
def get_prepbufr_templates(indir, vdates, paths=[], obsname='both', already_preprocessed=False):
    '''
        indir  - (str) Input directory for prepbufr file data
        vdates - (datetime object) List of datetimes used to fill templates
        paths  - (list of str) list of paths to append the prepbufr paths to 
                 Default is empty.
    '''
    prepbufr_templates = []
    prepbufr_paths = []
    for v, vdate in enumerate(vdates):
        vh = vdate.strftime('%H')
        vd = vdate.strftime('%Y%m%d')
        if vh in ['00', '03', '06', '09', '12', '15', '18', '21']:
            if vh in ['03', '09', '15', '21']:
                offsets = ['03']
            elif vh in ['00', '06', '12', '18']:
                offsets = ['00', '06']
                if obsname in ['both', 'raob']:
                    if not already_preprocessed:
                        prepbufr_templates.append(os.path.join(
                            indir, 
                            'gdas.{VDATE}',
                            '{VHOUR}',
                            'atmos',
                            'gdas.t{VHOUR}z.prepbufr'
                        ))
                    else:
                        prepbufr_templates.append(os.path.join(
                            indir, 
                            'gdas.t{VHOUR}z.prepbufr'
                        ))
            for offset in offsets:
                use_vdate = vdate + td(hours=int(offset))
                use_vd = use_vdate.strftime('%Y%m%d')
                use_vh = use_vdate.strftime('%H')
                if obsname in ['both', 'metar']:
                    if not already_preprocessed:
                        template = os.path.join(
                            indir, 
                            'nam.{VDATE}',
                            'nam.t{VHOUR}z.prepbufr.tm{OFFSET}'
                        )
                    else:
                        template = os.path.join(
                            indir, 
                            'nam.t{VHOUR}z.prepbufr.tm{OFFSET}'
                        )
                    prepbufr_paths.append(fname_constructor(
                        template, VDATE=use_vd, VHOUR=use_vh, OFFSET=offset
                    ))
        for template in prepbufr_templates:
            prepbufr_paths.append(fname_constructor(
                template, VDATE=vd, VHOUR=vh
            ))
    return np.concatenate((paths, np.unique(prepbufr_paths)))

def preprocess_prepbufr(indir, fname, workdir, outdir, subsets):
    if os.path.exists(os.path.join(outdir, fname)):
        print(f"{fname} exists in {outdir} so we can skip preprocessing.")
    else:
        wd = os.getcwd()
        os.chdir(workdir)
        if os.path.isfile(os.path.join(indir, fname)):
            run_shell_command(
                [
                    os.path.join(os.environ['bufr_ROOT'], 'bin', 'split_by_subset'), 
                    os.path.join(indir, fname)
                ]
            )
            if all([os.path.isfile(subset) for subset in subsets]):
                run_shell_command(
                    np.concatenate((
                        ['cat'], subsets, ['>>', os.path.join(outdir, fname)]
                    ))
                )
            else:
                raise FileNotFoundError(
                    f"The following prepbufr subsets do not exist in {workdir}: " 
                    + ', '.join([subset for subset in subsets if not os.path.isfile(subset)])
                    + ". Cannot concatenate subsets."
                )
        else:
            print(
                "WARNING: The following file does not exist: "
                + f"{os.path.join(indir, fname)}."
                + " Skipping split by subset."
            )
        os.chdir(wd)

# Create a list of ccpa file paths
def get_ccpa_qpe_templates(indir, vdates, obs_acc, target_acc, nest, paths=[]):
    '''
        indir..... - (str) Input directory for prepbufr file data
        vdates.... - (datetime object) List of datetimes used to fill templates
        obs_acc... - (str) precip accumulation interval of ccpa files in hours
        target_acc - (str) target precip accumulation interval of combined
                     ccpa files in hours
        nest...... - (str) domain used to find ccpa files
        paths..... - (list of str) list of paths to append the prepbufr paths to 
                     Default is empty.
    '''
    ccpa_paths = []
    for v, vdate in enumerate(vdates):
        vh = vdate.strftime('%H')
        vd = vdate.strftime('%Y%m%d')
        if int(target_acc) == 1:
            if int(obs_acc) == 1:
                offsets = [0]
            else:
                raise ValueError(f"obs_acc is not valid: \"{obs_acc}\"")
        elif int(target_acc) == 3:
            if int(obs_acc) == 1:
                offsets = [0, 1, 2]
            elif int(obs_acc) == 3:
                offsets = [0]
            else:
                raise ValueError(f"obs_acc is not valid: \"{obs_acc}\"")
        elif int(target_acc) == 24:
            if int(obs_acc) == 1:
                offsets = [
                    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
                    11, 12, 13, 14, 15, 16, 17, 18 , 19, 20, 
                    21, 22, 23
                ]
            elif int(obs_acc) == 3:
                offsets = [0, 3, 6, 9, 12, 15, 18, 21]
            elif int(obs_acc) == 24:
                offsets = [0]
            else:
                raise ValueError(f"obs_acc is not valid: \"{obs_acc}\"")
        else:
            raise ValueError(f"target_acc is not valid: \"{target_acc}\"")
        for offset in offsets:
            use_vdate = vdate - td(hours=int(offset))
            use_vd = use_vdate.strftime('%Y%m%d')
            use_vh = use_vdate.strftime('%H')
            template = os.path.join(
                indir, 
                'ccpa.{VDATE}',
                'ccpa.t{VHOUR}z.' + f'{obs_acc}h.hrap.{nest}.gb2'
            )
            ccpa_paths.append(fname_constructor(
                template, VDATE=use_vd, VHOUR=use_vh
            ))
    return np.concatenate((paths, np.unique(ccpa_paths)))

# Create a list of mrms file paths
def get_mrms_qpe_templates(indir, vdates, obs_acc, target_acc, nest, paths=[]):
    '''
        indir..... - (str) Input directory for prepbufr file data
        vdates.... - (datetime object) List of datetimes used to fill templates
        obs_acc... - (str) precip accumulation interval of mrms files in hours
        target_acc - (str) target precip accumulation interval of combined
                     mrms files in hours
        nest...... - (str) domain used to find mrms files
        paths..... - (list of str) list of paths to append the prepbufr paths to 
                     Default is empty.
    '''
    mrms_paths = []
    for v, vdate in enumerate(vdates):
        vh = vdate.strftime('%H')
        vd = vdate.strftime('%Y%m%d')
        if int(target_acc) == 1:
            if int(obs_acc) == 1:
                offsets = [0]
            else:
                raise ValueError(f"obs_acc is not valid: \"{obs_acc}\"")
        elif int(target_acc) == 3:
            if int(obs_acc) == 1:
                offsets = [0, 1, 2]
            elif int(obs_acc) == 3:
                offsets = [0]
            else:
                raise ValueError(f"obs_acc is not valid: \"{obs_acc}\"")
        elif int(target_acc) == 24:
            if int(obs_acc) == 1:
                offsets = [
                    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
                    11, 12, 13, 14, 15, 16, 17, 18 , 19, 20, 
                    21, 22, 23
                ]
            elif int(obs_acc) == 3:
                offsets = [0, 3, 6, 9, 12, 15, 18, 21]
            elif int(obs_acc) == 24:
                offsets = [0]
            else:
                raise ValueError(f"obs_acc is not valid: \"{obs_acc}\"")
        else:
            raise ValueError(f"target_acc is not valid: \"{target_acc}\"")
        for offset in offsets:
            use_vdate = vdate - td(hours=int(offset))
            use_vd = use_vdate.strftime('%Y%m%d')
            use_vh = use_vdate.strftime('%H')
            template = os.path.join(
                indir, 
                'mrms.{VDATE}',
                'mrms.t{VHOUR}z.' + f'{obs_acc}h.{nest}.gb2'
            )
            mrms_paths.append(fname_constructor(
                template, VDATE=use_vd, VHOUR=use_vh
            ))
    return np.concatenate((paths, np.unique(mrms_paths)))

# Create a list of nohrsc file paths
def get_nohrsc_qpe_templates(indir, vdates, obs_acc, target_acc, nest, paths=[]):
    '''
        indir..... - (str) Input directory for nohrsc file data
        vdates.... - (datetime object) List of datetimes used to fill templates
        obs_acc... - (str) snow accumulation interval of nohrsc files in hours
        target_acc - (str) target snow accumulation interval of combined
                     nohrsc files in hours
        nest...... - (str) domain used to find nohrsc files
        paths..... - (list of str) list of paths to append the nohrsc paths to 
                     Default is empty.
    '''
    nohrsc_paths = []
    for v, vdate in enumerate(vdates):
        vh = vdate.strftime('%H')
        vd = vdate.strftime('%Y%m%d')
        if int(target_acc) == 6:
            if int(obs_acc) == 6:
                offsets = [0]
            else:
                raise ValueError(f"obs_acc is not valid: \"{obs_acc}\"")
        elif int(target_acc) == 24:
            if int(obs_acc) == 6:
                offsets = [0, 6, 12, 18]
            elif int(obs_acc) == 24:
                offsets = [0]
            else:
                raise ValueError(f"obs_acc is not valid: \"{obs_acc}\"")
        else:
            raise ValueError(f"target_acc is not valid: \"{target_acc}\"")
        for offset in offsets:
            use_vdate = vdate - td(hours=int(offset))
            use_vd = use_vdate.strftime('%Y%m%d')
            use_vh = use_vdate.strftime('%H')
            template = os.path.join(
                indir, 
                '{VDATE}', 'wgrbbul', 'nohrsc_snowfall',
                f'sfav2_CONUS_{int(obs_acc)}h_' + '{VDATE}{VHOUR}_grid184.grb2'
            )
            nohrsc_paths.append(fname_constructor(
                template, VDATE=use_vd, VHOUR=use_vh
            ))
    return np.concatenate((paths, np.unique(nohrsc_paths)))

# Return a list of missing ccpa files needed to create "target_acc"
def check_ccpa_files(indir, vdate, obs_acc, target_acc, nest):
    '''
        indir..... - (str) Input directory for prepbufr file data
        vdate..... - (datetime object) datetime used to fill templates
        obs_acc... - (str) precip accumulation interval of ccpa files in hours
        target_acc - (str) target precip accumulation interval of combined
                     ccpa files in hours
        nest...... - (str) domain used to find ccpa files
    '''
    paths = get_ccpa_qpe_templates(indir, [vdate], obs_acc, target_acc, nest)
    return [path for path in paths if not os.path.exists(path)]

# Return a list of missing mrms files needed to create "target_acc"
def check_mrms_files(indir, vdate, obs_acc, target_acc, nest):
    '''
        indir..... - (str) Input directory for prepbufr file data
        vdate..... - (datetime object) datetime used to fill templates
        obs_acc... - (str) precip accumulation interval of mrms files in hours
        target_acc - (str) target precip accumulation interval of combined
                     mrms files in hours
        nest...... - (str) domain used to find mrms files
    '''
    paths = get_mrms_qpe_templates(indir, [vdate], obs_acc, target_acc, nest)
    return [path for path in paths if not os.path.exists(path)]

# Return a list of missing nohrsc files needed to create "target_acc"
def check_nohrsc_files(indir, vdate, obs_acc, target_acc, nest):
    '''
        indir..... - (str) Input directory for prepbufr file data
        vdate..... - (datetime object) datetime used to fill templates
        obs_acc... - (str) precip accumulation interval of nohrsc files in hours
        target_acc - (str) target precip accumulation interval of combined
                     nohrsc files in hours
        nest...... - (str) domain used to find nohrsc files
    '''
    paths = get_nohrsc_qpe_templates(indir, [vdate], obs_acc, target_acc, nest)
    return [path for path in paths if not os.path.exists(path)]

# Return the obs accumulation interval needed to create target_acc, based on
# available ccpa files
def get_ccpa_accums(indir, vdate, target_acc, nest):
    '''
        indir..... - (str) Input directory for prepbufr file data
        vdate..... - (datetime object) datetime used to fill templates
        target_acc - (str) target precip accumulation interval of combined
                     ccpa files in hours
        nest...... - (str) domain used to find ccpa files
    '''
    if int(target_acc) == 1:
        # check 1-h obs
        obs_acc = "01"
        missing_ccpa = check_ccpa_files(indir, vdate, obs_acc, target_acc, nest)
        if missing_ccpa:
            return None
        else:
            return obs_acc
    elif int(target_acc) == 3:
        # check 3-h obs
        obs_acc = "03"
        missing_ccpa = check_ccpa_files(indir, vdate, obs_acc, target_acc, nest)
        if missing_ccpa:
            # check 1-h obs
            obs_acc = "01"
            missing_ccpa = check_ccpa_files(indir, vdate, obs_acc, target_acc, nest)
            if missing_ccpa:
                return None
            else:
                return obs_acc
        else:
            return obs_acc
    elif int(target_acc) == 24:

        # check 24-h obs
        obs_acc = "24"
        missing_ccpa = check_ccpa_files(indir, vdate, obs_acc, target_acc, nest)
        if missing_ccpa:
            # check 3-h obs
            obs_acc = "03"
            missing_ccpa = check_ccpa_files(indir, vdate, obs_acc, target_acc, nest)
            if missing_ccpa:
                # check 1-h obs
                obs_acc = "01"
                missing_ccpa = check_ccpa_files(indir, vdate, obs_acc, target_acc, nest)
                if missing_ccpa:
                    return None
                else:
                    return obs_acc
            else:
                return obs_acc
        else:
            return obs_acc
    else:
        raise ValueError(f"Invalid target_acc: \"{target_acc}\"")

# Return the obs accumulation interval needed to create target_acc, based on
# available mrms files
def get_mrms_accums(indir, vdate, target_acc, nest):
    '''
        indir..... - (str) Input directory for prepbufr file data
        vdate..... - (datetime object) datetime used to fill templates
        target_acc - (str) target precip accumulation interval of combined
                     mrms files in hours
        nest...... - (str) domain used to find mrms files
    '''
    if int(target_acc) == 1:
        # check 1-h obs
        obs_acc = "01"
        missing_mrms = check_mrms_files(indir, vdate, obs_acc, target_acc, nest)
        if missing_mrms:
            return None
        else:
            return obs_acc
    elif int(target_acc) == 3:
        # check 3-h obs
        obs_acc = "03"
        missing_mrms = check_mrms_files(indir, vdate, obs_acc, target_acc, nest)
        if missing_mrms:
            # check 1-h obs
            obs_acc = "01"
            missing_mrms = check_mrms_files(indir, vdate, obs_acc, target_acc, nest)
            if missing_mrms:
                return None
            else:
                return obs_acc
        else:
            return obs_acc
    elif int(target_acc) == 24:

        # check 24-h obs
        obs_acc = "24"
        missing_mrms = check_mrms_files(indir, vdate, obs_acc, target_acc, nest)
        if missing_mrms:
            # check 3-h obs
            obs_acc = "03"
            missing_mrms = check_mrms_files(indir, vdate, obs_acc, target_acc, nest)
            if missing_mrms:
                # check 1-h obs
                obs_acc = "01"
                missing_mrms = check_mrms_files(indir, vdate, obs_acc, target_acc, nest)
                if missing_mrms:
                    return None
                else:
                    return obs_acc
            else:
                return obs_acc
        else:
            return obs_acc
    else:
        raise ValueError(f"Invalid target_acc: \"{target_acc}\"")

# Return the obs accumulation interval needed to create target_acc, based on
# available nohrsc files
def get_nohrsc_accums(indir, vdate, target_acc, nest):
    '''
        indir..... - (str) Input directory for prepbufr file data
        vdate..... - (datetime object) datetime used to fill templates
        target_acc - (str) target precip accumulation interval of combined
                     nohrsc files in hours
        nest...... - (str) domain used to find nohrsc files
    '''
    if int(target_acc) == 6:
        # check 6-h obs
        obs_acc = "06"
        missing_nohrsc = check_nohrsc_files(indir, vdate, obs_acc, target_acc, nest)
        if missing_nohrsc:
            return None
        else:
            return obs_acc
    elif int(target_acc) == 24:
        # check 24-h obs
        obs_acc = "24"
        missing_nohrsc = check_nohrsc_files(indir, vdate, obs_acc, target_acc, nest)
        if missing_nohrsc:
            # check 6-h obs
            obs_acc = "06"
            missing_nohrsc = check_nohrsc_files(indir, vdate, obs_acc, target_acc, nest)
            if missing_nohrsc:
                return None
            else:
                return obs_acc
        else:
            return obs_acc
    else:
        raise ValueError(f"Invalid target_acc: \"{target_acc}\"")

# Return the obs accumulation interval needed to create target_acc, based on
# available input files
def get_obs_accums(indir, vdate, target_acc, nest, obsname, job_type='reformat'):
    '''
        indir..... - (str) Input directory for obs file data
        vdate..... - (datetime object) datetime used to fill templates
        target_acc - (str) target precip accumulation interval of combined
                     obs files in hours
        nest...... - (str) domain used to find obs files
        obsname... - (str) name of input file dataset
    '''
    if obsname == "mrms":
        return get_mrms_accums(indir, vdate, target_acc, nest)
    elif obsname == "ccpa":
        return get_ccpa_accums(indir, vdate, target_acc, nest)
    elif obsname == "nohrsc":
        return get_nohrsc_accums(indir, vdate, target_acc, nest)
    else:
        raise ValueError(f"Invalid obsname: \"{obsname}\"")

# Return availability of obs needed for job
def get_obs_avail(indir, vdate, nest, obsname):
    '''
        indir..... - (str) Input directory for obs file data
        vdate..... - (datetime object) datetime used to fill templates
        nest...... - (str) domain used to find obs files
        obsname... - (str) name of input file dataset
    '''
    if obsname in ["raob", "metar"]:
        paths = get_prepbufr_templates(indir, [vdate], obsname=obsname, already_preprocessed=True)
        if paths.size > 0:
            return all([os.path.exists(fname) for fname in paths])
        else:
            return False
    else:
        raise ValueError(f"Invalid obsname: \"{obsname}\"")
