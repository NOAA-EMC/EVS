#!/usr/bin/env python3
###############################################################################
#
# Name:          df_preprocessing.py
# Contact(s):    Marcel Caron
# Developed:     Dec. 2, 2021 by Marcel Caron
# Last Modified: Jun. 7, 2023 by Marcel Caron
# Abstract:      Collection of functions that initialize and filter dataframes
#
###############################################################################

import os
import sys
import shutil
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta as td

SETTINGS_DIR = os.environ['USH_DIR']
sys.path.insert(0, os.path.abspath(SETTINGS_DIR))
from prune_stat_files import prune_data
import plot_util


# =================== FUNCTIONS =========================

def get_valid_range(logger, date_type, date_range, date_hours, fleads):
    if None in date_hours:
        e = (f"One or more FCST_{date_type}_HOURS is Nonetype. This may be"
             + f" because the input string is empty.")
        logger.error(e)
        raise ValueError(e)
    if date_type == 'INIT':
        init_beg, init_end = date_range
        valid_beg = (
            init_beg.replace(hour=min(date_hours))
            + td(hours=min(fleads))
        )
        valid_end = (
            init_end.replace(hour=max(date_hours))
            + td(hours=max(fleads))
        )
        valid_range = (valid_beg, valid_end)
    elif date_type == 'VALID':
        valid_range = date_range
    else:
        e = (f"Invalid DATE_TYPE: {str(date_type).upper()}. Valid values are"
             + f" VALID or INIT")
        logger.error(e)
        raise ValueError(e)
    return valid_range

def run_prune_data(logger, stats_dir, prune_dir, output_base_template, 
                   verif_case, verif_type, line_type, valid_range, eval_period, 
                   var_name, fcst_var_names, model_list, domain, fcst_lev):
    model_list = [str(model) for model in model_list]
    tmp_dir = 'tmp'+str(uuid.uuid4().hex)
    pruned_data_dir = os.path.join(
        prune_dir,
        (
            str(line_type).upper()+'_'+str(var_name).upper()+'_'
            +str(domain)+'_'+str(eval_period).upper()
        ),
        tmp_dir
    )
    # Check for pruned data, and run prune_data() if stat files are available
    if os.path.isdir(stats_dir):
        if len(os.listdir(stats_dir)):
            logger.info(f"Looking for stat files in {stats_dir} using the"
                        + f" template: {output_base_template}")
            if type(fcst_lev) == str:
                fcst_lev = [fcst_lev]
            elif type(fcst_lev) != list:
                e = (f"fcst_lev ({fcst_lev}) is neither a string nor a list."
                     + f" Please check the plotting script"
                     + f" (e.g., \"lead_average.py\") to make sure"
                     + f" fcst_level(s) is preprocessed correctly.")
                logger.error(e)
                raise TypeError(e)
            prune_data(
                stats_dir, prune_dir, tmp_dir, output_base_template, 
                valid_range, str(eval_period).upper(), str(verif_case).lower(), 
                str(verif_type).lower(), str(line_type).upper(), str(domain), 
                [' '+str(fcst_var_name)+' ' for fcst_var_name in fcst_var_names],
                str(var_name).upper(), model_list, 
                [' '+str(lev)+' ' for lev in fcst_lev]
            )
        else:
            e1 = f"{stats_dir} exists but is empty."
            e2 = f"Populate {stats_dir} and retry."
            logger.error(e1)
            logger.error(e2)
            raise OSError(e1+"\n"+e2)
    else:
        e1 = f"{stats_dir} does not exist."
        e2 = f"Create and populate {stats_dir} and retry."
        logger.error(e1)
        logger.error(e2)
        raise OSError(e1+"\n"+e2)
    return pruned_data_dir

def check_empty(df, logger, called_from):
    if df.empty:
        logger.warning(f"Called from {called_from}:")
        logger.warning(f"Empty Dataframe encountered while filtering a subset"
                       + f" of input statistics...")
        logger.info("========================================")
        return True
    else:
        return False

def create_df(logger, stats_dir, pruned_data_dir, line_type, date_range, 
              model_list, met_version, clear_prune_dir, verif_type, 
              fcst_var_names, obs_var_names, interp, domain, date_type,
              date_hours, model_queries):
    model_list = [str(model) for model in model_list]
    # Create df combining pruned stats for all models in model_list
    start_string = date_range[0].strftime('%HZ %d %B %Y')
    end_string = date_range[1].strftime('%HZ %d %B %Y')
    for model in model_list:
        fpath = os.path.join(pruned_data_dir,f'{str(model)}.stat')
        if not os.path.isfile(fpath):
            logger.warning(
                f"The stat file for {str(model)} is not a model in"
                + f" {pruned_data_dir}."
            )
            logger.warning(
                f"It may be a group name, or else check if the stats_dir ({stats_dir}) includes"
                + f" {str(model)} data according to the output_base template,"
                + f" given domain, variable, etc..."
            )
            logger.warning("Continuing ...")
            continue
        if not clear_prune_dir:
            logger.debug(f"Creating dataframe using pruned data from {fpath}")
        try:
            df_colnames = plot_util.get_stat_file_base_columns(met_version)
            df_line_type_colnames = plot_util.get_stat_file_line_type_columns(
                logger, met_version, str(line_type).upper(), df_colnames, 
                fpath
            )
            df_colnames = np.concatenate((
                df_colnames, df_line_type_colnames
            ))
            df_tmp = pd.read_csv(
                fpath, delim_whitespace=True, header=None, skiprows=1,
                names=df_colnames, dtype=str
            )
            i = -1*len(df_line_type_colnames)
            for col_name in df_colnames[i:]:
                df_tmp[col_name] = df_tmp[col_name].astype(float)
            df_tmp = run_filters(
                df_tmp, logger, verif_type, fcst_var_names, obs_var_names,
                interp, domain, date_type, date_range, date_hours, model_list,
                model_queries
            )
            try:
                if not df_tmp.empty:
                    df = pd.concat([df, df_tmp])
                else:
                    df = df
            except NameError:
                df = df_tmp
            except UnboundLocalError as e:
                df = df_tmp
            logger.debug(plot_util.get_memory_usage())
            total_memory, _, _ = map(
                int, os.popen('free -t -m').readlines()[-1].split()[1:]
            )
            logger.debug(f"RAM memory available: {total_memory} MiB")
        except pd.errors.EmptyDataError as e:
            logger.error(e)
            logger.error(f"The file in question:")
            logger.error(f"{fpath}")
            logger.error("Continuing ...")
        except OSError as e:
            logger.error(e)
            logger.error(f"The file in question:")
            logger.error(f"{fpath}")
            logger.error("Continuing ...")
    if clear_prune_dir:
        try:
            shutil.rmtree(pruned_data_dir)
        except OSError as e:
            logger.error(e)
            logger.error(f"The directory in question:")
            logger.error(f"{pruned_data_dir}")
            logger.error("Continuing ...")
    try:
        if check_empty(df, logger, 'create_df'):
            return None
        else:
            df.reset_index(drop=True, inplace=True)
            return df
    except UnboundLocalError as e:
        logger.error(e)
        logger.error(
            "Nonexistent dataframe. Check the logfile for more details."
        )
        logger.error("Quitting ...")
        sys.exit(0)

def filter_by_level_type(df, logger, verif_type):
    if df is None:
        return df
    if str(verif_type).lower() in ['pres', 'upper_air']:
        df = df[
            df['FCST_LEV'].str.startswith('P') 
            & df['OBS_LEV'].str.startswith('P')
        ]
        df = df[~df['OBTYPE'].eq('ONLYSF')]
    elif str(verif_type).lower() in ['sfc', 'conus_sfc', 'polar_sfc']:
        df = df[
            ~(df['FCST_LEV'].str.startswith('P') 
            | df['OBS_LEV'].str.startswith('P'))
        ]
    check_empty(df, logger, 'filter_by_level_type')
    return df

def filter_by_var_name(df, logger, fcst_var_names, obs_var_names):
    if df is None:
        return df
    df = df[
        df['FCST_VAR'].isin(fcst_var_names) 
        & df['OBS_VAR'].isin(obs_var_names)
    ]
    check_empty(df, logger, 'filter_by_var_name')
    return df

def filter_by_interp(df, logger, interp):
    if df is None:
        return df
    df = df[df['INTERP_MTHD'].eq(str(interp).upper())]
    check_empty(df, logger, 'filter_by_interp')
    return df

def filter_by_domain(df, logger, domain):
    if df is None:
        return df
    df = df[df['VX_MASK'].eq(str(domain))]
    check_empty(df, logger, 'filter_by_domain')
    return df

def create_lead_hours(df, logger):
    df['LEAD_HOURS'] = np.array([int(lead[:-4]) for lead in df['FCST_LEAD']])
    check_empty(df, logger, 'create_lead_hours')
    return df

def create_valid_datetime(df, logger):
    df['VALID'] = pd.to_datetime(df['FCST_VALID_END'], format='%Y%m%d_%H%M%S')
    check_empty(df, logger, 'create_valid_datetime')
    return df

def create_init_datetime(df, logger):
    df.reset_index(drop=True, inplace=True)
    df['INIT'] = [
        df['VALID'][v] - pd.DateOffset(hours=int(hour)) 
        for v, hour in enumerate(df['LEAD_HOURS'])
    ]
    check_empty(df, logger, 'create_init_datetime')
    return df

def filter_by_date_range(df, logger, date_type, date_range, model_list, 
                         model_queries):
    if df is None:
        return df
    if any(model_queries) and str(date_type).upper() == 'INIT':
        for m, model in enumerate(model_list):
            if 'shift' in model_queries[m]:
                date_range_shift = [
                    dt+td(hours=int(model_queries[m]['shift'][0])) 
                    for dt in date_range
                ]
            else:
                date_range_shift = date_range
            if m == 0:
                df_tmp = df.loc[
                    (df[str(date_type).upper()] >= date_range_shift[0])
                    & (df[str(date_type).upper()] <= date_range_shift[1])
                    & (df['MODEL'] == model)
                ]
            else:
                df_tmp2 = df.loc[
                    (df[str(date_type).upper()] >= date_range_shift[0])
                    & (df[str(date_type).upper()] <= date_range_shift[1])
                    & (df['MODEL'] == model)
                ]
                df_tmp = pd.concat([df_tmp, df_tmp2])
        df = df_tmp
    else:
        df = df.loc[
            (df[str(date_type).upper()] >= date_range[0]) 
            & (df[str(date_type).upper()] <= date_range[1])
        ]
    check_empty(df, logger, 'filter_by_date_range')
    return df

def filter_by_hour(df, logger, date_type, date_hours, model_list, 
                   model_queries):
    if df is None:
        return df
    if check_empty(df, logger, 'filter_by_hour'):
        return df
    else:
        if any(model_queries) and str(date_type).upper() == 'INIT':
            for m, model in enumerate(model_list):
                if 'shift' in model_queries[m]:
                    dhs = [
                        datetime.strptime(str(date_hour).zfill(2), '%H') 
                        for date_hour in date_hours
                    ]
                    dhs_shift = [
                        dh+td(hours=int(model_queries[m]['shift'][0])) 
                        for dh in dhs
                    ]
                    date_hours_shift = [
                        int(dh_shift.strftime('%H')) for dh_shift in dhs_shift
                    ]
                else:
                    date_hours_shift = date_hours
                if m == 0:
                    df_tmp = df.loc[
                        [
                            x in date_hours_shift 
                            for x in df[str(date_type).upper()].dt.hour
                        ]
                        & (df['MODEL'] == model)
                    ]
                else:
                    df_tmp2 = df.loc[
                        [
                            x in date_hours_shift 
                            for x in df[str(date_type).upper()].dt.hour
                        ]
                        & (df['MODEL'] == model)
                    ]
                    df_tmp = pd.concat([df_tmp, df_tmp2])
            df = df_tmp
        else:
            df = df.loc[
                [
                    x in date_hours 
                    for x in df[str(date_type).upper()].dt.hour
                ]
            ]
    check_empty(df, logger, 'filter_by_hour')
    return df

def get_preprocessed_data(logger, stats_dir, prune_dir, output_base_template, 
                          verif_case, verif_type, line_type, date_type, 
                          date_range, eval_period, date_hours, fleads, 
                          var_name, fcst_var_names, obs_var_names, model_list, 
                          model_queries, domain, interp, met_version, 
                          clear_prune_dir, fcst_lev):
    valid_range = get_valid_range(
        logger, date_type, date_range, date_hours, fleads
    )
    pruned_data_dir = run_prune_data(
        logger, stats_dir, prune_dir, output_base_template, verif_case, 
        verif_type, line_type, valid_range, eval_period, var_name, 
        fcst_var_names, model_list, domain, fcst_lev
    )
    df = create_df(
        logger, stats_dir, pruned_data_dir, line_type, date_range, model_list,
        met_version, clear_prune_dir, verif_type, fcst_var_names, obs_var_names, 
        interp, domain, date_type, date_hours, model_queries
    )
    if df is not None and check_empty(df, logger, 'get_preprocessed_data'):
        df = None
    return df

def run_filters(df, logger, verif_type, fcst_var_names, obs_var_names,
                interp, domain, date_type, date_range, date_hours, model_list,
                model_queries):
    df = filter_by_level_type(df, logger, verif_type)
    df = filter_by_var_name(df, logger, fcst_var_names, obs_var_names)
    df = filter_by_interp(df, logger, interp)
    df = filter_by_domain(df, logger, domain)
    df = create_lead_hours(df, logger)
    df = create_valid_datetime(df, logger)
    df = create_init_datetime(df, logger)
    df = filter_by_date_range(
        df, logger, date_type, date_range, model_list, model_queries
    )
    df = filter_by_hour(
        df, logger, date_type, date_hours, model_list, model_queries
    )
    return df

